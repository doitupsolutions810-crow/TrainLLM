# Enhanced Mining System - Quick Start Guide

## 🚀 Launch Enhanced Mining

### Basic Start (with live tests)
```bash
cd /Users/crownest/Desktop/anti2/Anti4
./mine.sh
```

This will:
- ✓ Start Simulation Kernel
- ✓ Start Unified Orchestrator
- ✓ Begin autonomous mining cycles
- ✓ Run live mining tests every 5 minutes
- ✓ Automatically adjust difficulty
- ✓ Display real-time statistics

### What You'll See

**Initial Start**:
```
╔════════════════════════════════════════════════════════════════╗
║     GhostShell Autonomous Mining System - Starting             ║
║     Network-Connected Miner v2.0                              ║
╚════════════════════════════════════════════════════════════════╝

[GhostShell] Clearing previous instances...
[GhostShell] Starting Simulation Kernel...
[GhostShell] Simulation running (PID: xxxxx)
[GhostShell] Starting Unified Orchestrator...
[GhostShell] Orchestrator running (PID: xxxxx)
[GhostShell] Health monitor running (PID: xxxxx)
[GhostShell] Entering Autonomous Mining Loop...
```

**Mining Iteration**:
```
════════════════════════════════════════════
Mining Iteration: #1
════════════════════════════════════════════
Mining cycle #1 (difficulty: 4x)
✓ Mining cycle success - hash computation complete (2.34s)
═══════════════════════════════════════════
Mining Statistics:
  Uptime: 45s
  Total Cycles: 1
  Avg Block Time: 2.34s
  Current Difficulty: 4
  Consecutive Failures: 0
═══════════════════════════════════════════
Next mining cycle in 30s...
```

**Live Mining Test** (every 5 minutes):
```
╔════════════════════════════════════════════════════════════════╗
║     LIVE MINING PERFORMANCE TEST - Starting                    ║
║     Sampling 10 mining cycles for analysis                     ║
╚════════════════════════════════════════════════════════════════╝
Live Test Cycle 1/10
  ✓ Cycle 1 success (0.48s)
Live Test Cycle 2/10
  ✓ Cycle 2 success (0.51s)
...
╔════════════════════════════════════════════════════════════════╗
║     LIVE MINING TEST RESULTS                                   ║
╚════════════════════════════════════════════════════════════════╝
Total Cycles: 10
Successes: 9
Failures: 1
Success Rate: 90.00%
Total Time: 5.12s
Average Block Time: 0.57s
Cycles/min: 105.26
```

---

## 📊 Monitor Mining Progress

### View Real-time Logs
```bash
# Watch mining activity
tail -f logs/mining.log

# Watch network activity
tail -f logs/network.log

# Watch health checks
tail -f logs/health.log
```

### View Live Test Results
```bash
# Show latest test results
cat logs/mining_test_results.json | jq .

# Show formatted test results
jq . logs/mining_test_results.json
```

### Check Miner State
```bash
# View current mining state
cat logs/.miner_state | jq .

# Monitor state changes
watch -n 1 'cat logs/.miner_state | jq .'
```

---

## ⚙️ Configuration

### Adjust Mining Frequency
```bash
# Edit mine.sh
MINE_INTERVAL=30          # Seconds between mining cycles

# Lower value = more frequent mining
# Higher value = longer resting periods
```

### Adjust Live Testing
```bash
# Edit mine.sh
TEST_FREQUENCY=300        # Seconds between tests (5 minutes)
SAMPLE_SIZE=10            # Number of test cycles per run
```

### Adjust Difficulty
```bash
# Edit mine.sh
ADAPTIVE_DIFFICULTY=true  # Enable automatic adjustment
MIN_DIFFICULTY=2          # Minimum difficulty
MAX_DIFFICULTY=8          # Maximum difficulty
TARGET_BLOCK_TIME=45      # Target seconds per block
```

### Adjust Pool Servers
```bash
# Edit mine.sh
POOL_SERVERS=(
    "localhost:9000"      # Primary
    "localhost:9001"      # Secondary
    "localhost:9002"      # Tertiary
)
```

---

## 🧪 Test Results Analysis

### Success Rate Tracking
```bash
# Extract success rates from test results
jq '.success_rate' logs/mining_test_results.json

# Should be > 80% for good performance
```

### Block Time Analysis
```bash
# Check average block time
jq '.average_block_time' logs/mining_test_results.json

# Check target (should be ~45s)
# Lower = faster mining, higher = slower
```

### Throughput Calculation
```bash
# Cycles per minute
jq '.cycles_per_minute' logs/mining_test_results.json

# Higher = better efficiency
```

---

## 🚨 Troubleshooting

### Mining Appears Stuck
```bash
# Check process status
ps aux | grep mine.sh

# Check log file size (growth = activity)
watch -n 2 'wc -l logs/mining.log'

# Check for errors
grep "WARN\|ERROR\|FATAL" logs/mining.log
```

### Low Success Rate
```bash
# Check consecutive failures
jq '.failed_attempts' logs/.miner_state

# Check difficulty level
jq '.current_difficulty' logs/.miner_state

# If too high, system is overloaded
```

### Test Failures
```bash
# Verify TrainLLM directory exists
ls -la TrainLLM/

# Check seed_generator.py is executable
file TrainLLM/seed_generator.py

# Run single test cycle manually
cd TrainLLM && python3 seed_generator.py && cd ..
```

### Network Issues
```bash
# Check pool connectivity
nc -zv localhost 9000

# Check which pools are online
bash test_mining_system.sh --ports

# Check network log
tail -50 logs/network.log
```

---

## 📈 Performance Metrics

### Key Indicators
| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| Success Rate | > 95% | 80-95% | < 80% |
| Avg Block Time | 40-50s | 30-60s | > 60s |
| Cycles/min | > 1.0 | 0.5-1.0 | < 0.5 |
| Consecutive Failures | 0 | 1-2 | > 3 |

### Monitoring Dashboard
```bash
# View all metrics at once
watch -n 2 'echo "=== MINER STATE ===" && jq . logs/.miner_state && echo && echo "=== TEST RESULTS ===" && jq . logs/mining_test_results.json'
```

---

## 🔄 Auto-Adjustments

### Difficulty Management
The system automatically:
- **Increases** difficulty when block time < 45s (mining too fast)
- **Decreases** difficulty when block time > 67.5s (mining too slow)
- Stays between difficulty 2 and 8
- Updates every live test cycle

### Failure Recovery
- Retries up to 5 times with exponential backoff
- Resets failure counter on success
- Tracks consecutive failures
- Auto-restarts dead processes

### Pool Failover
- Tries primary pool first
- Falls back to secondary if unavailable
- Falls back to tertiary if secondary fails
- Allows local mining if all pools offline

---

## 📝 Log File Locations

```
logs/mining.log              # Main mining operations
logs/network.log             # Network connectivity
logs/health.log              # Health check status
logs/.miner_state            # Current miner state (JSON)
logs/mining_test_results.json # Latest test results (JSON)
logs/sim_kernel.log          # Simulation kernel output
logs/orchestrator.log        # Orchestrator output
```

---

## 🛑 Stopping Mining

### Graceful Shutdown
```bash
# Send SIGINT to mine.sh (Ctrl+C in terminal)
# Or from another terminal:
kill <PID_of_mine.sh>

# Cleanup will:
# - Stop all child processes
# - Remove state file
# - Display shutdown message
```

### Emergency Stop
```bash
# Kill all mining-related processes
pkill -f "mine.sh"
pkill -f "python3"
pkill -f "full_cyclekernel"
```

---

## ✨ Advanced Usage

### Custom Test Frequency
```bash
# For rapid testing (every 60 seconds)
sed -i '' 's/TEST_FREQUENCY=300/TEST_FREQUENCY=60/' mine.sh

# For production (every 10 minutes)
sed -i '' 's/TEST_FREQUENCY=300/TEST_FREQUENCY=600/' mine.sh
```

### Export Statistics
```bash
# Create CSV of test results
jq -r '[.average_block_time, .success_rate, .cycles_per_minute] | @csv' logs/mining_test_results.json

# Append to historical file
echo "$(date +%s),$(jq '.success_rate' logs/mining_test_results.json),$(jq '.average_block_time' logs/mining_test_results.json)" >> mining_history.csv
```

### Compare Pool Performance
```bash
# Check pool efficiency from logs
grep "Mining against pool" logs/mining.log | sort | uniq -c

# Analyze failure rates per pool
grep "failed after" logs/mining.log
```

---

## 🎯 Next Steps

1. **Launch Mining**:
   ```bash
   ./mine.sh
   ```

2. **Monitor in Real-time**:
   ```bash
   tail -f logs/mining.log
   ```

3. **View Test Results** (after 5 minutes):
   ```bash
   cat logs/mining_test_results.json | jq .
   ```

4. **Check Statistics** (after 10 minutes):
   ```bash
   jq . logs/.miner_state
   ```

5. **Verify Dashboard** (ongoing):
   Open browser: http://localhost:9002

---

**Status**: Enhanced mining system ready for deployment with live testing and adaptive difficulty!
