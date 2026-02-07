#!/bin/bash

################################################################################
# GhostShell Mining System - Complete Setup & Test Script
# One-command setup, launch, and monitoring
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "${LOG_DIR}"

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║     GhostShell Mining System - Complete Test & Launch         ║"
    echo "║                     v2.0 with Network Integration            ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_menu() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}GhostShell Mining System - Main Menu${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "🚀 LAUNCH OPTIONS"
    echo "  1. Start Mining System (with network integration)"
    echo "  2. Start Dashboard Only (monitoring only)"
    echo ""
    echo "🧪 TEST OPTIONS"
    echo "  3. Quick Latency Test (network endpoints)"
    echo "  4. Full System Test (comprehensive)"
    echo "  5. Stress Test (100 requests)"
    echo ""
    echo "📊 MONITORING"
    echo "  6. Open Web Dashboard (http://localhost:9002)"
    echo "  7. View Test Results"
    echo "  8. Export Metrics to JSON"
    echo ""
    echo "🔧 UTILITIES"
    echo "  9. Process Health Check"
    echo " 10. View Mining Logs"
    echo " 11. View Test Logs"
    echo " 12. Clear All Logs"
    echo ""
    echo "❌ EXIT"
    echo " 13. Exit"
    echo ""
}

launch_mining() {
    echo -e "${GREEN}[Launch] Starting GhostShell Mining System...${NC}"
    cd "${SCRIPT_DIR}"
    bash mine.sh &
    local MINE_PID=$!
    echo -e "${GREEN}[Launch] Mining started (PID: $MINE_PID)${NC}"
    echo "  - Mining logs: ${LOG_DIR}/mining.log"
    echo "  - Network logs: ${LOG_DIR}/network.log"
    echo "  - Health logs: ${LOG_DIR}/health.log"
    echo ""
    echo -e "${YELLOW}[Launch] Waiting for services to start (10s)...${NC}"
    sleep 10
    echo -e "${GREEN}[Launch] Services should be online${NC}"
    echo ""
    echo "  Simulation: http://localhost:5001"
    echo "  Orchestrator: http://localhost:8001"
    echo "  Dashboard: http://localhost:9002"
}

launch_dashboard() {
    echo -e "${GREEN}[Dashboard] Starting Test Dashboard...${NC}"
    cd "${SCRIPT_DIR}"
    python3 mining_test_dashboard.py --dashboard &
    local DASH_PID=$!
    echo -e "${GREEN}[Dashboard] Running on http://localhost:9002 (PID: $DASH_PID)${NC}"
    echo ""
    echo "  Opening dashboard in 3 seconds..."
    sleep 3
    open "http://localhost:9002" 2>/dev/null || echo "  Dashboard available at http://localhost:9002"
}

run_quick_test() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Quick Latency Test${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
    bash test_mining_system.sh --network
}

run_full_test() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Full System Test (All Tests)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
    bash test_mining_system.sh --all
}

run_stress_test() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Stress Test (100 Rapid Requests)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
    bash test_mining_system.sh --stress
}

health_check() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Process Health Check${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
    bash test_mining_system.sh --health
}

view_mining_logs() {
    if [ -f "${LOG_DIR}/mining.log" ]; then
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}Mining Logs (Last 30 lines)${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
        tail -30 "${LOG_DIR}/mining.log"
    else
        echo -e "${YELLOW}[Warning] No mining logs found${NC}"
    fi
}

view_test_logs() {
    local latest=$(ls -t "${LOG_DIR}"/test_results_*.json 2>/dev/null | head -1)
    if [ -n "$latest" ]; then
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}Latest Test Results${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
        cat "$latest" | jq '.' 2>/dev/null || cat "$latest"
    else
        echo -e "${YELLOW}[Warning] No test results found${NC}"
    fi
}

export_metrics() {
    echo -e "${GREEN}[Export] Exporting metrics...${NC}"
    cd "${SCRIPT_DIR}"
    python3 mining_test_dashboard.py --cli > /tmp/export_metrics_temp.txt 2>&1 &
    sleep 2
    echo -e "${GREEN}[Export] Check logs directory for exported JSON files${NC}"
    ls -lh "${LOG_DIR}"/test_results_*.json 2>/dev/null || echo "No exports yet"
}

clear_logs() {
    echo -e "${YELLOW}[Warning] This will delete all log files${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "${LOG_DIR}"/*.log "${LOG_DIR}"/test_results_*.json
        echo -e "${GREEN}[Success] Logs cleared${NC}"
    else
        echo -e "${YELLOW}[Cancelled] Logs preserved${NC}"
    fi
}

# Main loop
main() {
    clear
    print_banner
    
    while true; do
        show_menu
        read -p "Select option (1-13): " choice
        
        case $choice in
            1) 
                launch_mining
                read -p "Press Enter to continue..."
                clear
                ;;
            2) 
                launch_dashboard
                read -p "Press Enter to continue..."
                clear
                ;;
            3) 
                clear
                run_quick_test
                read -p "Press Enter to continue..."
                clear
                ;;
            4) 
                clear
                run_full_test
                read -p "Press Enter to continue..."
                clear
                ;;
            5) 
                clear
                run_stress_test
                read -p "Press Enter to continue..."
                clear
                ;;
            6) 
                open "http://localhost:9002" 2>/dev/null || echo "Open http://localhost:9002 in your browser"
                read -p "Press Enter to continue..."
                clear
                ;;
            7) 
                clear
                view_test_logs
                read -p "Press Enter to continue..."
                clear
                ;;
            8) 
                clear
                export_metrics
                read -p "Press Enter to continue..."
                clear
                ;;
            9) 
                clear
                health_check
                read -p "Press Enter to continue..."
                clear
                ;;
            10) 
                clear
                view_mining_logs
                read -p "Press Enter to continue..."
                clear
                ;;
            11) 
                clear
                view_test_logs
                read -p "Press Enter to continue..."
                clear
                ;;
            12) 
                clear
                clear_logs
                read -p "Press Enter to continue..."
                clear
                ;;
            13) 
                echo -e "\n${GREEN}Thank you for using GhostShell Mining System!${NC}\n"
                exit 0
                ;;
            *) 
                echo -e "${RED}Invalid option${NC}"
                sleep 1
                clear
                ;;
        esac
    done
}

# Run if no arguments
if [ $# -eq 0 ]; then
    main
else
    # Command line mode
    case "$1" in
        --mine) launch_mining ;;
        --dashboard) launch_dashboard ;;
        --test) run_quick_test ;;
        --all) run_full_test ;;
        --stress) run_stress_test ;;
        --health) health_check ;;
        *) echo "Usage: $0 [--mine|--dashboard|--test|--all|--stress|--health]" ;;
    esac
fi
