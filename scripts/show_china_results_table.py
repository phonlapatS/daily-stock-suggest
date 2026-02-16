#!/usr/bin/env python
"""
Show China Market Results Table - แสดงตารางผลลัพธ์แบบเดียวกับที่เห็นในภาพ

รูปแบบตาราง:
- Symbol, Name, Prob%, RRR, Count, Status
- คล้ายๆกับตารางไต้หวัน
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

# Stock names mapping
STOCK_NAMES = {
    '3690': 'MEITUAN',
    '1211': 'BYD',
    '9618': 'JD-COM',
    '2015': 'LI-AUTO',
    '700': 'TENCENT',
    '9988': 'ALIBABA',
    '1810': 'XIAOMI',
    '9888': 'BAIDU',
    '9868': 'XPENG',
    '9866': 'NIO'
}

def show_results_table():
    """Show results table"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        print("❌ File not found: symbol_performance.csv")
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        print("\nPlease run backtest first:")
        print("  python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        print("  python scripts/calculate_metrics.py")
        return None
    
    # Apply display criteria (V13.1/V13.2)
    # Prob >= 53%, RRR >= 0.95, Count >= 10
    passing = china_df[
        (china_df['Prob%'] >= 53.0) &
        (china_df['RR_Ratio'] >= 0.95) &
        (china_df['Count'] >= 10)
    ].copy()
    
    if len(passing) == 0:
        print("❌ No stocks passing criteria")
        print("\nCurrent Criteria:")
        print("  Prob% >= 53.0%")
        print("  RRR >= 0.95")
        print("  Count >= 10")
        print("\nAll China stocks:")
        if len(china_df) > 0:
            china_df['Name'] = china_df['symbol'].map(STOCK_NAMES).fillna(china_df['symbol'])
            print(china_df[['symbol', 'Name', 'Prob%', 'RR_Ratio', 'Count']].to_string(index=False))
        return None
    
    # Sort by Prob% descending
    passing = passing.sort_values('Prob%', ascending=False)
    
    # Add Name column
    passing['Name'] = passing['symbol'].map(STOCK_NAMES).fillna(passing['symbol'])
    
    # Create table
    print("="*100)
    print("ผลลัพธ์ V13.2 (China Market Focus)")
    print("="*100)
    print(f"หุ้นที่ผ่านเกณฑ์ ({len(passing)} หุ้น)")
    print("="*100)
    
    # Table header
    print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<10} {'Count':<10} {'Status':<10}")
    print("-" * 100)
    
    # Table rows
    for _, row in passing.iterrows():
        symbol = row['symbol']
        name = row['Name']
        prob = row['Prob%']
        rrr = row['RR_Ratio']
        count = row['Count']
        
        print(f"{symbol:<12} {name:<15} {prob:>6.1f}%     {rrr:>6.2f}     {count:>6.0f}     ✅ PASS")
    
    # Summary
    print("\n" + "="*100)
    print("สรุปผลลัพธ์")
    print("="*100)
    print(f"  จำนวนหุ้นที่ผ่าน: {len(passing)} หุ้น")
    print(f"  Prob% เฉลี่ย: {passing['Prob%'].mean():.1f}%")
    print(f"  RRR เฉลี่ย: {passing['RR_Ratio'].mean():.2f}")
    print(f"  Count เฉลี่ย: {passing['Count'].mean():.0f}")
    print(f"  Total Trades: {passing['Count'].sum():.0f}")
    
    # Best metrics
    best_prob = passing.loc[passing['Prob%'].idxmax()]
    best_rrr = passing.loc[passing['RR_Ratio'].idxmax()]
    
    print(f"\n  Best Prob%: {best_prob['Prob%']:.1f}% ({best_prob['symbol']} - {best_prob['Name']})")
    print(f"  Best RRR: {best_rrr['RR_Ratio']:.2f} ({best_rrr['symbol']} - {best_rrr['Name']})")
    
    # Assessment
    avg_rrr = passing['RR_Ratio'].mean()
    avg_prob = passing['Prob%'].mean()
    
    print(f"\n  Assessment:")
    if avg_rrr >= 1.5 and avg_prob >= 60:
        print(f"    ✅ ✅ ✅ EXCELLENT: RRR และ Prob% ดีมาก")
    elif avg_rrr >= 1.3 and avg_prob >= 55:
        print(f"    ✅ ✅ GOOD: RRR และ Prob% ดี")
    elif avg_rrr >= 1.2 and avg_prob >= 53:
        print(f"    ✅ ACCEPTABLE: RRR และ Prob% พอใช้")
    else:
        print(f"    ⚠️  NEEDS IMPROVEMENT: RRR หรือ Prob% ต่ำ")
    
    # Save to CSV
    output_file = 'data/china_results_table.csv'
    passing[['symbol', 'Name', 'Prob%', 'RR_Ratio', 'Count']].to_csv(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")
    
    return passing

if __name__ == '__main__':
    show_results_table()

