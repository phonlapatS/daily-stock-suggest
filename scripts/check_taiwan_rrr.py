#!/usr/bin/env python
"""
Check Taiwan RRR - ตรวจสอบ RRR ของ Taiwan market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_taiwan_rrr():
    """ตรวจสอบ RRR ของ Taiwan market"""
    
    print("="*80)
    print("Check Taiwan RRR - ตรวจสอบ RRR ของ Taiwan Market")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            
            print(f"✅ พบ: {perf_file}")
            print(f"   Total Taiwan symbols: {len(tw)}")
            print()
            
            if len(tw) > 0:
                print("   เปรียบเทียบ Criteria ต่างๆ:")
                print()
                
                # Current: Prob >= 55%, RRR >= 1.0, Count >= 15
                criteria_current = tw[
                    (tw['Prob%'] >= 55.0) & 
                    (tw['RR_Ratio'] >= 1.0) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 55%, RRR >= 1.0, Count >= 15: {len(criteria_current)} หุ้น")
                if len(criteria_current) > 0:
                    for idx, row in criteria_current.iterrows():
                        print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
                print()
                
                # Option 1: Prob >= 55%, RRR >= 1.1, Count >= 15
                criteria_1 = tw[
                    (tw['Prob%'] >= 55.0) & 
                    (tw['RR_Ratio'] >= 1.1) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 55%, RRR >= 1.1, Count >= 15: {len(criteria_1)} หุ้น")
                if len(criteria_1) > 0:
                    for idx, row in criteria_1.iterrows():
                        print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
                print()
                
                # Option 2: Prob >= 55%, RRR >= 1.15, Count >= 15
                criteria_2 = tw[
                    (tw['Prob%'] >= 55.0) & 
                    (tw['RR_Ratio'] >= 1.15) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 55%, RRR >= 1.15, Count >= 15: {len(criteria_2)} หุ้น")
                if len(criteria_2) > 0:
                    for idx, row in criteria_2.iterrows():
                        print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
                print()
                
                # Option 3: Prob >= 57%, RRR >= 1.1, Count >= 15
                criteria_3 = tw[
                    (tw['Prob%'] >= 57.0) & 
                    (tw['RR_Ratio'] >= 1.1) & 
                    (tw['Count'] >= 15)
                ]
                print(f"   ✅ Prob >= 57%, RRR >= 1.1, Count >= 15: {len(criteria_3)} หุ้น")
                if len(criteria_3) > 0:
                    for idx, row in criteria_3.iterrows():
                        print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
                print()
                
                print("   💡 เปรียบเทียบกับตลาดอื่น:")
                print("      - CHINA: RRR >= 1.2")
                print("      - US: RRR >= 1.5")
                print("      - THAI: RRR >= 1.3")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    check_taiwan_rrr()

