# voidOS Installation Report
Generated: 2026-02-01T16:36:19.942583

## Installation Status
Status: SUCCESS
Version: 1.0.0

## Seed Information
- Seed ID: 315610fa9a414c8a8d18eb94941fffa2
- Genesis Epoch: 13265
- Merkle Root: 8229f07d4a4c9b10093227e214407546aa669189c5e1a09d4ba8c5cb7d6fb9ac
- Telemetry Entries: 10

## Output Files
- voidOS ISO: /Users/crownest/Desktop/anti2/Anti4/voidos_output/voidos-1.0.0.iso
- USB Image: /Users/crownest/Desktop/anti2/Anti4/voidos_output/voidos-1.0.0.img

## Usage Instructions

### ISO Boot
1. Burn ISO to USB using tools like balenaEtcher or dd
2. Boot from USB (configure BIOS/UEFI for USB boot)
3. voidOS will automatically initialize and launch dashboard

### Direct USB Image
1. Write img file to USB: `dd if=voidos-1.0.0.img of=/dev/sdX`
2. Boot from USB
3. Dashboard available at http://localhost:5001

### Dashboard Access
- Web Interface: http://localhost:5001
- API Endpoints: /api/*
- WebSocket: ws://localhost:5001/socket.io/

## Seed Migration
To update seed:
1. Mount USB filesystem
2. Replace /etc/voidos/seed.json with new seed
3. Reboot voidOS system

## Technical Details
- Supports BIOS and UEFI boot
- Minimal footprint (~500MB)
- Offline-capable with network fallback
- Auto-restart on failure via systemd
