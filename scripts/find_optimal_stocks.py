#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
หาหุ้นที่ Prob >= 60%, Count >= 30 (น่าเชื่อถือ), RRR ใกล้ 2.0
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

def find_optimal_stocks(min_prob=60.0, min_count=30, target_rrr=2.0):
    """หาหุ้นที่ Prob >= 60%, Count >= 30, RRR ใกล้ 2.0"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    # กรองตามเกณฑ์
    filtered = df[
        (df['Prob%'] >= min_prob) &
        (df['Count'] >= min_count)
    ].copy()
    
    if filtered.empty:
        print(f"\n❌ ไม่พบหุ้นที่ Prob >= {min_prob}% และ Count >= {min_count}")
        return
    
    # คำนวณระยะห่างจาก RRR 2.0
    filtered['RRR_Distance_From_2'] = abs(filtered['RR_Ratio'] - target_rrr)
    
    # เรียงตาม RRR ใกล้ 2.0 มากที่สุด
    filtered = filtered.sort_values('RRR_Distance_From_2')
    
    print("\n" + "=" * 140)
    print(f"หาหุ้นที่ Prob >= {min_prob}%, Count >= {min_count}, RRR ใกล้ {target_rrr}")
    print("=" * 140)
    
    # แสดงผลทั้งหมด
    print(f"\nพบ {len(filtered)} หุ้นที่ผ่านเกณฑ์:")
    print("-" * 140)
    print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Distance':>10} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'Quality':<20}")
    print("-" * 140)
    
    for _, row in filtered.iterrows():
        symbol = str(row['symbol'])
        country = str(row.get('Country', 'N/A'))
        prob = row.get('Prob%', 0.0)
        rrr = row.get('RR_Ratio', 0.0)
        distance = row['RRR_Distance_From_2']
        count = int(row.get('Count', 0))
        avg_win = row.get('AvgWin%', 0.0)
        avg_loss = row.get('AvgLoss%', 0.0)
        
        # จัดหมวดหมู่ Quality
        if rrr >= 1.8:
            quality = "[EXCELLENT]"
        elif rrr >= 1.5:
            quality = "[GOOD]"
        elif rrr >= 1.2:
            quality = "[FAIR]"
        else:
            quality = "[POOR]"
        
        print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {distance:>9.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}% {quality}")
    
    print("-" * 140)
    
    # สรุปตามประเทศ
    print("\n" + "=" * 140)
    print("สรุปตามประเทศ:")
    print("-" * 140)
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        country_df = filtered[filtered['Country'] == country]
        if country_df.empty:
            continue
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN',
            'GL': 'METALS'
        }.get(country, country)
        
        excellent = country_df[country_df['RR_Ratio'] >= 1.8]
        good = country_df[(country_df['RR_Ratio'] >= 1.5) & (country_df['RR_Ratio'] < 1.8)]
        fair = country_df[(country_df['RR_Ratio'] >= 1.2) & (country_df['RR_Ratio'] < 1.5)]
        
        print(f"\n{country_name}: {len(country_df)} หุ้น")
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
        
        # Average metrics
        avg_rrr = country_df['RR_Ratio'].mean()
        avg_prob = country_df['Prob%'].mean()
        print(f"  Average RRR: {avg_rrr:.2f}, Average Prob: {avg_prob:.1f}%")
    
    # Top 10 ที่ RRR ใกล้ 2.0 มากที่สุด
    print("\n" + "=" * 140)
    print("TOP 10 หุ้นที่ RRR ใกล้ 2.0 มากที่สุด (Prob >= 60%, Count >= 30):")
    print("-" * 140)
    top_10 = filtered.head(10)
    print(f"{'Rank':<6} {'Symbol':<12} {'Country':<8} {'Prob%':>8} {'RRR':>8} {'Distance':>10} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
    print("-" * 140)
    for idx, (_, row) in enumerate(top_10.iterrows(), 1):
        symbol = str(row['symbol'])
        country = str(row.get('Country', 'N/A'))
        prob = row.get('Prob%', 0.0)
        rrr = row.get('RR_Ratio', 0.0)
        distance = row['RRR_Distance_From_2']
        count = int(row.get('Count', 0))
        avg_win = row.get('AvgWin%', 0.0)
        avg_loss = row.get('AvgLoss%', 0.0)
        print(f"{idx:<6} {symbol:<12} {country:<8} {prob:>7.1f}% {rrr:>7.2f} {distance:>9.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    
    print("\n" + "=" * 140)
    print("สรุป:")
    print(f"  - หุ้นที่ Prob >= {min_prob}% และ Count >= {min_count}: {len(filtered)} หุ้น")
    print(f"  - หุ้นที่ RRR >= 1.8 (Excellent): {len(filtered[filtered['RR_Ratio'] >= 1.8])} หุ้น")
    print(f"  - หุ้นที่ RRR 1.5-1.8 (Good): {len(filtered[(filtered['RR_Ratio'] >= 1.5) & (filtered['RR_Ratio'] < 1.8)])} หุ้น")
    print(f"  - หุ้นที่ RRR 1.2-1.5 (Fair): {len(filtered[(filtered['RR_Ratio'] >= 1.2) & (filtered['RR_Ratio'] < 1.5)])} หุ้น")
    print("=" * 140)

if __name__ == "__main__":
    find_optimal_stocks(min_prob=60.0, min_count=30, target_rrr=2.0)

