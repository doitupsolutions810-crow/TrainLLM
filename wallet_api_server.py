#!/usr/bin/env python3

"""
GhostShell Mining Wallet API Server
REST API for wallet operations and mining management
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Import wallet manager
sys.path.insert(0, str(Path(__file__).parent))
from wallet_manager import WalletManager

wallet_manager = WalletManager()

class WalletAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for wallet API"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        try:
            if path == "/api/wallet/status":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                summary = wallet_manager.get_wallet_summary()
                response = {
                    "status": "success",
                    "data": summary
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == "/api/wallet/balance":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                wallet = wallet_manager.load_wallet()
                response = {
                    "status": "success",
                    "data": {
                        "total_mined": wallet["total_mined"],
                        "pooled_balance": wallet["pooled_balance"],
                        "available_balance": wallet["available_balance"],
                        "withdrawn_total": wallet["withdrawn_total"]
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == "/api/wallet/transactions":
                limit = int(query.get("limit", [50])[0])
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                history = wallet_manager.get_transaction_history(limit)
                response = {
                    "status": "success",
                    "data": history
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == "/api/exchange/rate":
                crypto = query.get("crypto", ["bitcoin"])[0]
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                rate = wallet_manager.get_usd_exchange_rate(crypto)
                response = {
                    "status": "success",
                    "data": {
                        "crypto": crypto,
                        "rate_usd": rate,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                html = self.get_dashboard_html()
                self.wfile.write(html.encode())
            
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = {"status": "error", "message": "Endpoint not found"}
                self.wfile.write(json.dumps(response).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body) if body else {}
            
            if path == "/api/wallet/deposit":
                amount = data.get("amount")
                source = data.get("source", "manual")
                
                if not amount or amount <= 0:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {"status": "error", "message": "Invalid amount"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                result = wallet_manager.deposit_mining_reward(amount, source)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = {
                    "status": "success",
                    "data": result
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif path == "/api/wallet/withdraw":
                amount = data.get("amount")
                address = data.get("address")
                address_type = data.get("address_type", "ethereum")
                
                if not amount or not address:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {"status": "error", "message": "Missing amount or address"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                result = wallet_manager.request_withdrawal(amount, address, address_type)
                
                status_code = 200 if result["status"] != "error" else 400
                self.send_response(status_code)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                self.wfile.write(json.dumps(result).encode())
            
            elif path == "/api/wallet/confirm":
                withdrawal_id = data.get("withdrawal_id")
                tx_hash = data.get("tx_hash")
                
                if not withdrawal_id or not tx_hash:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    
                    response = {"status": "error", "message": "Missing withdrawal_id or tx_hash"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                result = wallet_manager.confirm_withdrawal(withdrawal_id, tx_hash)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                self.wfile.write(json.dumps(result).encode())
            
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = {"status": "error", "message": "Endpoint not found"}
                self.wfile.write(json.dumps(response).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass
    
    @staticmethod
    def get_dashboard_html():
        """Get wallet dashboard HTML"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>GhostShell Mining Wallet</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Monaco', monospace;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #00ff00;
            padding: 20px 0;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
        }
        .wallet-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 {
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .stat {
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
        }
        .stat-label {
            font-weight: bold;
        }
        .stat-value {
            text-align: right;
        }
        .exchange-rate {
            font-size: 1.5em;
            text-align: center;
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            border-radius: 5px;
            margin-top: 10px;
        }
        .api-section {
            margin-top: 30px;
        }
        .api-info {
            background: rgba(0, 100, 255, 0.1);
            border: 2px solid #0064ff;
            border-radius: 10px;
            padding: 20px;
        }
        .api-info h3 {
            color: #0064ff;
            margin-bottom: 15px;
        }
        .endpoint {
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #0064ff;
            font-size: 0.9em;
            overflow-x: auto;
        }
        .endpoint-method {
            color: #ffff00;
            font-weight: bold;
        }
        .refresh-btn {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 20px;
            width: 100%;
        }
        .refresh-btn:hover {
            background: #00dd00;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #ffff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 GhostShell Mining Wallet 🔥</h1>
            <p>Real-time Mining Rewards Management</p>
        </div>
        
        <div id="content" class="loading">
            Loading wallet data...
        </div>
    </div>
    
    <script>
        async function loadWalletData() {
            try {
                const [statusRes, rateRes] = await Promise.all([
                    fetch('/api/wallet/status'),
                    fetch('/api/exchange/rate?crypto=bitcoin')
                ]);
                
                const statusData = await statusRes.json();
                const rateData = await rateRes.json();
                
                const status = statusData.data;
                const rate = rateData.data.rate_usd;
                
                const html = `
                    <div class="wallet-grid">
                        <div class="card">
                            <h2>💰 Mining Summary</h2>
                            <div class="stat">
                                <span class="stat-label">Total Mined:</span>
                                <span class="stat-value">${status.balances.total_mined.toFixed(8)} BTC</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">USD Value:</span>
                                <span class="stat-value">$${status.usd_values.total_mined_usd.toFixed(2)}</span>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>🏦 Wallet Balance</h2>
                            <div class="stat">
                                <span class="stat-label">Available:</span>
                                <span class="stat-value">${status.balances.available_balance.toFixed(8)} BTC</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">USD Value:</span>
                                <span class="stat-value">$${status.usd_values.available_balance_usd.toFixed(2)}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Pending Withdrawals:</span>
                                <span class="stat-value">${status.balances.pending_withdrawals}</span>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>💸 Withdrawn</h2>
                            <div class="stat">
                                <span class="stat-label">Total Withdrawn:</span>
                                <span class="stat-value">${status.balances.withdrawn_total.toFixed(8)} BTC</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">USD Value:</span>
                                <span class="stat-value">$${status.usd_values.withdrawn_total_usd.toFixed(2)}</span>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>📊 Exchange Rate</h2>
                            <div class="exchange-rate">
                                $${rate.toFixed(2)} / BTC
                            </div>
                            <div class="stat" style="margin-top: 15px;">
                                <span class="stat-label">Transactions:</span>
                                <span class="stat-value">${status.transactions_count}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="api-section">
                        <div class="api-info">
                            <h3>📡 API Endpoints</h3>
                            <p><strong>GET Requests:</strong></p>
                            <div class="endpoint">
                                <span class="endpoint-method">GET</span> /api/wallet/status - Full wallet status with USD values
                            </div>
                            <div class="endpoint">
                                <span class="endpoint-method">GET</span> /api/wallet/balance - Current balance information
                            </div>
                            <div class="endpoint">
                                <span class="endpoint-method">GET</span> /api/wallet/transactions - Transaction history
                            </div>
                            <div class="endpoint">
                                <span class="endpoint-method">GET</span> /api/exchange/rate?crypto=bitcoin - USD exchange rate
                            </div>
                            
                            <p style="margin-top: 20px;"><strong>POST Requests:</strong></p>
                            <div class="endpoint">
                                <span class="endpoint-method">POST</span> /api/wallet/deposit - Deposit mining rewards
                            </div>
                            <div class="endpoint">
                                <span class="endpoint-method">POST</span> /api/wallet/withdraw - Request withdrawal
                            </div>
                            <div class="endpoint">
                                <span class="endpoint-method">POST</span> /api/wallet/confirm - Confirm withdrawal with TX hash
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('content').innerHTML = html;
                
                // Refresh every 30 seconds
                setTimeout(loadWalletData, 30000);
            } catch (error) {
                document.getElementById('content').innerHTML = `
                    <div class="card" style="color: #ff0000;">
                        <h2>Error Loading Data</h2>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        // Load on page load
        loadWalletData();
    </script>
</body>
</html>"""


def run_server(host='localhost', port=9004):
    """Run the wallet API server"""
    server = HTTPServer((host, port), WalletAPIHandler)
    print(f"[Wallet API] Starting server on http://{host}:{port}")
    print(f"[Wallet API] Endpoints:")
    print(f"  GET  /api/wallet/status")
    print(f"  GET  /api/wallet/balance")
    print(f"  GET  /api/wallet/transactions")
    print(f"  GET  /api/exchange/rate")
    print(f"  POST /api/wallet/deposit")
    print(f"  POST /api/wallet/withdraw")
    print(f"  POST /api/wallet/confirm")
    print(f"[Wallet API] Dashboard: http://{host}:{port}/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Wallet API] Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostShell Wallet API Server')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=9004, help='Port to bind to')
    
    args = parser.parse_args()
    
    run_server(args.host, args.port)
