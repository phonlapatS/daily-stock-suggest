#!/usr/bin/env python
"""
Create China Market Comparison Table - แบบเดียวกับไต้หวัน

สร้างตารางเปรียบเทียบ:
1. Results Table (หุ้นที่ผ่านเกณฑ์)
2. Version Comparison Table (เปรียบเทียบหลาย version)
3. Performance Summary
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
    """Create main results table"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        print("❌ File not found")
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        return None
    
    # V13.1/V13.2 criteria
    passing = china_df[
        (china_df['Prob%'] >= 53.0) &
        (china_df['RR_Ratio'] >= 0.95) &
        (china_df['Count'] >= 10)
    ].copy()
    
    if len(passing) == 0:
        print("❌ No stocks passing criteria")
        return None
    
    passing = passing.sort_values('Prob%', ascending=False)
    passing['Name'] = passing['symbol'].map(STOCK_NAMES).fillna(passing['symbol'])
    
    # Print table
    print("="*100)
    print("ผลลัพธ์ V13.2 (China Market Focus)")
    print("="*100)
    print(f"หุ้นที่ผ่านเกณฑ์ ({len(passing)} หุ้น)")
    print("="*100)
    print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<10} {'Count':<10} {'Status':<10}")
    print("-" * 100)
    
    for _, row in passing.iterrows():
        print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}     {row['Count']:>6.0f}     ✅ PASS")
    
    # Summary
    print(f"\n{'='*100}")
    print("สรุปผลลัพธ์")
    print(f"{'='*100}")
    print(f"  จำนวนหุ้นที่ผ่าน: {len(passing)} หุ้น")
    print(f"  Prob% เฉลี่ย: {passing['Prob%'].mean():.1f}%")
    print(f"  RRR เฉลี่ย: {passing['RR_Ratio'].mean():.2f}")
    print(f"  Count เฉลี่ย: {passing['Count'].mean():.0f}")
    print(f"  Total Trades: {passing['Count'].sum():.0f}")
    
    return passing

def create_version_comparison():
    """Create version comparison table"""
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(perf_file):
        return None
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        return None
    
    # Different version scenarios
    versions = [
        {'name': 'V13.2 (Current)', 'prob': 53.0, 'rrr': 0.95, 'count': 10, 'desc': 'Prob>=53%, RRR>=0.95, Count>=10'},
        {'name': 'V13.1', 'prob': 53.0, 'rrr': 0.95, 'count': 10, 'desc': 'Prob>=53%, RRR>=0.95, Count>=10'},
        {'name': 'V13.0', 'prob': 53.0, 'rrr': 1.0, 'count': 15, 'desc': 'Prob>=53%, RRR>=1.0, Count>=15'},
        {'name': 'Strict', 'prob': 55.0, 'rrr': 1.2, 'count': 20, 'desc': 'Prob>=55%, RRR>=1.2, Count>=20'},
        {'name': 'Relaxed', 'prob': 50.0, 'rrr': 0.9, 'count': 10, 'desc': 'Prob>=50%, RRR>=0.9, Count>=10'},
    ]
    
    results = []
    
    for version in versions:
        passing = china_df[
            (china_df['Prob%'] >= version['prob']) &
            (china_df['RR_Ratio'] >= version['rrr']) &
            (china_df['Count'] >= version['count'])
        ]
        
        if len(passing) > 0:
            results.append({
                'Version': version['name'],
                'Stocks': len(passing),
                'Avg Prob%': passing['Prob%'].mean(),
                'Avg RRR': passing['RR_Ratio'].mean(),
                'Avg Count': passing['Count'].mean(),
                'Total Trades': passing['Count'].sum(),
                'Best Prob%': passing['Prob%'].max(),
                'Best RRR': passing['RR_Ratio'].max(),
                'Symbols': ', '.join(passing['symbol'].tolist())
            })
    
    if results:
        results_df = pd.DataFrame(results)
        
        print(f"\n{'='*100}")
        print("Version Comparison Table")
        print(f"{'='*100}")
        print(f"\n{'Version':<20} {'Stocks':<8} {'Avg Prob%':<12} {'Avg RRR':<10} {'Avg Count':<12} {'Total Trades':<12} {'Best Prob%':<12} {'Best RRR':<10}")
        print("-" * 100)
        
        for _, row in results_df.iterrows():
            print(f"{row['Version']:<20} {row['Stocks']:<8} {row['Avg Prob%']:>8.1f}%     {row['Avg RRR']:>6.2f}     {row['Avg Count']:>8.0f}       {row['Total Trades']:>8.0f}       {row['Best Prob%']:>8.1f}%     {row['Best RRR']:>6.2f}")
        
        results_df.to_csv('data/china_version_comparison.csv', index=False)
        print(f"\n✅ Saved to: data/china_version_comparison.csv")
    
    return results

def main():
    """Main function"""
    # Create main results table
    passing = create_results_table()
    
    # Create version comparison
    if passing is not None:
        create_version_comparison()

if __name__ == '__main__':
    main()

