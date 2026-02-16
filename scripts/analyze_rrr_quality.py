#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
วิเคราะห์หุ้นที่มี RRR ใกล้ 2.0 (ยิ่งใกล้ 2 ยิ่งดี)
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

def analyze_rrr_quality():
    """วิเคราะห์หุ้นตาม RRR Quality"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    # คำนวณ RRR Distance from 2.0 (ยิ่งใกล้ 2 ยิ่งดี)
    df['RRR_Distance_From_2'] = abs(df['RR_Ratio'] - 2.0)
    
    # จัดหมวดหมู่ RRR Quality
    def categorize_rrr(rrr):
        if rrr >= 1.8:
            return "[EXCELLENT] (>= 1.8)"
        elif rrr >= 1.5:
            return "[GOOD] (1.5-1.8)"
        elif rrr >= 1.2:
            return "[FAIR] (1.2-1.5)"
        else:
            return "[POOR] (< 1.2)"
    
    df['RRR_Quality'] = df['RR_Ratio'].apply(categorize_rrr)
    
    print("\n" + "=" * 120)
    print("RRR QUALITY ANALYSIS (ยิ่งใกล้ 2.0 ยิ่งดี)")
    print("=" * 120)
    
    # แสดงหุ้นที่ RRR ใกล้ 2.0 มากที่สุด (Top 20)
    print("\nTOP 20 หุ้นที่ RRR ใกล้ 2.0 มากที่สุด:")
    print("-" * 120)
    top_rrr = df.nsmallest(20, 'RRR_Distance_From_2')
    print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Distance':>10} {'Count':>8} {'Quality':<25}")
    print("-" * 120)
    for _, row in top_rrr.iterrows():
        symbol = str(row['symbol'])
        country = str(row.get('Country', 'N/A'))
        prob = row.get('Prob%', 0.0)
        rrr = row.get('RR_Ratio', 0.0)
        distance = row['RRR_Distance_From_2']
        count = int(row.get('Count', 0))
        quality = row['RRR_Quality']
        print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {distance:>9.2f} {count:>8} {quality}")
    
    # สรุปตามประเทศ
    print("\n" + "=" * 120)
    print("สรุป RRR Quality ตามประเทศ:")
    print("-" * 120)
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            continue
        
        excellent = country_df[country_df['RR_Ratio'] >= 1.8]
        good = country_df[(country_df['RR_Ratio'] >= 1.5) & (country_df['RR_Ratio'] < 1.8)]
        fair = country_df[(country_df['RR_Ratio'] >= 1.2) & (country_df['RR_Ratio'] < 1.5)]
        poor = country_df[country_df['RR_Ratio'] < 1.2]
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN',
            'GL': 'METALS'
        }.get(country, country)
        
        print(f"\n{country_name}:")
        print(f"  [EXCELLENT] (RRR >= 1.8): {len(excellent)} หุ้น")
        if not excellent.empty:
            for _, row in excellent.iterrows():
                print(f"     - {row['symbol']}: RRR {row['RR_Ratio']:.2f}, Prob {row['Prob%']:.1f}%, Count {int(row['Count'])}")
        
        print(f"  [GOOD] (RRR 1.5-1.8): {len(good)} หุ้น")
        if not good.empty and len(good) <= 5:
            for _, row in good.iterrows():
                print(f"     - {row['symbol']}: RRR {row['RR_Ratio']:.2f}, Prob {row['Prob%']:.1f}%, Count {int(row['Count'])}")
        elif len(good) > 5:
            top_good = good.nlargest(3, 'RR_Ratio')
            for _, row in top_good.iterrows():
                print(f"     - {row['symbol']}: RRR {row['RR_Ratio']:.2f}, Prob {row['Prob%']:.1f}%, Count {int(row['Count'])}")
            print(f"     ... และอีก {len(good) - 3} หุ้น")
        
        print(f"  [FAIR] (RRR 1.2-1.5): {len(fair)} หุ้น")
        print(f"  [POOR] (RRR < 1.2): {len(poor)} หุ้น")
        
        # คำนวณ Average RRR
        avg_rrr = country_df['RR_Ratio'].mean()
        print(f"  Average RRR: {avg_rrr:.2f}")
    
    # หุ้นที่ RRR >= 1.8 (Excellent)
    print("\n" + "=" * 120)
    print("หุ้นที่ RRR >= 1.8 (Excellent - ใกล้ 2.0):")
    print("-" * 120)
    excellent_all = df[df['RR_Ratio'] >= 1.8].sort_values('RRR_Distance_From_2')
    if not excellent_all.empty:
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Distance':>10} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
        print("-" * 120)
        for _, row in excellent_all.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)
            distance = row['RRR_Distance_From_2']
            count = int(row.get('Count', 0))
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {distance:>9.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    else:
        print("  ไม่มีหุ้นที่ RRR >= 1.8")
    
    # หุ้นที่ RRR ระหว่าง 1.5-1.8 (Good)
    print("\n" + "=" * 120)
    print("หุ้นที่ RRR 1.5-1.8 (Good - กำลังดี):")
    print("-" * 120)
    good_all = df[(df['RR_Ratio'] >= 1.5) & (df['RR_Ratio'] < 1.8)].sort_values('RRR_Distance_From_2')
    if not good_all.empty:
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Distance':>10} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
        print("-" * 120)
        for _, row in good_all.head(20).iterrows():  # แสดง Top 20
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)
            distance = row['RRR_Distance_From_2']
            count = int(row.get('Count', 0))
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {distance:>9.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
        if len(good_all) > 20:
            print(f"\n  ... และอีก {len(good_all) - 20} หุ้น")
    else:
        print("  ไม่มีหุ้นที่ RRR 1.5-1.8")
    
    print("\n" + "=" * 120)
    print("สรุป:")
    print(f"  - หุ้นที่ RRR >= 1.8 (Excellent): {len(df[df['RR_Ratio'] >= 1.8])} หุ้น")
    print(f"  - หุ้นที่ RRR 1.5-1.8 (Good): {len(df[(df['RR_Ratio'] >= 1.5) & (df['RR_Ratio'] < 1.8)])} หุ้น")
    print(f"  - หุ้นที่ RRR 1.2-1.5 (Fair): {len(df[(df['RR_Ratio'] >= 1.2) & (df['RR_Ratio'] < 1.5)])} หุ้น")
    print(f"  - หุ้นที่ RRR < 1.2 (Poor): {len(df[df['RR_Ratio'] < 1.2])} หุ้น")
    print("=" * 120)

if __name__ == "__main__":
    analyze_rrr_quality()

