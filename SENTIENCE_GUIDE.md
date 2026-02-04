# voidOS Sentience HUD - Integration Guide

## Overview

The **Sentience HUD** is an advanced cognitive monitoring system that integrates:

- **Three.js particle visualizations** - Real-time animated nebula background
- **CycleKernel bridge** - Polling system state every 1.2 seconds
- **Gemini AI** - Dynamic insight generation and TTS narration
- **Emergency mode detection** - Visual alerts when core integrity < 5%
- **Real-time metrics** - Divergence, precision, velocity, epoch tracking

## Architecture

```
┌─────────────────────────────────────────┐
│        Sentience HUD Dashboard          │
│  (HTML5 + Three.js + Vanilla JS)       │
├─────────────────────────────────────────┤
│                                          │
│  Left Panel          Center Panel        │
│  • Cognitive State   • Gemini Insight   │
│  • Integrity Bar     • TTS Controls     │
│  • Stats            • Analysis Logs    │
│  • Trigger Scan                        │
│                                          │
│  Right Panel                             │
│  • Applications Grid                     │
│  • System Metrics                       │
│                                          │
├─────────────────────────────────────────┤
│         Three.js Particle Nebula        │
│    (Purple/Cyan gradient animation)    │
└─────────────────────────────────────────┘
         ↓
   Backend (Python)
         ↓
   ┌──────────────────┐
   │ /api/cycle-kernel│ → CycleKernel bridge polling
   │ /api/gemini-*    │ → Gemini API integration
   │ /api/apps        │ → Application list
   │ /api/seed        │ → Seed configuration
   └──────────────────┘
```

## Installation

### 1. Basic Setup

```bash
# Navigate to voidOS directory
cd /Users/crownest/Desktop/anti2/Anti4

# Make executable
chmod +x voidos_sentience.py

# Run
python3 voidos_sentience.py
```

### 2. Gemini API Setup (Optional - for real TTS/Insights)

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey):

```bash
# Set environment variable
export GEMINI_API_KEY="your-key-here"

# Or add to ~/.zshrc or ~/.bash_profile
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. CycleKernel Bridge Integration (Optional)

If you have a CycleKernel server running:

```python
# In voidos_sentience.py, modify get_cycle_kernel_state():

async def get_cycle_kernel_state():
    try:
        response = await fetch('http://your-kernel-host:8000/v1/logic_delta')
        return await response.json()
    except:
        # Fallback to mock data
        return {...}
```

## API Endpoints

### GET `/api/cycle-kernel`
Returns current cognitive state from CycleKernel bridge:

```json
{
  "mode": "Balanced",
  "divergence_weight": 0.345,
  "precision_bias": 0.234,
  "velocity": 1.23,
  "core_integrity": 0.95,
  "epoch": 1707000000
}
```

### POST `/api/gemini-insight`
Generate AI insight from system state:

**Request:**
```json
{
  "systemState": {
    "mode": "Balanced",
    "core_integrity": 0.95,
    "divergence_weight": 0.345
  }
}
```

**Response:**
```json
{
  "insight": "COGNITIVE ANALYSIS REPORT\n\nSystem Mode: Balanced\nCore Integrity: 95.0%\n\n..."
}
```

### POST `/api/gemini-tts`
Convert insight text to audio:

**Request:**
```json
{
  "text": "System operating in balanced mode..."
}
```

**Response:**
- Binary WAV audio file (Content-Type: audio/wav)

### POST `/api/trigger-scan`
Initiate system analysis:

```json
{
  "status": "scan_initiated"
}
```

## UI Components

### Cognitive State Panel (Left)

**Mode Display**
- Color-coded by operational mode
- Real-time updates from bridge
- Modes:
  - 🟡 Heuristic/Exploratory (#ffaa00)
  - 🔵 Rigorous/Systematic (#00aaff)
  - 🔴 Stability/Conservative (#ff4444)
  - 🟢 Balanced (#00ff88)
  - ⚫ Locked/Fail-Closed (#991b1b)

**Integrity Bar**
- Dynamic color gradient
- 🟢 Green (>70%)
- 🟡 Yellow (30-70%)
- 🔴 Red (<30%)

**Emergency Overlay**
- Red tint + blur effect when core_integrity < 5%
- Pulsing animation
- Coupled with "FAIL-CLOSED" warning text

### Insight Panel (Center)

**Analyze System State**
- Generates real-time analysis
- Uses mock data if Gemini API unavailable
- Shows cognitive assessment

**Narrate**
- TTS conversion using Gemini API
- Voice changes based on system state
  - Normal: "Leda" voice
  - Critical: "Fenrir" voice
- Pulsing speaker indicator during playback

### Metrics Panel (Right)

- Application grid (8 apps from seed)
- System metrics display
- Real-time updates

## Configuration

### Colors & Themes

Edit `MODE_COLORS` dictionary:

```python
MODE_COLORS = {
    'Heuristic/Exploratory':   '#ffaa00',
    'Rigorous/Systematic':     '#00aaff',
    'Stability/Conservative':  '#ff4444',
    'Balanced':                '#00ff88',
    'Locked / Fail-Closed':    '#991b1b'
}
```

### Polling Interval

Adjust CycleKernel polling (default: 1.2s):

```javascript
// In dashboard HTML
setInterval(pollCycleKernel, 1200); // milliseconds
```

### Particle Settings

Modify nebula configuration:

```javascript
function createSentienceNebula() {
    const particleCount = 15000;  // Adjust density
    const r = 30 + Math.random() * 50;  // Adjust size
    // ... rotation speeds, colors, etc.
}
```

## Real Gemini API Integration

To use actual Gemini APIs instead of mock data:

### 1. Gemini Insights

```python
import google.generativeai as genai

def get_gemini_insight(system_state: dict) -> str:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Analyze this system cognitive state and provide clinical insights:
    {json.dumps(system_state, indent=2)}
    
    Provide a brief, technical analysis focusing on:
    - Current operational mode
    - Risk assessment
    - Recommendations
    """
    
    response = model.generate_content(prompt)
    return response.text
```

### 2. Gemini TTS

```python
import requests

def gemini_tts(text: str, api_key: str) -> bytes:
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}',
        headers={'Content-Type': 'application/json'},
        json={
            'contents': [{'parts': [{'text': text}]}],
            'generationConfig': {
                'responseModalities': ['AUDIO'],
                'speechConfig': {
                    'voiceConfig': {
                        'prebuiltVoiceConfig': {
                            'voiceName': 'Leda'  # or 'Fenrir' for critical
                        }
                    }
                }
            }
        }
    )
    return response.content
```

### 3. Update Handler

```python
class DashboardHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/gemini-insight':
            data = json.loads(self.rfile.read(...))
            insight = get_gemini_insight(data['systemState'])
            self.serve_json({'insight': insight})
        elif self.path == '/api/gemini-tts':
            data = json.loads(self.rfile.read(...))
            audio = gemini_tts(data['text'], os.getenv('GEMINI_API_KEY'))
            # Send audio response
```

## Troubleshooting

### Dashboard Not Loading
- Check port 5001 is available: `lsof -i :5001`
- Clear browser cache: Cmd+Shift+Delete
- Check console for errors: F12

### CycleKernel Bridge Not Connecting
- Verify bridge is running: `curl http://localhost:8000/v1/logic_delta`
- Check firewall settings
- Update API_URL if running on different host

### Gemini API Errors
- Verify API key is set: `echo $GEMINI_API_KEY`
- Check quota limits in Google AI Studio
- Ensure request format matches API spec

### Particle Performance Issues
- Reduce `particleCount` in `createSentienceNebula()`
- Disable animations on slower systems
- Lower camera resolution

## Advanced Customization

### Custom Cognitive Modes

```javascript
// Add new mode colors
MODE_COLORS['Quantum/Superposition'] = '#ff00ff';

// Update mode display logic
const customModes = ['Balanced', 'Your', 'Modes'];
```

### Custom Particle Effects

Create alternate nebula styles:

```javascript
function createCriticalNebula() {
    // Red/orange particles for emergency state
    const colorA = new THREE.Color(0xff4444);
    const colorB = new THREE.Color(0xffaa00);
    // ... rest of implementation
}
```

### Integration with External Systems

```javascript
// Hook to custom event handlers
window.addEventListener('CoreIntegrityChange', (e) => {
    if (e.detail.integrity < 0.5) {
        // Trigger custom alerts
        notifyExternalSystem(e.detail);
    }
});
```

## Performance Metrics

- **Particle Count:** 15,000 (adjustable)
- **Polling Interval:** 1.2 seconds
- **Target FPS:** 60fps (Three.js)
- **Memory Footprint:** ~50MB (Chrome)
- **Network:** ~2KB per poll

## Next Steps

1. ✅ Start system: `python3 voidos_sentience.py`
2. ✅ Visit dashboard: http://localhost:5001
3. ✅ Set Gemini API key for real insights
4. ✅ Configure CycleKernel bridge URL if available
5. ✅ Customize colors and particle effects
6. ✅ Integrate with your application

## Support

For issues or questions:
- Check terminal output for error messages
- Review browser console (F12)
- Verify all dependencies installed
- Check API endpoints are accessible

---

**Last Updated:** February 4, 2026  
**Version:** 2.0.0 Sentience Edition
