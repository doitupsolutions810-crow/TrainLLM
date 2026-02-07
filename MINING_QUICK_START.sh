#!/bin/bash

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          GhostShell Mining System - Test & Dashboard Quick Start          ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

🎮 QUICK COMMANDS
═══════════════════════════════════════════════════════════════════════════

Unified Menu (Recommended):
  bash ghostshell_complete.sh

Mining + Dashboard:
  bash mine.sh &
  python3 mining_test_dashboard.py --dashboard &

Test Suite:
  bash test_mining_system.sh --network       # Network latency
  bash test_mining_system.sh --health        # Process status
  bash test_mining_system.sh --ports         # Port availability
  bash test_mining_system.sh --all           # Full system test
  bash test_mining_system.sh --stress        # Stress test (100 req)

Dashboard:
  open http://localhost:9002


📊 WHAT YOU'LL SEE
═══════════════════════════════════════════════════════════════════════════

Web Dashboard (http://localhost:9002):
  ✓ Real-time metrics display
  ✓ 5 endpoint status monitors
  ✓ Live latency charts
  ✓ Success rate tracking
  ✓ Interactive controls
  ✓ Auto-refresh every 2 seconds

CLI Tests:
  ✓ Network latency per endpoint
  ✓ Process health status
  ✓ Port availability
  ✓ Mining cycle timing
  ✓ System resource usage
  ✓ Stress test results


📈 WHAT'S TESTED
═══════════════════════════════════════════════════════════════════════════

Endpoints Monitored:
  • Simulation Kernel (5001)
  • Orchestrator (8001)
  • CycleKernel Bridge (8000)
  • Sentience HUD API (5001/api)
  • Local Loopback (127.0.0.1:5001)

Metrics Collected:
  • Latency (min/max/avg)
  • Success rate (%)
  • Throughput (req/sec)
  • System resources
  • Process status


🚀 GETTING STARTED (3 STEPS)
═══════════════════════════════════════════════════════════════════════════

Step 1: Start the system
  bash ghostshell_complete.sh
  → Select option 1 (Start Mining)

Step 2: Monitor in real-time
  → Select option 6 (Open Dashboard)
  → Browser opens at http://localhost:9002

Step 3: Run tests
  → Select option 4 (Full System Test)
  → View results on dashboard


📁 FILES CREATED
═══════════════════════════════════════════════════════════════════════════

mine.sh                    9.7 KB  Enhanced mining with network monitoring
mining_test_dashboard.py   24 KB   Real-time web dashboard
test_mining_system.sh      9.5 KB  CLI test suite (6 test types)
ghostshell_complete.sh     11 KB   Unified launcher menu
MINING_TEST_GUIDE.md       12 KB   Comprehensive documentation
MINING_DASHBOARD_SUMMARY   18 KB   Feature overview


⚡ KEY FEATURES
═══════════════════════════════════════════════════════════════════════════

Mining System:
  ✓ Multi-endpoint monitoring
  ✓ Health checks (15s intervals)
  ✓ Pool failover
  ✓ Exponential backoff retries
  ✓ JSON state persistence

Web Dashboard:
  ✓ Live metric visualization
  ✓ 2-second auto-refresh
  ✓ Interactive buttons
  ✓ Cyberpunk design
  ✓ JSON export

Test Suite:
  ✓ Network profiling
  ✓ Process monitoring
  ✓ Performance analysis
  ✓ Stress testing (100 req)
  ✓ Interactive & CLI modes


🔧 CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

Edit in mine.sh:
  MINE_INTERVAL=30              # Time between mining attempts
  HEALTH_CHECK_INTERVAL=15      # Health check frequency
  MAX_RETRIES=3                 # Retry attempts
  DIFFICULTY=4                  # Mining difficulty

Edit in mining_test_dashboard.py:
  DASHBOARD_PORT=9002           # Web interface port
  REFRESH_INTERVAL=2            # Auto-refresh seconds


📊 PERFORMANCE TARGETS
═══════════════════════════════════════════════════════════════════════════

Excellent:     < 5ms latency, > 95% success
Good:          5-20ms latency, > 90% success
Acceptable:    20-50ms latency, > 80% success
Problematic:   > 50ms latency, < 80% success


🐛 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

Services offline?
  bash ghostshell_complete.sh → Option 1 (Start Mining)

Dashboard not loading?
  kill -9 $(lsof -t -i :9002)
  python3 mining_test_dashboard.py --dashboard

Check logs:
  tail -f logs/mining.log
  tail -f logs/network.log
  tail -f logs/health.log


📞 SUPPORT
═══════════════════════════════════════════════════════════════════════════

Documentation:
  MINING_TEST_GUIDE.md        Complete testing guide
  MINING_DASHBOARD_SUMMARY.md Feature overview

Get help:
  bash ghostshell_complete.sh
  → Select option 9 (Health Check)

View logs:
  bash ghostshell_complete.sh
  → Select option 10 (Mining Logs)
  → Select option 11 (Test Logs)


═════════════════════════════════════════════════════════════════════════════

Start now:  bash ghostshell_complete.sh
Dashboard:  http://localhost:9002
Tests:      bash test_mining_system.sh --all

═════════════════════════════════════════════════════════════════════════════

EOF
