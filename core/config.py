"""
Configuration file for Stock Statistics Extraction System
Pure statistical analysis - No ML models
"""

# Analysis parameters
THRESHOLD_PERCENT = 1.0  # กรองเฉพาะวันที่มีการเปลี่ยนแปลง ±1% ขึ้นไป
MIN_STREAK_LENGTH = 4    # ความยาวขั้นต่ำของ streak ที่สนใจ

# Timeframe options
TIMEFRAMES = {
    'daily': 'D',
    '15min': '15',
    '30min': '30',
    '1hour': '60'
}

# Exchange mappings for tvdatafeed
EXCHANGES = {
    'thai': 'SET',
    'nasdaq': 'NASDAQ',
    'nyse': 'NYSE',
    'binance': 'BINANCE',
    'oanda': 'OANDA'  # for commodities like gold
}

# Default stocks to analyze
DEFAULT_STOCKS = {
    'thai': ['PTT', 'CPALL', 'AOT', 'KBANK', 'SCB'],
    'us': [
        {'symbol': 'AAPL', 'exchange': 'NASDAQ'},
        {'symbol': 'MSFT', 'exchange': 'NASDAQ'},
        {'symbol': 'GOOGL', 'exchange': 'NASDAQ'},
        {'symbol': 'TSLA', 'exchange': 'NASDAQ'},
    ]
}

# Data fetching parameters
DEFAULT_N_BARS = 5000  # จำนวน bars ที่จะดึง (ประมาณ 5-10 ปีสำหรับ daily)

# Output directories
DATA_DIR = 'data/'
RESULTS_DIR = 'results/'
PLOTS_DIR = 'plots/'

# Statistics classification thresholds
SIDEWAYS_THRESHOLD = 0.5  # ถือว่า sideways ถ้า % change < 0.5%
