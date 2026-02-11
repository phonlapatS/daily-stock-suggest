
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
        "assets": [{'symbol': s, 'exchange': 'SET'} for s in THAI_STOCKS],
        "engine": "MEAN_REVERSION",
        "min_threshold": 0.01   # 1.0% floor for Thai stocks
    },
    "GROUP_B_US": {
        "description": "US Market (NASDAQ)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [{'symbol': s, 'exchange': 'NASDAQ'} for s in NASDAQ_STOCKS],
        "fixed_threshold": None, # Use Dynamic Base
        "engine": "TREND_MOMENTUM",
        "min_threshold": 0.005,  # Optimized to 0.5%
        "min_adx": 20            # Standard Trend Strength
    },
    # ==========================================
    # METALS - Split by Asset for Optimized Thresholds
    # (Based on Backtest Analysis: 5000 bars per TF)
    # ==========================================
    
    # GOLD (XAUUSD) - Optimal: 0.10% for both timeframes
    "GROUP_C1_GOLD_30M": {
        "description": "Gold Intraday 30min",
        "interval": Interval.in_30_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAUUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.10,  # Backtest: 90 trades, RR 1.74
        "engine": "MEAN_REVERSION"
    },
    "GROUP_C2_GOLD_15M": {
        "description": "Gold Intraday 15min",
        "interval": Interval.in_15_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAUUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.10,  # Backtest: 108 trades, RR 0.96
        "engine": "MEAN_REVERSION"
    },
    
    # SILVER (XAGUSD) - Different optimal thresholds per TF
    "GROUP_D1_SILVER_30M": {
        "description": "Silver Intraday 30min",
        "interval": Interval.in_30_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAGUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.15,  # Backtest: 34 trades, Acc 61.8%, RR 1.01
        "engine": "MEAN_REVERSION"
    },
    "GROUP_D2_SILVER_15M": {
        "description": "Silver Intraday 15min",
        "interval": Interval.in_15_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAGUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.20,  # Backtest: 53 trades, RR 1.42
        "engine": "MEAN_REVERSION"
    },
    "GROUP_C_CHINA_HK": {
        "description": "China & HK Tech (HKEX)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '700', 'exchange': 'HKEX', 'name': 'TENCENT'},
            {'symbol': '9988', 'exchange': 'HKEX', 'name': 'ALIBABA'},
            {'symbol': '3690', 'exchange': 'HKEX', 'name': 'MEITUAN'},
            {'symbol': '1810', 'exchange': 'HKEX', 'name': 'XIAOMI'},
            {'symbol': '9888', 'exchange': 'HKEX', 'name': 'BAIDU'},
            {'symbol': '9618', 'exchange': 'HKEX', 'name': 'JD-COM'},
            {'symbol': '1211', 'exchange': 'HKEX', 'name': 'BYD'},
            {'symbol': '2015', 'exchange': 'HKEX', 'name': 'LI-AUTO'},
            {'symbol': '9868', 'exchange': 'HKEX', 'name': 'XPENG'},
            {'symbol': '9866', 'exchange': 'HKEX', 'name': 'NIO'},
            {'symbol': '0981', 'exchange': 'HKEX', 'name': 'SMIC'}
        ],
        "fixed_threshold": None, 
        "engine": "MEAN_REVERSION", # V4.4: Switched from TREND to REVERSION (data-driven)
        "min_threshold": 0.005  # Optimized to 0.5%
    },
    "GROUP_D_TAIWAN": {
        "description": "Taiwan Semicon (TWSE)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'},
            {'symbol': '2454', 'exchange': 'TWSE', 'name': 'MEDIATEK'},
            {'symbol': '2317', 'exchange': 'TWSE', 'name': 'HON-HAI'},
            {'symbol': '2303', 'exchange': 'TWSE', 'name': 'UMC'},
            {'symbol': '2308', 'exchange': 'TWSE', 'name': 'DELTA'},
            {'symbol': '2382', 'exchange': 'TWSE', 'name': 'QUANTA'},
            {'symbol': '3711', 'exchange': 'TWSE', 'name': 'ASE'},
            {'symbol': '3008', 'exchange': 'TWSE', 'name': 'LARGAN'},
            {'symbol': '2357', 'exchange': 'TWSE', 'name': 'ASUSTEK'},
            {'symbol': '2395', 'exchange': 'TWSE', 'name': 'ADVANTECH'}
        ],
        "fixed_threshold": None,
        "engine": "TREND_MOMENTUM",
        "min_threshold": 0.005, # Optimized to 0.5% (was 1.0%)
        "min_adx": 20           # Standard ADX
    }
}
