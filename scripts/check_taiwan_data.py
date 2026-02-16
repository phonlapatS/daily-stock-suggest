#!/usr/bin/env python
"""
Check Taiwan Data - ตรวจสอบข้อมูล Taiwan market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_taiwan_data():
    """ตรวจสอบข้อมูล Taiwan market"""
    
    print("="*80)
    print("Check Taiwan Data - ตรวจสอบข้อมูล Taiwan Market")
    print("="*80)
    print()
    
    # 1. ตรวจสอบ symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            
            print(f"✅ พบ: {perf_file}")
            print(f"   Total Taiwan symbols: {len(tw)}")
            print()
            
            if len(tw) > 0:
                print("   Top 10 Taiwan symbols (sorted by Prob%):")
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
                print("-" * 40)
                
                for idx, row in tw.nlargest(10, 'Prob%').iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
                
                print()
                print("   Current Criteria: Prob >= 60%, RRR >= 1.25, Count >= 25")
                print()
                
                # ตรวจสอบหุ้นที่ผ่าน criteria ต่างๆ
                criteria_60_125_25 = tw[
                    (tw['Prob%'] >= 60.0) & 
                    (tw['RR_Ratio'] >= 1.25) & 
                    (tw['Count'] >= 25)
                ]
                print(f"   ✅ Prob >= 60%, RRR >= 1.25, Count >= 25: {len(criteria_60_125_25)} หุ้น")
                
                criteria_57_105_15 = tw[
                    (tw['Prob%'] >= 57.0) & 
                    (tw['RR_Ratio'] >= 1.05) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 57%, RRR >= 1.05, Count >= 15: {len(criteria_57_105_15)} หุ้น")
                
                criteria_55_100_15 = tw[
                    (tw['Prob%'] >= 55.0) & 
                    (tw['RR_Ratio'] >= 1.0) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 55%, RRR >= 1.0, Count >= 15: {len(criteria_55_100_15)} หุ้น")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print()
    print("="*80)

if __name__ == '__main__':
    check_taiwan_data()

