#!/usr/bin/env python
"""
Test Max Hold Necessity - ทดสอบว่า Max Hold 5 days จำเป็นจริงๆหรือไม่

วิเคราะห์:
- Trades ส่วนใหญ่ออกในกี่วัน?
- มี trades ที่ hold >3, >4, >5 days หรือไม่?
- ถ้าลด Max Hold เป็น 3-4 days จะมีผลอย่างไร?
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

def analyze_max_hold_necessity():
    """Analyze if Max Hold 5 days is necessary"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        print("❌ File not found: trade_history_CHINA.csv")
        print("   Please run backtest first")
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        print("❌ No trades found")
        return None
    
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df = df.dropna(subset=['hold_days'])
    
    print("="*100)
    print("Max Hold Necessity Analysis")
    print("="*100)
    
    print(f"\n📊 Hold Days Statistics:")
    print(f"  Total Trades: {len(df)}")
    print(f"  Avg Hold: {df['hold_days'].mean():.2f} days")
    print(f"  Median Hold: {df['hold_days'].median():.0f} days")
    print(f"  Max Hold: {df['hold_days'].max():.0f} days")
    print(f"  95th Percentile: {df['hold_days'].quantile(0.95):.0f} days")
    print(f"  99th Percentile: {df['hold_days'].quantile(0.99):.0f} days")
    
    print(f"\n📈 Hold Days Distribution:")
    dist = df['hold_days'].value_counts().sort_index()
    for days in dist.index[:10]:  # Top 10
        count = dist[days]
        pct = (count / len(df)) * 100
        print(f"  {days:.0f} days: {count} ({pct:.1f}%)")
    
    print(f"\n🔍 Trades by Hold Period:")
    hold_ranges = [
        (0, 1, "1 day"),
        (1, 2, "2 days"),
        (2, 3, "3 days"),
        (3, 4, "4 days"),
        (4, 5, "5 days"),
        (5, 10, "6-10 days"),
        (10, 100, ">10 days")
    ]
    
    for min_days, max_days, label in hold_ranges:
        if max_days == 100:
            count = len(df[df['hold_days'] > min_days])
        else:
            count = len(df[(df['hold_days'] > min_days) & (df['hold_days'] <= max_days)])
        pct = (count / len(df)) * 100 if len(df) > 0 else 0
        if count > 0:
            avg_ret = df[(df['hold_days'] > min_days) & (df['hold_days'] <= max_days)]['actual_return'].mean() if max_days < 100 else df[df['hold_days'] > min_days]['actual_return'].mean()
            print(f"  {label}: {count} ({pct:.1f}%) - Avg Return: {avg_ret:.2f}%")
    
    print(f"\n❓ Is Max Hold 5 days necessary?")
    print(f"\n  Trades that hold >3 days: {len(df[df['hold_days'] > 3])} ({len(df[df['hold_days'] > 3])/len(df)*100:.1f}%)")
    print(f"  Trades that hold >4 days: {len(df[df['hold_days'] > 4])} ({len(df[df['hold_days'] > 4])/len(df)*100:.1f}%)")
    print(f"  Trades that hold >5 days: {len(df[df['hold_days'] > 5])} ({len(df[df['hold_days'] > 5])/len(df)*100:.1f}%)")
    
    # Analyze exit reasons for longer holds
    if 'exit_reason' in df.columns:
        print(f"\n  Exit Reasons for Trades >3 days:")
        long_holds = df[df['hold_days'] > 3]
        if len(long_holds) > 0:
            exit_counts = long_holds['exit_reason'].value_counts()
            for reason in exit_counts.index:
                count = exit_counts[reason]
                pct = (count / len(long_holds)) * 100
                print(f"    {reason}: {count} ({pct:.1f}%)")
        else:
            print(f"    No trades hold >3 days")
    
    # Recommendation
    print(f"\n💡 Recommendation:")
    
    max_hold_actual = df['hold_days'].max()
    p95_hold = df['hold_days'].quantile(0.95)
    p99_hold = df['hold_days'].quantile(0.99)
    
    trades_over_3 = len(df[df['hold_days'] > 3])
    trades_over_4 = len(df[df['hold_days'] > 4])
    trades_over_5 = len(df[df['hold_days'] > 5])
    
    if trades_over_5 == 0:
        print(f"  ✅ Max Hold 5 days ไม่จำเป็น!")
        print(f"  💡 แนะนำ: Max Hold 3-4 days (เพียงพอ)")
        print(f"  📊 เหตุผล:")
        print(f"     - ไม่มี trades ที่ hold >5 days")
        print(f"     - 95% ของ trades ออกใน {p95_hold:.0f} days")
        print(f"     - Max Hold จริง: {max_hold_actual:.0f} days")
    elif trades_over_4 == 0:
        print(f"  ✅ Max Hold 4 days ไม่จำเป็น!")
        print(f"  💡 แนะนำ: Max Hold 3 days (เพียงพอ)")
        print(f"  📊 เหตุผล:")
        print(f"     - ไม่มี trades ที่ hold >4 days")
        print(f"     - 95% ของ trades ออกใน {p95_hold:.0f} days")
    elif trades_over_3 == 0:
        print(f"  ✅ Max Hold 3 days ไม่จำเป็น!")
        print(f"  💡 แนะนำ: Max Hold 2 days (เพียงพอ)")
        print(f"  📊 เหตุผล:")
        print(f"     - ไม่มี trades ที่ hold >3 days")
        print(f"     - 95% ของ trades ออกใน {p95_hold:.0f} days")
    else:
        print(f"  ⚠️  Max Hold 5 days อาจจำเป็น")
        print(f"  📊 เหตุผล:")
        print(f"     - มี {trades_over_5} trades ที่ hold >5 days ({trades_over_5/len(df)*100:.1f}%)")
        print(f"     - 95% ของ trades ออกใน {p95_hold:.0f} days")
        print(f"     - Max Hold จริง: {max_hold_actual:.0f} days")
    
    # Optimal Max Hold
    print(f"\n🎯 Optimal Max Hold:")
    if p95_hold <= 2:
        optimal = 3
    elif p95_hold <= 3:
        optimal = 4
    elif p95_hold <= 4:
        optimal = 5
    else:
        optimal = int(p95_hold) + 1
    
    print(f"  Recommended: {optimal} days")
    print(f"  Based on: 95th percentile = {p95_hold:.0f} days")
    print(f"  Current: 5 days")
    print(f"  Difference: {optimal - 5} days")
    
    if optimal < 5:
        print(f"  ✅ สามารถลด Max Hold จาก 5 → {optimal} days ได้")
    elif optimal == 5:
        print(f"  ✅ Max Hold 5 days เหมาะสม")
    else:
        print(f"  ⚠️  อาจต้องเพิ่ม Max Hold เป็น {optimal} days")
    
    return {
        'max_hold_actual': max_hold_actual,
        'p95_hold': p95_hold,
        'p99_hold': p99_hold,
        'trades_over_3': trades_over_3,
        'trades_over_4': trades_over_4,
        'trades_over_5': trades_over_5,
        'optimal_max_hold': optimal
    }

if __name__ == '__main__':
    result = analyze_max_hold_necessity()
    
    if result:
        print(f"\n{'='*100}")
        print("Summary")
        print(f"{'='*100}")
        print(f"\nMax Hold Actual: {result['max_hold_actual']:.0f} days")
        print(f"95th Percentile: {result['p95_hold']:.0f} days")
        print(f"Trades >5 days: {result['trades_over_5']} ({result['trades_over_5']/2988*100:.1f}%)")
        print(f"\nOptimal Max Hold: {result['optimal_max_hold']} days")
        print(f"Current Max Hold: 5 days")
        
        if result['optimal_max_hold'] < 5:
            print(f"\n✅ สามารถลด Max Hold จาก 5 → {result['optimal_max_hold']} days")
        else:
            print(f"\n✅ Max Hold 5 days เหมาะสม")

