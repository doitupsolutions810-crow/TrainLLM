/**
 * SentienceHUD - React Component for voidOS
 * 
 * Installation:
 * npm install three lucide-react
 * 
 * Usage:
 * import SentienceHUD from './SentienceHUD';
 * 
 * <SentienceHUD
 *   onTriggerScan={handleScan}
 *   isAnalyzing={isScanning}
 *   geminiInsight={insightText}
 * />
 */

import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import {
  Ghost, Volume2, Sparkles, Terminal, Scan, Square,
  Brain, AlertCircle, Activity
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5001';
const POLL_INTERVAL = 1200; // ms

const MODE_COLORS = {
  'Heuristic/Exploratory':   '#ffaa00',
  'Rigorous/Systematic':     '#00aaff',
  'Stability/Conservative':  '#ff4444',
  'Balanced':                '#00ff88',
  'Locked / Fail-Closed':    '#991b1b'
};

/**
 * SentienceHUD Component
 * 
 * Provides real-time cognitive state monitoring with:
 * - Three.js particle visualization
 * - CycleKernel bridge polling
 * - Gemini AI insights
 * - TTS narration
 * - Emergency mode detection
 */
const SentienceHUD = ({ 
  onTriggerScan = () => {}, 
  isAnalyzing = false, 
  geminiInsight = '' 
}) => {
  const canvasRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const particlesRef = useRef(null);
  
  const [systemState, setSystemState] = useState({
    mode: 'Balanced',
    divergence_weight: 0,
    precision_bias: 0,
    velocity: 0,
    core_integrity: 1.0,
    epoch: 0,
    loading: true,
    error: null
  });
  
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [logEntries, setLogEntries] = useState([
    '[INIT] System online',
    '[INIT] Connecting to bridge...'
  ]);
  const [apps, setApps] = useState([]);

  // ─── Three.js Setup ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!canvasRef.current) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a001f, 0.0008);

    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    camera.position.set(0, 0, 80);

    const renderer = new THREE.WebGLRenderer({ 
      canvas: canvasRef.current, 
      antialias: true, 
      alpha: true 
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x0a0a0f, 1);

    sceneRef.current = scene;
    rendererRef.current = renderer;

    // Create particle nebula
    const createNebula = () => {
      if (particlesRef.current) scene.remove(particlesRef.current);

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

      const particles = new THREE.Points(geometry, material);
      scene.add(particles);
      particlesRef.current = particles;
    };

    createNebula();

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      if (particlesRef.current) {
        particlesRef.current.rotation.y += 0.0003;
        particlesRef.current.rotation.x += 0.0001;
      }
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  // ─── Poll CycleKernel Bridge ──────────────────────────────────────────────
  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/cycle-kernel`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        setSystemState({
          mode: data.mode || 'Balanced',
          divergence_weight: data.divergence_weight ?? 0,
          precision_bias: data.precision_bias ?? 0,
          velocity: data.velocity ?? 0,
          core_integrity: data.core_integrity ?? 1.0,
          epoch: data.epoch ?? 0,
          loading: false,
          error: null
        });

        addLog(`[UPDATE] Mode: ${data.mode} | Integrity: ${(data.core_integrity * 100).toFixed(1)}%`);
      } catch (err) {
        setSystemState(prev => ({ ...prev, loading: false, error: err.message }));
        addLog(`[ERROR] Bridge: ${err.message}`, 'critical');
      }
    };

    fetchState();
    const interval = setInterval(fetchState, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  // ─── Load Applications ─────────────────────────────────────────────────────
  useEffect(() => {
    const loadApps = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/apps`);
        const data = await response.json();
        setApps(data);
      } catch (err) {
        console.error('Failed to load apps:', err);
      }
    };

    loadApps();
  }, []);

  // ─── Logging Helper ───────────────────────────────────────────────────────
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogEntries(prev => {
      const updated = [...prev, `${timestamp} ${message}`];
      return updated.slice(-20); // Keep last 20 entries
    });
  };

  // ─── Gemini TTS ────────────────────────────────────────────────────────────
  const speakInsight = async () => {
    if (isSpeaking || !geminiInsight) return;

    setIsSpeaking(true);

    try {
      const response = await fetch(`${API_BASE}/api/gemini-tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: geminiInsight })
      });

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      
      audio.play().catch(console.error);
      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(url);
      };

      addLog('[TTS] Narrating insight');
    } catch (err) {
      console.error('TTS error:', err);
      setIsSpeaking(false);
      addLog('[ERROR] TTS failed', 'critical');
    }
  };

  // ─── Styling ──────────────────────────────────────────────────────────────
  const modeColor = MODE_COLORS[systemState.mode] || '#00ff88';
  const isCritical = systemState.core_integrity < 0.05;
  const integrityPercent = systemState.core_integrity * 100;

  return (
    <>
      {/* Canvas for particles */}
      <canvas 
        ref={canvasRef} 
        style={{ 
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'block',
          zIndex: 0
        }} 
      />

      {/* Emergency overlay */}
      {isCritical && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(200, 30, 30, 0.3)',
          backdropFilter: 'blur(5px)',
          zIndex: 50,
          pointerEvents: 'none',
          animation: 'pulse 1s infinite'
        }} />
      )}

      {/* Content */}
      <div style={{
        position: 'relative',
        height: '100%',
        width: '100%',
        padding: '20px',
        fontFamily: '"Courier New", monospace',
        zIndex: 10,
        overflow: 'auto'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          color: '#e0e0e0'
        }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#ff00ff',
            textShadow: '0 0 20px rgba(255, 0, 255, 0.5)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <Ghost size={32} /> GHOSTSHELL
          </h1>
          <div style={{ fontSize: '12px', color: '#888' }}>
            Core: <span style={{ color: isCritical ? '#ff4444' : '#10b981' }}>
              {integrityPercent.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Main Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr 1fr',
          gap: '20px',
          maxHeight: 'calc(100vh - 100px)',
          overflow: 'auto'
        }}>
          {/* Left Panel */}
          <div style={{
            background: 'rgba(26,26,37,0.85)',
            border: '1px solid rgba(42,42,58,0.5)',
            borderRadius: '8px',
            padding: '20px',
            backdropFilter: 'blur(10px)'
          }}>
            <h2 style={{
              fontSize: '14px',
              marginBottom: '15px',
              color: '#00ff88',
              textShadow: '0 0 10px rgba(0,255,136,0.3)',
              textTransform: 'uppercase',
              letterSpacing: '2px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Brain size={16} /> Cognitive State
            </h2>

            <div style={{
              textAlign: 'center',
              padding: '20px 0',
              border: '2px solid rgba(0,255,136,0.3)',
              borderRadius: '6px',
              marginBottom: '15px'
            }}>
              <div style={{
                fontSize: '28px',
                fontWeight: 'bold',
                margin: '10px 0',
                color: modeColor,
                textShadow: `0 0 15px ${modeColor}`
              }}>
                {systemState.mode.toUpperCase()}
              </div>
              {isCritical && (
                <div style={{
                  color: '#ff4444',
                  fontSize: '11px',
                  marginTop: '8px',
                  fontWeight: 'bold',
                  animation: 'pulse 1s infinite'
                }}>
                  FAIL-CLOSED ENGAGED
                </div>
              )}
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '10px'
            }}>
              <div style={{
                background: 'rgba(30,30,42,0.7)',
                border: '1px solid rgba(0,255,136,0.2)',
                borderRadius: '4px',
                padding: '10px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '10px', color: '#888' }}>DIVERGENCE</div>
                <div style={{ fontSize: '14px', color: '#00ff88', fontWeight: 'bold' }}>
                  {systemState.divergence_weight.toFixed(3)}
                </div>
              </div>
              <div style={{
                background: 'rgba(30,30,42,0.7)',
                border: '1px solid rgba(0,255,136,0.2)',
                borderRadius: '4px',
                padding: '10px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '10px', color: '#888' }}>PRECISION</div>
                <div style={{ fontSize: '14px', color: '#00ff88', fontWeight: 'bold' }}>
                  {systemState.precision_bias.toFixed(3)}
                </div>
              </div>
            </div>

            <button
              onClick={onTriggerScan}
              disabled={isAnalyzing}
              style={{
                width: '100%',
                marginTop: '15px',
                padding: '10px',
                background: 'rgba(139,92,246,0.1)',
                border: '1px solid #8b5cf6',
                color: '#a78bfa',
                borderRadius: '4px',
                cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                opacity: isAnalyzing ? 0.5 : 1,
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <Scan size={16} />
              {isAnalyzing ? 'SCANNING...' : 'TRIGGER SCAN'}
            </button>
          </div>

          {/* Center Panel */}
          <div style={{
            background: 'rgba(26,26,37,0.85)',
            border: '1px solid rgba(42,42,58,0.5)',
            borderRadius: '8px',
            padding: '20px',
            backdropFilter: 'blur(10px)'
          }}>
            <h2 style={{
              fontSize: '14px',
              marginBottom: '15px',
              color: '#00ff88',
              textShadow: '0 0 10px rgba(0,255,136,0.3)',
              textTransform: 'uppercase',
              letterSpacing: '2px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Sparkles size={16} /> Gemini Insight
            </h2>

            {geminiInsight && (
              <button
                onClick={speakInsight}
                disabled={isSpeaking}
                style={{
                  marginBottom: '15px',
                  padding: '8px 12px',
                  background: 'rgba(139,92,246,0.1)',
                  border: '1px solid #8b5cf6',
                  color: '#a78bfa',
                  borderRadius: '4px',
                  cursor: isSpeaking ? 'not-allowed' : 'pointer',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Volume2 size={14} />
                {isSpeaking ? 'NARRATING...' : 'NARRATE'}
              </button>
            )}

            <div style={{
              background: 'rgba(30,30,42,0.7)',
              borderLeft: '3px solid #8b5cf6',
              padding: '15px',
              borderRadius: '4px',
              minHeight: '150px',
              overflowY: 'auto',
              fontSize: '12px',
              lineHeight: 1.6,
              color: geminiInsight ? '#e0e0e0' : '#666',
              fontStyle: geminiInsight ? 'normal' : 'italic'
            }}>
              {geminiInsight || 'No insight generated yet.'}
            </div>
          </div>

          {/* Right Panel */}
          <div style={{
            background: 'rgba(26,26,37,0.85)',
            border: '1px solid rgba(42,42,58,0.5)',
            borderRadius: '8px',
            padding: '20px',
            backdropFilter: 'blur(10px)',
            overflow: 'auto'
          }}>
            <h2 style={{
              fontSize: '14px',
              marginBottom: '15px',
              color: '#00ff88',
              textShadow: '0 0 10px rgba(0,255,136,0.3)',
              textTransform: 'uppercase',
              letterSpacing: '2px'
            }}>
              🎯 Applications
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
              gap: '10px'
            }}>
              {apps.map((app, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(30,30,42,0.7)',
                    border: '1px solid rgba(0,255,136,0.3)',
                    borderRadius: '6px',
                    padding: '10px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s'
                  }}
                >
                  <div style={{ fontSize: '24px', marginBottom: '4px' }}>
                    {app.icon || '🔧'}
                  </div>
                  <div style={{ fontSize: '9px', color: '#00ff88' }}>
                    {app.name}
                  </div>
                </div>
              ))}
            </div>

            <h2 style={{
              fontSize: '14px',
              marginTop: '25px',
              marginBottom: '15px',
              color: '#00ff88'
            }}>
              📊 Metrics
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '10px'
            }}>
              <div style={{
                background: 'rgba(30,30,42,0.7)',
                border: '1px solid rgba(0,255,136,0.2)',
                borderRadius: '4px',
                padding: '10px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '10px', color: '#888' }}>VELOCITY</div>
                <div style={{ fontSize: '14px', color: '#00ff88', fontWeight: 'bold' }}>
                  {systemState.velocity.toFixed(2)}
                </div>
              </div>
              <div style={{
                background: 'rgba(30,30,42,0.7)',
                border: '1px solid rgba(0,255,136,0.2)',
                borderRadius: '4px',
                padding: '10px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '10px', color: '#888' }}>EPOCH</div>
                <div style={{ fontSize: '14px', color: '#00ff88', fontWeight: 'bold' }}>
                  {systemState.epoch}
                </div>
              </div>
            </div>

            <div style={{
              marginTop: '20px',
              fontSize: '10px',
              color: '#666',
              maxHeight: '150px',
              overflowY: 'auto',
              background: 'rgba(0,0,0,0.3)',
              padding: '10px',
              borderRadius: '4px'
            }}>
              {logEntries.map((log, idx) => (
                <div key={idx} style={{ margin: '2px 0' }}>
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SentienceHUD;
