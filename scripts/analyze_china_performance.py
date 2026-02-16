#!/usr/bin/env python
"""
Analyze China Market Performance - หาค่าที่เสี่ยงน้อยและได้กำไรจริง

วิเคราะห์:
1. Win Rate และ RRR
2. Exit reasons distribution
3. Average return
4. Risk metrics (SL hit rate, Max Drawdown)
5. หาค่าที่เหมาะสมที่สุด
"""

import sys
import os
import pandas as pd
import numpy as np
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_performance():
    """Analyze China market performance"""
    print("="*80)
    print("China Market - Performance Analysis")
    print("="*80)
    
    # Load trade history
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        return None
    
    # Load data
    df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    df_perf = pd.read_csv(perf_file) if os.path.exists(perf_file) else pd.DataFrame()
    
    print(f"\n📊 Total Trades: {len(df_trades)}")
    
    if len(df_trades) == 0:
        print("❌ No trades found")
        return None
    
    # Convert to numeric
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
    df_trades['trader_return'] = pd.to_numeric(df_trades['trader_return'], errors='coerce')
    df_trades['hold_days'] = pd.to_numeric(df_trades['hold_days'], errors='coerce')
    
    # Remove invalid rows
    df_trades = df_trades.dropna(subset=['actual_return', 'trader_return'])
    
    print(f"✅ Valid Trades: {len(df_trades)}")
    
    # ========================================================================
    # 1. Overall Performance
    # ========================================================================
    print(f"\n{'='*80}")
    print("1. Overall Performance")
    print(f"{'='*80}")
    
    wins = df_trades[df_trades['actual_return'] > 0]
    losses = df_trades[df_trades['actual_return'] <= 0]
    
    total_trades = len(df_trades)
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    
    avg_return = df_trades['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    total_return = df_trades['actual_return'].sum()
    expectancy = avg_return
    
    print(f"  Total Trades: {total_trades}")
    print(f"  Wins: {win_count} ({win_rate:.1f}%)")
    print(f"  Losses: {loss_count} ({100-win_rate:.1f}%)")
    print(f"  Avg Return: {avg_return:.2f}%")
    print(f"  Avg Win: {avg_win:.2f}%")
    print(f"  Avg Loss: {avg_loss:.2f}%")
    print(f"  RRR: {rrr:.2f}")
    print(f"  Total Return: {total_return:.2f}%")
    print(f"  Expectancy: {expectancy:.2f}%")
    
    # ========================================================================
    # 2. Exit Reasons Analysis
    # ========================================================================
    print(f"\n{'='*80}")
    print("2. Exit Reasons Analysis")
    print(f"{'='*80}")
    
    if 'exit_reason' in df_trades.columns:
        exit_counts = df_trades['exit_reason'].value_counts()
        exit_pct = df_trades['exit_reason'].value_counts(normalize=True) * 100
        
        for reason in exit_counts.index:
            count = exit_counts[reason]
            pct = exit_pct[reason]
            reason_df = df_trades[df_trades['exit_reason'] == reason]
            avg_ret = reason_df['actual_return'].mean() if len(reason_df) > 0 else 0
            print(f"  {reason:<20}: {count:>5} ({pct:>5.1f}%) - Avg Return: {avg_ret:>6.2f}%")
    
    # ========================================================================
    # 3. Risk Metrics
    # ========================================================================
    print(f"\n{'='*80}")
    print("3. Risk Metrics")
    print(f"{'='*80}")
    
    # SL hit rate
    sl_hits = len(df_trades[df_trades['exit_reason'] == 'STOP_LOSS']) if 'exit_reason' in df_trades.columns else 0
    sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
    
    # Max drawdown
    cumulative = df_trades['actual_return'].cumsum()
    running_max = cumulative.expanding().max()
    drawdown = cumulative - running_max
    max_drawdown = drawdown.min()
    
    # Win streak / Loss streak
    df_trades['is_win'] = df_trades['actual_return'] > 0
    win_streak = 0
    loss_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    current_win = 0
    current_loss = 0
    
    for is_win in df_trades['is_win']:
        if is_win:
            current_win += 1
            current_loss = 0
            max_win_streak = max(max_win_streak, current_win)
        else:
            current_loss += 1
            current_win = 0
            max_loss_streak = max(max_loss_streak, current_loss)
    
    print(f"  SL Hit Rate: {sl_rate:.1f}%")
    print(f"  Max Drawdown: {max_drawdown:.2f}%")
    print(f"  Max Win Streak: {max_win_streak}")
    print(f"  Max Loss Streak: {max_loss_streak}")
    
    # ========================================================================
    # 4. By Symbol Performance
    # ========================================================================
    print(f"\n{'='*80}")
    print("4. By Symbol Performance")
    print(f"{'='*80}")
    
    if 'symbol' in df_trades.columns:
        symbol_stats = []
        for symbol in df_trades['symbol'].unique():
            sym_df = df_trades[df_trades['symbol'] == symbol]
            sym_wins = sym_df[sym_df['actual_return'] > 0]
            sym_losses = sym_df[sym_df['actual_return'] <= 0]
            
            sym_win_rate = (len(sym_wins) / len(sym_df)) * 100 if len(sym_df) > 0 else 0
            sym_avg_return = sym_df['actual_return'].mean()
            sym_avg_win = sym_wins['actual_return'].mean() if len(sym_wins) > 0 else 0
            sym_avg_loss = sym_losses['actual_return'].abs().mean() if len(sym_losses) > 0 else 0
            sym_rrr = sym_avg_win / sym_avg_loss if sym_avg_loss > 0 else 0
            sym_total_return = sym_df['actual_return'].sum()
            
            symbol_stats.append({
                'symbol': symbol,
                'trades': len(sym_df),
                'win_rate': sym_win_rate,
                'avg_return': sym_avg_return,
                'rrr': sym_rrr,
                'total_return': sym_total_return
            })
        
        symbol_df = pd.DataFrame(symbol_stats)
        symbol_df = symbol_df.sort_values('total_return', ascending=False)
        
        print(f"\n{'Symbol':<12} {'Trades':<8} {'Win Rate':<10} {'Avg Return':<12} {'RRR':<8} {'Total Return':<12}")
        print("-" * 80)
        for _, row in symbol_df.iterrows():
            print(f"{row['symbol']:<12} {row['trades']:<8} {row['win_rate']:>6.1f}%     {row['avg_return']:>8.2f}%     {row['rrr']:>6.2f}     {row['total_return']:>10.2f}%")
    
    # ========================================================================
    # 5. Performance from symbol_performance.csv
    # ========================================================================
    print(f"\n{'='*80}")
    print("5. Stocks Passing Criteria")
    print(f"{'='*80}")
    
    if len(df_perf) > 0:
        china_perf = df_perf[df_perf['Country'] == 'CN'].copy()
        
        if len(china_perf) > 0:
            print(f"\n  Total Stocks Passing: {len(china_perf)}")
            print(f"\n{'Symbol':<12} {'Prob%':<8} {'RRR':<8} {'Count':<8} {'AvgWin%':<10} {'AvgLoss%':<10}")
            print("-" * 80)
            for _, row in china_perf.iterrows():
                print(f"{row['symbol']:<12} {row['Prob%']:>6.1f}%   {row['RR_Ratio']:>6.2f}   {row['Count']:>6.0f}   {row['AvgWin%']:>8.2f}%   {row['AvgLoss%']:>8.2f}%")
            
            avg_prob = china_perf['Prob%'].mean()
            avg_rrr = china_perf['RR_Ratio'].mean()
            avg_count = china_perf['Count'].mean()
            
            print(f"\n  Average Prob%: {avg_prob:.1f}%")
            print(f"  Average RRR: {avg_rrr:.2f}")
            print(f"  Average Count: {avg_count:.0f}")
        else:
            print("  No stocks passing criteria")
    else:
        print("  No symbol_performance.csv found")
    
    # ========================================================================
    # 6. Assessment & Recommendations
    # ========================================================================
    print(f"\n{'='*80}")
    print("6. Assessment & Recommendations")
    print(f"{'='*80}")
    
    # Risk assessment
    risk_score = 0
    if sl_rate > 30:
        risk_score += 2
        print(f"  ⚠️  HIGH RISK: SL hit rate = {sl_rate:.1f}% (สูงเกินไป)")
    elif sl_rate > 20:
        risk_score += 1
        print(f"  ⚠️  MODERATE RISK: SL hit rate = {sl_rate:.1f}% (ปานกลาง)")
    else:
        print(f"  ✅ LOW RISK: SL hit rate = {sl_rate:.1f}% (ต่ำ)")
    
    if max_drawdown < -10:
        risk_score += 2
        print(f"  ⚠️  HIGH RISK: Max drawdown = {max_drawdown:.2f}% (ลึกเกินไป)")
    elif max_drawdown < -5:
        risk_score += 1
        print(f"  ⚠️  MODERATE RISK: Max drawdown = {max_drawdown:.2f}% (ปานกลาง)")
    else:
        print(f"  ✅ LOW RISK: Max drawdown = {max_drawdown:.2f}% (ต่ำ)")
    
    # Profit assessment
    profit_score = 0
    if expectancy > 0.5:
        profit_score += 2
        print(f"  ✅ GOOD PROFIT: Expectancy = {expectancy:.2f}% (ดี)")
    elif expectancy > 0:
        profit_score += 1
        print(f"  ⚠️  MODERATE PROFIT: Expectancy = {expectancy:.2f}% (ปานกลาง)")
    else:
        print(f"  ❌ NO PROFIT: Expectancy = {expectancy:.2f}% (ไม่ดี)")
    
    if win_rate > 55:
        profit_score += 1
        print(f"  ✅ GOOD WIN RATE: {win_rate:.1f}% (ดี)")
    elif win_rate > 50:
        profit_score += 0.5
        print(f"  ⚠️  MODERATE WIN RATE: {win_rate:.1f}% (ปานกลาง)")
    else:
        print(f"  ❌ LOW WIN RATE: {win_rate:.1f}% (ไม่ดี)")
    
    if rrr > 1.5:
        profit_score += 1
        print(f"  ✅ GOOD RRR: {rrr:.2f} (ดี)")
    elif rrr > 1.2:
        profit_score += 0.5
        print(f"  ⚠️  MODERATE RRR: {rrr:.2f} (ปานกลาง)")
    else:
        print(f"  ❌ LOW RRR: {rrr:.2f} (ไม่ดี)")
    
    # Overall assessment
    print(f"\n  Overall Risk Score: {risk_score}/4 (ต่ำ = ดี)")
    print(f"  Overall Profit Score: {profit_score}/4 (สูง = ดี)")
    
    if risk_score <= 1 and profit_score >= 2:
        print(f"\n  ✅ ✅ ✅ EXCELLENT: เสี่ยงน้อย + ได้กำไรจริง")
    elif risk_score <= 2 and profit_score >= 1.5:
        print(f"\n  ✅ ✅ GOOD: เสี่ยงปานกลาง + ได้กำไร")
    elif risk_score <= 2 and profit_score >= 1:
        print(f"\n  ✅ ACCEPTABLE: เสี่ยงปานกลาง + กำไรเล็กน้อย")
    else:
        print(f"\n  ⚠️  NEEDS IMPROVEMENT: เสี่ยงสูงหรือกำไรไม่ดี")
    
    # Recommendations
    print(f"\n  Recommendations:")
    if sl_rate > 30:
        print(f"    - ลด SL หรือเพิ่ม Max Hold เพื่อลด SL hit rate")
    if max_drawdown < -10:
        print(f"    - ปรับ Risk Management เพื่อลด drawdown")
    if expectancy <= 0:
        print(f"    - ปรับ Strategy หรือ RM parameters เพื่อเพิ่มกำไร")
    if win_rate < 50:
        print(f"    - เพิ่ม min_prob หรือปรับ threshold เพื่อเพิ่ม win rate")
    if rrr < 1.2:
        print(f"    - ปรับ TP/SL ratio เพื่อเพิ่ม RRR")
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_return': avg_return,
        'rrr': rrr,
        'expectancy': expectancy,
        'sl_rate': sl_rate,
        'max_drawdown': max_drawdown,
        'risk_score': risk_score,
        'profit_score': profit_score
    }

if __name__ == '__main__':
    result = analyze_performance()
    
    if result:
        print(f"\n{'='*80}")
        print("Analysis Complete!")
        print(f"{'='*80}")

