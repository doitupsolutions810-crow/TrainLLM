#!/bin/bash

################################################################################
# GhostShell Autonomous Mining Script with Live Network Integration
# Advanced miner with network connectivity, health checks, dynamic pooling
# Enhanced with Live Mining Tests, Optimized Algorithms, and Real-time Analytics
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
MINE_LOG="${LOG_DIR}/mining.log"
NETWORK_LOG="${LOG_DIR}/network.log"
HEALTH_LOG="${LOG_DIR}/health.log"
MINER_STATE="${LOG_DIR}/.miner_state"
TEST_RESULTS="${LOG_DIR}/mining_test_results.json"

# Ports
SIM_PORT=5001
ORCH_PORT=8001
MINER_PORT=9001
HEALTH_CHECK_PORT=9002
MINING_TEST_PORT=9003

# Network Configuration
NETWORK_ENDPOINTS=(
    "http://localhost:5001"           # Local Simulation
    "http://localhost:8000"           # CycleKernel Bridge
    "http://localhost:5001/api"       # Sentience HUD API
)

POOL_SERVERS=(
    "localhost:9000"                  # Primary mining pool
    "localhost:9001"                  # Secondary mining pool
    "localhost:9002"                  # Tertiary mining pool
)

# Mining Configuration
MINE_INTERVAL=30                      # Seconds between mining attempts
HEALTH_CHECK_INTERVAL=15              # Seconds between health checks
RECONNECT_TIMEOUT=60                  # Seconds before attempting reconnect
MAX_RETRIES=5                         # Maximum retry attempts (increased)
DIFFICULTY=4                          # Mining difficulty multiplier
ADAPTIVE_DIFFICULTY=true              # Enable difficulty adjustment
MIN_DIFFICULTY=2
MAX_DIFFICULTY=8
TARGET_BLOCK_TIME=45                  # Target seconds per block

# Live Testing Configuration
LIVE_TEST_ENABLED=true                # Enable live mining tests
TEST_FREQUENCY=300                    # Run live test every N seconds
SAMPLE_SIZE=10                        # Number of mining samples for testing
PERFORMANCE_THRESHOLD=50              # Alert if above N% CPU usage

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize logging
mkdir -p "${LOG_DIR}"

# Global performance tracking
declare -g TOTAL_HASH_TIME=0
declare -g TOTAL_HASHES=0
declare -g BLOCK_TIMES=()
declare -g MINING_START_TIME=$(date +%s)
declare -g TEST_LAST_RUN=0
declare -g CONSECUTIVE_FAILURES=0
trap cleanup EXIT INT TERM

cleanup() {
    echo -e "${YELLOW}[CLEANUP] Shutting down mining operation...${NC}"
    kill $SIM_PID $ORCH_PID $HEALTH_CHECK_PID 2>/dev/null || true
    rm -f "${MINER_STATE}"
}

# Logging functions
log_mining() {
    local msg="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" | tee -a "${MINE_LOG}"
}

log_network() {
    local msg="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" | tee -a "${NETWORK_LOG}"
}

log_health() {
    local msg="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" | tee -a "${HEALTH_LOG}"
}

# Network connectivity check
check_network_endpoint() {
    local endpoint="$1"
    local timeout=5
    
    if curl -s --connect-timeout "${timeout}" "${endpoint}/health" >/dev/null 2>&1 || \
       curl -s --connect-timeout "${timeout}" "${endpoint}" >/dev/null 2>&1; then
        echo "online"
    else
        echo "offline"
    fi
}

# Get active pool server
get_active_pool() {
    for pool in "${POOL_SERVERS[@]}"; do
        if timeout 2 bash -c "</dev/tcp/${pool%:*}/${pool#*:}" 2>/dev/null; then
            echo "$pool"
            return 0
        fi
    done
    echo ""
}

# Initialize miner state file
init_miner_state() {
    cat > "${MINER_STATE}" << EOF
{
  "miner_id": "$(uuidgen 2>/dev/null || echo 'ghostshell-miner-'$RANDOM)",
  "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "initializing",
  "network_status": "checking",
  "pool_connected": false,
  "total_hashes": 0,
  "successful_blocks": 0,
  "failed_attempts": 0,
  "last_block_time": null,
  "difficulty": $DIFFICULTY,
  "avg_block_time": 0,
  "pool_efficiency": 0,
  "cpu_usage": 0,
  "memory_usage": 0,
  "current_difficulty": $DIFFICULTY,
  "total_uptime_seconds": 0
}
EOF
    log_mining "Miner state initialized: $(cat ${MINER_STATE})"
}

# Update miner state
update_miner_state() {
    local key="$1"
    local value="$2"
    
    if command -v jq &>/dev/null; then
        jq --arg k "$key" --arg v "$value" '.[$k] = $v' "${MINER_STATE}" > "${MINER_STATE}.tmp"
        mv "${MINER_STATE}.tmp" "${MINER_STATE}"
    fi
}

# Health check background process
run_health_checks() {
    while true; do
        local sim_status=$(check_network_endpoint "http://localhost:${SIM_PORT}")
        local orch_status=$(check_network_endpoint "http://localhost:${ORCH_PORT}")
        local pool_status=""
        
        local active_pool=$(get_active_pool)
        if [ -n "$active_pool" ]; then
            pool_status="online (${active_pool})"
        else
            pool_status="offline"
        fi
        
        log_health "Status: Sim=$sim_status | Orch=$orch_status | Pool=$pool_status"
        
        # Update state file
        update_miner_state "network_status" "$sim_status"
        
        sleep "${HEALTH_CHECK_INTERVAL}"
    done
}

# Advanced mining function with retries and live testing
perform_mining_cycle() {
    local attempt=0
    local success=false
    local cycle_start_time=$(date +%s.%N)
    
    while [ $attempt -lt $MAX_RETRIES ] && [ "$success" = false ]; do
        attempt=$((attempt + 1))
        
        log_mining "Mining cycle #$attempt (difficulty: ${DIFFICULTY}x)"
        
        cd "${SCRIPT_DIR}/TrainLLM"
        
        # Get active pool and mining target
        local active_pool=$(get_active_pool)
        if [ -z "$active_pool" ]; then
            log_mining "No active pool found, attempting local mining"
        else
            log_mining "Mining against pool: $active_pool"
        fi
        
        # Execute mining script with environment variables
        local hash_start=$(date +%s.%N)
        
        if POOL_ADDRESS="${active_pool:-localhost:9000}" \
           MINER_ID="$(jq -r '.miner_id' ${MINER_STATE})" \
           DIFFICULTY="${DIFFICULTY}" \
           python3 seed_generator.py >> "${MINE_LOG}" 2>&1; then
            
            local hash_end=$(date +%s.%N)
            local hash_time=$(echo "$hash_end - $hash_start" | bc)
            
            log_mining "✓ Mining cycle success - hash computation complete (${hash_time}s)"
            update_miner_state "status" "mining_complete"
            update_miner_state "last_block_time" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            
            # Track performance
            TOTAL_HASH_TIME=$(echo "$TOTAL_HASH_TIME + $hash_time" | bc)
            TOTAL_HASHES=$((TOTAL_HASHES + 1))
            BLOCK_TIMES+=("$hash_time")
            CONSECUTIVE_FAILURES=0
            
            success=true
            
        else
            local exit_code=$?
            log_mining "✗ Mining attempt $attempt failed (exit code: $exit_code)"
            CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
            
            if [ $attempt -lt $MAX_RETRIES ]; then
                local backoff=$((2 ** attempt))
                log_mining "Backing off ${backoff}s before retry..."
                sleep "$backoff"
            fi
        fi
        
        cd "${SCRIPT_DIR}"
    done
    
    if [ "$success" = false ]; then
        log_mining "[WARN] Mining cycle failed after $MAX_RETRIES attempts"
        update_miner_state "failed_attempts" "$(($(jq '.failed_attempts' ${MINER_STATE}) + 1))"
        return 1
    fi
    
    return 0
}

# Calculate average block time
calculate_avg_block_time() {
    if [ ${#BLOCK_TIMES[@]} -eq 0 ]; then
        echo "0"
        return
    fi
    
    local sum=0
    for time in "${BLOCK_TIMES[@]}"; do
        sum=$(echo "$sum + $time" | bc)
    done
    
    echo "scale=2; $sum / ${#BLOCK_TIMES[@]}" | bc
}

# Adaptive difficulty adjustment
adjust_difficulty() {
    if [ "$ADAPTIVE_DIFFICULTY" != "true" ]; then
        return
    fi
    
    local avg_time=$(calculate_avg_block_time)
    
    # If avg time is too short, increase difficulty
    if (( $(echo "$avg_time < $TARGET_BLOCK_TIME" | bc -l) )); then
        if [ $DIFFICULTY -lt $MAX_DIFFICULTY ]; then
            DIFFICULTY=$((DIFFICULTY + 1))
            log_mining "Difficulty increased to $DIFFICULTY (block time: ${avg_time}s < ${TARGET_BLOCK_TIME}s)"
            update_miner_state "current_difficulty" "$DIFFICULTY"
        fi
    fi
    
    # If avg time is too long, decrease difficulty
    if (( $(echo "$avg_time > $TARGET_BLOCK_TIME * 1.5" | bc -l) )); then
        if [ $DIFFICULTY -gt $MIN_DIFFICULTY ]; then
            DIFFICULTY=$((DIFFICULTY - 1))
            log_mining "Difficulty decreased to $DIFFICULTY (block time: ${avg_time}s > ${TARGET_BLOCK_TIME}s)"
            update_miner_state "current_difficulty" "$DIFFICULTY"
        fi
    fi
}

# Live mining performance test
run_live_mining_test() {
    local current_time=$(date +%s)
    local time_since_last_test=$((current_time - TEST_LAST_RUN))
    
    if [ $time_since_last_test -lt $TEST_FREQUENCY ]; then
        return
    fi
    
    TEST_LAST_RUN=$current_time
    
    log_mining "╔════════════════════════════════════════════════════════════════╗"
    log_mining "║     LIVE MINING PERFORMANCE TEST - Starting                    ║"
    log_mining "║     Sampling $SAMPLE_SIZE mining cycles for analysis           ║"
    log_mining "╚════════════════════════════════════════════════════════════════╝"
    
    local test_start=$(date +%s.%N)
    local test_hashes=0
    local test_successes=0
    local test_failures=0
    local block_times=()
    
    for ((i=1; i<=SAMPLE_SIZE; i++)); do
        log_mining "Live Test Cycle $i/$SAMPLE_SIZE"
        
        # Run lightweight mining test
        cd "${SCRIPT_DIR}/TrainLLM"
        
        local cycle_start=$(date +%s.%N)
        
        if POOL_ADDRESS="localhost:9000" \
           MINER_ID="test-cycle-$i" \
           DIFFICULTY="2" \
           timeout 10 python3 seed_generator.py >> "${TEST_RESULTS}" 2>&1; then
            
            test_successes=$((test_successes + 1))
            local cycle_end=$(date +%s.%N)
            local cycle_time=$(echo "$cycle_end - $cycle_start" | bc)
            block_times+=("$cycle_time")
            
            log_mining "  ✓ Cycle $i success (${cycle_time}s)"
        else
            test_failures=$((test_failures + 1))
            log_mining "  ✗ Cycle $i failed"
        fi
        
        test_hashes=$((test_hashes + 1))
        cd "${SCRIPT_DIR}"
    done
    
    local test_end=$(date +%s.%N)
    local total_test_time=$(echo "$test_end - $test_start" | bc)
    
    # Calculate statistics
    local success_rate=$(echo "scale=2; $test_successes / $test_hashes * 100" | bc)
    local avg_block_time=0
    
    if [ ${#block_times[@]} -gt 0 ]; then
        local sum=0
        for time in "${block_times[@]}"; do
            sum=$(echo "$sum + $time" | bc)
        done
        avg_block_time=$(echo "scale=2; $sum / ${#block_times[@]}" | bc)
    fi
    
    # Log test results
    log_mining "╔════════════════════════════════════════════════════════════════╗"
    log_mining "║     LIVE MINING TEST RESULTS                                   ║"
    log_mining "╚════════════════════════════════════════════════════════════════╝"
    log_mining "Total Cycles: $test_hashes"
    log_mining "Successes: $test_successes"
    log_mining "Failures: $test_failures"
    log_mining "Success Rate: ${success_rate}%"
    log_mining "Total Time: ${total_test_time}s"
    log_mining "Average Block Time: ${avg_block_time}s"
    log_mining "Cycles/min: $(echo "scale=2; 60 / $avg_block_time" | bc 2>/dev/null || echo 'N/A')"
    
    # Save test results as JSON
    if command -v jq &>/dev/null; then
        cat > "${TEST_RESULTS}" << EOF
{
  "test_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "test_duration_seconds": $total_test_time,
  "sample_size": $SAMPLE_SIZE,
  "total_cycles": $test_hashes,
  "successful_cycles": $test_successes,
  "failed_cycles": $test_failures,
  "success_rate": $success_rate,
  "average_block_time": $avg_block_time,
  "cycles_per_minute": $(echo "60 / $avg_block_time" | bc 2>/dev/null || echo "0"),
  "difficulty_used": 2,
  "block_times": [$(echo "${block_times[@]}" | tr ' ' ',')]
}
EOF
        log_mining "Test results saved to: $TEST_RESULTS"
    fi
    
    # Trigger difficulty adjustment if needed
    adjust_difficulty
}

# Network probe to discover mining opportunities
probe_network() {
    log_network "Probing network for mining opportunities..."
    
    for endpoint in "${NETWORK_ENDPOINTS[@]}"; do
        local status=$(check_network_endpoint "$endpoint")
        log_network "Endpoint $endpoint: $status"
    done
    
    # Attempt to discover additional peers
    if command -v nmap &>/dev/null; then
        log_network "Scanning for active mining services on common ports..."
        nmap -p 9000-9010 localhost 2>/dev/null | grep -E 'open|closed' || true
    fi
}

# Main initialization
init_miner_state
log_mining "╔════════════════════════════════════════════════════════════════╗"
log_mining "║     GhostShell Autonomous Mining System - Starting             ║"
log_mining "║     Network-Connected Miner v2.0                              ║"
log_mining "╚════════════════════════════════════════════════════════════════╝"

# Clear existing instances
echo -e "${YELLOW}[GhostShell] Clearing previous instances...${NC}"
kill $(lsof -t -i :${SIM_PORT}) 2>/dev/null || true
kill $(lsof -t -i :${ORCH_PORT}) 2>/dev/null || true

# Start Simulation Kernel
echo -e "${BLUE}[GhostShell] Starting Simulation Kernel...${NC}"
cd "${SCRIPT_DIR}/TrainLLM"
python3 full_cyclekernel_buildA_FH_complete.py > logs/sim_kernel.log 2>&1 &
SIM_PID=$!
echo -e "${GREEN}[GhostShell] Simulation running (PID: $SIM_PID)${NC}"
cd "${SCRIPT_DIR}"

# Start Orchestrator
echo -e "${BLUE}[GhostShell] Starting Unified Orchestrator...${NC}"
python3 unified_llm_integration.py > TrainLLM/logs/orchestrator.log 2>&1 &
ORCH_PID=$!
echo -e "${GREEN}[GhostShell] Orchestrator running (PID: $ORCH_PID)${NC}"

# Start Health Check Monitor
run_health_checks &
HEALTH_CHECK_PID=$!
echo -e "${GREEN}[GhostShell] Health monitor running (PID: $HEALTH_CHECK_PID)${NC}"

# Wait for services to initialize
sleep 5

# Network probe
probe_network

# Main Mining Loop
echo -e "${BLUE}[GhostShell] Entering Autonomous Mining Loop...${NC}"
update_miner_state "status" "active"

mining_iteration=0

while true; do
    mining_iteration=$((mining_iteration + 1))
    local loop_start=$(date +%s)
    
    echo -e "${YELLOW}════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Mining Iteration: #$mining_iteration${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════${NC}"
    
    # Verify services are alive
    if ! kill -0 $SIM_PID 2>/dev/null; then
        echo -e "${RED}[FATAL] Simulation Kernel died! Restarting...${NC}"
        log_mining "[CRITICAL] Simulation restart required"
        cd "${SCRIPT_DIR}/TrainLLM"
        python3 full_cyclekernel_buildA_FH_complete.py > logs/sim_kernel.log 2>&1 &
        SIM_PID=$!
        cd "${SCRIPT_DIR}"
        sleep 5
    fi
    
    if ! kill -0 $ORCH_PID 2>/dev/null; then
        echo -e "${RED}[WARN] Orchestrator died, restarting...${NC}"
        log_mining "[WARN] Orchestrator restart"
        python3 unified_llm_integration.py > TrainLLM/logs/orchestrator.log 2>&1 &
        ORCH_PID=$!
        sleep 3
    fi
    
    # Perform mining cycle
    if perform_mining_cycle; then
        echo -e "${GREEN}✓ Mining cycle #$mining_iteration completed successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Mining cycle #$mining_iteration had issues${NC}"
    fi
    
    # Run live mining test periodically
    if [ "$LIVE_TEST_ENABLED" = "true" ]; then
        run_live_mining_test
    fi
    
    # Print statistics
    local uptime=$(($(date +%s) - MINING_START_TIME))
    local avg_block_time=$(calculate_avg_block_time)
    
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}Mining Statistics:${NC}"
    echo -e "  Uptime: ${uptime}s"
    echo -e "  Total Cycles: $TOTAL_HASHES"
    echo -e "  Avg Block Time: ${avg_block_time}s"
    echo -e "  Current Difficulty: $DIFFICULTY"
    echo -e "  Consecutive Failures: $CONSECUTIVE_FAILURES"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    
    # Update total uptime in state
    update_miner_state "total_uptime_seconds" "$uptime"
    update_miner_state "total_hashes" "$TOTAL_HASHES"
    update_miner_state "avg_block_time" "$(printf '%.2f' $(echo "$avg_block_time" | bc 2>/dev/null || echo 0))"
    
    # Sleep before next iteration
    echo -e "${BLUE}Next mining cycle in ${MINE_INTERVAL}s...${NC}"
    sleep "${MINE_INTERVAL}"
done