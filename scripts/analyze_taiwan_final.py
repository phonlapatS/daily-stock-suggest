#!/usr/bin/env python
"""
Analyze Taiwan Final - วิเคราะห์หุ้นไต้หวันเพื่อหา balance สุดท้าย
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_taiwan_final():
    """วิเคราะห์หุ้นไต้หวันเพื่อหา balance สุดท้าย"""
    
    print("="*80)
    print("Analyze Taiwan Final - Balance Prob% ใกล้ 60%, RRR ใกล้ 2")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW'].copy()
            tw['Score'] = tw['Prob%'] * tw['RR_Ratio'] / 100
            
            print("1. วิเคราะห์ Criteria ต่างๆ:")
            print("-" * 80)
            
            # Option A: Prob >= 49%, RRR >= 1.5 (เพื่อให้ได้ 2317)
            optA = tw[(tw['Prob%'] >= 49.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option A: Prob >= 49%, RRR >= 1.5, Count >= 15: {len(optA)} หุ้น")
            if len(optA) > 0:
                for idx, row in optA.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option B: Prob >= 55%, RRR >= 1.0 (เพื่อให้ได้หุ้นที่มี Prob ใกล้ 60%)
            optB = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0) & (tw['Count'] >= 15)]
            print(f"   Option B: Prob >= 55%, RRR >= 1.0, Count >= 15: {len(optB)} หุ้น")
            if len(optB) > 0:
                for idx, row in optB.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option C: Combined (Prob >= 49%, RRR >= 1.5) OR (Prob >= 55%, RRR >= 1.0)
            optC = tw[
                ((tw['Prob%'] >= 49.0) & (tw['RR_Ratio'] >= 1.5)) |
                ((tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0))
            ]
            optC = optC[optC['Count'] >= 15].sort_values(by='Score', ascending=False)
            print(f"   Option C: (Prob >= 49%, RRR >= 1.5) OR (Prob >= 55%, RRR >= 1.0), Count >= 15: {len(optC)} หุ้น")
            if len(optC) > 0:
                for idx, row in optC.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option D: Score >= 0.6 (Prob% * RRR / 100)
            optD = tw[(tw['Score'] >= 0.6) & (tw['Count'] >= 15)].sort_values(by='Score', ascending=False)
            print(f"   Option D: Score >= 0.6, Count >= 15: {len(optD)} หุ้น")
            if len(optD) > 0:
                for idx, row in optD.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option E: Prob >= 55%, RRR >= 1.05 (เพื่อให้ได้หุ้นที่มี Prob ใกล้ 60% และ RRR ใกล้ 1.0)
            optE = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.05) & (tw['Count'] >= 15)].sort_values(by='Prob%', ascending=False)
            print(f"   Option E: Prob >= 55%, RRR >= 1.05, Count >= 15: {len(optE)} หุ้น")
            if len(optE) > 0:
                for idx, row in optE.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            print()
            print("2. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   💡 เป้าหมาย: Prob% ใกล้ 60%, RRR ใกล้ 2")
            print()
            print("   💡 สถานการณ์:")
            print("      - หุ้นที่มี Prob% ใกล้ 60% → RRR ต่ำ (0.77-1.07)")
            print("      - หุ้นที่มี RRR ใกล้ 2 → Prob% ต่ำ (49.2%)")
            print()
            print("   💡 ทางเลือก:")
            print()
            print("   Option C (Combined) - แนะนำ:")
            print("      - Prob >= 49%, RRR >= 1.5 (เพื่อให้ได้ 2317 ที่มี RRR 1.70)")
            print("      - หรือ Prob >= 55%, RRR >= 1.0 (เพื่อให้ได้หุ้นที่มี Prob 55-60%)")
            print(f"      - ได้ {len(optC)} หุ้น")
            print()
            print("   Option D (Score-based):")
            print("      - Score >= 0.6 (Prob% * RRR / 100)")
            print(f"      - ได้ {len(optD)} หุ้น (2317: Score 0.84)")
            print()
            print("   Option E (Prob ใกล้ 60%):")
            print("      - Prob >= 55%, RRR >= 1.05")
            print(f"      - ได้ {len(optE)} หุ้น (Prob 55-60%, RRR 1.05-1.07)")
            print()
            print("   💡 สรุป:")
            print("      - Option C: ได้ 4 หุ้น (รวม 2317 + 3 หุ้นที่มี Prob 55-60%)")
            print("      - Option D: ได้ 1 หุ้น (2317 เท่านั้น)")
            print("      - Option E: ได้ 2 หุ้น (Prob 55-60%, RRR 1.05-1.07)")
            print()
            print("   💡 แนะนำ: Option C (Combined)")
            print("      - ครอบคลุมทั้งหุ้นที่มี RRR สูง (2317) และหุ้นที่มี Prob ใกล้ 60%")
            print("      - ได้ 4 หุ้น: 2317, 2330, 2303, 2382")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_taiwan_final()

