#!/bin/bash

################################################################################
# GhostShell Autonomous Mining Script with Live Network Integration
# Advanced miner with network connectivity, health checks, and dynamic pooling
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
MINE_LOG="${LOG_DIR}/mining.log"
NETWORK_LOG="${LOG_DIR}/network.log"
HEALTH_LOG="${LOG_DIR}/health.log"
MINER_STATE="${LOG_DIR}/.miner_state"

# Ports
SIM_PORT=5001
ORCH_PORT=8001
MINER_PORT=9001
HEALTH_CHECK_PORT=9002

# Network Configuration
NETWORK_ENDPOINTS=(
    "http://localhost:5001"           # Local Simulation
    "http://localhost:8000"           # CycleKernel Bridge
    "http://localhost:5001/api"       # Sentience HUD API
)

POOL_SERVERS=(
    "localhost:9000"                  # Primary mining pool
    "localhost:9001"                  # Secondary mining pool
)

# Mining Configuration
MINE_INTERVAL=30                      # Seconds between mining attempts
HEALTH_CHECK_INTERVAL=15              # Seconds between health checks
RECONNECT_TIMEOUT=60                  # Seconds before attempting reconnect
MAX_RETRIES=3                         # Maximum retry attempts
DIFFICULTY=4                          # Mining difficulty multiplier

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize logging
mkdir -p "${LOG_DIR}"

# Trap cleanup
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
  "difficulty": $DIFFICULTY
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

# Advanced mining function with retries
perform_mining_cycle() {
    local attempt=0
    local success=false
    
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
        if POOL_ADDRESS="${active_pool:-localhost:9000}" \
           MINER_ID="$(jq -r '.miner_id' ${MINER_STATE})" \
           DIFFICULTY="${DIFFICULTY}" \
           python3 seed_generator.py >> "${MINE_LOG}" 2>&1; then
            
            log_mining "✓ Mining cycle success - hash computation complete"
            update_miner_state "status" "mining_complete"
            update_miner_state "last_block_time" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            success=true
            
        else
            local exit_code=$?
            log_mining "✗ Mining attempt $attempt failed (exit code: $exit_code)"
            
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
    
    # Sleep before next iteration
    echo -e "${BLUE}Next mining cycle in ${MINE_INTERVAL}s...${NC}"
    sleep "${MINE_INTERVAL}"
done
