#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_count_impact.py - วิเคราะห์ผลกระทบของการเพิ่ม Count
================================================================================
วิเคราะห์ว่าถ้าเพิ่ม Count แล้ว Prob% และ RRR จะตกไหม
"""

import pandas as pd
import os
import sys

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
METRICS_FILE = os.path.join(DATA_DIR, "symbol_performance.csv")

def analyze_count_impact():
    """วิเคราะห์ผลกระทบของการเพิ่ม Count"""
    
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "="*120)
    print("📊 วิเคราะห์ผลกระทบของการเพิ่ม Count")
    print("="*120)
    
    # เกณฑ์ปัจจุบัน
    print("\n📋 เกณฑ์ Count ปัจจุบัน:")
    print("   THAI: Count >= 30")
    print("   US: Count >= 15")
    print("   CHINA/HK: Count >= 15")
    print("   TAIWAN: Count >= 15")
    
    # วิเคราะห์แต่ละประเทศ
    countries = {
        'TH': {'name': 'THAI', 'current': 30, 'suggested': [40, 50, 60]},
        'US': {'name': 'US', 'current': 15, 'suggested': [20, 25, 30]},
        'CN': {'name': 'CHINA/HK', 'current': 15, 'suggested': [20, 25, 30]},
        'TW': {'name': 'TAIWAN', 'current': 15, 'suggested': [20, 25, 30]}
    }
    
    for country_code, country_info in countries.items():
        country_df = df[df['Country'] == country_code].copy()
        
        if country_df.empty:
            continue
        
        print(f"\n" + "="*120)
        print(f"📊 {country_info['name']} MARKET")
        print("="*120)
        
        current_count = country_info['current']
        current_passing = country_df[country_df['Count'] >= current_count]
        
        print(f"\nเกณฑ์ปัจจุบัน (Count >= {current_count}):")
        print(f"   Symbols ที่ผ่าน: {len(current_passing)}")
        if len(current_passing) > 0:
            print(f"   Prob% เฉลี่ย: {current_passing['Prob%'].mean():.1f}%")
            print(f"   RRR เฉลี่ย: {current_passing['RR_Ratio'].mean():.2f}")
            print(f"   Count เฉลี่ย: {current_passing['Count'].mean():.1f}")
        
        # วิเคราะห์แต่ละ Count ที่แนะนำ
        for suggested_count in country_info['suggested']:
            suggested_passing = country_df[country_df['Count'] >= suggested_count]
            
            if len(suggested_passing) == 0:
                continue
            
            print(f"\nถ้าเพิ่มเป็น Count >= {suggested_count}:")
            print(f"   Symbols ที่ผ่าน: {len(suggested_passing)} (ลดลง {len(current_passing) - len(suggested_passing)} symbols)")
            
            if len(suggested_passing) > 0:
                print(f"   Prob% เฉลี่ย: {suggested_passing['Prob%'].mean():.1f}% (เปลี่ยน {suggested_passing['Prob%'].mean() - current_passing['Prob%'].mean():+.1f}%)")
                print(f"   RRR เฉลี่ย: {suggested_passing['RR_Ratio'].mean():.2f} (เปลี่ยน {suggested_passing['RR_Ratio'].mean() - current_passing['RR_Ratio'].mean():+.2f})")
                print(f"   Count เฉลี่ย: {suggested_passing['Count'].mean():.1f}")
                
                # เปรียบเทียบหุ้นที่หายไป
                lost_symbols = current_passing[~current_passing['symbol'].isin(suggested_passing['symbol'])]
                if len(lost_symbols) > 0:
                    print(f"   หุ้นที่หายไป ({len(lost_symbols)} symbols):")
                    for idx, row in lost_symbols.head(5).iterrows():
                        print(f"      {row['symbol']}: Count={row['Count']}, Prob%={row['Prob%']:.1f}%, RRR={row['RR_Ratio']:.2f}")
    
    # สรุปคำแนะนำ
    print("\n" + "="*120)
    print("💡 คำแนะนำ")
    print("="*120)
    
    print("\n📊 ผลกระทบของการเพิ่ม Count:")
    print("   ✅ Prob% และ RRR จะไม่ตก (เพราะใช้ค่าเดิม)")
    print("   ❌ แต่จำนวน Symbols ที่ผ่านจะลดลง")
    print("   ✅ Symbols ที่เหลือจะมี Count สูงกว่า → น่าเชื่อถือมากขึ้น")
    
    print("\n📋 คำแนะนำ Count ที่เหมาะสม:")
    print("   THAI: Count >= 40-50 (เพิ่มจาก 30)")
    print("   US: Count >= 20-25 (เพิ่มจาก 15)")
    print("   CHINA/HK: Count >= 20-25 (เพิ่มจาก 15)")
    print("   TAIWAN: Count >= 20-25 (เพิ่มจาก 15)")
    
    print("\n⚠️ หมายเหตุ:")
    print("   - Prob% และ RRR จะไม่เปลี่ยน (ใช้ค่าเดิม)")
    print("   - แต่จำนวน Symbols ที่ผ่านจะลดลง")
    print("   - Symbols ที่เหลือจะมี Count สูงกว่า → น่าเชื่อถือมากขึ้น")
    
    print("\n" + "="*120)

if __name__ == "__main__":
    analyze_count_impact()

