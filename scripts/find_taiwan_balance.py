#!/usr/bin/env python
"""
Find Taiwan Balance - หา balance ที่เหมาะสมสำหรับ Taiwan market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def find_taiwan_balance():
    """หา balance ที่เหมาะสมสำหรับ Taiwan market"""
    
    print("="*80)
    print("Find Taiwan Balance - หา balance ที่เหมาะสม")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW'].copy()
            
            print("1. หุ้นที่มี RRR >= 1.2 (เพื่อดู Prob%):")
            print("-" * 80)
            high_rrr = tw[tw['RR_Ratio'] >= 1.2]
            print(f"Total: {len(high_rrr)} หุ้น")
            print()
            
            if len(high_rrr) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
                print("-" * 40)
                for idx, row in high_rrr.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
            else:
                print("❌ ไม่มีหุ้นที่มี RRR >= 1.2")
            
            print()
            print("2. เปรียบเทียบ Criteria ต่างๆ:")
            print("-" * 80)
            
            # Option 1: Prob >= 60%, RRR >= 1.5 (Mentor ideal)
            opt1 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option 1: Prob >= 60%, RRR >= 1.5, Count >= 15: {len(opt1)} หุ้น")
            
            # Option 2: Prob >= 60%, RRR >= 1.2 (ใกล้เคียง)
            opt2 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 1.2) & (tw['Count'] >= 15)]
            print(f"   Option 2: Prob >= 60%, RRR >= 1.2, Count >= 15: {len(opt2)} หุ้น")
            
            # Option 3: Prob >= 60%, RRR >= 1.0 (ลด RRR)
            opt3 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 1.0) & (tw['Count'] >= 15)]
            print(f"   Option 3: Prob >= 60%, RRR >= 1.0, Count >= 15: {len(opt3)} หุ้น")
            if len(opt3) > 0:
                for idx, row in opt3.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}")
            
            # Option 4: Prob >= 55%, RRR >= 1.5 (ลด Prob)
            opt4 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option 4: Prob >= 55%, RRR >= 1.5, Count >= 15: {len(opt4)} หุ้น")
            
            # Option 5: Prob >= 55%, RRR >= 1.3 (balance)
            opt5 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.3) & (tw['Count'] >= 15)]
            print(f"   Option 5: Prob >= 55%, RRR >= 1.3, Count >= 15: {len(opt5)} หุ้น")
            
            print()
            print("3. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   ⚠️  Taiwan market ไม่มีหุ้นที่ผ่าน Prob >= 60%, RRR >= 1.5")
            print()
            print("   💡 ปัญหา:")
            print("      - หุ้นที่มี Prob >= 60% → RRR ต่ำ (3008: Prob 64.7%, RRR 0.77)")
            print("      - หุ้นที่มี RRR >= 1.5 → Prob ต่ำ (2317: Prob 49.2%, RRR 1.70)")
            print()
            print("   💡 ทางเลือก:")
            if len(opt3) > 0:
                print(f"      ✅ Option 3: Prob >= 60%, RRR >= 1.0 → ได้ {len(opt3)} หุ้น")
                print("         (Prob สูงตามที่ mentor ต้องการ แต่ RRR ต่ำกว่า 1.5)")
            if len(opt4) > 0:
                print(f"      ✅ Option 4: Prob >= 55%, RRR >= 1.5 → ได้ {len(opt4)} หุ้น")
                print("         (RRR สูงตามที่ mentor ต้องการ แต่ Prob ต่ำกว่า 60%)")
            if len(opt5) > 0:
                print(f"      ✅ Option 5: Prob >= 55%, RRR >= 1.3 → ได้ {len(opt5)} หุ้น")
                print("         (Balance ระหว่าง Prob และ RRR)")
            print()
            print("   💡 หรือตรวจสอบว่า Taiwan ใช้ Mean Reversion หรือ Trend Following")
            print("      - Config: engine = 'TREND_MOMENTUM'")
            print("      - Backtest: Regime-Aware (BULL → TREND, BEAR/SIDEWAYS → REVERSION)")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    find_taiwan_balance()

