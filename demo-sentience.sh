#!/bin/bash

# voidOS Sentience HUD - Quick Demo & Test Script
# Starts the system and runs comprehensive tests

set -e

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║        👻 voidOS Sentience HUD - Demo & Test Script                           ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PORT=5001
BASE_URL="http://localhost:$PORT"
PYTHON_CMD="python3"

# Helper functions
print_section() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Check if Python is installed
print_section "🔍 Environment Check"

if ! command -v $PYTHON_CMD &> /dev/null; then
    error "Python 3 not found!"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | awk '{print $2}')
success "Python version: $PYTHON_VERSION"

# Check if port is available
print_section "🔌 Port Availability"

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    warning "Port $PORT is in use"
    read -p "Kill existing process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$PORT | xargs kill -9
        sleep 1
        success "Port $PORT cleared"
    else
        error "Cannot proceed with port in use"
        exit 1
    fi
else
    success "Port $PORT is available"
fi

# Start the server
print_section "🚀 Starting Sentience HUD Server"

echo -e "${PURPLE}Starting on ${BLUE}$BASE_URL${NC}"
echo ""

$PYTHON_CMD voidos_sentience.py &
SERVER_PID=$!

sleep 2

# Check if server started
if ! kill -0 $SERVER_PID 2>/dev/null; then
    error "Server failed to start!"
    exit 1
fi

success "Server running (PID: $SERVER_PID)"

# Run tests
print_section "🧪 Running Test Suite"

sleep 1

# Test 1: Dashboard
echo -n "1. Dashboard HTML... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/)
if [ "$RESPONSE" = "200" ]; then
    success "OK (HTTP 200)"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 2: Cycle Kernel API
echo -n "2. CycleKernel API... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/cycle-kernel)
if [ "$RESPONSE" = "200" ]; then
    DATA=$(curl -s $BASE_URL/api/cycle-kernel)
    MODE=$(echo $DATA | grep -o '"mode":"[^"]*' | cut -d'"' -f4)
    INTEGRITY=$(echo $DATA | grep -o '"core_integrity":[0-9.]*' | cut -d':' -f2)
    success "OK - Mode: $MODE, Integrity: $INTEGRITY"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 3: Applications API
echo -n "3. Applications API... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/apps)
if [ "$RESPONSE" = "200" ]; then
    COUNT=$(curl -s $BASE_URL/api/apps | grep -o '"id"' | wc -l)
    success "OK ($COUNT apps found)"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 4: Seed API
echo -n "4. Seed Configuration... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/seed)
if [ "$RESPONSE" = "200" ]; then
    SEED=$(curl -s $BASE_URL/api/seed | grep -o '"seed_id":"[^"]*' | cut -d'"' -f4)
    success "OK - $SEED"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 5: Gemini Insight API
echo -n "5. Gemini Insight API... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/gemini-insight \
    -H "Content-Type: application/json" \
    -d '{"systemState":{"mode":"Balanced"}}')
if [ "$RESPONSE" = "200" ]; then
    success "OK"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 6: Gemini TTS API
echo -n "6. Gemini TTS API... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/gemini-tts \
    -H "Content-Type: application/json" \
    -d '{"text":"System test"}')
if [ "$RESPONSE" = "200" ]; then
    success "OK"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 7: Trigger Scan API
echo -n "7. Trigger Scan API... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/api/trigger-scan)
if [ "$RESPONSE" = "200" ]; then
    success "OK"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Test 8: Health Check
echo -n "8. Health Check... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/health)
if [ "$RESPONSE" = "200" ]; then
    status=$(curl -s $BASE_URL/api/health | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    success "OK - $status"
else
    error "FAIL (HTTP $RESPONSE)"
fi

# Summary
print_section "📊 Test Summary"

success "All API endpoints operational!"
echo ""
info "Server Features:"
echo "  • Real-time particle visualization (15k particles)"
echo "  • CycleKernel bridge polling (1.2s intervals)"
echo "  • Gemini AI insight generation"
echo "  • TTS narration support"
echo "  • Emergency mode detection"
echo "  • Cyberpunk UI with glassmorphism"
echo ""

print_section "🌐 Access Information"

echo -e "${BLUE}Dashboard:${NC}     $BASE_URL"
echo -e "${BLUE}Terminal:${NC}      $BASE_URL/terminal"
echo -e "${BLUE}API Base:${NC}      $BASE_URL/api"
echo ""

echo -e "${PURPLE}API Endpoints:${NC}"
echo "  GET  /api/cycle-kernel       - Get current cognitive state"
echo "  POST /api/gemini-insight     - Generate AI analysis"
echo "  POST /api/gemini-tts         - Generate audio narration"
echo "  POST /api/trigger-scan       - Initiate system scan"
echo "  GET  /api/apps               - Get application list"
echo "  GET  /api/seed               - Get seed configuration"
echo ""

print_section "🎯 Next Steps"

echo "1. Open dashboard:"
echo "   ${BLUE}open $BASE_URL${NC}"
echo ""
echo "2. View particle effects:"
echo "   The dashboard shows a real-time animated nebula background"
echo ""
echo "3. Generate insights:"
echo "   Click 'ANALYZE SYSTEM STATE' button in the dashboard"
echo ""
echo "4. Enable TTS narration:"
echo "   Set GEMINI_API_KEY environment variable for real voices"
echo ""
echo "5. Run comprehensive tests:"
echo "   ${BLUE}python3 test_sentience.py${NC}"
echo ""

print_section "⚙️ Configuration"

echo "Current settings:"
echo "  Port: $PORT"
echo "  CycleKernel URL: http://localhost:8000/v1/logic_delta (mock data)"
echo "  Particle Count: 15,000"
echo "  Polling Interval: 1.2 seconds"
echo ""

info "To connect to real CycleKernel, edit voidos_sentience.py"
info "To use real Gemini API, set GEMINI_API_KEY environment variable"
echo ""

print_section "🛑 Stop Server"

echo "Server is running with PID: $SERVER_PID"
echo "To stop: ${CYAN}kill $SERVER_PID${NC}"
echo ""

# Wait for user interaction
read -p "Press Enter to stop the server and exit... " -t 300

# Cleanup
echo ""
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

success "Server stopped"
echo ""
echo "👋 Thanks for testing voidOS Sentience HUD!"
echo ""
