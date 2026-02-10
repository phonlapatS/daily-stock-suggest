#!/usr/bin/env python
"""
quick_intl_analysis.py - Fast International Stock Analysis
============================================================
รัน ~5-8 นาที, ใช้ 2000 bars, 3 หุ้น, 3 thresholds
"""
import time
import numpy as np
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

start_time = time.time()

def analyze(df, threshold_pct):
    close = df['close']
    pct = close.pct_change()
    th = threshold_pct / 100.0
    
    wins, losses = [], []
    
    for i in range(3, len(df)-1):
        p = ''.join(['+' if pct.iloc[j] > th else '-' if pct.iloc[j] < -th else '.' for j in range(i-2, i+1)])
        if '.' in p: continue
        
        next_ret = (close.iloc[i+1] - close.iloc[i]) / close.iloc[i]
        hit = (p[-1] == '+' and next_ret > 0) or (p[-1] == '-' and next_ret < 0)
        (wins if hit else losses).append(abs(next_ret))
    
    if not wins and not losses: return None
    
    trades = len(wins) + len(losses)
    acc = len(wins) / trades * 100
    avg_w = np.mean(wins) * 100 if wins else 0
    avg_l = np.mean(losses) * 100 if losses else 0
    rr = avg_w / avg_l if avg_l else 0
    exp = (acc/100 * avg_w) - ((1-acc/100) * avg_l)
    
    return {'trades': trades, 'acc': acc, 'rr': rr, 'exp': exp}

print("="*60)
print(f"START: {datetime.now().strftime('%H:%M:%S')}")
print("Estimated: 5-8 minutes")
print("="*60)

tv = TvDatafeed()
stocks = [('AAPL','NASDAQ','US'), ('TSMC','NYSE','Taiwan'), ('BABA','NYSE','China')]
thresholds = [0.5, 0.6, 0.8]

results = []

for i, (sym, ex, mkt) in enumerate(stocks):
    print(f"\n[{i+1}/3] {sym} ({mkt})...")
    
    df = tv.get_hist(symbol=sym, exchange=ex, interval=Interval.in_daily, n_bars=2000)
    if df is None:
        print("  ❌ No data")
        continue
    
    print(f"  ✅ Loaded {len(df)} bars")
    
    for th in thresholds:
        r = analyze(df, th)
        if r:
            r['symbol'] = sym
            r['market'] = mkt
            r['threshold'] = th
            results.append(r)
            print(f"  {th}%: Trades={r['trades']}, Acc={r['acc']:.1f}%, RR={r['rr']:.2f}, Exp={r['exp']:.2f}%")
    
    elapsed = time.time() - start_time
    print(f"  ⏱️ Elapsed: {elapsed/60:.1f} min")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"{'Market':<10} {'Symbol':<8} {'Thresh':<8} {'Trades':<8} {'Acc':<8} {'RR':<8} {'Exp'}")
print("-"*60)
for r in results:
    marker = "⭐" if r['exp'] > 0.3 else ("⚠️" if r['exp'] < 0 else "")
    print(f"{r['market']:<10} {r['symbol']:<8} {r['threshold']:.1f}%     {r['trades']:<8} {r['acc']:.1f}%   {r['rr']:.2f}     {r['exp']:.2f}% {marker}")

print(f"\n✅ DONE at {datetime.now().strftime('%H:%M:%S')}")
print(f"Total time: {(time.time()-start_time)/60:.1f} minutes")
