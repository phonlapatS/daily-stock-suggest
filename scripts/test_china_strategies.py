#!/usr/bin/env python
"""
Test China Market - Different Strategies

ทดสอบ strategy หลายแบบสำหรับ China market:
1. MEAN_REVERSION (current)
2. TREND_FOLLOWING
3. US_HYBRID_VOL
4. REGIME_AWARE
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STRATEGIES = [
    ('MEAN_REVERSION', 'MEAN_REVERSION'),
    ('TREND_FOLLOWING', 'TREND_MOMENTUM'),
    ('US_HYBRID_VOL', 'TREND_MOMENTUM'),
    ('REGIME_AWARE', 'TREND_MOMENTUM'),
]

def modify_backtest_strategy(strategy_name):
    """Modify backtest.py to use specific strategy"""
    backtest_file = 'scripts/backtest.py'
    
    # Read file
    with open(backtest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace strategy assignment
    old_pattern = "elif is_thai_market or is_china_market:\n            strategy = \"MEAN_REVERSION\""
    new_pattern = f"elif is_thai_market:\n            strategy = \"MEAN_REVERSION\"\n        elif is_china_market:\n            strategy = \"{strategy_name}\""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
    else:
        # Try alternative pattern
        old_pattern = "elif is_thai_market or is_china_market:"
        new_pattern = f"elif is_thai_market:\n            strategy = \"MEAN_REVERSION\"\n        elif is_china_market:\n            strategy = \"{strategy_name}\""
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
    
    # Write back
    with open(backtest_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Modified backtest.py to use {strategy_name}")

def restore_backtest_strategy():
    """Restore original strategy"""
    backtest_file = 'scripts/backtest.py'
    
    # Read file
    with open(backtest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Restore original
    old_pattern = "elif is_thai_market:\n            strategy = \"MEAN_REVERSION\"\n        elif is_china_market:\n            strategy ="
    new_pattern = "elif is_thai_market or is_china_market:\n            strategy = \"MEAN_REVERSION\""
    
    # Find any china_market strategy and restore
    import re
    pattern = r"elif is_thai_market:\s+strategy = \"MEAN_REVERSION\"\s+elif is_china_market:\s+strategy = \"[^\"]+\""
    replacement = "elif is_thai_market or is_china_market:\n            strategy = \"MEAN_REVERSION\""
    content = re.sub(pattern, replacement, content)
    
    # Write back
    with open(backtest_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Restored original strategy")

def run_backtest(strategy_name, n_bars=2000):
    """Run backtest with specific strategy"""
    print(f"\n{'='*80}")
    print(f"Testing Strategy: {strategy_name}")
    print(f"{'='*80}")
    
    # Modify backtest.py
    modify_backtest_strategy(strategy_name)
    
    # Clean old results
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"✅ Removed {log_file}")
    
    # Run backtest
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', str(n_bars),
        '--group', 'CHINA',
        '--fast'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error running backtest:")
        print(result.stderr)
        return None
    
    # Wait a bit
    time.sleep(2)
    
    return True

def analyze_results(strategy_name):
    """Analyze results for specific strategy"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        return None
    
    result = {
        'strategy': strategy_name,
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
    print("China Market - Strategy Comparison Test")
    print("="*80)
    print(f"\nTesting Strategies: {[s[0] for s in STRATEGIES]}")
    print(f"Total tests: {len(STRATEGIES)}")
    
    results = []
    
    try:
        for strategy_name, engine_name in STRATEGIES:
            print(f"\n{'='*80}")
            print(f"Test {len(results)+1}/{len(STRATEGIES)}: {strategy_name}")
            print(f"{'='*80}")
            
            # Run backtest
            success = run_backtest(strategy_name)
            
            if not success:
                print(f"❌ Failed to run backtest for {strategy_name}")
                continue
            
            # Calculate metrics
            print(f"\nCalculating metrics...")
            subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
            
            # Analyze results
            result = analyze_results(strategy_name)
            
            if result:
                results.append(result)
                print(f"\n✅ Results for {strategy_name}:")
                print(f"   Stocks Passing: {result['stocks_passing']}")
                print(f"   Avg RRR: {result['avg_rrr']:.2f}")
                print(f"   Avg Prob%: {result['avg_prob']:.1f}%")
                print(f"   Total Count: {result['total_count']}")
            else:
                print(f"⚠️  No results for {strategy_name}")
            
            # Small delay
            time.sleep(1)
    
    finally:
        # Restore original strategy
        restore_backtest_strategy()
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv('data/china_strategy_comparison.csv', index=False)
        print(f"\n✅ Results saved to data/china_strategy_comparison.csv")
        
        # Print comparison table
        print(f"\n{'='*80}")
        print("Comparison Table")
        print(f"{'='*80}")
        print(results_df[['strategy', 'stocks_passing', 'avg_rrr', 'avg_prob', 
                          'total_count', 'best_rrr']].to_string(index=False))
        
        # Recommendations
        print(f"\n{'='*80}")
        print("Recommendations")
        print(f"{'='*80}")
        
        best_rrr = results_df.loc[results_df['avg_rrr'].idxmax()]
        most_stocks = results_df.loc[results_df['stocks_passing'].idxmax()]
        
        print(f"\n  Best RRR: {best_rrr['strategy']} (RRR = {best_rrr['avg_rrr']:.2f})")
        print(f"  Most Stocks: {most_stocks['strategy']} ({most_stocks['stocks_passing']} stocks)")
    else:
        print(f"\n⚠️  No results to compare")
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()

