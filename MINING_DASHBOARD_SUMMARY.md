# GhostShell Mining System - Enhanced Test Suite & Dashboard
## Complete Latency Profiling & Performance Monitoring

---

## 📋 System Overview

This enhanced mining system includes comprehensive testing infrastructure for measuring latency, monitoring performance, and analyzing system health in real-time.

### What's New (v2.0)

✅ **Advanced Mining Logic** (mine.sh)
- Multi-endpoint network connectivity
- Pool server discovery and failover
- Exponential backoff retry mechanism
- State persistence with JSON tracking
- Health check background process
- Configurable difficulty scaling

✅ **Web Dashboard** (mining_test_dashboard.py)
- Real-time metric visualization
- Live endpoint status monitoring
- Interactive control buttons
- Automatic 2-second refresh
- Glassmorphic cyberpunk UI
- JSON export functionality

✅ **CLI Test Suite** (test_mining_system.sh)
- Network connectivity profiling
- Process health monitoring
- Port availability checking
- Mining cycle simulation
- System resource analysis
- Stress testing (100 requests)

✅ **Complete Launcher** (ghostshell_complete.sh)
- Unified menu-driven interface
- One-command system launch
- Integrated monitoring
- Log viewing and export
- Health check utilities

---

## 🚀 Quick Start

### Option 1: Unified Launcher (Recommended)
```bash
bash ghostshell_complete.sh
```
Interactive menu with all features.

### Option 2: Direct Launch
```bash
# Terminal 1: Start mining system
bash mine.sh

# Terminal 2: Start dashboard (in background)
python3 mining_test_dashboard.py --dashboard &

# Terminal 3: Run tests
bash test_mining_system.sh --all
```

### Option 3: Dashboard Only
```bash
python3 mining_test_dashboard.py --dashboard
# Open http://localhost:9002 in browser
```

---

## 🧪 Test Types & Features

### 1. Network Connectivity Test
**What it tests:**
- Simulation Kernel (5001)
- Orchestrator (8001)
- CycleKernel Bridge (8000)
- Sentience HUD API (5001/api)
- Local loopback (127.0.0.1)

**Metrics collected:**
- Per-endpoint latency (ms)
- Min/max/average response times
- Success rate (%)
- Sample count per endpoint

**Run with:**
```bash
bash test_mining_system.sh --network
```

### 2. Process Health Check
**What it monitors:**
- Simulation Kernel running status
- Orchestrator running status
- Mining process running status
- Service restart capability

**Run with:**
```bash
bash test_mining_system.sh --health
```

### 3. Port Availability Test
**Ports monitored:**
- 5001 - Simulation Kernel
- 8001 - Orchestrator
- 8000 - CycleKernel Bridge
- 9001 - Mining Service
- 9002 - Dashboard

**Run with:**
```bash
bash test_mining_system.sh --ports
```

### 4. Mining Cycle Simulation
**What it simulates:**
- 5 complete mining cycles
- Per-cycle latency measurement
- Mining heartbeat tracking

**Metrics:**
- Cycle time (ms)
- Average time per cycle
- Total execution time

**Run with:**
```bash
bash test_mining_system.sh --mining
```

### 5. Performance Analysis
**System resources measured:**
- Free memory (MB)
- CPU usage (%)
- Network interface stats

**Run with:**
```bash
bash test_mining_system.sh --performance
```

### 6. Stress Test
**Configuration:**
- 100 rapid consecutive requests
- Success/failure tracking
- Throughput calculation

**Metrics:**
- Total execution time
- Success rate (%)
- Requests per second

**Run with:**
```bash
bash test_mining_system.sh --stress
```

---

## 📊 Web Dashboard Features

### Real-Time Display Sections

```
┌─────────────────────────────────────────────┐
│ 🔧 System Status                            │
│ - Network status (N online)                 │
│ - Mining cycles completed                   │
│ - System uptime                             │
│ - Last update timestamp                     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 📊 Latency Metrics                          │
│ - Min Latency: X.XX ms                      │
│ - Max Latency: X.XX ms                      │
│ - Avg Latency: X.XX ms                      │
│ - Total Probes: N                           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ ✓ Success Metrics                           │
│ - Successful Probes: N                      │
│ - Failed Probes: N                          │
│ - Success Rate: X.X%                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 🌐 Endpoint Status                          │
│ • Simulation Kernel: 2.45ms [ONLINE]        │
│ • Orchestrator: 1.23ms [ONLINE]             │
│ • CycleKernel: 5.67ms [ONLINE]              │
│ • Sentience API: 3.45ms [ONLINE]            │
│ • Local Loopback: 0.98ms [ONLINE]           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 📈 Latency Chart                            │
│ ▰▰▰▰▰▰▰▰▰▯▯▯▯▯▯▯ 2.45ms                  │
│ ▰▰▰▰▰▯▯▯▯▯▯▯▯▯▯▯ 1.23ms                  │
│ ▰▰▰▰▰▰▰▰▰▰▰▰▯▯▯▯ 5.67ms                  │
│ ▰▰▰▰▰▰▰▯▯▯▯▯▯▯▯▯ 3.45ms                  │
│ ▰▰▯▯▯▯▯▯▯▯▯▯▯▯▯▯ 0.98ms                  │
└─────────────────────────────────────────────┘
```

### Interactive Controls
- **▶ Quick Test** - Run 5-cycle test
- **▶ Long Test** - Run 20-cycle test
- **🔄 Refresh Metrics** - Force update
- **⬇ Export JSON** - Download data

### Auto-Refresh Behavior
- Updates every 2 seconds
- No page refresh needed
- Live status indicators
- Color-coded health states

---

## 📁 Generated Files

### Test Suite Components
```
mine.sh                      # Enhanced mining orchestrator (9.7 KB)
test_mining_system.sh        # CLI test suite (9.5 KB)
mining_test_dashboard.py     # Web dashboard (24 KB)
ghostshell_complete.sh       # Unified launcher (11 KB)
```

### Documentation
```
MINING_TEST_GUIDE.md         # Comprehensive testing guide
MINING_DASHBOARD_SUMMARY.md  # This file
```

### Log Directory
```
logs/
  mining.log                 # Mining cycle logs
  network.log                # Network probe results
  health.log                 # Health check logs
  test_results_*.json        # Test exports (timestamped)
```

---

## 🔧 Configuration Parameters

### Mining Configuration (mine.sh)
```bash
MINE_INTERVAL=30              # Seconds between mining attempts
HEALTH_CHECK_INTERVAL=15      # Seconds between health checks
RECONNECT_TIMEOUT=60          # Seconds before reconnect
MAX_RETRIES=3                 # Maximum retry attempts
DIFFICULTY=4                  # Mining difficulty multiplier
```

### Network Endpoints (Monitored)
```bash
http://localhost:5001         # Simulation Kernel
http://localhost:8000         # CycleKernel Bridge
http://localhost:5001/api     # Sentience HUD API
http://localhost:8001         # Orchestrator
```

### Pool Servers
```bash
localhost:9000               # Primary mining pool
localhost:9001               # Secondary mining pool
```

---

## 📈 Performance Benchmarks

### Expected Latency Ranges
```
Excellent:      < 5ms        ✓ Optimal performance
Good:           5-20ms       ✓ Acceptable performance
Acceptable:     20-50ms      ⚠ Monitor carefully
Slow:           > 50ms       ✗ Performance issue
```

### Success Rate Targets
```
Target:         > 95%        ✓ Expected
Warning:        80-95%       ⚠ Investigate
Critical:       < 80%        ✗ Immediate action
```

### Stress Test Results
```
100 Requests:   < 10s        ✓ Excellent throughput
100 Requests:   10-30s       ✓ Good throughput
100 Requests:   30-60s       ⚠ Monitor performance
100 Requests:   > 60s        ✗ Performance degradation
```

---

## 🎯 Usage Scenarios

### Scenario 1: Daily Health Check
```bash
# Quick 5-minute verification
bash ghostshell_complete.sh --health
bash test_mining_system.sh --network
```

### Scenario 2: Performance Baseline
```bash
# Establish performance metrics
bash test_mining_system.sh --all
# Export and save results
python3 mining_test_dashboard.py --cli
```

### Scenario 3: Continuous Monitoring
```bash
# Terminal 1: Start mining
bash mine.sh

# Terminal 2: Start dashboard
python3 mining_test_dashboard.py --dashboard

# Terminal 3: View in browser
open http://localhost:9002
```

### Scenario 4: Load Testing
```bash
# Run stress test multiple times
for i in {1..5}; do
  bash test_mining_system.sh --stress
  sleep 5
done
```

### Scenario 5: Troubleshooting
```bash
# Comprehensive system analysis
bash ghostshell_complete.sh        # Interactive menu
# Select: Health Check → Logs → Full Test
```

---

## 🔐 Security & Safety

✅ **Safety Features:**
- No code execution from untrusted sources
- Sandboxed network tests
- Log isolation
- Clean error handling
- Resource limits on tests

✅ **Data Privacy:**
- Logs stored locally only
- No external API calls (testing)
- JSON export for analysis
- Clear data retention policy

---

## 🐛 Troubleshooting

### Dashboard Not Loading
```bash
# Check port
lsof -i :9002

# Kill if needed
kill -9 $(lsof -t -i :9002)

# Restart
python3 mining_test_dashboard.py --dashboard
```

### Network Tests Show Offline
```bash
# Verify services running
pgrep -f "full_cyclekernel_buildA_FH_complete.py"
pgrep -f "unified_llm_integration.py"

# Start if needed
bash mine.sh
```

### High Latency Detected
```bash
# Run diagnostics
bash test_mining_system.sh --performance
bash test_mining_system.sh --stress

# Check system resources
top -l 1 | grep "CPU usage"
vm_stat | grep "Pages free"
```

### Tests Hanging
```bash
# Check active connections
netstat -an | grep ESTABLISHED

# Kill tests if needed
pkill -f "test_mining_system"
```

---

## 📚 Integration Examples

### With Existing Systems
```bash
# Start mining + dashboard together
bash mine.sh &
python3 mining_test_dashboard.py --dashboard &

# Access dashboard
open http://localhost:9002

# View real-time metrics
curl http://localhost:9002/api/metrics | jq '.'
```

### Custom Integration
```python
import json
import urllib.request

# Fetch metrics
response = urllib.request.urlopen('http://localhost:9002/api/metrics')
metrics = json.loads(response.read())

# Use in your app
print(f"Avg Latency: {metrics['avg_latency']*1000:.2f}ms")
print(f"Success Rate: {metrics['successful_probes']}%")
```

---

## 📞 Support & Documentation

**For detailed information:**
- Read [MINING_TEST_GUIDE.md](MINING_TEST_GUIDE.md) for comprehensive guide
- Check `logs/` directory for detailed logs
- Review JSON exports for data analysis
- Run `--health` for system diagnostics

**Key Files:**
- `mine.sh` - Main mining orchestrator
- `mining_test_dashboard.py` - Web interface
- `test_mining_system.sh` - CLI tests
- `ghostshell_complete.sh` - Unified launcher

---

## 🎉 Summary

The enhanced GhostShell Mining System now provides:

✅ Production-ready mining orchestrator with network integration  
✅ Real-time web dashboard with live metrics  
✅ Comprehensive CLI testing suite  
✅ Automated latency profiling  
✅ System health monitoring  
✅ Performance analysis tools  
✅ Stress testing capabilities  
✅ JSON export for analysis  
✅ Unified launcher interface  
✅ Complete documentation  

**Get started:** `bash ghostshell_complete.sh`

---

**Version:** 2.0 | **Date:** February 7, 2026 | **Status:** Production Ready
