#!/usr/bin/env python3
"""
📡 SIGNAL RADAR - Termux Signal Intelligence Toolkit
All-in-one scanner for WiFi, Bluetooth, Cell, Devices
"""

import subprocess
import json
import re
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Colors for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def banner():
    print(f"""{Colors.CYAN}
    ╔═══════════════════════════════════════════╗
    ║     📡 SIGNAL RADAR v1.0                  ║
    ║     Termux Signal Intelligence            ║
    ╠═══════════════════════════════════════════╣
    ║  [1] WiFi Scan      [5] Cell Tower        ║
    ║  [2] Bluetooth      [6] Connected Devices ║
    ║  [3] Network Radar  [7] Camera Detect     ║
    ║  [4] Full Scan      [8] Export Data       ║
    ║  [0] Exit                                 ║
    ╚═══════════════════════════════════════════╝
    {Colors.END}""")

def run_cmd(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except:
        return ""

def check_root():
    """Check if running as root"""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

# ============== WiFi Scanner ==============
def scan_wifi():
    """Scan WiFi networks using termux-wifi-scaninfo"""
    print(f"\n{Colors.CYAN}[📡] Scanning WiFi Networks...{Colors.END}\n")
    
    # Method 1: Termux API
    output = run_cmd("termux-wifi-scaninfo 2>/dev/null")
    
    if output and "error" not in output.lower():
        try:
            networks = json.loads(output)
            print(f"{Colors.GREEN}Found {len(networks)} networks:{Colors.END}\n")
            print(f"{'SSID':<25} {'BSSID':<18} {'Signal':<8} {'Security':<15} {'Channel'}")
            print("="*80)
            
            for net in sorted(networks, key=lambda x: x.get('rssi', -100), reverse=True):
                ssid = net.get('ssid', 'Hidden')[:24]
                bssid = net.get('bssid', 'Unknown')
                rssi = net.get('rssi', 0)
                security = net.get('capabilities', 'Unknown')[:14]
                freq = net.get('frequency', 0)
                channel = freq_to_channel(freq)
                
                # Color based on signal
                if rssi > -50:
                    sig_color = Colors.GREEN
                elif rssi > -70:
                    sig_color = Colors.YELLOW
                else:
                    sig_color = Colors.RED
                
                # Security warning
                if 'WEP' in security or 'Open' in security or not security:
                    sec_color = Colors.RED
                else:
                    sec_color = Colors.GREEN
                
                print(f"{ssid:<25} {bssid:<18} {sig_color}{rssi:>4} dBm{Colors.END}  {sec_color}{security:<15}{Colors.END} {channel}")
                
                # Vendor lookup
                vendor = get_vendor(bssid)
                if vendor:
                    print(f"  └─ Vendor: {Colors.BLUE}{vendor}{Colors.END}")
            
            return networks
        except json.JSONDecodeError:
            pass
    
    # Method 2: iwlist (root)
    output = run_cmd("iwlist wlan0 scan 2>/dev/null")
    if output:
        parse_iwlist(output)
    else:
        print(f"{Colors.RED}[!] Install Termux:API app and run: pkg install termux-api{Colors.END}")
    
    return []

def freq_to_channel(freq):
    """Convert frequency to channel number"""
    if freq >= 2412 and freq <= 2484:
        return (freq - 2412) // 5 + 1
    elif freq >= 5170 and freq <= 5825:
        return (freq - 5170) // 5 + 34
    return 0

# ============== Bluetooth Scanner ==============
def scan_bluetooth():
    """Scan Bluetooth devices"""
    print(f"\n{Colors.BLUE}[🔵] Scanning Bluetooth Devices...{Colors.END}\n")
    
    # Method 1: Termux API
    output = run_cmd("termux-bluetooth-scaninfo 2>/dev/null")
    
    if output and "error" not in output.lower():
        try:
            devices = json.loads(output)
            print(f"{Colors.GREEN}Found {len(devices)} devices:{Colors.END}\n")
            print(f"{'Name':<30} {'MAC':<18} {'RSSI':<8} {'Type'}")
            print("="*70)
            
            for dev in devices:
                name = dev.get('name', 'Unknown')[:29]
                mac = dev.get('address', 'Unknown')
                rssi = dev.get('rssi', 0)
                dev_type = classify_bt_device(name, mac)
                
                print(f"{name:<30} {mac:<18} {rssi:>4} dBm  {dev_type}")
            
            return devices
        except:
            pass
    
    # Method 2: hcitool (root)
    output = run_cmd("hcitool scan 2>/dev/null")
    if output:
        print(output)
    
    # BLE Scan
    print(f"\n{Colors.CYAN}[BLE] Scanning BLE Devices...{Colors.END}")
    output = run_cmd("timeout 10 hcitool lescan 2>/dev/null")
    if output:
        print(output)
    
    return []

def classify_bt_device(name, mac):
    """Classify Bluetooth device type"""
    name_lower = name.lower()
    
    if any(x in name_lower for x in ['airpod', 'buds', 'earphone', 'headphone', 'jbl', 'sony wf', 'galaxy buds']):
        return "🎧 Audio"
    elif any(x in name_lower for x in ['band', 'watch', 'fit', 'mi band', 'amazfit']):
        return "⌚ Wearable"
    elif any(x in name_lower for x in ['tv', 'fire', 'roku', 'chromecast']):
        return "📺 TV/Streaming"
    elif any(x in name_lower for x in ['keyboard', 'mouse', 'logitech']):
        return "⌨️ Input Device"
    elif any(x in name_lower for x in ['speaker', 'soundbar', 'echo', 'alexa', 'google home']):
        return "🔊 Speaker"
    elif any(x in name_lower for x in ['phone', 'iphone', 'samsung', 'oneplus', 'xiaomi', 'redmi', 'realme', 'oppo', 'vivo']):
        return "📱 Phone"
    elif any(x in name_lower for x in ['laptop', 'macbook', 'thinkpad', 'dell', 'hp']):
        return "💻 Laptop"
    elif any(x in name_lower for x in ['printer', 'canon', 'epson', 'hp deskjet']):
        return "🖨️ Printer"
    elif any(x in name_lower for x in ['car', 'ford', 'honda', 'toyota', 'hyundai']):
        return "🚗 Car"
    else:
        return "📟 Unknown"

# ============== Cell Tower Scanner ==============
def scan_cell():
    """Scan Cell Tower information"""
    print(f"\n{Colors.MAGENTA}[📶] Scanning Cell Towers...{Colors.END}\n")
    
    # Method 1: Termux API
    output = run_cmd("termux-telephony-cellinfo 2>/dev/null")
    
    if output and "error" not in output.lower():
        try:
            cells = json.loads(output)
            print(f"{Colors.GREEN}Cell Tower Information:{Colors.END}\n")
            
            for i, cell in enumerate(cells):
                print(f"{Colors.YELLOW}━━━ Tower {i+1} ━━━{Colors.END}")
                
                cell_type = cell.get('type', 'Unknown')
                registered = cell.get('registered', False)
                
                print(f"  Type: {cell_type} {'(Connected)' if registered else ''}")
                
                if 'lte' in cell_type.lower():
                    print(f"  MCC: {cell.get('mcc', 'N/A')}")
                    print(f"  MNC: {cell.get('mnc', 'N/A')}")
                    print(f"  TAC: {cell.get('tac', 'N/A')}")
                    print(f"  CID: {cell.get('ci', 'N/A')}")
                    print(f"  PCI: {cell.get('pci', 'N/A')}")
                    print(f"  EARFCN: {cell.get('earfcn', 'N/A')}")
                    print(f"  Signal: {cell.get('rsrp', 'N/A')} dBm")
                    print(f"  Quality: {cell.get('rsrq', 'N/A')} dB")
                    
                    # Operator lookup
                    mcc = cell.get('mcc', 0)
                    mnc = cell.get('mnc', 0)
                    operator = get_operator(mcc, mnc)
                    if operator:
                        print(f"  Operator: {Colors.GREEN}{operator}{Colors.END}")
                
                elif 'gsm' in cell_type.lower():
                    print(f"  MCC: {cell.get('mcc', 'N/A')}")
                    print(f"  MNC: {cell.get('mnc', 'N/A')}")
                    print(f"  LAC: {cell.get('lac', 'N/A')}")
                    print(f"  CID: {cell.get('cid', 'N/A')}")
                    print(f"  Signal: {cell.get('rssi', 'N/A')} dBm")
                
                print()
            
            return cells
        except:
            pass
    
    # Method 2: Android getprop
    print(f"{Colors.YELLOW}[*] Trying alternative methods...{Colors.END}")
    output = run_cmd("getprop gsm.operator.alpha 2>/dev/null")
    if output:
        print(f"  Operator: {output.strip()}")
    
    output = run_cmd("getprop gsm.network.type 2>/dev/null")
    if output:
        print(f"  Network: {output.strip()}")
    
    return []

def get_operator(mcc, mnc):
    """Get operator name from MCC/MNC"""
    operators = {
        (404, 10): "Airtel", (404, 40): "Airtel", (404, 45): "Airtel",
        (404, 49): "Airtel", (404, 90): "Airtel", (404, 92): "Airtel",
        (404, 93): "Airtel", (404, 94): "Airtel", (404, 95): "Airtel",
        (404, 96): "Airtel", (404, 97): "Airtel", (404, 98): "Airtel",
        (405, 51): "Airtel", (405, 52): "Airtel", (405, 53): "Airtel",
        (405, 54): "Airtel", (405, 55): "Airtel", (405, 56): "Airtel",
        (404, 11): "Vi", (404, 12): "Vi", (404, 13): "Vi",
        (404, 14): "Vi", (404, 15): "Vi", (404, 20): "Vi",
        (404, 21): "Vi", (404, 22): "Vi", (404, 27): "Vi",
        (404, 43): "Vi", (404, 46): "Vi", (404, 84): "Vi",
        (404, 86): "Vi", (404, 88): "Vi",
        (405, 840): "Jio", (405, 854): "Jio", (405, 855): "Jio",
        (405, 856): "Jio", (405, 857): "Jio", (405, 858): "Jio",
        (405, 859): "Jio", (405, 860): "Jio", (405, 861): "Jio",
        (405, 862): "Jio", (405, 863): "Jio", (405, 864): "Jio",
        (405, 865): "Jio", (405, 866): "Jio", (405, 867): "Jio",
        (405, 868): "Jio", (405, 869): "Jio", (405, 870): "Jio",
        (404, 34): "BSNL", (404, 38): "BSNL", (404, 51): "BSNL",
        (404, 53): "BSNL", (404, 54): "BSNL", (404, 55): "BSNL",
        (404, 57): "BSNL", (404, 58): "BSNL", (404, 59): "BSNL",
        (404, 62): "BSNL", (404, 64): "BSNL", (404, 66): "BSNL",
        (404, 71): "BSNL", (404, 72): "BSNL", (404, 73): "BSNL",
        (404, 74): "BSNL", (404, 75): "BSNL", (404, 76): "BSNL",
        (404, 77): "BSNL", (404, 79): "BSNL", (404, 80): "BSNL",
        (404, 81): "BSNL",
    }
    return operators.get((mcc, mnc), None)


# ============== Network Radar ==============
def network_radar():
    """Scan connected network for devices"""
    print(f"\n{Colors.GREEN}[🌐] Network Radar - Scanning Connected Devices...{Colors.END}\n")
    
    # Get gateway IP
    gateway = run_cmd("ip route | grep default | awk '{print $3}'").strip()
    if not gateway:
        gateway = "192.168.1.1"
    
    subnet = '.'.join(gateway.split('.')[:-1]) + '.0/24'
    print(f"  Gateway: {gateway}")
    print(f"  Scanning: {subnet}\n")
    
    # Method 1: nmap
    output = run_cmd(f"nmap -sn {subnet} 2>/dev/null")
    if output and "Nmap scan" in output:
        parse_nmap_output(output)
        return
    
    # Method 2: arp-scan
    output = run_cmd(f"arp-scan {subnet} 2>/dev/null")
    if output:
        print(output)
        return
    
    # Method 3: ping sweep + arp
    print(f"{Colors.YELLOW}[*] Using ping sweep (slower)...{Colors.END}\n")
    
    devices = []
    base = '.'.join(gateway.split('.')[:-1])
    
    for i in range(1, 255):
        ip = f"{base}.{i}"
        result = run_cmd(f"ping -c 1 -W 1 {ip} 2>/dev/null")
        if "1 received" in result or "1 packets received" in result:
            mac = get_mac_for_ip(ip)
            vendor = get_vendor(mac) if mac else "Unknown"
            devices.append({'ip': ip, 'mac': mac, 'vendor': vendor})
            print(f"  {Colors.GREEN}●{Colors.END} {ip:<15} {mac or 'N/A':<18} {vendor}")
    
    print(f"\n{Colors.GREEN}Found {len(devices)} devices{Colors.END}")
    return devices

def get_mac_for_ip(ip):
    """Get MAC address for IP from ARP table"""
    output = run_cmd(f"arp -n {ip} 2>/dev/null")
    match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', output)
    return match.group(0) if match else None

def parse_nmap_output(output):
    """Parse nmap scan output"""
    lines = output.split('\n')
    current_ip = None
    
    print(f"{'IP Address':<16} {'MAC Address':<18} {'Vendor':<25} {'Hostname'}")
    print("="*80)
    
    for line in lines:
        if "Nmap scan report for" in line:
            parts = line.split()
            if '(' in line:
                current_ip = parts[-1].strip('()')
                hostname = parts[-2]
            else:
                current_ip = parts[-1]
                hostname = ""
        elif "MAC Address:" in line:
            parts = line.split("MAC Address: ")[1]
            mac = parts.split()[0]
            vendor = ' '.join(parts.split()[1:]).strip('()')[:24]
            print(f"{current_ip:<16} {mac:<18} {vendor:<25} {hostname}")


# ============== Camera Detector ==============
def detect_cameras():
    """Detect potential hidden cameras on network"""
    print(f"\n{Colors.RED}[📷] Hidden Camera Detection...{Colors.END}\n")
    
    # Camera vendor MAC prefixes
    camera_vendors = {
        '00:80:f0': 'Panasonic', '00:0e:8f': 'Cisco/Linksys',
        '00:18:ae': 'TVT', '00:12:5a': 'Geutebruck',
        '00:40:8c': 'Axis', '00:1a:07': 'Arecont',
        '00:30:53': 'Basler', '00:0f:7c': 'ACTi',
        '00:1c:10': 'Cisco-Linksys', '00:62:6e': 'Dahua',
        '28:57:be': 'Hangzhou Hikvision', '54:c4:15': 'Hangzhou Hikvision',
        'c0:56:e3': 'Hangzhou Hikvision', '44:19:b6': 'Hangzhou Hikvision',
        'c4:2f:90': 'Hangzhou Hikvision', 'a4:14:37': 'Hangzhou Hikvision',
        'bc:ad:28': 'Hangzhou Hikvision', '4c:bd:8f': 'Hangzhou Hikvision',
        'e0:50:8b': 'Zhejiang Dahua', '3c:ef:8c': 'Zhejiang Dahua',
        '90:02:a9': 'Zhejiang Dahua', 'a0:bd:1d': 'Zhejiang Dahua',
        '00:1f:54': 'Lorex', '00:0e:53': 'AV Tech',
        '00:0c:43': 'Ralink', '00:26:73': 'Ricoh',
        '00:1e:c9': 'Dell', '00:1a:6b': 'Universal Global',
        '00:1d:c9': 'GainSpan', '00:1e:58': 'D-Link',
        '00:24:a5': 'Buffalo', '00:26:5a': 'D-Link',
        '14:d6:4d': 'D-Link', '1c:7e:e5': 'D-Link',
        '28:10:7b': 'D-Link', '34:08:04': 'D-Link',
        '00:1c:f0': 'D-Link', '00:22:b0': 'D-Link',
        '00:26:5a': 'D-Link', '1c:bd:b9': 'D-Link',
        '00:1e:58': 'D-Link', '00:21:91': 'D-Link',
        '00:24:01': 'D-Link', '00:26:5a': 'D-Link',
        '00:05:5d': 'D-Link', '00:0d:88': 'D-Link',
        '00:0f:3d': 'D-Link', '00:11:95': 'D-Link',
        '00:13:46': 'D-Link', '00:15:e9': 'D-Link',
        '00:17:9a': 'D-Link', '00:19:5b': 'D-Link',
        '00:1b:11': 'D-Link', '00:1c:f0': 'D-Link',
        '00:50:ba': 'D-Link', '00:55:da': 'Xiongmai',
        '00:12:41': 'Xiongmai', 'e0:3f:49': 'ASUSTek',
        '00:1f:c6': 'ASUSTek', '00:22:15': 'ASUSTek',
        '00:23:54': 'ASUSTek', '00:24:8c': 'ASUSTek',
        '00:26:18': 'ASUSTek', '00:e0:18': 'ASUSTek',
        '00:e0:4c': 'Realtek', '00:0e:2e': 'Edimax',
        '00:1f:1f': 'Edimax', '00:50:fc': 'Edimax',
        '74:da:38': 'Edimax', '80:1f:02': 'Edimax',
        'b0:c5:54': 'D-Link', 'c8:be:19': 'D-Link',
        'cc:b2:55': 'D-Link', 'f0:7d:68': 'D-Link',
    }
    
    print(f"{Colors.YELLOW}[*] Scanning WiFi for camera devices...{Colors.END}\n")
    
    # Scan WiFi
    wifi_output = run_cmd("termux-wifi-scaninfo 2>/dev/null")
    cameras_found = []
    
    if wifi_output:
        try:
            networks = json.loads(wifi_output)
            for net in networks:
                bssid = net.get('bssid', '').lower()
                ssid = net.get('ssid', '')
                prefix = bssid[:8]
                
                # Check vendor
                if prefix in camera_vendors:
                    cameras_found.append({
                        'type': 'WiFi Camera',
                        'ssid': ssid,
                        'mac': bssid,
                        'vendor': camera_vendors[prefix],
                        'signal': net.get('rssi', 0)
                    })
                
                # Check SSID patterns
                camera_ssid_patterns = ['cam', 'ipcam', 'camera', 'dvr', 'nvr', 'cctv', 'hikvision', 'dahua', 'yi-', 'wyze']
                if any(p in ssid.lower() for p in camera_ssid_patterns):
                    cameras_found.append({
                        'type': 'Suspected Camera',
                        'ssid': ssid,
                        'mac': bssid,
                        'vendor': 'Unknown',
                        'signal': net.get('rssi', 0)
                    })
        except:
            pass
    
    # Network scan for camera ports
    print(f"{Colors.YELLOW}[*] Scanning network for camera ports (554, 8080, 8554)...{Colors.END}\n")
    
    gateway = run_cmd("ip route | grep default | awk '{print $3}'").strip()
    if gateway:
        subnet = '.'.join(gateway.split('.')[:-1]) + '.0/24'
        
        # Quick port scan
        output = run_cmd(f"nmap -p 554,8080,8554,80,443 --open {subnet} 2>/dev/null")
        if output:
            # Parse for open RTSP ports
            if "554/tcp" in output or "8554/tcp" in output:
                print(f"{Colors.RED}[!] RTSP streaming ports found - possible cameras!{Colors.END}")
                print(output)
    
    # Results
    if cameras_found:
        print(f"\n{Colors.RED}⚠️  POTENTIAL CAMERAS DETECTED:{Colors.END}\n")
        for cam in cameras_found:
            print(f"  {Colors.RED}●{Colors.END} {cam['type']}")
            print(f"    SSID: {cam['ssid']}")
            print(f"    MAC: {cam['mac']}")
            print(f"    Vendor: {cam['vendor']}")
            print(f"    Signal: {cam['signal']} dBm")
            print()
    else:
        print(f"{Colors.GREEN}[✓] No obvious cameras detected{Colors.END}")
    
    return cameras_found


# ============== Vendor Lookup ==============
def get_vendor(mac):
    """Get vendor from MAC address"""
    if not mac:
        return None
    
    prefix = mac.lower().replace('-', ':')[:8]
    
    vendors = {
        '00:00:0c': 'Cisco', '00:01:42': 'Cisco', '00:1a:a1': 'Cisco',
        '00:50:56': 'VMware', '00:0c:29': 'VMware', '00:15:5d': 'Microsoft Hyper-V',
        '08:00:27': 'VirtualBox', '52:54:00': 'QEMU',
        'b8:27:eb': 'Raspberry Pi', 'dc:a6:32': 'Raspberry Pi', 'e4:5f:01': 'Raspberry Pi',
        '00:1e:c2': 'Apple', '00:03:93': 'Apple', '00:0a:95': 'Apple',
        '00:0d:93': 'Apple', '00:11:24': 'Apple', '00:14:51': 'Apple',
        '00:16:cb': 'Apple', '00:17:f2': 'Apple', '00:19:e3': 'Apple',
        '00:1b:63': 'Apple', '00:1c:b3': 'Apple', '00:1d:4f': 'Apple',
        '00:1e:52': 'Apple', '00:1f:5b': 'Apple', '00:1f:f3': 'Apple',
        '00:21:e9': 'Apple', '00:22:41': 'Apple', '00:23:12': 'Apple',
        '00:23:32': 'Apple', '00:23:6c': 'Apple', '00:23:df': 'Apple',
        '00:24:36': 'Apple', '00:25:00': 'Apple', '00:25:4b': 'Apple',
        '00:25:bc': 'Apple', '00:26:08': 'Apple', '00:26:4a': 'Apple',
        '00:26:b0': 'Apple', '00:26:bb': 'Apple', '04:0c:ce': 'Apple',
        '04:15:52': 'Apple', '04:1e:64': 'Apple', '04:26:65': 'Apple',
        '04:48:9a': 'Apple', '04:52:f3': 'Apple', '04:54:53': 'Apple',
        '04:d3:cf': 'Apple', '04:db:56': 'Apple', '04:e5:36': 'Apple',
        '04:f1:3e': 'Apple', '04:f7:e4': 'Apple', '08:66:98': 'Apple',
        '08:6d:41': 'Apple', '08:70:45': 'Apple', '08:74:02': 'Apple',
        'f8:ff:c2': 'Apple', 'fc:25:3f': 'Apple', 'fc:e9:98': 'Apple',
        '00:09:2d': 'HTC', '00:23:76': 'HTC', '18:87:96': 'HTC',
        '1c:b0:94': 'HTC', '2c:8a:72': 'HTC', '38:e7:d8': 'HTC',
        '64:a7:69': 'HTC', '7c:61:93': 'HTC', '80:01:84': 'HTC',
        '84:7a:88': 'HTC', '90:21:55': 'HTC', '98:0d:2e': 'HTC',
        'a0:f4:50': 'HTC', 'ac:37:43': 'HTC', 'b4:ce:f6': 'HTC',
        'd8:b3:77': 'HTC', 'e8:99:c4': 'HTC', 'f8:db:7f': 'HTC',
        '00:12:fb': 'Samsung', '00:13:77': 'Samsung', '00:15:99': 'Samsung',
        '00:16:32': 'Samsung', '00:16:6b': 'Samsung', '00:16:6c': 'Samsung',
        '00:17:c9': 'Samsung', '00:17:d5': 'Samsung', '00:18:af': 'Samsung',
        '00:1a:8a': 'Samsung', '00:1b:98': 'Samsung', '00:1c:43': 'Samsung',
        '00:1d:25': 'Samsung', '00:1d:f6': 'Samsung', '00:1e:7d': 'Samsung',
        '00:1f:cc': 'Samsung', '00:1f:cd': 'Samsung', '00:21:19': 'Samsung',
        '00:21:4c': 'Samsung', '00:21:d1': 'Samsung', '00:21:d2': 'Samsung',
        '00:23:39': 'Samsung', '00:23:3a': 'Samsung', '00:23:99': 'Samsung',
        '00:23:d6': 'Samsung', '00:23:d7': 'Samsung', '00:24:54': 'Samsung',
        '00:24:90': 'Samsung', '00:24:91': 'Samsung', '00:24:e9': 'Samsung',
        '00:25:66': 'Samsung', '00:25:67': 'Samsung', '00:26:37': 'Samsung',
        '9c:02:98': 'Samsung', '9c:3a:af': 'Samsung', '9c:65:b0': 'Samsung',
        '28:6a:ba': 'Xiaomi', '0c:1d:af': 'Xiaomi', '14:f6:5a': 'Xiaomi',
        '18:59:36': 'Xiaomi', '20:82:c0': 'Xiaomi', '34:80:b3': 'Xiaomi',
        '38:a4:ed': 'Xiaomi', '3c:bd:3e': 'Xiaomi', '50:64:2b': 'Xiaomi',
        '58:44:98': 'Xiaomi', '64:09:80': 'Xiaomi', '64:b4:73': 'Xiaomi',
        '68:df:dd': 'Xiaomi', '74:23:44': 'Xiaomi', '74:51:ba': 'Xiaomi',
        '78:02:f8': 'Xiaomi', '78:11:dc': 'Xiaomi', '7c:1d:d9': 'Xiaomi',
        '84:f3:eb': 'Xiaomi', '88:c3:97': 'Xiaomi', '8c:be:be': 'Xiaomi',
        '98:fa:e3': 'Xiaomi', '9c:99:a0': 'Xiaomi', 'a0:86:c6': 'Xiaomi',
        'a4:77:33': 'Xiaomi', 'ac:c1:ee': 'Xiaomi', 'ac:f7:f3': 'Xiaomi',
        'b0:e2:35': 'Xiaomi', 'c4:0b:cb': 'Xiaomi', 'c4:6a:b7': 'Xiaomi',
        'd4:97:0b': 'Xiaomi', 'e8:ab:fa': 'Xiaomi', 'ec:d0:9f': 'Xiaomi',
        'f0:b4:29': 'Xiaomi', 'f4:f5:db': 'Xiaomi', 'f8:a4:5f': 'Xiaomi',
        'fc:64:ba': 'Xiaomi',
        '2c:33:61': 'OnePlus', '64:a2:f9': 'OnePlus', '94:65:2d': 'OnePlus',
        'c0:ee:fb': 'OnePlus',
        '00:09:df': 'Realme/Oppo', '1c:77:f6': 'Realme/Oppo', '2c:5b:b8': 'Realme/Oppo',
        '3c:cd:5d': 'Realme/Oppo', '48:db:50': 'Realme/Oppo', '5c:4c:a9': 'Realme/Oppo',
        '74:04:2b': 'Realme/Oppo', '88:44:77': 'Realme/Oppo', '90:17:ac': 'Realme/Oppo',
        '94:d9:b3': 'Realme/Oppo', 'a4:3b:fa': 'Realme/Oppo', 'ac:5a:fc': 'Realme/Oppo',
        'b4:a9:84': 'Realme/Oppo', 'bc:7f:a4': 'Realme/Oppo', 'c4:50:06': 'Realme/Oppo',
        'd4:50:3f': 'Realme/Oppo', 'e8:61:7e': 'Realme/Oppo', 'ec:5c:68': 'Realme/Oppo',
        'f4:c1:14': 'Realme/Oppo',
        '00:e0:4c': 'Realtek', '4c:ed:fb': 'Realtek', '52:54:00': 'Realtek',
        '00:1d:7e': 'TP-Link', '14:cc:20': 'TP-Link', '14:cf:92': 'TP-Link',
        '18:a6:f7': 'TP-Link', '1c:3b:f3': 'TP-Link', '30:b5:c2': 'TP-Link',
        '50:c7:bf': 'TP-Link', '54:c8:0f': 'TP-Link', '5c:89:9a': 'TP-Link',
        '60:e3:27': 'TP-Link', '64:56:01': 'TP-Link', '64:66:b3': 'TP-Link',
        '64:70:02': 'TP-Link', '6c:5a:b0': 'TP-Link', '78:44:76': 'TP-Link',
        '90:f6:52': 'TP-Link', '94:0c:6d': 'TP-Link', '98:da:c4': 'TP-Link',
        'a4:2b:b0': 'TP-Link', 'ac:84:c6': 'TP-Link', 'b0:4e:26': 'TP-Link',
        'b0:95:75': 'TP-Link', 'c0:25:e9': 'TP-Link', 'c4:6e:1f': 'TP-Link',
        'c8:3a:35': 'TP-Link', 'd4:6e:0e': 'TP-Link', 'd8:07:b6': 'TP-Link',
        'e4:d3:32': 'TP-Link', 'e8:94:f6': 'TP-Link', 'ec:08:6b': 'TP-Link',
        'ec:17:2f': 'TP-Link', 'f4:ec:38': 'TP-Link', 'f8:1a:67': 'TP-Link',
        '34:60:f9': 'Jio', '48:ee:0c': 'Jio', '5c:aa:fd': 'Jio',
        '74:40:be': 'Jio', '78:d2:94': 'Jio', '84:a9:3e': 'Jio',
        '94:b8:6d': 'Jio', 'a4:c6:4f': 'Jio', 'b4:a9:fc': 'Jio',
        'c8:02:10': 'Jio', 'd4:a1:48': 'Jio', 'e8:65:d4': 'Jio',
        'f0:81:75': 'Jio', 'f4:ee:14': 'Jio',
    }
    
    return vendors.get(prefix, None)


# ============== Full Scan ==============
def full_scan():
    """Run all scans"""
    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"       📡 FULL SIGNAL INTELLIGENCE SCAN")
    print(f"{'='*50}{Colors.END}\n")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Scan Time: {timestamp}\n")
    
    results = {
        'timestamp': timestamp,
        'wifi': [],
        'bluetooth': [],
        'cell': [],
        'network': [],
        'cameras': []
    }
    
    # WiFi
    results['wifi'] = scan_wifi() or []
    
    # Bluetooth
    results['bluetooth'] = scan_bluetooth() or []
    
    # Cell
    results['cell'] = scan_cell() or []
    
    # Network
    results['network'] = network_radar() or []
    
    # Cameras
    results['cameras'] = detect_cameras() or []
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"              📊 SCAN SUMMARY")
    print(f"{'='*50}{Colors.END}\n")
    
    print(f"  📡 WiFi Networks:     {len(results['wifi'])}")
    print(f"  🔵 Bluetooth Devices: {len(results['bluetooth'])}")
    print(f"  📶 Cell Towers:       {len(results['cell'])}")
    print(f"  🌐 Network Devices:   {len(results['network'])}")
    print(f"  📷 Suspected Cameras: {len(results['cameras'])}")
    
    return results

# ============== Export Data ==============
def export_data(results):
    """Export scan results to JSON"""
    if not results:
        print(f"{Colors.RED}[!] No data to export. Run a scan first.{Colors.END}")
        return
    
    filename = f"signal_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"{Colors.GREEN}[✓] Data exported to: {filename}{Colors.END}")

# ============== Setup ==============
def setup_termux():
    """Install required packages"""
    print(f"\n{Colors.CYAN}[*] Setting up Termux environment...{Colors.END}\n")
    
    packages = [
        'termux-api',
        'nmap',
        'python',
        'wireless-tools',
        'net-tools',
        'iproute2'
    ]
    
    for pkg in packages:
        print(f"  Installing {pkg}...")
        run_cmd(f"pkg install -y {pkg}")
    
    print(f"\n{Colors.GREEN}[✓] Setup complete!{Colors.END}")
    print(f"{Colors.YELLOW}[!] Also install 'Termux:API' app from F-Droid{Colors.END}")

# ============== Main ==============
def main():
    results = None
    
    while True:
        banner()
        choice = input(f"{Colors.CYAN}Select option: {Colors.END}").strip()
        
        if choice == '1':
            scan_wifi()
        elif choice == '2':
            scan_bluetooth()
        elif choice == '3':
            network_radar()
        elif choice == '4':
            results = full_scan()
        elif choice == '5':
            scan_cell()
        elif choice == '6':
            network_radar()
        elif choice == '7':
            detect_cameras()
        elif choice == '8':
            export_data(results)
        elif choice == '9':
            setup_termux()
        elif choice == '0':
            print(f"\n{Colors.GREEN}Goodbye! 👋{Colors.END}\n")
            break
        else:
            print(f"{Colors.RED}Invalid option{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    main()
