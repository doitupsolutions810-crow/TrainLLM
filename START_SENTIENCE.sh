#!/bin/bash
# voidOS Sentience HUD - Quick Start Guide

# Start the system
python3 voidos_sentience.py &

# Wait for startup
sleep 2

# Open in browser (macOS)
open http://localhost:5001

# For Linux:
# xdg-open http://localhost:5001

# For Windows WSL:
# cmd.exe /C start http://localhost:5001

echo "🚀 Dashboard opening at http://localhost:5001"
echo ""
echo "Available endpoints:"
echo "  GET  /api/cycle-kernel        - Cognitive state"
echo "  POST /api/gemini-insight      - AI analysis"
echo "  POST /api/gemini-tts          - Audio narration"
echo "  GET  /api/apps                - App list"
echo "  GET  /api/seed                - Configuration"
echo ""
echo "Press Ctrl+C to stop server"
