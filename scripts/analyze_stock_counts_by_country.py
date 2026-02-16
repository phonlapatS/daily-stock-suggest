#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_stock_counts_by_country.py - วิเคราะห์จำนวนหุ้นทั้งหมดและทำไมถึงเจอน้อย
================================================================================
"""

import pandas as pd
import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
METRICS_FILE = os.path.join(DATA_DIR, "symbol_performance.csv")


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์จำนวนหุ้นทั้งหมดและทำไมถึงเจอน้อย")
    print("="*100)
    
    # Load data
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    print(f"\n📊 โหลดข้อมูล: {len(df)} symbols ทั้งหมด")
    
    # Count by country
    print("\n[1] จำนวนหุ้นทั้งหมดในแต่ละประเทศ")
    print("-" * 80)
    country_counts = df.groupby('Country').size().sort_values(ascending=False)
    for country, count in country_counts.items():
        print(f"   {country}: {count} symbols")
    
    # Statistics by country
    print("\n[2] สถิติ Prob%, RRR, AvgWin%, AvgLoss% ตามประเทศ")
    print("-" * 80)
    
    for country in ['US', 'CN', 'TW', 'TH', 'GL']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            print(f"\n   [{country}] ไม่มีข้อมูล")
            continue
        
        print(f"\n   [{country}] {len(country_df)} symbols")
        print(f"      Prob%: Mean={country_df['Prob%'].mean():.1f}%, "
              f"Min={country_df['Prob%'].min():.1f}%, Max={country_df['Prob%'].max():.1f}%")
        print(f"      RRR: Mean={country_df['RR_Ratio'].mean():.2f}, "
              f"Min={country_df['RR_Ratio'].min():.2f}, Max={country_df['RR_Ratio'].max():.2f}")
        print(f"      AvgWin%: Mean={country_df['AvgWin%'].mean():.2f}%, "
              f"Max={country_df['AvgWin%'].max():.2f}%")
        print(f"      AvgLoss%: Mean={country_df['AvgLoss%'].mean():.2f}%, "
              f"Max={country_df['AvgLoss%'].max():.2f}%")
        print(f"      Count: Mean={country_df['Count'].mean():.0f}, "
              f"Min={country_df['Count'].min():.0f}, Max={country_df['Count'].max():.0f}")
    
    # Check why US/CN/TW have few matches
    print("\n[3] วิเคราะห์ทำไม US/CN/TW เจอน้อย")
    print("-" * 80)
    
    # Current criteria
    print("\n   [เกณฑ์ปัจจุบัน]")
    print("   US: Prob >= 55% AND RRR >= 1.2 AND AvgWin > 1.5% AND AvgLoss < 2.5% AND Count >= 10")
    print("   CN: Prob >= 55% AND RRR >= 1.2 AND AvgWin > 1.0% AND AvgLoss < 2.0% AND Count >= 10")
    print("   TW: Prob >= 55% AND RRR >= 1.2 AND AvgWin > 1.0% AND AvgLoss < 2.5% AND Count >= 10")
    
    # Check US
    print("\n   [US Market Analysis]")
    us_df = df[df['Country'] == 'US']
    if not us_df.empty:
        print(f"      ทั้งหมด: {len(us_df)} symbols")
        
        # Check each criteria
        prob_ok = us_df[us_df['Prob%'] >= 55.0]
        print(f"      Prob >= 55%: {len(prob_ok)} symbols")
        
        rrr_ok = us_df[us_df['RR_Ratio'] >= 1.2]
        print(f"      RRR >= 1.2: {len(rrr_ok)} symbols")
        
        avgwin_ok = us_df[us_df['AvgWin%'] > 1.5]
        print(f"      AvgWin > 1.5%: {len(avgwin_ok)} symbols")
        
        avgloss_ok = us_df[us_df['AvgLoss%'] < 2.5]
        print(f"      AvgLoss < 2.5%: {len(avgloss_ok)} symbols")
        
        count_ok = us_df[us_df['Count'] >= 10]
        print(f"      Count >= 10: {len(count_ok)} symbols")
        
        # Combined
        combined = us_df[
            (us_df['Prob%'] >= 55.0) & 
            (us_df['RR_Ratio'] >= 1.2) &
            (us_df['AvgWin%'] > 1.5) &
            (us_df['AvgLoss%'] < 2.5) &
            (us_df['Count'] >= 10)
        ]
        print(f"      รวมทั้งหมด: {len(combined)} symbols")
        
        # Show what's blocking
        if len(combined) < len(us_df):
            print(f"\n      [ปัญหาที่พบ]")
            # Check which criteria is blocking
            prob_block = us_df[us_df['Prob%'] < 55.0]
            rrr_block = us_df[us_df['RR_Ratio'] < 1.2]
            avgwin_block = us_df[us_df['AvgWin%'] <= 1.5]
            avgloss_block = us_df[us_df['AvgLoss%'] >= 2.5]
            count_block = us_df[us_df['Count'] < 10]
            
            print(f"      Prob < 55%: {len(prob_block)} symbols")
            print(f"      RRR < 1.2: {len(rrr_block)} symbols")
            print(f"      AvgWin <= 1.5%: {len(avgwin_block)} symbols")
            print(f"      AvgLoss >= 2.5%: {len(avgloss_block)} symbols")
            print(f"      Count < 10: {len(count_block)} symbols")
            
            # Show top stocks that don't pass
            print(f"\n      [ตัวอย่างหุ้นที่ไม่ได้ผ่านเกณฑ์]")
            failed = us_df[~us_df.index.isin(combined.index)]
            top_failed = failed.nlargest(5, 'Prob%')
            for _, row in top_failed.iterrows():
                reasons = []
                if row['Prob%'] < 55.0:
                    reasons.append(f"Prob={row['Prob%']:.1f}%")
                if row['RR_Ratio'] < 1.2:
                    reasons.append(f"RRR={row['RR_Ratio']:.2f}")
                if row['AvgWin%'] <= 1.5:
                    reasons.append(f"AvgWin={row['AvgWin%']:.2f}%")
                if row['AvgLoss%'] >= 2.5:
                    reasons.append(f"AvgLoss={row['AvgLoss%']:.2f}%")
                if row['Count'] < 10:
                    reasons.append(f"Count={row['Count']:.0f}")
                print(f"        {row['symbol']}: {', '.join(reasons)}")
    
    # Check CN
    print("\n   [CN Market Analysis]")
    cn_df = df[df['Country'] == 'CN']
    if not cn_df.empty:
        print(f"      ทั้งหมด: {len(cn_df)} symbols")
        
        combined = cn_df[
            (cn_df['Prob%'] >= 55.0) & 
            (cn_df['RR_Ratio'] >= 1.2) &
            (cn_df['AvgWin%'] > 1.0) &
            (cn_df['AvgLoss%'] < 2.0) &
            (cn_df['Count'] >= 10)
        ]
        print(f"      ผ่านเกณฑ์: {len(combined)} symbols")
        
        if len(combined) == 0:
            print(f"\n      [ปัญหาที่พบ]")
            print(f"      Prob >= 55%: {len(cn_df[cn_df['Prob%'] >= 55.0])} symbols")
            print(f"      RRR >= 1.2: {len(cn_df[cn_df['RR_Ratio'] >= 1.2])} symbols")
            print(f"      AvgWin > 1.0%: {len(cn_df[cn_df['AvgWin%'] > 1.0])} symbols")
            print(f"      AvgLoss < 2.0%: {len(cn_df[cn_df['AvgLoss%'] < 2.0])} symbols")
            print(f"      Count >= 10: {len(cn_df[cn_df['Count'] >= 10])} symbols")
            
            # Show all CN stocks
            print(f"\n      [หุ้นทั้งหมดใน CN]")
            for _, row in cn_df.iterrows():
                print(f"        {row['symbol']}: Prob={row['Prob%']:.1f}%, "
                      f"RRR={row['RR_Ratio']:.2f}, AvgWin={row['AvgWin%']:.2f}%, "
                      f"AvgLoss={row['AvgLoss%']:.2f}%, Count={row['Count']:.0f}")
    
    # Check TW
    print("\n   [TW Market Analysis]")
    tw_df = df[df['Country'] == 'TW']
    if not tw_df.empty:
        print(f"      ทั้งหมด: {len(tw_df)} symbols")
        
        combined = tw_df[
            (tw_df['Prob%'] >= 55.0) & 
            (tw_df['RR_Ratio'] >= 1.2) &
            (tw_df['AvgWin%'] > 1.0) &
            (tw_df['AvgLoss%'] < 2.5) &
            (tw_df['Count'] >= 10)
        ]
        print(f"      ผ่านเกณฑ์: {len(combined)} symbols")
        
        if len(combined) == 0:
            print(f"\n      [ปัญหาที่พบ]")
            print(f"      Prob >= 55%: {len(tw_df[tw_df['Prob%'] >= 55.0])} symbols")
            print(f"      RRR >= 1.2: {len(tw_df[tw_df['RR_Ratio'] >= 1.2])} symbols")
            print(f"      AvgWin > 1.0%: {len(tw_df[tw_df['AvgWin%'] > 1.0])} symbols")
            print(f"      AvgLoss < 2.5%: {len(tw_df[tw_df['AvgLoss%'] < 2.5])} symbols")
            print(f"      Count >= 10: {len(tw_df[tw_df['Count'] >= 10])} symbols")
            
            # Show all TW stocks
            print(f"\n      [หุ้นทั้งหมดใน TW]")
            for _, row in tw_df.iterrows():
                print(f"        {row['symbol']}: Prob={row['Prob%']:.1f}%, "
                      f"RRR={row['RR_Ratio']:.2f}, AvgWin={row['AvgWin%']:.2f}%, "
                      f"AvgLoss={row['AvgLoss%']:.2f}%, Count={row['Count']:.0f}")
    
    # Suggest improvements
    print("\n[4] แนวทางปรับปรุง")
    print("-" * 80)
    print("   [US Market]")
    print("   - ลด AvgWin requirement: 1.5% → 1.0% (เพราะ US มี AvgWin ต่ำ)")
    print("   - หรือลด Prob requirement: 55% → 52% (เพราะ Trend Following มี Prob ต่ำ)")
    print("   - หรือลด RRR requirement: 1.2 → 1.0 (เพราะ US มี RRR ต่ำ)")
    print()
    print("   [CN Market]")
    print("   - ลด Prob requirement: 55% → 50% (เพราะ CN มี Prob ต่ำ)")
    print("   - หรือลด RRR requirement: 1.2 → 1.0")
    print("   - หรือลด AvgWin requirement: 1.0% → 0.8%")
    print()
    print("   [TW Market]")
    print("   - ลด Prob requirement: 55% → 50%")
    print("   - หรือลด RRR requirement: 1.2 → 1.0")
    print("   - หรือลด AvgWin requirement: 1.0% → 0.8%")
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้น")
    print("="*100)


if __name__ == "__main__":
    main()

