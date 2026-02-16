#!/usr/bin/env python
"""
Compare China Market - Different Max Hold Values

ทดสอบและเปรียบเทียบ Max Hold หลายค่า:
- Max Hold: 5, 6, 7, 8, 9, 10 days

วิเคราะห์:
1. Exit reasons distribution
2. Win/Loss ratio
3. Average return
4. SL hit rate
5. TP hit rate
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

MAX_HOLD_OPTIONS = [5, 6, 7, 8, 9, 10]

def run_backtest(max_hold, n_bars=2000):
    """Run backtest with specific max_hold"""
    print(f"\n{'='*80}")
    print(f"Testing Max Hold = {max_hold} days")
    print(f"{'='*80}")
    
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
        '--fast',
        '--max_hold', str(max_hold)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error running backtest:")
        print(result.stderr)
        return None
    
    # Wait a bit for file to be written
    time.sleep(2)
    
    return True

def analyze_results(max_hold):
    """Analyze results for specific max_hold"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        return None
    
    # Convert to numeric
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce')
    
    # Remove invalid rows
    df = df.dropna(subset=['exit_reason', 'hold_days', 'actual_return'])
    
    if len(df) == 0:
        return None
    
    # Calculate metrics
    total_trades = len(df)
    wins = df[df['actual_return'] > 0]
    losses = df[df['actual_return'] <= 0]
    
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
    avg_return = df['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Exit reasons
    exit_counts = df['exit_reason'].value_counts()
    sl_hits = len(df[df['exit_reason'] == 'STOP_LOSS'])
    tp_hits = len(df[df['exit_reason'] == 'TAKE_PROFIT'])
    max_hold_exits = len(df[df['exit_reason'] == 'MAX_HOLD'])
    trailing_exits = len(df[df['exit_reason'] == 'TRAILING_STOP'])
    
    sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
    tp_rate = (tp_hits / total_trades) * 100 if total_trades > 0 else 0
    max_hold_rate = (max_hold_exits / total_trades) * 100 if total_trades > 0 else 0
    trailing_rate = (trailing_exits / total_trades) * 100 if total_trades > 0 else 0
    
    # Avg hold days
    avg_hold_days = df['hold_days'].mean()
    
    # MAX_HOLD exit analysis
    max_hold_df = df[df['exit_reason'] == 'MAX_HOLD']
    max_hold_avg_return = max_hold_df['actual_return'].mean() if len(max_hold_df) > 0 else 0
    max_hold_win_rate = (len(max_hold_df[max_hold_df['actual_return'] > 0]) / len(max_hold_df) * 100) if len(max_hold_df) > 0 else 0
    
    result = {
        'max_hold': max_hold,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_return': avg_return,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rrr': rrr,
        'sl_hits': sl_hits,
        'sl_rate': sl_rate,
        'tp_hits': tp_hits,
        'tp_rate': tp_rate,
        'max_hold_exits': max_hold_exits,
        'max_hold_rate': max_hold_rate,
        'trailing_exits': trailing_exits,
        'trailing_rate': trailing_rate,
        'avg_hold_days': avg_hold_days,
        'max_hold_avg_return': max_hold_avg_return,
        'max_hold_win_rate': max_hold_win_rate,
    }
    
    return result

def main():
    """Main comparison function"""
    print("="*80)
    print("China Market - Max Hold Comparison")
    print("="*80)
    print(f"\nTesting Max Hold values: {MAX_HOLD_OPTIONS}")
    print(f"Total tests: {len(MAX_HOLD_OPTIONS)}")
    
    results = []
    
    for max_hold in MAX_HOLD_OPTIONS:
        # Run backtest
        success = run_backtest(max_hold)
        
        if not success:
            print(f"❌ Failed to run backtest for Max Hold = {max_hold}")
            continue
        
        # Analyze results
        result = analyze_results(max_hold)
        
        if result:
            results.append(result)
            print(f"\n✅ Results for Max Hold = {max_hold}:")
            print(f"   Total Trades: {result['total_trades']}")
            print(f"   Win Rate: {result['win_rate']:.1f}%")
            print(f"   Avg Return: {result['avg_return']:.2f}%")
            print(f"   RRR: {result['rrr']:.2f}")
            print(f"   SL Rate: {result['sl_rate']:.1f}%")
            print(f"   TP Rate: {result['tp_rate']:.1f}%")
            print(f"   MAX_HOLD Exits: {result['max_hold_rate']:.1f}% (Avg Return: {result['max_hold_avg_return']:.2f}%)")
        else:
            print(f"⚠️  No results for Max Hold = {max_hold}")
        
        # Small delay
        time.sleep(1)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv('data/china_max_hold_comparison.csv', index=False)
        print(f"\n✅ Results saved to data/china_max_hold_comparison.csv")
        
        # Print comparison table
        print(f"\n{'='*80}")
        print("Comparison Table")
        print(f"{'='*80}")
        print(results_df[['max_hold', 'total_trades', 'win_rate', 'avg_return', 'rrr', 
                          'sl_rate', 'tp_rate', 'max_hold_rate', 'max_hold_avg_return']].to_string(index=False))
        
        # Recommendations
        print(f"\n{'='*80}")
        print("Recommendations")
        print(f"{'='*80}")
        
        best_rrr = results_df.loc[results_df['rrr'].idxmax()]
        best_win_rate = results_df.loc[results_df['win_rate'].idxmax()]
        lowest_sl = results_df.loc[results_df['sl_rate'].idxmin()]
        
        print(f"\n  Best RRR: Max Hold = {best_rrr['max_hold']} days (RRR = {best_rrr['rrr']:.2f})")
        print(f"  Best Win Rate: Max Hold = {best_win_rate['max_hold']} days (Win Rate = {best_win_rate['win_rate']:.1f}%)")
        print(f"  Lowest SL Rate: Max Hold = {lowest_sl['max_hold']} days (SL Rate = {lowest_sl['sl_rate']:.1f}%)")
        
        # Check for MAX_HOLD exits with negative return
        negative_max_hold = results_df[results_df['max_hold_avg_return'] < 0]
        if len(negative_max_hold) > 0:
            print(f"\n  ⚠️  WARNING: These Max Hold values have negative return on MAX_HOLD exits:")
            for _, row in negative_max_hold.iterrows():
                print(f"     Max Hold = {row['max_hold']} days: {row['max_hold_avg_return']:.2f}%")
            print(f"     Consider using shorter Max Hold values")
    else:
        print(f"\n⚠️  No results to compare")
    
    print(f"\n{'='*80}")
    print("Comparison Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()

