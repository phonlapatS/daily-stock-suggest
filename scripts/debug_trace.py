#!/usr/bin/env python
"""
Debug: trace through processor logic step by step
"""
import sys
sys.path.insert(0, '/Users/rocket/Desktop/Intern/predict')

from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np

tv = TvDatafeed()
print("Fetching PTT data...")
df = tv.get_hist(symbol='PTT', exchange='SET', interval=Interval.in_daily, n_bars=500)

if df is None:
    print("Failed to fetch!")
    sys.exit(1)

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
pattern_occurrences = {}

print(f"Scanning {len(pct_change)} days...")

for i in range(5, len(pct_change)):
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
        if pattern not in pattern_occurrences:
            pattern_occurrences[pattern] = []
        pattern_occurrences[pattern].append(i)

print(f"\nFound {len(pattern_occurrences)} unique patterns")

# Now calculate stats for each
for pattern_str, occurrence_indices in pattern_occurrences.items():
    future_returns = []
    
    for end_idx in occurrence_indices:
        next_idx = end_idx + 1
        if next_idx < len(close):
            price_at_pattern_end = close.iloc[end_idx]
            price_next_day = close.iloc[next_idx]
            ret = (price_next_day - price_at_pattern_end) / price_at_pattern_end
            future_returns.append(ret)
    
    if len(future_returns) >= 10:
        bull_count = sum(1 for r in future_returns if r > 0)
        total = len(future_returns)
        bull_prob = (bull_count / total) * 100
        bear_prob = 100 - bull_prob
        dominant_prob = max(bull_prob, bear_prob)
        
        if dominant_prob >= 60:
            avg_ret = np.mean(future_returns) * 100
            print(f"\n✅ {pattern_str:<8} | Matches: {total:<4} | Prob: {int(dominant_prob)}% | Exp: {avg_ret:+.2f}%")
