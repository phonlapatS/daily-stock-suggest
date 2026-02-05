#!/usr/bin/env python
"""
threshold_comparison.py - Compare different threshold values
=============================================================
ทดสอบหลายค่า Threshold เพื่อหาค่าที่เหมาะสม
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

def backtest_with_threshold(df, threshold_pct, n_test_bars=500):
    """
    Backtest ด้วย threshold ที่กำหนด
    """
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
    rr_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    return {
        'threshold': threshold_pct,
        'trades': total,
        'accuracy': accuracy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rr_ratio': rr_ratio
    }


def main():
    print("=" * 70)
    print("🔬 THRESHOLD COMPARISON TEST")
    print("=" * 70)
    
    tv = TvDatafeed()
    
    # Test 1: Gold 15m with different thresholds
    print("\n📊 TEST 1: XAUUSD (Gold) 15min - Multiple Thresholds")
    print("-" * 70)
    
    df_gold = tv.get_hist(symbol='XAUUSD', exchange='OANDA', 
                          interval=Interval.in_15_minute, n_bars=5000)
    
    if df_gold is not None and len(df_gold) >= 500:
        print(f"✅ Loaded {len(df_gold)} bars")
        
        thresholds = [0.08, 0.10, 0.12, 0.15, 0.18, 0.20]
        results = []
        
        for thresh in thresholds:
            result = backtest_with_threshold(df_gold, thresh)
            if result:
                results.append(result)
                print(f"   Threshold {thresh:.2f}%: {result['trades']} trades, "
                      f"Acc {result['accuracy']:.1f}%, RR {result['rr_ratio']:.2f}")
        
        print("\n📈 GOLD 15m SUMMARY:")
        print(f"{'Threshold':<12} {'Trades':>8} {'Accuracy':>10} {'Avg Win':>10} {'Avg Loss':>10} {'RR':>8}")
        print("-" * 60)
        for r in results:
            print(f"{r['threshold']:.2f}%{'':<7} {r['trades']:>8} {r['accuracy']:>9.1f}% "
                  f"{r['avg_win']:>9.2f}% {r['avg_loss']:>9.2f}% {r['rr_ratio']:>8.2f}")
    
    time.sleep(2)
    
    # Test 2: Silver 30m (retry)
    print("\n" + "=" * 70)
    print("📊 TEST 2: XAGUSD (Silver) 30min - Retry Fetch")
    print("-" * 70)
    
    df_silver = tv.get_hist(symbol='XAGUSD', exchange='OANDA', 
                            interval=Interval.in_30_minute, n_bars=5000)
    
    if df_silver is not None and len(df_silver) >= 500:
        print(f"✅ Loaded {len(df_silver)} bars")
        
        # Save to cache
        os.makedirs("cache", exist_ok=True)
        df_silver.to_parquet("cache/XAGUSD_30m.parquet")
        print(f"💾 Cached to cache/XAGUSD_30m.parquet")
        
        thresholds = [0.10, 0.12, 0.15, 0.20]
        results = []
        
        for thresh in thresholds:
            result = backtest_with_threshold(df_silver, thresh)
            if result:
                results.append(result)
        
        print("\n📈 SILVER 30m SUMMARY:")
        print(f"{'Threshold':<12} {'Trades':>8} {'Accuracy':>10} {'Avg Win':>10} {'Avg Loss':>10} {'RR':>8}")
        print("-" * 60)
        for r in results:
            print(f"{r['threshold']:.2f}%{'':<7} {r['trades']:>8} {r['accuracy']:>9.1f}% "
                  f"{r['avg_win']:>9.2f}% {r['avg_loss']:>9.2f}% {r['rr_ratio']:>8.2f}")
    else:
        print("❌ Failed to fetch Silver 30m data")
    
    print("\n✅ Test Complete!")


if __name__ == "__main__":
    main()
