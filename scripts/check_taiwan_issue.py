#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบว่าทำไมหุ้นไต้หวันหายไป
"""
import pandas as pd
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(BASE_DIR, "data", "symbol_performance.csv")

def check_taiwan_issue():
    """ตรวจสอบหุ้นไต้หวัน"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("ตรวจสอบหุ้นไต้หวัน")
    print("=" * 160)
    
    tw_all = df[df['Country'] == 'TW'].sort_values('Prob%', ascending=False)
    
    if tw_all.empty:
        print("❌ ไม่มีข้อมูลหุ้นไต้หวัน")
        return
    
    print(f"\nหุ้นไต้หวันทั้งหมด ({len(tw_all)} หุ้น):")
    print(f"{'Symbol':<12} {'Raw_Prob%':>12} {'Elite_Prob%':>14} {'Prob%':>8} {'RRR':>8} {'Raw_Count':>12} {'Elite_Count':>14} {'Count':>8} {'ผ่านเกณฑ์':<15}")
    print("-" * 160)
    
    # เกณฑ์: Prob >= 60%, RRR >= 1.3, Count 25-150
    for _, row in tw_all.iterrows():
        symbol = str(row['symbol'])
        raw_prob = row.get('Raw_Prob%', 0.0)
        elite_prob = row.get('Elite_Prob%', 0.0)
        prob = row.get('Prob%', 0.0)
        rrr = row.get('RR_Ratio', 0.0)
        raw_count = int(row.get('Raw_Count', 0))
        elite_count = int(row.get('Elite_Count', 0))
        count = int(row.get('Count', 0))
        
        # ตรวจสอบว่าผ่านเกณฑ์หรือไม่
        passes_prob = prob >= 60.0
        passes_rrr = rrr >= 1.3
        passes_count_min = count >= 25
        passes_count_max = count <= 150
        passes_all = passes_prob and passes_rrr and passes_count_min and passes_count_max
        
        status = "✅ ผ่าน" if passes_all else "❌ ไม่ผ่าน"
        if not passes_all:
            reasons = []
            if not passes_prob:
                reasons.append(f"Prob {prob:.1f}% < 60%")
            if not passes_rrr:
                reasons.append(f"RRR {rrr:.2f} < 1.3")
            if not passes_count_min:
                reasons.append(f"Count {count} < 25")
            if not passes_count_max:
                reasons.append(f"Count {count} > 150")
            status += f" ({', '.join(reasons)})"
        
        print(f"{symbol:<12} {raw_prob:>11.1f}% {elite_prob:>13.1f}% {prob:>7.1f}% {rrr:>7.2f} {raw_count:>12} {elite_count:>14} {count:>8} {status}")
    
    # ตรวจสอบหุ้นที่ควรผ่านเกณฑ์
    print("\n" + "=" * 160)
    print("หุ้นที่ควรผ่านเกณฑ์ (Prob >= 60%, RRR >= 1.3, Count 25-150):")
    print("-" * 160)
    
    should_pass = tw_all[
        (tw_all['Prob%'] >= 60.0) &
        (tw_all['RR_Ratio'] >= 1.3) &
        (tw_all['Count'] >= 25) &
        (tw_all['Count'] <= 150)
    ]
    
    if should_pass.empty:
        print("❌ ไม่มีหุ้นที่ผ่านเกณฑ์")
        
        # ตรวจสอบหุ้นที่ใกล้เกณฑ์
        print("\nหุ้นที่ใกล้เกณฑ์:")
        prob_60 = tw_all[tw_all['Prob%'] >= 60.0]
        rrr_13 = tw_all[tw_all['RR_Ratio'] >= 1.3]
        count_ok = tw_all[(tw_all['Count'] >= 25) & (tw_all['Count'] <= 150)]
        
        print(f"  Prob >= 60%: {len(prob_60)} หุ้น")
        if not prob_60.empty:
            for _, row in prob_60.iterrows():
                print(f"    - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
        
        print(f"  RRR >= 1.3: {len(rrr_13)} หุ้น")
        if not rrr_13.empty:
            for _, row in rrr_13.iterrows():
                print(f"    - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
        
        print(f"  Count 25-150: {len(count_ok)} หุ้น")
        if not count_ok.empty:
            for _, row in count_ok.iterrows():
                print(f"    - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
        
        # หาหุ้นที่ผ่าน 2 ใน 3 เกณฑ์
        print("\nหุ้นที่ผ่าน 2 ใน 3 เกณฑ์:")
        for _, row in tw_all.iterrows():
            prob_ok = row['Prob%'] >= 60.0
            rrr_ok = row['RR_Ratio'] >= 1.3
            count_ok = (row['Count'] >= 25) and (row['Count'] <= 150)
            
            passed = sum([prob_ok, rrr_ok, count_ok])
            if passed >= 2:
                print(f"  - {row['symbol']}: Prob {row['Prob%']:.1f}% ({'✅' if prob_ok else '❌'}), RRR {row['RR_Ratio']:.2f} ({'✅' if rrr_ok else '❌'}), Count {int(row['Count'])} ({'✅' if count_ok else '❌'})")
    else:
        print(f"✅ พบ {len(should_pass)} หุ้นที่ผ่านเกณฑ์:")
        print(f"{'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
        print("-" * 60)
        for _, row in should_pass.iterrows():
            print(f"{row['symbol']:<12} {row['Prob%']:>7.1f}% {row['RR_Ratio']:>7.2f} {int(row['Count']):>8}")
    
    print("\n" + "=" * 160)

if __name__ == "__main__":
    check_taiwan_issue()

