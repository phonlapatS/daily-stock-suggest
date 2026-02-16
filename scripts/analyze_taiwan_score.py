#!/usr/bin/env python
"""
Analyze Taiwan Score - วิเคราะห์หุ้นไต้หวันเรียงตาม Score (Prob% * RRR)
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_taiwan_score():
    """วิเคราะห์หุ้นไต้หวันเรียงตาม Score"""
    
    print("="*80)
    print("Analyze Taiwan Score - Prob% * RRR")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW'].copy()
            tw['Score'] = tw['Prob%'] * tw['RR_Ratio'] / 100
            
            print("1. หุ้นไต้หวันเรียงตาม Score (Prob% * RRR / 100):")
            print("-" * 80)
            
            tw_sorted = tw[tw['Count'] >= 15].sort_values(by='Score', ascending=False)
            
            print(f"Total: {len(tw_sorted)} หุ้น")
            print()
            print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
            print("-" * 50)
            
            for idx, row in tw_sorted.head(15).iterrows():
                symbol = row.get('symbol', 'N/A')
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                count = row.get('Count', 0)
                score = row.get('Score', 0)
                print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("2. วิเคราะห์ Criteria เพื่อหา Balance (Prob% ใกล้ 60%, RRR ใกล้ 2):")
            print("-" * 80)
            
            # Option 1: Prob >= 50%, RRR >= 1.5 (เพื่อให้ได้ 2317)
            opt1 = tw[(tw['Prob%'] >= 50.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option 1: Prob >= 50%, RRR >= 1.5, Count >= 15: {len(opt1)} หุ้น")
            if len(opt1) > 0:
                for idx, row in opt1.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 2: Prob >= 55%, RRR >= 1.0 (เพื่อให้ได้หุ้นที่มี Prob ใกล้ 60%)
            opt2 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0) & (tw['Count'] >= 15)]
            print(f"   Option 2: Prob >= 55%, RRR >= 1.0, Count >= 15: {len(opt2)} หุ้น")
            if len(opt2) > 0:
                for idx, row in opt2.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 3: Score >= 0.6 (Prob% * RRR / 100)
            opt3 = tw[(tw['Score'] >= 0.6) & (tw['Count'] >= 15)]
            print(f"   Option 3: Score >= 0.6, Count >= 15: {len(opt3)} หุ้น")
            if len(opt3) > 0:
                for idx, row in opt3.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 4: Prob >= 55%, RRR >= 1.05 (เพื่อให้ได้หุ้นที่มี Prob ใกล้ 60% และ RRR ใกล้ 1.0)
            opt4 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.05) & (tw['Count'] >= 15)]
            print(f"   Option 4: Prob >= 55%, RRR >= 1.05, Count >= 15: {len(opt4)} หุ้น")
            if len(opt4) > 0:
                for idx, row in opt4.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 5: Prob >= 50%, RRR >= 1.5 หรือ Prob >= 55%, RRR >= 1.0
            opt5 = tw[
                ((tw['Prob%'] >= 50.0) & (tw['RR_Ratio'] >= 1.5)) |
                ((tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0))
            ]
            opt5 = opt5[opt5['Count'] >= 15]
            print(f"   Option 5: (Prob >= 50%, RRR >= 1.5) OR (Prob >= 55%, RRR >= 1.0), Count >= 15: {len(opt5)} หุ้น")
            if len(opt5) > 0:
                for idx, row in opt5.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            print()
            print("3. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   💡 ปัญหา:")
            print("      - หุ้นที่มี Prob% ใกล้ 60% → RRR ต่ำ (0.77-1.07)")
            print("      - หุ้นที่มี RRR ใกล้ 2 → Prob% ต่ำ (49.2%)")
            print()
            print("   💡 ทางเลือก:")
            print("      Option 1: Prob >= 50%, RRR >= 1.5 → ได้ 2317 (Prob 49.2%, RRR 1.70)")
            print("      Option 4: Prob >= 55%, RRR >= 1.05 → ได้ 3 หุ้น (Prob 55-60%, RRR 1.05-1.07)")
            print("      Option 5: Combined → ได้ 4 หุ้น (รวม 2317 + 3 หุ้นที่มี Prob 55-60%)")
            print()
            print("   💡 แนะนำ: Option 5 (Combined)")
            print("      - Prob >= 50%, RRR >= 1.5 (เพื่อให้ได้ 2317 ที่มี RRR สูง)")
            print("      - หรือ Prob >= 55%, RRR >= 1.0 (เพื่อให้ได้หุ้นที่มี Prob ใกล้ 60%)")
            print("      - Count >= 15")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_taiwan_score()

