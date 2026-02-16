#!/usr/bin/env python
"""
Test China Realistic Prob% - ทดสอบ threshold_multiplier, min_stats, min_prob เพื่อให้ Prob% realistic มากขึ้น
"""

import sys
import os
import pandas as pd
import subprocess
import time
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_china_cache():
    """ลบ cache files เพื่อบังคับให้รัน backtest ใหม่"""
    files_to_clean = [
        'logs/trade_history_CHINA.csv',
        'data/symbol_performance.csv'
    ]
    
    # Clean full_backtest_results.csv (เฉพาะ China/HK entries)
    full_results_file = 'data/full_backtest_results.csv'
    if os.path.exists(full_results_file):
        try:
            df = pd.read_csv(full_results_file, on_bad_lines='skip', engine='python')
            if 'country' in df.columns:
                # Remove China/HK entries
                df_cleaned = df[~df['country'].isin(['CN', 'HK'])]
                df_cleaned.to_csv(full_results_file, index=False)
                print(f"✅ Cleaned China/HK entries from {full_results_file}")
        except Exception as e:
            print(f"⚠️  Could not clean {full_results_file}: {e}")
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed {file}")
            except Exception as e:
                print(f"⚠️  Could not remove {file}: {e}")

def run_backtest(threshold_multiplier, min_stats, min_prob):
    """รัน backtest ด้วย parameters ที่กำหนด"""
    print(f"\n{'='*100}")
    print(f"Testing: threshold_multiplier={threshold_multiplier}, min_stats={min_stats}, min_prob={min_prob}%")
    print(f"{'='*100}\n")
    
    # Clean cache first
    clean_china_cache()
    
    # Run backtest
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', '2000',
        '--group', 'CHINA',
        '--multiplier', str(threshold_multiplier),
        '--min_stats', str(min_stats),
        '--min_prob', str(min_prob)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    if result.returncode != 0:
        print(f"❌ Backtest failed: {result.stderr}")
        return None
    
    # Run calculate_metrics
    cmd_metrics = ['python', 'scripts/calculate_metrics.py']
    result_metrics = subprocess.run(cmd_metrics, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    if result_metrics.returncode != 0:
        print(f"❌ Calculate metrics failed: {result_metrics.stderr}")
        return None
    
    # Wait a bit for file to be written
    time.sleep(2)
    
    return True

def analyze_results(threshold_multiplier, min_stats, min_prob):
    """วิเคราะห์ผลลัพธ์"""
    trade_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(trade_file) or not os.path.exists(perf_file):
        return None
    
    # Load trade history
    df_trades = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    df_perf = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
    
    # Filter China/HK
    china_perf = df_perf[(df_perf['Country'].isin(['CN', 'HK']))].copy()
    
    # Apply display criteria
    display_criteria = china_perf[
        (china_perf['Prob%'] >= 60.0) &
        (china_perf['RR_Ratio'] >= 1.0) &
        (china_perf['Count'] >= 20)
    ]
    
    # Calculate metrics
    total_trades = len(df_trades)
    if total_trades == 0:
        return None
    
    df_trades['correct'] = pd.to_numeric(df_trades['correct'], errors='coerce').fillna(0)
    df_trades['prob'] = pd.to_numeric(df_trades['prob'], errors='coerce').fillna(0)
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce').fillna(0)
    
    raw_wins = int(df_trades['correct'].sum())
    raw_prob = (raw_wins / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate RRR
    df_trades['pnl'] = df_trades.apply(
        lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
        axis=1
    )
    wins = df_trades[df_trades['pnl'] > 0]
    losses = df_trades[df_trades['pnl'] <= 0]
    avg_win = wins['pnl'].mean() if not wins.empty else 0
    avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Calculate average Prob% from display criteria
    avg_prob = display_criteria['Prob%'].mean() if len(display_criteria) > 0 else 0
    avg_rrr = display_criteria['RR_Ratio'].mean() if len(display_criteria) > 0 else 0
    total_count = display_criteria['Count'].sum() if len(display_criteria) > 0 else 0
    
    # Check historical prob distribution
    below_54 = len(df_trades[df_trades['prob'] < 54.0])
    below_55 = len(df_trades[df_trades['prob'] < 55.0])
    below_56 = len(df_trades[df_trades['prob'] < 56.0])
    
    return {
        'threshold_multiplier': threshold_multiplier,
        'min_stats': min_stats,
        'min_prob': min_prob,
        'total_trades': total_trades,
        'raw_prob': raw_prob,
        'avg_prob': avg_prob,
        'num_stocks': len(display_criteria),
        'avg_rrr': avg_rrr,
        'total_count': total_count,
        'below_54': below_54,
        'below_55': below_55,
        'below_56': below_56,
        'rrr': rrr,
        'name': ''  # Will be filled in main()
    }

def main():
    """Main function"""
    print("="*100)
    print("Test China Realistic Prob% - ทดสอบ threshold_multiplier, min_stats, min_prob")
    print("="*100)
    print()
    print("Goal: ลด Prob% ให้ realistic มากขึ้น (60-65%)")
    print("      โดยยังคง RRR >= 1.40, Stocks >= 4, Count >= 20")
    print()
    
    # Test parameters - Focus on most promising combinations
    test_configs = [
        # Baseline (current V13.9)
        {'threshold_multiplier': 0.9, 'min_stats': 30, 'min_prob': 54.0, 'name': 'Baseline (V13.9)'},
        
        # Option 1: Increase threshold_multiplier only (most likely to work)
        {'threshold_multiplier': 1.0, 'min_stats': 30, 'min_prob': 54.0, 'name': 'th=1.0'},
        {'threshold_multiplier': 1.1, 'min_stats': 30, 'min_prob': 54.0, 'name': 'th=1.1'},
        
        # Option 2: Increase min_stats only
        {'threshold_multiplier': 0.9, 'min_stats': 35, 'min_prob': 54.0, 'name': 'stats=35'},
        {'threshold_multiplier': 0.9, 'min_stats': 40, 'min_prob': 54.0, 'name': 'stats=40'},
        
        # Option 3: Increase min_prob only (gatekeeper - but may not help much)
        {'threshold_multiplier': 0.9, 'min_stats': 30, 'min_prob': 55.0, 'name': 'prob=55%'},
        {'threshold_multiplier': 0.9, 'min_stats': 30, 'min_prob': 56.0, 'name': 'prob=56%'},
        
        # Option 4: Combined - threshold_multiplier + min_stats (most promising)
        {'threshold_multiplier': 1.0, 'min_stats': 35, 'min_prob': 54.0, 'name': 'th=1.0, stats=35'},
        {'threshold_multiplier': 1.0, 'min_stats': 40, 'min_prob': 54.0, 'name': 'th=1.0, stats=40'},
        
        # Option 5: Combined - threshold_multiplier + min_prob
        {'threshold_multiplier': 1.0, 'min_stats': 30, 'min_prob': 55.0, 'name': 'th=1.0, prob=55%'},
        
        # Option 6: All combined (most aggressive)
        {'threshold_multiplier': 1.0, 'min_stats': 35, 'min_prob': 55.0, 'name': 'th=1.0, stats=35, prob=55%'},
        {'threshold_multiplier': 1.1, 'min_stats': 35, 'min_prob': 55.0, 'name': 'th=1.1, stats=35, prob=55%'},
    ]
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{'#'*100}")
        print(f"Test {i}/{len(test_configs)}: {config.get('name', 'Unknown')}")
        print(f"{'#'*100}\n")
        
        success = run_backtest(
            config['threshold_multiplier'],
            config['min_stats'],
            config['min_prob']
        )
        
        if success:
            result = analyze_results(
                config['threshold_multiplier'],
                config['min_stats'],
                config['min_prob']
            )
            if result:
                result['name'] = config.get('name', 'Unknown')
                results.append(result)
                print(f"\n✅ Test {i} Results ({config.get('name', 'Unknown')}):")
                print(f"   Raw Prob%: {result['raw_prob']:.1f}%")
                print(f"   Avg Prob%: {result['avg_prob']:.1f}%")
                print(f"   Stocks: {result['num_stocks']}")
                print(f"   Avg RRR: {result['avg_rrr']:.2f}")
                print(f"   Total Count: {result['total_count']}")
                print(f"   Trades with prob < 54%: {result['below_54']}")
            else:
                print(f"❌ Test {i} failed to analyze results")
        else:
            print(f"❌ Test {i} failed")
        
        # Wait between tests
        if i < len(test_configs):
            print(f"\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY - สรุปผลการทดสอบ")
    print("="*100)
    print()
    
    if not results:
        print("❌ No results to summarize")
        return
    
    # Create summary DataFrame
    df_summary = pd.DataFrame(results)
    
    # Sort by raw_prob (ascending - lower is better for realistic)
    df_summary = df_summary.sort_values('raw_prob')
    
    print(f"{'Name':<35} {'Raw Prob%':<15} {'Avg Prob%':<15} {'Stocks':<10} {'Avg RRR':<12} {'Total Count':<15} {'Below 54%':<12}")
    print("-" * 100)
    
    for _, row in df_summary.iterrows():
        name = row.get('name', f"th={row['threshold_multiplier']:.1f}, stats={row['min_stats']}, prob={row['min_prob']:.1f}%")
        print(f"{name:<35} {row['raw_prob']:<15.1f} {row['avg_prob']:<15.1f} {row['num_stocks']:<10} {row['avg_rrr']:<12.2f} {row['total_count']:<15} {row['below_54']:<12}")
    
    print()
    
    # Find best config
    print("="*100)
    print("BEST CONFIGURATIONS - ค่าที่ดีที่สุด")
    print("="*100)
    print()
    
    # Filter by criteria
    criteria_met = df_summary[
        (df_summary['raw_prob'] >= 60.0) & (df_summary['raw_prob'] <= 65.0) &
        (df_summary['avg_rrr'] >= 1.40) &
        (df_summary['num_stocks'] >= 4) &
        (df_summary['total_count'] >= 80)  # At least 4 stocks * 20 trades
    ]
    
    if len(criteria_met) > 0:
        print("✅ Configurations that meet all criteria (Prob% 60-65%, RRR >= 1.40, Stocks >= 4):")
        print()
        for _, row in criteria_met.iterrows():
            name = row.get('name', f"th={row['threshold_multiplier']:.1f}, stats={row['min_stats']}, prob={row['min_prob']:.1f}%")
            config_str = f"threshold_multiplier={row['threshold_multiplier']:.1f}, min_stats={row['min_stats']}, min_prob={row['min_prob']:.1f}%"
            print(f"  {name}")
            print(f"    Config: {config_str}")
            print(f"    Raw Prob%: {row['raw_prob']:.1f}%")
            print(f"    Avg Prob%: {row['avg_prob']:.1f}%")
            print(f"    Stocks: {row['num_stocks']}")
            print(f"    Avg RRR: {row['avg_rrr']:.2f}")
            print(f"    Total Count: {row['total_count']}")
            print()
    else:
        print("⚠️  No configuration meets all criteria")
        print()
        print("Best compromise (closest to criteria):")
        best = df_summary.iloc[0]
        name = best.get('name', f"th={best['threshold_multiplier']:.1f}, stats={best['min_stats']}, prob={best['min_prob']:.1f}%")
        config_str = f"threshold_multiplier={best['threshold_multiplier']:.1f}, min_stats={best['min_stats']}, min_prob={best['min_prob']:.1f}%"
        print(f"  {name}")
        print(f"    Config: {config_str}")
        print(f"    Raw Prob%: {best['raw_prob']:.1f}%")
        print(f"    Avg Prob%: {best['avg_prob']:.1f}%")
        print(f"    Stocks: {best['num_stocks']}")
        print(f"    Avg RRR: {best['avg_rrr']:.2f}")
        print(f"    Total Count: {best['total_count']}")
        print()
    
    # Save results
    output_file = 'data/china_realistic_prob_test_results.csv'
    df_summary.to_csv(output_file, index=False)
    print(f"💾 Saved results to: {output_file}")

if __name__ == "__main__":
    main()

