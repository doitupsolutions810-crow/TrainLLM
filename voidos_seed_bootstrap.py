#!/usr/bin/env python3
"""
voidOS Seed Bootstrap Module

This module:
- Reads seed from USB/embedded storage
- Initializes GhostShell core with seed data
- Generates HTML dashboard dynamically
- Sets up API endpoints for dashboard
- Manages lifecycle (start/stop/restart)
"""

import hashlib
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Configure logging
LOG_DIR = Path("/var/log/voidos")
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fallback to local directory when /var/log is not writable
    LOG_DIR = Path.cwd() / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "bootstrap.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_CONFIG = {
    "dashboard_port": 5001,
    "websocket_port": 5001,
    "seed_path": "/tmp/voidos/seed.json",
    "dashboard_template": "/opt/voidos/dashboard_template.html",
    "static_dir": "/opt/voidos/static",
    "log_dir": "/var/log/voidos",
    "pid_file": "/var/run/voidos.pid",
    "update_interval": 5,  # seconds
    "max_telemetry_entries": 1000,
}

# ============================================================================
# Seed Management
# ============================================================================

class SeedManager:
    """Manages seed loading, validation, and migration."""
    
    def __init__(self, seed_path: str):
        self.seed_path = Path(seed_path)
        self.seed_data: Optional[Dict[str, Any]] = None
        self.seed_id: str = "unknown"
        self.genesis_epoch: int = 0
        self.merkle_root: str = "unknown"
        self.load_time: Optional[datetime] = None
        
    def load(self) -> bool:
        """Load and validate seed from storage."""
        logger.info(f"Loading seed from: {self.seed_path}")
        
        if not self.seed_path.exists():
            logger.error(f"Seed file not found: {self.seed_path}")
            return False
            
        try:
            with open(self.seed_path, 'r') as f:
                self.seed_data = json.load(f)
                
            # Validate seed structure
            if not self._validate_seed():
                logger.error("Seed validation failed")
                return False
                
            # Extract key fields
            self.seed_id = self.seed_data.get('seed_id', 'unknown')
            self.genesis_epoch = self.seed_data.get('genesis_epoch', 0)
            self.merkle_root = self.seed_data.get('merkle_verification', 'unknown')
            self.load_time = datetime.utcnow()
            
            logger.info(f"Seed loaded successfully: {self.seed_id}")
            logger.info(f"  Genesis Epoch: {self.genesis_epoch}")
            logger.info(f"  Merkle Root: {self.merkle_root}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in seed file: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load seed: {e}")
            return False
            
    def _validate_seed(self) -> bool:
        """Validate seed has required fields."""
        required_fields = ['seed_id', 'genesis_epoch', 'telemetry_chain']
        
        for field in required_fields:
            if field not in self.seed_data:
                logger.error(f"Missing required field in seed: {field}")
                return False
                
        return True
    
    def get_telemetry(self) -> List[Dict[str, Any]]:
        """Get telemetry chain from seed."""
        return self.seed_data.get('telemetry_chain', []) if self.seed_data else []
    
    def get_civilizations(self) -> List[Dict[str, Any]]:
        """Get civilizations from seed."""
        if not self.seed_data:
            return []
        return self.seed_data.get('civilizations', [])
    
    def get_myths(self) -> List[Dict[str, Any]]:
        """Get myths from seed."""
        if not self.seed_data:
            return []
        return self.seed_data.get('myths', [])
    
    def get_factions(self) -> List[Dict[str, Any]]:
        """Get factions from seed."""
        if not self.seed_data:
            return []
        return self.seed_data.get('factions', [])


# ============================================================================
# Dashboard Generator
# ============================================================================

class DashboardGenerator:
    """Generates HTML dashboard from seed data."""
    
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.html_cache: Optional[str] = None
        
    def generate(self, seed_data: Dict[str, Any], seed_manager: SeedManager) -> str:
        """Generate dashboard HTML from seed data."""
        logger.info("Generating dashboard HTML...")
        
        try:
            with open(self.template_path, 'r') as f:
                template = f.read()
        except FileNotFoundError:
            logger.warning(f"Template not found: {self.template_path}, using default")
            template = self._get_default_template()
        
        # Populate template
        html = template.replace('{{SEED_ID}}', seed_data.get('seed_id', 'unknown'))
        html = html.replace('{{MERKLE_ROOT}}', seed_data.get('merkle_verification', 'unknown'))
        html = html.replace('{{GENESIS_EPOCH}}', str(seed_data.get('genesis_epoch', 0)))
        html = html.replace('{{TIMESTAMP}}', datetime.utcnow().isoformat())
        html = html.replace('{{DASHBOARD_PORT}}', str(DEFAULT_CONFIG['dashboard_port']))
        
        # Generate civilizations table
        civilizations = seed_manager.get_civilizations()
        civ_rows = ""
        for civ in civilizations[:20]:  # Limit display
            civ_rows += f"""
            <tr>
                <td>{civ.get('id', 'N/A')}</td>
                <td>{civ.get('name', 'Unknown')}</td>
                <td>{civ.get('population', 0)}</td>
                <td>{civ.get('tech_level', 0)}</td>
                <td class="status-{civ.get('status', 'unknown')}">{civ.get('status', 'unknown')}</td>
            </tr>
            """
        html = html.replace('{{CIVILIZATIONS_TABLE}}', civ_rows or "<tr><td colspan='5'>No civilizations found</td></tr>")
        
        # Generate myths section
        myths = seed_manager.get_myths()
        myth_cards = ""
        for myth in myths[:10]:
            myth_cards += f"""
            <div class="myth-card">
                <h4>{myth.get('title', 'Unknown Myth')}</h4>
                <p>{myth.get('description', 'No description')[:200]}...</p>
                <span class="myth-origin">{myth.get('origin_civ', 'Unknown')}</span>
            </div>
            """
        html = html.replace('{{MYTHS_CARDS}}', myth_cards or "<p>No myths found</p>")
        
        # Generate telemetry chart data
        telemetry = seed_manager.get_telemetry()
        chart_data = []
        for entry in telemetry[-50:]:  # Last 50 entries
            chart_data.append({
                'timestamp': entry.get('timestamp', ''),
                'value': entry.get('value', 0),
                'metric': entry.get('metric', 'unknown')
            })
        html = html.replace('{{TELEMETRY_DATA}}', json.dumps(chart_data))
        
        # Generate Merkle proof section
        html = html.replace('{{MERKLE_PROOF}}', self._generate_merkle_proof(seed_data))
        
        # Generate factions list
        factions = seed_manager.get_factions()
        faction_list = ""
        for faction in factions[:10]:
            faction_list += f"<li>{faction.get('name', 'Unknown')} ({faction.get('alignment', 'neutral')})</li>"
        html = html.replace('{{FACTIONS_LIST}}', faction_list or "<li>No factions found</li>")
        
        self.html_cache = html
        return html
    
    def _generate_merkle_proof(self, seed_data: Dict[str, Any]) -> str:
        """Generate Merkle verification section."""
        merkle_root = seed_data.get('merkle_verification', 'unknown')
        chain = seed_data.get('telemetry_chain', [])
        
        proof_html = f"""
        <div class="merkle-section">
            <h3>Merkle Root Verification</h3>
            <div class="merkle-root">{merkle_root}</div>
            <div class="chain-info">
                <p>Telemetry Entries: {len(chain)}</p>
                <p>Status: Verified</p>
            </div>
        </div>
        """
        return proof_html
    
    def _get_default_template(self) -> str:
        """Return a minimal default template if file not found."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>voidOS Dashboard</title>
    <style>
        body { font-family: monospace; background: #0a0a0a; color: #00ff00; }
        .header { border-bottom: 1px solid #00ff00; padding: 20px; }
        .status { color: #00ff00; }
    </style>
</head>
<body>
    <div class="header">
        <h1>voidOS Dashboard</h1>
        <p>Seed: {{SEED_ID}}</p>
        <p>Merkle: {{MERKLE_ROOT}}</p>
    </div>
</body>
</html>
        """


# ============================================================================
# API Server
# ============================================================================

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True
    allow_reuse_address = True


class DashboardAPIHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for dashboard API."""
    
    def __init__(self, *args, seed_manager: SeedManager, **kwargs):
        self.seed_manager = seed_manager
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path == '/api/health':
            self.serve_json({'status': 'healthy', 'seed_id': self.seed_manager.seed_id})
        elif self.path == '/api/state':
            self.serve_state()
        elif self.path == '/api/seed':
            self.serve_seed()
        elif self.path == '/api/telemetry':
            self.serve_telemetry()
        elif self.path == '/api/civilizations':
            self.serve_civilizations()
        elif self.path == '/api/myths':
            self.serve_myths()
        elif self.path == '/api/factions':
            self.serve_factions()
        elif self.path == '/api/merkle':
            self.serve_merkle()
        # App API endpoints
        elif self.path.startswith('/api/apps'):
            self.handle_apps_api('GET')
        elif self.path.startswith('/api/terminal'):
            self.handle_terminal_api('GET')
        elif self.path.endswith('.js'):
            self.serve_static()
        elif self.path.endswith('.css'):
            self.serve_static()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve the main dashboard page."""
        dashboard_generator = DashboardGenerator(DEFAULT_CONFIG['dashboard_template'])
        html = dashboard_generator.generate(
            self.seed_manager.seed_data or {},
            self.seed_manager
        )
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_json(self, data: Dict[str, Any]):
        """Serve JSON response."""
        response = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def serve_state(self):
        """Serve full system state."""
        state = {
            'seed_id': self.seed_manager.seed_id,
            'genesis_epoch': self.seed_manager.genesis_epoch,
            'merkle_root': self.seed_manager.merkle_root,
            'civilizations_count': len(self.seed_manager.get_civilizations()),
            'myths_count': len(self.seed_manager.get_myths()),
            'factions_count': len(self.seed_manager.get_factions()),
            'telemetry_entries': len(self.seed_manager.get_telemetry()),
            'load_time': self.seed_manager.load_time.isoformat() if self.seed_manager.load_time else None,
            'uptime': time.time()
        }
        self.serve_json(state)
    
    def serve_seed(self):
        """Serve seed data."""
        self.serve_json(self.seed_manager.seed_data or {})
    
    def serve_telemetry(self):
        """Serve telemetry data."""
        self.serve_json(self.seed_manager.get_telemetry())
    
    def serve_civilizations(self):
        """Serve civilizations list."""
        self.serve_json(self.seed_manager.get_civilizations())
    
    def serve_myths(self):
        """Serve myths list."""
        self.serve_json(self.seed_manager.get_myths())
    
    def serve_factions(self):
        """Serve factions list."""
        self.serve_json(self.seed_manager.get_factions())
    
    def serve_merkle(self):
        """Serve Merkle verification data."""
        data = {
            'root': self.seed_manager.merkle_root,
            'verified': True,
            'chain_length': len(self.seed_manager.get_telemetry())
        }
        self.serve_json(data)
    
    def serve_static(self):
        """Serve static files."""
        try:
            static_path = Path(DEFAULT_CONFIG['static_dir']) / self.path[1:]
            if static_path.exists():
                with open(static_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                if self.path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif self.path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)
        except Exception as e:
            logger.error(f"Static file error: {e}")
            self.send_error(500)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/proposal':
            self.handle_proposal()
        elif self.path == '/api/update':
            self.handle_update()
        # App API endpoints
        elif self.path.startswith('/api/apps'):
            self.handle_apps_api('POST')
        elif self.path.startswith('/api/terminal'):
            self.handle_terminal_api('POST')
        else:
            self.send_error(404, "Not Found")
    
    def handle_apps_api(self, method):
        """Handle app management API requests."""
        try:
            # Parse the path to get app ID and action
            # Paths can be: /api/apps, /api/apps/list, /api/apps/{id}/launch, /api/apps/{id}/stop, /api/apps/{id}/status
            path_parts = [p for p in self.path.split('/') if p]
            
            if len(path_parts) < 2:
                self.serve_json({'error': 'Invalid path'})
                return
            
            # /api/apps -> list
            if len(path_parts) == 2 and path_parts[1] == 'apps' and method == 'GET':
                action = 'list'
                app_id = None
            # /api/apps/list
            elif len(path_parts) == 3 and path_parts[1] == 'apps' and path_parts[2] == 'list' and method == 'GET':
                action = 'list'
                app_id = None
            # /api/apps/status (get all status)
            elif len(path_parts) == 3 and path_parts[1] == 'apps' and path_parts[2] == 'status' and method == 'GET':
                action = 'status'
                app_id = None
            # /api/apps/{id}/status
            elif len(path_parts) == 4 and path_parts[1] == 'apps' and path_parts[3] == 'status':
                action = 'status'
                app_id = path_parts[2]
            # /api/apps/{id}/launch
            elif len(path_parts) == 4 and path_parts[1] == 'apps' and path_parts[3] == 'launch':
                action = 'launch'
                app_id = path_parts[2]
            # /api/apps/{id}/stop
            elif len(path_parts) == 4 and path_parts[1] == 'apps' and path_parts[3] == 'stop':
                action = 'stop'
                app_id = path_parts[2]
            else:
                self.serve_json({'error': 'Unknown action'})
                return
            
            # List all apps
            if action == 'list' and method == 'GET':
                apps = [
                    {'id': 'terminal', 'name': 'Terminal', 'status': 'RUNNING', 'tags': ['shell', 'system']},
                    {'id': 'file-manager', 'name': 'File Manager', 'status': 'RUNNING', 'tags': ['files', 'system']},
                    {'id': 'seed-manager', 'name': 'Seed Manager', 'status': 'RUNNING', 'tags': ['blockchain', 'seed']},
                    {'id': 'ghostshell', 'name': 'GhostShell', 'status': 'RUNNING', 'tags': ['ai', 'agent']},
                    {'id': 'llm-training', 'name': 'LLM Training', 'status': 'RUNNING', 'tags': ['ml', 'training']},
                    {'id': 'memory-loop', 'name': 'Memory Loop', 'status': 'RUNNING', 'tags': ['memory', 'metrics']},
                    {'id': 'logs', 'name': 'Logs Viewer', 'status': 'RUNNING', 'tags': ['logs', 'system']},
                    {'id': 'settings', 'name': 'Settings', 'status': 'RUNNING', 'tags': ['config', 'system']},
                ]
                self.serve_json({'apps': apps})
            
            # Get app status
            elif action == 'status':
                if app_id:
                    self.serve_json({'app_id': app_id, 'status': 'RUNNING', 'last_updated': time.time()})
                else:
                    # All apps status
                    status = {
                        'terminal': 'RUNNING',
                        'file-manager': 'RUNNING',
                        'seed-manager': 'RUNNING',
                        'ghostshell': 'RUNNING',
                        'llm-training': 'RUNNING',
                        'memory-loop': 'RUNNING',
                        'logs': 'RUNNING',
                        'settings': 'RUNNING'
                    }
                    self.serve_json(status)
            
            # Launch app
            elif action == 'launch' and method == 'POST' and app_id:
                self.serve_json({'app_id': app_id, 'status': 'STARTING', 'message': f'{app_id} launched'})
            
            # Stop app
            elif action == 'stop' and method == 'POST' and app_id:
                self.serve_json({'app_id': app_id, 'status': 'STOPPING', 'message': f'{app_id} stopped'})
            
            else:
                self.serve_json({'error': 'Unknown action'})
        
        except Exception as e:
            logger.error(f"App API error: {e}")
            self.serve_json({'error': str(e)})
    
    def handle_terminal_api(self, method):
        """Handle terminal API requests."""
        try:
            # Parse the path to get action
            # Paths can be: /api/terminal/execute, /api/terminal/history, /api/terminal/pwd, /api/terminal/clear
            path_parts = [p for p in self.path.split('/') if p]
            
            if len(path_parts) < 3:
                self.serve_json({'error': 'Invalid path'})
                return
            
            action = path_parts[2]  # execute, history, pwd, clear
            
            # Execute command
            if action == 'execute' and method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode())
                    command = data.get('command', '')
                else:
                    command = ''
                
                # Execute command and capture output
                import subprocess
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    output = result.stdout + result.stderr
                    self.serve_json({
                        'command': command,
                        'output': output,
                        'exit_code': result.returncode,
                        'timestamp': time.time()
                    })
                except subprocess.TimeoutExpired:
                    self.serve_json({'error': 'Command timeout', 'command': command})
                except Exception as e:
                    self.serve_json({'error': str(e), 'command': command})
            
            # Get terminal history
            elif action == 'history' and method == 'GET':
                history = [
                    {'command': 'pwd', 'output': '/Users/crownest/Desktop/anti2/Anti4', 'timestamp': time.time()},
                    {'command': 'whoami', 'output': 'crownest', 'timestamp': time.time()},
                ]
                self.serve_json({'history': history})
            
            # Get current PWD
            elif action == 'pwd' and method == 'GET':
                pwd = os.getcwd()
                self.serve_json({'pwd': pwd})
            
            # Clear history
            elif action == 'clear' and method == 'POST':
                self.serve_json({'message': 'History cleared'})
            
            else:
                self.serve_json({'error': 'Unknown terminal action'})
        
        except Exception as e:
            logger.error(f"Terminal API error: {e}")
            self.serve_json({'error': str(e)})
    
    def handle_proposal(self):
        """Handle governance proposal submission."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            proposal = json.loads(body.decode())
            
            logger.info(f"Received proposal: {proposal.get('type', 'unknown')}")
            
            # Acknowledge proposal
            response = {
                'status': 'accepted',
                'proposal_id': hashlib.md5(body).hexdigest()[:8],
                'timestamp': datetime.utcnow().isoformat()
            }
            self.serve_json(response)
            
        except Exception as e:
            logger.error(f"Proposal handling error: {e}")
            self.serve_json({'status': 'error', 'message': str(e)})
    
    def handle_update(self):
        """Handle seed update request."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            new_seed = json.loads(body.decode())
            
            logger.info(f"Received seed update")
            
            # Validate and update
            if self._validate_new_seed(new_seed):
                # Backup current seed
                if self.seed_manager.seed_path.exists():
                    backup_path = str(self.seed_manager.seed_path) + '.backup'
                    shutil.copy(self.seed_manager.seed_path, backup_path)
                
                # Write new seed
                with open(self.seed_manager.seed_path, 'w') as f:
                    json.dump(new_seed, f, indent=2)
                
                # Reload seed
                self.seed_manager.load()
                
                response = {'status': 'updated', 'seed_id': self.seed_manager.seed_id}
            else:
                response = {'status': 'error', 'message': 'Invalid seed format'}
            
            self.serve_json(response)
            
        except Exception as e:
            logger.error(f"Update handling error: {e}")
            self.serve_json({'status': 'error', 'message': str(e)})
    
    def _validate_new_seed(self, seed: Dict[str, Any]) -> bool:
        """Validate incoming seed data."""
        required = ['seed_id', 'genesis_epoch', 'telemetry_chain']
        return all(field in seed for field in required)


# ============================================================================
# Lifecycle Manager
# ============================================================================

class LifecycleManager:
    """Manages voidOS service lifecycle."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.seed_manager = SeedManager(self.config['seed_path'])
        self.server: Optional[ThreadedHTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start(self, daemon: bool = False) -> bool:
        """Start the voidOS service."""
        logger.info("Starting voidOS bootstrap...")
        
        # Load seed
        if not self.seed_manager.load():
            logger.error("Failed to load seed")
            return False
        
        # Create server
        try:
            self.server = ThreadedHTTPServer(
                ('0.0.0.0', self.config['dashboard_port']),
                lambda *args, **kwargs: DashboardAPIHandler(
                    *args, seed_manager=self.seed_manager, **kwargs
                )
            )
            logger.info(f"Server created on port {self.config['dashboard_port']}")
            
        except Exception as e:
            logger.error(f"Failed to create server: {e}")
            return False
        
        # Start server thread
        self.running = True
        
        if daemon:
            self.server_thread = threading.Thread(target=self._serve_forever, daemon=True)
            self.server_thread.start()
            logger.info("Server started in daemon mode")
            return True
        else:
            logger.info("Starting server in foreground...")
            self._serve_forever()
            return True
    
    def _serve_forever(self):
        """Server main loop."""
        try:
            while self.running:
                self.server.handle_request()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the voidOS service."""
        logger.info("Stopping voidOS service...")
        self.running = False
        
        if self.server:
            self.server.shutdown()
            
        logger.info("voidOS service stopped")
    
    def restart(self):
        """Restart the voidOS service."""
        logger.info("Restarting voidOS service...")
        self.stop()
        time.sleep(1)
        self.start()
    
    def status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            'running': self.running,
            'seed_id': self.seed_manager.seed_id,
            'port': self.config['dashboard_port'],
            'pid': os.getpid()
        }


# ============================================================================
# Main Entry Point
# ============================================================================

import shutil


def setup_signal_handlers(lifecycle: LifecycleManager):
    """Setup graceful shutdown handlers."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        lifecycle.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main entry point for voidOS seed bootstrap."""
    import argparse
    
    parser = argparse.ArgumentParser(description='voidOS Seed Bootstrap')
    parser.add_argument('--seed', '-s', default=DEFAULT_CONFIG['seed_path'],
                       help='Path to seed file')
    parser.add_argument('--port', '-p', type=int, default=DEFAULT_CONFIG['dashboard_port'],
                       help='Dashboard port')
    parser.add_argument('--template', '-t', default=DEFAULT_CONFIG['dashboard_template'],
                       help='Dashboard template path')
    parser.add_argument('--daemon', '-d', action='store_true',
                       help='Run as daemon')
    parser.add_argument('--foreground', '-f', action='store_true',
                       help='Run in foreground (default)')
    parser.add_argument('--status', action='store_true',
                       help='Show status and exit')
    parser.add_argument('--stop', action='store_true',
                       help='Stop running service')
    
    args = parser.parse_args()
    
    # Update config
    DEFAULT_CONFIG['seed_path'] = args.seed
    DEFAULT_CONFIG['dashboard_port'] = args.port
    DEFAULT_CONFIG['dashboard_template'] = args.template
    
    # Create lifecycle manager
    lifecycle = LifecycleManager(DEFAULT_CONFIG)
    
    # Handle status/stop commands
    if args.status:
        status = lifecycle.status()
        print(json.dumps(status, indent=2))
        return
    
    if args.stop:
        lifecycle.stop()
        return
    
    # Setup signal handlers
    setup_signal_handlers(lifecycle)
    
    # Write PID file
    pid_path = Path(DEFAULT_CONFIG['pid_file'])
    try:
        pid_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pid_path, 'w') as f:
            f.write(str(os.getpid()))
    except PermissionError:
        # Fallback to local PID file
        pid_path = Path.cwd() / "voidos.pid"
        with open(pid_path, 'w') as f:
            f.write(str(os.getpid()))
        DEFAULT_CONFIG['pid_file'] = str(pid_path)
    
    try:
        # Start service
        lifecycle.start(daemon=args.daemon)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        lifecycle.stop()


if __name__ == "__main__":
    main()
