#!/usr/bin/env python
"""
Test China Market - Realistic TP Settings

ทดสอบหลายค่า TP และ Max Hold เพื่อหาค่าที่เหมาะสมกับความเป็นจริงของหุ้นรายวัน

เป้าหมาย:
- TP Hit Rate >= 20-30%
- MAX_HOLD Rate < 50%
- RRR >= 1.3-1.5
- MAX_HOLD Exits Return > 0%
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

# Test Parameters - Realistic for Daily Bars
TP_OPTIONS = [4.0, 4.5, 5.0, 5.5]  # ลด TP เพื่อให้ถึงง่ายขึ้น
MAX_HOLD_OPTIONS = [8, 10, 12]      # เพิ่ม Max Hold เพื่อให้มีเวลาไปถึง TP
SL_FIXED = 1.2                      # Fixed SL (ไม่เปลี่ยน)

def run_backtest(tp, max_hold, n_bars=2000):
    """Run backtest with specific TP and Max Hold"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    # Clean old results
    if os.path.exists(log_file):
        os.remove(log_file)
    
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
        '--take_profit', str(tp),
        '--max_hold', str(max_hold),
        '--stop_loss', str(SL_FIXED)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return False
    
    # Calculate metrics
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    time.sleep(2)
    return True

def analyze_results(tp, max_hold):
    """Analyze results for specific TP and Max Hold"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        return None
    
    # Convert to numeric
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df = df.dropna(subset=['actual_return'])
    
    if len(df) == 0:
        return None
    
    # Calculate metrics
    wins = df[df['actual_return'] > 0]
    losses = df[df['actual_return'] <= 0]
    
    total_trades = len(df)
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
    avg_return = df['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Exit reasons
    if 'exit_reason' in df.columns:
        tp_hits = len(df[df['exit_reason'] == 'TAKE_PROFIT'])
        sl_hits = len(df[df['exit_reason'] == 'STOP_LOSS'])
        max_hold_exits = len(df[df['exit_reason'] == 'MAX_HOLD'])
        
        tp_rate = (tp_hits / total_trades) * 100 if total_trades > 0 else 0
        sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
        max_hold_rate = (max_hold_exits / total_trades) * 100 if total_trades > 0 else 0
        
        # MAX_HOLD exits return
        max_hold_df = df[df['exit_reason'] == 'MAX_HOLD']
        max_hold_return = max_hold_df['actual_return'].mean() if len(max_hold_df) > 0 else 0
    else:
        tp_rate = 0
        sl_rate = 0
        max_hold_rate = 0
        max_hold_return = 0
    
    # Stocks passing
    stocks_passing = 0
    if os.path.exists(perf_file):
        try:
            df_perf = pd.read_csv(perf_file)
            stocks_passing = len(df_perf[df_perf['Country'] == 'CN'])
        except:
            pass
    
    # Score calculation
    score = 0
    if tp_rate >= 20:
        score += 2
    elif tp_rate >= 10:
        score += 1
    
    if max_hold_rate < 50:
        score += 2
    elif max_hold_rate < 60:
        score += 1
    
    if max_hold_return > 0:
        score += 1
    
    if rrr >= 1.3:
        score += 2
    elif rrr >= 1.2:
        score += 1
    
    return {
        'tp': tp,
        'max_hold': max_hold,
        'stocks_passing': stocks_passing,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'rrr': rrr,
        'expectancy': avg_return,
        'tp_rate': tp_rate,
        'sl_rate': sl_rate,
        'max_hold_rate': max_hold_rate,
        'max_hold_return': max_hold_return,
        'score': score
    }

def main():
    """Main function"""
    print("="*100)
    print("China Market - Realistic TP Testing")
    print("="*100)
    print(f"\nTesting Parameters:")
    print(f"  TP Options: {TP_OPTIONS}%")
    print(f"  Max Hold Options: {MAX_HOLD_OPTIONS} days")
    print(f"  SL Fixed: {SL_FIXED}%")
    print(f"  Total Tests: {len(TP_OPTIONS) * len(MAX_HOLD_OPTIONS)}")
    
    print(f"\nTarget Criteria:")
    print(f"  TP Hit Rate: >= 20-30%")
    print(f"  MAX_HOLD Rate: < 50%")
    print(f"  RRR: >= 1.3-1.5")
    print(f"  MAX_HOLD Exits Return: > 0%")
    
    results = []
    
    # Test all combinations
    for tp in TP_OPTIONS:
        for max_hold in MAX_HOLD_OPTIONS:
            print(f"\n{'='*100}")
            print(f"Test {len(results)+1}/{len(TP_OPTIONS)*len(MAX_HOLD_OPTIONS)}: TP={tp}%, Max Hold={max_hold} days")
            print(f"{'='*100}")
            
            if run_backtest(tp, max_hold):
                result = analyze_results(tp, max_hold)
                if result:
                    results.append(result)
                    print(f"✅ Results:")
                    print(f"   Stocks: {result['stocks_passing']}, Trades: {result['total_trades']}")
                    print(f"   Win Rate: {result['win_rate']:.1f}%, RRR: {result['rrr']:.2f}")
                    print(f"   TP Rate: {result['tp_rate']:.1f}%, MAX_HOLD Rate: {result['max_hold_rate']:.1f}%")
                    print(f"   MAX_HOLD Return: {result['max_hold_return']:.2f}%, Score: {result['score']}")
                else:
                    print(f"⚠️  No results")
            else:
                print(f"❌ Backtest failed")
            
            time.sleep(1)
    
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('score', ascending=False)
        results_df.to_csv('data/china_realistic_tp_results.csv', index=False)
        
        print(f"\n{'='*100}")
        print("COMPARISON TABLE - Sorted by Score (Best First)")
        print(f"{'='*100}")
        print(f"\n{'TP':<8} {'Max Hold':<10} {'Stocks':<8} {'Trades':<8} {'Win Rate':<10} {'RRR':<8} {'TP Rate':<10} {'MAX_HOLD Rate':<12} {'MAX_HOLD Ret':<12} {'Score':<8}")
        print("-" * 100)
        for _, row in results_df.iterrows():
            print(f"{row['tp']:<8} {row['max_hold']:<10} {row['stocks_passing']:<8} {row['total_trades']:<8} {row['win_rate']:>6.1f}%     {row['rrr']:>6.2f}   {row['tp_rate']:>6.1f}%     {row['max_hold_rate']:>10.1f}%        {row['max_hold_return']:>10.2f}%     {row['score']:<8}")
        
        # Best combination
        best = results_df.iloc[0]
        print(f"\n{'='*100}")
        print("BEST COMBINATION (Realistic for Daily Bars)")
        print(f"{'='*100}")
        print(f"  TP: {best['tp']}%")
        print(f"  Max Hold: {best['max_hold']} days")
        print(f"  SL: {SL_FIXED}%")
        print(f"  Stocks Passing: {best['stocks_passing']}")
        print(f"  Total Trades: {best['total_trades']}")
        print(f"  Win Rate: {best['win_rate']:.1f}%")
        print(f"  RRR: {best['rrr']:.2f}")
        print(f"  TP Hit Rate: {best['tp_rate']:.1f}% {'✅' if best['tp_rate'] >= 20 else '⚠️'}")
        print(f"  MAX_HOLD Rate: {best['max_hold_rate']:.1f}% {'✅' if best['max_hold_rate'] < 50 else '⚠️'}")
        print(f"  MAX_HOLD Return: {best['max_hold_return']:.2f}% {'✅' if best['max_hold_return'] > 0 else '❌'}")
        print(f"  Score: {best['score']}/8")
        
        # Recommendations
        print(f"\n{'='*100}")
        print("RECOMMENDATIONS")
        print(f"{'='*100}")
        
        if best['tp_rate'] < 20:
            print(f"  ⚠️  TP Hit Rate ต่ำ ({best['tp_rate']:.1f}%)")
            print(f"  💡 แนะนำ: ลด TP เพิ่มเติม (ปัจจุบัน: {best['tp']}%)")
        
        if best['max_hold_rate'] > 50:
            print(f"  ⚠️  MAX_HOLD Rate สูง ({best['max_hold_rate']:.1f}%)")
            print(f"  💡 แนะนำ: เพิ่ม Max Hold เพิ่มเติม (ปัจจุบัน: {best['max_hold']} days)")
        
        if best['max_hold_return'] < 0:
            print(f"  ❌ MAX_HOLD Exits Return ติดลบ ({best['max_hold_return']:.2f}%)")
            print(f"  💡 แนะนำ: ลด TP หรือปรับ Max Hold")
        
        if best['rrr'] < 1.3:
            print(f"  ⚠️  RRR ต่ำ ({best['rrr']:.2f})")
            print(f"  💡 แนะนำ: ปรับ TP/SL ratio หรือ Max Hold")
        
        print(f"\n✅ Results saved to: data/china_realistic_tp_results.csv")
    else:
        print(f"\n⚠️  No results to display")
    
    print(f"\n{'='*100}")
    print("Testing Complete!")
    print(f"{'='*100}")

if __name__ == '__main__':
    main()

