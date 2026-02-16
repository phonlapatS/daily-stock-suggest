#!/usr/bin/env python
"""
Analyze Passing Stocks - วิเคราะห์หุ้นที่ผ่านเกณฑ์และหาทางเพิ่มจำนวน
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_passing_stocks():
    """วิเคราะห์หุ้นที่ผ่านเกณฑ์และหาทางเพิ่มจำนวน"""
    
    print("="*80)
    print("Analyze Passing Stocks - วิเคราะห์หุ้นที่ผ่านเกณฑ์")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            
            print("1. สรุปหุ้นที่ผ่านเกณฑ์ปัจจุบัน:")
            print("-" * 80)
            
            # THAI: Prob >= 60%, RRR >= 1.3, Count >= 30
            th = df[df['Country'] == 'TH']
            th_passed = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)]
            print(f"   THAI: Prob >= 60%, RRR >= 1.3, Count >= 30: {len(th_passed)} หุ้น")
            
            # US: Prob >= 60%, RRR >= 1.5, Count >= 15
            us = df[df['Country'] == 'US']
            us_passed = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)]
            print(f"   US: Prob >= 60%, RRR >= 1.5, Count >= 15: {len(us_passed)} หุ้น")
            
            # CHINA: Prob >= 60%, RRR >= 1.2, Count >= 15
            cn = df[(df['Country'] == 'CN') | (df['Country'] == 'HK')]
            cn_passed = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)]
            print(f"   CHINA/HK: Prob >= 60%, RRR >= 1.2, Count >= 15: {len(cn_passed)} หุ้น")
            
            # TAIWAN: Prob >= 60%, RRR >= 0.75, Count >= 15
            tw = df[df['Country'] == 'TW']
            tw_passed = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 15)]
            print(f"   TAIWAN: Prob >= 60%, RRR >= 0.75, Count >= 15: {len(tw_passed)} หุ้น")
            
            total_passed = len(th_passed) + len(us_passed) + len(cn_passed) + len(tw_passed)
            print()
            print(f"   📊 TOTAL: {total_passed} หุ้น")
            
            print()
            print("2. วิเคราะห์หุ้นที่ใกล้เคียงเกณฑ์ (ไม่ผ่านเพราะขาด 1 เงื่อนไข):")
            print("-" * 80)
            
            # THAI: ใกล้เคียง
            th_near = th[
                ((th['Prob%'] >= 58.0) & (th['Prob%'] < 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)) |
                ((th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.2) & (th['RR_Ratio'] < 1.3) & (th['Count'] >= 30)) |
                ((th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 25) & (th['Count'] < 30))
            ]
            print(f"   THAI (ใกล้เคียง): {len(th_near)} หุ้น")
            if len(th_near) > 0:
                for idx, row in th_near.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # US: ใกล้เคียง
            us_near = us[
                ((us['Prob%'] >= 58.0) & (us['Prob%'] < 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)) |
                ((us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.3) & (us['RR_Ratio'] < 1.5) & (us['Count'] >= 15)) |
                ((us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 10) & (us['Count'] < 15))
            ]
            print(f"   US (ใกล้เคียง): {len(us_near)} หุ้น")
            if len(us_near) > 0:
                for idx, row in us_near.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # CHINA: ใกล้เคียง
            cn_near = cn[
                ((cn['Prob%'] >= 58.0) & (cn['Prob%'] < 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)) |
                ((cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.0) & (cn['RR_Ratio'] < 1.2) & (cn['Count'] >= 15)) |
                ((cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 10) & (cn['Count'] < 15))
            ]
            print(f"   CHINA/HK (ใกล้เคียง): {len(cn_near)} หุ้น")
            if len(cn_near) > 0:
                for idx, row in cn_near.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # TAIWAN: ใกล้เคียง
            tw_near = tw[
                ((tw['Prob%'] >= 58.0) & (tw['Prob%'] < 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 15)) |
                ((tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.6) & (tw['RR_Ratio'] < 0.75) & (tw['Count'] >= 15)) |
                ((tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 10) & (tw['Count'] < 15))
            ]
            print(f"   TAIWAN (ใกล้เคียง): {len(tw_near)} หุ้น")
            if len(tw_near) > 0:
                for idx, row in tw_near.head(5).iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            print()
            print("3. วิเคราะห์การปรับ Criteria เพื่อเพิ่มจำนวนหุ้น:")
            print("-" * 80)
            
            # Option 1: ลด Prob% ทุกตลาด 2%
            print("   Option 1: ลด Prob% ทุกตลาด 2%")
            th_opt1 = th[(th['Prob%'] >= 58.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)]
            us_opt1 = us[(us['Prob%'] >= 58.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)]
            cn_opt1 = cn[(cn['Prob%'] >= 58.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)]
            tw_opt1 = tw[(tw['Prob%'] >= 58.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 15)]
            total_opt1 = len(th_opt1) + len(us_opt1) + len(cn_opt1) + len(tw_opt1)
            print(f"      THAI: {len(th_opt1)} (+{len(th_opt1) - len(th_passed)})")
            print(f"      US: {len(us_opt1)} (+{len(us_opt1) - len(us_passed)})")
            print(f"      CHINA/HK: {len(cn_opt1)} (+{len(cn_opt1) - len(cn_passed)})")
            print(f"      TAIWAN: {len(tw_opt1)} (+{len(tw_opt1) - len(tw_passed)})")
            print(f"      TOTAL: {total_opt1} (+{total_opt1 - total_passed})")
            print()
            
            # Option 2: ลด RRR ทุกตลาด 0.1-0.2
            print("   Option 2: ลด RRR ทุกตลาด 0.1-0.2")
            th_opt2 = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.2) & (th['Count'] >= 30)]
            us_opt2 = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.3) & (us['Count'] >= 15)]
            cn_opt2 = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.1) & (cn['Count'] >= 15)]
            tw_opt2 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.65) & (tw['Count'] >= 15)]
            total_opt2 = len(th_opt2) + len(us_opt2) + len(cn_opt2) + len(tw_opt2)
            print(f"      THAI: {len(th_opt2)} (+{len(th_opt2) - len(th_passed)})")
            print(f"      US: {len(us_opt2)} (+{len(us_opt2) - len(us_passed)})")
            print(f"      CHINA/HK: {len(cn_opt2)} (+{len(cn_opt2) - len(cn_passed)})")
            print(f"      TAIWAN: {len(tw_opt2)} (+{len(tw_opt2) - len(tw_passed)})")
            print(f"      TOTAL: {total_opt2} (+{total_opt2 - total_passed})")
            print()
            
            # Option 3: ลด Count requirement
            print("   Option 3: ลด Count requirement")
            th_opt3 = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 25)]
            us_opt3 = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 10)]
            cn_opt3 = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 10)]
            tw_opt3 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 10)]
            total_opt3 = len(th_opt3) + len(us_opt3) + len(cn_opt3) + len(tw_opt3)
            print(f"      THAI: {len(th_opt3)} (+{len(th_opt3) - len(th_passed)})")
            print(f"      US: {len(us_opt3)} (+{len(us_opt3) - len(us_passed)})")
            print(f"      CHINA/HK: {len(cn_opt3)} (+{len(cn_opt3) - len(cn_passed)})")
            print(f"      TAIWAN: {len(tw_opt3)} (+{len(tw_opt3) - len(tw_passed)})")
            print(f"      TOTAL: {total_opt3} (+{total_opt3 - total_passed})")
            print()
            
            # Option 4: Combined (ลด Prob 2%, ลด RRR 0.1, ลด Count)
            print("   Option 4: Combined (ลด Prob 2%, ลด RRR 0.1, ลด Count)")
            th_opt4 = th[(th['Prob%'] >= 58.0) & (th['RR_Ratio'] >= 1.2) & (th['Count'] >= 25)]
            us_opt4 = us[(us['Prob%'] >= 58.0) & (us['RR_Ratio'] >= 1.3) & (us['Count'] >= 10)]
            cn_opt4 = cn[(cn['Prob%'] >= 58.0) & (cn['RR_Ratio'] >= 1.1) & (cn['Count'] >= 10)]
            tw_opt4 = tw[(tw['Prob%'] >= 58.0) & (tw['RR_Ratio'] >= 0.65) & (tw['Count'] >= 10)]
            total_opt4 = len(th_opt4) + len(us_opt4) + len(cn_opt4) + len(tw_opt4)
            print(f"      THAI: {len(th_opt4)} (+{len(th_opt4) - len(th_passed)})")
            print(f"      US: {len(us_opt4)} (+{len(us_opt4) - len(us_passed)})")
            print(f"      CHINA/HK: {len(cn_opt4)} (+{len(cn_opt4) - len(cn_passed)})")
            print(f"      TAIWAN: {len(tw_opt4)} (+{len(tw_opt4) - len(tw_passed)})")
            print(f"      TOTAL: {total_opt4} (+{total_opt4 - total_passed})")
            print()
            
            print("4. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   💡 ทางเลือกที่เหมาะสม:")
            print()
            print("   Option 1: ลด Prob% 2% → เพิ่มหุ้นได้มาก แต่ Prob% ต่ำลง")
            print("   Option 2: ลด RRR 0.1-0.2 → เพิ่มหุ้นได้ปานกลาง แต่ RRR ต่ำลง")
            print("   Option 3: ลด Count → เพิ่มหุ้นได้มาก แต่ Count ต่ำลง (น่าเชื่อถือน้อยลง)")
            print("   Option 4: Combined → เพิ่มหุ้นได้มากที่สุด แต่ทุก criteria ต่ำลง")
            print()
            print("   💡 แนะนำ: Option 4 (Combined) เพื่อเพิ่มหุ้นให้มากที่สุด")
            print("      แต่ต้อง balance ระหว่าง Prob%, RRR, และ Count")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_passing_stocks()

