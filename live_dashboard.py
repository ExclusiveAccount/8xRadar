#!/usr/bin/env python3
"""
📡 SIGNAL RADAR - Live Auto-Refresh Dashboard
No menu, automatic scanning, real-time updates
"""

import subprocess
import json
import os
import sys
import time
import threading
from datetime import datetime

# ============== CONFIG ==============
REFRESH_INTERVAL = 5  # seconds
CLEAR_SCREEN = True

# ============== COLORS ==============
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
    E = '\033[0m'    # End

# ============== GLOBAL DATA ==============
data = {
    'wifi': [],
    'bluetooth': [],
    'cell': [],
    'network': [],
    'scan_time': '',
    'scanning': {'wifi': False, 'bt': False, 'cell': False, 'net': False}
}

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except:
        return ""

def clear():
    if CLEAR_SCREEN:
        os.system('clear' if os.name != 'nt' else 'cls')

# ============== SCANNERS ==============
def scan_wifi():
    data['scanning']['wifi'] = True
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    try:
        nets = json.loads(out) if out else []
        data['wifi'] = sorted(nets, key=lambda x: x.get('rssi', -100), reverse=True)[:15]
    except:
        data['wifi'] = []
    data['scanning']['wifi'] = False

def scan_bluetooth():
    data['scanning']['bt'] = True
    out = cmd("termux-bluetooth-scaninfo 2>/dev/null")
    try:
        data['bluetooth'] = json.loads(out) if out else []
    except:
        data['bluetooth'] = []
    data['scanning']['bt'] = False

def scan_cell():
    data['scanning']['cell'] = True
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    try:
        data['cell'] = json.loads(out) if out else []
    except:
        data['cell'] = []
    data['scanning']['cell'] = False

def scan_network():
    data['scanning']['net'] = True
    gw = cmd("ip route | grep default | awk '{print $3}'").strip()
    if gw:
        subnet = '.'.join(gw.split('.')[:-1]) + '.0/24'
        out = cmd(f"nmap -sn {subnet} 2>/dev/null | grep 'Nmap scan report' | wc -l")
        try:
            data['network'] = [{'count': int(out.strip())}]
        except:
            data['network'] = []
    data['scanning']['net'] = False

# ============== HELPERS ==============
def signal_bar(rssi):
    if rssi > -50: return f"{C.G}████{C.E}"
    elif rssi > -60: return f"{C.G}███{C.DIM}█{C.E}"
    elif rssi > -70: return f"{C.Y}██{C.DIM}██{C.E}"
    elif rssi > -80: return f"{C.Y}█{C.DIM}███{C.E}"
    else: return f"{C.R}█{C.DIM}███{C.E}"

def get_operator(mcc, mnc):
    ops = {
        (404,10):"Airtel",(404,40):"Airtel",(404,45):"Airtel",(404,49):"Airtel",
        (404,90):"Airtel",(404,92):"Airtel",(404,93):"Airtel",(404,94):"Airtel",
        (404,11):"Vi",(404,12):"Vi",(404,20):"Vi",(404,27):"Vi",(404,86):"Vi",
        (405,840):"Jio",(405,854):"Jio",(405,855):"Jio",(405,857):"Jio",
        (405,858):"Jio",(405,859):"Jio",(405,860):"Jio",(405,861):"Jio",
        (404,34):"BSNL",(404,38):"BSNL",(404,51):"BSNL",(404,72):"BSNL",
    }
    return ops.get((mcc, mnc), "Unknown")

def classify_bt(name):
    n = name.lower()
    if any(x in n for x in ['airpod','buds','earphone','jbl']): return "🎧"
    elif any(x in n for x in ['band','watch','fit']): return "⌚"
    elif any(x in n for x in ['tv','fire','roku']): return "📺"
    elif any(x in n for x in ['phone','iphone','samsung','oneplus','xiaomi','redmi']): return "📱"
    elif any(x in n for x in ['speaker','echo','alexa']): return "🔊"
    elif any(x in n for x in ['laptop','macbook']): return "💻"
    else: return "📟"

def sec_icon(sec):
    if 'WPA3' in sec: return f"{C.G}🔒{C.E}"
    elif 'WPA2' in sec: return f"{C.G}🔐{C.E}"
    elif 'WPA' in sec: return f"{C.Y}🔑{C.E}"
    elif 'WEP' in sec: return f"{C.R}⚠️{C.E}"
    else: return f"{C.R}🔓{C.E}"


# ============== DASHBOARD RENDER ==============
def render_dashboard():
    clear()
    now = datetime.now().strftime("%H:%M:%S")
    
    # Header
    print(f"""
{C.C}{C.BOLD}╔══════════════════════════════════════════════════════════════════════╗
║                    📡 SIGNAL RADAR - LIVE DASHBOARD                   ║
╠══════════════════════════════════════════════════════════════════════╣{C.E}
{C.DIM}║  Last Update: {now}                              [Ctrl+C to Exit]  ║{C.E}
{C.C}╚══════════════════════════════════════════════════════════════════════╝{C.E}
""")

    # Stats Bar
    wifi_count = len(data['wifi'])
    bt_count = len(data['bluetooth'])
    cell_count = len(data['cell'])
    net_count = data['network'][0]['count'] if data['network'] else 0
    
    spin = "◐◓◑◒"[int(time.time()) % 4]
    
    print(f"  {C.G}📡 WiFi: {wifi_count:>2}{C.E}  │  {C.B}🔵 Bluetooth: {bt_count:>2}{C.E}  │  {C.M}📶 Towers: {cell_count}{C.E}  │  {C.Y}🌐 Devices: {net_count:>2}{C.E}  │  {spin}")
    print()

    # ============== WiFi Section ==============
    print(f"{C.G}{C.BOLD}┌─────────────────────────── 📡 WiFi Networks ───────────────────────────┐{C.E}")
    
    if data['scanning']['wifi']:
        print(f"  {C.Y}Scanning...{C.E}")
    elif data['wifi']:
        print(f"  {'SSID':<22} {'Signal':^8} {'Sec':^4} {'Ch':>3}")
        print(f"  {'-'*22} {'-'*8} {'-'*4} {'-'*3}")
        
        for net in data['wifi'][:8]:
            ssid = net.get('ssid', 'Hidden')[:21] or '[Hidden]'
            rssi = net.get('rssi', -100)
            sec = net.get('capabilities', '')[:20]
            freq = net.get('frequency', 0)
            ch = (freq - 2412) // 5 + 1 if 2412 <= freq <= 2484 else (freq - 5170) // 5 + 34 if freq > 5000 else 0
            
            bar = signal_bar(rssi)
            icon = sec_icon(sec)
            
            print(f"  {ssid:<22} {bar} {rssi:>3}  {icon}  {ch:>3}")
    else:
        print(f"  {C.DIM}No WiFi data - Install Termux:API{C.E}")
    
    print(f"{C.G}└────────────────────────────────────────────────────────────────────────┘{C.E}")
    print()

    # ============== Bluetooth Section ==============
    print(f"{C.B}{C.BOLD}┌─────────────────────────── 🔵 Bluetooth ───────────────────────────────┐{C.E}")
    
    if data['scanning']['bt']:
        print(f"  {C.Y}Scanning...{C.E}")
    elif data['bluetooth']:
        for dev in data['bluetooth'][:6]:
            name = dev.get('name', 'Unknown')[:25]
            rssi = dev.get('rssi', 0)
            icon = classify_bt(name)
            bar = signal_bar(rssi)
            print(f"  {icon} {name:<25} {bar} {rssi:>3} dBm")
    else:
        print(f"  {C.DIM}No Bluetooth devices found{C.E}")
    
    print(f"{C.B}└────────────────────────────────────────────────────────────────────────┘{C.E}")
    print()

    # ============== Cell Tower Section ==============
    print(f"{C.M}{C.BOLD}┌─────────────────────────── 📶 Cell Towers ─────────────────────────────┐{C.E}")
    
    if data['scanning']['cell']:
        print(f"  {C.Y}Scanning...{C.E}")
    elif data['cell']:
        for cell in data['cell'][:3]:
            ctype = cell.get('type', 'Unknown')
            registered = "●" if cell.get('registered') else "○"
            
            if 'lte' in ctype.lower():
                mcc = cell.get('mcc', 0)
                mnc = cell.get('mnc', 0)
                cid = cell.get('ci', 'N/A')
                rsrp = cell.get('rsrp', -100)
                op = get_operator(mcc, mnc)
                bar = signal_bar(rsrp)
                
                print(f"  {C.G if registered == '●' else C.DIM}{registered}{C.E} {C.BOLD}{op:<10}{C.E} │ CID: {cid:<10} │ {bar} {rsrp:>3} dBm │ 4G LTE")
            
            elif 'gsm' in ctype.lower():
                mcc = cell.get('mcc', 0)
                mnc = cell.get('mnc', 0)
                lac = cell.get('lac', 'N/A')
                cid = cell.get('cid', 'N/A')
                rssi = cell.get('rssi', -100)
                op = get_operator(mcc, mnc)
                bar = signal_bar(rssi)
                
                print(f"  {C.G if registered == '●' else C.DIM}{registered}{C.E} {C.BOLD}{op:<10}{C.E} │ LAC:{lac} CID:{cid} │ {bar} {rssi:>3} dBm │ 2G GSM")
            
            elif 'nr' in ctype.lower() or '5g' in ctype.lower():
                mcc = cell.get('mcc', 0)
                mnc = cell.get('mnc', 0)
                op = get_operator(mcc, mnc)
                ss = cell.get('ssRsrp', cell.get('csiRsrp', -100))
                bar = signal_bar(ss)
                
                print(f"  {C.G if registered == '●' else C.DIM}{registered}{C.E} {C.BOLD}{op:<10}{C.E} │ 5G NR │ {bar} {ss:>3} dBm │ {C.C}5G{C.E}")
    else:
        print(f"  {C.DIM}No cell data - Install Termux:API{C.E}")
    
    print(f"{C.M}└────────────────────────────────────────────────────────────────────────┘{C.E}")
    print()

    # ============== Security Alerts ==============
    alerts = []
    
    # Check for open WiFi
    open_wifi = [n for n in data['wifi'] if not n.get('capabilities') or 'WPA' not in n.get('capabilities', '')]
    if open_wifi:
        alerts.append(f"{C.R}⚠️  {len(open_wifi)} Open/Weak WiFi networks detected!{C.E}")
    
    # Check for WEP
    wep_wifi = [n for n in data['wifi'] if 'WEP' in n.get('capabilities', '')]
    if wep_wifi:
        alerts.append(f"{C.R}⚠️  {len(wep_wifi)} WEP encrypted networks (vulnerable)!{C.E}")
    
    # Strong nearby signals (potential cameras)
    strong = [n for n in data['wifi'] if n.get('rssi', -100) > -40]
    if strong:
        alerts.append(f"{C.Y}📷 {len(strong)} very strong signals nearby (check for cameras){C.E}")
    
    if alerts:
        print(f"{C.R}{C.BOLD}┌─────────────────────────── ⚠️  ALERTS ──────────────────────────────────┐{C.E}")
        for alert in alerts:
            print(f"  {alert}")
        print(f"{C.R}└────────────────────────────────────────────────────────────────────────┘{C.E}")
    
    print(f"\n{C.DIM}  Auto-refreshing every {REFRESH_INTERVAL}s... Press Ctrl+C to exit{C.E}")


# ============== BACKGROUND SCANNER ==============
def background_scanner():
    """Continuously scan in background"""
    while True:
        threads = [
            threading.Thread(target=scan_wifi),
            threading.Thread(target=scan_bluetooth),
            threading.Thread(target=scan_cell),
        ]
        
        for t in threads:
            t.daemon = True
            t.start()
        
        for t in threads:
            t.join(timeout=10)
        
        # Network scan less frequently
        if int(time.time()) % 3 == 0:
            scan_network()
        
        time.sleep(REFRESH_INTERVAL)

# ============== MAIN ==============
def main():
    print(f"{C.C}")
    print("  ╔═══════════════════════════════════════╗")
    print("  ║     📡 SIGNAL RADAR - Starting...     ║")
    print("  ╚═══════════════════════════════════════╝")
    print(f"{C.E}")
    print(f"  {C.Y}Initializing scanners...{C.E}")
    
    # Initial scan
    print(f"  {C.DIM}[1/4] WiFi...{C.E}")
    scan_wifi()
    print(f"  {C.DIM}[2/4] Bluetooth...{C.E}")
    scan_bluetooth()
    print(f"  {C.DIM}[3/4] Cell Towers...{C.E}")
    scan_cell()
    print(f"  {C.DIM}[4/4] Network...{C.E}")
    scan_network()
    
    print(f"\n  {C.G}✓ Ready! Starting live dashboard...{C.E}")
    time.sleep(1)
    
    # Start background scanner
    scanner_thread = threading.Thread(target=background_scanner)
    scanner_thread.daemon = True
    scanner_thread.start()
    
    # Main display loop
    try:
        while True:
            render_dashboard()
            time.sleep(2)
    except KeyboardInterrupt:
        clear()
        print(f"\n{C.G}  👋 Signal Radar stopped. Goodbye!{C.E}\n")
        
        # Export option
        export = input(f"  {C.Y}Export data to JSON? (y/n): {C.E}").strip().lower()
        if export == 'y':
            filename = f"signal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  {C.G}✓ Saved to {filename}{C.E}\n")

if __name__ == "__main__":
    main()
