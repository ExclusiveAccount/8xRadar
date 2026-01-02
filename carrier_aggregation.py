#!/usr/bin/env python3
"""
📡 CARRIER AGGREGATION ANALYZER
2CC, 3CC, 4CC, 5CC Detection with Band Combinations
LTE-A / LTE-A Pro / 5G NR CA Analysis
"""

import subprocess
import json
import os
import time
from datetime import datetime

# ============== COLORS ==============
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
    BOLD = '\033[1m'; DIM = '\033[2m'; E = '\033[0m'

# ============== INDIA LTE BANDS ==============
LTE_BANDS_INDIA = {
    1:  {"freq": 2100, "bw": [5,10,15,20], "type": "FDD", "ops": ["Airtel","Vi"], "name": "B1"},
    3:  {"freq": 1800, "bw": [5,10,15,20], "type": "FDD", "ops": ["Jio","Airtel","Vi"], "name": "B3"},
    5:  {"freq": 850,  "bw": [5,10], "type": "FDD", "ops": ["Jio"], "name": "B5"},
    8:  {"freq": 900,  "bw": [5,10], "type": "FDD", "ops": ["Airtel","Vi"], "name": "B8"},
    40: {"freq": 2300, "bw": [5,10,15,20], "type": "TDD", "ops": ["Airtel","Jio"], "name": "B40"},
    41: {"freq": 2500, "bw": [5,10,15,20], "type": "TDD", "ops": ["Jio"], "name": "B41"},
}

# ============== 5G NR BANDS INDIA ==============
NR_BANDS_INDIA = {
    "n1":  {"freq": 2100, "bw": [5,10,15,20], "type": "FDD", "ops": ["Airtel","Vi"]},
    "n3":  {"freq": 1800, "bw": [5,10,15,20], "type": "FDD", "ops": ["Jio","Airtel"]},
    "n5":  {"freq": 850,  "bw": [5,10], "type": "FDD", "ops": ["Jio"]},
    "n8":  {"freq": 900,  "bw": [5,10], "type": "FDD", "ops": ["Airtel","Vi"]},
    "n28": {"freq": 700,  "bw": [5,10,15,20], "type": "FDD", "ops": ["Jio","Airtel"]},
    "n40": {"freq": 2300, "bw": [20,40], "type": "TDD", "ops": ["Airtel"]},
    "n41": {"freq": 2500, "bw": [20,40,50,80,100], "type": "TDD", "ops": ["Jio"]},
    "n77": {"freq": 3700, "bw": [20,40,50,80,100], "type": "TDD", "ops": ["Airtel","Jio","Vi"]},
    "n78": {"freq": 3500, "bw": [20,40,50,80,100], "type": "TDD", "ops": ["Airtel","Jio","Vi"]},
    "n258":{"freq": 26000,"bw": [50,100,200,400], "type": "TDD", "ops": ["Jio"]},  # mmWave
}

# ============== COMMON CA COMBINATIONS INDIA ==============
CA_COMBINATIONS = {
    # Jio CA Combos
    "Jio": {
        "2CC": [
            {"combo": "B3+B40", "max_bw": "20+20=40MHz", "speed": "~300 Mbps"},
            {"combo": "B3+B41", "max_bw": "20+20=40MHz", "speed": "~300 Mbps"},
            {"combo": "B5+B40", "max_bw": "10+20=30MHz", "speed": "~225 Mbps"},
            {"combo": "B40+B41", "max_bw": "20+20=40MHz", "speed": "~300 Mbps"},
        ],
        "3CC": [
            {"combo": "B3+B40+B41", "max_bw": "20+20+20=60MHz", "speed": "~450 Mbps"},
            {"combo": "B5+B40+B41", "max_bw": "10+20+20=50MHz", "speed": "~375 Mbps"},
        ],
        "4CC": [
            {"combo": "B3+B5+B40+B41", "max_bw": "20+10+20+20=70MHz", "speed": "~525 Mbps"},
        ],
        "5G_NSA": [
            {"combo": "B3+n78", "max_bw": "20+100=120MHz", "speed": "~1.5 Gbps"},
            {"combo": "B40+n78", "max_bw": "20+100=120MHz", "speed": "~1.5 Gbps"},
            {"combo": "B3+B40+n78", "max_bw": "20+20+100=140MHz", "speed": "~1.8 Gbps"},
        ],
    },
    # Airtel CA Combos
    "Airtel": {
        "2CC": [
            {"combo": "B1+B3", "max_bw": "10+20=30MHz", "speed": "~225 Mbps"},
            {"combo": "B3+B40", "max_bw": "20+20=40MHz", "speed": "~300 Mbps"},
            {"combo": "B1+B40", "max_bw": "10+20=30MHz", "speed": "~225 Mbps"},
            {"combo": "B3+B8", "max_bw": "20+10=30MHz", "speed": "~225 Mbps"},
        ],
        "3CC": [
            {"combo": "B1+B3+B40", "max_bw": "10+20+20=50MHz", "speed": "~375 Mbps"},
            {"combo": "B3+B8+B40", "max_bw": "20+10+20=50MHz", "speed": "~375 Mbps"},
        ],
        "5G_NSA": [
            {"combo": "B3+n78", "max_bw": "20+100=120MHz", "speed": "~1.5 Gbps"},
            {"combo": "B1+n78", "max_bw": "10+100=110MHz", "speed": "~1.4 Gbps"},
            {"combo": "B1+B3+n78", "max_bw": "10+20+100=130MHz", "speed": "~1.6 Gbps"},
        ],
    },
    # Vi CA Combos
    "Vi": {
        "2CC": [
            {"combo": "B1+B3", "max_bw": "10+20=30MHz", "speed": "~225 Mbps"},
            {"combo": "B3+B8", "max_bw": "20+10=30MHz", "speed": "~225 Mbps"},
        ],
        "3CC": [
            {"combo": "B1+B3+B8", "max_bw": "10+20+10=40MHz", "speed": "~300 Mbps"},
        ],
        "5G_NSA": [
            {"combo": "B3+n78", "max_bw": "20+100=120MHz", "speed": "~1.5 Gbps"},
        ],
    },
}

def cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except:
        return ""

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


# ============== EARFCN TO BAND MAPPING ==============
def earfcn_to_band(earfcn):
    """Convert EARFCN to band number and frequency"""
    bands = [
        (0, 599, 1, 2100, "FDD"),
        (600, 1199, 2, 1900, "FDD"),
        (1200, 1949, 3, 1800, "FDD"),
        (1950, 2399, 4, 1700, "FDD"),
        (2400, 2649, 5, 850, "FDD"),
        (2650, 2749, 6, 800, "FDD"),
        (2750, 3449, 7, 2600, "FDD"),
        (3450, 3799, 8, 900, "FDD"),
        (6150, 6449, 20, 800, "FDD"),
        (36200, 36349, 33, 1900, "TDD"),
        (36350, 36949, 34, 2000, "TDD"),
        (36950, 37549, 35, 1900, "TDD"),
        (37550, 37749, 36, 1900, "TDD"),
        (37750, 38249, 37, 1900, "TDD"),
        (38250, 38649, 38, 2600, "TDD"),
        (38650, 39649, 39, 1900, "TDD"),
        (39650, 41589, 40, 2300, "TDD"),
        (41590, 43589, 41, 2500, "TDD"),
        (43590, 45589, 42, 3500, "TDD"),
        (45590, 46589, 43, 3700, "TDD"),
    ]
    
    for start, end, band, freq, duplex in bands:
        if start <= earfcn <= end:
            return {"band": band, "freq": freq, "duplex": duplex, "earfcn": earfcn}
    
    return {"band": None, "freq": None, "duplex": None, "earfcn": earfcn}

def nrarfcn_to_band(nrarfcn):
    """Convert NR-ARFCN to band"""
    bands = [
        (422000, 434000, "n1", 2100),
        (361000, 376000, "n3", 1800),
        (173800, 178800, "n5", 850),
        (185000, 192000, "n8", 900),
        (151600, 160600, "n28", 700),
        (460000, 480000, "n40", 2300),
        (499200, 537999, "n41", 2500),
        (620000, 653333, "n77", 3700),
        (620000, 653333, "n78", 3500),
        (2054166, 2104165, "n258", 26000),
    ]
    
    for start, end, band, freq in bands:
        if start <= nrarfcn <= end:
            return {"band": band, "freq": freq, "nrarfcn": nrarfcn}
    
    return {"band": None, "freq": None, "nrarfcn": nrarfcn}

# ============== BANDWIDTH CALCULATION ==============
def calculate_bandwidth(earfcn, nrb=None):
    """Calculate bandwidth from number of resource blocks"""
    # NRB to BW mapping
    nrb_bw = {
        6: 1.4, 15: 3, 25: 5, 50: 10, 75: 15, 100: 20
    }
    
    if nrb and nrb in nrb_bw:
        return nrb_bw[nrb]
    
    return None

# ============== CA DETECTION ==============
def detect_carrier_aggregation(cells):
    """Detect Carrier Aggregation from cell data"""
    
    ca_info = {
        'active': False,
        'type': None,  # 2CC, 3CC, 4CC, 5CC
        'pcell': None,  # Primary Cell
        'scells': [],   # Secondary Cells
        'total_bandwidth': 0,
        'bands': [],
        'max_speed': 0,
        'nr_nsa': False,  # 5G NSA mode
        'nr_sa': False,   # 5G SA mode
    }
    
    lte_cells = []
    nr_cells = []
    
    for cell in cells:
        cell_type = cell.get('type', '').lower()
        
        if 'lte' in cell_type:
            earfcn = cell.get('earfcn', 0)
            band_info = earfcn_to_band(earfcn)
            
            cell_info = {
                'type': 'LTE',
                'earfcn': earfcn,
                'band': band_info.get('band'),
                'freq': band_info.get('freq'),
                'duplex': band_info.get('duplex'),
                'pci': cell.get('pci'),
                'rsrp': cell.get('rsrp'),
                'rsrq': cell.get('rsrq'),
                'registered': cell.get('registered', False),
                'bandwidth': cell.get('bandwidth'),
            }
            lte_cells.append(cell_info)
            
        elif 'nr' in cell_type or '5g' in cell_type:
            nrarfcn = cell.get('nrarfcn', 0)
            band_info = nrarfcn_to_band(nrarfcn)
            
            cell_info = {
                'type': 'NR',
                'nrarfcn': nrarfcn,
                'band': band_info.get('band'),
                'freq': band_info.get('freq'),
                'pci': cell.get('pci'),
                'ss_rsrp': cell.get('ssRsrp') or cell.get('csiRsrp'),
                'ss_rsrq': cell.get('ssRsrq') or cell.get('csiRsrq'),
                'registered': cell.get('registered', False),
            }
            nr_cells.append(cell_info)
    
    # Identify PCell and SCells
    pcell = None
    scells = []
    
    for cell in lte_cells:
        if cell['registered']:
            pcell = cell
        else:
            scells.append(cell)
    
    ca_info['pcell'] = pcell
    ca_info['scells'] = scells
    
    # Count carriers
    total_carriers = 1 if pcell else 0
    total_carriers += len(scells)
    
    if nr_cells:
        total_carriers += len(nr_cells)
        ca_info['nr_nsa'] = True if pcell else False
        ca_info['nr_sa'] = True if not pcell and nr_cells else False
    
    # Determine CA type
    if total_carriers >= 2:
        ca_info['active'] = True
        if total_carriers == 2:
            ca_info['type'] = '2CC'
        elif total_carriers == 3:
            ca_info['type'] = '3CC'
        elif total_carriers == 4:
            ca_info['type'] = '4CC'
        elif total_carriers >= 5:
            ca_info['type'] = '5CC+'
    
    # Collect bands
    bands = []
    if pcell and pcell['band']:
        bands.append(f"B{pcell['band']}")
    for sc in scells:
        if sc['band']:
            bands.append(f"B{sc['band']}")
    for nr in nr_cells:
        if nr['band']:
            bands.append(nr['band'])
    
    ca_info['bands'] = bands
    
    # Estimate bandwidth and speed
    total_bw = 0
    for cell in lte_cells:
        bw = cell.get('bandwidth') or 20  # Assume 20MHz if unknown
        total_bw += bw
    for cell in nr_cells:
        total_bw += 100  # Assume 100MHz for NR
    
    ca_info['total_bandwidth'] = total_bw
    ca_info['max_speed'] = total_bw * 7.5  # Rough estimate: 7.5 Mbps per MHz
    
    ca_info['lte_cells'] = lte_cells
    ca_info['nr_cells'] = nr_cells
    
    return ca_info
