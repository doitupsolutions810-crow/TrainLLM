#!/bin/bash
# voidOS Simple - One-Command Setup & Run
# Copy this entire file and paste into terminal, then hit Enter

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     voidOS Simple - Quick Setup    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}\n"

# Check Python
echo -e "${YELLOW}⏳ Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}\n"

# Check if voidos_simple.py exists
echo -e "${YELLOW}⏳ Checking for voidos_simple.py...${NC}"
if [ ! -f "voidos_simple.py" ]; then
    echo -e "${YELLOW}📥 Downloading voidos_simple.py...${NC}"
    # If GitHub is available, download from there
    # For now, use local file from Anti4 directory
    if [ -f "/Users/crownest/Desktop/anti2/Anti4/voidos_simple.py" ]; then
        cp /Users/crownest/Desktop/anti2/Anti4/voidos_simple.py .
        echo -e "${GREEN}✅ voidos_simple.py copied${NC}\n"
    else
        echo "❌ voidos_simple.py not found"
        exit 1
    fi
else
    echo -e "${GREEN}✅ voidos_simple.py found${NC}\n"
fi

# Check ports
echo -e "${YELLOW}⏳ Checking ports 5001-5002...${NC}"
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 5001 in use. Killing existing process...${NC}"
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 5002 in use. Killing existing process...${NC}"
    lsof -ti:5002 | xargs kill -9 2>/dev/null || true
    sleep 1
fi
echo -e "${GREEN}✅ Ports available${NC}\n"

# Create seed directory
echo -e "${YELLOW}⏳ Creating seed directory...${NC}"
mkdir -p /tmp/voidos
echo -e "${GREEN}✅ Seed directory ready${NC}\n"

# Start voidOS
echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Starting voidOS Simple...     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}\n"

python3 voidos_simple.py &
VOIDOS_PID=$!
echo -e "${GREEN}✅ voidOS started (PID: ${VOIDOS_PID})${NC}\n"

# Wait for servers to start
sleep 3

# Test endpoints
echo -e "${YELLOW}⏳ Testing endpoints...${NC}"
if curl -s http://localhost:5001/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Dashboard API responding${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard API not ready yet${NC}"
fi

if curl -s http://localhost:5002/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Terminal API responding${NC}"
else
    echo -e "${YELLOW}⚠️  Terminal API not ready yet${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✨ voidOS is Ready!              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}📍 Access Points:${NC}"
echo -e "   Dashboard: ${BLUE}http://localhost:5001${NC}"
echo -e "   Terminal:  ${BLUE}http://localhost:5002${NC}\n"

echo -e "${GREEN}🔌 Quick API Tests:${NC}"
echo -e "   curl http://localhost:5001/api/health"
echo -e "   curl http://localhost:5001/api/seed"
echo -e "   curl http://localhost:5001/api/apps\n"

echo -e "${GREEN}🛑 To Stop:${NC}"
echo -e "   Press Ctrl+C or run: kill ${VOIDOS_PID}\n"

# Keep running
wait $VOIDOS_PID
