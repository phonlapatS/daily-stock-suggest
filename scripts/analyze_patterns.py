#!/usr/bin/env python
"""
Count pattern types from last run
"""
import re

# Read output (simulated - would need actual output file)
# But let me create a script to analyze patterns in real-time

import sys
sys.path.insert(0, '/Users/rocket/Desktop/Intern/predict')

from tvDatafeed import TvDatafeed, Interval
import processor

tv = TvDatafeed()

pattern_lengths = {}

# Test with a few US stocks
test_symbols = [('AAPL', 'NASDAQ'), ('TSLA', 'NASDAQ'), ('NVDA', 'NASDAQ')]

print("Analyzing pattern lengths...\n")

for symbol, exchange in test_symbols:
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=500)
        if df is not None:
            results = processor.analyze_asset(df)
            print(f"{symbol}: {len(results)} patterns found")
            for r in results:
                pattern = r['pattern_display']
                length = len(pattern)
                if length not in pattern_lengths:
                    pattern_lengths[length] = 0
                pattern_lengths[length] += 1
                print(f"  {pattern} ({length} chars, {r['matches']} matches)")
    except Exception as e:
        print(f"{symbol}: Error - {e}")

print(f"\n{'='*50}")
print("Pattern Length Distribution:")
for length in sorted(pattern_lengths.keys()):
    count = pattern_lengths[length]
    print(f"  {length}-char patterns: {count} found")
