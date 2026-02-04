# voidOS Simple - Copy & Paste Ready

Everything you need to run voidOS in one place.

## 🎯 Copy-Paste to Run (Choose One Method)

### Method 1: Direct Copy from File
```bash
cd /Users/crownest/Desktop/anti2/Anti4
python3 voidos_simple.py
```

### Method 2: From GitHub (Once Available)
```bash
curl -O https://raw.githubusercontent.com/doitupsolutions810-crow/TrainLLM/master/voidos_simple.py
python3 voidos_simple.py
```

### Method 3: From Current Directory
```bash
python3 voidos_simple.py
# Then open:
# - http://localhost:5001
# - http://localhost:5002
```

## ✅ Verify It Works

```bash
# In another terminal while voidos_simple.py is running:

# Test Dashboard
curl http://localhost:5001/api/health

# Test Terminal
curl http://localhost:5002/api/health

# Test Command
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'
```

## 🌐 Access Points

Open in your browser:

```
Dashboard: http://localhost:5001
Terminal:  http://localhost:5002
```

## 📊 What Runs

```
Port 5001: Dashboard
  - Home (status info)
  - Apps (launcher)
  - Terminal (quick commands)
  - Info (system details)

Port 5002: Terminal
  - Full web-based shell
  - Session management
  - Command history
```

## 🔌 API Endpoints (Copy-Paste)

### Get Health Status
```bash
curl http://localhost:5001/api/health
curl http://localhost:5002/api/health
```

### Get Seed Info
```bash
curl http://localhost:5001/api/seed
```

### Get Apps List
```bash
curl http://localhost:5001/api/apps
```

### Execute Command (Dashboard)
```bash
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd"}'
```

### Execute Command (Terminal)
```bash
curl -X POST http://localhost:5002/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la","session_id":"term_demo"}'
```

### Create Terminal Session
```bash
curl http://localhost:5002/api/terminal/session/create
```

## 📋 The Complete File (voidos_simple.py)

File location: `/Users/crownest/Desktop/anti2/Anti4/voidos_simple.py`
File size: 18KB
Lines: ~800

Contains everything:
- Both servers
- All HTML UIs
- All APIs
- Seed management
- Command execution

## 🛠️ Customization (Edit These Lines)

In `voidos_simple.py`, change:

```python
# Line 16
DASHBOARD_PORT = 5001    # ← Change if port in use

# Line 17
TERMINAL_PORT = 5002     # ← Change if port in use

# Line 18
SEED_PATH = "/tmp/voidos/seed.json"  # ← Change location if needed
```

Then run:
```bash
python3 voidos_simple.py
```

## 🧪 Full Test Script (Copy-Paste)

```bash
#!/bin/bash

echo "🧪 Testing voidOS..."

# Wait for startup
sleep 2

# Test 1: Dashboard health
echo "1️⃣  Dashboard health:"
curl -s http://localhost:5001/api/health | jq . || echo "FAILED"

# Test 2: Terminal health
echo "2️⃣  Terminal health:"
curl -s http://localhost:5002/api/health | jq . || echo "FAILED"

# Test 3: Get seed
echo "3️⃣  Get seed ID:"
curl -s http://localhost:5001/api/seed | jq .seed_id || echo "FAILED"

# Test 4: Get apps count
echo "4️⃣  Get apps count:"
curl -s http://localhost:5001/api/apps | jq 'length' || echo "FAILED"

# Test 5: Execute command
echo "5️⃣  Execute whoami:"
curl -s -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}' | jq . || echo "FAILED"

# Test 6: Execute pwd
echo "6️⃣  Execute pwd:"
curl -s -X POST http://localhost:5002/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd"}' | jq . || echo "FAILED"

echo "✅ All tests completed!"
```

Save as `test_voidos.sh` and run:
```bash
chmod +x test_voidos.sh
./test_voidos.sh
```

## 📁 Files You Need

Only this one file:
```
voidos_simple.py  (18KB)
```

That's it! Everything is included.

## 🚀 Quick Start Checklist

- [ ] Have Python 3.7+ installed
- [ ] File downloaded to current directory
- [ ] Run: `python3 voidos_simple.py`
- [ ] Wait 2-3 seconds for startup
- [ ] Open http://localhost:5001
- [ ] Try clicking dashboard panels
- [ ] Open http://localhost:5002
- [ ] Try running a command (e.g., `whoami`)
- [ ] Test API with curl
- [ ] Done! 🎉

## ⚡ Command Examples to Try

In Terminal panel (http://localhost:5002):

```bash
whoami
pwd
ls -la
date
echo "Hello voidOS"
cat /etc/hostname
ps aux | head -5
uname -a
```

## 🐛 Quick Fixes

**Port 5001 in use:**
```bash
lsof -i :5001 | tail -1 | awk '{print $2}' | xargs kill -9
python3 voidos_simple.py
```

**Port 5002 in use:**
```bash
lsof -i :5002 | tail -1 | awk '{print $2}' | xargs kill -9
python3 voidos_simple.py
```

**Check if running:**
```bash
ps aux | grep voidos_simple
```

**Stop gracefully:**
```bash
# Press Ctrl+C in the terminal where it's running
```

## 📊 Expected Output on Start

```
============================================================
🚀 voidOS Complete System
============================================================
✅ Seed created at /tmp/voidos/seed.json
✅ Dashboard server running on http://localhost:5001
✅ Terminal server running on http://localhost:5002

📍 Access points:
   Dashboard: http://localhost:5001
   Terminal:  http://localhost:5002

🔌 API Endpoints:
   GET  http://localhost:5001/api/seed
   GET  http://localhost:5001/api/apps
   POST http://localhost:5001/api/terminal/execute
   POST http://localhost:5002/api/terminal/execute

⚡ Press Ctrl+C to stop
```

## 🎓 Next Steps

1. **Explore Dashboard** (http://localhost:5001)
   - Click each sidebar icon
   - Try commands in Terminal panel
   - Check System Info

2. **Use Terminal** (http://localhost:5002)
   - Type commands
   - See live output
   - Multiple sessions possible

3. **Try API Calls**
   ```bash
   # Get everything
   curl http://localhost:5001/api/seed | jq .
   curl http://localhost:5001/api/apps | jq .
   ```

4. **Build on It**
   - Add new apps to seed
   - Create custom HTML UIs
   - Add API endpoints

## 💾 Save Configuration

Seed file auto-created at:
```
/tmp/voidos/seed.json
```

Contains:
- 8 registered applications
- System configuration
- Merkle verification data

## 🎯 System Features

✅ Web-based dashboard
✅ Web-based terminal
✅ Command execution
✅ Session management
✅ JSON APIs
✅ CORS support
✅ Dark theme UI
✅ Cross-browser compatible

## 📞 Support

- Check seed file exists: `cat /tmp/voidos/seed.json`
- Verify ports available: `lsof -i :5001,:5002`
- Check Python version: `python3 --version`

---

**Ready to go!** 🚀 Run `python3 voidos_simple.py` and enjoy voidOS!
