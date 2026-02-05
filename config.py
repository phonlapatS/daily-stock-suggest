
"""
config.py - Fractal N+1 Prediction Configuration
================================================
Defines asset groups, timeframes, and analysis parameters.
"""
from tvDatafeed import Interval

# ==========================================
# 1. System Settings
# ==========================================
RESULTS_LOG = "data/fractal_results.log"
FRACTAL_WINDOW = 14       # Pattern length (candles)
MIN_CORRELATION = 0.80    # Minimum similarity score (Pearson)
TOP_MATCHES = 10          # Number of historical matches to analyze
VOLATILITY_WINDOW = 20    # Rolling window for Volatility analysis

# ==========================================
# 2. Asset Groups
# ==========================================

def load_symbols(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        return []

THAI_STOCKS = load_symbols("data/thai_set100.txt")
NASDAQ_STOCKS = load_symbols("data/nasdaq_stocks.txt")

CHINA_ADR_STOCKS = [
    {'symbol': 'BABA', 'exchange': 'NYSE', 'name': 'ALIBABA'},
    {'symbol': 'JD', 'exchange': 'NASDAQ', 'name': 'JD-COM'},
    {'symbol': 'PDD', 'exchange': 'NASDAQ', 'name': 'PINDUODUO'},
    {'symbol': 'BIDU', 'exchange': 'NASDAQ', 'name': 'BAIDU'},
    {'symbol': 'NIO', 'exchange': 'NYSE', 'name': 'NIO'},
    {'symbol': 'XPEV', 'exchange': 'NYSE', 'name': 'XPENG'},
    {'symbol': 'LI', 'exchange': 'NASDAQ', 'name': 'LI-AUTO'},
    {'symbol': 'BILI', 'exchange': 'NASDAQ', 'name': 'BILIBILI'},
    {'symbol': 'TCOM', 'exchange': 'NASDAQ', 'name': 'TRIP-COM'},
    {'symbol': 'IQ', 'exchange': 'NASDAQ', 'name': 'IQIYI'},
    {'symbol': 'ZTO', 'exchange': 'NYSE', 'name': 'ZTO-EXP'},
    {'symbol': 'BEKE', 'exchange': 'NYSE', 'name': 'KE-HOLDINGS'},
    {'symbol': 'TCEHY', 'exchange': 'OTC', 'name': 'TENCENT-ADR'}
]

CHINA_ECONOMY_STOCKS = [
    # Large Cap ADRs (Economy / Consumer) - Replacing ETFs
    {'symbol': 'YUMC', 'exchange': 'NYSE'},    # Yum China (KFC/Pizza Hut China)
    {'symbol': 'HTHT', 'exchange': 'NASDAQ'},  # H World Group (Hotels)
    {'symbol': 'EDU', 'exchange': 'NYSE'},     # New Oriental Education
    {'symbol': 'TAL', 'exchange': 'NYSE'},     # TAL Education
    {'symbol': 'ZTO', 'exchange': 'NYSE'}      # ZTO Express (Logistics)
]

MARKET_INDICES = [
    {'symbol': 'SET', 'exchange': 'SET'},
    {'symbol': 'SET50', 'exchange': 'SET'},
    {'symbol': 'SET100', 'exchange': 'SET'},
    {'symbol': 'NDX', 'exchange': 'TVC'},      # NASDAQ 100
    {'symbol': 'SPX', 'exchange': 'TVC'},      # S&P 500
    {'symbol': 'DJI', 'exchange': 'TVC'},      # Dow Jones
    {'symbol': 'HSI', 'exchange': 'TVC'},      # Hang Seng
    {'symbol': 'SSEC', 'exchange': 'TVC'},     # Shanghai Composite
    {'symbol': 'NI225', 'exchange': 'TVC'}     # Nikkei 225
]

ASSET_GROUPS = {
    "GROUP_A_THAI": {
        "description": "Thai Market (SET100+)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [{'symbol': s, 'exchange': 'SET'} for s in THAI_STOCKS]
    },
    "GROUP_B_US": {
        "description": "US Market (NASDAQ)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [{'symbol': s, 'exchange': 'NASDAQ'} for s in NASDAQ_STOCKS]
    },
    "GROUP_C_METALS": {
        "description": "Intraday Metals (Gold/Silver)",
        "interval": Interval.in_30_minute,
        "history_bars": 5000,
        "assets": [
            {'symbol': 'XAUUSD', 'exchange': 'OANDA'}, 
            {'symbol': 'XAGUSD', 'exchange': 'OANDA'}
        ]
    },
    "GROUP_D_METALS_15M": {
        "description": "Intraday Metals 15min (Gold/Silver)",
        "interval": Interval.in_15_minute,
        "history_bars": 5000,  # ~2.5 เดือน
        "assets": [
            {'symbol': 'XAUUSD', 'exchange': 'OANDA'}, 
            {'symbol': 'XAGUSD', 'exchange': 'OANDA'}
        ]
    },
    "GROUP_E_CHINA_ADR": {
        "description": "China ADRs (US Market)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": CHINA_ADR_STOCKS + CHINA_ECONOMY_STOCKS
    },
    "GROUP_F_CHINA_A": {
        "description": "China A-Shares (Shanghai/Shenzhen)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '600519', 'exchange': 'SSE', 'name': 'MOUTAI'},     # Kweichow Moutai
            {'symbol': '601318', 'exchange': 'SSE', 'name': 'PINGAN'},     # Ping An Insurance
            {'symbol': '000858', 'exchange': 'SZSE', 'name': 'WULIANG'},    # Wuliangye Yibin
            {'symbol': '300750', 'exchange': 'SZSE', 'name': 'CATL'},       # CATL
            {'symbol': '002594', 'exchange': 'SZSE', 'name': 'BYD-SZ'},     # BYD (SZ)
            {'symbol': '600036', 'exchange': 'SSE', 'name': 'CM-BANK'},    # China Merchants Bank
        ]
    },
    "GROUP_G_HK_TECH": {
        "description": "Hong Kong Tech (HKEX)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '700', 'exchange': 'HKEX', 'name': 'TENCENT'},      # Tencent
            {'symbol': '9988', 'exchange': 'HKEX', 'name': 'ALIBABA'},     # Alibaba
            {'symbol': '3690', 'exchange': 'HKEX', 'name': 'MEITUAN'},     # Meituan
            {'symbol': '1810', 'exchange': 'HKEX', 'name': 'XIAOMI'},      # Xiaomi
            {'symbol': '9618', 'exchange': 'HKEX', 'name': 'JD-COM'},      # JD.com
            {'symbol': '1211', 'exchange': 'HKEX', 'name': 'BYD-HK'},      # BYD (HK)
        ]
    },
    "GROUP_H_TAIWAN": {
        "description": "Taiwan Semiconductor (TWSE)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'},        # TSMC
            {'symbol': '2454', 'exchange': 'TWSE', 'name': 'MEDIATEK'},    # MediaTek
            {'symbol': '2317', 'exchange': 'TWSE', 'name': 'FOXCONN'},     # Hon Hai
            {'symbol': '2308', 'exchange': 'TWSE', 'name': 'DELTA'},       # Delta Electronics
            {'symbol': '2303', 'exchange': 'TWSE', 'name': 'UMC'},         # UMC
        ]
    }
}
