import pandas as pd
import os
import sys
import glob

# Mock Config / Paths
DATA_CACHE_DIR = "data/cache"
TRADE_LOG = "logs/trade_history.csv"

def load_cache_map():
    """Map Symbol -> Filepath"""
    files = glob.glob(os.path.join(DATA_CACHE_DIR, "*.csv"))
    cache_map = {}
    for f in files:
        # Expected: EXCHANGE_SYMBOL.csv or just SYMBOL.csv (loose match)
        basename = os.path.basename(f).replace(".csv", "")
        if "_" in basename:
            exchange, symbol = basename.split("_", 1)
            cache_map[symbol] = f
        else:
            cache_map[basename] = f
            
    print(f"📂 Loaded {len(cache_map)} cached symbols.")
    return cache_map

def get_rvol(symbol, trade_date, cache_map):
    """Calculate RVol for a specific date"""
    if symbol not in cache_map:
        return None
        
    try:
        # Optimization: Move load out of loop in production
        df = pd.read_csv(cache_map[symbol], index_col=0, parse_dates=True)
        
        # Normalize index to midnight to match trade dates
        df.index = df.index.normalize()
        
        if trade_date not in df.index:
            return None
            
        # Get location of trade date
        idx = df.index.get_loc(trade_date)
        
        # Calculate trailing 20-day avg volume (excluding today)
        # We need historical context
        if idx < 20: 
            return 1.0 # Not enough history
            
        # Volume series (upto yesterday)
        # Note: In backtest, signals are generated on CLOSE of the day.
        # So we compare Today's Volume vs Prev 20 Days Avg.
        
        vol_today = df.iloc[idx]['volume']
        
        # Calculate MA on previous 20 days (shift by 1 to exclude today for MA if needed, 
        # but for RVol we usually compare Today vs Avg(Past 20). 
        # If we use window ending yesterday: df.iloc[idx-20:idx] is correct (Python slice excludes end)
        
        vol_window = df.iloc[idx-20:idx]['volume']
        vol_ma = vol_window.mean()
        
        if vol_ma == 0 or pd.isna(vol_ma): return 0.0
        
        return vol_today / vol_ma
        
    except Exception as e:
        # print(f"Error {symbol} on {trade_date}: {e}")
        return None

def test_integration():
    print("🚀 Volume Integration Test")
    
    # 1. Load Trades
    if not os.path.exists(TRADE_LOG):
        print("❌ Trade log not found.")
        return
        
    df_trades = pd.read_csv(TRADE_LOG)
    df_trades['date'] = pd.to_datetime(df_trades['date'])
    
    print(f"📜 Loaded {len(df_trades)} trades.")
    
    # 2. Load Cache Map
    cache_map = load_cache_map()
    print("DEBUG: First 5 cache map keys:", list(cache_map.keys())[:5])
    
    # 3. Sample Check (First 100 trades)
    print("\n🔍 Sampling Verification:")
    successful_lookups = 0
    
    # Add RVol column
    results = []
    
    for i, row in df_trades.head(100).iterrows():
        symbol = str(row['symbol'])
        exchange = str(row['exchange']) # Try using exchange too
        date = row['date']
        
        # Adjust date format if needed (remove time)
        date_clean = date.normalize()
        
        if i < 5:
            print(f"DEBUG: Looking up Symbol='{symbol}' Exchange='{exchange}' Date='{date_clean}'")
        
        # Try finding key
        # Priority: EXCHANGE_SYMBOL or just SYMBOL
        key1 = f"{exchange}_{symbol}"
        key2 = symbol
        
        lookup_key = key1 if key1 in cache_map else key2
        
        rvol = get_rvol(lookup_key, date_clean, cache_map)
        
        if rvol is not None:
            successful_lookups += 1
            results.append({
                'Symbol': symbol,
                'Date': date_clean.date(),
                'RVol': round(rvol, 2),
                'Outcome': row['actual']
            })
            
    # Show Results
    print(f"\n✅ Successfully matched {successful_lookups}/100 trades.")
    
    if results:
        print("\n نمونه Example Data:")
        print(pd.DataFrame(results).head(10))
        
    # Validation
    if successful_lookups < 10:
        print("\n⚠️ WARNING: Low match rate. Check Symbol naming (700 vs HKEX_700) or Date formats.")
    else:
        print("\n✅ Integration Logic Validated. Ready to scale.")

if __name__ == "__main__":
    test_integration()
