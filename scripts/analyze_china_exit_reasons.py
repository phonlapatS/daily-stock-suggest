#!/usr/bin/env python
"""
Analyze China Market - Exit Reasons & Hold Days

วิเคราะห์:
1. Exit reasons distribution (STOP_LOSS, TAKE_PROFIT, MAX_HOLD, TRAILING_STOP)
2. Hold days distribution
3. Win/Loss ratio by exit reason
4. Average return by exit reason
5. หุ้นที่ผันผวนนิดๆไปเรื่อยๆ (exit ด้วย MAX_HOLD หรือ TRAILING_STOP)
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

def analyze_exit_reasons():
    """Analyze exit reasons and hold days"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        return None
    
    print("="*80)
    print("China Market - Exit Reasons & Hold Days Analysis")
    print("="*80)
    
    # Load data
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    print(f"\n📊 Total Trades: {len(df)}")
    
    if len(df) == 0:
        print("❌ No trades found")
        return None
    
    # Check required columns
    required_cols = ['exit_reason', 'hold_days', 'actual_return', 'trader_return']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        print(f"   Available columns: {df.columns.tolist()}")
        return None
    
    # Convert to numeric
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce')
    
    # Remove invalid rows
    df = df.dropna(subset=['exit_reason', 'hold_days', 'actual_return'])
    
    print(f"✅ Valid Trades: {len(df)}")
    
    # ========================================================================
    # 1. Exit Reasons Distribution
    # ========================================================================
    print(f"\n{'='*80}")
    print("1. Exit Reasons Distribution")
    print(f"{'='*80}")
    
    exit_counts = df['exit_reason'].value_counts()
    exit_pct = df['exit_reason'].value_counts(normalize=True) * 100
    
    for reason in exit_counts.index:
        count = exit_counts[reason]
        pct = exit_pct[reason]
        print(f"  {reason:<20}: {count:>5} trades ({pct:>5.1f}%)")
    
    # ========================================================================
    # 2. Hold Days Distribution
    # ========================================================================
    print(f"\n{'='*80}")
    print("2. Hold Days Distribution")
    print(f"{'='*80}")
    
    print(f"  Min Hold Days: {df['hold_days'].min():.0f}")
    print(f"  Max Hold Days: {df['hold_days'].max():.0f}")
    print(f"  Avg Hold Days: {df['hold_days'].mean():.2f}")
    print(f"  Median Hold Days: {df['hold_days'].median():.2f}")
    
    # Hold days by exit reason
    print(f"\n  Hold Days by Exit Reason:")
    for reason in df['exit_reason'].unique():
        reason_df = df[df['exit_reason'] == reason]
        if len(reason_df) > 0:
            avg_hold = reason_df['hold_days'].mean()
            print(f"    {reason:<20}: {avg_hold:>5.2f} days (avg)")
    
    # Hold days distribution
    print(f"\n  Hold Days Distribution:")
    hold_bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]
    hold_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10+']
    df['hold_days_bin'] = pd.cut(df['hold_days'], bins=hold_bins, labels=hold_labels, right=False)
    hold_dist = df['hold_days_bin'].value_counts().sort_index()
    for days, count in hold_dist.items():
        pct = (count / len(df)) * 100
        print(f"    {days} days: {count:>5} trades ({pct:>5.1f}%)")
    
    # ========================================================================
    # 3. Win/Loss by Exit Reason
    # ========================================================================
    print(f"\n{'='*80}")
    print("3. Win/Loss by Exit Reason")
    print(f"{'='*80}")
    
    for reason in df['exit_reason'].unique():
        reason_df = df[df['exit_reason'] == reason]
        if len(reason_df) == 0:
            continue
        
        wins = reason_df[reason_df['actual_return'] > 0]
        losses = reason_df[reason_df['actual_return'] <= 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        total = len(reason_df)
        win_rate = (win_count / total) * 100 if total > 0 else 0
        
        avg_return = reason_df['actual_return'].mean()
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = losses['actual_return'].mean() if len(losses) > 0 else 0
        
        print(f"\n  {reason}:")
        print(f"    Total: {total} trades")
        print(f"    Wins: {win_count} ({win_rate:.1f}%)")
        print(f"    Losses: {loss_count} ({100-win_rate:.1f}%)")
        print(f"    Avg Return: {avg_return:.2f}%")
        if len(wins) > 0:
            print(f"    Avg Win: {avg_win:.2f}%")
        if len(losses) > 0:
            print(f"    Avg Loss: {avg_loss:.2f}%")
    
    # ========================================================================
    # 4. Average Return by Hold Days
    # ========================================================================
    print(f"\n{'='*80}")
    print("4. Average Return by Hold Days")
    print(f"{'='*80}")
    
    for days in sorted(df['hold_days'].unique()):
        days_df = df[df['hold_days'] == days]
        if len(days_df) == 0:
            continue
        
        avg_return = days_df['actual_return'].mean()
        win_rate = (len(days_df[days_df['actual_return'] > 0]) / len(days_df)) * 100
        count = len(days_df)
        
        print(f"  {days:>2} days: {count:>4} trades, Avg Return: {avg_return:>6.2f}%, Win Rate: {win_rate:>5.1f}%")
    
    # ========================================================================
    # 5. หุ้นที่ผันผวนนิดๆไปเรื่อยๆ (MAX_HOLD หรือ TRAILING_STOP)
    # ========================================================================
    print(f"\n{'='*80}")
    print("5. หุ้นที่ผันผวนนิดๆไปเรื่อยๆ (Exit ด้วย MAX_HOLD หรือ TRAILING_STOP)")
    print(f"{'='*80}")
    
    volatile_exits = df[df['exit_reason'].isin(['MAX_HOLD', 'TRAILING_STOP'])]
    
    if len(volatile_exits) > 0:
        print(f"\n  Total: {len(volatile_exits)} trades")
        
        wins = volatile_exits[volatile_exits['actual_return'] > 0]
        losses = volatile_exits[volatile_exits['actual_return'] <= 0]
        
        print(f"  Wins: {len(wins)} ({len(wins)/len(volatile_exits)*100:.1f}%)")
        print(f"  Losses: {len(losses)} ({len(losses)/len(volatile_exits)*100:.1f}%)")
        print(f"  Avg Return: {volatile_exits['actual_return'].mean():.2f}%")
        
        if len(wins) > 0:
            print(f"  Avg Win: {wins['actual_return'].mean():.2f}%")
        if len(losses) > 0:
            print(f"  Avg Loss: {losses['actual_return'].mean():.2f}%")
        
        # By symbol
        if 'symbol' in volatile_exits.columns:
            print(f"\n  By Symbol:")
            symbol_stats = volatile_exits.groupby('symbol').agg({
                'actual_return': ['count', 'mean'],
                'hold_days': 'mean'
            }).round(2)
            symbol_stats.columns = ['Count', 'Avg Return', 'Avg Hold Days']
            print(symbol_stats.to_string())
    else:
        print("  No trades found with MAX_HOLD or TRAILING_STOP exit")
    
    # ========================================================================
    # 6. Risk Analysis: SL Hit Rate
    # ========================================================================
    print(f"\n{'='*80}")
    print("6. Risk Analysis: Stop Loss Hit Rate")
    print(f"{'='*80}")
    
    sl_hits = df[df['exit_reason'] == 'STOP_LOSS']
    sl_rate = (len(sl_hits) / len(df)) * 100 if len(df) > 0 else 0
    
    print(f"  Stop Loss Hits: {len(sl_hits)} ({sl_rate:.1f}%)")
    
    if len(sl_hits) > 0:
        avg_hold_sl = sl_hits['hold_days'].mean()
        print(f"  Avg Hold Days (SL): {avg_hold_sl:.2f} days")
        
        # SL hits by hold days
        print(f"\n  SL Hits by Hold Days:")
        sl_by_days = sl_hits.groupby('hold_days').size()
        for days, count in sl_by_days.items():
            pct = (count / len(sl_hits)) * 100
            print(f"    {days} days: {count} hits ({pct:.1f}%)")
    
    # ========================================================================
    # 7. TP Hit Rate
    # ========================================================================
    print(f"\n{'='*80}")
    print("7. Take Profit Hit Rate")
    print(f"{'='*80}")
    
    tp_hits = df[df['exit_reason'] == 'TAKE_PROFIT']
    tp_rate = (len(tp_hits) / len(df)) * 100 if len(df) > 0 else 0
    
    print(f"  Take Profit Hits: {len(tp_hits)} ({tp_rate:.1f}%)")
    
    if len(tp_hits) > 0:
        avg_hold_tp = tp_hits['hold_days'].mean()
        print(f"  Avg Hold Days (TP): {avg_hold_tp:.2f} days")
        
        # TP hits by hold days
        print(f"\n  TP Hits by Hold Days:")
        tp_by_days = tp_hits.groupby('hold_days').size()
        for days, count in tp_by_days.items():
            pct = (count / len(tp_hits)) * 100
            print(f"    {days} days: {count} hits ({pct:.1f}%)")
    
    # ========================================================================
    # 8. Summary & Recommendations
    # ========================================================================
    print(f"\n{'='*80}")
    print("8. Summary & Recommendations")
    print(f"{'='*80}")
    
    max_hold_exits = df[df['exit_reason'] == 'MAX_HOLD']
    max_hold_rate = (len(max_hold_exits) / len(df)) * 100 if len(df) > 0 else 0
    
    print(f"\n  Current Max Hold: 8 days")
    print(f"  Max Hold Exits: {len(max_hold_exits)} ({max_hold_rate:.1f}%)")
    
    if len(max_hold_exits) > 0:
        avg_return_max_hold = max_hold_exits['actual_return'].mean()
        win_rate_max_hold = (len(max_hold_exits[max_hold_exits['actual_return'] > 0]) / len(max_hold_exits)) * 100
        
        print(f"  Avg Return (MAX_HOLD): {avg_return_max_hold:.2f}%")
        print(f"  Win Rate (MAX_HOLD): {win_rate_max_hold:.1f}%")
        
        if avg_return_max_hold < 0:
            print(f"\n  ⚠️  WARNING: MAX_HOLD exits have negative average return!")
            print(f"     This suggests Max Hold = 8 days may be too long")
        elif win_rate_max_hold < 50:
            print(f"\n  ⚠️  WARNING: MAX_HOLD exits have low win rate!")
            print(f"     This suggests many trades exit at loss after holding 8 days")
    
    print(f"\n  Recommendations:")
    print(f"    1. If SL hit rate > 30%: Consider tighter SL or shorter Max Hold")
    print(f"    2. If MAX_HOLD exits have negative return: Consider shorter Max Hold")
    print(f"    3. If TP hit rate < 20%: Consider lower TP or longer Max Hold")
    print(f"    4. If many trades exit at MAX_HOLD with small profit: Consider trailing stop")
    
    return df

if __name__ == '__main__':
    df = analyze_exit_reasons()
    
    if df is not None:
        print(f"\n{'='*80}")
        print("Analysis Complete!")
        print(f"{'='*80}")

