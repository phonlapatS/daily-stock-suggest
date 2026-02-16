#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบ Prob% ของจีน/ฮ่องกง
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

def check_china_prob():
    """ตรวจสอบ Prob% ของจีน/ฮ่องกง"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    china = df[(df['Country'] == 'CN') | (df['Country'] == 'HK')]
    
    if china.empty:
        print("❌ ไม่พบข้อมูลจีน/ฮ่องกง")
        return
    
    print("\n" + "=" * 120)
    print("CHINA/HK Prob% Statistics")
    print("=" * 120)
    
    print(f"\n📊 สถิติ Prob%:")
    print(f"  Min: {china['Prob%'].min():.1f}%")
    print(f"  Max: {china['Prob%'].max():.1f}%")
    print(f"  Mean (เฉลี่ย): {china['Prob%'].mean():.1f}%")
    print(f"  Median (ค่ากลาง): {china['Prob%'].median():.1f}%")
    
    print(f"\n📈 จำนวนหุ้นตาม Prob%:")
    print(f"  Prob >= 60%: {len(china[china['Prob%'] >= 60])} หุ้น")
    print(f"  Prob >= 65%: {len(china[china['Prob%'] >= 65])} หุ้น")
    print(f"  Prob >= 70%: {len(china[china['Prob%'] >= 70])} หุ้น")
    print(f"  Prob >= 75%: {len(china[china['Prob%'] >= 75])} หุ้น")
    
    print(f"\n✅ หุ้นที่ผ่านเกณฑ์ (Prob >= 60%, RRR >= 1.0, Count >= 20):")
    print("-" * 120)
    passed = china[
        (china['Prob%'] >= 60) & 
        (china['RR_Ratio'] >= 1.0) & 
        (china['Count'] >= 20)
    ].sort_values('Prob%', ascending=False)
    
    if not passed.empty:
        print(f"{'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
        print("-" * 120)
        for _, row in passed.iterrows():
            symbol = str(row['symbol'])
            prob = row['Prob%']
            rrr = row['RR_Ratio']
            count = int(row['Count'])
            avg_win = row['AvgWin%']
            avg_loss = row['AvgLoss%']
            print(f"{symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
        
        print("-" * 120)
        print(f"\n📊 สรุปหุ้นที่ผ่านเกณฑ์:")
        print(f"  จำนวน: {len(passed)} หุ้น")
        print(f"  Prob% เฉลี่ย: {passed['Prob%'].mean():.1f}%")
        print(f"  Prob% ต่ำสุด: {passed['Prob%'].min():.1f}%")
        print(f"  Prob% สูงสุด: {passed['Prob%'].max():.1f}%")
        
        # ตรวจสอบว่ามีหุ้นที่ Prob >= 70% หรือไม่
        prob_70_plus = passed[passed['Prob%'] >= 70]
        if not prob_70_plus.empty:
            print(f"\n🌟 หุ้นที่ Prob >= 70%: {len(prob_70_plus)} หุ้น")
            for _, row in prob_70_plus.iterrows():
                print(f"     - {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
        else:
            print(f"\n⚠️  ไม่มีหุ้นที่ Prob >= 70%")
    else:
        print("  ไม่มีหุ้นที่ผ่านเกณฑ์")
    
    print("\n" + "=" * 120)
    print("สรุป:")
    print(f"  - เกณฑ์ปัจจุบัน: Prob >= 60%, RRR >= 1.0, Count >= 20")
    print(f"  - Prob% เฉลี่ยของหุ้นที่ผ่านเกณฑ์: {passed['Prob%'].mean():.1f}%" if not passed.empty else "  - ไม่มีหุ้นที่ผ่านเกณฑ์")
    print("=" * 120)

if __name__ == "__main__":
    check_china_prob()

