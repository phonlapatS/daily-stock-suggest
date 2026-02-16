#!/usr/bin/env python
"""
Test China Count Improvement - ทดสอบหลาย options เพื่อเพิ่ม Count

Options:
1. min_prob 50.0% → 49.5% (current n_bars 2000)
2. min_prob 50.0% → 49.0% (current n_bars 2000)
3. n_bars 2000 → 2500 (current min_prob 50.0%)
4. Combined: min_prob 49.5% + n_bars 2500
"""

import sys
import os
import subprocess
import time
import pandas as pd
import io
import shutil

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STOCK_NAMES = {
    '3690': 'MEITUAN',
    '1211': 'BYD',
    '9618': 'JD-COM',
    '2015': 'LI-AUTO',
    '700': 'TENCENT',
    '9988': 'ALIBABA',
    '1810': 'XIAOMI',
    '9888': 'BAIDU',
    '9868': 'XPENG',
    '9866': 'NIO'
}

def clean_results():
    """Clean old results"""
    files_to_remove = [
        'logs/trade_history_CHINA.csv',
        'data/full_backtest_results.csv'
    ]
    
    # Remove China stocks from symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            if 'Country' in df.columns:
                df = df[df['Country'] != 'CN']
                df.to_csv(perf_file, index=False)
        except:
            pass
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def run_backtest(min_prob=None, n_bars=2000):
    """Run backtest with specific parameters"""
    clean_results()
    
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', str(n_bars),
        '--group', 'CHINA',
        '--fast'
    ]
    
    if min_prob is not None:
        cmd.extend(['--min_prob', str(min_prob)])
    
    print(f"  Running: min_prob={min_prob or 50.0}%, n_bars={n_bars}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"  ❌ Backtest failed")
        return False
    
    # Calculate metrics
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    time.sleep(2)
    
    return True

def get_results():
    """Get results from symbol_performance.csv"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        return None
    
    # Current criteria
    CURRENT_RRR = 1.0
    CURRENT_COUNT = 15
    CURRENT_PROB = 53.0
    
    passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= CURRENT_COUNT)
    ].copy()
    
    return {
        'total_stocks': len(china_df),
        'passing_stocks': len(passing),
        'avg_count': china_df['Count'].mean(),
        'min_count': china_df['Count'].min(),
        'max_count': china_df['Count'].max(),
        'passing_avg_count': passing['Count'].mean() if len(passing) > 0 else 0,
        'passing_min_count': passing['Count'].min() if len(passing) > 0 else 0,
        'passing_max_count': passing['Count'].max() if len(passing) > 0 else 0,
        'avg_rrr': china_df['RR_Ratio'].mean(),
        'passing_avg_rrr': passing['RR_Ratio'].mean() if len(passing) > 0 else 0,
        'avg_prob': china_df['Prob%'].mean(),
        'passing_avg_prob': passing['Prob%'].mean() if len(passing) > 0 else 0,
        'stocks': passing.copy() if len(passing) > 0 else pd.DataFrame()
    }

def test_options():
    """Test different options"""
    print("="*100)
    print("China Market - Count Improvement Test")
    print("="*100)
    print("\n⚠️  เป้าหมาย: เพิ่ม Count โดยไม่ลดคุณภาพ")
    print("   - Count < 20: ไม่น่าเชื่อถือ")
    print("   - Count >= 30: น่าเชื่อถือ")
    print("")
    
    options = [
        {
            'name': 'Baseline (Current)',
            'min_prob': 50.0,
            'n_bars': 2000,
            'description': 'Current settings'
        },
        {
            'name': 'Option 1: Lower min_prob to 49.5%',
            'min_prob': 49.5,
            'n_bars': 2000,
            'description': 'Reduce min_prob by 0.5%'
        },
        {
            'name': 'Option 2: Lower min_prob to 49.0%',
            'min_prob': 49.0,
            'n_bars': 2000,
            'description': 'Reduce min_prob by 1.0%'
        },
        {
            'name': 'Option 3: Increase n_bars to 2500',
            'min_prob': 50.0,
            'n_bars': 2500,
            'description': 'More historical data'
        },
        {
            'name': 'Option 4: Combined (min_prob 49.5% + n_bars 2500)',
            'min_prob': 49.5,
            'n_bars': 2500,
            'description': 'Best of both'
        }
    ]
    
    results = []
    
    for i, option in enumerate(options, 1):
        print(f"\n{'='*100}")
        print(f"Test {i}/{len(options)}: {option['name']}")
        print(f"{'='*100}")
        print(f"  Description: {option['description']}")
        print(f"  Parameters: min_prob={option['min_prob']}%, n_bars={option['n_bars']}")
        print("")
        
        if run_backtest(min_prob=option['min_prob'], n_bars=option['n_bars']):
            result = get_results()
            if result:
                result['option'] = option['name']
                result['min_prob'] = option['min_prob']
                result['n_bars'] = option['n_bars']
                results.append(result)
                
                print(f"  ✅ Results:")
                print(f"     Passing stocks: {result['passing_stocks']}")
                print(f"     Avg Count: {result['passing_avg_count']:.0f}")
                print(f"     Min Count: {result['passing_min_count']:.0f}")
                print(f"     Avg RRR: {result['passing_avg_rrr']:.2f}")
                print(f"     Avg Prob%: {result['passing_avg_prob']:.1f}%")
            else:
                print(f"  ❌ No results found")
        else:
            print(f"  ❌ Test failed")
        
        time.sleep(3)  # Cool down between tests
    
    # Compare results
    print(f"\n{'='*100}")
    print("📊 Comparison of All Options:")
    print(f"{'='*100}")
    
    if len(results) > 0:
        print(f"\n{'Option':<40} {'Passing':<10} {'Avg Count':<12} {'Min Count':<12} {'Avg RRR':<10} {'Avg Prob%':<10}")
        print("-" * 100)
        
        baseline = results[0] if results else None
        
        for result in results:
            count_change = ""
            if baseline and result['option'] != baseline['option']:
                count_diff = result['passing_avg_count'] - baseline['passing_avg_count']
                if count_diff > 0:
                    count_change = f" (+{count_diff:.0f})"
                elif count_diff < 0:
                    count_change = f" ({count_diff:.0f})"
            
            print(f"{result['option']:<40} {result['passing_stocks']:<10} {result['passing_avg_count']:.0f}{count_change:<12} {result['passing_min_count']:.0f}{'':<12} {result['passing_avg_rrr']:.2f}{'':<10} {result['passing_avg_prob']:.1f}%")
        
        # Find best option
        print(f"\n{'='*100}")
        print("💡 Best Option Analysis:")
        print(f"{'='*100}")
        
        if baseline:
            best_count = max(results, key=lambda x: x['passing_avg_count'])
            best_min_count = max(results, key=lambda x: x['passing_min_count'])
            best_stocks = max(results, key=lambda x: x['passing_stocks'])
            
            print(f"\n  Best Avg Count: {best_count['option']}")
            print(f"    Avg Count: {best_count['passing_avg_count']:.0f} (vs baseline {baseline['passing_avg_count']:.0f})")
            
            print(f"\n  Best Min Count: {best_min_count['option']}")
            print(f"    Min Count: {best_min_count['passing_min_count']:.0f} (vs baseline {baseline['passing_min_count']:.0f})")
            
            print(f"\n  Most Stocks: {best_stocks['option']}")
            print(f"    Passing stocks: {best_stocks['passing_stocks']} (vs baseline {baseline['passing_stocks']})")
            
            # Recommendation
            print(f"\n  📊 Recommendation:")
            
            # Check if any option improves min_count significantly
            improved_min = [r for r in results if r['passing_min_count'] > baseline['passing_min_count'] + 2]
            if improved_min:
                best_improved = max(improved_min, key=lambda x: x['passing_min_count'])
                print(f"     ✅ {best_improved['option']}")
                print(f"        - Min Count: {best_improved['passing_min_count']:.0f} (เพิ่มจาก {baseline['passing_min_count']:.0f})")
                print(f"        - Avg Count: {best_improved['passing_avg_count']:.0f} (เพิ่มจาก {baseline['passing_avg_count']:.0f})")
                print(f"        - Passing stocks: {best_improved['passing_stocks']} (vs {baseline['passing_stocks']})")
            else:
                print(f"     ⚠️  ไม่มี option ที่เพิ่ม Count อย่างมีนัยสำคัญ")
                print(f"        - Baseline ดีอยู่แล้ว")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    test_options()

