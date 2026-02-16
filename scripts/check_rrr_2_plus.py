#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบหุ้นที่มี RRR >= 2.0 และ Prob >= 60%
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

def check_rrr_2_plus():
    """ตรวจสอบหุ้นที่มี RRR >= 2.0"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 140)
    print("ตรวจสอบหุ้นที่มี RRR >= 2.0")
    print("=" * 140)
    
    # หาหุ้นที่มี RRR >= 2.0
    rrr_2_plus = df[df['RR_Ratio'] >= 2.0].sort_values('RR_Ratio', ascending=False)
    
    if rrr_2_plus.empty:
        print("\n❌ ไม่มีหุ้นใดที่มี RRR >= 2.0")
    else:
        print(f"\nพบ {len(rrr_2_plus)} หุ้นที่มี RRR >= 2.0:")
        print("-" * 140)
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
        print("-" * 140)
        for _, row in rrr_2_plus.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)
            count = int(row.get('Count', 0))
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    
    # ตรวจสอบหุ้นที่มี Prob >= 60% และ RRR >= 2.0
    print("\n" + "=" * 140)
    print("ตรวจสอบหุ้นที่มี Prob >= 60% และ RRR >= 2.0")
    print("=" * 140)
    
    both_criteria = df[
        (df['Prob%'] >= 60.0) & 
        (df['RR_Ratio'] >= 2.0)
    ].sort_values('RR_Ratio', ascending=False)
    
    if both_criteria.empty:
        print("\n❌ ไม่มีหุ้นใดที่มี Prob >= 60% และ RRR >= 2.0")
        
        # แสดงหุ้นที่ใกล้เกณฑ์ที่สุด
        print("\n" + "=" * 140)
        print("หุ้นที่ใกล้เกณฑ์ที่สุด (Prob >= 60%, RRR ใกล้ 2.0):")
        print("-" * 140)
        
        prob_60_plus = df[df['Prob%'] >= 60.0].sort_values('RR_Ratio', ascending=False)
        if not prob_60_plus.empty:
            print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
            print("-" * 140)
            for _, row in prob_60_plus.head(10).iterrows():
                symbol = str(row['symbol'])
                country = str(row.get('Country', 'N/A'))
                prob = row.get('Prob%', 0.0)
                rrr = row.get('RR_Ratio', 0.0)
                count = int(row.get('Count', 0))
                avg_win = row.get('AvgWin%', 0.0)
                avg_loss = row.get('AvgLoss%', 0.0)
                print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    else:
        print(f"\n✅ พบ {len(both_criteria)} หุ้นที่มี Prob >= 60% และ RRR >= 2.0:")
        print("-" * 140)
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
        print("-" * 140)
        for _, row in both_criteria.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)
            count = int(row.get('Count', 0))
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    
    # สรุปตามประเทศ
    print("\n" + "=" * 140)
    print("สรุปตามประเทศ:")
    print("-" * 140)
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            continue
        
        rrr_2_plus_country = country_df[country_df['RR_Ratio'] >= 2.0]
        both_criteria_country = country_df[
            (country_df['Prob%'] >= 60.0) & 
            (country_df['RR_Ratio'] >= 2.0)
        ]
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN',
            'GL': 'METALS'
        }.get(country, country)
        
        print(f"\n{country_name}:")
        print(f"  หุ้นที่มี RRR >= 2.0: {len(rrr_2_plus_country)} หุ้น")
        if not rrr_2_plus_country.empty:
            for _, row in rrr_2_plus_country.iterrows():
                print(f"     - {row['symbol']}: RRR {row['RR_Ratio']:.2f}, Prob {row['Prob%']:.1f}%, Count {int(row['Count'])}")
        
        print(f"  หุ้นที่มี Prob >= 60% และ RRR >= 2.0: {len(both_criteria_country)} หุ้น")
        if not both_criteria_country.empty:
            for _, row in both_criteria_country.iterrows():
                print(f"     - {row['symbol']}: RRR {row['RR_Ratio']:.2f}, Prob {row['Prob%']:.1f}%, Count {int(row['Count'])}")
    
    print("\n" + "=" * 140)

if __name__ == "__main__":
    check_rrr_2_plus()

