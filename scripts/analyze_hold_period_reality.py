#!/usr/bin/env python
"""
Analyze Hold Period Reality - วิเคราะห์ความเป็นจริงของการ hold นาน

คำถาม:
1. คนเราจะ hold ถึง 10 วันเลยหรอ?
2. Pattern matching จะไหวกับการ hold นานหรือไม่?
3. ตลาดจะยอมให้ hold นานขนาดนั้นเลย?

วิเคราะห์:
- Hold days distribution
- Return by hold days
- Pattern matching effectiveness over time
- Market volatility impact
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

def analyze_hold_reality():
    """Analyze hold period reality"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        print("❌ File not found: trade_history_CHINA.csv")
        print("   Please run backtest first")
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        print("❌ No trades found")
        return None
    
    # Convert to numeric
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df = df.dropna(subset=['actual_return', 'hold_days'])
    
    print("="*100)
    print("Hold Period Reality Analysis")
    print("="*100)
    print(f"\n📊 Total Trades: {len(df)}")
    
    # ========================================================================
    # 1. Hold Days Distribution
    # ========================================================================
    print(f"\n{'='*100}")
    print("1. Hold Days Distribution")
    print(f"{'='*100}")
    
    hold_dist = df['hold_days'].value_counts().sort_index()
    hold_pct = df['hold_days'].value_counts(normalize=True).sort_index() * 100
    
    print(f"\n  Hold Days Distribution:")
    print(f"  {'Days':<8} {'Count':<10} {'Percentage':<12} {'Avg Return':<12}")
    print(f"  {'-'*50}")
    for days in hold_dist.index:
        count = hold_dist[days]
        pct = hold_pct[days]
        days_df = df[df['hold_days'] == days]
        avg_ret = days_df['actual_return'].mean() if len(days_df) > 0 else 0
        print(f"  {days:<8} {count:<10} {pct:>8.1f}%      {avg_ret:>8.2f}%")
    
    # ========================================================================
    # 2. Return by Hold Days
    # ========================================================================
    print(f"\n{'='*100}")
    print("2. Return by Hold Days")
    print(f"{'='*100}")
    
    print(f"\n  Return Analysis by Hold Days:")
    print(f"  {'Days':<8} {'Avg Return':<12} {'Win Rate':<12} {'Avg Win':<12} {'Avg Loss':<12}")
    print(f"  {'-'*60}")
    
    for days in sorted(df['hold_days'].unique()):
        days_df = df[df['hold_days'] == days]
        if len(days_df) == 0:
            continue
        
        wins = days_df[days_df['actual_return'] > 0]
        losses = days_df[days_df['actual_return'] <= 0]
        
        avg_ret = days_df['actual_return'].mean()
        win_rate = (len(wins) / len(days_df)) * 100 if len(days_df) > 0 else 0
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
        
        print(f"  {days:<8} {avg_ret:>8.2f}%     {win_rate:>8.1f}%     {avg_win:>8.2f}%     {avg_loss:>8.2f}%")
    
    # ========================================================================
    # 3. Pattern Matching Effectiveness Over Time
    # ========================================================================
    print(f"\n{'='*100}")
    print("3. Pattern Matching Effectiveness Over Time")
    print(f"{'='*100}")
    
    # Group by hold days ranges
    df['hold_range'] = pd.cut(df['hold_days'], bins=[0, 3, 5, 7, 10, 20], labels=['1-3', '4-5', '6-7', '8-10', '10+'])
    
    print(f"\n  Pattern Effectiveness by Hold Period:")
    print(f"  {'Range':<10} {'Trades':<10} {'Win Rate':<12} {'Avg Return':<12} {'Pattern Valid':<15}")
    print(f"  {'-'*70}")
    
    for hold_range in ['1-3', '4-5', '6-7', '8-10', '10+']:
        range_df = df[df['hold_range'] == hold_range]
        if len(range_df) == 0:
            continue
        
        wins = range_df[range_df['actual_return'] > 0]
        win_rate = (len(wins) / len(range_df)) * 100 if len(range_df) > 0 else 0
        avg_ret = range_df['actual_return'].mean()
        
        # Pattern validity: ถ้า win rate > 50% = pattern ยัง valid
        pattern_valid = "✅ Valid" if win_rate > 50 else "❌ Invalid"
        
        print(f"  {hold_range:<10} {len(range_df):<10} {win_rate:>8.1f}%     {avg_ret:>8.2f}%     {pattern_valid:<15}")
    
    # ========================================================================
    # 4. Market Volatility Impact
    # ========================================================================
    print(f"\n{'='*100}")
    print("4. Market Volatility Impact (Longer Hold = More Risk)")
    print(f"{'='*100}")
    
    # Calculate volatility by hold days
    print(f"\n  Risk Analysis by Hold Days:")
    print(f"  {'Days':<8} {'Std Dev':<12} {'Max Loss':<12} {'Max Win':<12} {'Risk Score':<12}")
    print(f"  {'-'*60}")
    
    for days in sorted(df['hold_days'].unique()):
        days_df = df[df['hold_days'] == days]
        if len(days_df) == 0:
            continue
        
        std_dev = days_df['actual_return'].std()
        max_loss = days_df['actual_return'].min()
        max_win = days_df['actual_return'].max()
        
        # Risk score: higher std dev = higher risk
        risk_score = "High" if std_dev > 2.0 else "Medium" if std_dev > 1.0 else "Low"
        
        print(f"  {days:<8} {std_dev:>8.2f}%     {max_loss:>8.2f}%     {max_win:>8.2f}%     {risk_score:<12}")
    
    # ========================================================================
    # 5. Exit Reasons by Hold Days
    # ========================================================================
    print(f"\n{'='*100}")
    print("5. Exit Reasons by Hold Days")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        print(f"\n  Exit Reasons Distribution:")
        print(f"  {'Days':<8} {'TP':<10} {'SL':<10} {'MAX_HOLD':<12} {'TRAILING':<12}")
        print(f"  {'-'*60}")
        
        for days in sorted(df['hold_days'].unique()):
            days_df = df[df['hold_days'] == days]
            if len(days_df) == 0:
                continue
            
            tp_count = len(days_df[days_df['exit_reason'] == 'TAKE_PROFIT'])
            sl_count = len(days_df[days_df['exit_reason'] == 'STOP_LOSS'])
            max_hold_count = len(days_df[days_df['exit_reason'] == 'MAX_HOLD'])
            trailing_count = len(days_df[days_df['exit_reason'] == 'TRAILING_STOP'])
            
            total = len(days_df)
            
            print(f"  {days:<8} {tp_count:>5} ({tp_count/total*100:>4.1f}%) {sl_count:>5} ({sl_count/total*100:>4.1f}%) {max_hold_count:>5} ({max_hold_count/total*100:>4.1f}%) {trailing_count:>5} ({trailing_count/total*100:>4.1f}%)")
    
    # ========================================================================
    # 6. Assessment: Hold 10 วันเหมาะสมหรือไม่?
    # ========================================================================
    print(f"\n{'='*100}")
    print("6. Assessment: Hold 10 วันเหมาะสมหรือไม่?")
    print(f"{'='*100}")
    
    # Analyze trades that hold > 7 days
    long_holds = df[df['hold_days'] > 7]
    short_holds = df[df['hold_days'] <= 7]
    
    if len(long_holds) > 0:
        long_hold_win_rate = (len(long_holds[long_holds['actual_return'] > 0]) / len(long_holds)) * 100
        long_hold_avg_ret = long_holds['actual_return'].mean()
        long_hold_std = long_holds['actual_return'].std()
        
        print(f"\n  Long Holds (>7 days):")
        print(f"    Count: {len(long_holds)} ({len(long_holds)/len(df)*100:.1f}%)")
        print(f"    Win Rate: {long_hold_win_rate:.1f}%")
        print(f"    Avg Return: {long_hold_avg_ret:.2f}%")
        print(f"    Std Dev: {long_hold_std:.2f}%")
        
        if long_hold_win_rate < 50:
            print(f"    ❌ Win Rate ต่ำ - Pattern ไม่ valid สำหรับ hold นาน")
        elif long_hold_std > 2.0:
            print(f"    ⚠️  Volatility สูง - Risk สูง")
        else:
            print(f"    ✅ Pattern ยัง valid สำหรับ hold นาน")
    
    if len(short_holds) > 0:
        short_hold_win_rate = (len(short_holds[short_holds['actual_return'] > 0]) / len(short_holds)) * 100
        short_hold_avg_ret = short_holds['actual_return'].mean()
        
        print(f"\n  Short Holds (<=7 days):")
        print(f"    Count: {len(short_holds)} ({len(short_holds)/len(df)*100:.1f}%)")
        print(f"    Win Rate: {short_hold_win_rate:.1f}%")
        print(f"    Avg Return: {short_hold_avg_ret:.2f}%")
        
        if short_hold_win_rate > long_hold_win_rate:
            print(f"    ✅ Win Rate สูงกว่า long holds - Pattern ดีกว่าในระยะสั้น")
    
    # ========================================================================
    # 7. Recommendations
    # ========================================================================
    print(f"\n{'='*100}")
    print("7. Recommendations")
    print(f"{'='*100}")
    
    # Find optimal hold period
    optimal_hold = None
    best_score = -1
    
    for days in sorted(df['hold_days'].unique()):
        days_df = df[df['hold_days'] == days]
        if len(days_df) == 0:
            continue
        
        wins = days_df[days_df['actual_return'] > 0]
        win_rate = (len(wins) / len(days_df)) * 100
        avg_ret = days_df['actual_return'].mean()
        std_dev = days_df['actual_return'].std()
        
        # Score: win rate + avg return - risk (std dev)
        score = win_rate + (avg_ret * 10) - (std_dev * 5)
        
        if score > best_score:
            best_score = score
            optimal_hold = days
    
    if optimal_hold:
        print(f"\n  Optimal Hold Period: {optimal_hold} days")
        print(f"  Score: {best_score:.1f}")
        
        if optimal_hold <= 5:
            print(f"  💡 แนะนำ: Max Hold 5-6 days (สั้น - Pattern valid)")
        elif optimal_hold <= 7:
            print(f"  💡 แนะนำ: Max Hold 6-7 days (ปานกลาง)")
        else:
            print(f"  ⚠️  Optimal Hold นาน ({optimal_hold} days) - ต้องระวัง")
            print(f"  💡 พิจารณา: ลด TP แทนการเพิ่ม Max Hold")
    
    # Final recommendations
    print(f"\n  Final Recommendations:")
    
    if len(long_holds) > 0 and long_hold_win_rate < 50:
        print(f"    1. ❌ ไม่ควร hold นาน (>7 days) - Pattern ไม่ valid")
        print(f"    2. 💡 แนะนำ: Max Hold 5-6 days")
        print(f"    3. 💡 แนะนำ: ลด TP (5.5% → 3.5-4.0%)")
    elif len(long_holds) > 0 and long_hold_std > 2.0:
        print(f"    1. ⚠️  Hold นานมีความเสี่ยงสูง (volatility สูง)")
        print(f"    2. 💡 แนะนำ: Max Hold 6-7 days")
        print(f"    3. 💡 แนะนำ: ใช้ Trailing Stop แทน")
    else:
        print(f"    1. ✅ Pattern ยัง valid สำหรับ hold นาน")
        print(f"    2. 💡 แต่ควรพิจารณา: Max Hold 6-7 days (สมดุล)")
        print(f"    3. 💡 ใช้ Trailing Stop เพื่อ lock profits")
    
    return df

if __name__ == '__main__':
    df = analyze_hold_reality()
    
    if df is not None:
        print(f"\n{'='*100}")
        print("Analysis Complete!")
        print(f"{'='*100}")

