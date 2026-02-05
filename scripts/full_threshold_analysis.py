#!/usr/bin/env python
"""
full_threshold_analysis.py - Complete threshold comparison for all metals
=========================================================================
รันทดสอบ Threshold ทุกค่าสำหรับทั้ง Gold และ Silver ใน 15m และ 30m
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

def backtest_with_threshold(df, threshold_pct, n_test_bars=500):
    """Backtest ด้วย threshold ที่กำหนด"""
    total_bars = len(df)
    test_bars = min(n_test_bars, int(total_bars * 0.2))
    train_end = total_bars - test_bars
    
    close = df['close']
    pct_change = close.pct_change()
    threshold = threshold_pct / 100.0
    
    correct = 0
    total = 0
    wins = []
    losses = []
    
    for i in range(train_end, total_bars - 1):
        pattern_3 = ""
        for j in range(i-2, i+1):
            ret = pct_change.iloc[j]
            if ret > threshold:
                pattern_3 += "+"
            elif ret < -threshold:
                pattern_3 += "-"
            else:
                pattern_3 += "."
        
        if "." in pattern_3:
            continue
        
        matches = []
        for k in range(50, train_end - 1):
            hist_pattern = ""
            for m in range(k-2, k+1):
                ret = pct_change.iloc[m]
                if ret > threshold:
                    hist_pattern += "+"
                elif ret < -threshold:
                    hist_pattern += "-"
                else:
                    hist_pattern += "."
            
            if hist_pattern == pattern_3:
                next_ret = (close.iloc[k+1] - close.iloc[k]) / close.iloc[k]
                matches.append(next_ret)
        
        if len(matches) < 10:
            continue
        
        if pattern_3[-1] == "+":
            up_count = sum(1 for r in matches if r > 0)
            prob = (up_count / len(matches)) * 100
            forecast = "UP"
        else:
            down_count = sum(1 for r in matches if r < 0)
            prob = (down_count / len(matches)) * 100
            forecast = "DOWN"
        
        if prob < 55:
            continue
        
        actual_ret = (close.iloc[i+1] - close.iloc[i]) / close.iloc[i]
        actual_dir = "UP" if actual_ret > 0 else "DOWN"
        
        is_correct = (forecast == actual_dir)
        total += 1
        if is_correct:
            correct += 1
            wins.append(abs(actual_ret))
        else:
            losses.append(abs(actual_ret))
    
    if total == 0:
        return None
    
    accuracy = (correct / total) * 100
    avg_win = np.mean(wins) * 100 if wins else 0
    avg_loss = np.mean(losses) * 100 if losses else 0
    rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    
    return {
        'threshold': threshold_pct,
        'trades': total,
        'accuracy': accuracy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rr_ratio': rr_ratio
    }


def main():
    print("=" * 80)
    print("🔬 FULL THRESHOLD ANALYSIS - GOLD & SILVER (15m & 30m)")
    print("=" * 80)
    
    tv = TvDatafeed()
    
    configs = [
        {'symbol': 'XAUUSD', 'name': 'GOLD', 'interval': Interval.in_15_minute, 'tf': '15m'},
        {'symbol': 'XAUUSD', 'name': 'GOLD', 'interval': Interval.in_30_minute, 'tf': '30m'},
        {'symbol': 'XAGUSD', 'name': 'SILVER', 'interval': Interval.in_15_minute, 'tf': '15m'},
        {'symbol': 'XAGUSD', 'name': 'SILVER', 'interval': Interval.in_30_minute, 'tf': '30m'},
    ]
    
    thresholds = [0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25]
    all_results = []
    
    for cfg in configs:
        print(f"\n{'='*80}")
        print(f"📊 {cfg['name']} ({cfg['tf']})")
        print("-" * 80)
        
        df = tv.get_hist(symbol=cfg['symbol'], exchange='OANDA', 
                         interval=cfg['interval'], n_bars=5000)
        
        if df is None or len(df) < 500:
            print(f"❌ Failed to fetch data")
            continue
        
        print(f"✅ Loaded {len(df)} bars")
        
        for thresh in thresholds:
            result = backtest_with_threshold(df, thresh)
            if result:
                result['asset'] = cfg['name']
                result['timeframe'] = cfg['tf']
                all_results.append(result)
                print(f"   {thresh:.2f}%: {result['trades']:>3} trades, "
                      f"Acc {result['accuracy']:>5.1f}%, RR {result['rr_ratio']:.2f}")
        
        time.sleep(1)
    
    # Create summary tables
    print("\n" + "=" * 80)
    print("📈 COMPLETE SUMMARY TABLE")
    print("=" * 80)
    
    for asset in ['GOLD', 'SILVER']:
        for tf in ['15m', '30m']:
            subset = [r for r in all_results if r['asset'] == asset and r['timeframe'] == tf]
            if not subset:
                continue
            
            print(f"\n### {asset} {tf}")
            print(f"{'Threshold':<12} {'Trades':>8} {'Accuracy':>10} {'Avg Win':>10} {'Avg Loss':>10} {'RR':>8} {'Score':>8}")
            print("-" * 70)
            
            for r in subset:
                # Score = (Accuracy/50) * RR * log(Trades+1)
                score = (r['accuracy']/50) * r['rr_ratio'] * np.log(r['trades']+1)
                marker = " ⭐" if score == max((s['accuracy']/50) * s['rr_ratio'] * np.log(s['trades']+1) for s in subset) else ""
                print(f"{r['threshold']:.2f}%{'':<7} {r['trades']:>8} {r['accuracy']:>9.1f}% "
                      f"{r['avg_win']:>9.2f}% {r['avg_loss']:>9.2f}% {r['rr_ratio']:>8.2f} {score:>7.2f}{marker}")
    
    # Save to CSV
    if all_results:
        df_results = pd.DataFrame(all_results)
        df_results.to_csv('logs/threshold_analysis.csv', index=False)
        print(f"\n💾 Saved to logs/threshold_analysis.csv")
    
    print("\n✅ Analysis Complete!")


if __name__ == "__main__":
    main()
