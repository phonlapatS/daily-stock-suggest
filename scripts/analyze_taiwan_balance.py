#!/usr/bin/env python
"""
Analyze Taiwan Balance - วิเคราะห์ balance ระหว่าง Prob และ RRR สำหรับ Taiwan market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_taiwan_balance():
    """วิเคราะห์ balance ระหว่าง Prob และ RRR สำหรับ Taiwan market"""
    
    print("="*80)
    print("Analyze Taiwan Balance - วิเคราะห์ balance ระหว่าง Prob และ RRR")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            
            print("1. Taiwan symbols (sorted by Prob%):")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
            print("-" * 80)
            
            # คำนวณ Score = Prob% * RRR (balance metric)
            tw['Score'] = tw['Prob%'] * tw['RR_Ratio']
            
            for idx, row in tw.nlargest(10, 'Prob%').iterrows():
                symbol = row.get('symbol', 'N/A')
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                count = row.get('Count', 0)
                score = row.get('Score', 0)
                print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("2. Taiwan symbols (sorted by RRR):")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
            print("-" * 80)
            
            for idx, row in tw.nlargest(10, 'RR_Ratio').iterrows():
                symbol = row.get('symbol', 'N/A')
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                count = row.get('Count', 0)
                score = row.get('Score', 0)
                print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("3. Taiwan symbols (sorted by Score = Prob% * RRR):")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
            print("-" * 80)
            
            for idx, row in tw.nlargest(10, 'Score').iterrows():
                symbol = row.get('symbol', 'N/A')
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                count = row.get('Count', 0)
                score = row.get('Score', 0)
                print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("4. เปรียบเทียบ Criteria ต่างๆ:")
            print("-" * 80)
            
            # Option 1: Prob >= 55%, RRR >= 1.0 (เดิม)
            opt1 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0) & (tw['Count'] >= 15)]
            print(f"   Option 1: Prob >= 55%, RRR >= 1.0, Count >= 15: {len(opt1)} หุ้น")
            if len(opt1) > 0:
                for idx, row in opt1.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 2: Prob >= 50%, RRR >= 1.1 (ปัจจุบัน)
            opt2 = tw[(tw['Prob%'] >= 50.0) & (tw['RR_Ratio'] >= 1.1) & (tw['Count'] >= 15)]
            print(f"   Option 2: Prob >= 50%, RRR >= 1.1, Count >= 15: {len(opt2)} หุ้น")
            if len(opt2) > 0:
                for idx, row in opt2.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 3: Prob >= 49%, RRR >= 1.1 (ปัจจุบัน)
            opt3 = tw[(tw['Prob%'] >= 49.0) & (tw['RR_Ratio'] >= 1.1) & (tw['Count'] >= 15)]
            print(f"   Option 3: Prob >= 49%, RRR >= 1.1, Count >= 15: {len(opt3)} หุ้น")
            if len(opt3) > 0:
                for idx, row in opt3.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 4: Score >= 60 (balance)
            opt4 = tw[(tw['Score'] >= 60.0) & (tw['Count'] >= 15)]
            print(f"   Option 4: Score >= 60 (Prob% * RRR), Count >= 15: {len(opt4)} หุ้น")
            if len(opt4) > 0:
                for idx, row in opt4.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            # Option 5: Prob >= 52%, RRR >= 1.05 (balance)
            opt5 = tw[(tw['Prob%'] >= 52.0) & (tw['RR_Ratio'] >= 1.05) & (tw['Count'] >= 15)]
            print(f"   Option 5: Prob >= 52%, RRR >= 1.05, Count >= 15: {len(opt5)} หุ้น")
            if len(opt5) > 0:
                for idx, row in opt5.iterrows():
                    print(f"      - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Score {row['Score']:.2f}")
            
            print()
            print("5. เปรียบเทียบกับตลาดอื่น:")
            print("-" * 80)
            
            # THAI
            th = df[df['Country'] == 'TH']
            th_passed = th[(th['Prob%'] >= 60.0) & (th['RR_Ratio'] >= 1.3) & (th['Count'] >= 30)]
            print(f"   THAI: Prob >= 60%, RRR >= 1.3, Count >= 30: {len(th_passed)} หุ้น")
            if len(th_passed) > 0:
                avg_prob = th_passed['Prob%'].mean()
                avg_rrr = th_passed['RR_Ratio'].mean()
                print(f"      Avg Prob: {avg_prob:.1f}%, Avg RRR: {avg_rrr:.2f}")
            
            # US
            us = df[df['Country'] == 'US']
            us_passed = us[(us['Prob%'] >= 60.0) & (us['RR_Ratio'] >= 1.5) & (us['Count'] >= 15)]
            print(f"   US: Prob >= 60%, RRR >= 1.5, Count >= 15: {len(us_passed)} หุ้น")
            if len(us_passed) > 0:
                avg_prob = us_passed['Prob%'].mean()
                avg_rrr = us_passed['RR_Ratio'].mean()
                print(f"      Avg Prob: {avg_prob:.1f}%, Avg RRR: {avg_rrr:.2f}")
            
            # CHINA
            cn = df[(df['Country'] == 'CN') | (df['Country'] == 'HK')]
            cn_passed = cn[(cn['Prob%'] >= 60.0) & (cn['RR_Ratio'] >= 1.2) & (cn['Count'] >= 15)]
            print(f"   CHINA: Prob >= 60%, RRR >= 1.2, Count >= 15: {len(cn_passed)} หุ้น")
            if len(cn_passed) > 0:
                avg_prob = cn_passed['Prob%'].mean()
                avg_rrr = cn_passed['RR_Ratio'].mean()
                print(f"      Avg Prob: {avg_prob:.1f}%, Avg RRR: {avg_rrr:.2f}")
            
            print()
            print("6. ข้อเสนอแนะ:")
            print("-" * 80)
            print("   💡 Taiwan market มีปัญหา:")
            print("      - หุ้นที่มี Prob สูง → RRR ต่ำ (3008: Prob 64.7%, RRR 0.77)")
            print("      - หุ้นที่มี RRR สูง → Prob ต่ำ (2317: Prob 49.2%, RRR 1.70)")
            print()
            print("   💡 ทางเลือก:")
            print("      1. ใช้ Score = Prob% * RRR เพื่อ balance (Option 4)")
            print("      2. ใช้ Prob >= 52%, RRR >= 1.05 เพื่อ balance (Option 5)")
            print("      3. ตรวจสอบว่า Taiwan ใช้ Mean Reversion หรือ Trend Following")
            print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ℹ️  ไม่พบ: {perf_file}")
    
    print("="*80)

if __name__ == '__main__':
    analyze_taiwan_balance()

