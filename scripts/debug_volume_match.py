import pandas as pd
import os

LOG_DIR = "e:/PredictPlus1/logs"
CACHE_DIR = "e:/PredictPlus1/data/cache"

def check_match(market, symbol, log_file):
    print(f"\n--- Checking {market}: {symbol} ---")
    
    # Load Log
    log_path = os.path.join(LOG_DIR, log_file)
    if not os.path.exists(log_path):
        print(f"❌ Log not found: {log_path}")
        return
        
    df_log = pd.read_csv(log_path)
    df_log['date'] = pd.to_datetime(df_log['date'])
    
    # Filter for symbol
    symbol_log = df_log[df_log['symbol'] == symbol]
    if symbol_log.empty:
        print(f"❌ Symbol {symbol} not found in log")
        # Print valid symbols
        print(f"Valid symbols in log: {df_log['symbol'].unique()[:5]}...")
        return
        
    print(f"✅ Found {len(symbol_log)} trades in log")
    sample_date = symbol_log['date'].iloc[0]
    print(f"Sample Log Date: {sample_date} (Type: {type(sample_date)})")
    
    # Load Cache
    # Try finding the file
    cache_files = [f for f in os.listdir(CACHE_DIR) if symbol in f]
    if not cache_files:
        print(f"❌ No cache file found for {symbol}")
        return
        
    print(f"Found cache files: {cache_files}")
    cache_path = os.path.join(CACHE_DIR, cache_files[0])
    
    df_cache = pd.read_csv(cache_path)
    df_cache['datetime'] = pd.to_datetime(df_cache['datetime'])
    df_cache = df_cache.set_index('datetime')
    
    print(f"✅ Loaded cache: {len(df_cache)} rows")
    if not df_cache.empty:
        limit = min(5, len(df_cache))
        print(f"Sample Cache Dates: {df_cache.index[:limit]}")
        
    # check match
    # Log date is likely 00:00:00
    normalized_log_date = sample_date.normalize()
    
    if normalized_log_date in df_cache.index:
        print(f"✅ MATCH FOUND for {normalized_log_date}")
    else:
        print(f"❌ NO MATCH for {normalized_log_date}")
        # Show nearest
        # valid checks logic needs to handle this

# Check Taiwan
check_match("TAIWAN", "2330", "trade_history_TAIWAN.csv")

# Check Metals
check_match("METALS", "XAUUSD", "trade_history_METALS.csv")

# Check China
check_match("CHINA", "700", "trade_history_CHINA.csv")
