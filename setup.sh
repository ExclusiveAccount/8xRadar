#!/bin/bash
# 8xRadar - Termux Setup Script

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     ██████╗ ██╗  ██╗██████╗  █████╗ ██████╗  █████╗ ██████╗  ║"
echo "║    ██╔═══██╗╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗ ║"
echo "║    ╚█████╔╝ ╚███╔╝ ██████╔╝███████║██║  ██║███████║██████╔╝ ║"
echo "║    ██╔══██╗ ██╔██╗ ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗ ║"
echo "║    ╚█████╔╝██╔╝ ██╗██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║ ║"
echo "║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║"
echo "║                                                               ║"
echo "║              Signal Intelligence Toolkit - Setup              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Update packages
echo "[1/5] Updating packages..."
pkg update -y
pkg upgrade -y

# Install required packages
echo ""
echo "[2/5] Installing core dependencies..."
pkg install -y python
pkg install -y termux-api
pkg install -y curl

echo ""
echo "[3/5] Installing network tools..."
pkg install -y nmap
pkg install -y net-tools
pkg install -y iproute2

# Install Python packages (optional)
echo ""
echo "[4/5] Installing Python packages..."
pip install requests 2>/dev/null

# Set permissions
echo ""
echo "[5/5] Setting permissions..."
chmod +x *.py

# Grant Termux permissions
echo ""
echo "📍 Requesting location permission..."
termux-location -p network 2>/dev/null &
sleep 2
kill $! 2>/dev/null

# Done
clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                         ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║                                                               ║"
echo "║  📱 IMPORTANT: Install 'Termux:API' app from F-Droid         ║"
echo "║     https://f-droid.org/packages/com.termux.api/             ║"
echo "║                                                               ║"
echo "║  🔐 Enable Location in phone Settings for GPS features       ║"
echo "║                                                               ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║                                                               ║"
echo "║  🚀 RUN OPTIONS:                                              ║"
echo "║                                                               ║"
echo "║     python 8xradar.py          # 🌟 MAIN (Beautiful UI)      ║"
echo "║     python panel.py            # 📋 Menu-based panel         ║"
echo "║     python ultimate_radar.py   # 📡 All-in-one scanner       ║"
echo "║     python cell_intelligence.py # 📶 Cell tower details      ║"
echo "║     python satellite_tracker.py # 🛰️ Satellite tracker       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Type: python 8xradar.py   to start!"
echo ""
