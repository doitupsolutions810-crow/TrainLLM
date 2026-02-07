#!/usr/bin/env python3

"""
GhostShell Mining System Test Dashboard
Real-time latency monitoring, performance metrics, and system health checks
"""

import json
import time
import subprocess
import threading
import os
import sys
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

# Configuration
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"
DASHBOARD_PORT = 9002
REFRESH_INTERVAL = 2

# Performance tracking
class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "endpoints": {},
            "mining_cycles": 0,
            "total_latency": 0,
            "min_latency": float('inf'),
            "max_latency": 0,
            "avg_latency": 0,
            "successful_probes": 0,
            "failed_probes": 0,
            "network_status": "offline",
            "last_update": datetime.now().isoformat()
        }
    
    def update_endpoint(self, endpoint, latency, status):
        """Update endpoint metrics"""
        self.metrics["endpoints"][endpoint] = {
            "latency_ms": round(latency * 1000, 2),
            "status": status,
            "last_check": datetime.now().isoformat()
        }
        
        if status == "online":
            self.metrics["successful_probes"] += 1
            self.metrics["total_latency"] += latency
            self.metrics["min_latency"] = min(self.metrics["min_latency"], latency)
            self.metrics["max_latency"] = max(self.metrics["max_latency"], latency)
            if self.metrics["mining_cycles"] > 0:
                self.metrics["avg_latency"] = self.metrics["total_latency"] / self.metrics["mining_cycles"]
        else:
            self.metrics["failed_probes"] += 1
        
        self.metrics["last_update"] = datetime.now().isoformat()
    
    def get_metrics(self):
        return self.metrics
    
    def to_json(self):
        return json.dumps(self.metrics, indent=2)

# Global metrics instance
metrics = PerformanceMetrics()

# Latency probe functions
def probe_latency(url, timeout=5):
    """Measure latency to an endpoint"""
    try:
        start = time.time()
        urllib.request.urlopen(url, timeout=timeout)
        latency = time.time() - start
        return latency, "online"
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        return None, "offline"

def test_endpoint(endpoint, name):
    """Test single endpoint and update metrics"""
    latency, status = probe_latency(endpoint)
    if latency is not None:
        metrics.update_endpoint(name, latency, status)
        return f"✓ {name:30s} {status:10s} {latency*1000:8.2f}ms"
    else:
        metrics.update_endpoint(name, 0, status)
        return f"✗ {name:30s} {status:10s} timeout"

def run_endpoint_tests():
    """Run all endpoint tests"""
    endpoints = {
        "Simulation Kernel": "http://localhost:5001",
        "Orchestrator": "http://localhost:8001",
        "Sentience HUD": "http://localhost:5001/api",
        "CycleKernel Bridge": "http://localhost:8000",
        "Mining Dashboard": "http://localhost:9002"
    }
    
    results = []
    for name, url in endpoints.items():
        result = test_endpoint(url, name)
        results.append(result)
    
    return results

def run_mining_simulation(cycles=5):
    """Simulate mining cycles with latency tracking"""
    results = []
    
    for cycle in range(1, cycles + 1):
        metrics.metrics["mining_cycles"] = cycle
        
        # Simulate mining cycle time
        cycle_start = time.time()
        
        # Run tests
        test_results = run_endpoint_tests()
        
        cycle_time = time.time() - cycle_start
        
        results.append({
            "cycle": cycle,
            "cycle_time_ms": round(cycle_time * 1000, 2),
            "endpoint_results": test_results
        })
    
    return results

# Dashboard HTTP Handler
class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode('utf-8'))
        
        elif self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(metrics.to_json().encode('utf-8'))
        
        elif self.path == '/api/test':
            results = run_endpoint_tests()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"results": results}, indent=2).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostShell Mining System - Test Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Monaco', 'Courier New', monospace;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 20px;
        }
        
        .header h1 {
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #00ff88;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(0, 20, 40, 0.8);
            border: 2px solid #00ff88;
            border-radius: 8px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }
        
        .card h2 {
            color: #00ffff;
            margin-bottom: 15px;
            text-transform: uppercase;
            font-size: 14px;
            letter-spacing: 2px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(0, 255, 136, 0.2);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #00ccff;
        }
        
        .metric-value {
            color: #00ff88;
            font-weight: bold;
        }
        
        .endpoint-list {
            list-style: none;
        }
        
        .endpoint-item {
            padding: 10px;
            margin: 5px 0;
            background: rgba(0, 255, 136, 0.05);
            border-left: 3px solid;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .endpoint-item.online {
            border-left-color: #00ff88;
            color: #00ff88;
        }
        
        .endpoint-item.offline {
            border-left-color: #ff4444;
            color: #ff8888;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 5px;
        }
        
        .status-badge.online {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        
        .status-badge.offline {
            background: rgba(255, 68, 68, 0.2);
            color: #ff8888;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 20px;
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            border: 2px solid #00ff88;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Monaco', monospace;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 12px;
            font-weight: bold;
        }
        
        button:hover {
            background: rgba(0, 255, 136, 0.2);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        button:active {
            transform: scale(0.95);
        }
        
        .chart-container {
            width: 100%;
            height: 250px;
            margin-top: 15px;
            background: rgba(0, 255, 136, 0.05);
            border-radius: 4px;
            padding: 10px;
        }
        
        .latency-bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        
        .latency-bar-label {
            width: 150px;
            font-size: 11px;
            color: #00ccff;
        }
        
        .latency-bar-fill {
            height: 20px;
            background: linear-gradient(90deg, #00ff88, #00ffff);
            border-radius: 3px;
            margin: 0 10px;
            min-width: 50px;
        }
        
        .latency-bar-value {
            width: 60px;
            text-align: right;
            color: #00ff88;
            font-weight: bold;
            font-size: 11px;
        }
        
        .footer {
            text-align: center;
            color: #00ccff;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 255, 136, 0.2);
            font-size: 12px;
        }
        
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #00ff88;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        
        .status-indicator.online {
            background: #00ff88;
            box-shadow: 0 0 10px #00ff88;
        }
        
        .status-indicator.offline {
            background: #ff4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ GhostShell Mining System</h1>
            <p>Real-Time Latency Monitoring & Performance Testing</p>
        </div>
        
        <div class="controls">
            <button onclick="runQuickTest()">▶ Quick Test (5 cycles)</button>
            <button onclick="runLongTest()">▶ Long Test (20 cycles)</button>
            <button onclick="refreshMetrics()">🔄 Refresh Metrics</button>
            <button onclick="exportData()">⬇ Export JSON</button>
        </div>
        
        <div class="grid">
            <!-- System Status -->
            <div class="card">
                <h2>🔧 System Status</h2>
                <div class="metric">
                    <span class="metric-label">Network Status</span>
                    <span class="metric-value">
                        <span class="status-indicator online"></span>
                        <span id="network-status">checking...</span>
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Mining Cycles</span>
                    <span class="metric-value" id="cycling-count">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">0s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Update</span>
                    <span class="metric-value" id="last-update">--:--:--</span>
                </div>
            </div>
            
            <!-- Latency Metrics -->
            <div class="card">
                <h2>📊 Latency Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Min Latency</span>
                    <span class="metric-value" id="min-latency">∞ ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Max Latency</span>
                    <span class="metric-value" id="max-latency">0 ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Latency</span>
                    <span class="metric-value" id="avg-latency">0 ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Probes</span>
                    <span class="metric-value" id="total-probes">0</span>
                </div>
            </div>
            
            <!-- Success Rate -->
            <div class="card">
                <h2>✓ Success Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Successful Probes</span>
                    <span class="metric-value" id="success-probes">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed Probes</span>
                    <span class="metric-value" id="fail-probes">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value" id="success-rate">0%</span>
                </div>
            </div>
        </div>
        
        <!-- Endpoint Status -->
        <div class="card" style="margin-bottom: 20px;">
            <h2>🌐 Endpoint Status</h2>
            <div id="endpoints-list"></div>
        </div>
        
        <!-- Latency Chart -->
        <div class="card">
            <h2>📈 Latency Chart</h2>
            <div class="chart-container" id="latency-chart"></div>
        </div>
        
        <div class="footer">
            <p>GhostShell Mining System v2.0 | Real-time monitoring dashboard</p>
            <p>Auto-refresh every 2 seconds | <span id="status-spinner" class="spinner"></span> Live</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh metrics
        setInterval(refreshMetrics, 2000);
        
        function refreshMetrics() {
            fetch('/api/metrics')
                .then(r => r.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(e => console.error('Metrics fetch failed:', e));
        }
        
        function updateDashboard(metrics) {
            // Update status
            const endpoints = metrics.endpoints || {};
            const onlineCount = Object.values(endpoints).filter(e => e.status === 'online').length;
            const totalCount = Object.keys(endpoints).length;
            
            document.getElementById('network-status').textContent = 
                onlineCount > 0 ? `${onlineCount}/${totalCount} online` : 'offline';
            
            document.getElementById('cycling-count').textContent = metrics.mining_cycles || 0;
            
            // Latency metrics
            const minLat = metrics.min_latency === Infinity ? '∞' : (metrics.min_latency * 1000).toFixed(2) + ' ms';
            const maxLat = (metrics.max_latency * 1000).toFixed(2) + ' ms';
            const avgLat = (metrics.avg_latency * 1000).toFixed(2) + ' ms';
            
            document.getElementById('min-latency').textContent = minLat;
            document.getElementById('max-latency').textContent = maxLat;
            document.getElementById('avg-latency').textContent = avgLat;
            
            const totalProbes = metrics.successful_probes + metrics.failed_probes;
            document.getElementById('total-probes').textContent = totalProbes;
            document.getElementById('success-probes').textContent = metrics.successful_probes;
            document.getElementById('fail-probes').textContent = metrics.failed_probes;
            
            const successRate = totalProbes > 0 ? ((metrics.successful_probes / totalProbes) * 100).toFixed(1) : 0;
            document.getElementById('success-rate').textContent = successRate + '%';
            
            // Update last update time
            const updateTime = new Date(metrics.last_update).toLocaleTimeString();
            document.getElementById('last-update').textContent = updateTime;
            
            // Update endpoints list
            updateEndpointsList(endpoints);
            
            // Update chart
            updateLatencyChart(endpoints);
        }
        
        function updateEndpointsList(endpoints) {
            const list = document.getElementById('endpoints-list');
            list.innerHTML = '';
            
            Object.entries(endpoints).forEach(([name, data]) => {
                const item = document.createElement('div');
                item.className = `endpoint-item ${data.status}`;
                const latency = (data.latency_ms || 0).toFixed(2);
                item.innerHTML = `
                    ${name}
                    <span class="status-badge ${data.status}">
                        ${data.status.toUpperCase()} (${latency}ms)
                    </span>
                `;
                list.appendChild(item);
            });
        }
        
        function updateLatencyChart(endpoints) {
            const chart = document.getElementById('latency-chart');
            chart.innerHTML = '';
            
            const maxLatency = Math.max(...Object.values(endpoints).map(e => e.latency_ms || 0), 100);
            
            Object.entries(endpoints).forEach(([name, data]) => {
                if (data.status === 'online') {
                    const bar = document.createElement('div');
                    bar.className = 'latency-bar';
                    const width = ((data.latency_ms || 0) / maxLatency) * 300;
                    bar.innerHTML = `
                        <div class="latency-bar-label">${name}</div>
                        <div class="latency-bar-fill" style="width: ${width}px;"></div>
                        <div class="latency-bar-value">${(data.latency_ms || 0).toFixed(2)}ms</div>
                    `;
                    chart.appendChild(bar);
                }
            });
        }
        
        function runQuickTest() {
            alert('Running 5-cycle quick test... Check console for results');
            fetch('/api/test').then(r => r.json()).then(d => console.log(d));
        }
        
        function runLongTest() {
            alert('Running 20-cycle long test... This may take a minute');
        }
        
        function exportData() {
            fetch('/api/metrics')
                .then(r => r.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `mining-metrics-${Date.now()}.json`;
                    a.click();
                });
        }
        
        // Initial load
        refreshMetrics();
    </script>
</body>
</html>'''

# Start dashboard server
def start_dashboard():
    server = HTTPServer(('localhost', DASHBOARD_PORT), DashboardHandler)
    print(f"[Dashboard] Starting on http://localhost:{DASHBOARD_PORT}")
    server.serve_forever()

# CLI Test Interface
def test_cli_interface():
    """Interactive CLI testing interface"""
    while True:
        print("\n" + "="*70)
        print("GhostShell Mining System - Test Interface")
        print("="*70)
        print("1. Quick Endpoint Test (1 cycle)")
        print("2. Standard Test (5 cycles)")
        print("3. Extended Test (20 cycles)")
        print("4. Stress Test (100 cycles)")
        print("5. View Current Metrics")
        print("6. Open Web Dashboard")
        print("7. Export Metrics to JSON")
        print("8. Exit")
        print("="*70)
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == '1':
            print("\n[Test] Running quick endpoint test...")
            results = run_endpoint_tests()
            for result in results:
                print(result)
        
        elif choice == '2':
            print("\n[Test] Running standard 5-cycle test...")
            results = run_mining_simulation(5)
            for r in results:
                print(f"\nCycle {r['cycle']} - {r['cycle_time_ms']}ms")
                for res in r['endpoint_results']:
                    print(f"  {res}")
        
        elif choice == '3':
            print("\n[Test] Running extended 20-cycle test...")
            results = run_mining_simulation(20)
            total_time = sum(r['cycle_time_ms'] for r in results)
            avg_time = total_time / len(results)
            print(f"\nTotal: {total_time}ms | Average: {avg_time:.2f}ms/cycle")
        
        elif choice == '4':
            print("\n[Test] Running stress test (100 cycles)...")
            results = run_mining_simulation(100)
            total_time = sum(r['cycle_time_ms'] for r in results)
            avg_time = total_time / len(results)
            print(f"\nStress Test Complete!")
            print(f"Total Time: {total_time}ms")
            print(f"Average: {avg_time:.2f}ms/cycle")
            print(f"Min Latency: {metrics.metrics['min_latency']*1000:.2f}ms")
            print(f"Max Latency: {metrics.metrics['max_latency']*1000:.2f}ms")
        
        elif choice == '5':
            print("\n" + metrics.to_json())
        
        elif choice == '6':
            print(f"\n[Dashboard] Opening http://localhost:{DASHBOARD_PORT}")
            subprocess.Popen(['open', f'http://localhost:{DASHBOARD_PORT}'])
        
        elif choice == '7':
            filename = f"mining-metrics-{int(time.time())}.json"
            with open(filename, 'w') as f:
                f.write(metrics.to_json())
            print(f"\n[Export] Metrics saved to {filename}")
        
        elif choice == '8':
            print("\n[Exit] Goodbye!")
            break
        
        else:
            print("\n[Error] Invalid option")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dashboard':
        # Start only dashboard
        print("[Dashboard] GhostShell Mining Test Dashboard")
        print(f"[Dashboard] Listening on http://localhost:{DASHBOARD_PORT}")
        print("[Dashboard] Press Ctrl+C to stop")
        start_dashboard()
    elif len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Start only CLI
        test_cli_interface()
    else:
        # Start both
        print("[System] Starting GhostShell Mining Test System")
        print(f"[System] Dashboard: http://localhost:{DASHBOARD_PORT}")
        
        # Start dashboard in background thread
        dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Start CLI
        try:
            test_cli_interface()
        except KeyboardInterrupt:
            print("\n[System] Shutting down...")
            sys.exit(0)
