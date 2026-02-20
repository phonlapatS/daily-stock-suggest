import pandas as pd
import numpy as np
import os

CACHE_DIR = "e:/PredictPlus1/data/cache"
LOG_FILE = "e:/PredictPlus1/logs/trade_history_THAI.csv"

price_cache = {}

def get_volume_data(symbol):
    if symbol in price_cache:
        return price_cache[symbol]
        
    # Try SET prefix
    path = os.path.join(CACHE_DIR, f"SET_{symbol}.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['datetime'] = df['datetime'].dt.normalize()
            df = df.set_index('datetime')
            df = df[~df.index.duplicated(keep='first')]
            price_cache[symbol] = df
            return df
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return None
    return None

def analyze_thai():
    print("🇹🇭 Starting Deep Dive Analysis for Thai Market...")
    
    # 1. Load Trade Logs (We need to filter for Thai trades from main log or use specific log)
    # Since we just ran backtest for GROUP_A_THAI, checks mainly trade_history.csv
    main_log = "e:/PredictPlus1/logs/trade_history_THAI.csv" 
    
    if not os.path.exists(main_log):
        print(f"❌ Log file not found at {main_log}")
        return

    df_trades = pd.read_csv(main_log)
    
    # Filter for Thai stocks (Exchange = SET)
    df_trades = df_trades[df_trades['exchange'] == 'SET'].copy()
    
    if df_trades.empty:
        print("❌ No SET trades found.")
        return

    print(f"Loaded {len(df_trades)} Thai trades.")
    
    # 2. Add RVol Column
    df_trades['rvol'] = np.nan
    
    for idx, row in df_trades.iterrows():
        symbol = row['symbol']
        entry_date = pd.to_datetime(row['date']).normalize()
        
        df_price = get_volume_data(symbol)
        if df_price is None: 
            continue
            
        # Get volume 20 days prior
        if entry_date in df_price.index:
            loc_idx = df_price.index.get_loc(entry_date)
            if isinstance(loc_idx, slice): loc_idx = loc_idx.start
            
            if loc_idx >= 20:
                vol_series = df_price['volume'].iloc[loc_idx-20:loc_idx]
                avg_vol = vol_series.mean()
                curr_vol = df_price['volume'].iloc[loc_idx]
                
                if avg_vol > 0:
                    df_trades.at[idx, 'rvol'] = curr_vol / avg_vol
                    
    # 3. Analyze by Buckets
    df_trades = df_trades.dropna(subset=['rvol'])
    
    # Define arbitrary buckets for analysis
    buckets = [
        {'name': 'Low (<0.8)', 'min': 0.0, 'max': 0.8},
        {'name': 'Normal (0.8-1.5)', 'min': 0.8, 'max': 1.5},
        {'name': 'High (1.5-2.0)', 'min': 1.5, 'max': 2.0},
        {'name': 'Extreme (>2.0)', 'min': 2.0, 'max': 999.0}
    ]
    
    print("\n📊 RVol Threshold Analysis (Thai Only):")
    print("| RVol Range | Total Trades | Win Rate % | Edge |")
    print("| :--- | :--- | :--- | :--- |")
    
    global_wr = len(df_trades[df_trades['correct'] == 1]) / len(df_trades) * 100
    
    for b in buckets:
        subset = df_trades[(df_trades['rvol'] >= b['min']) & (df_trades['rvol'] < b['max'])]
        if len(subset) == 0:
            continue
            
        wins = len(subset[subset['correct'] == 1])
        wr = (wins / len(subset)) * 100
        edge = wr - global_wr
        
        print(f"| {b['name']} | {len(subset)} | {wr:.2f}% | {edge:+.2f}% |")

if __name__ == "__main__":
    analyze_thai()
