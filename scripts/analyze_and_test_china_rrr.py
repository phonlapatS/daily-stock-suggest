#!/usr/bin/env python
"""
Analyze Existing Results (Option 3) + Run New Tests (Option 1)
- วิเคราะห์ผลลัพธ์ที่มีอยู่ก่อน
- แล้วรันทดสอบเพิ่มเติมสำหรับค่าที่ยังไม่มี
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
THRESHOLD_OPTIONS = [0.9, 0.95]
MIN_STATS_OPTIONS = [25, 30]
MIN_PROB_OPTIONS = [50.0, 51.0]

# Fixed RM Parameters (V13.5 ATR-based)
RM_ATR_SL = 1.0
RM_ATR_TP = 4.0
RM_MAX_HOLD = 3
RM_TRAIL_ACTIVATE = 1.0
RM_TRAIL_DISTANCE = 40.0

def analyze_existing_results():
    """Option 3: วิเคราะห์ผลลัพธ์ที่มีอยู่"""
    print("="*100)
    print("OPTION 3: วิเคราะห์ผลลัพธ์ที่มีอยู่")
    print("="*100)
    
    results = []
    
    # Check symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            china_df = df[((df['Country'] == 'CN') | (df['Country'] == 'HK')) & 
                         (df['Prob%'] >= 50.0) & 
                         (df['RR_Ratio'] >= 1.0) & 
                         (df['Count'] >= 20)]
            
            if not china_df.empty:
                print(f"\n✅ Found {len(china_df)} China/HK stocks in symbol_performance.csv")
                print(f"   Avg RRR: {china_df['RR_Ratio'].mean():.2f}")
                print(f"   Avg Prob%: {china_df['Prob%'].mean():.1f}%")
                print(f"   Avg Count: {china_df['Count'].mean():.0f}")
                print(f"\n   Details:")
                # Get available columns (symbol or Symbol)
                symbol_col = 'symbol' if 'symbol' in china_df.columns else 'Symbol'
                detail_cols = [col for col in [symbol_col, 'Prob%', 'RR_Ratio', 'Count', 'AvgWin%', 'AvgLoss%'] if col in china_df.columns]
                print(china_df[detail_cols].to_string(index=False))
                
                # Estimate parameters from existing results
                # (We can't know exact parameters, but we can use current defaults)
                results.append({
                    'threshold': 0.9,  # Current default
                    'min_stats': 25,   # Current default
                    'min_prob': 50.0,  # Current default
                    'avg_rrr': china_df['RR_Ratio'].mean(),
                    'avg_prob': china_df['Prob%'].mean(),
                    'avg_count': china_df['Count'].mean(),
                    'num_stocks': len(china_df),
                    'source': 'existing'
                })
        except Exception as e:
            print(f"⚠️ Error reading {perf_file}: {e}")
    
    # Check trade_history_CHINA.csv
    log_file = 'logs/trade_history_CHINA.csv'
    if os.path.exists(log_file):
        try:
            df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
            print(f"\n✅ Found {len(df)} China/HK trades in trade_history_CHINA.csv")
            
            # Calculate metrics from trades
            if 'correct' in df.columns and 'trader_return' in df.columns:
                df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
                df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce').fillna(0)
                
                raw_prob = (df['correct'].sum() / len(df) * 100) if len(df) > 0 else 0
                wins = df[df['trader_return'] > 0]['trader_return'].abs()
                losses = df[df['trader_return'] <= 0]['trader_return'].abs()
                avg_win = wins.mean() if len(wins) > 0 else 0
                avg_loss = losses.mean() if len(losses) > 0 else 0
                rrr = avg_win / avg_loss if avg_loss > 0 else 0
                
                print(f"   Raw Prob%: {raw_prob:.1f}%")
                print(f"   RRR: {rrr:.2f}")
                print(f"   Avg Win: {avg_win:.2f}%")
                print(f"   Avg Loss: {avg_loss:.2f}%")
        except Exception as e:
            print(f"⚠️ Error reading {log_file}: {e}")
    
    if not results:
        print("\n⚠️ No existing results found")
    
    return results

def run_china_backtest(threshold_multiplier, min_stats, min_prob, n_bars=2000):
    """Run backtest for China market with specific parameters"""
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
        
        # Run backtest
        backtest_all(
            n_bars=n_bars,
            full_scan=True,
            target_group='CHINA',
            threshold_multiplier=threshold_multiplier,
            min_stats=min_stats,
            min_prob=min_prob,
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
                
                # Get available columns (symbol or Symbol)
                symbol_col = 'symbol' if 'symbol' in china_df.columns else 'Symbol'
                available_cols = [col for col in [symbol_col, 'Prob%', 'RR_Ratio', 'Count'] if col in china_df.columns]
                
                return {
                    'threshold': threshold_multiplier,
                    'min_stats': min_stats,
                    'min_prob': min_prob,
                    'avg_rrr': avg_rrr,
                    'avg_prob': avg_prob,
                    'avg_count': avg_count,
                    'num_stocks': num_stocks,
                    'stocks': china_df[available_cols].to_dict('records') if available_cols else [],
                    'source': 'new_test'
                }
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function - Option 3 + Option 1"""
    print("="*100)
    print("China Market RRR Tuning - Option 3 (Analyze Existing) + Option 1 (Run New Tests)")
    print("="*100)
    
    all_results = []
    
    # ====== OPTION 3: วิเคราะห์ผลลัพธ์ที่มีอยู่ ======
    existing_results = analyze_existing_results()
    all_results.extend(existing_results)
    
    # ====== OPTION 1: รันทดสอบใหม่ทั้งหมด ======
    print("\n" + "="*100)
    print("OPTION 1: รันทดสอบใหม่ทั้งหมด")
    print("="*100)
    print(f"\nTesting {len(THRESHOLD_OPTIONS)} x {len(MIN_STATS_OPTIONS)} x {len(MIN_PROB_OPTIONS)} = {len(THRESHOLD_OPTIONS) * len(MIN_STATS_OPTIONS) * len(MIN_PROB_OPTIONS)} combinations")
    print(f"\n📋 Test Parameters:")
    print(f"  - Threshold: {THRESHOLD_OPTIONS}")
    print(f"  - Min Stats: {MIN_STATS_OPTIONS}")
    print(f"  - Min Prob: {MIN_PROB_OPTIONS}%")
    print(f"\n🎯 Target:")
    print(f"  - RRR > 1.2 (ดีขึ้นจาก 1.0-1.3)")
    print(f"  - Prob% > 50% (ยังคง realistic - Raw Prob%)")
    print(f"  - Count > 20 (ยังคงน่าเชื่อถือทางสถิติ)")
    print()
    
    total_combinations = len(THRESHOLD_OPTIONS) * len(MIN_STATS_OPTIONS) * len(MIN_PROB_OPTIONS)
    current = 0
    
    for threshold in THRESHOLD_OPTIONS:
        for min_stats in MIN_STATS_OPTIONS:
            for min_prob in MIN_PROB_OPTIONS:
                current += 1
                print(f"\n[{current}/{total_combinations}] Testing combination...")
                
                result = run_china_backtest(threshold, min_stats, min_prob, n_bars=2000)
                
                if result:
                    all_results.append(result)
                    print(f"✅ Result: Avg RRR={result['avg_rrr']:.2f}, Avg Prob%={result['avg_prob']:.1f}%, Avg Count={result['avg_count']:.0f}, Stocks={result['num_stocks']}")
                else:
                    print(f"❌ No results")
                
                # Small delay to avoid rate limiting
                time.sleep(2)
    
    # ====== ANALYZE ALL RESULTS ======
    if all_results:
        print("\n" + "="*100)
        print("RESULTS SUMMARY (Existing + New Tests)")
        print("="*100)
        
        # Sort by RRR
        results_sorted = sorted(all_results, key=lambda x: x['avg_rrr'], reverse=True)
        
        print(f"\n📊 All Combinations (by Avg RRR):")
        print(f"{'Source':<10} {'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
        print("-" * 100)
        
        for r in results_sorted:
            source = r.get('source', 'unknown')
            print(f"{source:<10} {r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        
        # Filter by criteria
        print(f"\n🎯 Best Combinations (RRR > 1.2, Prob% > 50%, Count > 20):")
        print(f"{'Source':<10} {'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
        print("-" * 100)
        
        best_results = [r for r in results_sorted if r['avg_rrr'] > 1.2 and r['avg_prob'] > 50.0 and r['avg_count'] > 20]
        
        if best_results:
            for r in best_results[:5]:
                source = r.get('source', 'unknown')
                print(f"{source:<10} {r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        else:
            print("  (No combinations meet all criteria)")
            # Fallback: Best RRR
            print(f"\n💡 Best RRR Combinations (may not meet all criteria):")
            print(f"{'Source':<10} {'Threshold':<12} {'MinStats':<10} {'MinProb':<10} {'Avg RRR':<10} {'Avg Prob%':<12} {'Avg Count':<12} {'Stocks':<8}")
            print("-" * 100)
            for r in results_sorted[:3]:
                source = r.get('source', 'unknown')
                print(f"{source:<10} {r['threshold']:<12} {r['min_stats']:<10} {r['min_prob']:<10.1f} {r['avg_rrr']:<10.2f} {r['avg_prob']:<12.1f} {r['avg_count']:<12.0f} {r['num_stocks']:<8}")
        
        # Save results
        results_df = pd.DataFrame(all_results)
        results_df.to_csv('data/china_rrr_tuning_results.csv', index=False)
        print(f"\n💾 Results saved to: data/china_rrr_tuning_results.csv")
        
        # Recommend best combination
        if best_results:
            best = best_results[0]
            print(f"\n💡 Recommended Combination (ยืดหยุ่นและมีประสิทธิภาพ):")
            print(f"   Source: {best.get('source', 'unknown')}")
            print(f"   Threshold: {best['threshold']}")
            print(f"   Min Stats: {best['min_stats']}")
            print(f"   Min Prob: {best['min_prob']}%")
            print(f"   Expected Avg RRR: {best['avg_rrr']:.2f}")
            print(f"   Expected Avg Prob%: {best['avg_prob']:.1f}%")
            print(f"   Expected Avg Count: {best['avg_count']:.0f}")
            print(f"   Expected Stocks: {best['num_stocks']}")
        else:
            best = results_sorted[0]
            print(f"\n💡 Best RRR Combination (อาจไม่ผ่านทุก criteria):")
            print(f"   Source: {best.get('source', 'unknown')}")
            print(f"   Threshold: {best['threshold']}")
            print(f"   Min Stats: {best['min_stats']}")
            print(f"   Min Prob: {best['min_prob']}%")
            print(f"   Avg RRR: {best['avg_rrr']:.2f}")
            print(f"   Avg Prob%: {best['avg_prob']:.1f}%")
            print(f"   Avg Count: {best['avg_count']:.0f}")
            print(f"   Stocks: {best['num_stocks']}")
    else:
        print("\n❌ No results found")

if __name__ == "__main__":
    main()

