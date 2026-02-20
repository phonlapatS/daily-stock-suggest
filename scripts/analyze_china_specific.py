import pandas as pd
import numpy as np
import os
import glob

CACHE_DIR = "e:/PredictPlus1/data/cache"
LOG_FILE = "e:/PredictPlus1/logs/trade_history_CHINA.csv"

def get_volume_data(symbol):
    # Try different prefixes for China stocks (HKEX, NASDAQ, NYSE)
    prefixes = ["HKEX", "NASDAQ", "NYSE", "TWSE"]
    
    for prefix in prefixes:
        path = os.path.join(CACHE_DIR, f"{prefix}_{symbol}.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['datetime'] = df['datetime'].dt.normalize()
                df = df.set_index('datetime')
                # Remove duplicate indices if any
                df = df[~df.index.duplicated(keep='first')]
                return df
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
                
    return None

def analyze_china():
    print("🇨🇳 Starting Deep Dive Analysis for China Market...")
    
    if not os.path.exists(LOG_FILE):
        print("❌ China trade log not found!")
        return

    df = pd.read_csv(LOG_FILE)
    df['date'] = pd.to_datetime(df['date'])
    
    total_trades = len(df)
    print(f"Loaded {total_trades} China trades.")
    
    # Metrics to track
    rvol_bins = {
        "Low (<1.0)": {"wins": 0, "total": 0},
        "Normal (1.0-1.5)": {"wins": 0, "total": 0},
        "High (1.5-2.0)": {"wins": 0, "total": 0},
        "Extreme (>2.0)": {"wins": 0, "total": 0}
    }
    
    for idx, row in df.iterrows():
        symbol = str(row['symbol'])
        entry_date = row['date'].normalize()
        is_win = (row['forecast'] == row['actual'])
        
        cache = get_volume_data(symbol)
        if cache is not None and entry_date in cache.index:
            loc = cache.index.get_loc(entry_date)
            # Handle slice if multiple entries
            if isinstance(loc, slice):
                loc = loc.start
                
            if loc >= 20:
                vol_today = cache.iloc[loc]['volume']
                vol_ma = cache.iloc[loc-20:loc]['volume'].mean()
                
                rvol = 0
                if vol_ma > 0:
                    rvol = vol_today / vol_ma
                
                # Bucketing
                if rvol < 1.0:
                    key = "Low (<1.0)"
                elif rvol < 1.5:
                    key = "Normal (1.0-1.5)"
                elif rvol < 2.0:
                    key = "High (1.5-2.0)"
                else:
                    key = "Extreme (>2.0)"
                    
                rvol_bins[key]["total"] += 1
                if is_win:
                    rvol_bins[key]["wins"] += 1

    print("\n📊 RVol Threshold Analysis (China Only):")
    print("| RVol Range | Total Trades | Win Rate % | Edge |")
    print("| :--- | :--- | :--- | :--- |")
    
    # Calculate baseline (approx)
    total_wins = sum(b['wins'] for b in rvol_bins.values())
    total_count = sum(b['total'] for b in rvol_bins.values())
    baseline_wr = (total_wins/total_count*100) if total_count > 0 else 0
    
    for key, data in rvol_bins.items():
        count = data['total']
        wins = data['wins']
        wr = (wins / count * 100) if count > 0 else 0
        edge = wr - baseline_wr
        print(f"| {key} | {count} | {wr:.2f}% | {edge:+.2f}% |")

if __name__ == "__main__":
    analyze_china()
