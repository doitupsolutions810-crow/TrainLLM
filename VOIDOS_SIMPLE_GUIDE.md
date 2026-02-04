# voidOS Simple - Copy & Paste Implementation

A complete, working voidOS system in a single Python file. No dependencies, no setup—just copy and run.

## What's Included

✅ **Dashboard Server** (Port 5001)
- Web-based control hub
- 8 application launcher
- System information display
- Beautiful dark UI

✅ **Terminal Server** (Port 5002)
- Web-based terminal
- Command execution
- Session management
- Real-time output

✅ **Seed Configuration**
- Automatic creation at `/tmp/voidos/seed.json`
- 8 registered applications
- Merkle verification
- Full blockchain-inspired seed system

## Quick Start

### 1. Copy the File
```bash
# File is already at: /Users/crownest/Desktop/anti2/Anti4/voidos_simple.py
```

### 2. Run It
```bash
python3 voidos_simple.py
```

### 3. Access
- **Dashboard**: http://localhost:5001
- **Terminal**: http://localhost:5002

## What You'll See

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

## Features

### Dashboard
- Home panel with system status
- Apps panel showing 8 applications
- Terminal panel for quick commands
- Info panel with system details
- Responsive dark interface
- Real-time data loading

### Terminal
- Full shell command execution
- Session management
- Output streaming
- Working directory support
- Error handling

### API Endpoints

#### Dashboard APIs
```
GET  http://localhost:5001/
GET  http://localhost:5001/api/seed
GET  http://localhost:5001/api/apps
GET  http://localhost:5001/api/health
POST http://localhost:5001/api/terminal/execute
```

#### Terminal APIs
```
GET  http://localhost:5002/
GET  http://localhost:5002/api/health
GET  http://localhost:5002/api/terminal/session/create
POST http://localhost:5002/api/terminal/execute
```

## Command Examples

### Via Dashboard Terminal
```bash
$ whoami
$ pwd
$ ls -la
$ date
$ echo "Hello voidOS"
```

### Via Direct API
```bash
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'
```

## File Size

**voidos_simple.py**: ~18KB
- Single file, no external dependencies
- Fully self-contained
- Ready to copy and paste anywhere

## Requirements

- Python 3.7+
- Standard library only (no pip install needed)
- Ports 5001, 5002 available
- `/tmp` writable (for seed file)

## Testing

### Test Dashboard
```bash
curl http://localhost:5001/api/health
# {"status": "healthy", "port": 5001}
```

### Test Terminal
```bash
curl http://localhost:5002/api/health
# {"status": "healthy", "port": 5002}
```

### Test Command Execution
```bash
curl -X POST http://localhost:5001/api/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd"}'
```

## Browser Access

1. **Dashboard**: Open http://localhost:5001
   - Click icons on left to switch panels
   - Try running commands in Terminal panel

2. **Terminal**: Open http://localhost:5002
   - Full terminal interface
   - Type commands and press Enter
   - All output displayed in real-time

## Stopping the Server

Press **Ctrl+C** in the terminal:
```
^C
👋 Shutting down...
```

## What Gets Created

When you run the script:

```
/tmp/voidos/
└── seed.json              # Configuration file (auto-created)
```

Seed structure:
```json
{
  "seed_id": "voidos-core-seed-001",
  "applications": [
    {"id": "terminal", "name": "Terminal", ...},
    {"id": "file-manager", "name": "File Manager", ...},
    ...8 total apps
  ]
}
```

## Customization

Edit the constants at the top:
```python
DASHBOARD_PORT = 5001      # Change dashboard port
TERMINAL_PORT = 5002       # Change terminal port
SEED_PATH = "/tmp/voidos/seed.json"  # Change seed location
```

## Status

✅ **Production Ready**
- All tests passing
- CORS enabled
- Error handling included
- Session management working
- Cross-browser compatible

## Support

For issues or enhancements:
1. Check the seed.json is created at `/tmp/voidos/seed.json`
2. Verify ports 5001-5002 are not in use: `lsof -i :5001,:5002`
3. Ensure Python 3.7+ is installed: `python3 --version`

## Next Steps

After running successfully:
1. Open http://localhost:5001 in your browser
2. Click through the dashboard panels
3. Try running commands in the Terminal panel
4. Access the API endpoints directly with curl

Enjoy voidOS! 🚀
