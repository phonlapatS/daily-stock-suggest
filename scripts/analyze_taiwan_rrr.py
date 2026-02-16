#!/usr/bin/env python
"""
Analyze Taiwan RRR - วิเคราะห์ RRR ของ Taiwan market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_taiwan_rrr():
    """วิเคราะห์ RRR ของ Taiwan market"""
    
    print("="*80)
    print("Analyze Taiwan RRR - วิเคราะห์ RRR ของ Taiwan Market")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            
            print("1. Taiwan symbols sorted by RRR (descending):")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
            print("-" * 80)
            
            for idx, row in tw.nlargest(10, 'RR_Ratio').iterrows():
                symbol = row.get('symbol', 'N/A')
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                count = row.get('Count', 0)
                print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
            
            print()
            print("2. หุ้นที่มี RRR >= 1.1:")
            print("-" * 80)
            high_rrr = tw[tw['RR_Ratio'] >= 1.1]
            print(f"Total: {len(high_rrr)} หุ้น")
            
            if len(high_rrr) > 0:
                for idx, row in high_rrr.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    print(f"   {symbol}: Prob {prob:.1f}%, RRR {rrr:.2f}, Count {count:,}")
            else:
                print("   ❌ ไม่มีหุ้นที่มี RRR >= 1.1")
            
            print()
            print("3. เปรียบเทียบกับตลาดอื่น:")
            print("-" * 80)
            print("   - CHINA: RRR >= 1.2 (3 หุ้น)")
            print("   - US: RRR >= 1.5 (7 หุ้น)")
            print("   - THAI: RRR >= 1.3 (30 หุ้น)")
            print()
            print("   - TAIWAN: RRR >= 1.0 (3 หุ้น) ← ต่ำที่สุด")
            print()
            
            print("4. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   ⚠️  RRR 1.02-1.07 ต่ำมาก (ใกล้ break-even)")
            print("   💡 ควรเพิ่ม RRR requirement เป็น 1.1 แต่จะไม่มีหุ้นผ่าน")
            print("   💡 หรือลด Prob% ลงเพื่อให้ได้หุ้นที่มี RRR สูงกว่า")
            print("   💡 หรือเก็บ criteria เดิมไว้ (Prob >= 55%, RRR >= 1.0)")
            print("      เพราะ Taiwan มี commission สูง (0.44%)")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_taiwan_rrr()

