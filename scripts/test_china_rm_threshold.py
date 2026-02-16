#!/usr/bin/env python
"""
Test China Market - Risk Management & Threshold Optimization

ทดสอบหลายค่า:
- Max Hold: 5, 6, 7, 8, 9, 10 days
- Threshold Multiplier: 0.8, 0.85, 0.9, 0.95, 1.0

แยก logic ของ China market ให้ชัดเจน
"""

import sys
import os
import pandas as pd
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.backtest import backtest_all, TvDatafeed
from scripts.calculate_metrics import calculate_metrics

# Test Parameters
MAX_HOLD_OPTIONS = [5, 6, 7, 8, 9, 10]
THRESHOLD_OPTIONS = [0.8, 0.85, 0.9, 0.95, 1.0]

# Fixed RM Parameters (V13.2 base)
RM_STOP_LOSS = 1.2
RM_TAKE_PROFIT = 5.5
RM_TRAIL_ACTIVATE = 1.0
RM_TRAIL_DISTANCE = 40.0

def run_china_backtest(max_hold, threshold_multiplier, n_bars=2000):
    """
    Run backtest for China market with specific parameters
    
    Args:
        max_hold: Max hold days
        threshold_multiplier: Threshold multiplier
        n_bars: Number of test bars
    """
    print(f"\n{'='*80}")
    print(f"Testing: Max Hold={max_hold} days, Threshold={threshold_multiplier}")
    print(f"{'='*80}")
    
    # Clean old results
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"✅ Removed {log_file}")
    
    if os.path.exists(perf_file):
        # Remove only China entries
        try:
            df = pd.read_csv(perf_file)
            df = df[df['Country'] != 'CN']
            df.to_csv(perf_file, index=False)
            print(f"✅ Cleaned China entries from {perf_file}")
        except:
            pass
    
    # Run backtest with custom parameters
    try:
        print(f"Running backtest...")
        print(f"  Max Hold: {max_hold} days")
        print(f"  Threshold: {threshold_multiplier}")
        print(f"  Test Bars: {n_bars}")
        
        # Note: backtest_all needs to be modified to accept custom kwargs
        # For now, we'll use a workaround by calling backtest_single directly
        # or modify backtest_all to pass kwargs through
        
        # This is a placeholder - actual implementation needs:
        # 1. Modify backtest_all to accept and pass kwargs to backtest_single
        # 2. Or call backtest_single directly for each China stock
        
        print(f"⚠️  Note: This requires backtest_all to accept custom kwargs")
        print(f"   See implementation in docs/CHINA_TEST_PLAN.md")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_results(max_hold, threshold_multiplier):
    """Analyze results from backtest"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        return None
    
    result = {
        'max_hold': max_hold,
        'threshold': threshold_multiplier,
        'stocks_passing': len(china_df),
        'avg_rrr': china_df['RR_Ratio'].mean() if len(china_df) > 0 else 0,
        'avg_prob': china_df['Prob%'].mean() if len(china_df) > 0 else 0,
        'total_count': china_df['Count'].sum() if len(china_df) > 0 else 0,
        'avg_count': china_df['Count'].mean() if len(china_df) > 0 else 0,
        'best_rrr': china_df['RR_Ratio'].max() if len(china_df) > 0 else 0,
        'worst_rrr': china_df['RR_Ratio'].min() if len(china_df) > 0 else 0,
        'stocks': ', '.join(china_df['symbol'].tolist()) if len(china_df) > 0 else '',
    }
    
    return result

def main():
    """Main test function"""
    print("="*80)
    print("China Market - RM & Threshold Optimization Test")
    print("="*80)
    print(f"\nTest Matrix:")
    print(f"  Max Hold: {MAX_HOLD_OPTIONS}")
    print(f"  Threshold: {THRESHOLD_OPTIONS}")
    print(f"  Total Tests: {len(MAX_HOLD_OPTIONS) * len(THRESHOLD_OPTIONS)}")
    print(f"\nFixed RM Parameters:")
    print(f"  SL: {RM_STOP_LOSS}%")
    print(f"  TP: {RM_TAKE_PROFIT}%")
    print(f"  Trail Activate: {RM_TRAIL_ACTIVATE}%")
    print(f"  Trail Distance: {RM_TRAIL_DISTANCE}%")
    
    results = []
    
    for max_hold in MAX_HOLD_OPTIONS:
        for threshold in THRESHOLD_OPTIONS:
            print(f"\n{'='*80}")
            print(f"Test {len(results)+1}/{len(MAX_HOLD_OPTIONS)*len(THRESHOLD_OPTIONS)}")
            print(f"Max Hold={max_hold}, Threshold={threshold}")
            print(f"{'='*80}")
            
            # Run backtest
            run_china_backtest(max_hold, threshold)
            
            # Analyze results
            result = analyze_results(max_hold, threshold)
            if result:
                results.append(result)
                print(f"✅ Results: {result['stocks_passing']} stocks, Avg RRR: {result['avg_rrr']:.2f}")
            else:
                print(f"⚠️  No results found")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv('data/china_rm_threshold_test_results.csv', index=False)
        print(f"\n✅ Results saved to data/china_rm_threshold_test_results.csv")
        print(f"\nSummary:")
        print(results_df[['max_hold', 'threshold', 'stocks_passing', 'avg_rrr', 'avg_prob']].to_string(index=False))
    else:
        print(f"\n⚠️  No results to save")
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
