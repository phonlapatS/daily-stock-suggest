#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
วิเคราะห์ปัญหา Count ที่น้อย
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

def analyze_count_issue():
    """วิเคราะห์ปัญหา Count ที่น้อย"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("วิเคราะห์ปัญหา Count ที่น้อย")
    print("=" * 160)
    
    # หาหุ้นที่ผ่านเกณฑ์ปัจจุบัน
    criteria = {
        'TH': {'prob': 60.0, 'rrr': 1.3, 'count': 30},
        'US': {'prob': 60.0, 'rrr': 1.5, 'count': 15},
        'CN': {'prob': 60.0, 'rrr': 1.5, 'count': 20},
        'TW': {'prob': 60.0, 'rrr': 1.3, 'count': 25},
    }
    
    for country_code, crit in criteria.items():
        country_df = df[df['Country'] == country_code]
        if country_df.empty:
            continue
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN'
        }.get(country_code, country_code)
        
        # กรองตามเกณฑ์
        filtered = country_df[
            (country_df['Prob%'] >= crit['prob']) &
            (country_df['RR_Ratio'] >= crit['rrr']) &
            (country_df['Count'] >= crit['count'])
        ]
        
        if filtered.empty:
            continue
        
        print(f"\n{'=' * 160}")
        print(f"{country_name} - เปรียบเทียบ Raw_Count vs Elite_Count vs Count")
        print("=" * 160)
        print(f"{'Symbol':<12} {'Raw_Count':>12} {'Elite_Count':>14} {'Count':>8} {'Diff':>10} {'Prob%':>8} {'RRR':>8}")
        print("-" * 160)
        
        for _, row in filtered.sort_values('Count', ascending=True).iterrows():
            symbol = str(row['symbol'])
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            count = int(row.get('Count', 0))
            prob = row.get('Prob%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)
            
            # คำนวณความแตกต่าง
            if raw_count > 0:
                diff = raw_count - count
                diff_pct = (diff / raw_count) * 100 if raw_count > 0 else 0
            else:
                diff = 0
                diff_pct = 0
            
            # ตรวจสอบว่าควรใช้ Raw_Count หรือไม่
            if diff > 100:
                status = "⚠️  Count ลดลงมาก"
            elif diff > 50:
                status = "⚠️  Count ลดลง"
            else:
                status = "✅ OK"
            
            print(f"{symbol:<12} {raw_count:>12} {elite_count:>14} {count:>8} {diff:>9} ({diff_pct:>5.1f}%) {prob:>7.1f}% {rrr:>7.2f} {status}")
        
        # สรุป
        print("\n" + "-" * 160)
        print("สรุป:")
        avg_raw = filtered['Raw_Count'].mean()
        avg_elite = filtered['Elite_Count'].mean()
        avg_count = filtered['Count'].mean()
        
        print(f"  Raw_Count เฉลี่ย: {avg_raw:.0f}")
        print(f"  Elite_Count เฉลี่ย: {avg_elite:.0f}")
        print(f"  Count เฉลี่ย: {avg_count:.0f}")
        print(f"  Count ลดลงเฉลี่ย: {avg_raw - avg_count:.0f} ({(avg_raw - avg_count)/avg_raw*100:.1f}%)")
        
        # หาหุ้นที่ Count น้อยที่สุด
        min_count = filtered['Count'].min()
        min_stocks = filtered[filtered['Count'] == min_count]
        print(f"\n  หุ้นที่ Count น้อยที่สุด ({min_count}):")
        for _, row in min_stocks.iterrows():
            symbol = str(row['symbol'])
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            count = int(row.get('Count', 0))
            print(f"    - {symbol}: Raw={raw_count}, Elite={elite_count}, Count={count}")
    
    # วิเคราะห์ว่าควรใช้ Raw_Count หรือ Elite_Count
    print("\n" + "=" * 160)
    print("คำแนะนำ:")
    print("=" * 160)
    print("""
1. Count ที่แสดงคือ Elite_Count (สำหรับหุ้นที่ไม่ใช่ China/HK)
   - Elite_Count = จำนวน trades ที่ผ่าน Elite Filter (Prob > 55%)
   - Raw_Count = จำนวน trades ทั้งหมด

2. ปัญหา:
   - Elite_Count อาจจะน้อยกว่า Raw_Count มาก
   - ทำให้ดูเหมือน Count น้อย แต่จริงๆ มีข้อมูลมากกว่า

3. ทางเลือก:
   a) ใช้ Raw_Count แทน Elite_Count (จะได้ Count สูงขึ้น)
   b) ลดเกณฑ์ Count min (เช่น จาก 30 → 20 สำหรับไทย)
   c) ใช้ Raw_Count สำหรับหุ้นที่ Elite_Count < 30

4. สำหรับ China/HK:
   - ใช้ Raw_Count เสมอ (ตาม V13.6 logic)
   - ไม่มีปัญหา Count น้อย
    """)
    print("=" * 160)

if __name__ == "__main__":
    analyze_count_issue()

