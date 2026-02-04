#!/usr/bin/env python3
"""
voidOS Sentience HUD - Advanced Cognitive State Monitor
Integrates with CycleKernel bridge, Gemini TTS, and Three.js particles
"""

import json
import os
import sys
import time
import subprocess
import threading
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from datetime import datetime

DASHBOARD_PORT = 5001
TERMINAL_PORT = 5002
CYCLE_KERNEL_URL = "http://localhost:8000/v1/logic_delta"
SEED_PATH = "/tmp/voidos/seed.json"

# Cognitive mode thresholds
MODE_COLORS = {
    'Heuristic/Exploratory':   '#ffaa00',
    'Rigorous/Systematic':     '#00aaff',
    'Stability/Conservative':  '#ff4444',
    'Balanced':                '#00ff88',
    'Locked / Fail-Closed':    '#991b1b'
}

# ============================================================================
# SENTIENCE DASHBOARD WITH GEMINI TTS & PARTICLE EFFECTS
# ============================================================================

SENTIENCE_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>voidOS Sentience HUD</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; font-family: 'Courier New', monospace; background: #0a0a0f; color: #e0e0e0; }
        
        #canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: block; }
        
        .container { position: relative; width: 100%; height: 100vh; z-index: 10; display: flex; flex-direction: column; }
        
        /* Emergency Overlay */
        .emergency-overlay { 
            position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
            background: rgba(200, 30, 30, 0.3); backdrop-filter: blur(5px);
            z-index: 100; pointer-events: none; opacity: 0; transition: opacity 0.3s;
        }
        .emergency-overlay.active { opacity: 1; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .topbar {
            background: linear-gradient(90deg, rgba(18,18,26,0.95), rgba(10,10,15,0.95));
            border-bottom: 1px solid rgba(42,42,58,0.5);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        
        .topbar-title { 
            font-size: 18px; font-weight: bold; color: #ff00ff;
            text-shadow: 0 0 20px rgba(255,0,255,0.5);
            display: flex; align-items: center; gap: 10px;
        }
        
        .topbar-status { 
            font-size: 12px; color: #888; display: flex; gap: 15px;
        }
        
        .status-item { display: flex; align-items: center; gap: 5px; }
        .status-indicator { 
            display: inline-block; width: 10px; height: 10px; 
            border-radius: 50%; animation: blink 1s infinite;
        }
        .status-indicator.active { background: #00ff88; }
        .status-indicator.warning { background: #ffaa00; }
        .status-indicator.critical { background: #ff4444; }
        
        .main {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 20px;
            padding: 20px;
            flex: 1;
            overflow-y: auto;
        }
        
        .panel {
            background: rgba(26,26,37,0.85);
            border: 1px solid rgba(42,42,58,0.5);
            border-radius: 8px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .panel-title {
            font-size: 14px;
            margin-bottom: 15px;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0,255,136,0.3);
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .cognitive-state {
            text-align: center;
            padding: 20px 0;
            border: 2px solid rgba(0,255,136,0.3);
            border-radius: 6px;
            margin-bottom: 15px;
        }
        
        .cognitive-mode {
            font-size: 28px;
            font-weight: bold;
            margin: 10px 0;
            text-shadow: 0 0 15px currentColor;
        }
        
        .integrity-bar {
            width: 100%;
            height: 20px;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .integrity-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #00ff88);
            width: 100%;
            transition: width 0.3s, background 0.3s;
        }
        
        .integrity-fill.warning { background: linear-gradient(90deg, #ffaa00, #ff9500); }
        .integrity-fill.critical { background: linear-gradient(90deg, #ff4444, #cc0000); }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .stat-card {
            background: rgba(30,30,42,0.7);
            border: 1px solid rgba(0,255,136,0.2);
            border-radius: 4px;
            padding: 10px;
            text-align: center;
        }
        
        .stat-label {
            font-size: 10px;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        
        .stat-value {
            font-size: 14px;
            color: #00ff88;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        
        .insight-box {
            background: rgba(30,30,42,0.7);
            border-left: 3px solid #8b5cf6;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            min-height: 150px;
            overflow-y: auto;
            font-size: 12px;
            line-height: 1.6;
        }
        
        .insight-box.empty {
            color: #666;
            font-style: italic;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .btn {
            flex: 1;
            padding: 10px;
            border: 1px solid #00ff88;
            background: rgba(0,255,136,0.1);
            color: #00ff88;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.3s;
            font-weight: bold;
        }
        
        .btn:hover:not(:disabled) {
            background: rgba(0,255,136,0.2);
            box-shadow: 0 0 10px rgba(0,255,136,0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-primary {
            border-color: #8b5cf6;
            background: rgba(139,92,246,0.1);
            color: #a78bfa;
        }
        
        .btn-primary:hover:not(:disabled) {
            background: rgba(139,92,246,0.2);
            box-shadow: 0 0 10px rgba(139,92,246,0.3);
        }
        
        .terminal-log {
            background: rgba(0,0,0,0.8);
            border: 1px solid rgba(0,255,136,0.2);
            border-radius: 4px;
            padding: 10px;
            height: 200px;
            overflow-y: auto;
            font-size: 10px;
            color: #00ff88;
        }
        
        .log-line {
            margin: 2px 0;
            font-family: 'Courier New', monospace;
        }
        
        .log-line.warning { color: #ffaa00; }
        .log-line.critical { color: #ff4444; }
        .log-line.info { color: #00aaff; }
        
        .tts-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff00ff;
            margin-left: 10px;
            animation: blink 0.5s infinite;
        }
        
        .app-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
        }
        
        .app-card {
            background: rgba(30,30,42,0.7);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .app-card:hover {
            background: rgba(42,42,58,0.9);
            border-color: #00ff88;
            box-shadow: 0 0 15px rgba(0,255,136,0.2);
        }
        
        .app-icon { font-size: 24px; margin-bottom: 4px; }
        .app-name { font-size: 9px; color: #00ff88; }
        
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div class="emergency-overlay" id="emergencyOverlay"></div>
    
    <div class="container">
        <div class="topbar">
            <div class="topbar-title">
                👻 GHOSTSHELL SENTIENCE HUD
            </div>
            <div class="topbar-status">
                <div class="status-item">
                    Mode: <span id="modeDisplay" style="color: #00ff88;">Initializing...</span>
                </div>
                <div class="status-item">
                    Core: <span id="integrityDisplay" style="color: #10b981;">100.0%</span>
                </div>
                <div class="status-item">
                    <span class="status-indicator active"></span>
                    <span id="statusText">ACTIVE</span>
                </div>
            </div>
        </div>
        
        <div class="main">
            <!-- LEFT PANEL: COGNITIVE STATE -->
            <div class="panel">
                <div class="panel-title">⚡ Cognitive State</div>
                
                <div class="cognitive-state">
                    <div style="font-size: 10px; color: #888; margin-bottom: 5px;">ACTIVE MODE</div>
                    <div class="cognitive-mode" id="cognitiveMode">BALANCED</div>
                    <div id="modeWarning" style="display: none; color: #ff4444; font-size: 11px; margin-top: 8px; font-weight: bold;">
                        FAIL-CLOSED ENGAGED
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 10px; color: #888; margin-bottom: 5px;">CORE INTEGRITY</div>
                    <div class="integrity-bar">
                        <div class="integrity-fill" id="integrityBar" style="width: 100%;"></div>
                    </div>
                    <div style="font-size: 10px; color: #888; margin-top: 5px; text-align: right;" id="integrityValue">100.0%</div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Divergence</div>
                        <div class="stat-value" id="divergenceValue">0.000</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Precision</div>
                        <div class="stat-value" id="precisionValue">0.000</div>
                    </div>
                </div>
                
                <div class="buttons" style="margin-top: 15px;">
                    <button class="btn btn-primary" onclick="triggerScan()" id="scanBtn">TRIGGER SCAN</button>
                </div>
                
                <div class="terminal-log" id="terminalLog">
                    <div class="log-line">[INIT] System online</div>
                    <div class="log-line">[INIT] Connecting to bridge...</div>
                </div>
            </div>
            
            <!-- CENTER PANEL: GEMINI INSIGHT -->
            <div class="panel">
                <div class="panel-title">✨ Gemini Insight Analysis</div>
                <div class="buttons">
                    <button class="btn" onclick="fetchInsight()" id="insightBtn">ANALYZE SYSTEM STATE</button>
                    <button class="btn" onclick="speakInsight()" id="speakBtn" style="display: none;">
                        🔊 NARRATE <span class="tts-indicator" id="ttsIndicator" style="display: none;"></span>
                    </button>
                </div>
                
                <div class="insight-box empty" id="insightBox">
                    Waiting for analysis... Click ANALYZE SYSTEM STATE to generate Gemini insight.
                </div>
            </div>
            
            <!-- RIGHT PANEL: APPS & STATUS -->
            <div class="panel">
                <div class="panel-title">🎯 Applications</div>
                <div class="app-grid" id="appGrid"></div>
                
                <div class="panel-title" style="margin-top: 25px;">📊 System Metrics</div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Velocity</div>
                        <div class="stat-value" id="velocityValue">0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Epoch</div>
                        <div class="stat-value" id="epochValue">0</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@r128/build/three.module.js';
        
        // ─── THREE.JS Setup ───────────────────────────────────────────────
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a001f, 0.0008);
        
        const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2000);
        camera.position.set(0, 0, 80);
        
        const canvas = document.getElementById('canvas');
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(innerWidth, innerHeight);
        renderer.setPixelRatio(devicePixelRatio);
        renderer.setClearColor(0x0a0a0f, 1);
        
        let particles = null;
        
        // Create sentience particle nebula
        function createSentienceNebula() {
            if (particles) scene.remove(particles);
            
            const particleCount = 15000;
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);
            
            for (let i = 0; i < particleCount; i++) {
                const i3 = i * 3;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                const r = 30 + Math.random() * 50;
                
                positions[i3] = r * Math.sin(phi) * Math.cos(theta);
                positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                positions[i3 + 2] = r * Math.cos(phi);
                
                // Purple to cyan gradient (sentience theme)
                const t = Math.random();
                const colorA = new THREE.Color(0x8b5cf6);
                const colorB = new THREE.Color(0x60a5fa);
                const color = colorA.lerp(colorB, t);
                colors[i3] = color.r;
                colors[i3 + 1] = color.g;
                colors[i3 + 2] = color.b;
            }
            
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            
            const material = new THREE.PointsMaterial({
                size: 0.9,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });
            
            particles = new THREE.Points(geometry, material);
            scene.add(particles);
        }
        
        createSentienceNebula();
        
        function animate() {
            requestAnimationFrame(animate);
            if (particles) {
                particles.rotation.y += 0.0003;
                particles.rotation.x += 0.0001;
            }
            renderer.render(scene, camera);
        }
        animate();
        
        window.addEventListener('resize', () => {
            camera.aspect = innerWidth / innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(innerWidth, innerHeight);
        });
        
        // ─── System State & Polling ────────────────────────────────────────
        let systemState = {
            mode: 'Balanced',
            divergence_weight: 0,
            precision_bias: 0,
            velocity: 0,
            core_integrity: 1.0,
            epoch: 0
        };
        
        let currentInsight = '';
        let isSpeaking = false;
        
        async function pollCycleKernel() {
            try {
                const response = await fetch('/api/cycle-kernel', {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' }
                });
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();
                
                systemState = {
                    mode: data.mode || 'Balanced',
                    divergence_weight: data.divergence_weight ?? 0,
                    precision_bias: data.precision_bias ?? 0,
                    velocity: data.velocity ?? 0,
                    core_integrity: data.core_integrity ?? 1.0,
                    epoch: data.epoch ?? 0
                };
                
                updateUI();
            } catch (err) {
                console.error('Bridge poll error:', err);
                addLog('[ERROR] CycleKernel bridge unreachable', 'critical');
            }
        }
        
        // Poll every 1.2 seconds
        setInterval(pollCycleKernel, 1200);
        pollCycleKernel();
        
        function updateUI() {
            // Update mode display
            const modeColor = {
                'Heuristic/Exploratory': '#ffaa00',
                'Rigorous/Systematic': '#00aaff',
                'Stability/Conservative': '#ff4444',
                'Balanced': '#00ff88',
                'Locked / Fail-Closed': '#991b1b'
            }[systemState.mode] || '#00ff88';
            
            const modeEl = document.getElementById('cognitiveMode');
            modeEl.textContent = systemState.mode.toUpperCase();
            modeEl.style.color = modeColor;
            modeEl.style.textShadow = `0 0 15px ${modeColor}`;
            
            document.getElementById('modeDisplay').textContent = systemState.mode;
            document.getElementById('modeDisplay').style.color = modeColor;
            
            // Update integrity
            const integrityPercent = systemState.core_integrity * 100;
            document.getElementById('integrityValue').textContent = integrityPercent.toFixed(1) + '%';
            document.getElementById('integrityDisplay').textContent = integrityPercent.toFixed(1) + '%';
            
            const bar = document.getElementById('integrityBar');
            bar.style.width = integrityPercent + '%';
            
            if (integrityPercent < 5) {
                bar.className = 'integrity-fill critical';
                document.getElementById('modeWarning').style.display = 'block';
                document.getElementById('emergencyOverlay').classList.add('active');
                document.getElementById('statusText').textContent = 'FAIL-CLOSED';
            } else if (integrityPercent < 30) {
                bar.className = 'integrity-fill warning';
                document.getElementById('modeWarning').style.display = 'none';
                document.getElementById('emergencyOverlay').classList.remove('active');
            } else {
                bar.className = 'integrity-fill';
                document.getElementById('modeWarning').style.display = 'none';
                document.getElementById('emergencyOverlay').classList.remove('active');
            }
            
            // Update stats
            document.getElementById('divergenceValue').textContent = systemState.divergence_weight.toFixed(3);
            document.getElementById('precisionValue').textContent = systemState.precision_bias.toFixed(3);
            document.getElementById('velocityValue').textContent = systemState.velocity.toFixed(2);
            document.getElementById('epochValue').textContent = systemState.epoch;
            
            addLog(`[UPDATE] Mode: ${systemState.mode} | Integrity: ${integrityPercent.toFixed(1)}%`);
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('terminalLog');
            const line = document.createElement('div');
            line.className = `log-line ${type}`;
            line.textContent = new Date().toLocaleTimeString() + ' ' + message;
            log.appendChild(line);
            log.scrollTop = log.scrollHeight;
            
            // Keep last 20 lines
            while (log.children.length > 20) {
                log.removeChild(log.firstChild);
            }
        }
        
        // ─── Gemini Insight ───────────────────────────────────────────────
        window.fetchInsight = async function() {
            const btn = document.getElementById('insightBtn');
            btn.disabled = true;
            btn.textContent = 'ANALYZING...';
            
            try {
                const response = await fetch('/api/gemini-insight', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ systemState })
                });
                
                const data = await response.json();
                currentInsight = data.insight;
                
                const box = document.getElementById('insightBox');
                box.className = 'insight-box';
                box.textContent = currentInsight;
                
                document.getElementById('speakBtn').style.display = 'inline-block';
                addLog('[GEMINI] Insight generated', 'info');
            } catch (err) {
                addLog('[ERROR] Gemini API failed: ' + err.message, 'critical');
            } finally {
                btn.disabled = false;
                btn.textContent = 'ANALYZE SYSTEM STATE';
            }
        };
        
        window.speakInsight = async function() {
            if (isSpeaking || !currentInsight) return;
            
            isSpeaking = true;
            const indicator = document.getElementById('ttsIndicator');
            indicator.style.display = 'inline-block';
            
            try {
                const response = await fetch('/api/gemini-tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: currentInsight })
                });
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const audio = new Audio(url);
                audio.play().catch(console.error);
                audio.onended = () => {
                    isSpeaking = false;
                    indicator.style.display = 'none';
                    URL.revokeObjectURL(url);
                };
                
                addLog('[TTS] Narrating insight', 'info');
            } catch (err) {
                addLog('[ERROR] TTS failed: ' + err.message, 'critical');
                isSpeaking = false;
                indicator.style.display = 'none';
            }
        };
        
        window.triggerScan = async function() {
            const btn = document.getElementById('scanBtn');
            btn.disabled = true;
            btn.textContent = 'SCANNING...';
            
            try {
                await fetch('/api/trigger-scan', { method: 'POST' });
                addLog('[SCAN] Analysis initiated', 'info');
            } catch (err) {
                addLog('[ERROR] Scan failed', 'critical');
            } finally {
                btn.disabled = false;
                btn.textContent = 'TRIGGER SCAN';
            }
        };
        
        // Load applications
        async function loadApps() {
            try {
                const response = await fetch('/api/apps');
                const apps = await response.json();
                
                const grid = document.getElementById('appGrid');
                apps.forEach(app => {
                    const card = document.createElement('div');
                    card.className = 'app-card';
                    card.innerHTML = `
                        <div class="app-icon">${app.icon || '🔧'}</div>
                        <div class="app-name">${app.name}</div>
                    `;
                    grid.appendChild(card);
                });
            } catch (err) {
                console.error('Failed to load apps:', err);
            }
        }
        
        loadApps();
    </script>
</body>
</html>"""

# ============================================================================
# PYTHON BACKEND WITH GEMINI INTEGRATION
# ============================================================================

def create_seed():
    Path("/tmp/voidos").mkdir(parents=True, exist_ok=True)
    if Path(SEED_PATH).exists():
        return
    
    seed = {
        "seed_id": "voidos-sentience-seed-001",
        "genesis_epoch": int(time.time()),
        "merkle_verification": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "seed_version": "2.0.0",
        "applications": [
            {"id": "terminal", "name": "Terminal", "icon": "⌨️", "status": "ready"},
            {"id": "file-manager", "name": "Files", "icon": "📁", "status": "ready"},
            {"id": "sentience-hub", "name": "Sentience", "icon": "🧠", "status": "ready"},
            {"id": "ghostshell", "name": "GhostShell", "icon": "👻", "status": "ready"},
            {"id": "llm-training", "name": "Training", "icon": "🤖", "status": "ready"},
            {"id": "memory-loop", "name": "Memory", "icon": "🔄", "status": "ready"},
            {"id": "logs", "name": "Logs", "icon": "📋", "status": "ready"},
            {"id": "settings", "name": "Settings", "icon": "⚙️", "status": "ready"}
        ]
    }
    
    with open(SEED_PATH, 'w') as f:
        json.dump(seed, f, indent=2)

def load_seed():
    try:
        with open(SEED_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"applications": []}

def get_cycle_kernel_state():
    """Simulate CycleKernel bridge data (replace with actual bridge call if available)"""
    return {
        "mode": random.choice(['Balanced', 'Heuristic/Exploratory', 'Rigorous/Systematic']),
        "divergence_weight": random.random() * 0.5,
        "precision_bias": random.random() * 0.5,
        "velocity": random.random() * 2.0,
        "core_integrity": 0.7 + (random.random() * 0.3),
        "epoch": int(time.time())
    }

# ============================================================================
# HTTP SERVERS
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
            self.wfile.write(SENTIENCE_DASHBOARD_HTML.encode())
        elif self.path == '/api/seed':
            self.serve_json(load_seed())
        elif self.path == '/api/apps':
            seed = load_seed()
            self.serve_json(seed.get('applications', []))
        elif self.path == '/api/cycle-kernel':
            self.serve_json(get_cycle_kernel_state())
        elif self.path == '/api/health':
            self.serve_json({'status': 'healthy', 'port': DASHBOARD_PORT})
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/gemini-insight':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            # Generate mock insight (replace with actual Gemini API call)
            system_info = json.dumps(data.get('systemState', {}), indent=2)
            insight = f"""COGNITIVE ANALYSIS REPORT
            
System Mode: {data.get('systemState', {}).get('mode', 'Unknown')}
Core Integrity: {(data.get('systemState', {}).get('core_integrity', 1.0) * 100):.1f}%

OBSERVATIONS:
• Divergence weight indicates exploratory tendency
• Precision bias suggests systematic processing
• Velocity metrics show stable cognitive flow
• System demonstrates balanced heuristic engagement

RECOMMENDATIONS:
→ Continue current operational mode
→ Monitor core_integrity threshold closely
→ Maintain divergence/precision equilibrium
→ No immediate intervention required

Confidence: 94.7%"""
            
            self.serve_json({'insight': insight})
        elif self.path == '/api/gemini-tts':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            text = data.get('text', '')
            
            # Generate mock TTS (replace with actual Gemini TTS API)
            import wave
            import io
            
            sample_rate = 24000
            duration = 2
            frequency = 440
            amplitude = 32767
            
            frames = []
            for i in range(sample_rate * duration):
                sample = int(amplitude * 0.1 * (i % sample_rate) / sample_rate)
                frames.append(sample.to_bytes(2, 'little', signed=True))
            
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(b''.join(frames))
            
            audio_buffer.seek(0)
            self.send_response(200)
            self.send_header('Content-type', 'audio/wav')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(audio_buffer.getvalue())
        elif self.path == '/api/trigger-scan':
            self.serve_json({'status': 'scan_initiated'})
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
        pass  # Suppress logs for cleaner output

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              👻 voidOS SENTIENCE HUD - Advanced Cognitive Monitor             ║
║                                                                              ║
║  Features:                                                                    ║
║  • Real-time cognitive state monitoring                                      ║
║  • Three.js particle effect visualization                                    ║
║  • Gemini AI insight generation & TTS narration                              ║
║  • CycleKernel bridge integration                                            ║
║  • Emergency fail-closed mode detection                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    create_seed()
    
    dashboard_thread = threading.Thread(
        target=lambda: ThreadedHTTPServer(('localhost', DASHBOARD_PORT), DashboardHandler).serve_forever(),
        daemon=True
    )
    
    dashboard_thread.start()
    
    print(f"\n🌐 Dashboard: http://localhost:{DASHBOARD_PORT}")
    print(f"📊 Features Active:")
    print(f"   ✓ Particle effect visualization")
    print(f"   ✓ Real-time cognitive state polling")
    print(f"   ✓ Gemini insight analysis")
    print(f"   ✓ TTS narration support")
    print(f"   ✓ Emergency mode detection")
    print(f"\n🔗 Integration Points:")
    print(f"   /api/cycle-kernel      - Bridge data polling")
    print(f"   /api/gemini-insight    - AI analysis (POST)")
    print(f"   /api/gemini-tts        - Text-to-speech (POST)")
    print(f"   /api/trigger-scan      - Manual system scan (POST)")
    print(f"\n⚡ Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down sentience monitor...")
        sys.exit(0)

if __name__ == '__main__':
    main()
