#!/usr/bin/env python3
"""
voidOS Complete System - Single File Implementation
A simplified, copy-paste ready implementation of the voidOS Dashboard + Terminal system
"""

import json
import os
import sys
import time
import socket
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

DASHBOARD_PORT = 5001
TERMINAL_PORT = 5002
SEED_PATH = "/tmp/voidos/seed.json"

# ============================================================================
# SEED INITIALIZATION
# ============================================================================

def create_seed():
    """Create seed.json if it doesn't exist."""
    Path("/tmp/voidos").mkdir(parents=True, exist_ok=True)
    
    if Path(SEED_PATH).exists():
        return
    
    seed = {
        "seed_id": "voidos-core-seed-001",
        "genesis_epoch": 1704067200,
        "merkle_verification": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "seed_version": "1.0.0",
        "components": {
            "dashboard": {"enabled": True, "port": DASHBOARD_PORT, "status": "active"},
            "terminal": {"enabled": True, "port": TERMINAL_PORT, "status": "active"}
        },
        "applications": [
            {"id": "terminal", "name": "Terminal", "icon": "⌨️", "status": "ready"},
            {"id": "file-manager", "name": "File Manager", "icon": "📁", "status": "ready"},
            {"id": "seed-manager", "name": "Seed Manager", "icon": "🌱", "status": "ready"},
            {"id": "ghostshell", "name": "GhostShell", "icon": "👻", "status": "ready"},
            {"id": "llm-training", "name": "LLM Training", "icon": "🤖", "status": "ready"},
            {"id": "memory-loop", "name": "Memory Loop", "icon": "🔄", "status": "ready"},
            {"id": "logs-viewer", "name": "Logs Viewer", "icon": "📋", "status": "ready"},
            {"id": "settings", "name": "Settings", "icon": "⚙️", "status": "ready"}
        ]
    }
    
    with open(SEED_PATH, 'w') as f:
        json.dump(seed, f, indent=2)
    
    print(f"✅ Seed created at {SEED_PATH}")

def load_seed():
    """Load seed from file."""
    with open(SEED_PATH, 'r') as f:
        return json.load(f)

# ============================================================================
# DASHBOARD HTML
# ============================================================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>voidOS Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; font-family: 'Courier New', monospace; background: #0a0a0f; color: #e0e0e0; }
        .desktop { display: flex; width: 100%; height: 100vh; flex-direction: column; }
        .topbar { background: #12121a; border-bottom: 1px solid #2a2a3a; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .topbar-title { font-size: 18px; font-weight: bold; color: #00ff88; }
        .topbar-status { font-size: 12px; color: #888; }
        .main { display: flex; flex: 1; overflow: hidden; }
        .sidebar { width: 60px; background: #12121a; border-right: 1px solid #2a2a3a; display: flex; flex-direction: column; align-items: center; padding: 10px 0; }
        .sidebar-item { width: 50px; height: 50px; margin: 5px 0; background: #1a1a25; border: 2px solid #2a2a3a; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 20px; transition: all 0.3s; }
        .sidebar-item:hover { background: #2a2a3a; border-color: #00ff88; }
        .sidebar-item.active { background: #00ff88; color: #0a0a0f; }
        .content { flex: 1; overflow: auto; padding: 20px; }
        .panel { display: none; }
        .panel.active { display: block; }
        .panel-title { font-size: 20px; margin-bottom: 15px; color: #00ff88; }
        .app-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 15px; }
        .app-card { background: #1a1a25; border: 1px solid #2a2a3a; border-radius: 8px; padding: 15px; text-align: center; cursor: pointer; transition: all 0.3s; }
        .app-card:hover { background: #2a2a3a; border-color: #00ff88; box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
        .app-icon { font-size: 32px; margin-bottom: 8px; }
        .app-name { font-size: 12px; font-weight: bold; color: #00ff88; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .info-card { background: #1a1a25; border: 1px solid #2a2a3a; border-radius: 8px; padding: 15px; }
        .info-label { font-size: 11px; color: #888; margin-bottom: 5px; text-transform: uppercase; }
        .info-value { font-size: 14px; color: #00ff88; font-weight: bold; word-break: break-all; }
        .terminal-output { background: #0a0a0f; border: 1px solid #2a2a3a; border-radius: 4px; padding: 10px; height: 300px; overflow-y: auto; font-size: 12px; margin-bottom: 10px; }
        .terminal-line { margin: 2px 0; }
        .terminal-input { width: 100%; padding: 8px; background: #1a1a25; border: 1px solid #2a2a3a; border-radius: 4px; color: #00ff88; font-family: monospace; font-size: 12px; }
        .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
        .status-active { background: #00ff88; }
        .status-inactive { background: #666; }
    </style>
</head>
<body data-seed-id="">
    <div class="desktop">
        <div class="topbar">
            <div class="topbar-title">⚡ voidOS Dashboard</div>
            <div class="topbar-status">Status: <span class="status-indicator status-active"></span>ACTIVE</div>
        </div>
        
        <div class="main">
            <div class="sidebar">
                <div class="sidebar-item active" onclick="showPanel('home')">🏠</div>
                <div class="sidebar-item" onclick="showPanel('apps')">📦</div>
                <div class="sidebar-item" onclick="showPanel('terminal')">⌨️</div>
                <div class="sidebar-item" onclick="showPanel('info')">ℹ️</div>
            </div>
            
            <div class="content">
                <!-- HOME PANEL -->
                <div id="home" class="panel active">
                    <div class="panel-title">Welcome to voidOS</div>
                    <div class="info-grid">
                        <div class="info-card">
                            <div class="info-label">Seed ID</div>
                            <div class="info-value" id="seedId">Loading...</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Status</div>
                            <div class="info-value"><span class="status-indicator status-active"></span>Running</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Dashboard Port</div>
                            <div class="info-value">5001</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Terminal Port</div>
                            <div class="info-value">5002</div>
                        </div>
                    </div>
                </div>
                
                <!-- APPS PANEL -->
                <div id="apps" class="panel">
                    <div class="panel-title">Applications</div>
                    <div class="app-grid" id="appGrid"></div>
                </div>
                
                <!-- TERMINAL PANEL -->
                <div id="terminal" class="panel">
                    <div class="panel-title">Terminal</div>
                    <div class="terminal-output" id="terminalOutput"></div>
                    <input type="text" class="terminal-input" id="terminalInput" placeholder="$ Enter command..." onkeypress="executeCommand(event)">
                </div>
                
                <!-- INFO PANEL -->
                <div id="info" class="panel">
                    <div class="panel-title">System Information</div>
                    <div class="info-grid">
                        <div class="info-card">
                            <div class="info-label">Platform</div>
                            <div class="info-value">voidOS</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Version</div>
                            <div class="info-value">1.0.0</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Architecture</div>
                            <div class="info-value">Modular</div>
                        </div>
                        <div class="info-card">
                            <div class="info-label">Theme</div>
                            <div class="info-value">Dark Mode</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        
        function showPanel(panelId) {
            // Hide all panels
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            
            // Show selected panel
            document.getElementById(panelId).classList.add('active');
            event.target.closest('.sidebar-item').classList.add('active');
        }
        
        function terminalLog(message) {
            const output = document.getElementById('terminalOutput');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.textContent = message;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }
        
        async function executeCommand(e) {
            if (e.key !== 'Enter') return;
            const input = e.target;
            const command = input.value;
            if (!command) return;
            
            input.value = '';
            terminalLog('$ ' + command);
            
            try {
                const response = await fetch(API_BASE + '/api/terminal/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command })
                });
                const result = await response.json();
                
                if (result.output) {
                    result.output.split('\\n').forEach(line => {
                        if (line) terminalLog(line);
                    });
                }
                if (result.error) {
                    terminalLog('ERROR: ' + result.error);
                }
            } catch (err) {
                terminalLog('ERROR: ' + err.message);
            }
        }
        
        async function loadApps() {
            try {
                const response = await fetch(API_BASE + '/api/apps');
                const apps = await response.json();
                const grid = document.getElementById('appGrid');
                grid.innerHTML = '';
                
                apps.forEach(app => {
                    const card = document.createElement('div');
                    card.className = 'app-card';
                    card.innerHTML = `
                        <div class="app-icon">${app.icon}</div>
                        <div class="app-name">${app.name}</div>
                    `;
                    grid.appendChild(card);
                });
            } catch (err) {
                console.error('Failed to load apps:', err);
            }
        }
        
        async function loadSeed() {
            try {
                const response = await fetch(API_BASE + '/api/seed');
                const seed = await response.json();
                document.getElementById('seedId').textContent = seed.seed_id;
                document.body.dataset.seedId = seed.seed_id;
            } catch (err) {
                console.error('Failed to load seed:', err);
            }
        }
        
        // Load data on startup
        window.addEventListener('load', () => {
            loadSeed();
            loadApps();
        });
    </script>
</body>
</html>"""

# ============================================================================
# TERMINAL HTML
# ============================================================================

TERMINAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>voidOS Terminal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; font-family: 'Courier New', monospace; background: #000; color: #00ff88; }
        .terminal { width: 100%; height: 100vh; display: flex; flex-direction: column; }
        .terminal-header { background: #1a1a1a; padding: 10px 15px; border-bottom: 1px solid #333; }
        .terminal-header-title { font-size: 14px; color: #00ff88; }
        .terminal-output { flex: 1; overflow-y: auto; padding: 15px; background: #000; }
        .terminal-line { margin: 2px 0; }
        .terminal-input-line { display: flex; padding: 0 15px 15px; }
        .terminal-prompt { color: #00ff88; margin-right: 8px; user-select: none; }
        .terminal-input { flex: 1; background: transparent; border: none; color: #00ff88; font-family: monospace; font-size: 14px; outline: none; }
        .error { color: #ff4444; }
        .success { color: #00ff88; }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="terminal-header">
            <div class="terminal-header-title">⌨️ voidOS Terminal - Session <span id="sessionId">loading...</span></div>
        </div>
        <div class="terminal-output" id="terminalOutput"></div>
        <div class="terminal-input-line">
            <span class="terminal-prompt">$</span>
            <input type="text" class="terminal-input" id="terminalInput" placeholder="Enter command..." autofocus>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let sessionId = null;
        
        function addLine(text, className = '') {
            const output = document.getElementById('terminalOutput');
            const line = document.createElement('div');
            line.className = 'terminal-line ' + className;
            line.textContent = text;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }
        
        async function createSession() {
            try {
                const response = await fetch(API_BASE + '/api/terminal/session/create');
                const data = await response.json();
                sessionId = data.session_id;
                document.getElementById('sessionId').textContent = sessionId;
                addLine('Session created: ' + sessionId, 'success');
            } catch (err) {
                addLine('Failed to create session: ' + err.message, 'error');
            }
        }
        
        async function executeCommand(command) {
            if (!command.trim()) return;
            
            addLine('$ ' + command);
            
            try {
                const response = await fetch(API_BASE + '/api/terminal/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command, session_id: sessionId })
                });
                const result = await response.json();
                
                if (result.output) {
                    result.output.split('\\n').forEach(line => {
                        if (line) addLine(line);
                    });
                }
                if (result.error) {
                    addLine('ERROR: ' + result.error, 'error');
                }
            } catch (err) {
                addLine('ERROR: ' + err.message, 'error');
            }
        }
        
        document.getElementById('terminalInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = e.target.value;
                e.target.value = '';
                executeCommand(command);
            }
        });
        
        // Initialize on load
        window.addEventListener('load', createSession);
    </script>
</body>
</html>"""

# ============================================================================
# DASHBOARD SERVER
# ============================================================================

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        
        elif self.path == '/api/seed':
            self.serve_json(load_seed())
        
        elif self.path == '/api/apps':
            seed = load_seed()
            self.serve_json(seed.get('applications', []))
        
        elif self.path == '/api/health':
            self.serve_json({'status': 'healthy', 'port': DASHBOARD_PORT})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/terminal/execute':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode())
            command = data.get('command', '')
            
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
                output = result.stdout
                if result.returncode != 0:
                    output = result.stderr or f"Command failed with code {result.returncode}"
                self.serve_json({'output': output})
            except Exception as e:
                self.serve_json({'error': str(e)})
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_json(self, data):
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        print(f"[Dashboard] {format % args}")

# ============================================================================
# TERMINAL SERVER
# ============================================================================

class TerminalHandler(SimpleHTTPRequestHandler):
    sessions = {}
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(TERMINAL_HTML.encode())
        
        elif self.path.startswith('/api/terminal/session/create'):
            session_id = f"term_{int(time.time() * 1000)}"
            self.sessions[session_id] = {'pwd': os.path.expanduser('~'), 'created': time.time()}
            self.serve_json({'session_id': session_id})
        
        elif self.path == '/api/health':
            self.serve_json({'status': 'healthy', 'port': TERMINAL_PORT})
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/terminal/execute':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode())
            command = data.get('command', '')
            session_id = data.get('session_id', 'default')
            
            # Handle 'cd' specially
            if command.startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(os.path.expanduser(path))
                    if session_id in self.sessions:
                        self.sessions[session_id]['pwd'] = os.getcwd()
                    self.serve_json({'output': f"Changed directory to {os.getcwd()}"})
                except Exception as e:
                    self.serve_json({'error': str(e)})
                return
            
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5, cwd=os.getcwd())
                output = result.stdout or result.stderr or f"Exit code: {result.returncode}"
                self.serve_json({'output': output})
            except Exception as e:
                self.serve_json({'error': str(e)})
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_json(self, data):
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        print(f"[Terminal] {format % args}")

# ============================================================================
# SERVER STARTUP
# ============================================================================

def start_dashboard():
    """Start dashboard server."""
    handler = lambda *args, **kwargs: DashboardHandler(*args, **kwargs)
    server = ThreadedHTTPServer(('localhost', DASHBOARD_PORT), handler)
    print(f"✅ Dashboard server running on http://localhost:{DASHBOARD_PORT}")
    server.serve_forever()

def start_terminal():
    """Start terminal server."""
    handler = lambda *args, **kwargs: TerminalHandler(*args, **kwargs)
    server = ThreadedHTTPServer(('localhost', TERMINAL_PORT), handler)
    print(f"✅ Terminal server running on http://localhost:{TERMINAL_PORT}")
    server.serve_forever()

def main():
    """Start both servers."""
    print("=" * 60)
    print("🚀 voidOS Complete System")
    print("=" * 60)
    
    # Create seed
    create_seed()
    
    # Start servers in threads
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    terminal_thread = threading.Thread(target=start_terminal, daemon=True)
    
    dashboard_thread.start()
    terminal_thread.start()
    
    print("\n📍 Access points:")
    print(f"   Dashboard: http://localhost:{DASHBOARD_PORT}")
    print(f"   Terminal:  http://localhost:{TERMINAL_PORT}")
    print("\n🔌 API Endpoints:")
    print(f"   GET  http://localhost:{DASHBOARD_PORT}/api/seed")
    print(f"   GET  http://localhost:{DASHBOARD_PORT}/api/apps")
    print(f"   POST http://localhost:{DASHBOARD_PORT}/api/terminal/execute")
    print(f"   POST http://localhost:{TERMINAL_PORT}/api/terminal/execute")
    print("\n⚡ Press Ctrl+C to stop\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
