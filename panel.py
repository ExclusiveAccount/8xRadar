#!/usr/bin/env python3
"""
📡 SIGNAL RADAR - Terminal Control Panel
All tools in one menu - WiFi, Bluetooth, Cell, Satellite, Camera
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime

# ============== COLORS ==============
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
    BOLD = '\033[1m'; DIM = '\033[2m'; E = '\033[0m'
    BG_B = '\033[44m'; BG_G = '\033[42m'; BG_R = '\033[41m'

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout + r.stderr
    except:
        return ""

def pause():
    input(f"\n{C.DIM}Press Enter to continue...{C.E}")

# ============== BANNER ==============
def banner():
    clear()
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
    ║              📡 Signal Intelligence Control Panel                 ║
    ║                        Termux Edition                             ║
    ╚═══════════════════════════════════════════════════════════════════╝
{C.E}""")

# ============== MAIN MENU ==============
def main_menu():
    print(f"""
{C.BOLD}    ┌─────────────────── MAIN MENU ───────────────────┐{C.E}
    │                                                   │
    │  {C.G}[1]{C.E} 📡 WiFi Scanner                              │
    │  {C.B}[2]{C.E} 🔵 Bluetooth Scanner                         │
    │  {C.M}[3]{C.E} 📶 Cell Tower Analyzer                       │
    │  {C.C}[4]{C.E} 🛰️  Satellite Tracker                         │
    │  {C.R}[5]{C.E} 📷 Camera Detector                           │
    │  {C.Y}[6]{C.E} 🌐 Network Scanner                           │
    │  {C.G}[7]{C.E} 📍 GPS Location                              │
    │                                                   │
    │  {C.C}[8]{C.E} ⚡ FULL SCAN (All at once)                   │
    │  {C.G}[9]{C.E} 🔄 Live Dashboard (Auto-refresh)             │
    │                                                   │
    │  {C.R}[0]{C.E} ❌ Exit                                       │
    │                                                   │
    └───────────────────────────────────────────────────┘
""")

# ============== OPERATORS ==============
OPERATORS = {
    (404,10):"Airtel",(404,40):"Airtel",(404,45):"Airtel",(404,49):"Airtel",
    (404,90):"Airtel",(404,92):"Airtel",(404,93):"Airtel",(404,94):"Airtel",
    (404,11):"Vi",(404,12):"Vi",(404,20):"Vi",(404,86):"Vi",(404,88):"Vi",
    (405,840):"Jio",(405,854):"Jio",(405,855):"Jio",(405,857):"Jio",
    (405,858):"Jio",(405,859):"Jio",(405,860):"Jio",(405,861):"Jio",
    (405,862):"Jio",(405,863):"Jio",(405,864):"Jio",(405,865):"Jio",
    (404,34):"BSNL",(404,38):"BSNL",(404,51):"BSNL",(404,72):"BSNL",
}

LTE_BANDS = {1:"B1(2100)",3:"B3(1800)",5:"B5(850)",8:"B8(900)",40:"B40(2300)",41:"B41(2500)"}

def earfcn_to_band(e):
    if 0<=e<=599: return 1
    if 1200<=e<=1949: return 3
    if 2400<=e<=2649: return 5
    if 3450<=e<=3799: return 8
    if 38650<=e<=39649: return 40
    if 39650<=e<=41589: return 41
    return None

def signal_bar(rssi):
    if rssi is None: return f"{C.DIM}░░░░░{C.E}"
    if rssi > -50: return f"{C.G}█████{C.E}"
    elif rssi > -60: return f"{C.G}████{C.DIM}░{C.E}"
    elif rssi > -70: return f"{C.Y}███{C.DIM}░░{C.E}"
    elif rssi > -80: return f"{C.Y}██{C.DIM}░░░{C.E}"
    elif rssi > -90: return f"{C.R}█{C.DIM}░░░░{C.E}"
    else: return f"{C.R}░{C.DIM}░░░░{C.E}"


# ============== 1. WIFI SCANNER ==============
def wifi_scanner():
    clear()
    print(f"\n{C.G}{C.BOLD}╔══════════════════════ 📡 WiFi SCANNER ══════════════════════╗{C.E}")
    print(f"{C.Y}Scanning WiFi networks...{C.E}\n")
    
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    if not out or 'error' in out.lower():
        print(f"{C.R}Error: Install Termux:API app from F-Droid{C.E}")
        pause()
        return
    
    try:
        networks = sorted(json.loads(out), key=lambda x: x.get('rssi',-100), reverse=True)
        
        print(f"  {C.BOLD}Found {len(networks)} networks:{C.E}\n")
        print(f"  {'SSID':<25} {'Signal':^10} {'Security':<15} {'Ch':>3} {'Band'}")
        print(f"  {'-'*25} {'-'*10} {'-'*15} {'-'*3} {'-'*5}")
        
        for net in networks[:20]:
            ssid = net.get('ssid','[Hidden]')[:24] or '[Hidden]'
            rssi = net.get('rssi',-100)
            sec = net.get('capabilities','Open')[:14]
            freq = net.get('frequency',0)
            ch = (freq-2412)//5+1 if 2412<=freq<=2484 else (freq-5170)//5+34 if freq>5000 else 0
            band = '2.4G' if freq<5000 else '5G'
            
            bar = signal_bar(rssi)
            
            # Security color
            if 'WPA3' in sec: sec_c = C.G
            elif 'WPA2' in sec: sec_c = C.G
            elif 'WPA' in sec: sec_c = C.Y
            elif 'WEP' in sec: sec_c = C.R
            else: sec_c = C.R
            
            print(f"  {ssid:<25} {bar} {rssi:>3}  {sec_c}{sec:<15}{C.E} {ch:>3} {band}")
        
        # Stats
        open_nets = len([n for n in networks if 'WPA' not in n.get('capabilities','')])
        print(f"\n  {C.BOLD}Stats:{C.E}")
        print(f"    Total: {len(networks)} | Open/Weak: {C.R}{open_nets}{C.E} | 5GHz: {len([n for n in networks if n.get('frequency',0)>5000])}")
        
    except Exception as e:
        print(f"{C.R}Error parsing: {e}{C.E}")
    
    print(f"\n{C.G}╚══════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 2. BLUETOOTH SCANNER ==============
def bluetooth_scanner():
    clear()
    print(f"\n{C.B}{C.BOLD}╔══════════════════════ 🔵 BLUETOOTH SCANNER ══════════════════════╗{C.E}")
    print(f"{C.Y}Scanning Bluetooth devices...{C.E}\n")
    
    out = cmd("termux-bluetooth-scaninfo 2>/dev/null")
    if not out or 'error' in out.lower():
        print(f"{C.R}Error: Install Termux:API app{C.E}")
        pause()
        return
    
    try:
        devices = json.loads(out)
        
        print(f"  {C.BOLD}Found {len(devices)} devices:{C.E}\n")
        print(f"  {'Name':<30} {'Signal':^10} {'MAC':<18} {'Type'}")
        print(f"  {'-'*30} {'-'*10} {'-'*18} {'-'*10}")
        
        for dev in devices:
            name = dev.get('name','Unknown')[:29]
            rssi = dev.get('rssi',-100)
            mac = dev.get('address','?')
            
            # Classify device
            n = name.lower()
            if any(x in n for x in ['airpod','buds','earphone','jbl']): dtype = "🎧 Audio"
            elif any(x in n for x in ['band','watch','fit']): dtype = "⌚ Wearable"
            elif any(x in n for x in ['tv','fire','roku']): dtype = "📺 TV"
            elif any(x in n for x in ['phone','iphone','samsung','xiaomi']): dtype = "📱 Phone"
            elif any(x in n for x in ['speaker','echo']): dtype = "🔊 Speaker"
            else: dtype = "📟 Device"
            
            bar = signal_bar(rssi)
            print(f"  {name:<30} {bar} {rssi:>3}  {mac:<18} {dtype}")
        
    except Exception as e:
        print(f"{C.R}Error: {e}{C.E}")
    
    print(f"\n{C.B}╚══════════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 3. CELL TOWER ANALYZER ==============
def cell_analyzer():
    clear()
    print(f"\n{C.M}{C.BOLD}╔══════════════════════ 📶 CELL TOWER ANALYZER ══════════════════════╗{C.E}")
    print(f"{C.Y}Scanning cell towers...{C.E}\n")
    
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    if not out or 'error' in out.lower():
        print(f"{C.R}Error: Install Termux:API app{C.E}")
        pause()
        return
    
    try:
        cells = json.loads(out)
        lte_count = nr_count = 0
        
        for cell in cells:
            ctype = cell.get('type','').lower()
            reg = cell.get('registered',False)
            status = f"{C.G}● CONNECTED{C.E}" if reg else f"{C.DIM}○ Neighbor{C.E}"
            
            if 'lte' in ctype:
                lte_count += 1
                mcc,mnc = cell.get('mcc',0),cell.get('mnc',0)
                op = OPERATORS.get((mcc,mnc),'Unknown')
                earfcn = cell.get('earfcn',0)
                band = earfcn_to_band(earfcn)
                ci = cell.get('ci')
                ta = cell.get('timingAdvance')
                
                print(f"  {C.G}━━━ 4G LTE {status} ━━━{C.E}")
                print(f"  │ Operator: {C.BOLD}{op}{C.E}")
                print(f"  │ MCC: {mcc}  MNC: {mnc}")
                print(f"  │ TAC: {cell.get('tac')}  CI: {ci}")
                if ci:
                    print(f"  │ eNodeB: {ci//256}  Sector: {ci%256}")
                print(f"  │ PCI: {cell.get('pci')}  EARFCN: {earfcn}")
                print(f"  │ Band: {C.C}{LTE_BANDS.get(band,'?')}{C.E}")
                print(f"  │ RSRP: {cell.get('rsrp')} dBm  RSRQ: {cell.get('rsrq')} dB")
                print(f"  │ SINR: {cell.get('rssnr')} dB")
                if ta is not None and ta >= 0:
                    dist = ta * 78.12
                    print(f"  │ TA: {ta}  Distance: {C.Y}~{dist:.0f}m{C.E}")
                print()
                
            elif 'nr' in ctype or '5g' in ctype:
                nr_count += 1
                mcc,mnc = cell.get('mcc',0),cell.get('mnc',0)
                op = OPERATORS.get((mcc,mnc),'Unknown')
                
                print(f"  {C.C}━━━ 5G NR {status} ━━━{C.E}")
                print(f"  │ Operator: {C.BOLD}{op}{C.E}")
                print(f"  │ MCC: {mcc}  MNC: {mnc}")
                print(f"  │ NCI: {cell.get('nci')}  PCI: {cell.get('pci')}")
                print(f"  │ NRARFCN: {cell.get('nrarfcn')}")
                print(f"  │ SS-RSRP: {cell.get('ssRsrp')} dBm")
                print(f"  │ SS-RSRQ: {cell.get('ssRsrq')} dB")
                print(f"  │ SS-SINR: {cell.get('ssSinr')} dB")
                print()
        
        # CA Detection
        total = lte_count + nr_count
        if total >= 2:
            print(f"  {C.G}⚡ Carrier Aggregation: {total}CC detected!{C.E}")
            if nr_count > 0 and lte_count > 0:
                print(f"  {C.C}   Mode: NSA (Non-Standalone 5G){C.E}")
        
    except Exception as e:
        print(f"{C.R}Error: {e}{C.E}")
    
    print(f"\n{C.M}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()


# ============== 4. SATELLITE TRACKER ==============
def satellite_tracker():
    clear()
    print(f"\n{C.C}{C.BOLD}╔══════════════════════ 🛰️ SATELLITE TRACKER ══════════════════════╗{C.E}")
    print(f"{C.Y}Getting GPS satellite info...{C.E}\n")
    
    # Get location first
    out = cmd("termux-location -p gps 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            print(f"  {C.BOLD}📍 Your Location:{C.E}")
            print(f"     Latitude:  {loc.get('latitude',0):.6f}°")
            print(f"     Longitude: {loc.get('longitude',0):.6f}°")
            print(f"     Altitude:  {loc.get('altitude',0):.1f} m")
            print(f"     Accuracy:  ±{loc.get('accuracy',0):.1f} m")
            print()
        except:
            pass
    
    # GNSS Info
    print(f"  {C.BOLD}📡 GNSS Constellations:{C.E}")
    print(f"     🇺🇸 GPS      - 32 satellites (USA)")
    print(f"     🇷🇺 GLONASS  - 24 satellites (Russia)")
    print(f"     🇪🇺 Galileo  - 30 satellites (EU)")
    print(f"     🇨🇳 BeiDou   - 35 satellites (China)")
    print(f"     🇮🇳 NavIC    - 7 satellites (India - ISRO)")
    print()
    
    # NavIC Details
    print(f"  {C.M}{C.BOLD}🇮🇳 NavIC (IRNSS) - Indian Navigation:{C.E}")
    print(f"     IRNSS-1A to 1I - 7 operational satellites")
    print(f"     Coverage: India + 1500km around")
    print(f"     Accuracy: <20m (India), <10m with GAGAN")
    print()
    
    # ISS
    print(f"  {C.Y}{C.BOLD}🛸 ISS (International Space Station):{C.E}")
    iss_out = cmd("curl -s 'http://api.open-notify.org/iss-now.json' 2>/dev/null")
    if iss_out:
        try:
            iss = json.loads(iss_out)
            pos = iss.get('iss_position',{})
            print(f"     Latitude:  {pos.get('latitude','?')}°")
            print(f"     Longitude: {pos.get('longitude','?')}°")
            print(f"     Altitude:  ~420 km")
            print(f"     Speed:     ~27,600 km/h")
        except:
            print(f"     {C.DIM}Unable to get ISS position{C.E}")
    print()
    
    # ISRO Satellites
    print(f"  {C.M}{C.BOLD}🚀 ISRO Satellites:{C.E}")
    print(f"     Communication: GSAT-11, GSAT-30, GSAT-31")
    print(f"     Navigation:    NavIC (IRNSS-1A to 1I)")
    print(f"     Earth Obs:     Cartosat-3, RISAT-2BR1, EOS-04")
    print(f"     Weather:       INSAT-3D, INSAT-3DR")
    print()
    
    # DTH
    print(f"  {C.B}{C.BOLD}📺 DTH Satellites (India):{C.E}")
    print(f"     GSAT-15 (93.5°E) - Tata Play, Airtel")
    print(f"     INSAT-4A (83°E)  - DD Free Dish")
    print(f"     SES-8 (95°E)     - Dish TV")
    
    print(f"\n{C.C}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 5. CAMERA DETECTOR ==============
def camera_detector():
    clear()
    print(f"\n{C.R}{C.BOLD}╔══════════════════════ 📷 CAMERA DETECTOR ══════════════════════╗{C.E}")
    print(f"{C.Y}Scanning for hidden cameras...{C.E}\n")
    
    # Camera vendor MACs
    cam_vendors = {
        '28:57:be':'Hikvision','54:c4:15':'Hikvision','c0:56:e3':'Hikvision',
        'e0:50:8b':'Dahua','3c:ef:8c':'Dahua','90:02:a9':'Dahua',
        '00:55:da':'Xiongmai','7c:dd:90':'Xiaomi Cam','00:40:8c':'Axis',
    }
    
    cameras_found = []
    
    # Scan WiFi for camera devices
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    if out:
        try:
            networks = json.loads(out)
            for net in networks:
                ssid = net.get('ssid','').lower()
                bssid = net.get('bssid','').lower()
                prefix = bssid[:8]
                
                # Check vendor
                if prefix in cam_vendors:
                    cameras_found.append({
                        'type': 'WiFi Camera (Vendor Match)',
                        'ssid': net.get('ssid','?'),
                        'mac': bssid,
                        'vendor': cam_vendors[prefix],
                        'signal': net.get('rssi'),
                        'risk': 'HIGH'
                    })
                
                # Check SSID patterns
                cam_patterns = ['cam','ipcam','camera','dvr','nvr','cctv','hikvision','dahua','yi-','wyze']
                if any(p in ssid for p in cam_patterns):
                    cameras_found.append({
                        'type': 'Suspected Camera (SSID)',
                        'ssid': net.get('ssid','?'),
                        'mac': bssid,
                        'vendor': 'Unknown',
                        'signal': net.get('rssi'),
                        'risk': 'MEDIUM'
                    })
        except:
            pass
    
    if cameras_found:
        print(f"  {C.R}⚠️  POTENTIAL CAMERAS DETECTED:{C.E}\n")
        for cam in cameras_found:
            risk_c = C.R if cam['risk']=='HIGH' else C.Y
            print(f"  {risk_c}● {cam['type']}{C.E}")
            print(f"    SSID:   {cam['ssid']}")
            print(f"    MAC:    {cam['mac']}")
            print(f"    Vendor: {cam['vendor']}")
            print(f"    Signal: {cam['signal']} dBm")
            print(f"    Risk:   {risk_c}{cam['risk']}{C.E}")
            print()
    else:
        print(f"  {C.G}✓ No obvious cameras detected in WiFi scan{C.E}")
        print(f"  {C.DIM}Note: Wired cameras won't be detected{C.E}")
    
    print(f"\n  {C.BOLD}Tips to detect hidden cameras:{C.E}")
    print(f"    • Look for small holes in walls/objects")
    print(f"    • Use phone camera to detect IR LEDs (night vision)")
    print(f"    • Check for unusual WiFi networks")
    print(f"    • Scan for open RTSP ports (554, 8554)")
    
    print(f"\n{C.R}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 6. NETWORK SCANNER ==============
def network_scanner():
    clear()
    print(f"\n{C.Y}{C.BOLD}╔══════════════════════ 🌐 NETWORK SCANNER ══════════════════════╗{C.E}")
    print(f"{C.Y}Scanning local network...{C.E}\n")
    
    # Get gateway
    gw = cmd("ip route | grep default | awk '{print $3}'").strip()
    if not gw:
        print(f"{C.R}Not connected to any network{C.E}")
        pause()
        return
    
    subnet = '.'.join(gw.split('.')[:-1]) + '.0/24'
    print(f"  Gateway: {gw}")
    print(f"  Scanning: {subnet}\n")
    
    # nmap scan
    out = cmd(f"nmap -sn {subnet} 2>/dev/null")
    if 'Nmap scan report' in out:
        devices = []
        current_ip = None
        
        for line in out.split('\n'):
            if 'Nmap scan report for' in line:
                current_ip = line.split()[-1].strip('()')
            elif 'MAC Address:' in line:
                parts = line.split('MAC Address: ')[1]
                mac = parts.split()[0]
                vendor = ' '.join(parts.split()[1:]).strip('()')[:25]
                devices.append({'ip': current_ip, 'mac': mac, 'vendor': vendor})
        
        print(f"  {C.BOLD}Found {len(devices)} devices:{C.E}\n")
        print(f"  {'IP Address':<16} {'MAC Address':<18} {'Vendor'}")
        print(f"  {'-'*16} {'-'*18} {'-'*25}")
        
        for dev in devices:
            print(f"  {dev['ip']:<16} {dev['mac']:<18} {dev['vendor']}")
    else:
        print(f"  {C.Y}nmap not installed. Install: pkg install nmap{C.E}")
        
        # Fallback: ARP table
        print(f"\n  {C.BOLD}ARP Table:{C.E}")
        arp = cmd("ip neigh show")
        print(f"  {arp}")
    
    print(f"\n{C.Y}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 7. GPS LOCATION ==============
def gps_location():
    clear()
    print(f"\n{C.G}{C.BOLD}╔══════════════════════ 📍 GPS LOCATION ══════════════════════╗{C.E}")
    print(f"{C.Y}Getting GPS location...{C.E}\n")
    
    out = cmd("termux-location -p gps 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            print(f"  {C.BOLD}📍 Current Location:{C.E}")
            print(f"     Latitude:  {loc.get('latitude',0):.6f}°")
            print(f"     Longitude: {loc.get('longitude',0):.6f}°")
            print(f"     Altitude:  {loc.get('altitude',0):.1f} m")
            print(f"     Accuracy:  ±{loc.get('accuracy',0):.1f} m")
            print(f"     Speed:     {loc.get('speed',0):.1f} m/s")
            print(f"     Bearing:   {loc.get('bearing',0):.1f}°")
            print(f"     Provider:  {loc.get('provider','?')}")
            
            lat,lon = loc.get('latitude',0),loc.get('longitude',0)
            print(f"\n  {C.BOLD}🗺️ Map Links:{C.E}")
            print(f"     Google Maps: https://maps.google.com/?q={lat},{lon}")
            print(f"     OpenStreetMap: https://www.openstreetmap.org/?mlat={lat}&mlon={lon}")
        except:
            print(f"{C.R}Error parsing location{C.E}")
    else:
        print(f"{C.R}Unable to get GPS. Enable location in settings.{C.E}")
    
    print(f"\n{C.G}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()


# ============== 8. FULL SCAN ==============
def full_scan():
    clear()
    print(f"\n{C.C}{C.BOLD}╔══════════════════════ ⚡ FULL SCAN ══════════════════════╗{C.E}")
    print(f"{C.Y}Running all scanners...{C.E}\n")
    
    results = {'wifi':0,'bt':0,'cell':0,'cameras':0}
    
    # WiFi
    print(f"  {C.G}[1/4]{C.E} Scanning WiFi...")
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    if out:
        try:
            nets = json.loads(out)
            results['wifi'] = len(nets)
            print(f"        Found {C.G}{len(nets)}{C.E} networks")
        except: pass
    
    # Bluetooth
    print(f"  {C.B}[2/4]{C.E} Scanning Bluetooth...")
    out = cmd("termux-bluetooth-scaninfo 2>/dev/null")
    if out:
        try:
            devs = json.loads(out)
            results['bt'] = len(devs)
            print(f"        Found {C.B}{len(devs)}{C.E} devices")
        except: pass
    
    # Cell
    print(f"  {C.M}[3/4]{C.E} Scanning Cell Towers...")
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    if out:
        try:
            cells = json.loads(out)
            results['cell'] = len(cells)
            print(f"        Found {C.M}{len(cells)}{C.E} towers")
        except: pass
    
    # GPS
    print(f"  {C.Y}[4/4]{C.E} Getting GPS...")
    out = cmd("termux-location -p network 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            print(f"        Location: {loc.get('latitude',0):.4f}, {loc.get('longitude',0):.4f}")
        except: pass
    
    # Summary
    print(f"\n  {C.BOLD}━━━━━━━━━━━━━━ SUMMARY ━━━━━━━━━━━━━━{C.E}")
    print(f"  📡 WiFi Networks:     {results['wifi']}")
    print(f"  🔵 Bluetooth Devices: {results['bt']}")
    print(f"  📶 Cell Towers:       {results['cell']}")
    print(f"  {C.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.E}")
    
    print(f"\n{C.C}╚══════════════════════════════════════════════════════════════════════╝{C.E}")
    pause()

# ============== 9. LIVE DASHBOARD ==============
def live_dashboard():
    print(f"\n{C.Y}Starting Live Dashboard...{C.E}")
    print(f"{C.DIM}This will run 8xradar.py{C.E}\n")
    
    # Check if file exists
    if os.path.exists('8xradar.py'):
        os.system('python 8xradar.py')
    elif os.path.exists('ultimate_radar.py'):
        os.system('python ultimate_radar.py')
    else:
        print(f"{C.R}Dashboard files not found!{C.E}")
        print(f"Make sure all files are in the same directory.")
        pause()

# ============== MAIN ==============
def main():
    while True:
        banner()
        main_menu()
        
        choice = input(f"  {C.C}Select option [0-9]: {C.E}").strip()
        
        if choice == '1':
            wifi_scanner()
        elif choice == '2':
            bluetooth_scanner()
        elif choice == '3':
            cell_analyzer()
        elif choice == '4':
            satellite_tracker()
        elif choice == '5':
            camera_detector()
        elif choice == '6':
            network_scanner()
        elif choice == '7':
            gps_location()
        elif choice == '8':
            full_scan()
        elif choice == '9':
            live_dashboard()
        elif choice == '0':
            clear()
            print(f"\n{C.G}  👋 Goodbye! Stay safe.{C.E}\n")
            sys.exit(0)
        else:
            print(f"{C.R}Invalid option!{C.E}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print(f"\n{C.G}  👋 Goodbye!{C.E}\n")
