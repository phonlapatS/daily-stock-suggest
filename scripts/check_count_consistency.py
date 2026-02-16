#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบว่า Count ลดลงหรือไม่ เมื่อกรองด้วย Prob >= 60%, Count >= 30
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

def check_count_consistency():
    """ตรวจสอบ Count consistency"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    # กรองตามเกณฑ์
    filtered = df[
        (df['Prob%'] >= 60.0) &
        (df['Count'] >= 30)
    ].copy()
    
    print("\n" + "=" * 160)
    print("ตรวจสอบ Count Consistency (Prob >= 60%, Count >= 30)")
    print("=" * 160)
    
    print("\nเปรียบเทียบ Raw_Count vs Elite_Count vs Count_Used:")
    print("-" * 160)
    print(f"{'Symbol':<12} {'Country':<8} {'Raw_Count':>10} {'Elite_Count':>12} {'Count_Used':>12} {'Count':>8} {'Prob%':>8} {'RRR':>8}")
    print("-" * 160)
    
    # แสดง Top 20 เพื่อตรวจสอบ
    top_20 = filtered.head(20).sort_values('RRR_Distance_From_2', errors='ignore') if 'RRR_Distance_From_2' in filtered.columns else filtered.head(20)
    
    for _, row in top_20.iterrows():
        symbol = str(row['symbol'])
        country = str(row.get('Country', 'N/A'))
        raw_count = int(row.get('Raw_Count', 0))
        elite_count = int(row.get('Elite_Count', 0))
        count_used = int(row.get('Count_Used', 0))
        count = int(row.get('Count', 0))
        prob = row.get('Prob%', 0.0)
        rrr = row.get('RR_Ratio', 0.0)
        
        # ตรวจสอบว่า Count ถูกต้องหรือไม่
        if count_used > 0:
            count_check = "✓" if count == count_used else "✗"
        else:
            count_check = "?"
        
        print(f"{symbol:<12} {country:<8} {raw_count:>10} {elite_count:>12} {count_used:>12} {count:>8} {count_check} {prob:>7.1f}% {rrr:>7.2f}")
    
    print("-" * 160)
    
    # สรุปสถิติ
    print("\n" + "=" * 160)
    print("สรุปสถิติ Count:")
    print("-" * 160)
    
    print(f"\nTotal หุ้นที่ผ่านเกณฑ์: {len(filtered)}")
    print(f"  - ใช้ Elite_Count: {len(filtered[filtered['Elite_Count'] >= 5])} หุ้น")
    print(f"  - ใช้ Raw_Count: {len(filtered[filtered['Elite_Count'] < 5])} หุ้น")
    
    # สำหรับ China/HK
    china_hk = filtered[(filtered['Country'] == 'CN') | (filtered['Country'] == 'HK')]
    if not china_hk.empty:
        print(f"\nChina/HK ({len(china_hk)} หุ้น):")
        print(f"  - ใช้ Raw_Count เสมอ (ตาม V13.6 logic)")
        for _, row in china_hk.iterrows():
            print(f"     {row['symbol']}: Raw_Count={int(row['Raw_Count'])}, Count={int(row['Count'])}")
    
    # ตรวจสอบหุ้นที่ Count ลดลงมาก
    print("\n" + "=" * 160)
    print("หุ้นที่ Raw_Count มากกว่า Count มาก (อาจมีการกรอง):")
    print("-" * 160)
    
    filtered['Count_Diff'] = filtered['Raw_Count'] - filtered['Count']
    high_diff = filtered[filtered['Count_Diff'] > 50].sort_values('Count_Diff', ascending=False).head(10)
    
    if not high_diff.empty:
        print(f"{'Symbol':<12} {'Country':<8} {'Raw_Count':>10} {'Elite_Count':>12} {'Count':>8} {'Diff':>8} {'Prob%':>8}")
        print("-" * 160)
        for _, row in high_diff.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            count = int(row.get('Count', 0))
            diff = int(row['Count_Diff'])
            prob = row.get('Prob%', 0.0)
            print(f"{symbol:<12} {country:<8} {raw_count:>10} {elite_count:>12} {count:>8} {diff:>8} {prob:>7.1f}%")
    else:
        print("  ไม่มีหุ้นที่ Count ลดลงมาก")
    
    print("\n" + "=" * 160)
    print("อธิบาย:")
    print("  - Raw_Count: จำนวน trades ทั้งหมด (ไม่มีการกรอง)")
    print("  - Elite_Count: จำนวน trades ที่ผ่าน Elite Filter (Prob > 55%)")
    print("  - Count_Used: Count ที่ใช้จริง (Elite_Count ถ้า >= 5, ไม่งั้นใช้ Raw_Count)")
    print("  - Count: Count ที่แสดงในตาราง (มาจาก Count_Used)")
    print("  - China/HK: ใช้ Raw_Count เสมอ (ตาม V13.6 logic)")
    print("=" * 160)

if __name__ == "__main__":
    check_count_consistency()

