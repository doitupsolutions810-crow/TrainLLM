START HERE - voidOS Sentience HUD Quick Guide
===============================================

FASTEST START (2 commands):

1. python3 voidos_sentience.py
2. Open: http://localhost:5001


KEY FILES:

To Run:
  - voidos_sentience.py (main backend server)
  - test_sentience.py (run tests)
  - demo-sentience.sh (automated demo)

To Learn:
  - SENTIENCE_PACKAGE.md (complete reference - read this!)
  - SENTIENCE_README.md (quick overview)
  - SENTIENCE_GUIDE.md (integration details)

To Integrate:
  - SentienceHUD.jsx (React component)
  - PARTICLES_EXAMPLES.md (code examples)


WHAT YOU GET:

✓ 15,000 animated particles (Three.js nebula)
✓ Real-time CycleKernel polling
✓ Gemini AI insight generation
✓ TTS narration (voice)
✓ Emergency mode detection
✓ Cyberpunk UI
✓ Full test suite
✓ Production ready


API ENDPOINTS:

GET  /api/cycle-kernel       - Cognitive state
POST /api/gemini-insight     - AI analysis
POST /api/gemini-tts         - Text to speech
GET  /api/apps               - App list
GET  /api/seed               - Configuration


QUICK TASKS:

Start:  python3 voidos_sentience.py
Test:   python3 test_sentience.py
Demo:   bash demo-sentience.sh

Test endpoint:  curl http://localhost:5001/api/cycle-kernel


OPTIONAL SETUP (Gemini API):

1. Get key: https://aistudio.google.com/apikey
2. Set env: export GEMINI_API_KEY="your-key"
3. Restart server

Now get real AI insights and voice narration!


NEED HELP?

1. Read SENTIENCE_PACKAGE.md (everything is documented)
2. Check terminal output for errors
3. Run: python3 test_sentience.py (verify everything works)
4. See PARTICLES_EXAMPLES.md (code examples)


PERFORMANCE:

Particles:    15,000 (adjustable)
FPS:          60 (Three.js)
Memory:       ~50 MB
Polling:      1.2 seconds
Status:       Production ready


NEXT STEPS:

1. python3 voidos_sentience.py
2. http://localhost:5001
3. Read SENTIENCE_PACKAGE.md
4. Set GEMINI_API_KEY (optional)
5. Integrate with your app using SentienceHUD.jsx


STATUS: ✅ Ready to go!
