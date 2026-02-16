#!/usr/bin/env python
"""
Quick China Market Test Table - ทดสอบและสร้างตารางเปรียบเทียบ

ทดสอบบางค่าเพื่อประหยัดเวลา:
- Max Hold: 6, 7, 8, 9
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

# Test Parameters (reduced for speed)
MAX_HOLD_OPTIONS = [6, 7, 8, 9]
THRESHOLD_OPTIONS = [0.85, 0.9, 0.95]

def run_backtest(max_hold, threshold, n_bars=2000):
    """Run backtest with specific parameters"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            df = df[df['Country'] != 'CN']
            df.to_csv(perf_file, index=False)
        except:
            pass
    
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
    
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    time.sleep(2)
    return True

def analyze_results(max_hold, threshold):
    """Analyze results"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        return None
    
    df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df_trades) == 0:
        return None
    
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
    df_trades = df_trades.dropna(subset=['actual_return'])
    
    if len(df_trades) == 0:
        return None
    
    wins = df_trades[df_trades['actual_return'] > 0]
    losses = df_trades[df_trades['actual_return'] <= 0]
    
    total_trades = len(df_trades)
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
    avg_return = df_trades['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    sl_hits = len(df_trades[df_trades['exit_reason'] == 'STOP_LOSS']) if 'exit_reason' in df_trades.columns else 0
    sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
    
    cumulative = df_trades['actual_return'].cumsum()
    max_drawdown = (cumulative - cumulative.expanding().max()).min()
    
    stocks_passing = 0
    if os.path.exists(perf_file):
        try:
            df_perf = pd.read_csv(perf_file)
            stocks_passing = len(df_perf[df_perf['Country'] == 'CN'])
        except:
            pass
    
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
    if avg_return > 0.5:
        profit_score += 2
    elif avg_return > 0:
        profit_score += 1
    if win_rate > 55:
        profit_score += 1
    elif win_rate > 50:
        profit_score += 0.5
    if rrr > 1.5:
        profit_score += 1
    elif rrr > 1.2:
        profit_score += 0.5
    
    return {
        'max_hold': max_hold,
        'threshold': threshold,
        'stocks_passing': stocks_passing,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'rrr': rrr,
        'expectancy': avg_return,
        'sl_rate': sl_rate,
        'max_drawdown': max_drawdown,
        'risk_score': risk_score,
        'profit_score': profit_score,
        'total_score': (4 - risk_score) + profit_score
    }

def main():
    """Main function"""
    print("="*100)
    print("China Market - Quick Test Table")
    print("="*100)
    print(f"\nTesting:")
    print(f"  Max Hold: {MAX_HOLD_OPTIONS}")
    print(f"  Threshold: {THRESHOLD_OPTIONS}")
    print(f"  Total: {len(MAX_HOLD_OPTIONS) * len(THRESHOLD_OPTIONS)} tests")
    print(f"\nThis will take several minutes...")
    
    results = []
    
    for max_hold in MAX_HOLD_OPTIONS:
        for threshold in THRESHOLD_OPTIONS:
            print(f"\n{'='*100}")
            print(f"Test {len(results)+1}/{len(MAX_HOLD_OPTIONS)*len(THRESHOLD_OPTIONS)}: Max Hold={max_hold}, Threshold={threshold}")
            print(f"{'='*100}")
            
            if run_backtest(max_hold, threshold):
                result = analyze_results(max_hold, threshold)
                if result:
                    results.append(result)
                    print(f"✅ {result['stocks_passing']} stocks, Win Rate: {result['win_rate']:.1f}%, RRR: {result['rrr']:.2f}")
                else:
                    print(f"⚠️  No results")
            else:
                print(f"❌ Failed")
            
            time.sleep(1)
    
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('total_score', ascending=False)
        df.to_csv('data/china_quick_test_table.csv', index=False)
        
        print(f"\n{'='*100}")
        print("COMPARISON TABLE - Sorted by Total Score (Best First)")
        print(f"{'='*100}")
        print(f"\n{'Max Hold':<10} {'Threshold':<10} {'Stocks':<8} {'Trades':<8} {'Win Rate':<10} {'RRR':<8} {'Expectancy':<12} {'SL Rate':<10} {'Max DD':<10} {'Risk':<6} {'Profit':<8} {'Total':<8}")
        print("-" * 100)
        for _, row in df.iterrows():
            print(f"{row['max_hold']:<10} {row['threshold']:<10} {row['stocks_passing']:<8} {row['total_trades']:<8} {row['win_rate']:>6.1f}%     {row['rrr']:>6.2f}   {row['expectancy']:>10.2f}%     {row['sl_rate']:>6.1f}%     {row['max_drawdown']:>8.2f}%   {row['risk_score']:<6} {row['profit_score']:<8.1f} {row['total_score']:<8.1f}")
        
        best = df.iloc[0]
        print(f"\n{'='*100}")
        print("BEST COMBINATION")
        print(f"{'='*100}")
        print(f"  Max Hold: {best['max_hold']} days")
        print(f"  Threshold: {best['threshold']}")
        print(f"  Win Rate: {best['win_rate']:.1f}%")
        print(f"  RRR: {best['rrr']:.2f}")
        print(f"  Expectancy: {best['expectancy']:.2f}%")
        print(f"  SL Rate: {best['sl_rate']:.1f}%")
        print(f"  Risk Score: {best['risk_score']}/4")
        print(f"  Profit Score: {best['profit_score']}/4")
        
        print(f"\n✅ Saved to: data/china_quick_test_table.csv")
    else:
        print(f"\n⚠️  No results")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    main()

