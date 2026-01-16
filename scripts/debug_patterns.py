#!/usr/bin/env python
"""
Debug script to see what patterns are being found
"""
import sys
sys.path.insert(0, '/Users/rocket/Desktop/Intern/predict')

from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np

tv = TvDatafeed()
print("Fetching PTT data...")
df = tv.get_hist(symbol='PTT', exchange='SET', interval=Interval.in_daily, n_bars=200)

if df is not None:
    close = df['close']
    pct_change = close.pct_change()
    
    # Calc volatility
    short_term_std = pct_change.rolling(window=20).std()
    long_term_std = pct_change.rolling(window=252).std()
    long_term_floor = long_term_std * 0.50
    effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
    effective_std = effective_std.fillna(short_term_std)
    
    threshold_series = effective_std * 2.0
    
    # Find patterns
    pattern_counts = {}
    
    for i in range(10, len(pct_change)):
        if i < 4:
            continue
        window_returns = pct_change.iloc[i-3:i+1]
        window_thresh = threshold_series.iloc[i-3:i+1]
        
        pattern = ""
        for ret, thresh in zip(window_returns, window_thresh):
            if pd.isna(ret) or pd.isna(thresh):
                continue
            if ret > thresh:
                pattern += '+'
            elif ret < -thresh:
                pattern += '-'
        
        if pattern:
            if pattern not in pattern_counts:
                pattern_counts[pattern] = 0
            pattern_counts[pattern] += 1
    
    print(f"\n✅ Found {len(pattern_counts)} unique patterns:")
    for p, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {p:<8} → {count} occurrences")
else:
    print("Failed to fetch")
