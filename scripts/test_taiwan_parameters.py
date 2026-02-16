#!/usr/bin/env python
"""
Taiwan Market Parameter Testing Script
ทดสอบหลายค่า min_prob และ n_bars เพื่อหาค่าที่เหมาะสมที่สุด
"""

import pandas as pd
import subprocess
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def run_backtest(min_prob, n_bars=2000, group='TAIWAN'):
    """
    Run backtest with specific parameters
    
    Args:
        min_prob: Minimum probability threshold (51.0, 51.5, 52.0, etc.)
        n_bars: Number of historical bars (2000, 2500, 3000)
        group: Market group (TAIWAN)
    """
    print(f"\n{'='*80}")
    print(f"Testing: min_prob={min_prob}%, n_bars={n_bars}")
    print(f"{'='*80}")
    
    # Modify backtest.py temporarily
    backtest_file = project_root / 'scripts' / 'backtest.py'
    
    # Read current file
    with open(backtest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace min_prob for Taiwan
    import re
    pattern = r"(elif is_tw_market:\s+min_prob = )[\d.]+"
    replacement = f"\\g<1>{min_prob}"
    new_content = re.sub(pattern, replacement, content)
    
    # Write modified file
    backup_file = backtest_file.with_suffix('.py.bak')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)  # Backup original
    
    with open(backtest_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    try:
        # Clean old results
        trade_history = project_root / 'logs' / 'trade_history_TAIWAN.csv'
        if trade_history.exists():
            trade_history.unlink()
        
        # Run backtest
        cmd = [
            sys.executable,
            'scripts/backtest.py',
            '--full',
            '--bars', str(n_bars),
            '--group', group
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return None
        
        # Calculate metrics
        cmd_metrics = [sys.executable, 'scripts/calculate_metrics.py']
        result_metrics = subprocess.run(cmd_metrics, cwd=project_root, capture_output=True, text=True)
        
        if result_metrics.returncode != 0:
            print(f"❌ Metrics Error: {result_metrics.stderr}")
            return None
        
        # Read results
        metrics_file = project_root / 'data' / 'symbol_performance.csv'
        if not metrics_file.exists():
            print("❌ Metrics file not found")
            return None
        
        df = pd.read_csv(metrics_file)
        taiwan = df[df['Country'] == 'TW'].copy()
        
        # Filter by criteria
        passing = taiwan[
            (taiwan['Prob%'] >= 53.0) &
            (taiwan['RR_Ratio'] >= 1.3) &
            (taiwan['Count'] >= 25) &
            (taiwan['Count'] <= 150)
        ]
        
        return {
            'min_prob': min_prob,
            'n_bars': n_bars,
            'total_taiwan_stocks': len(taiwan),
            'passing_stocks': len(passing),
            'passing_symbols': passing['symbol'].tolist() if not passing.empty else [],
            'avg_prob': passing['Prob%'].mean() if not passing.empty else 0,
            'avg_rrr': passing['RR_Ratio'].mean() if not passing.empty else 0,
            'avg_count': passing['Count'].mean() if not passing.empty else 0,
            'total_trades': passing['Count'].sum() if not passing.empty else 0,
            'details': passing[['symbol', 'Prob%', 'RR_Ratio', 'Count']].to_dict('records') if not passing.empty else []
        }
    
    finally:
        # Restore original file
        if backup_file.exists():
            with open(backup_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(backtest_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            backup_file.unlink()

def main():
    """Main testing function"""
    print("\n" + "="*80)
    print("Taiwan Market Parameter Testing")
    print("="*80)
    print("\nThis script will test multiple parameter combinations:")
    print("- min_prob: 51.0%, 51.5%, 52.0%, 52.5%")
    print("- n_bars: 2000, 2500, 3000")
    print("\n⚠️  This will take a LONG time (multiple backtest runs)")
    print("⚠️  Each backtest may take 10-30 minutes")
    print("\nDo you want to continue? (y/n): ", end='')
    
    response = input().strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Test parameters
    min_prob_values = [51.0, 51.5, 52.0, 52.5]
    n_bars_values = [2000, 2500, 3000]
    
    results = []
    
    for min_prob in min_prob_values:
        for n_bars in n_bars_values:
            result = run_backtest(min_prob, n_bars)
            if result:
                results.append(result)
    
    # Save results
    results_df = pd.DataFrame(results)
    output_file = project_root / 'docs' / 'TAIWAN_PARAMETER_TEST_RESULTS.csv'
    results_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print("Results Summary")
    print(f"{'='*80}")
    print(results_df.to_string(index=False))
    print(f"\n✅ Results saved to: {output_file}")
    
    # Find best combination
    if not results_df.empty:
        best = results_df.loc[results_df['passing_stocks'].idxmax()]
        print(f"\n{'='*80}")
        print("Best Combination (Most Passing Stocks)")
        print(f"{'='*80}")
        print(f"min_prob: {best['min_prob']}%")
        print(f"n_bars: {best['n_bars']}")
        print(f"Passing Stocks: {best['passing_stocks']}")
        print(f"Avg Prob%: {best['avg_prob']:.2f}%")
        print(f"Avg RRR: {best['avg_rrr']:.2f}")
        print(f"Avg Count: {best['avg_count']:.1f}")
        print(f"Total Trades: {best['total_trades']:.0f}")

if __name__ == '__main__':
    main()

