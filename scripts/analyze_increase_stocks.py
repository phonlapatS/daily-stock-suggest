#!/usr/bin/env python
"""
Analyze Increase Stocks - วิเคราะห์วิธีเพิ่มจำนวนหุ้นที่ผ่านเกณฑ์
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_increase_stocks():
    """วิเคราะห์วิธีเพิ่มจำนวนหุ้นที่ผ่านเกณฑ์"""
    
    print("="*80)
    print("Analyze Increase Stocks - วิเคราะห์วิธีเพิ่มจำนวนหุ้น")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            
            print("1. สถานการณ์ปัจจุบัน:")
            print("-" * 80)
            
            # Current criteria
            th = df[df['Country'] == 'TH']
            us = df[df['Country'] == 'US']
            cn = df[(df['Country'] == 'CN') | (df['Country'] == 'HK')]
            tw = df[df['Country'] == 'TW']
            
            th_curr = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)]
            us_curr = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)]
            cn_curr = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)]
            tw_curr = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 15)]
            
            total_curr = len(th_curr) + len(us_curr) + len(cn_curr) + len(tw_curr)
            
            print(f"   THAI: {len(th_curr)} หุ้น (Prob >= 60%, RRR >= 1.3, Count >= 30)")
            print(f"   US: {len(us_curr)} หุ้น (Prob >= 60%, RRR >= 1.5, Count >= 15)")
            print(f"   CHINA/HK: {len(cn_curr)} หุ้น (Prob >= 60%, RRR >= 1.2, Count >= 15)")
            print(f"   TAIWAN: {len(tw_curr)} หุ้น (Prob >= 60%, RRR >= 0.75, Count >= 15)")
            print(f"   📊 TOTAL: {total_curr} หุ้น")
            print()
            
            print("2. วิเคราะห์หุ้นที่ใกล้เคียงเกณฑ์ (ขาด 1 เงื่อนไข):")
            print("-" * 80)
            
            # THAI: Prob >= 58%, RRR >= 1.2, Count >= 25 (ใกล้เคียง)
            th_near = th[
                ((th['Prob%'] >= 58.0) & (th['Prob%'] < 60.0) & (th['RR_Ratio'] >= 1.2) & (th['Count'] >= 25)) |
                ((th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.2) & (th['RR_Ratio'] < 1.3) & (th['Count'] >= 25)) |
                ((th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 25) & (th['Count'] < 30))
            ]
            print(f"   THAI (ใกล้เคียง): {len(th_near)} หุ้น")
            if len(th_near) > 0:
                print(f"      Top 5:")
                for idx, row in th_near.head(5).iterrows():
                    print(f"         {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # US: Prob >= 58%, RRR >= 1.3, Count >= 10 (ใกล้เคียง)
            us_near = us[
                ((us['Prob%'] >= 58.0) & (us['Prob%'] < 60.0) & (us['RR_Ratio'] >= 1.3) & (us['Count'] >= 10)) |
                ((us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.3) & (us['RR_Ratio'] < 1.5) & (us['Count'] >= 10)) |
                ((us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 10) & (us['Count'] < 15))
            ]
            print(f"   US (ใกล้เคียง): {len(us_near)} หุ้น")
            if len(us_near) > 0:
                print(f"      Top 5:")
                for idx, row in us_near.head(5).iterrows():
                    print(f"         {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # CHINA: Prob >= 58%, RRR >= 1.1, Count >= 10 (ใกล้เคียง)
            cn_near = cn[
                ((cn['Prob%'] >= 58.0) & (cn['Prob%'] < 60.0) & (cn['RR_Ratio'] >= 1.1) & (cn['Count'] >= 10)) |
                ((cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.1) & (cn['RR_Ratio'] < 1.2) & (cn['Count'] >= 10)) |
                ((cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 10) & (cn['Count'] < 15))
            ]
            print(f"   CHINA/HK (ใกล้เคียง): {len(cn_near)} หุ้น")
            if len(cn_near) > 0:
                print(f"      Top 5:")
                for idx, row in cn_near.head(5).iterrows():
                    print(f"         {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            # TAIWAN: Prob >= 58%, RRR >= 0.7, Count >= 10 (ใกล้เคียง)
            tw_near = tw[
                ((tw['Prob%'] >= 58.0) & (tw['Prob%'] < 60.0) & (tw['RR_Ratio'] >= 0.7) & (tw['Count'] >= 10)) |
                ((tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.7) & (tw['RR_Ratio'] < 0.75) & (tw['Count'] >= 10)) |
                ((tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 10) & (tw['Count'] < 15))
            ]
            print(f"   TAIWAN (ใกล้เคียง): {len(tw_near)} หุ้น")
            if len(tw_near) > 0:
                print(f"      Top 5:")
                for idx, row in tw_near.head(5).iterrows():
                    print(f"         {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {row['Count']}")
            
            print()
            print("3. เปรียบเทียบ Options:")
            print("-" * 80)
            
            # Option A: ลด Prob% 2% (58%), RRR คงเดิม, Count คงเดิม
            th_optA = th[(th['Prob%'] >= 58.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)]
            us_optA = us[(us['Prob%'] >= 58.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)]
            cn_optA = cn[(cn['Prob%'] >= 58.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)]
            tw_optA = tw[(tw['Prob%'] >= 58.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 15)]
            total_optA = len(th_optA) + len(us_optA) + len(cn_optA) + len(tw_optA)
            
            print(f"   Option A: Prob >= 58% (ลด 2%), RRR/Count คงเดิม")
            print(f"      THAI: {len(th_optA)} (+{len(th_optA) - len(th_curr)})")
            print(f"      US: {len(us_optA)} (+{len(us_optA) - len(us_curr)})")
            print(f"      CHINA/HK: {len(cn_optA)} (+{len(cn_optA) - len(cn_curr)})")
            print(f"      TAIWAN: {len(tw_optA)} (+{len(tw_optA) - len(tw_curr)})")
            print(f"      TOTAL: {total_optA} (+{total_optA - total_curr})")
            print()
            
            # Option B: ลด RRR 0.1-0.2, Prob/Count คงเดิม
            th_optB = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.2) & (th['Count'] >= 30)]
            us_optB = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.3) & (us['Count'] >= 15)]
            cn_optB = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.1) & (cn['Count'] >= 15)]
            tw_optB = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.65) & (tw['Count'] >= 15)]
            total_optB = len(th_optB) + len(us_optB) + len(cn_optB) + len(tw_optB)
            
            print(f"   Option B: RRR ลด 0.1-0.2, Prob/Count คงเดิม")
            print(f"      THAI: {len(th_optB)} (+{len(th_optB) - len(th_curr)})")
            print(f"      US: {len(us_optB)} (+{len(us_optB) - len(us_curr)})")
            print(f"      CHINA/HK: {len(cn_optB)} (+{len(cn_optB) - len(cn_curr)})")
            print(f"      TAIWAN: {len(tw_optB)} (+{len(tw_optB) - len(tw_curr)})")
            print(f"      TOTAL: {total_optB} (+{total_optB - total_curr})")
            print()
            
            # Option C: ลด Count, Prob/RRR คงเดิม
            th_optC = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 25)]
            us_optC = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 10)]
            cn_optC = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 10)]
            tw_optC = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 0.75) & (tw['Count'] >= 10)]
            total_optC = len(th_optC) + len(us_optC) + len(cn_optC) + len(tw_optC)
            
            print(f"   Option C: Count ลด, Prob/RRR คงเดิม")
            print(f"      THAI: {len(th_optC)} (+{len(th_optC) - len(th_curr)})")
            print(f"      US: {len(us_optC)} (+{len(us_optC) - len(us_curr)})")
            print(f"      CHINA/HK: {len(cn_optC)} (+{len(cn_optC) - len(cn_curr)})")
            print(f"      TAIWAN: {len(tw_optC)} (+{len(tw_optC) - len(tw_curr)})")
            print(f"      TOTAL: {total_optC} (+{total_optC - total_curr})")
            print()
            
            # Option D: Combined (Prob 58%, RRR ลด, Count ลด)
            th_optD = th[(th['Prob%'] >= 58.0) & (th['RR_Ratio'] >= 1.2) & (th['Count'] >= 25)]
            us_optD = us[(us['Prob%'] >= 58.0) & (us['RR_Ratio'] >= 1.3) & (us['Count'] >= 10)]
            cn_optD = cn[(cn['Prob%'] >= 58.0) & (cn['RR_Ratio'] >= 1.1) & (cn['Count'] >= 10)]
            tw_optD = tw[(tw['Prob%'] >= 58.0) & (tw['RR_Ratio'] >= 0.65) & (tw['Count'] >= 10)]
            total_optD = len(th_optD) + len(us_optD) + len(cn_optD) + len(tw_optD)
            
            print(f"   Option D: Combined (Prob 58%, RRR ลด, Count ลด)")
            print(f"      THAI: {len(th_optD)} (+{len(th_optD) - len(th_curr)})")
            print(f"      US: {len(us_optD)} (+{len(us_optD) - len(us_curr)})")
            print(f"      CHINA/HK: {len(cn_optD)} (+{len(cn_optD) - len(cn_curr)})")
            print(f"      TAIWAN: {len(tw_optD)} (+{len(tw_optD) - len(tw_curr)})")
            print(f"      TOTAL: {total_optD} (+{total_optD - total_curr})")
            print()
            
            print("4. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   💡 สรุป Options:")
            print(f"      Option A: {total_optA} หุ้น (+{total_optA - total_curr}) - ลด Prob% 2%")
            print(f"      Option B: {total_optB} หุ้น (+{total_optB - total_curr}) - ลด RRR 0.1-0.2")
            print(f"      Option C: {total_optC} หุ้น (+{total_optC - total_curr}) - ลด Count")
            print(f"      Option D: {total_optD} หุ้น (+{total_optD - total_curr}) - Combined")
            print()
            print("   💡 แนะนำ: Option D (Combined) เพื่อเพิ่มหุ้นให้มากที่สุด")
            print("      - Prob >= 58% (ลด 2% จาก 60%)")
            print("      - RRR ลด 0.1-0.2 (THAI 1.2, US 1.3, CHINA 1.1, TAIWAN 0.65)")
            print("      - Count ลด (THAI 25, US/CHINA/TAIWAN 10)")
            print()
            print("   ⚠️  ข้อควรระวัง:")
            print("      - Prob% ต่ำลง → คุณภาพลดลง")
            print("      - RRR ต่ำลง → ความคุ้มค่าเสี่ยงลดลง")
            print("      - Count ต่ำลง → น่าเชื่อถือลดลง")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_increase_stocks()

