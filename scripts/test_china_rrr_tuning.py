#!/usr/bin/env python
"""
Test China Market RRR Tuning - ปรับจูน RRR โดยไม่ทำให้ overfitting

ทดสอบหลายค่า:
- threshold_multiplier: 0.85, 0.9, 0.95, 1.0
- min_stats: 20, 25, 30
- min_prob: 50.0, 51.0, 52.0, 53.0

เป้าหมาย:
- RRR > 1.2 (ดีขึ้นจาก 1.0-1.3)
- Prob% > 50% (ยังคง realistic)
- Count > 20 (ยังคงน่าเชื่อถือ)
- หลีกเลี่ยง overfitting (ใช้ Raw Prob%)
"""

import sys
import os
import pandas as pd
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.backtest import backtest_all, TvDatafeed
from scripts.calculate_metrics import calculate_metrics

# Test Parameters - เน้นค่าที่ยืดหยุ่นและมีประสิทธิภาพจริงๆ
# Threshold: 0.9 (ปัจจุบัน), 0.95 (เพิ่มคุณภาพ) - ไม่เอา 0.85 (ต่ำเกิน) และ 1.0 (สูงเกิน)
# Min Stats: 25 (ปัจจุบัน), 30 (เพิ่มคุณภาพ) - ไม่เอา 20 (ต่ำเกิน)
# Min Prob: 50.0% (ปัจจุบัน), 51.0% (เพิ่มคุณภาพเล็กน้อย) - ไม่เอา 52%+ (สูงเกิน, อาจลด Count)
THRESHOLD_OPTIONS = [0.9, 0.95]
MIN_STATS_OPTIONS = [25, 30]
MIN_PROB_OPTIONS = [50.0, 51.0]

# Fixed RM Parameters (V13.5 ATR-based)
RM_ATR_SL = 1.0
RM_ATR_TP = 4.0
RM_MAX_HOLD = 3
RM_TRAIL_ACTIVATE = 1.0
RM_TRAIL_DISTANCE = 40.0

def run_china_backtest(threshold_multiplier, min_stats, min_prob, n_bars=2000):
    """
    Run backtest for China market with specific parameters
    
    Args:
        threshold_multiplier: Threshold multiplier
        min_stats: Minimum stats for pattern
        min_prob: Minimum probability for gatekeeper
        n_bars: Number of test bars
    """
    print(f"\n{'='*80}")
    print(f"Testing: Threshold={threshold_multiplier}, MinStats={min_stats}, MinProb={min_prob}%")
    print(f"{'='*80}")
    
    # Clean old results - Force rerun by removing existing results
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    backtest_results_file = 'data/full_backtest_results.csv'
    
    # Remove China trade history
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"✅ Removed {log_file}")
    
    # Remove China entries from performance file
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            df = df[df['Country'] != 'CN']
            df = df[df['Country'] != 'HK']
            df.to_csv(perf_file, index=False)
            print(f"✅ Cleaned China/HK entries from {perf_file}")
        except:
            pass
    
    # Remove China symbols from backtest results to force rerun
    if os.path.exists(backtest_results_file):
        try:
            df = pd.read_csv(backtest_results_file, on_bad_lines='skip', engine='python')
            if 'group' in df.columns:
                # Remove China/HK groups
                df = df[~df['group'].str.upper().str.contains('CHINA', na=False)]
                df = df[~df['group'].str.upper().str.contains('HK', na=False)]
                df.to_csv(backtest_results_file, index=False)
                print(f"✅ Cleaned China/HK entries from {backtest_results_file} (force rerun)")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean {backtest_results_file}: {e}")
    
    # Run backtest with custom parameters
    try:
        print(f"Running backtest...")
        print(f"  Threshold: {threshold_multiplier}")
        print(f"  Min Stats: {min_stats}")
        print(f"  Min Prob: {min_prob}%")
        print(f"  Test Bars: {n_bars}")
        
        # Run backtest (min_stats and min_prob are passed via kwargs)
        backtest_all(
            n_bars=n_bars,
            full_scan=True,
            target_group='CHINA',
            threshold_multiplier=threshold_multiplier,
            min_stats=min_stats,  # Passed via kwargs to backtest_single
            min_prob=min_prob,    # Passed via kwargs to backtest_single
            atr_sl_mult=RM_ATR_SL,
            atr_tp_mult=RM_ATR_TP,
            max_hold=RM_MAX_HOLD,
            trail_activate=RM_TRAIL_ACTIVATE,
            trail_distance=RM_TRAIL_DISTANCE,
            production=False,
            fast_mode=True
        )
        
        # Calculate metrics
        print(f"\nCalculating metrics...")
        calculate_metrics(
            input_path='logs/trade_history_CHINA.csv',
            output_path='data/symbol_performance.csv'
        )
        
        # Load results
        if os.path.exists('data/symbol_performance.csv'):
            df = pd.read_csv('data/symbol_performance.csv')
            china_df = df[((df['Country'] == 'CN') | (df['Country'] == 'HK')) & 
                         (df['Prob%'] >= 50.0) & 
                         (df['RR_Ratio'] >= 1.0) & 
                         (df['Count'] >= 20)]
            
            if not china_df.empty:
                avg_rrr = china_df['RR_Ratio'].mean()
                avg_prob = china_df['Prob%'].mean()
                avg_count = china_df['Count'].mean()
                num_stocks = len(china_df)
                
                return {
                    'threshold': threshold_multiplier,
                    'min_stats': min_stats,
                    'min_prob': min_prob,
                    'avg_rrr': avg_rrr,
                    'avg_prob': avg_prob,
                    'avg_count': avg_count,
                    'num_stocks': num_stocks,
                    'stocks': china_df[['Symbol', 'Prob%', 'RR_Ratio', 'Count']].to_dict('records')
                }
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all test combinations"""
    print("="*100)
    print("China Market RRR Tuning Test - ยืดหยุ่นและมีประสิทธิภาพจริงๆ")
    print("="*100)
    print(f"\nTesting {len(THRESHOLD_OPTIONS)} x {len(MIN_STATS_OPTIONS)} x {len(MIN_PROB_OPTIONS)} = {len(THRESHOLD_OPTIONS) * len(MIN_STATS_OPTIONS) * len(MIN_PROB_OPTIONS)} combinations")
    print(f"\n📋 Test Parameters:")
    print(f"  - Threshold: {THRESHOLD_OPTIONS} (เน้นคุณภาพ)")
    print(f"  - Min Stats: {MIN_STATS_OPTIONS} (เพิ่มความน่าเชื่อถือ)")
    print(f"  - Min Prob: {MIN_PROB_OPTIONS}% (balance quality/quantity)")
    print(f"\n🎯 Target:")
    print(f"  - RRR > 1.2 (ดีขึ้นจาก 1.0-1.3)")
    print(f"  - Prob% > 50% (ยังคง realistic - Raw Prob%)")
    print(f"  - Count > 20 (ยังคงน่าเชื่อถือทางสถิติ)")
    print(f"  - หลีกเลี่ยง overfitting (ใช้ Raw Prob% ไม่ใช่ Elite Prob%)")
    print(f"  - ยืดหยุ่น (ไม่ lock ค่าไว้ตายตัว)")
    print()
    
    results = []
    total_combinations = len(THRESHOLD_OPTIONS) * len(MIN_STATS_OPTIONS) * len(MIN_PROB_OPTIONS)
    current = 0
    
    for threshold in THRESHOLD_OPTIONS:
        for min_stats in MIN_STATS_OPTIONS:
            for min_prob in MIN_PROB_OPTIONS:
                current += 1
                print(f"\n[{current}/{total_combinations}] Testing combination...")
                
                result = run_china_backtest(threshold, min_stats, min_prob, n_bars=2000)
                
                if result:
                    results.append(result)
                    print(f"✅ Result: Avg RRR={result['avg_rrr']:.2f}, Avg Prob%={result['avg_prob']:.1f}%, Avg Count={result['avg_count']:.0f}, Stocks={result['num_stocks']}")
                else:
                    print(f"❌ No results")
                
                # Small delay to avoid rate limiting
                time.sleep(2)
    
    # Analyze results
    if results:
        print("\n" + "="*100)
        print("RESULTS SUMMARY")
        print("="*100)
        
        # Sort by RRR
        results_sorted = sorted(results, key=lambda x: x['avg_rrr'], reverse=True)
        
        print(f"\n📊 Top 10 Combinations (by Avg RRR):")
        print(f"{'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
        print("-" * 100)
        
        for r in results_sorted[:10]:
            print(f"{r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        
        # Filter by criteria - เน้นประสิทธิภาพจริงๆ
        print(f"\n🎯 Best Combinations (RRR > 1.2, Prob% > 50%, Count > 20):")
        print(f"{'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
        print("-" * 100)
        
        best_results = [r for r in results_sorted if r['avg_rrr'] > 1.2 and r['avg_prob'] > 50.0 and r['avg_count'] > 20]
        
        if best_results:
            for r in best_results[:5]:
                print(f"{r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        else:
            print("  (No combinations meet all criteria)")
            # Fallback: Best RRR with reasonable Prob% and Count
            print(f"\n💡 Best RRR Combinations (may not meet all criteria):")
            print(f"{'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
            print("-" * 100)
            for r in results_sorted[:3]:
                print(f"{r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        
        # Save results
        results_df = pd.DataFrame(results)
        results_df.to_csv('data/china_rrr_tuning_results.csv', index=False)
        print(f"\n💾 Results saved to: data/china_rrr_tuning_results.csv")
        
        # Recommend best combination - เน้นประสิทธิภาพและความยืดหยุ่น
        if best_results:
            best = best_results[0]
            print(f"\n💡 Recommended Combination (ยืดหยุ่นและมีประสิทธิภาพ):")
            print(f"   Threshold: {best['threshold']} (เพิ่มคุณภาพ pattern)")
            print(f"   Min Stats: {best['min_stats']} (เพิ่มความน่าเชื่อถือ)")
            print(f"   Min Prob: {best['min_prob']}% (balance quality/quantity)")
            print(f"   Expected Avg RRR: {best['avg_rrr']:.2f} (ดีขึ้นจาก 1.0-1.3)")
            print(f"   Expected Avg Prob%: {best['avg_prob']:.1f}% (Raw Prob% - realistic)")
            print(f"   Expected Avg Count: {best['avg_count']:.0f} (น่าเชื่อถือทางสถิติ)")
            print(f"   Expected Stocks: {best['num_stocks']} (หุ้นที่เทรดได้)")
            print(f"\n   ✅ ข้อดี:")
            print(f"      - RRR > 1.2 (ชนะได้กำไรมากกว่าขาดทุน)")
            print(f"      - ใช้ Raw Prob% (หลีกเลี่ยง overfitting)")
            print(f"      - Count > 20 (น่าเชื่อถือทางสถิติ)")
            print(f"      - ยืดหยุ่น (ไม่ lock ค่าไว้ตายตัว)")
        else:
            # Fallback: best RRR with reasonable criteria
            best = results_sorted[0]
            print(f"\n💡 Best RRR Combination (อาจไม่ผ่านทุก criteria):")
            print(f"   Threshold: {best['threshold']}")
            print(f"   Min Stats: {best['min_stats']}")
            print(f"   Min Prob: {best['min_prob']}%")
            print(f"   Avg RRR: {best['avg_rrr']:.2f}")
            print(f"   Avg Prob%: {best['avg_prob']:.1f}%")
            print(f"   Avg Count: {best['avg_count']:.0f}")
            print(f"   Stocks: {best['num_stocks']}")
            print(f"\n   ⚠️  ควรตรวจสอบ:")
            print(f"      - RRR อาจไม่ > 1.2")
            print(f"      - Count อาจไม่ > 20")
            print(f"      - ควรทดสอบเพิ่มเติม")
    else:
        print("\n❌ No results found")

if __name__ == "__main__":
    main()

