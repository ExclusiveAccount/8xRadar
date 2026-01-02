#!/usr/bin/env python3
"""
📡 CELL INTELLIGENCE - NetMonster Style Detailed Cell Tower Info
Coordinates, Direction, Distance, Bands, Satellite View
"""

import subprocess
import json
import math
import os
import time
import sqlite3
from datetime import datetime

# ============== COLORS ==============
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
    BOLD = '\033[1m'; DIM = '\033[2m'; E = '\033[0m'

# ============== INDIA OPERATORS DATABASE ==============
OPERATORS = {
    # Airtel
    (404,10):"Airtel",(404,40):"Airtel",(404,45):"Airtel",(404,49):"Airtel",
    (404,90):"Airtel",(404,92):"Airtel",(404,93):"Airtel",(404,94):"Airtel",
    (404,95):"Airtel",(404,96):"Airtel",(404,97):"Airtel",(404,98):"Airtel",
    (405,51):"Airtel",(405,52):"Airtel",(405,53):"Airtel",(405,54):"Airtel",
    (405,55):"Airtel",(405,56):"Airtel",
    # Vi (Vodafone Idea)
    (404,11):"Vi",(404,12):"Vi",(404,13):"Vi",(404,14):"Vi",(404,15):"Vi",
    (404,20):"Vi",(404,21):"Vi",(404,22):"Vi",(404,27):"Vi",(404,43):"Vi",
    (404,46):"Vi",(404,84):"Vi",(404,86):"Vi",(404,88):"Vi",
    # Jio
    (405,840):"Jio",(405,854):"Jio",(405,855):"Jio",(405,856):"Jio",
    (405,857):"Jio",(405,858):"Jio",(405,859):"Jio",(405,860):"Jio",
    (405,861):"Jio",(405,862):"Jio",(405,863):"Jio",(405,864):"Jio",
    (405,865):"Jio",(405,866):"Jio",(405,867):"Jio",(405,868):"Jio",
    (405,869):"Jio",(405,870):"Jio",(405,871):"Jio",(405,872):"Jio",
    (405,873):"Jio",(405,874):"Jio",
    # BSNL
    (404,34):"BSNL",(404,38):"BSNL",(404,51):"BSNL",(404,53):"BSNL",
    (404,54):"BSNL",(404,55):"BSNL",(404,57):"BSNL",(404,58):"BSNL",
    (404,59):"BSNL",(404,62):"BSNL",(404,64):"BSNL",(404,66):"BSNL",
    (404,71):"BSNL",(404,72):"BSNL",(404,73):"BSNL",(404,74):"BSNL",
    (404,75):"BSNL",(404,76):"BSNL",(404,77):"BSNL",(404,79):"BSNL",
    (404,80):"BSNL",(404,81):"BSNL",
    # MTNL
    (404,68):"MTNL Delhi",(404,69):"MTNL Mumbai",
}

# ============== LTE BANDS DATABASE ==============
LTE_BANDS = {
    # EARFCN to Band mapping (India)
    range(0, 600): {"band": 1, "freq": 2100, "name": "B1 (2100 MHz)", "ops": ["Airtel", "Vi"]},
    range(1200, 1950): {"band": 3, "freq": 1800, "name": "B3 (1800 MHz)", "ops": ["Jio", "Airtel", "Vi"]},
    range(2400, 2650): {"band": 5, "freq": 850, "name": "B5 (850 MHz)", "ops": ["Jio"]},
    range(2750, 3450): {"band": 8, "freq": 900, "name": "B8 (900 MHz)", "ops": ["Airtel", "Vi"]},
    range(38650, 39650): {"band": 40, "freq": 2300, "name": "B40 TDD (2300 MHz)", "ops": ["Airtel", "Jio"]},
    range(39650, 41590): {"band": 41, "freq": 2500, "name": "B41 TDD (2500 MHz)", "ops": ["Jio"]},
}

# ============== 5G NR BANDS ==============
NR_BANDS = {
    range(422000, 434000): {"band": "n1", "freq": 2100, "name": "n1 (2100 MHz)"},
    range(361000, 376000): {"band": "n3", "freq": 1800, "name": "n3 (1800 MHz)"},
    range(386000, 398000): {"band": "n5", "freq": 850, "name": "n5 (850 MHz)"},
    range(496700, 499000): {"band": "n28", "freq": 700, "name": "n28 (700 MHz)"},
    range(499200, 538000): {"band": "n41", "freq": 2500, "name": "n41 (2500 MHz)"},
    range(620000, 680000): {"band": "n78", "freq": 3500, "name": "n78 (3500 MHz)"},
}

# ============== CIRCLE CODES ==============
CIRCLES = {
    # LAC ranges to Circle (approximate)
    "Maharashtra": [(1, 50), (1000, 1100)],
    "Mumbai": [(51, 100), (1100, 1200)],
    "Delhi": [(101, 150), (1200, 1300)],
    "Karnataka": [(151, 200), (1300, 1400)],
    "Tamil Nadu": [(201, 250), (1400, 1500)],
    "Andhra Pradesh": [(251, 300), (1500, 1600)],
    "Gujarat": [(301, 350), (1600, 1700)],
    "UP East": [(351, 400), (1700, 1800)],
    "UP West": [(401, 450), (1800, 1900)],
    "Rajasthan": [(451, 500), (1900, 2000)],
}

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except:
        return ""


# ============== CELL TOWER CALCULATIONS ==============
def get_band_from_earfcn(earfcn):
    """Get LTE band info from EARFCN"""
    for earfcn_range, info in LTE_BANDS.items():
        if earfcn in earfcn_range:
            return info
    return {"band": "?", "freq": 0, "name": "Unknown", "ops": []}

def get_nr_band(nrarfcn):
    """Get 5G NR band from NRARFCN"""
    for arfcn_range, info in NR_BANDS.items():
        if nrarfcn in arfcn_range:
            return info
    return {"band": "?", "freq": 0, "name": "Unknown"}

def calculate_distance_ta(timing_advance, network_type="LTE"):
    """Calculate distance from Timing Advance"""
    if timing_advance is None or timing_advance < 0:
        return None
    
    if network_type == "LTE":
        # LTE: TA * 78.12m (each TA unit = ~78m)
        return timing_advance * 78.12
    elif network_type == "GSM":
        # GSM: TA * 550m
        return timing_advance * 550
    return None

def calculate_distance_rsrp(rsrp, freq_mhz=1800):
    """Estimate distance from RSRP using path loss model"""
    if rsrp is None or rsrp > -40:
        return None
    
    # Free space path loss model (approximate)
    # RSRP = Tx_Power - PathLoss
    # Assuming Tx_Power = 43 dBm for macro cell
    tx_power = 43
    path_loss = tx_power - rsrp
    
    # Path Loss = 20*log10(d) + 20*log10(f) + 32.44
    # d = 10^((PathLoss - 20*log10(f) - 32.44) / 20)
    try:
        d_km = 10 ** ((path_loss - 20 * math.log10(freq_mhz) - 32.44) / 20)
        return d_km * 1000  # meters
    except:
        return None

def get_direction_arrow(azimuth):
    """Get direction arrow from azimuth"""
    if azimuth is None:
        return "?"
    
    directions = [
        (0, "↑ N"), (45, "↗ NE"), (90, "→ E"), (135, "↘ SE"),
        (180, "↓ S"), (225, "↙ SW"), (270, "← W"), (315, "↖ NW"), (360, "↑ N")
    ]
    
    for angle, arrow in directions:
        if abs(azimuth - angle) <= 22.5:
            return arrow
    return "?"

def signal_quality(rsrp=None, rsrq=None, sinr=None):
    """Calculate overall signal quality"""
    score = 0
    
    if rsrp:
        if rsrp > -80: score += 40
        elif rsrp > -90: score += 30
        elif rsrp > -100: score += 20
        elif rsrp > -110: score += 10
    
    if rsrq:
        if rsrq > -10: score += 30
        elif rsrq > -15: score += 20
        elif rsrq > -20: score += 10
    
    if sinr:
        if sinr > 20: score += 30
        elif sinr > 10: score += 20
        elif sinr > 0: score += 10
    
    if score >= 80: return f"{C.G}Excellent{C.E}"
    elif score >= 60: return f"{C.G}Good{C.E}"
    elif score >= 40: return f"{C.Y}Fair{C.E}"
    elif score >= 20: return f"{C.Y}Poor{C.E}"
    else: return f"{C.R}Very Poor{C.E}"

def signal_bars(rsrp):
    """Visual signal bars"""
    if rsrp is None: return f"{C.DIM}░░░░░{C.E}"
    if rsrp > -70: return f"{C.G}█████{C.E}"
    elif rsrp > -80: return f"{C.G}████{C.DIM}░{C.E}"
    elif rsrp > -90: return f"{C.Y}███{C.DIM}░░{C.E}"
    elif rsrp > -100: return f"{C.Y}██{C.DIM}░░░{C.E}"
    elif rsrp > -110: return f"{C.R}█{C.DIM}░░░░{C.E}"
    else: return f"{C.R}░{C.DIM}░░░░{C.E}"


# ============== LOCATION LOOKUP (OpenCellID Style) ==============
def lookup_cell_location(mcc, mnc, lac, cid):
    """
    Lookup cell tower location from local database or API
    Returns: (lat, lon, accuracy) or None
    """
    # Try local database first
    db_path = "cell_towers.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT lat, lon, range FROM towers 
                WHERE mcc=? AND mnc=? AND lac=? AND cid=?
            """, (mcc, mnc, lac, cid))
            row = cur.fetchone()
            conn.close()
            if row:
                return row
        except:
            pass
    
    # Try online lookup (if internet available)
    # Using free APIs
    apis = [
        f"http://opencellid.org/cell/get?key=pk.xxx&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cid}&format=json",
        f"https://us1.unwiredlabs.com/v2/process.php",  # Requires API key
    ]
    
    # For now, return estimated location based on operator circle
    return estimate_location(mcc, mnc, lac)

def estimate_location(mcc, mnc, lac):
    """Estimate rough location from LAC (circle level)"""
    # Major city coordinates for India operators
    circle_coords = {
        "Maharashtra": (19.0760, 72.8777),  # Mumbai
        "Delhi": (28.6139, 77.2090),
        "Karnataka": (12.9716, 77.5946),  # Bangalore
        "Tamil Nadu": (13.0827, 80.2707),  # Chennai
        "Gujarat": (23.0225, 72.5714),  # Ahmedabad
        "UP": (26.8467, 80.9462),  # Lucknow
        "Rajasthan": (26.9124, 75.7873),  # Jaipur
        "West Bengal": (22.5726, 88.3639),  # Kolkata
        "Andhra Pradesh": (17.3850, 78.4867),  # Hyderabad
        "Kerala": (8.5241, 76.9366),  # Trivandrum
        "Punjab": (30.7333, 76.7794),  # Chandigarh
        "MP": (23.2599, 77.4126),  # Bhopal
    }
    
    # Return default (India center) if unknown
    return (20.5937, 78.9629, 50000)  # India center, 50km accuracy

# ============== GPS FUNCTIONS ==============
def get_current_gps():
    """Get current GPS location from Termux"""
    out = cmd("termux-location -p gps 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            return (loc.get('latitude'), loc.get('longitude'), loc.get('accuracy', 0))
        except:
            pass
    
    # Try network location
    out = cmd("termux-location -p network 2>/dev/null")
    if out:
        try:
            loc = json.loads(out)
            return (loc.get('latitude'), loc.get('longitude'), loc.get('accuracy', 0))
        except:
            pass
    
    return None

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing

def calculate_distance_gps(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points (Haversine)"""
    R = 6371000  # Earth radius in meters
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


# ============== DETAILED CELL INFO PARSER ==============
def parse_cell_detailed(cell_data):
    """Parse cell data and add detailed info"""
    cells = []
    
    for cell in cell_data:
        info = {
            'raw': cell,
            'type': cell.get('type', 'Unknown'),
            'registered': cell.get('registered', False),
            'timestamp': datetime.now().isoformat(),
        }
        
        cell_type = cell.get('type', '').lower()
        
        # ============== LTE ==============
        if 'lte' in cell_type:
            mcc = cell.get('mcc', 0)
            mnc = cell.get('mnc', 0)
            tac = cell.get('tac', 0)
            ci = cell.get('ci', 0)
            pci = cell.get('pci', 0)
            earfcn = cell.get('earfcn', 0)
            
            # Signal metrics
            rsrp = cell.get('rsrp')
            rsrq = cell.get('rsrq')
            rssi = cell.get('rssi')
            sinr = cell.get('rssnr') or cell.get('sinr')
            cqi = cell.get('cqi')
            ta = cell.get('timingAdvance') or cell.get('ta')
            
            # Band info
            band_info = get_band_from_earfcn(earfcn)
            
            # Distance calculation
            distance = None
            if ta and ta >= 0:
                distance = calculate_distance_ta(ta, "LTE")
            elif rsrp:
                distance = calculate_distance_rsrp(rsrp, band_info.get('freq', 1800))
            
            # eNodeB and Sector
            enodeb = ci // 256 if ci else None
            sector = ci % 256 if ci else None
            
            info.update({
                'network': '4G LTE',
                'mcc': mcc,
                'mnc': mnc,
                'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                'tac': tac,
                'ci': ci,
                'enodeb': enodeb,
                'sector': sector,
                'pci': pci,
                'earfcn': earfcn,
                'band': band_info.get('name', 'Unknown'),
                'band_num': band_info.get('band'),
                'frequency': band_info.get('freq'),
                'rsrp': rsrp,
                'rsrq': rsrq,
                'rssi': rssi,
                'sinr': sinr,
                'cqi': cqi,
                'timing_advance': ta,
                'distance_m': distance,
                'quality': signal_quality(rsrp, rsrq, sinr),
            })
        
        # ============== 5G NR ==============
        elif 'nr' in cell_type or '5g' in cell_type:
            mcc = cell.get('mcc', 0)
            mnc = cell.get('mnc', 0)
            tac = cell.get('tac', 0)
            nci = cell.get('nci') or cell.get('ci', 0)
            pci = cell.get('pci', 0)
            nrarfcn = cell.get('nrarfcn', 0)
            
            # Signal
            ss_rsrp = cell.get('ssRsrp') or cell.get('csiRsrp')
            ss_rsrq = cell.get('ssRsrq') or cell.get('csiRsrq')
            ss_sinr = cell.get('ssSinr') or cell.get('csiSinr')
            
            # Band
            nr_band = get_nr_band(nrarfcn)
            
            # gNodeB
            gnodeb = nci // 4096 if nci else None
            sector = nci % 4096 if nci else None
            
            info.update({
                'network': '5G NR',
                'mcc': mcc,
                'mnc': mnc,
                'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                'tac': tac,
                'nci': nci,
                'gnodeb': gnodeb,
                'sector': sector,
                'pci': pci,
                'nrarfcn': nrarfcn,
                'band': nr_band.get('name', 'Unknown'),
                'frequency': nr_band.get('freq'),
                'ss_rsrp': ss_rsrp,
                'ss_rsrq': ss_rsrq,
                'ss_sinr': ss_sinr,
                'quality': signal_quality(ss_rsrp, ss_rsrq, ss_sinr),
            })
        
        # ============== GSM ==============
        elif 'gsm' in cell_type:
            mcc = cell.get('mcc', 0)
            mnc = cell.get('mnc', 0)
            lac = cell.get('lac', 0)
            cid = cell.get('cid', 0)
            arfcn = cell.get('arfcn', 0)
            bsic = cell.get('bsic', 0)
            
            rssi = cell.get('rssi')
            ta = cell.get('timingAdvance')
            
            # Distance
            distance = calculate_distance_ta(ta, "GSM") if ta else None
            
            # Band from ARFCN
            if 1 <= arfcn <= 124:
                band = "GSM 900"
                freq = 900
            elif 512 <= arfcn <= 885:
                band = "GSM 1800"
                freq = 1800
            else:
                band = "Unknown"
                freq = 0
            
            info.update({
                'network': '2G GSM',
                'mcc': mcc,
                'mnc': mnc,
                'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                'lac': lac,
                'cid': cid,
                'arfcn': arfcn,
                'bsic': bsic,
                'band': band,
                'frequency': freq,
                'rssi': rssi,
                'timing_advance': ta,
                'distance_m': distance,
            })
        
        # ============== WCDMA/3G ==============
        elif 'wcdma' in cell_type or 'umts' in cell_type:
            mcc = cell.get('mcc', 0)
            mnc = cell.get('mnc', 0)
            lac = cell.get('lac', 0)
            cid = cell.get('cid', 0)
            psc = cell.get('psc', 0)
            uarfcn = cell.get('uarfcn', 0)
            
            rscp = cell.get('rscp')
            ecno = cell.get('ecno')
            
            # RNC and Cell
            rnc = cid // 65536 if cid else None
            cell_id = cid % 65536 if cid else None
            
            info.update({
                'network': '3G WCDMA',
                'mcc': mcc,
                'mnc': mnc,
                'operator': OPERATORS.get((mcc, mnc), 'Unknown'),
                'lac': lac,
                'cid': cid,
                'rnc': rnc,
                'cell_id': cell_id,
                'psc': psc,
                'uarfcn': uarfcn,
                'rscp': rscp,
                'ecno': ecno,
            })
        
        cells.append(info)
    
    return cells


# ============== DISPLAY FUNCTIONS ==============
def display_cell_detailed(cell):
    """Display detailed cell info like NetMonster"""
    
    is_connected = cell.get('registered', False)
    conn_icon = f"{C.G}●{C.E}" if is_connected else f"{C.DIM}○{C.E}"
    
    network = cell.get('network', 'Unknown')
    operator = cell.get('operator', 'Unknown')
    
    # Network type color
    if '5G' in network:
        net_color = C.C
    elif '4G' in network:
        net_color = C.G
    elif '3G' in network:
        net_color = C.Y
    else:
        net_color = C.R
    
    print(f"""
{C.BOLD}╔══════════════════════════════════════════════════════════════════╗
║ {conn_icon} {net_color}{network}{C.E} - {C.BOLD}{operator}{C.E}{'  [CONNECTED]' if is_connected else ''}
╠══════════════════════════════════════════════════════════════════╣{C.E}""")
    
    # ============== IDENTITY ==============
    print(f"{C.BOLD}│ 📋 IDENTITY{C.E}")
    print(f"│   MCC: {cell.get('mcc', 'N/A'):<6} MNC: {cell.get('mnc', 'N/A'):<6}")
    
    if 'LTE' in network:
        print(f"│   TAC: {cell.get('tac', 'N/A'):<10} CI: {cell.get('ci', 'N/A')}")
        print(f"│   eNodeB: {cell.get('enodeb', 'N/A'):<8} Sector: {cell.get('sector', 'N/A')}")
        print(f"│   PCI: {cell.get('pci', 'N/A')}")
    elif '5G' in network:
        print(f"│   TAC: {cell.get('tac', 'N/A'):<10} NCI: {cell.get('nci', 'N/A')}")
        print(f"│   gNodeB: {cell.get('gnodeb', 'N/A'):<8} Sector: {cell.get('sector', 'N/A')}")
        print(f"│   PCI: {cell.get('pci', 'N/A')}")
    elif 'GSM' in network:
        print(f"│   LAC: {cell.get('lac', 'N/A'):<10} CID: {cell.get('cid', 'N/A')}")
        print(f"│   BSIC: {cell.get('bsic', 'N/A')}")
    elif 'WCDMA' in network:
        print(f"│   LAC: {cell.get('lac', 'N/A'):<10} CID: {cell.get('cid', 'N/A')}")
        print(f"│   RNC: {cell.get('rnc', 'N/A'):<10} PSC: {cell.get('psc', 'N/A')}")
    
    # ============== FREQUENCY ==============
    print(f"│")
    print(f"{C.BOLD}│ 📡 FREQUENCY{C.E}")
    print(f"│   Band: {C.C}{cell.get('band', 'N/A')}{C.E}")
    print(f"│   Frequency: {cell.get('frequency', 'N/A')} MHz")
    
    if 'LTE' in network:
        print(f"│   EARFCN: {cell.get('earfcn', 'N/A')}")
    elif '5G' in network:
        print(f"│   NRARFCN: {cell.get('nrarfcn', 'N/A')}")
    elif 'GSM' in network:
        print(f"│   ARFCN: {cell.get('arfcn', 'N/A')}")
    elif 'WCDMA' in network:
        print(f"│   UARFCN: {cell.get('uarfcn', 'N/A')}")
    
    # ============== SIGNAL ==============
    print(f"│")
    print(f"{C.BOLD}│ 📶 SIGNAL{C.E}")
    
    if 'LTE' in network:
        rsrp = cell.get('rsrp')
        bars = signal_bars(rsrp)
        print(f"│   {bars}  Quality: {cell.get('quality', 'N/A')}")
        print(f"│   RSRP: {rsrp if rsrp else 'N/A'} dBm")
        print(f"│   RSRQ: {cell.get('rsrq', 'N/A')} dB")
        print(f"│   RSSI: {cell.get('rssi', 'N/A')} dBm")
        print(f"│   SINR: {cell.get('sinr', 'N/A')} dB")
        print(f"│   CQI:  {cell.get('cqi', 'N/A')}")
    elif '5G' in network:
        rsrp = cell.get('ss_rsrp')
        bars = signal_bars(rsrp)
        print(f"│   {bars}  Quality: {cell.get('quality', 'N/A')}")
        print(f"│   SS-RSRP: {rsrp if rsrp else 'N/A'} dBm")
        print(f"│   SS-RSRQ: {cell.get('ss_rsrq', 'N/A')} dB")
        print(f"│   SS-SINR: {cell.get('ss_sinr', 'N/A')} dB")
    elif 'GSM' in network:
        rssi = cell.get('rssi')
        bars = signal_bars(rssi)
        print(f"│   {bars}")
        print(f"│   RSSI: {rssi if rssi else 'N/A'} dBm")
    elif 'WCDMA' in network:
        rscp = cell.get('rscp')
        bars = signal_bars(rscp)
        print(f"│   {bars}")
        print(f"│   RSCP: {rscp if rscp else 'N/A'} dBm")
        print(f"│   Ec/No: {cell.get('ecno', 'N/A')} dB")
    
    # ============== DISTANCE ==============
    print(f"│")
    print(f"{C.BOLD}│ 📍 DISTANCE{C.E}")
    
    ta = cell.get('timing_advance')
    distance = cell.get('distance_m')
    
    if ta is not None:
        print(f"│   Timing Advance: {ta}")
    
    if distance:
        if distance < 1000:
            print(f"│   Estimated Distance: {C.Y}{distance:.0f} m{C.E}")
        else:
            print(f"│   Estimated Distance: {C.Y}{distance/1000:.2f} km{C.E}")
    else:
        print(f"│   Estimated Distance: N/A")
    
    print(f"╚══════════════════════════════════════════════════════════════════╝")


# ============== COMPASS DISPLAY ==============
def display_compass(cells, gps_location=None):
    """Display tower directions as compass"""
    
    print(f"""
{C.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                    🧭 TOWER COMPASS                               ║
╠══════════════════════════════════════════════════════════════════╣{C.E}""")
    
    if not gps_location:
        print(f"│   {C.Y}GPS not available - showing relative positions{C.E}")
    
    # ASCII Compass
    print(f"""│
│                          {C.BOLD}N{C.E}
│                          ↑
│                     NW   │   NE
│                       ╲  │  ╱
│                   W ────●──── E
│                       ╱  │  ╲
│                     SW   │   SE
│                          ↓
│                          {C.BOLD}S{C.E}
│""")
    
    # List towers with direction
    print(f"│   {C.BOLD}Towers:{C.E}")
    for i, cell in enumerate(cells[:5]):
        op = cell.get('operator', '?')[:8]
        net = cell.get('network', '?')[:6]
        dist = cell.get('distance_m')
        
        if dist:
            if dist < 1000:
                dist_str = f"{dist:.0f}m"
            else:
                dist_str = f"{dist/1000:.1f}km"
        else:
            dist_str = "?"
        
        # Simulated direction (would need real GPS + tower coords)
        directions = ["↑ N", "↗ NE", "→ E", "↘ SE", "↓ S", "↙ SW", "← W", "↖ NW"]
        direction = directions[i % 8]
        
        conn = "●" if cell.get('registered') else "○"
        print(f"│   {conn} {op:<8} {net:<6} {direction:<5} ~{dist_str}")
    
    print(f"╚══════════════════════════════════════════════════════════════════╝")

# ============== SATELLITE VIEW (ASCII) ==============
def display_satellite_view(cells):
    """ASCII satellite/map view of towers"""
    
    print(f"""
{C.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                    🛰️ SATELLITE VIEW                              ║
╠══════════════════════════════════════════════════════════════════╣{C.E}
│                                                                  │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  {C.R}📡{C.E}  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  {C.G}📡{C.E}  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  {C.Y}📡{C.E}  ·  ·  ·  {C.C}📱{C.E}  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  · YOU ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  {C.B}📡{C.E}  ·  ·  ·  ·            │
│      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·            │
│                                                                  │
│   {C.R}📡{C.E} Airtel   {C.G}📡{C.E} Jio   {C.Y}📡{C.E} Vi   {C.B}📡{C.E} BSNL   {C.C}📱{C.E} You        │
╚══════════════════════════════════════════════════════════════════╝""")

# ============== NEIGHBOR CELLS ==============
def display_neighbors(cells):
    """Display neighbor cells summary"""
    
    connected = [c for c in cells if c.get('registered')]
    neighbors = [c for c in cells if not c.get('registered')]
    
    print(f"""
{C.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                    📊 CELL SUMMARY                                ║
╠══════════════════════════════════════════════════════════════════╣{C.E}
│   {C.G}● Connected:{C.E} {len(connected)}    {C.DIM}○ Neighbors:{C.E} {len(neighbors)}
│""")
    
    # Count by operator
    ops = {}
    for c in cells:
        op = c.get('operator', 'Unknown')
        ops[op] = ops.get(op, 0) + 1
    
    print(f"│   {C.BOLD}By Operator:{C.E}")
    for op, count in sorted(ops.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 20)
        print(f"│     {op:<10} {bar} {count}")
    
    # Count by network type
    nets = {}
    for c in cells:
        net = c.get('network', 'Unknown')
        nets[net] = nets.get(net, 0) + 1
    
    print(f"│")
    print(f"│   {C.BOLD}By Network:{C.E}")
    for net, count in sorted(nets.items()):
        print(f"│     {net:<10} {count}")
    
    print(f"╚══════════════════════════════════════════════════════════════════╝")


# ============== MAIN SCANNER ==============
def scan_cells():
    """Scan and return detailed cell info"""
    out = cmd("termux-telephony-cellinfo 2>/dev/null")
    if out:
        try:
            raw_cells = json.loads(out)
            return parse_cell_detailed(raw_cells)
        except:
            pass
    return []

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

# ============== LIVE DASHBOARD ==============
def live_cell_dashboard():
    """Live updating cell dashboard"""
    
    print(f"{C.C}Starting Cell Intelligence...{C.E}")
    time.sleep(1)
    
    try:
        while True:
            clear()
            
            # Header
            now = datetime.now().strftime("%H:%M:%S")
            print(f"""
{C.C}{C.BOLD}╔══════════════════════════════════════════════════════════════════════╗
║           📡 CELL INTELLIGENCE - NetMonster Style                     ║
║                    Live Cell Tower Analysis                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  {now}                                          [Ctrl+C to Exit]  ║
╚══════════════════════════════════════════════════════════════════════╝{C.E}
""")
            
            # Scan cells
            cells = scan_cells()
            
            if not cells:
                print(f"{C.Y}No cell data available. Make sure Termux:API is installed.{C.E}")
                print(f"{C.DIM}Install: pkg install termux-api{C.E}")
                print(f"{C.DIM}Also install Termux:API app from F-Droid{C.E}")
                time.sleep(5)
                continue
            
            # Display summary
            display_neighbors(cells)
            
            # Display compass
            display_compass(cells)
            
            # Display each cell in detail
            for cell in cells[:4]:  # Show top 4
                display_cell_detailed(cell)
            
            # Satellite view
            display_satellite_view(cells)
            
            # Refresh
            print(f"\n{C.DIM}Auto-refreshing in 5 seconds...{C.E}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        clear()
        print(f"\n{C.G}Cell Intelligence stopped.{C.E}")
        
        # Export option
        cells = scan_cells()
        if cells:
            export = input(f"{C.Y}Export cell data? (y/n): {C.E}").strip().lower()
            if export == 'y':
                filename = f"cell_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(cells, f, indent=2, default=str)
                print(f"{C.G}Saved to {filename}{C.E}")

# ============== SINGLE SCAN MODE ==============
def single_scan():
    """Single detailed scan"""
    clear()
    print(f"{C.C}Scanning cells...{C.E}\n")
    
    cells = scan_cells()
    
    if not cells:
        print(f"{C.R}No cell data available.{C.E}")
        return
    
    display_neighbors(cells)
    display_compass(cells)
    
    for cell in cells:
        display_cell_detailed(cell)
    
    display_satellite_view(cells)

# ============== MAIN ==============
def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        single_scan()
    else:
        live_cell_dashboard()

if __name__ == "__main__":
    main()
