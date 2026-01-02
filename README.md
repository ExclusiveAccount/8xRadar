# 📡 8xRadar - Signal Intelligence Toolkit

```
    ╔═══════════════════════════════════════════════════════════════╗
    ║     ██████╗ ██╗  ██╗██████╗  █████╗ ██████╗  █████╗ ██████╗  ║
    ║    ██╔═══██╗╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗ ║
    ║    ╚█████╔╝ ╚███╔╝ ██████╔╝███████║██║  ██║███████║██████╔╝ ║
    ║    ██╔══██╗ ██╔██╗ ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗ ║
    ║    ╚█████╔╝██╔╝ ██╗██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║ ║
    ║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║
    ╚═══════════════════════════════════════════════════════════════╝
```

Real-Time Signal Intelligence & Monitoring for Android (Termux)

## 🎯 8 Types of Signal Detection

| # | Type | Description |
|---|------|-------------|
| 1 | 📶 Cell Towers | 4G LTE / 5G NR with TA distance |
| 2 | 📡 WiFi | Networks, security, channels |
| 3 | 🔵 Bluetooth | Devices, types, signal |
| 4 | 🛰️ Satellites | GPS, NavIC, ISS tracking |
| 5 | 📷 Cameras | Hidden camera detection |
| 6 | 🏠 IoT | Smart home devices |
| 7 | 🌐 Network | Connected devices scan |
| 8 | 📍 Location | GPS coordinates |

## 📱 Installation (Termux)

### Step 1: Install Apps
```
1. Termux (F-Droid): https://f-droid.org/packages/com.termux/
2. Termux:API (F-Droid): https://f-droid.org/packages/com.termux.api/
```

### Step 2: Setup
```bash
# Extract and enter directory
unzip signal-radar.zip
cd signal-radar

# Run setup
bash setup.sh
```

### Step 3: Run
```bash
python 8xradar.py
```

## 🚀 Available Tools

| Tool | Command | Description |
|------|---------|-------------|
| **8xRadar** | `python 8xradar.py` | 🌟 Main beautiful dashboard |
| **Panel** | `python panel.py` | Menu-based control panel |
| **Ultimate** | `python ultimate_radar.py` | All-in-one scanner |
| **Cell Intel** | `python cell_intelligence.py` | NetMonster style details |
| **Satellite** | `python satellite_tracker.py` | GPS/NavIC/ISS tracker |

## 📶 Cell Tower Features

- **MCC/MNC** - Country & Network codes
- **TAC/LAC** - Tracking/Location Area
- **CI/CID** - Cell Identity
- **eNodeB/gNodeB** - Base station ID
- **PCI** - Physical Cell ID
- **EARFCN/NRARFCN** - Frequency channel
- **Band** - B1, B3, B40, B41, n78, etc.
- **RSRP** - Signal power (dBm)
- **RSRQ** - Signal quality (dB)
- **SINR/SNR** - Signal-to-noise ratio
- **TA** - Timing Advance → Distance calculation
- **Bandwidth** - 10/20/100 MHz
- **Tower Height** - Estimated height

## 📊 Signal Graphs

- Real-time signal strength bars
- Historical sparkline graphs
- Distance visualization
- Quality indicators

## 🇮🇳 India Operators

| MCC | MNC | Operator |
|-----|-----|----------|
| 404 | 10,40,45,90-98 | Airtel |
| 404 | 11,12,20,86,88 | Vi |
| 405 | 840,854-874 | Jio |
| 404 | 34,38,51,72 | BSNL |

## ⚠️ Requirements

- Android phone with Termux
- Termux:API app (F-Droid)
- Location permission enabled
- No root required (basic features)

## 📄 License

For educational and personal use only.

## 👨‍💻 Author

8xRadar - Signal Intelligence Toolkit
