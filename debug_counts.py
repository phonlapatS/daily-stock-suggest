import pandas as pd
from tvDatafeed import TvDatafeed, Interval

def debug_counts(symbol='ADVANC', pattern='+'):
    # Load Data directly to match batch_processor logic
    tv = TvDatafeed()
    df = tv.get_hist(symbol=symbol, exchange='SET', interval=Interval.in_daily, n_bars=5000)
    
    if df is None or df.empty:
        print("No data found")
        return

    close = df['close']
    pct_change = close.pct_change()
    
    # Calculate Threshold (Strict Logic)
    recent_std = pct_change.iloc[-20:].std()
    threshold = recent_std * 1.25 # Raw value
    
    print(f"DEBUG: Symbol={symbol}, Pattern={pattern}, Threshold={threshold:.5f}")
    
    pattern_len = len(pattern)
    returns = []
    
    # Scan logic from batch_processor
    for i in range(pattern_len, len(pct_change) - 1):
        window = pct_change.iloc[i - pattern_len:i]
        
        window_pattern = ''
        for ret in window:
            if pd.isna(ret): break
            if ret > threshold: window_pattern += '+'
            elif ret < -threshold: window_pattern += '-'
        
        if len(window_pattern) != pattern_len: continue

        if window_pattern == pattern:
            next_ret = pct_change.iloc[i]
            returns.append(next_ret)

    total = len(returns)
    up_count = sum(1 for r in returns if r > 0)
    down_count = sum(1 for r in returns if r < 0)
    flat_count = sum(1 for r in returns if r == 0)
    
    print(f"Total Occurrences: {total}")
    print(f"UP   (>0): {up_count} ({up_count/total*100:.2f}%)")
    print(f"DOWN (<0): {down_count} ({down_count/total*100:.2f}%)")
    print(f"FLAT (=0): {flat_count} ({flat_count/total*100:.2f}%)")
    
    winner = "UP" if up_count >= down_count else "DOWN"
    print(f"Winner: {winner}")

if __name__ == "__main__":
    debug_counts()
