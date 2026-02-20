"""
US Market Volume & RRR Deep Analysis (V14.6 Optimization)
Analyzes trade_history_US.csv to find optimal RVol thresholds and RM parameters.
"""
import pandas as pd
import numpy as np
import os

CACHE_DIR = "e:/PredictPlus1/data/cache"
LOG_FILE = "e:/PredictPlus1/logs/trade_history_US.csv"

price_cache = {}

def get_volume_data(symbol):
    if symbol in price_cache:
        return price_cache[symbol]
    
    for prefix in ["NASDAQ", "NYSE", "COMEX", "NYMEX"]:
        path = os.path.join(CACHE_DIR, f"{prefix}_{symbol}.csv")
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
                continue
    return None

def analyze_us():
    print("🇺🇸 US Market Deep Dive Analysis")
    print("=" * 60)
    
    if not os.path.exists(LOG_FILE):
        print(f"❌ Log file not found: {LOG_FILE}")
        return

    df_trades = pd.read_csv(LOG_FILE)
    print(f"Loaded {len(df_trades)} US trades.")
    
    # === 1. RVol Bucket Analysis ===
    df_trades['rvol'] = np.nan
    df_trades['avg_win'] = np.nan
    df_trades['avg_loss'] = np.nan
    
    for idx, row in df_trades.iterrows():
        symbol = row['symbol']
        try:
            entry_date = pd.to_datetime(row['date']).normalize()
        except:
            continue
        
        df_price = get_volume_data(symbol)
        if df_price is None or 'volume' not in df_price.columns:
            continue
            
        if entry_date in df_price.index:
            loc_idx = df_price.index.get_loc(entry_date)
            if isinstance(loc_idx, slice): loc_idx = loc_idx.start
            
            if loc_idx >= 20:
                vol_series = df_price['volume'].iloc[loc_idx-20:loc_idx]
                avg_vol = vol_series.mean()
                curr_vol = df_price['volume'].iloc[loc_idx]
                
                if avg_vol > 0:
                    df_trades.at[idx, 'rvol'] = curr_vol / avg_vol
    
    df_with_rvol = df_trades.dropna(subset=['rvol'])
    print(f"Matched RVol data for {len(df_with_rvol)} / {len(df_trades)} trades.\n")
    
    # === 2. RVol Bucket Analysis (Win Rate + RRR) ===
    buckets = [
        {'name': 'Very Low (<0.5)', 'min': 0.0, 'max': 0.5},
        {'name': 'Low (0.5-0.8)', 'min': 0.5, 'max': 0.8},
        {'name': 'Normal (0.8-1.2)', 'min': 0.8, 'max': 1.2},
        {'name': 'Above Avg (1.2-1.5)', 'min': 1.2, 'max': 1.5},
        {'name': 'High (1.5-2.0)', 'min': 1.5, 'max': 2.0},
        {'name': 'Extreme (>2.0)', 'min': 2.0, 'max': 999.0}
    ]
    
    global_wr = len(df_with_rvol[df_with_rvol['correct'] == 1]) / len(df_with_rvol) * 100 if len(df_with_rvol) > 0 else 0
    
    # Compute global average win/loss
    wins_global = df_with_rvol[df_with_rvol['correct'] == 1]
    losses_global = df_with_rvol[df_with_rvol['correct'] == 0]
    global_avg_win = wins_global['trader_return'].mean() if len(wins_global) > 0 else 0
    global_avg_loss = abs(losses_global['trader_return'].mean()) if len(losses_global) > 0 else 1
    global_rrr = global_avg_win / global_avg_loss if global_avg_loss > 0 else 0
    
    print(f"📊 Global Baseline: WR {global_wr:.1f}% | AvgWin {global_avg_win:.2f}% | AvgLoss {global_avg_loss:.2f}% | RRR {global_rrr:.2f}")
    print()
    print("📊 RVol Bucket Analysis (US Market):")
    print(f"{'RVol Range':<20} {'Trades':>8} {'WinRate%':>10} {'Edge':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>8}")
    print("-" * 80)
    
    for b in buckets:
        subset = df_with_rvol[(df_with_rvol['rvol'] >= b['min']) & (df_with_rvol['rvol'] < b['max'])]
        if len(subset) < 10:
            continue
        
        wins = subset[subset['correct'] == 1]
        losses = subset[subset['correct'] == 0]
        wr = (len(wins) / len(subset)) * 100
        edge = wr - global_wr
        avg_win = wins['trader_return'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['trader_return'].mean()) if len(losses) > 0 else 1
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        print(f"{b['name']:<20} {len(subset):>8} {wr:>9.1f}% {edge:>+7.1f}% {avg_win:>9.2f}% {avg_loss:>9.2f}% {rrr:>7.2f}")
    
    # === 3. Exit Reason Analysis ===
    print("\n📊 Exit Reason Distribution:")
    if 'exit_reason' in df_trades.columns:
        exit_dist = df_trades['exit_reason'].value_counts()
        for reason, count in exit_dist.items():
            pct = count / len(df_trades) * 100
            subset_exits = df_trades[df_trades['exit_reason'] == reason]
            avg_ret = subset_exits['trader_return'].mean()
            print(f"   {reason:<15}: {count:>6} ({pct:>5.1f}%) | Avg Return: {avg_ret:>+.2f}%")
    
    # === 4. Trailing Stop Impact ===
    print("\n📊 Trailing Stop Analysis:")
    if 'exit_reason' in df_trades.columns:
        trail_exits = df_trades[df_trades['exit_reason'] == 'TRAILING_STOP']
        non_trail = df_trades[df_trades['exit_reason'] != 'TRAILING_STOP']
        
        if len(trail_exits) > 0:
            trail_avg = trail_exits['trader_return'].mean()
            non_trail_avg = non_trail['trader_return'].mean()
            print(f"   Trailing Exits:     {len(trail_exits):>6} trades | Avg Return: {trail_avg:>+.2f}%")
            print(f"   Non-Trailing Exits: {len(non_trail):>6} trades | Avg Return: {non_trail_avg:>+.2f}%")
        else:
            print("   No trailing stop exits found.")

if __name__ == "__main__":
    analyze_us()
