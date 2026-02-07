#!/bin/bash

################################################################################
# GhostShell Mining System - Quick Test Suite
# Latency profiling, performance analysis, and system diagnostics
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
TEST_RESULTS="${LOG_DIR}/test_results_$(date +%s).json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "${LOG_DIR}"

# Helper functions
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_test() {
    echo -e "${CYAN}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Latency test function
test_endpoint_latency() {
    local endpoint="$1"
    local name="$2"
    local samples=5
    local total_latency=0
    local min_latency=999999
    local max_latency=0
    local success_count=0
    
    print_test "Testing $name ($endpoint)"
    
    for i in $(seq 1 $samples); do
        local start=$(date +%s%N)
        
        if curl -s --connect-timeout 5 "$endpoint" >/dev/null 2>&1; then
            local end=$(date +%s%N)
            local latency=$(( (end - start) / 1000000 ))
            
            total_latency=$((total_latency + latency))
            min_latency=$((latency < min_latency ? latency : min_latency))
            max_latency=$((latency > max_latency ? latency : max_latency))
            success_count=$((success_count + 1))
            
            echo -ne "  Sample $i/$samples: ${latency}ms\r"
        fi
    done
    
    if [ $success_count -gt 0 ]; then
        local avg_latency=$((total_latency / success_count))
        print_success "$name - Avg: ${avg_latency}ms | Min: ${min_latency}ms | Max: ${max_latency}ms"
        echo "  Success Rate: $((success_count * 100 / samples))%"
        
        echo "{\"endpoint\":\"$name\",\"url\":\"$endpoint\",\"avg_ms\":$avg_latency,\"min_ms\":$min_latency,\"max_ms\":$max_latency,\"samples\":$samples,\"success\":$success_count}" >> "$TEST_RESULTS"
    else
        print_error "$name - UNREACHABLE"
    fi
}

# Network connectivity test
test_network_connectivity() {
    print_header "Network Connectivity Test"
    
    local endpoints=(
        "http://localhost:5001 Simulation Kernel"
        "http://localhost:8001 Orchestrator"
        "http://localhost:8000 CycleKernel Bridge"
        "http://localhost:5001/api Sentience HUD API"
        "http://127.0.0.1:5001 Local Loopback"
    )
    
    for entry in "${endpoints[@]}"; do
        test_endpoint_latency $entry
    done
}

# Process health test
test_process_health() {
    print_header "Process Health Check"
    
    print_test "Checking for running services..."
    
    # Check simulation
    if pgrep -f "full_cyclekernel_buildA_FH_complete.py" >/dev/null; then
        print_success "Simulation Kernel is running"
    else
        print_warning "Simulation Kernel is NOT running"
    fi
    
    # Check orchestrator
    if pgrep -f "unified_llm_integration.py" >/dev/null; then
        print_success "Orchestrator is running"
    else
        print_warning "Orchestrator is NOT running"
    fi
    
    # Check mining
    if pgrep -f "seed_generator.py" >/dev/null; then
        print_success "Mining process is running"
    else
        print_warning "Mining process is NOT running"
    fi
}

# Port availability test
test_port_availability() {
    print_header "Port Availability Test"
    
    local ports=(
        "5001 Simulation"
        "8001 Orchestrator"
        "8000 CycleKernel"
        "9001 Mining"
        "9002 Dashboard"
    )
    
    for entry in "${ports[@]}"; do
        local port=${entry%% *}
        local service=${entry#* }
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            print_success "Port $port ($service) is OPEN"
        else
            print_warning "Port $port ($service) is CLOSED"
        fi
    done
}

# Mining cycle simulation
test_mining_cycles() {
    print_header "Mining Cycle Simulation"
    
    local cycles=5
    local total_time=0
    
    print_test "Running $cycles mining cycles..."
    
    for i in $(seq 1 $cycles); do
        local cycle_start=$(date +%s%N)
        
        # Simulate mining work
        sleep 0.1
        
        local cycle_end=$(date +%s%N)
        local cycle_time=$(( (cycle_end - cycle_start) / 1000000 ))
        total_time=$((total_time + cycle_time))
        
        echo "  Cycle $i/$cycles: ${cycle_time}ms"
    done
    
    local avg_time=$((total_time / cycles))
    print_success "Mining cycles complete - Average: ${avg_time}ms/cycle"
}

# Performance analysis
test_performance_analysis() {
    print_header "Performance Analysis"
    
    print_test "Analyzing system resources..."
    
    # Memory usage
    if command -v vm_stat &>/dev/null; then
        local free_mem=$(vm_stat | grep "Pages free" | awk '{print $3}' | tr -d '.')
        print_success "Free Memory: ~$((free_mem / 4096))MB"
    fi
    
    # CPU usage
    local cpu=$(top -l 1 | grep "CPU usage" | head -1)
    print_success "CPU Status: $cpu"
    
    # Network I/O
    local netstat=$(netstat -i | grep -E "en0|en1" | head -1)
    print_success "Network Interface: ${netstat:0:50}..."
}

# Stress test
test_stress() {
    print_header "Stress Test (100 Rapid Requests)"
    
    local endpoint="http://localhost:5001"
    local success=0
    local fail=0
    local start=$(date +%s%N)
    
    for i in {1..100}; do
        if curl -s --connect-timeout 2 "$endpoint" >/dev/null 2>&1; then
            success=$((success + 1))
            echo -ne "Success: $success/100 | Failed: $fail/100\r"
        else
            fail=$((fail + 1))
            echo -ne "Success: $success/100 | Failed: $fail/100\r"
        fi
    done
    
    local end=$(date +%s%N)
    local total_time=$(( (end - start) / 1000000000 ))
    
    echo ""
    print_success "Stress Test Complete"
    echo "  Total Time: ${total_time}s"
    echo "  Success Rate: $(( success * 100 / 100 ))%"
    echo "  Requests/sec: $((100 / total_time))"
}

# Export results
export_test_results() {
    if [ -f "$TEST_RESULTS" ]; then
        # Convert to proper JSON array
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
            echo "  \"test_results\": ["
            sed 's/$/,/' "$TEST_RESULTS" | sed '$ s/,$//'
            echo "  ],"
            echo "  \"system_info\": {"
            echo "    \"os\": \"$(uname -s)\","
            echo "    \"hostname\": \"$(hostname)\","
            echo "    \"architecture\": \"$(uname -m)\""
            echo "  }"
            echo "}"
        } > "${TEST_RESULTS}.final"
        mv "${TEST_RESULTS}.final" "$TEST_RESULTS"
        print_success "Results exported to: $TEST_RESULTS"
    fi
}

# Main menu
show_menu() {
    echo -e "\n${CYAN}GhostShell Mining System - Test Suite${NC}"
    echo "========================================"
    echo "1. Network Connectivity Test"
    echo "2. Process Health Check"
    echo "3. Port Availability Test"
    echo "4. Mining Cycle Simulation"
    echo "5. Performance Analysis"
    echo "6. Stress Test (100 requests)"
    echo "7. Run ALL Tests"
    echo "8. Exit"
    echo "========================================"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Select test (1-8): " choice
            
            case $choice in
                1) test_network_connectivity ;;
                2) test_process_health ;;
                3) test_port_availability ;;
                4) test_mining_cycles ;;
                5) test_performance_analysis ;;
                6) test_stress ;;
                7) 
                    test_network_connectivity
                    test_process_health
                    test_port_availability
                    test_mining_cycles
                    test_performance_analysis
                    test_stress
                    ;;
                8) 
                    print_success "Exiting test suite"
                    export_test_results
                    exit 0
                    ;;
                *) print_error "Invalid option" ;;
            esac
        done
    else
        # Command line mode
        case "$1" in
            --network) test_network_connectivity ;;
            --health) test_process_health ;;
            --ports) test_port_availability ;;
            --mining) test_mining_cycles ;;
            --performance) test_performance_analysis ;;
            --stress) test_stress ;;
            --all)
                test_network_connectivity
                test_process_health
                test_port_availability
                test_mining_cycles
                test_performance_analysis
                test_stress
                ;;
            *)
                echo "Usage: $0 [--network|--health|--ports|--mining|--performance|--stress|--all]"
                exit 1
                ;;
        esac
        export_test_results
    fi
}

main "$@"
