#!/usr/bin/env python3
"""
8xRadar - Signal Intelligence Toolkit
Real-time Cell Tower, WiFi, Bluetooth, GPS monitoring
"""

import subprocess
import json
import os
import time
import threading
from datetime import datetime
from collections import deque

# ============== SIMPLE COLORS (Termux Compatible) ==============
class C:
    R = '\033[91m'   # Red
    G = '\033[92m'   # Green
    Y = '\033[93m'   # Yellow
    B = '\033[94m'   # Blue
    M = '\033[95m'   # Magenta
    C = '\033[96m'   # Cyan
    W = '\033[97m'   # White
    BOLD = '\033[1m'
    DIM = '\033[2m'
    E = '\033[0m'    # End/Reset

# ============== GLOBAL DATA ==============
DATA = {
    'cell': [], 'wifi': [], 'bluetooth': [],
    'gps': None, 'sim1': None, 'sim2': None,
    'history': deque(maxlen=20),
    'start_time': datetime.now()
}

# ============== INDIA OPERATORS (Complete) ==============
OPERATORS = {
    # Airtel
    (404, 2): "Airtel", (404, 3): "Airtel", (404, 10): "Airtel",
    (404, 31): "Airtel", (404, 40): "Airtel", (404, 45): "Airtel",
    (404, 49): "Airtel", (404, 70): "Airtel", (404, 90): "Airtel",
    (404, 92): "Airtel", (404, 93): "Airtel", (404, 94): "Airtel",
    (404, 95): "Airtel", (404, 96): "Airtel", (404, 97): "Airtel",
    (404, 98): "Airtel",
    # Vi (Vodafone Idea)
    (404, 4): "Vi", (404, 5): "Vi", (404, 11): "Vi", (404, 12): "Vi",
    (404, 13): "Vi", (404, 14): "Vi", (404, 15): "Vi", (404, 16): "Vi",
    (404, 17): "Vi", (404, 18): "Vi", (404, 19): "Vi", (404, 20): "Vi",
    (404, 21): "Vi", (404, 22): "Vi", (404, 24): "Vi", (404, 25): "Vi",
    (404, 27): "Vi", (404, 28): "Vi", (404, 30): "Vi", (404, 43): "Vi",
    (404, 46): "Vi", (404, 56): "Vi", (404, 60): "Vi", (404, 78): "Vi",
    (404, 82): "Vi", (404, 84): "Vi", (404, 86): "Vi", (404, 87): "Vi",
    (404, 88): "Vi", (404, 89): "Vi",
    # Jio
    (405, 840): "Jio", (405, 854): "Jio", (405, 855): "Jio",
    (405, 856): "Jio", (405, 857): "Jio", (405, 858): "Jio",
    (405, 859): "Jio", (405, 860): "Jio", (405, 861): "Jio",
    (405, 862): "Jio", (405, 863): "Jio", (405, 864): "Jio",
    (405, 865): "Jio", (405, 866): "Jio", (405, 867): "Jio",
    (405, 868): "Jio", (405, 869): "Jio", (405, 870): "Jio",
    (405, 871): "Jio", (405, 872): "Jio", (405, 873): "Jio",
    (405, 874): "Jio",
    # BSNL
    (404, 34): "BSNL", (404, 36): "BSNL", (404, 38): "BSNL",
    (404, 51): "BSNL", (404, 52): "BSNL", (404, 53): "BSNL",
    (404, 54): "BSNL", (404, 55): "BSNL", (404, 57): "BSNL",
    (404, 58): "BSNL", (404, 59): "BSNL", (404, 62): "BSNL",
    (404, 64): "BSNL", (404, 66): "BSNL", (404, 71): "BSNL",
    (404, 72): "BSNL", (404, 73): "BSNL", (404, 74): "BSNL",
    (404, 75): "BSNL", (404, 76): "BSNL", (404, 77): "BSNL",
    (404, 79): "BSNL", (404, 80): "BSNL", (404, 81): "BSNL",
    # MTNL
    (404, 68): "MTNL", (404, 69): "MTNL",
}

# ============== LTE BANDS ==============
def get_band_name(band_num):
    bands = {
        1: "B1 (2100 MHz)",
        3: "B3 (1800 MHz)", 
        5: "B5 (850 MHz)",
        8: "B8 (900 MHz)",
        40: "B40 (2300 MHz TDD)",
        41: "B41 (2500 MHz TDD)",
    }
    return bands.get(band_num, f"B{band_num}")

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except:
        return ""

def clear():
    os.system('clear')


# ============== SIMPLE SIGNAL BAR (ASCII Safe) ==============
def signal_bar(rsrp, width=10):
    """Simple signal bar that works in Termux"""
    if rsrp is None:
        return "[----N/A----]"
    
    # Calculate strength (0-100%)
    # RSRP range: -140 (worst) to -40 (best)
    strength = max(0, min(100, (rsrp + 140) * 100 / 100))
    filled = int(width * strength / 100)
    
    # Color based on strength
    if strength > 60:
        color = C.G  # Green - Good
        quality = "Good"
    elif strength > 40:
        color = C.Y  # Yellow - Fair
        quality = "Fair"
    else:
        color = C.R  # Red - Poor
        quality = "Poor"
    
    bar = "#" * filled + "-" * (width - filled)
    return f"{color}[{bar}]{C.E} {rsrp}dBm ({quality})"

# ============== DISTANCE CALCULATION (Fixed) ==============
def calc_distance(ta, rsrp=None):
    """
    Calculate distance from Timing Advance
    LTE: 1 TA = 78.12 meters (based on speed of light / 2)
    """
    if ta is not None and ta >= 0:
        distance_m = ta * 78.12
        if distance_m < 1000:
            return f"{distance_m:.0f}m"
        else:
            return f"{distance_m/1000:.2f}km"
    
    # Fallback: estimate from RSRP (less accurate)
    if rsrp is not None:
        # Very rough estimate
        if rsrp > -70:
            return "~100-500m"
        elif rsrp > -85:
            return "~500m-1km"
        elif rsrp > -100:
            return "~1-3km"
        else:
            return "~3km+"
    
    return "Unknown"

# ============== SCANNERS ==============
def scan_cell():
    """Scan cell towers - handles dual SIM"""
    out = cmd("termux-telephony-cellinfo")
    if not out:
        return
    
    try:
        cells = json.loads(out)
        DATA['cell'] = cells
        
        # Separate by SIM (registered cells)
        sim1_cells = []
        sim2_cells = []
        neighbors = []
        
        registered_count = 0
        for cell in cells:
            if cell.get('registered'):
                registered_count += 1
                if registered_count == 1:
                    sim1_cells.append(cell)
                else:
                    sim2_cells.append(cell)
            else:
                neighbors.append(cell)
        
        DATA['sim1'] = sim1_cells[0] if sim1_cells else None
        DATA['sim2'] = sim2_cells[0] if sim2_cells else None
        DATA['neighbors'] = neighbors
        
    except Exception as e:
        pass

def scan_wifi():
    """Scan WiFi networks"""
    out = cmd("termux-wifi-scaninfo")
    if out and out != "[]":
        try:
            DATA['wifi'] = json.loads(out)
        except:
            DATA['wifi'] = []

def scan_bluetooth():
    """Scan Bluetooth devices"""
    out = cmd("termux-bluetooth-scaninfo")
    if out and out != "[]":
        try:
            DATA['bluetooth'] = json.loads(out)
        except:
            DATA['bluetooth'] = []

def scan_gps():
    """Get GPS location"""
    out = cmd("termux-location -p gps")
    if out:
        try:
            DATA['gps'] = json.loads(out)
        except:
            pass


# ============== DISPLAY FUNCTIONS (Simple ASCII) ==============
def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    uptime = datetime.now() - DATA['start_time']
    uptime_str = str(uptime).split('.')[0]
    
    print(f"""
{C.C}+===========================================================+
|                    8xRADAR v2.0                           |
|              Signal Intelligence Toolkit                  |
+===========================================================+
|  Time: {now}  |  Uptime: {uptime_str}  |  [Ctrl+C to Exit]  |
+===========================================================+{C.E}
""")

def render_sim_card(sim_num, cell):
    """Render single SIM card details"""
    if not cell:
        print(f"  {C.DIM}SIM {sim_num}: Not detected{C.E}")
        return
    
    mcc = cell.get('mcc', 0)
    mnc = cell.get('mnc', 0)
    operator = OPERATORS.get((mcc, mnc), f"Unknown ({mcc}/{mnc})")
    
    # Get band from bands array
    bands = cell.get('bands', [])
    band_num = bands[0] if bands else None
    band_name = get_band_name(band_num) if band_num else "Unknown"
    
    rsrp = cell.get('rsrp')
    rsrq = cell.get('rsrq')
    rssi = cell.get('rssi')
    sinr = cell.get('rssnr') or cell.get('sinr')
    ta = cell.get('timing_advance')
    ci = cell.get('ci')
    pci = cell.get('pci')
    tac = cell.get('tac')
    
    # Calculate eNodeB and Sector from CI
    enb_id = ci // 256 if ci else None
    sector = ci % 256 if ci else None
    
    # Distance
    distance = calc_distance(ta, rsrp)
    
    # Operator color
    if 'Jio' in operator:
        op_color = C.B
    elif 'Airtel' in operator:
        op_color = C.R
    elif 'Vi' in operator:
        op_color = C.M
    elif 'BSNL' in operator:
        op_color = C.Y
    else:
        op_color = C.W
    
    print(f"""
  {C.G}[SIM {sim_num}] {op_color}{C.BOLD}{operator}{C.E}
  +-------------------------------------------------------+
  | Network: 4G LTE                                       |
  | Band:    {band_name:<43}|
  +-------------------------------------------------------+
  | Signal:  {signal_bar(rsrp, 12):<43}|
  | RSRP:    {str(rsrp) + ' dBm':<10} RSRQ: {str(rsrq) + ' dB':<10} RSSI: {str(rssi) + ' dBm':<8}|
  | SINR:    {str(sinr) + ' dB' if sinr else 'N/A':<43}|
  +-------------------------------------------------------+
  | MCC:     {mcc:<10} MNC:  {mnc:<28}|
  | TAC:     {tac if tac else 'N/A':<10} CI:   {ci if ci else 'N/A':<28}|
  | eNodeB:  {enb_id if enb_id else 'N/A':<10} Sector: {sector if sector else 'N/A':<25}|
  | PCI:     {pci if pci else 'N/A':<43}|
  +-------------------------------------------------------+
  | TA:      {ta if ta is not None else 'N/A':<10} Distance: {C.Y}{distance}{C.E:<30}|
  +-------------------------------------------------------+""")

def render_cell_section():
    """Render cell tower section with dual SIM support"""
    print(f"\n{C.M}[CELL TOWERS]{C.E}")
    print(f"  Total towers detected: {len(DATA.get('cell', []))}")
    
    # SIM 1
    render_sim_card(1, DATA.get('sim1'))
    
    # SIM 2
    render_sim_card(2, DATA.get('sim2'))
    
    # Neighbors summary
    neighbors = DATA.get('neighbors', [])
    if neighbors:
        print(f"\n  {C.DIM}Neighbor Cells: {len(neighbors)}{C.E}")
        for i, n in enumerate(neighbors[:5]):
            rsrp = n.get('rsrp', 'N/A')
            pci = n.get('pci', '?')
            bands = n.get('bands', [])
            band = bands[0] if bands else '?'
            print(f"    [{i+1}] PCI:{pci} Band:B{band} RSRP:{rsrp}dBm")

def render_wifi_section():
    """Render WiFi section"""
    wifi = DATA.get('wifi', [])
    
    print(f"\n{C.G}[WiFi NETWORKS]{C.E}")
    
    if not wifi:
        print(f"  {C.Y}No WiFi data - Grant location permission to Termux:API{C.E}")
        print(f"  {C.DIM}Settings > Apps > Termux:API > Permissions > Location{C.E}")
        return
    
    print(f"  Found: {len(wifi)} networks\n")
    print(f"  {'SSID':<25} {'Signal':<15} {'Ch':>3} {'Security'}")
    print(f"  {'-'*25} {'-'*15} {'-'*3} {'-'*15}")
    
    # Sort by signal strength
    wifi_sorted = sorted(wifi, key=lambda x: x.get('rssi', -100), reverse=True)
    
    for net in wifi_sorted[:8]:
        ssid = net.get('ssid', '[Hidden]')[:24] or '[Hidden]'
        rssi = net.get('rssi', -100)
        freq = net.get('frequency', 0)
        ch = (freq - 2412) // 5 + 1 if 2412 <= freq <= 2484 else (freq - 5170) // 5 + 34 if freq > 5000 else 0
        sec = net.get('capabilities', 'Open')[:15]
        
        # Signal color
        if rssi > -50:
            sig_color = C.G
        elif rssi > -70:
            sig_color = C.Y
        else:
            sig_color = C.R
        
        print(f"  {ssid:<25} {sig_color}{rssi:>4}dBm{C.E}       {ch:>3} {sec}")

def render_bluetooth_section():
    """Render Bluetooth section"""
    bt = DATA.get('bluetooth', [])
    
    print(f"\n{C.B}[BLUETOOTH DEVICES]{C.E}")
    
    if not bt:
        print(f"  {C.Y}No Bluetooth devices found{C.E}")
        print(f"  {C.DIM}Make sure Bluetooth is ON and devices are nearby{C.E}")
        return
    
    print(f"  Found: {len(bt)} devices\n")
    
    for dev in bt[:6]:
        name = dev.get('name', 'Unknown')[:30]
        rssi = dev.get('rssi', 'N/A')
        mac = dev.get('address', '?')
        
        # Device type icon (simple)
        n = name.lower()
        if any(x in n for x in ['airpod', 'buds', 'earphone', 'headphone']):
            icon = "[Audio]"
        elif any(x in n for x in ['band', 'watch', 'fit']):
            icon = "[Watch]"
        elif any(x in n for x in ['phone', 'iphone', 'samsung']):
            icon = "[Phone]"
        else:
            icon = "[Device]"
        
        print(f"  {icon} {name:<25} {rssi}dBm")

def render_gps_section():
    """Render GPS section"""
    gps = DATA.get('gps')
    
    print(f"\n{C.Y}[GPS LOCATION]{C.E}")
    
    if not gps:
        print(f"  {C.DIM}Getting GPS fix...{C.E}")
        return
    
    lat = gps.get('latitude', 0)
    lon = gps.get('longitude', 0)
    alt = gps.get('altitude', 0)
    acc = gps.get('accuracy', 0)
    
    print(f"  Latitude:  {lat:.6f}")
    print(f"  Longitude: {lon:.6f}")
    print(f"  Altitude:  {alt:.1f}m")
    print(f"  Accuracy:  +/-{acc:.1f}m")


# ============== MAIN ==============
def background_scanner():
    """Background scanning"""
    while True:
        try:
            scan_cell()
            scan_wifi()
            scan_bluetooth()
            if int(time.time()) % 5 == 0:
                scan_gps()
            time.sleep(3)
        except:
            time.sleep(3)

def render_dashboard():
    """Render full dashboard"""
    clear()
    render_header()
    render_cell_section()
    render_wifi_section()
    render_bluetooth_section()
    render_gps_section()
    print(f"\n{C.DIM}  Auto-refresh every 3 seconds...{C.E}")

def main():
    clear()
    print(f"""
{C.C}
+===========================================================+
|                                                           |
|     .d8888b.           8888888b.                888       |
|    d88P  Y88b          888   Y88b               888       |
|    Y88b. d88P          888    888               888       |
|     "Y88888"  888  888 888   d88P  8888b.   .d88888       |
|    .d8P""Y8b. `Y8bd8P' 8888888P"      "88b d88" 888       |
|    888    888   X88K   888 T88b   .d888888 888  888       |
|    Y88b  d88P .d8""8b. 888  T88b  888  888 Y88b 888       |
|     "Y8888P"  888  888 888   T88b "Y888888  "Y88888       |
|                                                           |
|              Signal Intelligence Toolkit                  |
|                     Version 2.0                           |
+===========================================================+
{C.E}""")
    
    print(f"  {C.Y}Initializing...{C.E}")
    
    # Initial scans
    print(f"  {C.DIM}[1/4] Scanning Cell Towers...{C.E}")
    scan_cell()
    
    print(f"  {C.DIM}[2/4] Scanning WiFi...{C.E}")
    scan_wifi()
    
    print(f"  {C.DIM}[3/4] Scanning Bluetooth...{C.E}")
    scan_bluetooth()
    
    print(f"  {C.DIM}[4/4] Getting GPS...{C.E}")
    scan_gps()
    
    print(f"\n  {C.G}Ready! Starting dashboard...{C.E}")
    time.sleep(1)
    
    # Start background scanner
    scanner = threading.Thread(target=background_scanner, daemon=True)
    scanner.start()
    
    # Main loop
    try:
        while True:
            render_dashboard()
            time.sleep(3)
    except KeyboardInterrupt:
        clear()
        print(f"""
{C.G}
+===========================================================+
|                   8xRadar Stopped                         |
+===========================================================+
|  Session Summary:                                         |
|    Cell Towers: {len(DATA.get('cell', [])):>3}                                      |
|    WiFi Networks: {len(DATA.get('wifi', [])):>3}                                    |
|    Bluetooth: {len(DATA.get('bluetooth', [])):>3}                                       |
+===========================================================+
{C.E}""")
        
        # Export option
        try:
            export = input(f"  {C.Y}Export data? (y/n): {C.E}").strip().lower()
            if export == 'y':
                filename = f"8xradar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'cell': DATA.get('cell', []),
                        'wifi': DATA.get('wifi', []),
                        'bluetooth': DATA.get('bluetooth', []),
                        'gps': DATA.get('gps'),
                    }, f, indent=2)
                print(f"  {C.G}Saved: {filename}{C.E}")
        except:
            pass
        
        print(f"\n  {C.G}Goodbye!{C.E}\n")

if __name__ == "__main__":
    main()
