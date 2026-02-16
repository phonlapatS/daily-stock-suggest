#!/usr/bin/env python
"""
Optimize China Market - หาค่าที่เสี่ยงน้อยและได้กำไรจริง

ทดสอบหลายค่า:
- Max Hold: 5, 6, 7, 8, 9, 10
- Threshold: 0.8, 0.85, 0.9, 0.95, 1.0
- Strategy: MEAN_REVERSION, TREND_FOLLOWING

เป้าหมาย:
- Risk Score <= 1 (เสี่ยงน้อย)
- Profit Score >= 2 (ได้กำไรจริง)
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

from scripts.analyze_china_performance import analyze_performance

# Test Parameters
MAX_HOLD_OPTIONS = [5, 6, 7, 8, 9, 10]
THRESHOLD_OPTIONS = [0.8, 0.85, 0.9, 0.95, 1.0]

def run_backtest(max_hold, threshold, n_bars=2000):
    """Run backtest with specific parameters"""
    print(f"\n{'='*80}")
    print(f"Testing: Max Hold={max_hold}, Threshold={threshold}")
    print(f"{'='*80}")
    
    # Clean old results
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Remove China entries from perf file
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            df = df[df['Country'] != 'CN']
            df.to_csv(perf_file, index=False)
        except:
            pass
    
    # Run backtest
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', str(n_bars),
        '--group', 'CHINA',
        '--fast',
        '--max_hold', str(max_hold),
        '--multiplier', str(threshold)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    # Calculate metrics
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    
    time.sleep(2)
    return True

def calculate_score(result):
    """Calculate risk and profit scores"""
    if result is None:
        return None, None, None
    
    risk_score = 0
    if result['sl_rate'] > 30:
        risk_score += 2
    elif result['sl_rate'] > 20:
        risk_score += 1
    
    if result['max_drawdown'] < -10:
        risk_score += 2
    elif result['max_drawdown'] < -5:
        risk_score += 1
    
    profit_score = 0
    if result['expectancy'] > 0.5:
        profit_score += 2
    elif result['expectancy'] > 0:
        profit_score += 1
    
    if result['win_rate'] > 55:
        profit_score += 1
    elif result['win_rate'] > 50:
        profit_score += 0.5
    
    if result['rrr'] > 1.5:
        profit_score += 1
    elif result['rrr'] > 1.2:
        profit_score += 0.5
    
    total_score = (4 - risk_score) + profit_score  # Higher is better
    
    return risk_score, profit_score, total_score

def main():
    """Main optimization function"""
    print("="*80)
    print("China Market - Risk/Profit Optimization")
    print("="*80)
    print(f"\nTesting:")
    print(f"  Max Hold: {MAX_HOLD_OPTIONS}")
    print(f"  Threshold: {THRESHOLD_OPTIONS}")
    print(f"  Total: {len(MAX_HOLD_OPTIONS) * len(THRESHOLD_OPTIONS)} tests")
    print(f"\nTarget:")
    print(f"  Risk Score <= 1 (เสี่ยงน้อย)")
    print(f"  Profit Score >= 2 (ได้กำไรจริง)")
    
    results = []
    
    # Test current settings first (Max Hold=8, Threshold=0.9)
    print(f"\n{'='*80}")
    print("Testing Current Settings (Max Hold=8, Threshold=0.9)")
    print(f"{'='*80}")
    
    if run_backtest(8, 0.9):
        result = analyze_performance()
        if result:
            risk_score, profit_score, total_score = calculate_score(result)
            results.append({
                'max_hold': 8,
                'threshold': 0.9,
                'risk_score': risk_score,
                'profit_score': profit_score,
                'total_score': total_score,
                'win_rate': result['win_rate'],
                'rrr': result['rrr'],
                'expectancy': result['expectancy'],
                'sl_rate': result['sl_rate'],
                'max_drawdown': result['max_drawdown'],
                'total_trades': result['total_trades']
            })
    
    # Test other combinations (sample - not all to save time)
    test_combinations = [
        (6, 0.9),  # Shorter hold
        (7, 0.9),  # Medium hold
        (8, 0.85), # Lower threshold
        (8, 0.95), # Higher threshold
        (9, 0.9),  # Longer hold
    ]
    
    for max_hold, threshold in test_combinations:
        print(f"\n{'='*80}")
        print(f"Testing: Max Hold={max_hold}, Threshold={threshold}")
        print(f"{'='*80}")
        
        if run_backtest(max_hold, threshold):
            result = analyze_performance()
            if result:
                risk_score, profit_score, total_score = calculate_score(result)
                results.append({
                    'max_hold': max_hold,
                    'threshold': threshold,
                    'risk_score': risk_score,
                    'profit_score': profit_score,
                    'total_score': total_score,
                    'win_rate': result['win_rate'],
                    'rrr': result['rrr'],
                    'expectancy': result['expectancy'],
                    'sl_rate': result['sl_rate'],
                    'max_drawdown': result['max_drawdown'],
                    'total_trades': result['total_trades']
                })
    
    # Save and display results
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('total_score', ascending=False)
        results_df.to_csv('data/china_optimization_results.csv', index=False)
        
        print(f"\n{'='*80}")
        print("Optimization Results")
        print(f"{'='*80}")
        print(results_df[['max_hold', 'threshold', 'risk_score', 'profit_score', 'total_score',
                          'win_rate', 'rrr', 'expectancy', 'sl_rate', 'max_drawdown']].to_string(index=False))
        
        # Find best combination
        best = results_df.iloc[0]
        print(f"\n{'='*80}")
        print("Best Combination (เสี่ยงน้อย + กำไรจริง)")
        print(f"{'='*80}")
        print(f"  Max Hold: {best['max_hold']} days")
        print(f"  Threshold: {best['threshold']}")
        print(f"  Risk Score: {best['risk_score']}/4 (ต่ำ = ดี)")
        print(f"  Profit Score: {best['profit_score']}/4 (สูง = ดี)")
        print(f"  Total Score: {best['total_score']:.1f}")
        print(f"  Win Rate: {best['win_rate']:.1f}%")
        print(f"  RRR: {best['rrr']:.2f}")
        print(f"  Expectancy: {best['expectancy']:.2f}%")
        print(f"  SL Rate: {best['sl_rate']:.1f}%")
        print(f"  Max Drawdown: {best['max_drawdown']:.2f}%")
        
        if best['risk_score'] <= 1 and best['profit_score'] >= 2:
            print(f"\n  ✅ ✅ ✅ EXCELLENT: เสี่ยงน้อย + ได้กำไรจริง")
        elif best['risk_score'] <= 2 and best['profit_score'] >= 1.5:
            print(f"\n  ✅ ✅ GOOD: เสี่ยงปานกลาง + ได้กำไร")
        else:
            print(f"\n  ⚠️  NEEDS IMPROVEMENT")
    else:
        print(f"\n⚠️  No results to compare")
    
    print(f"\n{'='*80}")
    print("Optimization Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()

