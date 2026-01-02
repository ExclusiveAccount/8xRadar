#!/usr/bin/env python3
"""
📡 ULTIMATE SIGNAL RADAR - All-in-One
WiFi | Bluetooth | Cell Tower | Camera | IoT | Network Devices
Carrier Aggregation | 5G | Band Analysis | Live Dashboard
"""

import subprocess
import json
import os
import sys
import time
import threading
import math
import re
from datetime import datetime
from collections import defaultdict

# ============== COLORS ==============
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
    BOLD = '\033[1m'; DIM = '\033[2m'; BLINK = '\033[5m'; E = '\033[0m'
    BG_R = '\033[41m'; BG_G = '\033[42m'; BG_Y = '\033[43m'; BG_B = '\033[44m'

# ============== GLOBAL DATA ==============
DATA = {
    'wifi': [], 'bluetooth': [], 'cell': [], 'network': [],
    'cameras': [], 'iot': [], 'printers': [], 'smart_tv': [],
    'gps': None, 'ca_info': None,
    'stats': {'wifi': 0, 'bt': 0, 'cell': 0, 'net': 0, 'cam': 0, 'iot': 0},
    'alerts': [], 'scan_time': None,
}

# ============== DEVICE DATABASES ==============
CAMERA_VENDORS = {
    '00:80:f0': 'Panasonic', '28:57:be': 'Hikvision', '54:c4:15': 'Hikvision',
    'c0:56:e3': 'Hikvision', '44:19:b6': 'Hikvision', 'c4:2f:90': 'Hikvision',
    'e0:50:8b': 'Dahua', '3c:ef:8c': 'Dahua', '90:02:a9': 'Dahua',
    '00:62:6e': 'Dahua', 'a0:bd:1d': 'Dahua', '00:1f:54': 'Lorex',
    '00:40:8c': 'Axis', '00:1a:07': 'Arecont', '00:30:53': 'Basler',
    '7c:dd:90': 'Xiaomi Cam', '78:11:dc': 'Xiaomi Cam', '00:55:da': 'Xiongmai',
    '00:12:41': 'Xiongmai', 'ac:cf:23': 'Hikvision', 'c0:3d:03': 'Hikvision',
}

IOT_VENDORS = {
    # Smart Home
    '18:b4:30': 'Nest', '64:16:66': 'Nest', 'f4:f5:d8': 'Google Home',
    '30:fd:38': 'Google Home', '1c:f2:9a': 'Google Home', 'e4:f0:42': 'Google Home',
    '44:07:0b': 'Google Chromecast', 'd4:73:d7': 'Google Chromecast',
    '68:a4:0e': 'Amazon Echo', '74:c2:46': 'Amazon Echo', 'fc:65:de': 'Amazon Echo',
    '00:fc:8b': 'Amazon Echo', 'a4:08:ea': 'Amazon Echo', '84:d6:d0': 'Amazon Echo',
    'b4:7c:9c': 'Amazon Fire TV', '00:bb:3a': 'Amazon Fire TV',
    # Smart Plugs/Switches
    '5c:cf:7f': 'Tuya/Smart Life', 'd8:f1:5b': 'Tuya/Smart Life',
    '60:01:94': 'Tuya/Smart Life', '68:57:2d': 'Tuya/Smart Life',
    '50:02:91': 'TP-Link Smart', 'b0:be:76': 'TP-Link Smart',
    '98:da:c4': 'TP-Link Smart', '1c:3b:f3': 'TP-Link Smart',
    # Smart Bulbs
    'd0:73:d5': 'Philips Hue', '00:17:88': 'Philips Hue',
    'ec:b5:fa': 'Philips Hue', 'b4:e6:2d': 'Philips Hue',
    # Xiaomi IoT
    '28:6a:ba': 'Xiaomi IoT', '0c:1d:af': 'Xiaomi IoT', '14:f6:5a': 'Xiaomi IoT',
    '78:02:f8': 'Xiaomi IoT', '64:09:80': 'Xiaomi IoT', '04:cf:8c': 'Xiaomi IoT',
    # Smart Locks
    '00:1a:22': 'Yale Lock', 'e0:b9:4d': 'August Lock',
    # Robot Vacuums
    '50:ec:50': 'iRobot Roomba', '80:c5:f2': 'iRobot Roomba',
    '74:f6:1c': 'Roborock', '70:9c:d1': 'Roborock',
}

SMART_TV_VENDORS = {
    '00:09:df': 'LG TV', '00:1c:62': 'LG TV', '00:1e:75': 'LG TV',
    '00:22:a9': 'LG TV', '00:24:83': 'LG TV', '00:26:e8': 'LG TV',
    '00:34:da': 'LG TV', '00:e0:91': 'LG TV', '10:68:3f': 'LG TV',
    '00:07:a6': 'Samsung TV', '00:09:18': 'Samsung TV', '00:0d:ae': 'Samsung TV',
    '00:12:47': 'Samsung TV', '00:13:77': 'Samsung TV', '00:15:b9': 'Samsung TV',
    '00:16:32': 'Samsung TV', '00:17:c9': 'Samsung TV', '00:18:af': 'Samsung TV',
    '00:1a:8a': 'Samsung TV', '00:1b:98': 'Samsung TV', '00:1c:43': 'Samsung TV',
    '00:1d:25': 'Samsung TV', '00:1d:f6': 'Samsung TV', '00:1e:7d': 'Samsung TV',
    '00:1f:cc': 'Samsung TV', '00:21:19': 'Samsung TV', '00:21:4c': 'Samsung TV',
    '00:e0:4c': 'Realtek (Smart TV)', '00:1a:79': 'TCL TV',
    '00:04:4b': 'Sony TV', '00:0a:d9': 'Sony TV', '00:0e:07': 'Sony TV',
    '00:12:ee': 'Sony TV', '00:13:a9': 'Sony TV', '00:15:c1': 'Sony TV',
    '00:16:20': 'Sony TV', '00:18:13': 'Sony TV', '00:19:c5': 'Sony TV',
    '00:1a:80': 'Sony TV', '00:1d:ba': 'Sony TV', '00:1e:a4': 'Sony TV',
    '28:d2:44': 'TCL/Roku TV', '00:0d:4b': 'Roku', 'b8:3e:59': 'Roku',
    'b0:a7:37': 'Roku', 'ac:3a:7a': 'Roku', 'd8:31:34': 'Roku',
    '00:8e:f2': 'MI TV', '64:cc:2e': 'MI TV', '98:fa:e3': 'MI TV',
}

PRINTER_VENDORS = {
    '00:00:48': 'HP Printer', '00:01:e6': 'HP Printer', '00:02:a5': 'HP Printer',
    '00:0b:cd': 'HP Printer', '00:0d:9d': 'HP Printer', '00:0e:7f': 'HP Printer',
    '00:0f:61': 'HP Printer', '00:10:83': 'HP Printer', '00:11:0a': 'HP Printer',
    '00:12:79': 'HP Printer', '00:13:21': 'HP Printer', '00:14:38': 'HP Printer',
    '00:15:60': 'HP Printer', '00:16:35': 'HP Printer', '00:17:08': 'HP Printer',
    '00:18:fe': 'HP Printer', '00:19:bb': 'HP Printer', '00:1a:4b': 'HP Printer',
    '00:00:85': 'Canon Printer', '00:00:f0': 'Canon Printer', '00:1e:8f': 'Canon Printer',
    '18:0c:ac': 'Canon Printer', '3c:a9:f4': 'Canon Printer', '54:04:a6': 'Canon Printer',
    '00:00:00': 'Xerox Printer', '00:00:01': 'Xerox Printer', '00:00:aa': 'Xerox Printer',
    '00:00:48': 'Epson Printer', '00:1b:a9': 'Brother Printer', '00:80:77': 'Brother Printer',
}

PHONE_VENDORS = {
    # Apple
    '00:03:93': 'Apple', '00:0a:95': 'Apple', '00:0d:93': 'Apple',
    '00:11:24': 'Apple', '00:14:51': 'Apple', '00:16:cb': 'Apple',
    '00:17:f2': 'Apple', '00:19:e3': 'Apple', '00:1b:63': 'Apple',
    '00:1c:b3': 'Apple', '00:1d:4f': 'Apple', '00:1e:52': 'Apple',
    '00:1f:5b': 'Apple', '00:1f:f3': 'Apple', '00:21:e9': 'Apple',
    # Samsung
    '00:12:fb': 'Samsung', '00:13:77': 'Samsung', '00:15:99': 'Samsung',
    '00:16:32': 'Samsung', '00:17:d5': 'Samsung', '00:18:af': 'Samsung',
    '00:1a:8a': 'Samsung', '00:1b:98': 'Samsung', '00:1c:43': 'Samsung',
    '9c:02:98': 'Samsung', '9c:3a:af': 'Samsung', '9c:65:b0': 'Samsung',
    # Xiaomi
    '28:6a:ba': 'Xiaomi', '0c:1d:af': 'Xiaomi', '14:f6:5a': 'Xiaomi',
    '18:59:36': 'Xiaomi', '20:82:c0': 'Xiaomi', '34:80:b3': 'Xiaomi',
    '64:b4:73': 'Xiaomi', '78:02:f8': 'Xiaomi', '98:fa:e3': 'Xiaomi',
    # OnePlus
    '2c:33:61': 'OnePlus', '64:a2:f9': 'OnePlus', '94:65:2d': 'OnePlus',
    # Realme/Oppo
    '3c:cd:5d': 'Realme/Oppo', '48:db:50': 'Realme/Oppo', '5c:4c:a9': 'Realme/Oppo',
    '74:04:2b': 'Realme/Oppo', '90:17:ac': 'Realme/Oppo', 'a4:3b:fa': 'Realme/Oppo',
    # Vivo
    '00:27:15': 'Vivo', '3c:b6:b7': 'Vivo', '58:3f:54': 'Vivo',
}

# ============== INDIA OPERATORS ==============
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

# ============== LTE BANDS ==============
LTE_BANDS = {
    1: "B1 (2100)", 3: "B3 (1800)", 5: "B5 (850)", 8: "B8 (900)",
    40: "B40 (2300 TDD)", 41: "B41 (2500 TDD)",
}

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=20)
        return r.stdout + r.stderr
    except:
        return ""

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


# ============== HELPER FUNCTIONS ==============
def get_vendor(mac):
    """Get vendor from MAC prefix"""
    if not mac: return None
    prefix = mac.lower().replace('-', ':')[:8]
    
    # Check all databases
    for db in [CAMERA_VENDORS, IOT_VENDORS, SMART_TV_VENDORS, PRINTER_VENDORS, PHONE_VENDORS]:
        if prefix in db:
            return db[prefix]
    return None

def classify_device(mac, name="", ssid=""):
    """Classify device type from MAC and name"""
    prefix = mac.lower().replace('-', ':')[:8] if mac else ""
    name_lower = (name or "").lower()
    ssid_lower = (ssid or "").lower()
    
    # Camera detection
    if prefix in CAMERA_VENDORS:
        return ("📷", "Camera", CAMERA_VENDORS[prefix], "HIGH")
    if any(x in name_lower or x in ssid_lower for x in ['cam', 'ipcam', 'camera', 'dvr', 'nvr', 'cctv', 'hikvision', 'dahua']):
        return ("📷", "Camera", "Suspected", "MEDIUM")
    
    # IoT detection
    if prefix in IOT_VENDORS:
        return ("🏠", "IoT", IOT_VENDORS[prefix], "LOW")
    if any(x in name_lower for x in ['nest', 'echo', 'alexa', 'google home', 'smart', 'tuya', 'hue']):
        return ("🏠", "IoT", "Smart Home", "LOW")
    
    # Smart TV
    if prefix in SMART_TV_VENDORS:
        return ("📺", "Smart TV", SMART_TV_VENDORS[prefix], "LOW")
    if any(x in name_lower or x in ssid_lower for x in ['tv', 'roku', 'fire tv', 'chromecast', 'android tv']):
        return ("📺", "Smart TV", "Detected", "LOW")
    
    # Printer
    if prefix in PRINTER_VENDORS:
        return ("🖨️", "Printer", PRINTER_VENDORS[prefix], "LOW")
    if any(x in name_lower or x in ssid_lower for x in ['printer', 'print', 'hp ', 'canon', 'epson', 'brother']):
        return ("🖨️", "Printer", "Detected", "LOW")
    
    # Phone
    if prefix in PHONE_VENDORS:
        return ("📱", "Phone", PHONE_VENDORS[prefix], "LOW")
    if any(x in name_lower for x in ['iphone', 'samsung', 'xiaomi', 'oneplus', 'redmi', 'realme', 'oppo', 'vivo', 'phone']):
        return ("📱", "Phone", "Mobile", "LOW")
    
    # Audio
    if any(x in name_lower for x in ['airpod', 'buds', 'earphone', 'headphone', 'jbl', 'speaker', 'soundbar']):
        return ("🎧", "Audio", "Detected", "LOW")
    
    # Wearable
    if any(x in name_lower for x in ['band', 'watch', 'fit', 'amazfit', 'mi band']):
        return ("⌚", "Wearable", "Detected", "LOW")
    
    # Laptop
    if any(x in name_lower for x in ['laptop', 'macbook', 'thinkpad', 'dell', 'hp pavilion']):
        return ("💻", "Laptop", "Detected", "LOW")
    
    # Router
    if any(x in name_lower or x in ssid_lower for x in ['router', 'gateway', 'ap-', 'access point']):
        return ("📡", "Router", "Detected", "LOW")
    
    # WiFi Direct devices
    if 'direct-' in ssid_lower:
        return ("📲", "WiFi Direct", "Detected", "LOW")
    
    return ("📟", "Unknown", "Device", "LOW")

def signal_bar(rssi, width=5):
    """Generate signal strength bar"""
    if rssi is None: return f"{C.DIM}{'░'*width}{C.E}"
    
    if rssi > -50: filled = width; color = C.G
    elif rssi > -60: filled = 4; color = C.G
    elif rssi > -70: filled = 3; color = C.Y
    elif rssi > -80: filled = 2; color = C.Y
    elif rssi > -90: filled = 1; color = C.R
    else: filled = 1; color = C.R
    
    return f"{color}{'█'*filled}{C.DIM}{'░'*(width-filled)}{C.E}"

def security_icon(sec):
    """Get security icon"""
    if not sec: return f"{C.R}🔓 OPEN{C.E}"
    sec = sec.upper()
    if 'WPA3' in sec: return f"{C.G}🔒 WPA3{C.E}"
    if 'WPA2' in sec: return f"{C.G}🔐 WPA2{C.E}"
    if 'WPA' in sec: return f"{C.Y}🔑 WPA{C.E}"
    if 'WEP' in sec: return f"{C.R}⚠️ WEP{C.E}"
    return f"{C.R}🔓 OPEN{C.E}"

def earfcn_to_band(earfcn):
    """Convert EARFCN to band"""
    if 0 <= earfcn <= 599: return 1
    if 1200 <= earfcn <= 1949: return 3
    if 2400 <= earfcn <= 2649: return 5
    if 3450 <= earfcn <= 3799: return 8
    if 38650 <= earfcn <= 39649: return 40
    if 39650 <= earfcn <= 41589: return 41
    return None


# ============== SCANNERS ==============
def scan_wifi():
    """Scan WiFi networks"""
    out = cmd("termux-wifi-scaninfo 2>/dev/null")
    networks = []
    cameras = []
    iot_devices = []
    
    if out:
        try:
            raw = json.loads(out)
            for net in raw:
                ssid = net.get('ssid', '')
                bssid = net.get('bssid', '')
                rssi = net.get('rssi', -100)
                sec = net.get('capabilities', '')
                freq = net.get('frequency', 0)
                
                # Classify
                icon, dtype, vendor, risk = classify_device(bssid, ssid, ssid)
                
                network = {
                    'ssid': ssid or '[Hidden]',
                    'bssid': bssid,
                    'rssi': rssi,
                    'security': sec,
                    'frequency': freq,
                    'channel': (freq - 2412) // 5 + 1 if 2412 <= freq <= 2484 else (freq - 5170) // 5 + 34 if freq > 5000 else 0,
                    'band': '2.4G' if freq < 5000 else '5G',
                    'vendor': vendor,
                    'type': dtype,
                    'icon': icon,
                    'risk': risk,
                }
                networks.append(network)
                
                # Separate cameras and IoT
                if dtype == "Camera":
                    cameras.append(network)
                elif dtype in ["IoT", "Smart TV"]:
                    iot_devices.append(network)
            
            networks.sort(key=lambda x: x['rssi'], reverse=True)
        except:
            pass
    
    DATA['wifi'] = networks
    DATA['cameras'].extend(cameras)
    DATA['iot'].extend(iot_devices)
    DATA['stats']['wifi'] = len(networks)
    DATA['stats']['cam'] = len(DATA['cameras'])
    DATA['stats']['iot'] = len(DATA['iot'])

def scan_bluetooth():
    """Scan Bluetooth devices"""
    out = cmd("termux-bluetooth-scaninfo 2>/dev/null")
    devices = []
    
    if out:
        try:
            raw = json.loads(out)
            for dev in raw:
                name = dev.get('name', 'Unknown')
                mac = dev.get('address', '')
                rssi = dev.get('rssi', -100)
                
                icon, dtype, vendor, risk = classify_device(mac, name)
                
                device = {
                    'name': name,
                    'mac': mac,
                    'rssi': rssi,
                    'type': dtype,
                    'vendor': vendor,
                    'icon': icon,
                    'risk': risk,
                }
                devices.append(device)
            
            devices.sort(key=lambda x: x['rssi'], reverse=True)
        except:
            pass
    
    DATA['bluetooth'] = devices
    DATA['stats']['bt'] = len(devices)

def calc_ta_distance(ta, network='LTE'):
    """Calculate distance from Timing Advance"""
    if ta is None or ta < 0: return None
    if network == 'LTE': return ta * 78.12  # meters
    if network == 'GSM': return ta * 550
    return None

def calc_enb_id(ci):
    """Calculate eNodeB ID from Cell ID"""
    if ci is None: return None, None
    enb_id = ci // 256
    sector = ci % 256
    return enb_id, sector

def get_bandwidth(earfcn, band):
    """Estimate bandwidth from band (typical India deployments)"""
    bw_map = {1: 10, 3: 20, 5: 10, 8: 10, 40: 20, 41: 20}
    return bw_map.get(band, 10)

def scan_cell():
    """Scan Cell Towers with full details - TA, Distance, eNB, RSRQ, SNR, BW"""
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    cells = []
    ca_info = {'active': False, 'type': None, 'bands': [], 'pcell': None, 'scells': [], 'total_bw': 0}
    
    if out:
        try:
            raw = json.loads(out)
            lte_cells = []
            nr_cells = []
            
            for cell in raw:
                ctype = cell.get('type', '').lower()
                registered = cell.get('registered', False)
                
                if 'lte' in ctype:
                    mcc = cell.get('mcc', 0)
                    mnc = cell.get('mnc', 0)
                    earfcn = cell.get('earfcn', 0)
                    band = earfcn_to_band(earfcn)
                    ci = cell.get('ci')
                    ta = cell.get('timingAdvance')
                    
                    # Calculate eNodeB ID and Sector
                    enb_id, sector = calc_enb_id(ci)
                    
                    # Calculate distance from TA
                    distance = calc_ta_distance(ta, 'LTE')
                    
                    # Get bandwidth
                    bandwidth = cell.get('bandwidth') or get_bandwidth(earfcn, band)
                    
                    cell_info = {
                        'type': '4G LTE',
                        'registered': registered,
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'tac': cell.get('tac'),
                        'ci': ci,
                        'enb_id': enb_id,
                        'sector': sector,
                        'pci': cell.get('pci'),
                        'earfcn': earfcn,
                        'band': band,
                        'band_name': LTE_BANDS.get(band, f"B{band}") if band else "Unknown",
                        'bandwidth': bandwidth,
                        'rsrp': cell.get('rsrp'),
                        'rsrq': cell.get('rsrq'),
                        'rssi': cell.get('rssi'),
                        'sinr': cell.get('rssnr') or cell.get('sinr'),
                        'cqi': cell.get('cqi'),
                        'ta': ta,
                        'distance_m': distance,
                    }
                    cells.append(cell_info)
                    lte_cells.append(cell_info)
                    
                    if registered:
                        ca_info['pcell'] = cell_info
                    else:
                        ca_info['scells'].append(cell_info)
                
                elif 'nr' in ctype or '5g' in ctype:
                    mcc = cell.get('mcc', 0)
                    mnc = cell.get('mnc', 0)
                    nci = cell.get('nci')
                    
                    # gNodeB ID
                    gnb_id = nci // 4096 if nci else None
                    sector = nci % 4096 if nci else None
                    
                    cell_info = {
                        'type': '5G NR',
                        'registered': registered,
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'tac': cell.get('tac'),
                        'nci': nci,
                        'gnb_id': gnb_id,
                        'sector': sector,
                        'pci': cell.get('pci'),
                        'nrarfcn': cell.get('nrarfcn'),
                        'bandwidth': 100,  # Typical 5G BW
                        'ss_rsrp': cell.get('ssRsrp') or cell.get('csiRsrp'),
                        'ss_rsrq': cell.get('ssRsrq') or cell.get('csiRsrq'),
                        'ss_sinr': cell.get('ssSinr') or cell.get('csiSinr'),
                    }
                    cells.append(cell_info)
                    nr_cells.append(cell_info)
                
                elif 'gsm' in ctype:
                    mcc = cell.get('mcc', 0)
                    mnc = cell.get('mnc', 0)
                    ta = cell.get('timingAdvance')
                    distance = calc_ta_distance(ta, 'GSM')
                    
                    cell_info = {
                        'type': '2G GSM',
                        'registered': registered,
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'lac': cell.get('lac'),
                        'cid': cell.get('cid'),
                        'arfcn': cell.get('arfcn'),
                        'bsic': cell.get('bsic'),
                        'rssi': cell.get('rssi'),
                        'ta': ta,
                        'distance_m': distance,
                    }
                    cells.append(cell_info)
                
                elif 'wcdma' in ctype or 'umts' in ctype:
                    mcc = cell.get('mcc', 0)
                    mnc = cell.get('mnc', 0)
                    cid = cell.get('cid')
                    rnc = cid // 65536 if cid else None
                    
                    cell_info = {
                        'type': '3G WCDMA',
                        'registered': registered,
                        'mcc': mcc, 'mnc': mnc,
                        'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                        'lac': cell.get('lac'),
                        'cid': cid,
                        'rnc': rnc,
                        'psc': cell.get('psc'),
                        'uarfcn': cell.get('uarfcn'),
                        'rscp': cell.get('rscp'),
                        'ecno': cell.get('ecno'),
                    }
                    cells.append(cell_info)
            
            # Detect CA
            total_carriers = len(lte_cells) + len(nr_cells)
            if total_carriers >= 2:
                ca_info['active'] = True
                if total_carriers == 2: ca_info['type'] = '2CC'
                elif total_carriers == 3: ca_info['type'] = '3CC'
                elif total_carriers == 4: ca_info['type'] = '4CC'
                else: ca_info['type'] = f'{total_carriers}CC'
            
            # Collect bands and total bandwidth
            total_bw = 0
            for c in lte_cells:
                if c.get('band'):
                    ca_info['bands'].append(f"B{c['band']}")
                total_bw += c.get('bandwidth', 0)
            for c in nr_cells:
                ca_info['bands'].append("n78")
                total_bw += c.get('bandwidth', 0)
            
            ca_info['total_bw'] = total_bw
            
            if nr_cells and lte_cells:
                ca_info['mode'] = 'NSA'
            elif nr_cells:
                ca_info['mode'] = 'SA'
            else:
                ca_info['mode'] = 'LTE'
                
        except:
            pass
    
    DATA['cell'] = cells
    DATA['ca_info'] = ca_info
    DATA['stats']['cell'] = len(cells)

def scan_network():
    """Scan network for connected devices"""
    devices = []
    
    gw = cmd("ip route | grep default | awk '{print $3}'").strip()
    if not gw:
        DATA['network'] = []
        DATA['stats']['net'] = 0
        return
    
    subnet = '.'.join(gw.split('.')[:-1]) + '.0/24'
    
    # Quick nmap scan
    out = cmd(f"nmap -sn {subnet} 2>/dev/null")
    if out:
        current_ip = None
        current_mac = None
        
        for line in out.split('\n'):
            if 'Nmap scan report for' in line:
                parts = line.split()
                current_ip = parts[-1].strip('()')
            elif 'MAC Address:' in line:
                parts = line.split('MAC Address: ')[1]
                current_mac = parts.split()[0]
                vendor_raw = ' '.join(parts.split()[1:]).strip('()')
                
                icon, dtype, vendor, risk = classify_device(current_mac)
                
                devices.append({
                    'ip': current_ip,
                    'mac': current_mac,
                    'vendor': vendor or vendor_raw[:20],
                    'type': dtype,
                    'icon': icon,
                    'risk': risk,
                })
    
    DATA['network'] = devices
    DATA['stats']['net'] = len(devices)

def scan_gps():
    """Get GPS location"""
    out = cmd("termux-location -p network 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            DATA['gps'] = {
                'lat': loc.get('latitude'),
                'lon': loc.get('longitude'),
                'accuracy': loc.get('accuracy'),
            }
        except:
            pass


# ============== DISPLAY FUNCTIONS ==============
def render_header():
    """Render dashboard header"""
    now = datetime.now().strftime("%H:%M:%S")
    
    print(f"""
{C.C}{C.BOLD}╔════════════════════════════════════════════════════════════════════════════╗
║              📡 ULTIMATE SIGNAL RADAR - All-in-One Scanner                 ║
╠════════════════════════════════════════════════════════════════════════════╣{C.E}
{C.DIM}║  {now}  │  WiFi: {DATA['stats']['wifi']:>2}  │  BT: {DATA['stats']['bt']:>2}  │  Cell: {DATA['stats']['cell']}  │  Net: {DATA['stats']['net']:>2}  │  Cam: {DATA['stats']['cam']}  │  IoT: {DATA['stats']['iot']}  ║{C.E}
{C.C}╚════════════════════════════════════════════════════════════════════════════╝{C.E}
""")

def render_cell_section():
    """Render Cell Tower & CA section"""
    ca = DATA.get('ca_info', {})
    cells = DATA.get('cell', [])
    
    # CA Status
    if ca.get('active'):
        ca_color = C.G
        ca_status = f"{C.G}{C.BOLD}✓ ACTIVE{C.E}"
    else:
        ca_color = C.DIM
        ca_status = f"{C.DIM}Inactive{C.E}"
    
    print(f"""{C.M}{C.BOLD}┌──────────────────────── 📶 CELL TOWERS & CARRIER AGGREGATION ────────────────────────┐{C.E}""")
    
    # CA Info
    if ca.get('active'):
        bands_str = ' + '.join(ca.get('bands', []))
        print(f"│  {C.G}⚡ CA: {ca.get('type', 'N/A')}{C.E}  │  Mode: {ca.get('mode', 'N/A')}  │  Bands: {C.C}{bands_str}{C.E}")
    else:
        print(f"│  CA: {ca_status}")
    
    print(f"│")
    
    # Cell list
    if cells:
        print(f"│  {'Type':<8} {'Operator':<10} {'Band':<15} {'Signal':^12} {'PCI':>5} {'Status':<10}")
        print(f"│  {'-'*8} {'-'*10} {'-'*15} {'-'*12} {'-'*5} {'-'*10}")
        
        for cell in cells[:5]:
            ctype = cell.get('type', '?')[:8]
            op = cell.get('operator', '?')[:10]
            
            if '5G' in ctype:
                band = 'n78 (3500)'
                rsrp = cell.get('ss_rsrp')
            elif 'LTE' in ctype:
                band = cell.get('band_name', '?')[:15]
                rsrp = cell.get('rsrp')
            else:
                band = 'GSM'
                rsrp = cell.get('rssi')
            
            bar = signal_bar(rsrp)
            rsrp_str = f"{rsrp} dBm" if rsrp else "N/A"
            pci = cell.get('pci', cell.get('cid', '?'))
            status = f"{C.G}●Connected{C.E}" if cell.get('registered') else f"{C.DIM}○Neighbor{C.E}"
            
            print(f"│  {ctype:<8} {op:<10} {band:<15} {bar} {rsrp_str:>6} {str(pci):>5} {status}")
    else:
        print(f"│  {C.DIM}No cell data - Install Termux:API{C.E}")
    
    print(f"{C.M}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_wifi_section():
    """Render WiFi section"""
    networks = DATA.get('wifi', [])
    
    print(f"""{C.G}{C.BOLD}┌──────────────────────────────────── 📡 WiFi NETWORKS ─────────────────────────────────┐{C.E}""")
    
    if networks:
        print(f"│  {'SSID':<24} {'Signal':^10} {'Security':<12} {'Ch':>3} {'Band':>4} {'Type':<10}")
        print(f"│  {'-'*24} {'-'*10} {'-'*12} {'-'*3} {'-'*4} {'-'*10}")
        
        for net in networks[:8]:
            ssid = net.get('ssid', '?')[:23]
            rssi = net.get('rssi')
            bar = signal_bar(rssi)
            sec = security_icon(net.get('security', ''))
            ch = net.get('channel', 0)
            band = net.get('band', '?')
            dtype = f"{net.get('icon', '?')} {net.get('type', '?')}"[:10]
            
            print(f"│  {ssid:<24} {bar} {rssi:>3}  {sec:<12} {ch:>3} {band:>4} {dtype}")
    else:
        print(f"│  {C.DIM}No WiFi data{C.E}")
    
    print(f"{C.G}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_bluetooth_section():
    """Render Bluetooth section"""
    devices = DATA.get('bluetooth', [])
    
    print(f"""{C.B}{C.BOLD}┌──────────────────────────────────── 🔵 BLUETOOTH ─────────────────────────────────────┐{C.E}""")
    
    if devices:
        print(f"│  {'Name':<28} {'Signal':^10} {'Type':<15} {'Vendor':<15}")
        print(f"│  {'-'*28} {'-'*10} {'-'*15} {'-'*15}")
        
        for dev in devices[:6]:
            name = dev.get('name', '?')[:27]
            rssi = dev.get('rssi')
            bar = signal_bar(rssi)
            dtype = f"{dev.get('icon', '?')} {dev.get('type', '?')}"[:15]
            vendor = dev.get('vendor', '?')[:15]
            
            print(f"│  {name:<28} {bar} {rssi:>3}  {dtype:<15} {vendor}")
    else:
        print(f"│  {C.DIM}No Bluetooth devices{C.E}")
    
    print(f"{C.B}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_devices_section():
    """Render Network Devices, Cameras, IoT"""
    network = DATA.get('network', [])
    cameras = DATA.get('cameras', [])
    iot = DATA.get('iot', [])
    
    print(f"""{C.Y}{C.BOLD}┌──────────────────────────────── 🌐 NETWORK DEVICES ───────────────────────────────────┐{C.E}""")
    
    if network:
        # Group by type
        by_type = defaultdict(list)
        for dev in network:
            by_type[dev.get('type', 'Unknown')].append(dev)
        
        for dtype, devs in by_type.items():
            icon = devs[0].get('icon', '📟') if devs else '📟'
            print(f"│  {icon} {dtype}: {len(devs)}")
            for dev in devs[:3]:
                print(f"│     └─ {dev.get('ip', '?'):<15} {dev.get('mac', '?'):<18} {dev.get('vendor', '?')[:20]}")
    else:
        print(f"│  {C.DIM}No network devices{C.E}")
    
    print(f"{C.Y}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")
    
    # Cameras Alert
    if cameras:
        print(f"""{C.R}{C.BOLD}┌──────────────────────────────── 📷 CAMERAS DETECTED ──────────────────────────────────┐{C.E}""")
        for cam in cameras[:5]:
            risk_color = C.R if cam.get('risk') == 'HIGH' else C.Y
            print(f"│  {risk_color}⚠️  {cam.get('ssid', '?'):<25} {cam.get('bssid', '?'):<18} {cam.get('vendor', '?')}{C.E}")
        print(f"{C.R}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")
    
    # IoT Devices
    if iot:
        print(f"""{C.C}{C.BOLD}┌──────────────────────────────── 🏠 IoT DEVICES ───────────────────────────────────────┐{C.E}""")
        for device in iot[:5]:
            print(f"│  {device.get('icon', '?')} {device.get('ssid', device.get('name', '?')):<25} {device.get('vendor', '?')}")
        print(f"{C.C}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")

def render_alerts():
    """Render security alerts"""
    alerts = []
    
    # Check for open WiFi
    open_wifi = [n for n in DATA.get('wifi', []) if not n.get('security') or 'WPA' not in n.get('security', '').upper()]
    if open_wifi:
        alerts.append(f"{C.R}⚠️  {len(open_wifi)} Open/Weak WiFi networks!{C.E}")
    
    # Check for WEP
    wep_wifi = [n for n in DATA.get('wifi', []) if 'WEP' in n.get('security', '').upper()]
    if wep_wifi:
        alerts.append(f"{C.R}⚠️  {len(wep_wifi)} WEP networks (vulnerable)!{C.E}")
    
    # Cameras
    if DATA.get('cameras'):
        alerts.append(f"{C.R}📷 {len(DATA['cameras'])} potential cameras detected!{C.E}")
    
    # Strong signals
    strong = [n for n in DATA.get('wifi', []) if n.get('rssi', -100) > -40]
    if strong:
        alerts.append(f"{C.Y}📶 {len(strong)} very strong signals nearby{C.E}")
    
    if alerts:
        print(f"""{C.R}{C.BOLD}┌──────────────────────────────── ⚠️  SECURITY ALERTS ──────────────────────────────────┐{C.E}""")
        for alert in alerts:
            print(f"│  {alert}")
        print(f"{C.R}└───────────────────────────────────────────────────────────────────────────────────────┘{C.E}")


# ============== MAIN LOOP ==============
def background_scanner():
    """Background scanning thread"""
    while True:
        try:
            threads = [
                threading.Thread(target=scan_wifi),
                threading.Thread(target=scan_bluetooth),
                threading.Thread(target=scan_cell),
            ]
            
            for t in threads:
                t.daemon = True
                t.start()
            
            for t in threads:
                t.join(timeout=15)
            
            # Network scan less frequently
            if int(time.time()) % 3 == 0:
                scan_network()
            
            DATA['scan_time'] = datetime.now().isoformat()
            time.sleep(5)
        except:
            time.sleep(5)

def render_dashboard():
    """Render full dashboard"""
    clear()
    render_header()
    render_cell_section()
    print()
    render_wifi_section()
    print()
    render_bluetooth_section()
    print()
    render_devices_section()
    print()
    render_alerts()
    print(f"\n{C.DIM}  Auto-refreshing every 3s... Press Ctrl+C to exit{C.E}")

def main():
    """Main entry point"""
    clear()
    print(f"""
{C.C}{C.BOLD}
    ╔═══════════════════════════════════════════════════════╗
    ║         📡 ULTIMATE SIGNAL RADAR                      ║
    ║         All-in-One Signal Intelligence                ║
    ╠═══════════════════════════════════════════════════════╣
    ║  WiFi Networks    │  Bluetooth Devices                ║
    ║  Cell Towers      │  Carrier Aggregation              ║
    ║  Hidden Cameras   │  IoT Devices                      ║
    ║  Smart TVs        │  Printers                         ║
    ║  Network Devices  │  Security Alerts                  ║
    ╚═══════════════════════════════════════════════════════╝
{C.E}""")
    
    print(f"  {C.Y}Initializing scanners...{C.E}")
    
    # Initial scans
    print(f"  {C.DIM}[1/5] WiFi...{C.E}")
    scan_wifi()
    print(f"  {C.DIM}[2/5] Bluetooth...{C.E}")
    scan_bluetooth()
    print(f"  {C.DIM}[3/5] Cell Towers...{C.E}")
    scan_cell()
    print(f"  {C.DIM}[4/5] Network...{C.E}")
    scan_network()
    print(f"  {C.DIM}[5/5] GPS...{C.E}")
    scan_gps()
    
    print(f"\n  {C.G}✓ Ready! Starting live dashboard...{C.E}")
    time.sleep(1)
    
    # Start background scanner
    scanner = threading.Thread(target=background_scanner)
    scanner.daemon = True
    scanner.start()
    
    # Main display loop
    try:
        while True:
            render_dashboard()
            time.sleep(3)
    except KeyboardInterrupt:
        clear()
        print(f"\n{C.G}  👋 Ultimate Signal Radar stopped.{C.E}\n")
        
        # Summary
        print(f"  {C.BOLD}Final Summary:{C.E}")
        print(f"    📡 WiFi Networks: {DATA['stats']['wifi']}")
        print(f"    🔵 Bluetooth: {DATA['stats']['bt']}")
        print(f"    📶 Cell Towers: {DATA['stats']['cell']}")
        print(f"    🌐 Network Devices: {DATA['stats']['net']}")
        print(f"    📷 Cameras: {DATA['stats']['cam']}")
        print(f"    🏠 IoT Devices: {DATA['stats']['iot']}")
        
        # CA Info
        ca = DATA.get('ca_info', {})
        if ca.get('active'):
            print(f"\n  {C.BOLD}Carrier Aggregation:{C.E}")
            print(f"    Type: {ca.get('type')}")
            print(f"    Bands: {' + '.join(ca.get('bands', []))}")
            print(f"    Mode: {ca.get('mode')}")
        
        # Export
        export = input(f"\n  {C.Y}Export all data to JSON? (y/n): {C.E}").strip().lower()
        if export == 'y':
            filename = f"signal_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'wifi': DATA['wifi'],
                'bluetooth': DATA['bluetooth'],
                'cell': DATA['cell'],
                'network': DATA['network'],
                'cameras': DATA['cameras'],
                'iot': DATA['iot'],
                'ca_info': DATA['ca_info'],
                'gps': DATA['gps'],
                'stats': DATA['stats'],
            }
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"  {C.G}✓ Saved to {filename}{C.E}\n")

if __name__ == "__main__":
    main()
