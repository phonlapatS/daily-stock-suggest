#!/usr/bin/env python
"""
Display China Market Results Table - แสดงตารางผลลัพธ์แบบเดียวกับที่เห็นในภาพ
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def display_table_from_image():
    """Display table from image data (V13.0)"""
    print("="*100)
    print("ผลลัพธ์ V13.0 (China Market Focus)")
    print("="*100)
    print("หุ้นที่ผ่านเกณฑ์ (3 หุ้น)")
    print("="*100)
    
    # Data from image
    data = [
        {'Symbol': '3690', 'Name': 'MEITUAN', 'Prob%': 76.9, 'RRR': 1.22, 'Count': 39, 'Status': 'PASS'},
        {'Symbol': '1211', 'Name': 'BYD', 'Prob%': 59.1, 'RRR': 1.00, 'Count': 159, 'Status': 'PASS'},
        {'Symbol': '9618', 'Name': 'JD-COM', 'Prob%': 54.2, 'RRR': 1.20, 'Count': 24, 'Status': 'PASS'},
    ]
    
    df = pd.DataFrame(data)
    
    # Print table
    print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<10} {'Count':<10} {'Status':<10}")
    print("-" * 100)
    
    for _, row in df.iterrows():
        print(f"{row['Symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RRR']:>6.2f}     {row['Count']:>6.0f}     ✅ PASS")
    
    # Summary
    print("\n" + "="*100)
    print("สรุปผลลัพธ์")
    print("="*100)
    print(f"  จำนวนหุ้นที่ผ่าน: {len(df)} หุ้น")
    print(f"  Prob% เฉลี่ย: {df['Prob%'].mean():.1f}%")
    print(f"  RRR เฉลี่ย: {df['RRR'].mean():.2f}")
    print(f"  Count เฉลี่ย: {df['Count'].mean():.0f}")
    print(f"  Total Trades: {df['Count'].sum():.0f}")
    
    # Best metrics
    best_prob = df.loc[df['Prob%'].idxmax()]
    best_rrr = df.loc[df['RR_Ratio'].idxmax()] if 'RR_Ratio' in df.columns else df.loc[df['RRR'].idxmax()]
    
    print(f"\n  Best Prob%: {best_prob['Prob%']:.1f}% ({best_prob['Symbol']} - {best_prob['Name']})")
    print(f"  Best RRR: {best_rrr['RRR']:.2f} ({best_rrr['Symbol']} - {best_rrr['Name']})")
    
    return df

def display_comparison_with_taiwan():
    """Display comparison with Taiwan"""
    print("\n" + "="*100)
    print("Comparison with Taiwan V12.4")
    print("="*100)
    
    comparison_data = [
        {'Metric': 'Stocks Passing', 'Taiwan V12.4': 2, 'China V13.0': 3, 'Difference': '+1', 'Status': '✅ Better'},
        {'Metric': 'Avg Prob%', 'Taiwan V12.4': '66.95%', 'China V13.0': '63.4%', 'Difference': '-3.55%', 'Status': '⚠️ Lower'},
        {'Metric': 'Avg RRR', 'Taiwan V12.4': 1.68, 'China V13.0': 1.14, 'Difference': '-0.54', 'Status': '⚠️ Lower'},
        {'Metric': 'Avg Count', 'Taiwan V12.4': 65.5, 'China V13.0': 74, 'Difference': '+8.5', 'Status': '➡️ Similar'},
        {'Metric': 'Total Trades', 'Taiwan V12.4': 131, 'China V13.0': 222, 'Difference': '+91', 'Status': '⚠️ Higher'},
        {'Metric': 'Best Prob%', 'Taiwan V12.4': '71.4%', 'China V13.0': '76.9%', 'Difference': '+5.5%', 'Status': '✅ Better'},
        {'Metric': 'Best RRR', 'Taiwan V12.4': 1.95, 'China V13.0': 1.22, 'Difference': '-0.73', 'Status': '⚠️ Lower'},
    ]
    
    comp_df = pd.DataFrame(comparison_data)
    
    print(f"\n{'Metric':<20} {'Taiwan V12.4':<15} {'China V13.0':<15} {'Difference':<12} {'Status':<15}")
    print("-" * 100)
    
    for _, row in comp_df.iterrows():
        print(f"{row['Metric']:<20} {str(row['Taiwan V12.4']):<15} {str(row['China V13.0']):<15} {str(row['Difference']):<12} {row['Status']:<15}")

def main():
    """Main function"""
    # Display table from image
    df = display_table_from_image()
    
    # Display comparison
    display_comparison_with_taiwan()
    
    # Save to CSV
    output_file = 'data/china_v13_results_table.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")

if __name__ == '__main__':
    main()

