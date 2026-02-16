#!/usr/bin/env python
"""
Create China Market Results Table - สร้างตารางผลลัพธ์แบบเดียวกับที่เห็นในภาพ

รูปแบบตาราง:
- Symbol, Name, Prob%, RRR, Count, Status
- แสดงหุ้นที่ผ่านเกณฑ์
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

def create_results_table():
    """Create results table"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        print("❌ File not found: symbol_performance.csv")
        print("   Please run calculate_metrics.py first")
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found in symbol_performance.csv")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        return None
    
    # Apply display criteria (V13.1)
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
        print(china_df[['symbol', 'Prob%', 'RR_Ratio', 'Count']].to_string(index=False))
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
    
    # Save to CSV
    output_file = 'data/china_results_table.csv'
    passing[['symbol', 'Name', 'Prob%', 'RR_Ratio', 'Count']].to_csv(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")
    
    return passing

def create_comparison_table():
    """Create comparison table with different versions/parameters"""
    print("\n" + "="*100)
    print("China Market - Version Comparison Table")
    print("="*100)
    
    # This would compare different versions/parameters
    # For now, just show current results
    
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        print("❌ File not found")
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        return None
    
    # Different criteria scenarios
    scenarios = [
        {'name': 'V13.2 (Current)', 'prob': 53.0, 'rrr': 0.95, 'count': 10},
        {'name': 'V13.1', 'prob': 53.0, 'rrr': 0.95, 'count': 10},
        {'name': 'V13.0', 'prob': 53.0, 'rrr': 1.0, 'count': 15},
        {'name': 'Strict', 'prob': 55.0, 'rrr': 1.2, 'count': 20},
        {'name': 'Relaxed', 'prob': 50.0, 'rrr': 0.9, 'count': 10},
    ]
    
    results = []
    
    for scenario in scenarios:
        passing = china_df[
            (china_df['Prob%'] >= scenario['prob']) &
            (china_df['RR_Ratio'] >= scenario['rrr']) &
            (china_df['Count'] >= scenario['count'])
        ]
        
        if len(passing) > 0:
            results.append({
                'Version': scenario['name'],
                'Criteria': f"Prob>={scenario['prob']}%, RRR>={scenario['rrr']}, Count>={scenario['count']}",
                'Stocks': len(passing),
                'Avg Prob%': passing['Prob%'].mean(),
                'Avg RRR': passing['RR_Ratio'].mean(),
                'Avg Count': passing['Count'].mean(),
                'Total Trades': passing['Count'].sum(),
                'Symbols': ', '.join(passing['symbol'].tolist())
            })
    
    if results:
        results_df = pd.DataFrame(results)
        
        print(f"\n{'Version':<20} {'Stocks':<8} {'Avg Prob%':<12} {'Avg RRR':<10} {'Avg Count':<12} {'Total Trades':<12} {'Symbols':<30}")
        print("-" * 100)
        for _, row in results_df.iterrows():
            print(f"{row['Version']:<20} {row['Stocks']:<8} {row['Avg Prob%']:>8.1f}%     {row['Avg RRR']:>6.2f}     {row['Avg Count']:>8.0f}       {row['Total Trades']:>8.0f}       {row['Symbols']:<30}")
        
        results_df.to_csv('data/china_version_comparison.csv', index=False)
        print(f"\n✅ Saved to: data/china_version_comparison.csv")
    
    return results

if __name__ == '__main__':
    # Create main results table
    passing = create_results_table()
    
    # Create comparison table
    if passing is not None:
        create_comparison_table()

