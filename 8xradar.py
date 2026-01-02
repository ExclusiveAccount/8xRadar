#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     ██████╗ ██╗  ██╗██████╗  █████╗ ██████╗  █████╗ ██████╗              ║
║    ██╔═══██╗╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗             ║
║    ╚█████╔╝ ╚███╔╝ ██████╔╝███████║██║  ██║███████║██████╔╝             ║
║    ██╔══██╗ ██╔██╗ ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗             ║
║    ╚█████╔╝██╔╝ ██╗██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║             ║
║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝             ║
║                                                                           ║
║              Real-Time Signal Intelligence & Monitoring                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

8xRadar - 8 Types of Signal Detection:
1. 📶 Cell Towers (4G/5G)
2. 📡 WiFi Networks
3. 🔵 Bluetooth Devices
4. 🛰️ Satellites (GPS/NavIC)
5. 📷 Hidden Cameras
6. 🏠 IoT Devices
7. 🌐 Network Devices
8. 📍 Location Tracking
"""

import subprocess
import json
import os
import sys
import time
import math
import threading
from datetime import datetime
from collections import deque

# ============== COLORS ==============
class C:
    # Basic
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
    # Styles
    BOLD = '\033[1m'; DIM = '\033[2m'; BLINK = '\033[5m'
    UNDERLINE = '\033[4m'; E = '\033[0m'
    # Backgrounds
    BG_R = '\033[41m'; BG_G = '\033[42m'; BG_Y = '\033[43m'
    BG_B = '\033[44m'; BG_M = '\033[45m'; BG_C = '\033[46m'

# ============== GLOBAL DATA ==============
DATA = {
    'cell': [], 'wifi': [], 'bluetooth': [], 'network': [],
    'gps': None, 'history': {'rsrp': deque(maxlen=30), 'wifi_count': deque(maxlen=30)},
    'stats': {'wifi': 0, 'bt': 0, 'cell': 0, 'net': 0},
    'alerts': [], 'start_time': datetime.now()
}

# ============== OPERATORS ==============
OPERATORS = {
    (404,10):"Airtel",(404,40):"Airtel",(404,45):"Airtel",(404,49):"Airtel",
    (404,90):"Airtel",(404,92):"Airtel",(404,93):"Airtel",(404,94):"Airtel",
    (404,95):"Airtel",(404,96):"Airtel",(404,97):"Airtel",(404,98):"Airtel",
    (404,11):"Vi",(404,12):"Vi",(404,13):"Vi",(404,20):"Vi",(404,27):"Vi",
    (404,84):"Vi",(404,86):"Vi",(404,88):"Vi",
    (405,840):"Jio",(405,854):"Jio",(405,855):"Jio",(405,857):"Jio",
    (405,858):"Jio",(405,859):"Jio",(405,860):"Jio",(405,861):"Jio",
    (405,862):"Jio",(405,863):"Jio",(405,864):"Jio",(405,865):"Jio",
    (405,866):"Jio",(405,867):"Jio",(405,868):"Jio",(405,869):"Jio",
    (405,870):"Jio",(405,871):"Jio",(405,872):"Jio",
    (404,34):"BSNL",(404,38):"BSNL",(404,51):"BSNL",(404,72):"BSNL",
}

LTE_BANDS = {
    1: {"name": "B1", "freq": 2100, "bw": 10},
    3: {"name": "B3", "freq": 1800, "bw": 20},
    5: {"name": "B5", "freq": 850, "bw": 10},
    8: {"name": "B8", "freq": 900, "bw": 10},
    40: {"name": "B40", "freq": 2300, "bw": 20, "type": "TDD"},
    41: {"name": "B41", "freq": 2500, "bw": 20, "type": "TDD"},
}

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=20)
        return r.stdout + r.stderr
    except:
        return ""

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def earfcn_to_band(e):
    if 0<=e<=599: return 1
    if 1200<=e<=1949: return 3
    if 2400<=e<=2649: return 5
    if 3450<=e<=3799: return 8
    if 38650<=e<=39649: return 40
    if 39650<=e<=41589: return 41
    return None


# ============== BEAUTIFUL GRAPHS ==============
def signal_bar_fancy(rssi, width=20, label=""):
    """Beautiful signal strength bar with gradient"""
    if rssi is None:
        return f"{C.DIM}{'░'*width}{C.E} N/A"
    
    # Normalize to 0-100%
    percent = max(0, min(100, (rssi + 120) * 100 / 70))
    filled = int(width * percent / 100)
    
    # Gradient colors based on strength
    if percent > 70:
        bar = f"{C.G}{'█'*filled}{C.DIM}{'░'*(width-filled)}{C.E}"
        quality = "Excellent"
    elif percent > 50:
        bar = f"{C.G}{'█'*int(filled*0.7)}{C.Y}{'▓'*int(filled*0.3)}{C.DIM}{'░'*(width-filled)}{C.E}"
        quality = "Good"
    elif percent > 30:
        bar = f"{C.Y}{'█'*int(filled*0.5)}{C.Y}{'▓'*int(filled*0.5)}{C.DIM}{'░'*(width-filled)}{C.E}"
        quality = "Fair"
    else:
        bar = f"{C.R}{'█'*filled}{C.DIM}{'░'*(width-filled)}{C.E}"
        quality = "Poor"
    
    return f"{bar} {rssi:>4}dBm {C.DIM}({quality}){C.E}"

def distance_bar(distance_m, max_dist=5000):
    """Visual distance indicator"""
    if distance_m is None:
        return f"{C.DIM}? m{C.E}"
    
    # Create distance visualization
    width = 15
    filled = min(width, int(width * distance_m / max_dist))
    
    if distance_m < 500:
        color = C.G
        icon = "📍"
    elif distance_m < 1500:
        color = C.Y
        icon = "📡"
    else:
        color = C.R
        icon = "🗼"
    
    bar = f"{color}{'▰'*filled}{'▱'*(width-filled)}{C.E}"
    
    if distance_m < 1000:
        dist_str = f"{distance_m:.0f}m"
    else:
        dist_str = f"{distance_m/1000:.2f}km"
    
    return f"{icon} {bar} {color}{dist_str}{C.E}"

def sparkline(data, width=30, height=5):
    """ASCII sparkline graph"""
    if not data or len(data) < 2:
        return [f"{C.DIM}{'─'*width}{C.E}"] * height
    
    data = list(data)
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val or 1
    
    # Normalize data
    normalized = [(v - min_val) / range_val for v in data]
    
    # Create graph
    chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    lines = []
    
    # Single line sparkline
    line = ""
    for val in normalized[-width:]:
        idx = min(len(chars)-1, int(val * (len(chars)-1)))
        if val > 0.7:
            line += f"{C.G}{chars[idx]}{C.E}"
        elif val > 0.4:
            line += f"{C.Y}{chars[idx]}{C.E}"
        else:
            line += f"{C.R}{chars[idx]}{C.E}"
    
    # Pad if needed
    line = line + f"{C.DIM}{'▁'*(width-len(data))}{C.E}"
    
    return line

def tower_ascii(height_m):
    """ASCII art tower based on height"""
    if height_m is None:
        height_m = 30  # Default
    
    # Scale: 10m = 1 line
    lines = min(5, max(1, int(height_m / 10)))
    
    tower = []
    tower.append(f"    {C.R}▲{C.E}")
    tower.append(f"   {C.Y}╱│╲{C.E}")
    for i in range(lines):
        if i == 0:
            tower.append(f"  {C.W}╱ │ ╲{C.E}")
        else:
            tower.append(f"  {C.W}│ │ │{C.E}")
    tower.append(f"  {C.DIM}═════{C.E}")
    
    return tower

def radar_animation(frame):
    """Animated radar sweep"""
    chars = ['◜', '◝', '◞', '◟']
    return f"{C.G}{chars[frame % 4]}{C.E}"

# ============== DISTANCE CALCULATIONS ==============
def calc_distance_ta(ta, network='LTE'):
    """Calculate distance from Timing Advance"""
    if ta is None or ta < 0:
        return None
    if network == 'LTE':
        return ta * 78.12  # meters (each TA = ~78m)
    if network == 'GSM':
        return ta * 550  # meters
    return None

def calc_distance_rsrp(rsrp, freq_mhz=1800):
    """Estimate distance from RSRP using path loss"""
    if rsrp is None or rsrp > -40:
        return None
    
    # Free space path loss model
    tx_power = 43  # dBm (typical macro cell)
    path_loss = tx_power - rsrp
    
    try:
        d_km = 10 ** ((path_loss - 20 * math.log10(freq_mhz) - 32.44) / 20)
        return d_km * 1000  # meters
    except:
        return None

def estimate_tower_height(distance_m, rsrp):
    """Estimate tower height based on signal propagation"""
    if distance_m is None:
        return None
    
    # Typical tower heights in India
    # Urban: 20-40m, Suburban: 30-50m, Rural: 40-80m
    
    if distance_m < 500:
        return 25  # Small cell / Urban
    elif distance_m < 1500:
        return 35  # Macro cell / Suburban
    elif distance_m < 3000:
        return 50  # Tall tower
    else:
        return 70  # Very tall / Rural


# ============== SCANNERS ==============
def scan_cell():
    """Scan cell towers with detailed info"""
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    cells = []
    
    if out:
        try:
            for c in json.loads(out):
                t = c.get('type', '').lower()
                
                if 'lte' in t:
                    mcc, mnc = c.get('mcc', 0), c.get('mnc', 0)
                    earfcn = c.get('earfcn', 0)
                    band = earfcn_to_band(earfcn)
                    band_info = LTE_BANDS.get(band, {})
                    ci = c.get('ci')
                    ta = c.get('timingAdvance')
                    rsrp = c.get('rsrp')
                    
                    # Calculate distance
                    distance = calc_distance_ta(ta, 'LTE')
                    if distance is None and rsrp:
                        distance = calc_distance_rsrp(rsrp, band_info.get('freq', 1800))
                    
                    # Estimate tower height
                    tower_height = estimate_tower_height(distance, rsrp)
                    
                    cells.append({
                        'type': '4G LTE',
                        'registered': c.get('registered'),
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'tac': c.get('tac'),
                        'ci': ci,
                        'enb_id': ci // 256 if ci else None,
                        'sector': ci % 256 if ci else None,
                        'pci': c.get('pci'),
                        'earfcn': earfcn,
                        'band': band,
                        'band_name': band_info.get('name', f'B{band}'),
                        'frequency': band_info.get('freq'),
                        'bandwidth': band_info.get('bw', 10),
                        'rsrp': rsrp,
                        'rsrq': c.get('rsrq'),
                        'rssi': c.get('rssi'),
                        'sinr': c.get('rssnr'),
                        'cqi': c.get('cqi'),
                        'ta': ta,
                        'distance_m': distance,
                        'tower_height': tower_height,
                    })
                    
                    # Add to history
                    if rsrp:
                        DATA['history']['rsrp'].append(abs(rsrp))
                
                elif 'nr' in t or '5g' in t:
                    mcc, mnc = c.get('mcc', 0), c.get('mnc', 0)
                    cells.append({
                        'type': '5G NR',
                        'registered': c.get('registered'),
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'nci': c.get('nci'),
                        'gnb_id': c.get('nci') // 4096 if c.get('nci') else None,
                        'pci': c.get('pci'),
                        'nrarfcn': c.get('nrarfcn'),
                        'ss_rsrp': c.get('ssRsrp') or c.get('csiRsrp'),
                        'ss_rsrq': c.get('ssRsrq') or c.get('csiRsrq'),
                        'ss_sinr': c.get('ssSinr'),
                        'bandwidth': 100,
                    })
                    
        except:
            pass
    
    DATA['cell'] = cells
    DATA['stats']['cell'] = len(cells)

def scan_wifi():
    """Scan WiFi networks"""
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    if out:
        try:
            DATA['wifi'] = sorted(json.loads(out), key=lambda x: x.get('rssi', -100), reverse=True)
            DATA['stats']['wifi'] = len(DATA['wifi'])
            DATA['history']['wifi_count'].append(len(DATA['wifi']))
        except:
            pass

def scan_bluetooth():
    """Scan Bluetooth devices"""
    out = cmd("termux-bluetooth-scaninfo 2>/dev/null")
    if out:
        try:
            DATA['bluetooth'] = json.loads(out)
            DATA['stats']['bt'] = len(DATA['bluetooth'])
        except:
            pass

def scan_gps():
    """Get GPS location"""
    out = cmd("termux-location -p gps 2>/dev/null")
    if out:
        try:
            DATA['gps'] = json.loads(out)
        except:
            pass


# ============== BEAUTIFUL DASHBOARD ==============
def render_header(frame):
    """Render animated header"""
    now = datetime.now()
    uptime = now - DATA['start_time']
    uptime_str = f"{int(uptime.total_seconds()//3600):02d}:{int((uptime.total_seconds()%3600)//60):02d}:{int(uptime.total_seconds()%60):02d}"
    
    radar = radar_animation(frame)
    
    print(f"""
{C.C}{C.BOLD}╔═══════════════════════════════════════════════════════════════════════════════════╗
║  {radar} {C.W}8xRADAR{C.C} - Real-Time Signal Intelligence                    {now.strftime('%H:%M:%S')}  ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  📶 Cell: {DATA['stats']['cell']:>2}  │  📡 WiFi: {DATA['stats']['wifi']:>2}  │  🔵 BT: {DATA['stats']['bt']:>2}  │  ⏱️ Uptime: {uptime_str}  │  {radar}  ║
╚═══════════════════════════════════════════════════════════════════════════════════╝{C.E}
""")

def render_cell_panel():
    """Render cell tower panel with tower visualization"""
    cells = DATA.get('cell', [])
    
    print(f"{C.M}{C.BOLD}┌────────────────────────────── 📶 CELL TOWERS ──────────────────────────────┐{C.E}")
    
    if not cells:
        print(f"│  {C.DIM}No cell data - Install Termux:API{C.E}")
        print(f"{C.M}└─────────────────────────────────────────────────────────────────────────────┘{C.E}")
        return
    
    # Find connected cell
    connected = next((c for c in cells if c.get('registered')), None)
    
    if connected:
        op = connected.get('operator', '?')
        ctype = connected.get('type', '?')
        
        # Operator color
        if 'Jio' in op: op_color = C.B
        elif 'Airtel' in op: op_color = C.R
        elif 'Vi' in op: op_color = C.M
        else: op_color = C.Y
        
        print(f"│  {C.G}● CONNECTED{C.E} to {op_color}{C.BOLD}{op}{C.E} ({ctype})")
        print(f"│")
        
        # Signal visualization
        rsrp = connected.get('rsrp') or connected.get('ss_rsrp')
        print(f"│  {C.BOLD}Signal:{C.E}")
        print(f"│    {signal_bar_fancy(rsrp, 25)}")
        
        # Distance and Tower
        distance = connected.get('distance_m')
        tower_h = connected.get('tower_height')
        
        print(f"│")
        print(f"│  {C.BOLD}Distance to Tower:{C.E}")
        print(f"│    {distance_bar(distance)}")
        
        if tower_h:
            print(f"│    Est. Tower Height: ~{tower_h}m")
        
        # Detailed info
        print(f"│")
        print(f"│  {C.BOLD}Details:{C.E}")
        
        if 'LTE' in ctype:
            print(f"│    MCC: {connected.get('mcc')}  MNC: {connected.get('mnc')}")
            print(f"│    TAC: {connected.get('tac')}  CI: {connected.get('ci')}")
            print(f"│    eNodeB: {connected.get('enb_id')}  Sector: {connected.get('sector')}")
            print(f"│    PCI: {connected.get('pci')}  EARFCN: {connected.get('earfcn')}")
            print(f"│    Band: {C.C}{connected.get('band_name')} ({connected.get('frequency')}MHz){C.E}  BW: {connected.get('bandwidth')}MHz")
            print(f"│    RSRP: {connected.get('rsrp')}dBm  RSRQ: {connected.get('rsrq')}dB  SINR: {connected.get('sinr')}dB")
            if connected.get('ta') is not None:
                print(f"│    TA: {connected.get('ta')}  → Distance: {C.Y}{distance:.0f}m{C.E}" if distance else f"│    TA: {connected.get('ta')}")
        
        elif '5G' in ctype:
            print(f"│    MCC: {connected.get('mcc')}  MNC: {connected.get('mnc')}")
            print(f"│    NCI: {connected.get('nci')}  gNodeB: {connected.get('gnb_id')}")
            print(f"│    PCI: {connected.get('pci')}  NRARFCN: {connected.get('nrarfcn')}")
            print(f"│    SS-RSRP: {connected.get('ss_rsrp')}dBm  SS-RSRQ: {connected.get('ss_rsrq')}dB")
            print(f"│    SS-SINR: {connected.get('ss_sinr')}dB  BW: {connected.get('bandwidth')}MHz")
    
    # Neighbors
    neighbors = [c for c in cells if not c.get('registered')]
    if neighbors:
        print(f"│")
        print(f"│  {C.DIM}○ Neighbors: {len(neighbors)}{C.E}")
        for n in neighbors[:3]:
            rsrp = n.get('rsrp') or n.get('ss_rsrp', -100)
            dist = n.get('distance_m')
            dist_str = f"{dist:.0f}m" if dist and dist < 1000 else f"{dist/1000:.1f}km" if dist else "?"
            print(f"│    {n.get('type')[:6]} PCI:{n.get('pci')} {signal_bar_fancy(rsrp, 10)} ~{dist_str}")
    
    # Signal history graph
    if DATA['history']['rsrp']:
        print(f"│")
        print(f"│  {C.BOLD}Signal History:{C.E}")
        graph = sparkline(DATA['history']['rsrp'], 40)
        print(f"│    {graph}")
    
    print(f"{C.M}└─────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_wifi_panel():
    """Render WiFi panel"""
    networks = DATA.get('wifi', [])[:6]
    
    print(f"{C.G}{C.BOLD}┌────────────────────────────── 📡 WiFi NETWORKS ──────────────────────────────┐{C.E}")
    
    if networks:
        print(f"│  {'SSID':<22} {'Signal':<28} {'Ch':>3} {'Sec':<8}")
        print(f"│  {'-'*22} {'-'*28} {'-'*3} {'-'*8}")
        
        for net in networks:
            ssid = net.get('ssid', '[Hidden]')[:21] or '[Hidden]'
            rssi = net.get('rssi', -100)
            freq = net.get('frequency', 0)
            ch = (freq-2412)//5+1 if 2412<=freq<=2484 else (freq-5170)//5+34 if freq>5000 else 0
            sec = net.get('capabilities', '')[:7]
            
            bar = signal_bar_fancy(rssi, 15, "")
            sec_c = C.G if 'WPA' in sec else C.R
            
            print(f"│  {ssid:<22} {bar} {ch:>3} {sec_c}{sec:<8}{C.E}")
    else:
        print(f"│  {C.DIM}No WiFi data{C.E}")
    
    # WiFi count history
    if DATA['history']['wifi_count']:
        print(f"│")
        print(f"│  Networks over time: {sparkline(DATA['history']['wifi_count'], 30)}")
    
    print(f"{C.G}└─────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_bluetooth_panel():
    """Render Bluetooth panel"""
    devices = DATA.get('bluetooth', [])[:5]
    
    print(f"{C.B}{C.BOLD}┌────────────────────────────── 🔵 BLUETOOTH ──────────────────────────────┐{C.E}")
    
    if devices:
        for dev in devices:
            name = dev.get('name', 'Unknown')[:25]
            rssi = dev.get('rssi', -100)
            
            # Device icon
            n = name.lower()
            if any(x in n for x in ['airpod', 'buds', 'earphone']): icon = "🎧"
            elif any(x in n for x in ['band', 'watch', 'fit']): icon = "⌚"
            elif any(x in n for x in ['phone', 'iphone', 'samsung']): icon = "📱"
            elif any(x in n for x in ['speaker', 'echo']): icon = "🔊"
            else: icon = "📟"
            
            bar = signal_bar_fancy(rssi, 12)
            print(f"│  {icon} {name:<25} {bar}")
    else:
        print(f"│  {C.DIM}No Bluetooth devices{C.E}")
    
    print(f"{C.B}└─────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_location_panel():
    """Render GPS location panel"""
    gps = DATA.get('gps')
    
    print(f"{C.Y}{C.BOLD}┌────────────────────────────── 📍 LOCATION ──────────────────────────────┐{C.E}")
    
    if gps:
        lat = gps.get('latitude', 0)
        lon = gps.get('longitude', 0)
        alt = gps.get('altitude', 0)
        acc = gps.get('accuracy', 0)
        
        print(f"│  Lat: {lat:.6f}°  Lon: {lon:.6f}°")
        print(f"│  Alt: {alt:.1f}m  Accuracy: ±{acc:.1f}m")
        print(f"│  {C.DIM}maps.google.com/?q={lat:.6f},{lon:.6f}{C.E}")
    else:
        print(f"│  {C.DIM}Getting GPS fix...{C.E}")
    
    print(f"{C.Y}└─────────────────────────────────────────────────────────────────────────────┘{C.E}")


# ============== MAIN LOOP ==============
def background_scanner():
    """Background scanning thread"""
    while True:
        try:
            threads = [
                threading.Thread(target=scan_cell),
                threading.Thread(target=scan_wifi),
                threading.Thread(target=scan_bluetooth),
            ]
            for t in threads:
                t.daemon = True
                t.start()
            for t in threads:
                t.join(timeout=15)
            
            # GPS less frequently
            if int(time.time()) % 5 == 0:
                scan_gps()
            
            time.sleep(3)
        except:
            time.sleep(3)

def render_dashboard(frame):
    """Render full dashboard"""
    clear()
    render_header(frame)
    render_cell_panel()
    print()
    render_wifi_panel()
    print()
    render_bluetooth_panel()
    print()
    render_location_panel()
    print(f"\n{C.DIM}  Auto-refreshing... Press Ctrl+C to exit{C.E}")

def main():
    """Main entry point"""
    clear()
    
    # Startup animation
    print(f"""
{C.C}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     ██████╗ ██╗  ██╗██████╗  █████╗ ██████╗  █████╗ ██████╗      ║
    ║    ██╔═══██╗╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗     ║
    ║    ╚█████╔╝ ╚███╔╝ ██████╔╝███████║██║  ██║███████║██████╔╝     ║
    ║    ██╔══██╗ ██╔██╗ ██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗     ║
    ║    ╚█████╔╝██╔╝ ██╗██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║     ║
    ║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝     ║
    ║                                                                   ║
    ║              Real-Time Signal Intelligence Monitor                ║
    ║                                                                   ║
    ║     📶 Cell Towers    📡 WiFi Networks    🔵 Bluetooth           ║
    ║     🛰️ Satellites     📷 Cameras          🏠 IoT Devices         ║
    ║     🌐 Network        📍 GPS Location                            ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
{C.E}""")
    
    print(f"  {C.Y}Initializing scanners...{C.E}")
    
    # Initial scans
    print(f"  {C.DIM}[1/4] Cell Towers...{C.E}")
    scan_cell()
    print(f"  {C.DIM}[2/4] WiFi Networks...{C.E}")
    scan_wifi()
    print(f"  {C.DIM}[3/4] Bluetooth...{C.E}")
    scan_bluetooth()
    print(f"  {C.DIM}[4/4] GPS Location...{C.E}")
    scan_gps()
    
    print(f"\n  {C.G}✓ Ready! Starting real-time monitoring...{C.E}")
    time.sleep(1)
    
    # Start background scanner
    scanner = threading.Thread(target=background_scanner)
    scanner.daemon = True
    scanner.start()
    
    # Main display loop
    frame = 0
    try:
        while True:
            render_dashboard(frame)
            frame += 1
            time.sleep(2)
    except KeyboardInterrupt:
        clear()
        print(f"""
{C.G}
  ╔═══════════════════════════════════════════════════════════════╗
  ║                    8xRadar Stopped                            ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║  Session Summary:                                             ║
  ║    📶 Cell Towers scanned:    {DATA['stats']['cell']:>3}                            ║
  ║    📡 WiFi Networks found:    {DATA['stats']['wifi']:>3}                            ║
  ║    🔵 Bluetooth devices:      {DATA['stats']['bt']:>3}                            ║
  ╚═══════════════════════════════════════════════════════════════╝
{C.E}""")
        
        # Export option
        export = input(f"  {C.Y}Export data to JSON? (y/n): {C.E}").strip().lower()
        if export == 'y':
            filename = f"8xradar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'cell': DATA['cell'],
                'wifi': DATA['wifi'],
                'bluetooth': DATA['bluetooth'],
                'gps': DATA['gps'],
                'stats': DATA['stats'],
            }
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"  {C.G}✓ Saved to {filename}{C.E}")
        
        print(f"\n  {C.G}👋 Goodbye!{C.E}\n")

if __name__ == "__main__":
    main()
