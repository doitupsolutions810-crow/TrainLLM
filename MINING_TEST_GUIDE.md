# GhostShell Mining System - Test Dashboard & CLI Suite

Comprehensive latency profiling, performance analysis, and real-time monitoring for the GhostShell autonomous mining system.

## Overview

This testing suite provides two interfaces for analyzing mining system performance:

1. **Web Dashboard** - Real-time visual monitoring with live metrics
2. **CLI Test Suite** - Interactive and command-line testing with detailed reports

## Quick Start

### Web Dashboard (Real-Time Monitoring)

```bash
# Start dashboard only (runs on http://localhost:9002)
python3 mining_test_dashboard.py --dashboard

# Or combined with CLI
python3 mining_test_dashboard.py
```

Access the dashboard at: `http://localhost:9002`

### CLI Test Suite

```bash
# Interactive mode (menu-driven)
bash test_mining_system.sh

# Or run specific tests
bash test_mining_system.sh --network       # Network connectivity
bash test_mining_system.sh --health        # Process health
bash test_mining_system.sh --ports         # Port availability
bash test_mining_system.sh --mining        # Mining cycles
bash test_mining_system.sh --performance   # System resources
bash test_mining_system.sh --stress        # 100-request stress test
bash test_mining_system.sh --all           # Run all tests
```

## Test Features

### Network Connectivity Tests
- **Endpoints Monitored**:
  - Simulation Kernel (http://localhost:5001)
  - Orchestrator (http://localhost:8001)
  - CycleKernel Bridge (http://localhost:8000)
  - Sentience HUD API (http://localhost:5001/api)
  - Local Loopback (127.0.0.1:5001)

- **Metrics Collected**:
  - Average latency (ms)
  - Min/Max latency
  - Success rate (%)
  - Sample count

### Process Health Checks
- Simulation Kernel status
- Orchestrator status
- Mining process status
- Service restart detection

### Port Availability Testing
- Monitors 5 critical ports
- Detects open/closed states
- TCP/LISTEN validation

### Mining Cycle Simulation
- 5 cycles per test run
- Measures per-cycle latency
- Calculates average time

### Performance Analysis
- Free memory tracking
- CPU usage monitoring
- Network interface stats

### Stress Testing
- 100 rapid requests
- Success rate calculation
- Throughput measurement (requests/sec)

## Web Dashboard Features

### Real-Time Metrics Display
```
📊 System Status
  - Network status (online/offline count)
  - Mining cycles completed
  - System uptime
  - Last update timestamp

📊 Latency Metrics
  - Minimum latency
  - Maximum latency
  - Average latency
  - Total probes

✓ Success Metrics
  - Successful probes
  - Failed probes
  - Success rate (%)

🌐 Endpoint Status
  - Individual endpoint health
  - Per-endpoint latency
  - Status badges (online/offline)

📈 Latency Chart
  - Visual bar chart of endpoint latencies
  - Comparative performance view
  - Interactive elements
```

### Interactive Controls
- **Quick Test** - 5 rapid test cycles
- **Long Test** - 20-cycle comprehensive test
- **Refresh Metrics** - Force metrics update
- **Export JSON** - Download test data as JSON

### Real-Time Auto-Refresh
- 2-second refresh interval
- Live status updates
- No page refresh required

## Performance Metrics

### Latency Ranges
- **Excellent**: < 5ms
- **Good**: 5-20ms
- **Acceptable**: 20-50ms
- **Slow**: > 50ms

### Success Thresholds
- **Target Success Rate**: > 95%
- **Warning Level**: 80-95%
- **Critical Level**: < 80%

### Stress Test Results
- Tests with 100 concurrent requests
- Measures maximum throughput
- Identifies performance bottlenecks

## Data Export

### JSON Export Format
```json
{
  "timestamp": "2026-02-07T12:34:56Z",
  "test_results": [
    {
      "endpoint": "Simulation Kernel",
      "url": "http://localhost:5001",
      "avg_ms": 2.45,
      "min_ms": 1.23,
      "max_ms": 5.67,
      "samples": 5,
      "success": 5
    }
  ],
  "system_info": {
    "os": "Darwin",
    "hostname": "MacBook-Pro",
    "architecture": "arm64"
  }
}
```

### Export Locations
- Dashboard exports: Named by timestamp
- CLI exports: `logs/test_results_[UNIX_TIMESTAMP].json`

## Dashboard URL

```
http://localhost:9002
```

Access from any browser on the same network. Dashboard updates automatically every 2 seconds.

## Log Files

Test results and logs are stored in:
```
logs/
  mining.log          # Mining cycle logs
  network.log         # Network probe results
  health.log          # Health check logs
  test_results_*.json # Test exports
```

## Usage Examples

### Example 1: Quick Network Test
```bash
bash test_mining_system.sh --network
```

Output:
```
▶ Testing Simulation Kernel (http://localhost:5001)
✓ Simulation Kernel - Avg: 2ms | Min: 1ms | Max: 5ms
  Success Rate: 100%
```

### Example 2: Full System Test
```bash
bash test_mining_system.sh --all
```

Runs:
1. Network Connectivity Test
2. Process Health Check
3. Port Availability Test
4. Mining Cycle Simulation
5. Performance Analysis
6. Stress Test

### Example 3: Monitor Dashboard in Real-Time
```bash
# Terminal 1: Start mining
bash mine.sh

# Terminal 2: Start test dashboard
python3 mining_test_dashboard.py --dashboard

# Terminal 3: Browser
open http://localhost:9002
```

## Troubleshooting

### Dashboard Not Loading
```bash
# Check if port is in use
lsof -i :9002

# Kill previous instance if needed
kill -9 $(lsof -t -i :9002)

# Restart dashboard
python3 mining_test_dashboard.py --dashboard
```

### Network Endpoints Offline
```bash
# Verify services are running
pgrep -f "full_cyclekernel_buildA_FH_complete.py"
pgrep -f "unified_llm_integration.py"

# If not running, start mining system
bash mine.sh
```

### Port Conflicts
```bash
# List all listening ports
lsof -i -P -n | grep LISTEN

# Kill specific port
kill -9 $(lsof -t -i :5001)
```

## Performance Optimization Tips

1. **Baseline Latency**: Run `--network` test before starting mining
2. **Monitor Continuously**: Keep dashboard open during mining
3. **Stress Test Regularly**: Run `--stress` to identify limits
4. **Export Results**: Compare runs over time with JSON exports
5. **Check Logs**: Review `logs/` directory for detailed info

## Integration with Mine.sh

The testing system runs independently but complements `mine.sh`:

```bash
# Terminal 1: Start mining with network integration
bash mine.sh

# Terminal 2: Monitor in real-time
python3 mining_test_dashboard.py --dashboard
```

The dashboard automatically detects when mining is active and updates metrics accordingly.

## System Requirements

- Python 3.7+
- Bash 4.0+
- `curl` (for HTTP tests)
- `lsof` (for port monitoring)
- macOS/Linux with standard utilities

## API Endpoints

### Metrics Endpoint
```
GET /api/metrics
Content-Type: application/json
```

Returns current system metrics as JSON.

### Test Endpoint
```
GET /api/test
Content-Type: application/json
```

Returns results of current endpoint test cycle.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify all services are running
3. Run `--health` to check process status
4. Review dashboard for visual indicators

---

**GhostShell Mining System v2.0** | Test & Monitoring Suite
