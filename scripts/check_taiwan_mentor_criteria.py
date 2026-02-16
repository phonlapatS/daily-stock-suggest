#!/usr/bin/env python
"""
Check Taiwan Mentor Criteria - ตรวจสอบหุ้นที่ผ่าน Prob >= 60%, RRR >= 1.5
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_taiwan_mentor_criteria():
    """ตรวจสอบหุ้นที่ผ่าน Prob >= 60%, RRR >= 1.5"""
    
    print("="*80)
    print("Check Taiwan Mentor Criteria - Prob >= 60%, RRR >= 1.5")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            
            # Mentor criteria: Prob >= 60%, RRR >= 1.5, Count >= 15
            criteria = tw[
                (tw['Prob%'] >= 60.0) & 
                (tw['RR_Ratio'] >= 1.5) & 
                (tw['Count'] >= 15)
            ]
            
            print("1. หุ้นที่ผ่าน Prob >= 60%, RRR >= 1.5, Count >= 15:")
            print("-" * 80)
            print(f"Total: {len(criteria)} หุ้น")
            print()
            
            if len(criteria) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
                print("-" * 40)
                for idx, row in criteria.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
            else:
                print("❌ ไม่มีหุ้นที่ผ่าน criteria นี้")
            
            print()
            print("2. หุ้นที่มี Prob >= 60% (เพื่อดู RRR):")
            print("-" * 80)
            high_prob = tw[tw['Prob%'] >= 60.0]
            print(f"Total: {len(high_prob)} หุ้น")
            print()
            
            if len(high_prob) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
                print("-" * 40)
                for idx, row in high_prob.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
            
            print()
            print("3. ข้อเสนอแนะ:")
            print("-" * 80)
            if len(criteria) == 0:
                print("⚠️  ไม่มีหุ้นที่ผ่าน Prob >= 60%, RRR >= 1.5")
                print()
                print("💡 ทางเลือก:")
                print("   1. ลด Prob% เป็น 55% (ยังคง Prob สูง)")
                print("   2. ลด RRR เป็น 1.3 (ยังคง RRR คุ้มค่า)")
                print("   3. ใช้ Prob >= 60%, RRR >= 1.2 (ใกล้เคียง)")
                print()
                if len(high_prob) > 0:
                    max_rrr = high_prob['RR_Ratio'].max()
                    print(f"   หุ้นที่มี Prob >= 60% มี RRR สูงสุด: {max_rrr:.2f}")
            else:
                print("✅ มีหุ้นที่ผ่าน criteria แล้ว")
            
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    check_taiwan_mentor_criteria()

