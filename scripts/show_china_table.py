#!/usr/bin/env python
"""
Show China Market Table - แสดงตารางผลลัพธ์

แสดงตารางจาก:
1. ผลลัพธ์ปัจจุบัน (ถ้ามี)
2. หรือแสดงตัวอย่างตาราง
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_current_results():
    """Show current results table"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        print("❌ No trade history found")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        return None
    
    df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df_trades) == 0:
        print("❌ No trades found")
        return None
    
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
    df_trades = df_trades.dropna(subset=['actual_return'])
    
    if len(df_trades) == 0:
        print("❌ No valid trades")
        return None
    
    # Calculate metrics
    wins = df_trades[df_trades['actual_return'] > 0]
    losses = df_trades[df_trades['actual_return'] <= 0]
    
    total_trades = len(df_trades)
    win_rate = (len(wins) / total_trades) * 100
    avg_return = df_trades['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    sl_hits = len(df_trades[df_trades['exit_reason'] == 'STOP_LOSS']) if 'exit_reason' in df_trades.columns else 0
    sl_rate = (sl_hits / total_trades) * 100
    
    cumulative = df_trades['actual_return'].cumsum()
    max_drawdown = (cumulative - cumulative.expanding().max()).min()
    
    stocks_passing = 0
    if os.path.exists(perf_file):
        try:
            df_perf = pd.read_csv(perf_file)
            stocks_passing = len(df_perf[df_perf['Country'] == 'CN'])
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
    
    total_score = (4 - risk_score) + profit_score
    
    # Create table
    print("="*100)
    print("China Market - Current Results Table")
    print("="*100)
    
    print(f"\n{'Metric':<30} {'Value':<20} {'Status':<20}")
    print("-" * 100)
    print(f"{'Stocks Passing':<30} {stocks_passing:<20} {'✅' if stocks_passing >= 4 else '⚠️'}")
    print(f"{'Total Trades':<30} {total_trades:<20} {'✅' if total_trades >= 50 else '⚠️'}")
    print(f"{'Win Rate':<30} {win_rate:>6.1f}%{'':<13} {'✅' if win_rate >= 55 else '⚠️' if win_rate >= 50 else '❌'}")
    print(f"{'RRR':<30} {rrr:>6.2f}{'':<13} {'✅' if rrr >= 1.5 else '⚠️' if rrr >= 1.2 else '❌'}")
    print(f"{'Expectancy':<30} {avg_return:>6.2f}%{'':<13} {'✅' if avg_return > 0.5 else '⚠️' if avg_return > 0 else '❌'}")
    print(f"{'Avg Win':<30} {avg_win:>6.2f}%{'':<13}")
    print(f"{'Avg Loss':<30} {avg_loss:>6.2f}%{'':<13}")
    print(f"{'SL Rate':<30} {sl_rate:>6.1f}%{'':<13} {'✅' if sl_rate <= 20 else '⚠️' if sl_rate <= 30 else '❌'}")
    print(f"{'Max Drawdown':<30} {max_drawdown:>6.2f}%{'':<13} {'✅' if max_drawdown >= -5 else '⚠️' if max_drawdown >= -10 else '❌'}")
    print(f"{'Risk Score':<30} {risk_score}/4{'':<15} {'✅' if risk_score <= 1 else '⚠️' if risk_score <= 2 else '❌'}")
    print(f"{'Profit Score':<30} {profit_score}/4{'':<15} {'✅' if profit_score >= 2 else '⚠️' if profit_score >= 1.5 else '❌'}")
    print(f"{'Total Score':<30} {total_score:>6.1f}{'':<13} {'✅ ✅ ✅' if risk_score <= 1 and profit_score >= 2 else '✅ ✅' if risk_score <= 2 and profit_score >= 1.5 else '⚠️'}")
    
    # By Symbol
    if 'symbol' in df_trades.columns:
        print(f"\n{'='*100}")
        print("By Symbol Performance")
        print(f"{'='*100}")
        
        symbol_stats = []
        for symbol in df_trades['symbol'].unique():
            sym_df = df_trades[df_trades['symbol'] == symbol]
            sym_wins = sym_df[sym_df['actual_return'] > 0]
            sym_win_rate = (len(sym_wins) / len(sym_df)) * 100 if len(sym_df) > 0 else 0
            sym_avg_return = sym_df['actual_return'].mean()
            sym_total_return = sym_df['actual_return'].sum()
            
            symbol_stats.append({
                'symbol': symbol,
                'trades': len(sym_df),
                'win_rate': sym_win_rate,
                'avg_return': sym_avg_return,
                'total_return': sym_total_return
            })
        
        symbol_df = pd.DataFrame(symbol_stats)
        symbol_df = symbol_df.sort_values('total_return', ascending=False)
        
        print(f"\n{'Symbol':<12} {'Trades':<8} {'Win Rate':<10} {'Avg Return':<12} {'Total Return':<12}")
        print("-" * 100)
        for _, row in symbol_df.iterrows():
            print(f"{row['symbol']:<12} {row['trades']:<8} {row['win_rate']:>6.1f}%     {row['avg_return']:>8.2f}%     {row['total_return']:>10.2f}%")
    
    return {
        'stocks_passing': stocks_passing,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'rrr': rrr,
        'expectancy': avg_return,
        'sl_rate': sl_rate,
        'max_drawdown': max_drawdown,
        'risk_score': risk_score,
        'profit_score': profit_score,
        'total_score': total_score
    }

def show_example_table():
    """Show example comparison table"""
    print("="*100)
    print("Example Comparison Table Format")
    print("="*100)
    print("\nThis is what the comparison table will look like after testing:")
    print("\n" + "="*100)
    print("COMPARISON TABLE - Sorted by Total Score (Best First)")
    print("="*100)
    print(f"\n{'Max Hold':<10} {'Threshold':<10} {'Stocks':<8} {'Trades':<8} {'Win Rate':<10} {'RRR':<8} {'Expectancy':<12} {'SL Rate':<10} {'Max DD':<10} {'Risk':<6} {'Profit':<8} {'Total':<8}")
    print("-" * 100)
    print(f"{'8':<10} {'0.9':<10} {'4':<8} {'156':<8} {'58.3%':<10} {'1.45':<8} {'0.65%':<12} {'18.5%':<10} {'-4.2%':<10} {'1':<6} {'2.5':<8} {'5.5':<8}")
    print(f"{'7':<10} {'0.9':<10} {'4':<8} {'148':<8} {'57.4%':<10} {'1.38':<8} {'0.58%':<12} {'19.2%':<10} {'-4.8%':<10} {'1':<6} {'2.0':<8} {'5.0':<8}")
    print(f"{'9':<10} {'0.9':<10} {'4':<8} {'162':<8} {'56.8%':<10} {'1.32':<8} {'0.52%':<12} {'20.1%':<10} {'-5.1%':<10} {'1':<6} {'1.5':<8} {'4.5':<8}")
    print(f"{'8':<10} {'0.85':<10} {'5':<8} {'178':<8} {'55.6%':<10} {'1.28':<8} {'0.48%':<12} {'21.3%':<10} {'-5.5%':<10} {'2':<6} {'1.5':<8} {'3.5':<8}")
    print(f"{'6':<10} {'0.9':<10} {'3':<8} {'134':<8} {'54.5%':<10} {'1.22':<8} {'0.42%':<12} {'22.4%':<10} {'-6.2%':<10} {'2':<6} {'1.0':<8} {'3.0':<8}")
    
    print(f"\n{'='*100}")
    print("Legend:")
    print("  Risk Score: 0-1 = ✅ LOW, 2 = ⚠️ MODERATE, 3-4 = ❌ HIGH")
    print("  Profit Score: 3-4 = ✅ ✅ ✅ EXCELLENT, 2-2.5 = ✅ ✅ GOOD, 1-1.5 = ⚠️ MODERATE")
    print("  Total Score: Higher is better (Risk Low + Profit High)")

def main():
    """Main function"""
    result = show_current_results()
    
    if result is None:
        print(f"\n{'='*100}")
        show_example_table()
        print(f"\n{'='*100}")
        print("To generate actual comparison table, run:")
        print("  python scripts/quick_china_test_table.py  (Quick - 12 tests)")
        print("  python scripts/create_china_comparison_table.py  (Full - 18 tests)")
    else:
        print(f"\n{'='*100}")
        print("Assessment:")
        if result['risk_score'] <= 1 and result['profit_score'] >= 2:
            print("  ✅ ✅ ✅ EXCELLENT: เสี่ยงน้อย + ได้กำไรจริง")
        elif result['risk_score'] <= 2 and result['profit_score'] >= 1.5:
            print("  ✅ ✅ GOOD: เสี่ยงปานกลาง + ได้กำไร")
        elif result['risk_score'] <= 2 and result['profit_score'] >= 1:
            print("  ✅ ACCEPTABLE: เสี่ยงปานกลาง + กำไรเล็กน้อย")
        else:
            print("  ⚠️  NEEDS IMPROVEMENT: เสี่ยงสูงหรือกำไรไม่ดี")
        
        print(f"\nTo test other parameters and create comparison table:")
        print("  python scripts/quick_china_test_table.py")

if __name__ == '__main__':
    main()

