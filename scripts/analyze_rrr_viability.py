#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
วิเคราะห์ RRR ว่าคุ้มค่าเสี่ยงหรือไม่ (Expected Value)
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

def calculate_expected_value(prob, rrr):
    """
    คำนวณ Expected Value
    EV = (Prob * RRR) - ((1 - Prob) * 1.0)
    """
    win_rate = prob / 100.0
    loss_rate = 1.0 - win_rate
    ev = (win_rate * rrr) - (loss_rate * 1.0)
    return ev

def analyze_rrr_viability():
    """วิเคราะห์ RRR ว่าคุ้มค่าเสี่ยงหรือไม่"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("วิเคราะห์ RRR ว่าคุ้มค่าเสี่ยงหรือไม่ (Expected Value Analysis)")
    print("=" * 160)
    
    # วิเคราะห์หุ้นที่มี Prob >= 60% และ RRR ต่างๆ
    print("\n📊 ตัวอย่าง Expected Value ตาม RRR:")
    print("-" * 160)
    print(f"{'Prob%':>8} {'RRR':>8} {'Expected Value':>18} {'ความหมาย':<50}")
    print("-" * 160)
    
    test_cases = [
        (60, 1.25, "RRR 1.25"),
        (60, 1.3, "RRR 1.3"),
        (60, 1.4, "RRR 1.4"),
        (60, 1.5, "RRR 1.5"),
        (65, 1.5, "RRR 1.5"),
        (70, 1.5, "RRR 1.5"),
    ]
    
    for prob, rrr, desc in test_cases:
        ev = calculate_expected_value(prob, rrr)
        if ev > 0.5:
            meaning = "ดีมาก - คุ้มค่าเสี่ยง"
        elif ev > 0.3:
            meaning = "ดี - คุ้มค่าเสี่ยง"
        elif ev > 0.1:
            meaning = "พอใช้ - คุ้มค่าเสี่ยงเล็กน้อย"
        elif ev > 0:
            meaning = "ต่ำ - คุ้มค่าเสี่ยงน้อย"
        else:
            meaning = "ไม่คุ้ม - เสี่ยงมาก"
        
        print(f"{prob:>7.0f}% {rrr:>7.2f} {ev:>17.3f} {meaning}")
    
    print("\n" + "=" * 160)
    print("หุ้นที่มี Prob >= 60% และ RRR ต่างๆ")
    print("=" * 160)
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            continue
        
        prob_60 = country_df[country_df['Prob%'] >= 60.0].copy()
        if prob_60.empty:
            continue
        
        # คำนวณ Expected Value
        prob_60['EV'] = prob_60.apply(lambda row: calculate_expected_value(row['Prob%'], row['RR_Ratio']), axis=1)
        prob_60 = prob_60.sort_values('EV', ascending=False)
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN',
            'GL': 'METALS'
        }.get(country, country)
        
        print(f"\n{country_name}:")
        print(f"  หุ้นที่มี Prob >= 60%: {len(prob_60)} หุ้น")
        
        # แบ่งตาม RRR
        rrr_15_plus = prob_60[prob_60['RR_Ratio'] >= 1.5]
        rrr_13_15 = prob_60[(prob_60['RR_Ratio'] >= 1.3) & (prob_60['RR_Ratio'] < 1.5)]
        rrr_125_13 = prob_60[(prob_60['RR_Ratio'] >= 1.25) & (prob_60['RR_Ratio'] < 1.3)]
        rrr_below_125 = prob_60[prob_60['RR_Ratio'] < 1.25]
        
        print(f"  RRR >= 1.5: {len(rrr_15_plus)} หุ้น (EV เฉลี่ย: {rrr_15_plus['EV'].mean():.3f})")
        print(f"  RRR 1.3-1.5: {len(rrr_13_15)} หุ้น (EV เฉลี่ย: {rrr_13_15['EV'].mean():.3f})")
        print(f"  RRR 1.25-1.3: {len(rrr_125_13)} หุ้น (EV เฉลี่ย: {rrr_125_13['EV'].mean():.3f})")
        print(f"  RRR < 1.25: {len(rrr_below_125)} หุ้น (EV เฉลี่ย: {rrr_below_125['EV'].mean():.3f})")
        
        # แสดงหุ้นที่ RRR >= 1.5
        if not rrr_15_plus.empty:
            print(f"\n  หุ้นที่ RRR >= 1.5 (คุ้มค่าเสี่ยง):")
            print(f"    {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'EV':>8} {'Count':>8}")
            print(f"    {'-' * 60}")
            for _, row in rrr_15_plus.head(10).iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                ev = row['EV']
                count = int(row['Count'])
                print(f"    {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {ev:>7.3f} {count:>8}")
        
        # แสดงหุ้นที่ RRR 1.3-1.5 (ใกล้เกณฑ์)
        if not rrr_13_15.empty:
            print(f"\n  หุ้นที่ RRR 1.3-1.5 (ใกล้เกณฑ์):")
            print(f"    {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'EV':>8} {'Count':>8}")
            print(f"    {'-' * 60}")
            for _, row in rrr_13_15.head(5).iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                ev = row['EV']
                count = int(row['Count'])
                print(f"    {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {ev:>7.3f} {count:>8}")
    
    # สรุป
    print("\n" + "=" * 160)
    print("สรุปและคำแนะนำ:")
    print("=" * 160)
    print("""
Expected Value (EV) = (Prob% * RRR) - ((1 - Prob%) * 1.0)

การตีความ:
  - EV > 0.5: ดีมาก - คุ้มค่าเสี่ยงมาก
  - EV > 0.3: ดี - คุ้มค่าเสี่ยง
  - EV > 0.1: พอใช้ - คุ้มค่าเสี่ยงเล็กน้อย
  - EV > 0: ต่ำ - คุ้มค่าเสี่ยงน้อย
  - EV <= 0: ไม่คุ้ม - เสี่ยงมาก

ตัวอย่าง:
  - Prob 60%, RRR 1.25 → EV = 0.35 (พอใช้)
  - Prob 60%, RRR 1.5 → EV = 0.50 (ดี)
  - Prob 65%, RRR 1.5 → EV = 0.65 (ดีมาก)

คำแนะนำ:
  - RRR >= 1.5 ควรเป็นเกณฑ์ขั้นต่ำสำหรับการเทรดจริง
  - RRR 1.25-1.3 อาจจะไม่คุ้มค่าเสี่ยงพอ (EV ต่ำ)
  - ถ้า Prob สูง (>= 70%) อาจยอมรับ RRR ต่ำกว่าได้เล็กน้อย
    """)
    print("=" * 160)

if __name__ == "__main__":
    analyze_rrr_viability()

