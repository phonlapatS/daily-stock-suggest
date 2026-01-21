
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
    {'symbol': 'BABA', 'exchange': 'NYSE'},
    {'symbol': 'JD', 'exchange': 'NASDAQ'},
    {'symbol': 'PDD', 'exchange': 'NASDAQ'},
    {'symbol': 'BIDU', 'exchange': 'NASDAQ'},
    {'symbol': 'NIO', 'exchange': 'NYSE'},
    {'symbol': 'XPEV', 'exchange': 'NYSE'},
    {'symbol': 'LI', 'exchange': 'NASDAQ'},
    {'symbol': 'BILI', 'exchange': 'NASDAQ'},
    {'symbol': 'TCOM', 'exchange': 'NASDAQ'},
    {'symbol': 'IQ', 'exchange': 'NASDAQ'},
    {'symbol': 'ZTO', 'exchange': 'NYSE'},
    {'symbol': 'BEKE', 'exchange': 'NYSE'},
    {'symbol': 'TCEHY', 'exchange': 'OTC'}
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
    "GROUP_E_CHINA": {
        "description": "China Market (Tech & Economy)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": CHINA_ADR_STOCKS + CHINA_ECONOMY_STOCKS
    },
    # "GROUP_F_INDICES": {
    #     "description": "Market Indices (Global)",
    #     "interval": Interval.in_daily,
    #     "history_bars": 5000,
    #     "assets": MARKET_INDICES
    # }
}
