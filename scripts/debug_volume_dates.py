import pandas as pd
import os
import glob

# Paths
CACHE_DIR = "e:/PredictPlus1/data/cache"
LOG_DIR = "e:/PredictPlus1/logs"

def debug_symbol(symbol, log_file, cache_file_pattern):
    print(f"--- Debugging {symbol} ---")
    
    # Load Cache
    cache_files = glob.glob(os.path.join(CACHE_DIR, cache_file_pattern))
    if not cache_files:
        print(f"Cache file not found for {cache_file_pattern}")
        return
    
    cache_path = cache_files[0]
    print(f"Cache File: {cache_path}")
    cache_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    cache_df.index = cache_df.index.normalize()
    print("Cache Index Sample:")
    print(cache_df.index[:5])
    print(f"Cache Index Dtype: {cache_df.index.dtype}")
    
    # Load Trade Log
    log_path = os.path.join(LOG_DIR, log_file)
    if not os.path.exists(log_path):
        print(f"Log file {log_path} not found")
        return
        
    print(f"Log File: {log_path}")
    log_df = pd.read_csv(log_path, on_bad_lines='skip')
    symbol_log = log_df[log_df['symbol'] == symbol]
    
    if symbol_log.empty:
        print(f"No trades found for {symbol} in log")
        return
        
    print(f"Found {len(symbol_log)} trades for {symbol}")
    
    # Check matching
    match_count = 0
    for idx, row in symbol_log.head(5).iterrows():
        raw_date = row['date']
        trade_date = pd.to_datetime(raw_date).normalize()
        print(f"Trade Date Raw: {raw_date} -> Normalized: {trade_date}")
        
        if trade_date in cache_df.index:
            print(f"  [MATCH] Found in cache")
            match_count += 1
        else:
            print(f"  [MISS] Not in cache")
            # Check nearby
            # print(f"  Cache info around this date:")
            # try:
            #     loc = cache_df.index.get_loc(trade_date, method='nearest')
            #     print(f"    Nearest: {cache_df.index[loc]}")
            # except:
            #     print("    (Lookup failed)")

    print(f"Total Matches in sample: {match_count}")

# Debug AMD (US)
debug_symbol("AMD", "trade_history_US.csv", "NASDAQ_AMD.csv")

# Debug ADVANC (Thai)
debug_symbol("ADVANC", "trade_history_THAI.csv", "SET_ADVANC.csv")
