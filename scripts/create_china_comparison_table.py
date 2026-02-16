#!/usr/bin/env python
"""
Create China Market Comparison Table - สร้างตารางเปรียบเทียบผลลัพธ์

ทดสอบหลายค่าและสร้างตารางเปรียบเทียบ:
- Max Hold: 5, 6, 7, 8, 9, 10
- Threshold: 0.85, 0.9, 0.95
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

# Test Parameters
MAX_HOLD_OPTIONS = [5, 6, 7, 8, 9, 10]
THRESHOLD_OPTIONS = [0.85, 0.9, 0.95]

def run_backtest(max_hold, threshold, n_bars=2000):
    """Run backtest with specific parameters"""
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
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return False
    
    # Calculate metrics
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    
    time.sleep(2)
    return True

def analyze_results(max_hold, threshold):
    """Analyze results for specific parameters"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        return None
    
    df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df_trades) == 0:
        return None
    
    # Convert to numeric
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
    df_trades['trader_return'] = pd.to_numeric(df_trades['trader_return'], errors='coerce')
    df_trades['hold_days'] = pd.to_numeric(df_trades['hold_days'], errors='coerce')
    
    # Remove invalid rows
    df_trades = df_trades.dropna(subset=['actual_return'])
    
    if len(df_trades) == 0:
        return None
    
    # Calculate metrics
    wins = df_trades[df_trades['actual_return'] > 0]
    losses = df_trades[df_trades['actual_return'] <= 0]
    
    total_trades = len(df_trades)
    win_count = len(wins)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    
    avg_return = df_trades['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    expectancy = avg_return
    
    # Exit reasons
    sl_hits = len(df_trades[df_trades['exit_reason'] == 'STOP_LOSS']) if 'exit_reason' in df_trades.columns else 0
    tp_hits = len(df_trades[df_trades['exit_reason'] == 'TAKE_PROFIT']) if 'exit_reason' in df_trades.columns else 0
    max_hold_exits = len(df_trades[df_trades['exit_reason'] == 'MAX_HOLD']) if 'exit_reason' in df_trades.columns else 0
    
    sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
    tp_rate = (tp_hits / total_trades) * 100 if total_trades > 0 else 0
    max_hold_rate = (max_hold_exits / total_trades) * 100 if total_trades > 0 else 0
    
    # Max drawdown
    cumulative = df_trades['actual_return'].cumsum()
    running_max = cumulative.expanding().max()
    drawdown = cumulative - running_max
    max_drawdown = drawdown.min()
    
    # Avg hold days
    avg_hold_days = df_trades['hold_days'].mean() if 'hold_days' in df_trades.columns else 0
    
    # Stocks passing
    stocks_passing = 0
    if os.path.exists(perf_file):
        try:
            df_perf = pd.read_csv(perf_file)
            china_perf = df_perf[df_perf['Country'] == 'CN']
            stocks_passing = len(china_perf)
        except:
            pass
    
    # Risk and profit scores
    risk_score = 0
    if sl_rate > 30:
        risk_score += 2
    elif sl_rate > 20:
        risk_score += 1
    
    if max_drawdown < -10:
        risk_score += 2
    elif max_drawdown < -5:
        risk_score += 1
    
    profit_score = 0
    if expectancy > 0.5:
        profit_score += 2
    elif expectancy > 0:
        profit_score += 1
    
    if win_rate > 55:
        profit_score += 1
    elif win_rate > 50:
        profit_score += 0.5
    
    if rrr > 1.5:
        profit_score += 1
    elif rrr > 1.2:
        profit_score += 0.5
    
    total_score = (4 - risk_score) + profit_score
    
    result = {
        'max_hold': max_hold,
        'threshold': threshold,
        'stocks_passing': stocks_passing,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'rrr': rrr,
        'expectancy': expectancy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'sl_rate': sl_rate,
        'tp_rate': tp_rate,
        'max_hold_rate': max_hold_rate,
        'max_drawdown': max_drawdown,
        'avg_hold_days': avg_hold_days,
        'risk_score': risk_score,
        'profit_score': profit_score,
        'total_score': total_score
    }
    
    return result

def create_comparison_table():
    """Create comparison table"""
    print("="*100)
    print("China Market - Comparison Table")
    print("="*100)
    print(f"\nTesting Parameters:")
    print(f"  Max Hold: {MAX_HOLD_OPTIONS}")
    print(f"  Threshold: {THRESHOLD_OPTIONS}")
    print(f"  Total Tests: {len(MAX_HOLD_OPTIONS) * len(THRESHOLD_OPTIONS)}")
    print(f"\nThis will take some time...")
    
    results = []
    
    # Test all combinations
    for max_hold in MAX_HOLD_OPTIONS:
        for threshold in THRESHOLD_OPTIONS:
            print(f"\n{'='*100}")
            print(f"Testing: Max Hold={max_hold}, Threshold={threshold}")
            print(f"{'='*100}")
            
            if run_backtest(max_hold, threshold):
                result = analyze_results(max_hold, threshold)
                if result:
                    results.append(result)
                    print(f"✅ Results: {result['stocks_passing']} stocks, Win Rate: {result['win_rate']:.1f}%, RRR: {result['rrr']:.2f}")
                else:
                    print(f"⚠️  No results")
            else:
                print(f"❌ Backtest failed")
            
            time.sleep(1)
    
    # Create DataFrame
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('total_score', ascending=False)
        
        # Save to CSV
        df.to_csv('data/china_comparison_table.csv', index=False)
        
        # Print table
        print(f"\n{'='*100}")
        print("Comparison Table - Sorted by Total Score (Best First)")
        print(f"{'='*100}")
        
        # Main metrics table
        print(f"\n{'Max Hold':<10} {'Threshold':<10} {'Stocks':<8} {'Trades':<8} {'Win Rate':<10} {'RRR':<8} {'Expectancy':<12} {'SL Rate':<10} {'Max DD':<10} {'Risk':<6} {'Profit':<8} {'Total':<8}")
        print("-" * 100)
        for _, row in df.iterrows():
            print(f"{row['max_hold']:<10} {row['threshold']:<10} {row['stocks_passing']:<8} {row['total_trades']:<8} {row['win_rate']:>6.1f}%     {row['rrr']:>6.2f}   {row['expectancy']:>10.2f}%     {row['sl_rate']:>6.1f}%     {row['max_drawdown']:>8.2f}%   {row['risk_score']:<6} {row['profit_score']:<8.1f} {row['total_score']:<8.1f}")
        
        # Detailed table
        print(f"\n{'='*100}")
        print("Detailed Comparison Table")
        print(f"{'='*100}")
        
        print(f"\n{'Max Hold':<10} {'Threshold':<10} {'Avg Win':<10} {'Avg Loss':<10} {'TP Rate':<10} {'Max Hold Rate':<12} {'Avg Hold Days':<12}")
        print("-" * 100)
        for _, row in df.iterrows():
            print(f"{row['max_hold']:<10} {row['threshold']:<10} {row['avg_win']:>8.2f}%   {row['avg_loss']:>8.2f}%   {row['tp_rate']:>6.1f}%     {row['max_hold_rate']:>10.1f}%        {row['avg_hold_days']:>10.1f}")
        
        # Best combination
        best = df.iloc[0]
        print(f"\n{'='*100}")
        print("Best Combination (เสี่ยงน้อย + กำไรจริง)")
        print(f"{'='*100}")
        print(f"  Max Hold: {best['max_hold']} days")
        print(f"  Threshold: {best['threshold']}")
        print(f"  Stocks Passing: {best['stocks_passing']}")
        print(f"  Total Trades: {best['total_trades']}")
        print(f"  Win Rate: {best['win_rate']:.1f}%")
        print(f"  RRR: {best['rrr']:.2f}")
        print(f"  Expectancy: {best['expectancy']:.2f}%")
        print(f"  SL Rate: {best['sl_rate']:.1f}%")
        print(f"  Max Drawdown: {best['max_drawdown']:.2f}%")
        print(f"  Risk Score: {best['risk_score']}/4 (ต่ำ = ดี)")
        print(f"  Profit Score: {best['profit_score']}/4 (สูง = ดี)")
        print(f"  Total Score: {best['total_score']:.1f}")
        
        if best['risk_score'] <= 1 and best['profit_score'] >= 2:
            print(f"\n  ✅ ✅ ✅ EXCELLENT: เสี่ยงน้อย + ได้กำไรจริง")
        elif best['risk_score'] <= 2 and best['profit_score'] >= 1.5:
            print(f"\n  ✅ ✅ GOOD: เสี่ยงปานกลาง + ได้กำไร")
        else:
            print(f"\n  ⚠️  NEEDS IMPROVEMENT")
        
        print(f"\n✅ Results saved to: data/china_comparison_table.csv")
    else:
        print(f"\n⚠️  No results to display")
    
    print(f"\n{'='*100}")
    print("Comparison Complete!")
    print(f"{'='*100}")

if __name__ == '__main__':
    create_comparison_table()

