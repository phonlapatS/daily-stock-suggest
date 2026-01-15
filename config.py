
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

ASSET_GROUPS = {
    "GROUP_A_THAI": {
        "description": "Thai Market (SET100+)",
        "interval": Interval.in_daily,
        "history_bars": 3000,
        "assets": [{'symbol': s, 'exchange': 'SET'} for s in THAI_STOCKS]
    },
    "GROUP_B_US": {
        "description": "US Market (NASDAQ)",
        "interval": Interval.in_daily,
        "history_bars": 3000,
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
    }
}
