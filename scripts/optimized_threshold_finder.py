#!/usr/bin/env python
"""
optimized_threshold_finder.py - Fast Threshold Analysis
=========================================================
ใช้ Pattern Index Pre-computation เพื่อเร็วขึ้น 10-50x
ไม่กระทบ Production Code

เวลาประมาณ: 30 วินาที - 1 นาที (แทน 5-10 นาที)
"""
import time
import numpy as np
import pandas as pd
from collections import defaultdict
from tvDatafeed import TvDatafeed, Interval

# ... (omitted helper functions build_pattern_index, analyze_threshold) ...

def main():
    start = time.time()
    
    print("="*70)
    print("OPTIMIZED THRESHOLD FINDER (Pattern Index Method)")
    print("Est. Time: 30-60 seconds")
    print("="*70)
    
    tv = TvDatafeed()
    
    # Test HK stocks individually to minimize timeout risk
    stocks = [
        ('700', 'HK', 'HK'), 
        ('9988', 'HK', 'HK'),
    ]
    
    thresholds = [0.4, 0.5, 0.6, 0.8, 1.0]
    
    all_results = []
    
    for symbol, exchange, market in stocks:
        print(f"\n📊 {market}: {symbol}...")
        
        try:
            # TvDatafeed request (reduced bars for nologin)
            df = tv.get_hist(symbol=symbol, exchange=exchange, 
                             interval=Interval.in_daily, n_bars=1000)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            df = None
        
        if df is None or len(df) < 200:
            print("  ❌ Insufficient data")
            continue
            
        returns = df['close'].pct_change().values
        print(f"  ✅ {len(df)} bars loaded")
        
        for th in thresholds:
            result = analyze_threshold(returns, th)
            if result:
                result['symbol'] = symbol
                result['market'] = market
                result['threshold'] = th
                all_results.append(result)
    
    # Print Summary
    print("\n" + "="*70)
    print("SUMMARY - RRR by Market and Threshold")
    print("="*70)
    print(f"{'Market':<8} {'Symbol':<6} {'Thresh':<8} {'Trades':<8} {'Acc':<8} {'RR':<8} {'Exp':<10} {'Status'}")
    print("-"*70)
    
    for r in sorted(all_results, key=lambda x: (x['market'], x['symbol'], x['threshold'])):
        status = "⭐" if r['expectancy'] > 0.3 else ("✅" if r['expectancy'] > 0 else "❌")
        print(f"{r['market']:<8} {r['symbol']:<6} {r['threshold']:.1f}%     "
              f"{r['trades']:<8} {r['accuracy']:.1f}%   {r['rr']:.2f}     "
              f"{r['expectancy']:.2f}%    {status}")
    
    # Best per market
    print("\n" + "="*70)
    print("BEST THRESHOLD PER MARKET")
    print("="*70)
    
    for market in ['US', 'China', 'Taiwan']:
        market_results = [r for r in all_results if r['market'] == market]
        if not market_results:
            continue
        best = max(market_results, key=lambda x: x['expectancy'])
        print(f"{market}: {best['threshold']:.1f}% (Exp: {best['expectancy']:.2f}%, RR: {best['rr']:.2f})")
    
    print(f"\n⏱️ Total Time: {time.time() - start:.1f} seconds")
    print("✅ Done!")


if __name__ == "__main__":
    main()
