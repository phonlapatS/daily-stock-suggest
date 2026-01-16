#!/usr/bin/env python
"""
Quick test with small subset to verify multi-pattern logic
"""
import sys
sys.path.insert(0, '/Users/rocket/Desktop/Intern/predict')

from tvDatafeed import TvDatafeed, Interval
import processor

# Test with 1 symbol only
tv = TvDatafeed()

print("Testing multi-pattern logic with PTT...")
df = tv.get_hist(symbol='PTT', exchange='SET', interval=Interval.in_daily, n_bars=500)

if df is not None:
    results = processor.analyze_asset(df)
    print(f"\n✅ Found {len(results)} patterns for PTT:\n")
    
    for i, r in enumerate(results, 1):
        print(f"{i}. Pattern: {r['pattern_display']:<8} | Matches: {r['matches']:<4} | Prob: {max(r['bull_prob'], r['bear_prob']):.0f}% | Exp: {r['avg_return']:+.2f}%")
    
    if not results:
        print("   (No patterns met quality criteria)")
else:
    print("❌ Failed to fetch data")
