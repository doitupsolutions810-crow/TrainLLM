# voidOS Simple - Quick Reference

## 🚀 Get Started in 30 Seconds

```bash
# 1. Download
curl -O https://raw.githubusercontent.com/doitupsolutions810-crow/TrainLLM/master/voidos_simple.py

# 2. Run
python3 voidos_simple.py

# 3. Open
# Dashboard: http://localhost:5001
# Terminal:  http://localhost:5002
```

## 📍 URLs

| Component | URL |
|-----------|-----|
| Dashboard | http://localhost:5001 |
| Terminal | http://localhost:5002 |
| Health Check | http://localhost:5001/api/health |
| Seed Info | http://localhost:5001/api/seed |
| Apps List | http://localhost:5001/api/apps |

## 🔌 API Examples

### Get Seed
```bash
curl http://localhost:5001/api/seed
```

### List Apps
```bash
curl http://localhost:5001/api/apps
```

### Execute Command (Dashboard)
```bash
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'
```

### Execute Command (Terminal)
```bash
curl -X POST http://localhost:5002/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd","session_id":"term_123"}'
```

## 📊 What You Get

```
✅ Dashboard UI        - Professional dark interface
✅ Terminal UI         - Full web-based shell
✅ Seed System         - Blockchain-inspired config
✅ 8 Applications      - Terminal, Files, Seed Mgr, GhostShell, LLM, Memory, Logs, Settings
✅ REST APIs           - JSON endpoints for everything
✅ Session Management  - Multiple terminal sessions
✅ Command Execution   - Full shell support
```

## ⚙️ Customize

Edit `voidos_simple.py`:

```python
DASHBOARD_PORT = 5001      # Change dashboard port
TERMINAL_PORT = 5002       # Change terminal port
SEED_PATH = "/tmp/voidos/seed.json"  # Change seed location
```

## 🧪 Test It

```bash
# Test dashboard health
curl http://localhost:5001/api/health

# Test terminal health
curl http://localhost:5002/api/health

# Test command execution
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la"}'

# Test seed loading
curl http://localhost:5001/api/seed | jq .seed_id
```

## 🛑 Stop It

```bash
# Method 1: Press Ctrl+C in terminal
^C

# Method 2: Kill from another terminal
kill $(lsof -t -i :5001)
```

## 📋 File Structure

Single file: `voidos_simple.py`

Contains:
- Configuration
- Seed management
- Dashboard HTML (embedded)
- Terminal HTML (embedded)
- Dashboard server
- Terminal server
- API handlers
- Command execution

## 🎯 Features Summary

| Feature | Status |
|---------|--------|
| Dashboard | ✅ Working |
| Terminal | ✅ Working |
| Seed System | ✅ Working |
| Command Execution | ✅ Working |
| Session Management | ✅ Working |
| CORS Support | ✅ Working |
| Thread Safety | ✅ Working |
| Error Handling | ✅ Working |
| Cross-Browser | ✅ Working |

## 📦 Requirements

- Python 3.7+
- Ports 5001, 5002 available
- `/tmp` writable
- No external dependencies!

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Find what's using port 5001
lsof -i :5001

# Kill it
kill -9 <PID>
```

**Permission denied:**
```bash
# Make script executable
chmod +x voidos_simple.py

# Or run explicitly
python3 voidos_simple.py
```

**Connection refused:**
```bash
# Wait for server to start
sleep 2

# Check if running
ps aux | grep voidos_simple
```

## 🎓 Learn More

For detailed info, see:
- `VOIDOS_SIMPLE_GUIDE.md` - Complete guide
- `BUILD_PROMPT.md` - Architecture details
- `FETCH_ERROR_FIX.md` - CORS/URL fixes

## 💡 Pro Tips

1. **Keep it running in background:**
   ```bash
   python3 voidos_simple.py &
   ```

2. **Run with custom ports:**
   ```bash
   # Edit DASHBOARD_PORT and TERMINAL_PORT in voidos_simple.py
   ```

3. **Use with curl for automation:**
   ```bash
   while true; do
     curl -X POST http://localhost:5001/api/terminal/execute \
       -H "Content-Type: application/json" \
       -d '{"command":"date"}'
     sleep 5
   done
   ```

4. **Monitor in browser:**
   - Open Dashboard: http://localhost:5001
   - Open Terminal: http://localhost:5002
   - They run independently

5. **Test all endpoints:**
   ```bash
   curl http://localhost:5001/api/health && echo
   curl http://localhost:5002/api/health && echo
   curl http://localhost:5001/api/seed | jq .seed_id && echo
   curl http://localhost:5001/api/apps | jq length && echo
   ```

## 🎉 Success Indicators

You'll know it's working when:

```
✅ Dashboard server running on http://localhost:5001
✅ Terminal server running on http://localhost:5002
✅ Dashboard loads in browser
✅ Terminal loads in browser
✅ Commands execute and show output
✅ Seed file created at /tmp/voidos/seed.json
✅ All 8 apps visible in dashboard
```

---

**Status**: ✅ Production Ready
**File Size**: 18KB
**Setup Time**: < 30 seconds
**Dependencies**: Zero (standard library only)

Enjoy! 🚀
