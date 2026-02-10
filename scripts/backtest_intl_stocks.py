#!/usr/bin/env python
"""
backtest_intl_stocks.py - Backtest International Stocks for Optimal Threshold
===============================================================================
ทดสอบหา Threshold ที่เหมาะสมสำหรับหุ้นต่างประเทศ (US/China/HK/Taiwan)
โดยไม่กระทบ Logic เดิม (สคริปต์แยกอิสระ)

Usage:
    python3 scripts/backtest_intl_stocks.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Test Samples from each market
TEST_SAMPLES = {
    "US": [
        {'symbol': 'AAPL', 'exchange': 'NASDAQ', 'name': 'Apple'},
        {'symbol': 'NVDA', 'exchange': 'NASDAQ', 'name': 'Nvidia'},
        {'symbol': 'MSFT', 'exchange': 'NASDAQ', 'name': 'Microsoft'},
    ],
    "CHINA_ADR": [
        {'symbol': 'BABA', 'exchange': 'NYSE', 'name': 'Alibaba'},
        {'symbol': 'NIO', 'exchange': 'NYSE', 'name': 'NIO'},
        {'symbol': 'JD', 'exchange': 'NASDAQ', 'name': 'JD.com'},
    ],
    "TAIWAN": [
        {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'},
    ],
}

# Thresholds to test (Daily)
THRESHOLDS = [0.4, 0.5, 0.6, 0.7, 0.8, 1.0]


def backtest_with_threshold(df, threshold_pct, n_test_bars=200):
    """Backtest ด้วย Fixed Threshold"""
    total_bars = len(df)
    test_bars = min(n_test_bars, int(total_bars * 0.2))
    train_end = total_bars - test_bars
    
    if train_end < 200:
        return None
    
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
    
    # Calculate Expectancy
    win_rate = correct / total
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    return {
        'threshold': threshold_pct,
        'trades': total,
        'accuracy': accuracy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rr_ratio': rr_ratio,
        'expectancy': expectancy
    }


def backtest_with_dynamic(df, n_test_bars=200):
    """Backtest ด้วย Dynamic Threshold (เหมือน Logic เดิม)"""
    total_bars = len(df)
    test_bars = min(n_test_bars, int(total_bars * 0.2))
    train_end = total_bars - test_bars
    
    if train_end < 200:
        return None
    
    close = df['close']
    pct_change = close.pct_change()
    
    # Dynamic SD Calculation
    short_term_std = pct_change.rolling(window=20).std()
    long_term_std = pct_change.rolling(window=252).std()
    long_term_floor = long_term_std * 0.50
    effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
    effective_std = effective_std.fillna(short_term_std)
    
    correct = 0
    total = 0
    wins = []
    losses = []
    
    for i in range(train_end, total_bars - 1):
        # Get dynamic threshold at this point
        threshold = effective_std.iloc[i] * 1.25
        if np.isnan(threshold) or threshold == 0:
            continue
        
        pattern_3 = ""
        for j in range(i-2, i+1):
            ret = pct_change.iloc[j]
            local_thresh = effective_std.iloc[j] * 1.25
            if np.isnan(local_thresh):
                local_thresh = threshold
            if ret > local_thresh:
                pattern_3 += "+"
            elif ret < -local_thresh:
                pattern_3 += "-"
            else:
                pattern_3 += "."
        
        if "." in pattern_3:
            continue
        
        matches = []
        for k in range(50, train_end - 1):
            hist_thresh = effective_std.iloc[k] * 1.25
            if np.isnan(hist_thresh):
                continue
            hist_pattern = ""
            for m in range(k-2, k+1):
                ret = pct_change.iloc[m]
                local_t = effective_std.iloc[m] * 1.25
                if np.isnan(local_t):
                    local_t = hist_thresh
                if ret > local_t:
                    hist_pattern += "+"
                elif ret < -local_t:
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
    win_rate = correct / total
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    return {
        'threshold': 'DYNAMIC',
        'trades': total,
        'accuracy': accuracy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rr_ratio': rr_ratio,
        'expectancy': expectancy
    }


def main():
    print("=" * 80)
    print("🔬 INTERNATIONAL STOCKS THRESHOLD ANALYSIS")
    print("   (Fixed vs Dynamic Comparison)")
    print("=" * 80)
    
    tv = TvDatafeed()
    all_results = []
    
    for market, stocks in TEST_SAMPLES.items():
        print(f"\n{'='*80}")
        print(f"📊 MARKET: {market}")
        print("=" * 80)
        
        for stock in stocks:
            print(f"\n--- {stock['name']} ({stock['symbol']}) ---")
            
            try:
                df = tv.get_hist(
                    symbol=stock['symbol'], 
                    exchange=stock['exchange'],
                    interval=Interval.in_daily, 
                    n_bars=5000
                )
                
                if df is None or len(df) < 500:
                    print(f"❌ Insufficient data")
                    continue
                
                print(f"✅ Loaded {len(df)} bars")
                
                # Test Fixed Thresholds
                fixed_results = []
                for thresh in THRESHOLDS:
                    result = backtest_with_threshold(df, thresh)
                    if result:
                        result['market'] = market
                        result['symbol'] = stock['symbol']
                        result['method'] = 'FIXED'
                        fixed_results.append(result)
                        all_results.append(result)
                
                # Test Dynamic
                dyn_result = backtest_with_dynamic(df)
                if dyn_result:
                    dyn_result['market'] = market
                    dyn_result['symbol'] = stock['symbol']
                    dyn_result['method'] = 'DYNAMIC'
                    all_results.append(dyn_result)
                
                # Print Results for this stock
                print(f"\n{'Method':<10} {'Thresh':<8} {'Trades':>8} {'Acc':>8} {'RR':>8} {'Expect':>10}")
                print("-" * 60)
                
                for r in fixed_results:
                    print(f"{'FIXED':<10} {r['threshold']:.1f}%{'':<4} {r['trades']:>8} "
                          f"{r['accuracy']:>7.1f}% {r['rr_ratio']:>8.2f} {r['expectancy']:>9.3f}%")
                
                if dyn_result:
                    print(f"{'DYNAMIC':<10} {'(SD)':<8} {dyn_result['trades']:>8} "
                          f"{dyn_result['accuracy']:>7.1f}% {dyn_result['rr_ratio']:>8.2f} {dyn_result['expectancy']:>9.3f}%")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)
    
    # Save all results
    if all_results:
        df_results = pd.DataFrame(all_results)
        df_results.to_csv('logs/intl_threshold_analysis.csv', index=False)
        print(f"\n💾 Saved to logs/intl_threshold_analysis.csv")
        
        # Summary by Market
        print("\n" + "=" * 80)
        print("📈 SUMMARY BY MARKET (Best Fixed vs Dynamic)")
        print("=" * 80)
        
        for market in TEST_SAMPLES.keys():
            market_data = df_results[df_results['market'] == market]
            if market_data.empty:
                continue
            
            print(f"\n### {market}")
            
            # Best Fixed
            fixed_data = market_data[market_data['method'] == 'FIXED']
            if not fixed_data.empty:
                best_fixed = fixed_data.loc[fixed_data['expectancy'].idxmax()]
                print(f"   Best Fixed: {best_fixed['threshold']:.1f}% "
                      f"(Exp: {best_fixed['expectancy']:.3f}%, Acc: {best_fixed['accuracy']:.1f}%)")
            
            # Dynamic Average
            dyn_data = market_data[market_data['method'] == 'DYNAMIC']
            if not dyn_data.empty:
                avg_exp = dyn_data['expectancy'].mean()
                avg_acc = dyn_data['accuracy'].mean()
                print(f"   Dynamic Avg: (Exp: {avg_exp:.3f}%, Acc: {avg_acc:.1f}%)")
    
    print("\n✅ Analysis Complete!")


if __name__ == "__main__":
    main()
