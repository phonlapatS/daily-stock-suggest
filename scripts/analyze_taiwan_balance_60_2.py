#!/usr/bin/env python
"""
Analyze Taiwan Balance - วิเคราะห์หุ้นไต้หวันเพื่อหา balance ระหว่าง Prob% ใกล้ 60% และ RRR ใกล้ 2
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
    """วิเคราะห์หุ้นไต้หวันเพื่อหา balance ระหว่าง Prob% ใกล้ 60% และ RRR ใกล้ 2"""
    
    print("="*80)
    print("Analyze Taiwan Balance - Prob% ใกล้ 60%, RRR ใกล้ 2")
    print("="*80)
    print()
    
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW'].copy()
            
            print("1. หุ้นที่มี Prob% ใกล้ 60% (55-65%) และ RRR ใกล้ 2 (1.5-2.5):")
            print("-" * 80)
            
            # หาหุ้นที่มี Prob% 55-65% และ RRR 1.5-2.5
            target = tw[
                (tw['Prob%'] >= 55.0) & (tw['Prob%'] <= 65.0) &
                (tw['RR_Ratio'] >= 1.5) & (tw['RR_Ratio'] <= 2.5) &
                (tw['Count'] >= 15)
            ].sort_values(by='RR_Ratio', ascending=False)
            
            print(f"Total: {len(target)} หุ้น")
            print()
            
            if len(target) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
                print("-" * 50)
                for idx, row in target.iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    score = prob * rrr / 100  # Score = Prob% * RRR
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            else:
                print("❌ ไม่มีหุ้นที่ผ่าน criteria นี้")
            
            print()
            print("2. หุ้นที่มี Prob% ใกล้ 60% (55-65%):")
            print("-" * 80)
            
            prob_target = tw[
                (tw['Prob%'] >= 55.0) & (tw['Prob%'] <= 65.0) &
                (tw['Count'] >= 15)
            ].sort_values(by='RR_Ratio', ascending=False)
            
            print(f"Total: {len(prob_target)} หุ้น")
            print()
            
            if len(prob_target) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
                print("-" * 50)
                for idx, row in prob_target.head(10).iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    score = prob * rrr / 100
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("3. หุ้นที่มี RRR ใกล้ 2 (1.5-2.5):")
            print("-" * 80)
            
            rrr_target = tw[
                (tw['RR_Ratio'] >= 1.5) & (tw['RR_Ratio'] <= 2.5) &
                (tw['Count'] >= 15)
            ].sort_values(by='Prob%', ascending=False)
            
            print(f"Total: {len(rrr_target)} หุ้น")
            print()
            
            if len(rrr_target) > 0:
                print(f"{'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Score':>8}")
                print("-" * 50)
                for idx, row in rrr_target.head(10).iterrows():
                    symbol = row.get('symbol', 'N/A')
                    prob = row.get('Prob%', 0)
                    rrr = row.get('RR_Ratio', 0)
                    count = row.get('Count', 0)
                    score = prob * rrr / 100
                    print(f"{symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {score:>7.2f}")
            
            print()
            print("4. วิเคราะห์ Criteria ต่างๆ:")
            print("-" * 80)
            
            # Option 1: Prob >= 55%, RRR >= 1.5
            opt1 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option 1: Prob >= 55%, RRR >= 1.5, Count >= 15: {len(opt1)} หุ้น")
            
            # Option 2: Prob >= 58%, RRR >= 1.8
            opt2 = tw[(tw['Prob%'] >= 58.0) & (tw['RR_Ratio'] >= 1.8) & (tw['Count'] >= 15)]
            print(f"   Option 2: Prob >= 58%, RRR >= 1.8, Count >= 15: {len(opt2)} หุ้น")
            
            # Option 3: Prob >= 60%, RRR >= 1.5
            opt3 = tw[(tw['Prob%'] >= 60.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
            print(f"   Option 3: Prob >= 60%, RRR >= 1.5, Count >= 15: {len(opt3)} หุ้น")
            
            # Option 4: Prob >= 55%, RRR >= 1.8
            opt4 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.8) & (tw['Count'] >= 15)]
            print(f"   Option 4: Prob >= 55%, RRR >= 1.8, Count >= 15: {len(opt4)} หุ้น")
            
            # Option 5: Score >= 1.0 (Prob% * RRR / 100)
            opt5 = tw[(tw['Prob%'] * tw['RR_Ratio'] / 100 >= 1.0) & (tw['Count'] >= 15)]
            print(f"   Option 5: Score >= 1.0 (Prob% * RRR / 100), Count >= 15: {len(opt5)} หุ้น")
            
            print()
            print("5. ข้อเสนอแนะ:")
            print("-" * 80)
            
            if len(target) > 0:
                print("   ✅ มีหุ้นที่ผ่าน Prob% 55-65% และ RRR 1.5-2.5 แล้ว")
                print(f"      จำนวน: {len(target)} หุ้น")
                print()
                print("   💡 แนะนำ Criteria:")
                print("      - Prob >= 55%, RRR >= 1.5, Count >= 15")
                print("      หรือ")
                print("      - Score >= 1.0 (Prob% * RRR / 100), Count >= 15")
            else:
                print("   ⚠️  ไม่มีหุ้นที่ผ่าน Prob% 55-65% และ RRR 1.5-2.5")
                print()
                print("   💡 ทางเลือก:")
                if len(opt1) > 0:
                    print(f"      Option 1: Prob >= 55%, RRR >= 1.5 → {len(opt1)} หุ้น")
                if len(opt4) > 0:
                    print(f"      Option 4: Prob >= 55%, RRR >= 1.8 → {len(opt4)} หุ้น")
                if len(opt5) > 0:
                    print(f"      Option 5: Score >= 1.0 → {len(opt5)} หุ้น")
            
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

