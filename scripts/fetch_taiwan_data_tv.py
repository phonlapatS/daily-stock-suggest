import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_fetcher import StockDataFetcher
import pandas as pd
import os
import time

# Params
CACHE_DIR = "e:/PredictPlus1/data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Symbol Map (Internal -> TV Exchange)
# Taiwan Stocks (TWSE)
TAIWAN_SYMBOLS = [
    '2330', # TSMC
    '2454', # MediaTek
    '2317', # Hon Hai
    '2303', # UMC
    '2308', # Delta
    '2382', # Quanta
    '3711', # ASE
    '3008', # Largan
    '2357', # Asustek
    '2395'  # Advantech
]

# Metals (OANDA)
METALS = ['XAUUSD', 'XAGUSD']

def fetch_and_save(symbol, exchange, prefix):
    print(f"📥 Fetching {symbol} from {exchange}...")
    try:
        fetcher = StockDataFetcher()
        # Download 5000 bars (approx 20 years daily)
        df = fetcher.fetch_daily_data(symbol, exchange, n_bars=5000)
        
        if df is None or df.empty:
            print(f"❌ No data for {symbol}")
            return

        # Save to cache pattern: {EXCHANGE}_{SYMBOL}.csv
        # System expects: TWSE_2330.csv, OANDA_XAUUSD.csv
        # But wait, config says:
        # "assets": [{'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'}]
        # In calculate_metrics.py: 
        # cache_file = os.path.join(CACHE_DIR, f"{exchange}_{symbol}.csv")
        # So we must use the EXCHANGE name from Config.
        
        filename = f"{prefix}_{symbol}.csv"
        filepath = os.path.join(CACHE_DIR, filename)
        
        # Ensure datetime is index and column
        if 'datetime' not in df.columns:
            df['datetime'] = df.index
            
        df.to_csv(filepath)
        print(f"✅ Saved to {filename} ({len(df)} rows)")
        time.sleep(1) # Rate limit friendly
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Run Taiwan
print("--- Fetching Taiwan Stocks (TWSE) ---")
for sym in TAIWAN_SYMBOLS:
    fetch_and_save(sym, 'TWSE', prefix="TWSE")

# Run Metals
print("\n--- Fetching Metals (OANDA) ---")
for sym in METALS:
    fetch_and_save(sym, 'OANDA', prefix="OANDA")

# Run Metals Intraday (for checking) - usually 15m/30m
print("\n--- Fetching Metals Intraday (30m) ---")
for sym in METALS:
    try:
        fetcher = StockDataFetcher()
        df = fetcher.fetch_intraday_data(sym, 'OANDA', interval='30', n_bars=5000)
        if df is not None:
             filename = f"OANDA_{sym}_30m.csv"
             filepath = os.path.join(CACHE_DIR, filename)
             df.to_csv(filepath)
             print(f"✅ Saved {filename}")
    except Exception as e:
        print(f"❌ Error Intraday: {e}")
