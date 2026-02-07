
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
        "assets": [{'symbol': s, 'exchange': 'NASDAQ'} for s in NASDAQ_STOCKS],
        "fixed_threshold": 0.6 # Mentor suggestion
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
        "fixed_threshold": 0.10  # Backtest: 90 trades, RR 1.74
    },
    "GROUP_C2_GOLD_15M": {
        "description": "Gold Intraday 15min",
        "interval": Interval.in_15_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAUUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.10  # Backtest: 108 trades, RR 0.96
    },
    
    # SILVER (XAGUSD) - Different optimal thresholds per TF
    "GROUP_D1_SILVER_30M": {
        "description": "Silver Intraday 30min",
        "interval": Interval.in_30_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAGUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.15  # Backtest: 34 trades, Acc 61.8%, RR 1.01
    },
    "GROUP_D2_SILVER_15M": {
        "description": "Silver Intraday 15min",
        "interval": Interval.in_15_minute,
        "history_bars": 5000,
        "assets": [{'symbol': 'XAGUSD', 'exchange': 'OANDA'}],
        "fixed_threshold": 0.20  # Backtest: 53 trades, RR 1.42
    },
    "GROUP_E_CHINA_ADR": {
        "description": "China ADRs (Alibaba, JD, Pinduoduo)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': 'BABA', 'exchange': 'NYSE', 'name': 'ALIBABA'},
            {'symbol': 'JD', 'exchange': 'NASDAQ', 'name': 'JD-COM'},
            {'symbol': 'PDD', 'exchange': 'NASDAQ', 'name': 'PINDUODUO'},
            {'symbol': 'BIDU', 'exchange': 'NASDAQ', 'name': 'BAIDU'},
            {'symbol': 'NIO', 'exchange': 'NYSE', 'name': 'NIO'}
        ],
        "fixed_threshold": 1.2  # Scaled for high volatility (Avg Daily Move ~1.8%)
    },
    "GROUP_F_CHINA_A": {
        "description": "China A-Shares (Moutai, Ping An, CATL)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '600519', 'exchange': 'SH', 'name': 'MOUTAI'},
            {'symbol': '601318', 'exchange': 'SH', 'name': 'PINGAN'},
            {'symbol': '000858', 'exchange': 'SZ', 'name': 'WULIANG'},
            {'symbol': '300750', 'exchange': 'SZ', 'name': 'CATL'},
            {'symbol': '002594', 'exchange': 'SZ', 'name': 'BYD-SZ'}
        ],
        "fixed_threshold": 1.2  # Scaled for high volatility
    },
    "GROUP_G_HK_TECH": {
        "description": "Hong Kong Tech (Tencent, Meituan)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '700', 'exchange': 'HK', 'name': 'TENCENT'},
            {'symbol': '9988', 'exchange': 'HK', 'name': 'ALIBABA'},
            {'symbol': '3690', 'exchange': 'HK', 'name': 'MEITUAN'},
            {'symbol': '1810', 'exchange': 'HK', 'name': 'XIAOMI'},
            {'symbol': '9618', 'exchange': 'HK', 'name': 'JD-COM'}
        ],
        "fixed_threshold": 0.6  # Standard international threshold
    },
    "GROUP_H_TAIWAN": {
        "description": "Taiwan Stocks (TSMC, MediaTek)",
        "interval": Interval.in_daily,
        "history_bars": 5000,
        "assets": [
            {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'},
            {'symbol': '2454', 'exchange': 'TWSE', 'name': 'MEDIATEK'},
            {'symbol': '2317', 'exchange': 'TWSE', 'name': 'FOXCONN'},
            {'symbol': '2308', 'exchange': 'TWSE', 'name': 'DELTA'},
            {'symbol': '2303', 'exchange': 'TWSE', 'name': 'UMC'}
        ],
        "fixed_threshold": 1.0  # OPTIMAL: High threshold filters noise effectively
    }
}
