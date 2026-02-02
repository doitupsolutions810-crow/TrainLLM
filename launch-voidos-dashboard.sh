#!/bin/bash
#
# voidOS Dashboard Quick Start Script
# Automatically configures and launches integrated dashboard
#

set -e

echo "=========================================="
echo "voidOS Integrated Dashboard Launcher"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[INFO] Detected macOS"
    BROWSER="open"
    QEMU_CMD="qemu-system-aarch64"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[INFO] Detected Linux"
    BROWSER="xdg-open"
    QEMU_CMD="qemu-system-x86_64"
else
    echo "[ERROR] Unsupported OS: $OSTYPE"
    exit 1
fi

# Configuration
VOIDOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISO_PATH="$VOIDOS_DIR/voidos_output/voidos-1.0.0.iso"
DASHBOARD_PORT=5001
DASHBOARD_URL="http://localhost:$DASHBOARD_PORT"

# Check ISO exists
if [ ! -f "$ISO_PATH" ]; then
    echo "[ERROR] ISO not found: $ISO_PATH"
    echo "[INFO] Run 'python3 TrainLLM/voidos_installer.py' to build ISO"
    exit 1
fi

echo "[INFO] ISO Location: $ISO_PATH"
echo "[INFO] Dashboard URL: $DASHBOARD_URL"
echo ""

# Check if QEMU is available
if ! command -v $QEMU_CMD &> /dev/null; then
    echo "[ERROR] $QEMU_CMD not found"
    echo "[INFO] Install QEMU: brew install qemu (macOS) or apt install qemu (Linux)"
    exit 1
fi

echo "[INFO] Launching voidOS in QEMU..."
echo "[INFO] Dashboard will be available at $DASHBOARD_URL"
echo "[INFO] Open your browser when QEMU window appears"
echo ""

# Kill any existing QEMU processes
killall $QEMU_CMD 2>/dev/null || true
sleep 1

# Launch QEMU with appropriate settings
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with HVF acceleration
    echo "[INFO] Starting with HVF acceleration..."
    $QEMU_CMD \
        -machine virt \
        -cpu host \
        -accel hvf \
        -m 2048 \
        -smp 2 \
        -cdrom "$ISO_PATH" \
        -boot d \
        -display cocoa \
        -name "voidOS" &
else
    # Linux with KVM or software emulation
    if grep -q kvm /proc/cpuinfo 2>/dev/null; then
        echo "[INFO] Starting with KVM acceleration..."
        ACCEL="-enable-kvm"
    else
        echo "[INFO] Starting with software emulation (slower)..."
        ACCEL=""
    fi
    
    $QEMU_CMD \
        $ACCEL \
        -m 2048 \
        -smp 2 \
        -cdrom "$ISO_PATH" \
        -boot d \
        -name "voidOS" &
fi

QEMU_PID=$!
echo "[INFO] QEMU started (PID: $QEMU_PID)"
echo ""

# Wait for dashboard to be ready
echo "[INFO] Waiting for voidOS to boot..."
sleep 3

# Try to open dashboard in browser
echo "[INFO] Opening dashboard..."
$BROWSER "$DASHBOARD_URL" 2>/dev/null || echo "[INFO] Open $DASHBOARD_URL in your browser"

echo ""
echo "=========================================="
echo "voidOS is running!"
echo "Dashboard: $DASHBOARD_URL"
echo "=========================================="
echo ""
echo "Available features:"
echo "  - 🏠 Home: System status & quick start"
echo "  - 📦 Apps: Launch integrated tools"
echo "  - ⌨️  Terminal: Web-based command shell"
echo "  - 📊 Monitor: System resource monitoring"
echo "  - ⚙️  Settings: System configuration"
echo ""
echo "To stop: Close the QEMU window or press Ctrl+C"
echo ""

# Keep script running
wait $QEMU_PID 2>/dev/null || true
echo "[INFO] voidOS session ended"
