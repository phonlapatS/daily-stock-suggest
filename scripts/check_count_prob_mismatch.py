#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบปัญหา Count กับ Prob% ไม่สอดคล้องกัน
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

def check_count_prob_mismatch():
    """ตรวจสอบปัญหา Count กับ Prob% ไม่สอดคล้องกัน"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("ตรวจสอบปัญหา Count กับ Prob% ไม่สอดคล้องกัน")
    print("=" * 160)
    
    # หาหุ้นที่ Count สูงมาก (> 1000)
    high_count = df[df['Count'] > 1000].sort_values('Count', ascending=False)
    
    if not high_count.empty:
        print(f"\nหุ้นที่ Count > 1000 ({len(high_count)} หุ้น):")
        print(f"{'Symbol':<12} {'Country':<8} {'Raw_Prob%':>12} {'Elite_Prob%':>14} {'Prob%':>8} {'Raw_Count':>12} {'Elite_Count':>14} {'Count':>8} {'ปัญหา':<30}")
        print("-" * 160)
        
        for _, row in high_count.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            raw_prob = row.get('Raw_Prob%', 0.0)
            elite_prob = row.get('Elite_Prob%', 0.0)
            prob = row.get('Prob%', 0.0)
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            count = int(row.get('Count', 0))
            
            # ตรวจสอบปัญหา
            issues = []
            if prob == elite_prob and count == raw_count and elite_count > 0:
                issues.append("Prob% มาจาก Elite แต่ Count มาจาก Raw")
            if count > raw_count * 1.1:  # Count มากกว่า Raw Count 10%
                issues.append("Count ผิดปกติ")
            if prob > raw_prob * 1.2:  # Prob% มากกว่า Raw Prob% 20%
                issues.append("Prob% สูงกว่า Raw Prob% มาก")
            
            issue_str = ", ".join(issues) if issues else "✅ OK"
            print(f"{symbol:<12} {country:<8} {raw_prob:>11.1f}% {elite_prob:>13.1f}% {prob:>7.1f}% {raw_count:>12} {elite_count:>14} {count:>8} {issue_str}")
    
    # ตรวจสอบหุ้นที่ Prob% สูงแต่ Count เยอะมาก
    print("\n" + "=" * 160)
    print("หุ้นที่ Prob% >= 70% และ Count > 500 (ดูเวอร์):")
    print("-" * 160)
    
    weird = df[
        (df['Prob%'] >= 70.0) &
        (df['Count'] > 500)
    ].sort_values('Count', ascending=False)
    
    if not weird.empty:
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'Count':>8} {'Raw_Prob%':>12} {'Elite_Prob%':>14} {'Elite_Count':>14} {'อธิบาย':<40}")
        print("-" * 160)
        
        for _, row in weird.iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            count = int(row.get('Count', 0))
            raw_prob = row.get('Raw_Prob%', 0.0)
            elite_prob = row.get('Elite_Prob%', 0.0)
            elite_count = int(row.get('Elite_Count', 0))
            
            # อธิบาย
            if prob == elite_prob and count == raw_count:
                explanation = f"Prob {prob:.1f}% มาจาก Elite ({elite_count} trades) แต่ Count แสดง Raw ({count})"
            elif prob == elite_prob:
                explanation = f"Prob {prob:.1f}% มาจาก Elite ({elite_count} trades)"
            else:
                explanation = f"Prob {prob:.1f}% มาจาก Raw"
            
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {count:>8} {raw_prob:>11.1f}% {elite_prob:>13.1f}% {elite_count:>14} {explanation}")
    else:
        print("ไม่พบหุ้นที่ Prob% >= 70% และ Count > 500")
    
    # วิเคราะห์ปัญหา
    print("\n" + "=" * 160)
    print("วิเคราะห์ปัญหา:")
    print("=" * 160)
    print("""
ปัญหา: Count กับ Prob% ไม่สอดคล้องกัน

ตัวอย่าง ILMN:
  - Prob%: 77.4% (Elite Prob% - มาจาก Elite Count 62 trades)
  - Count: 3,112 (Raw Count - มาจาก Raw Count 3,112 trades)
  
  → Prob 77.4% มาจาก Elite trades 62 ตัว แต่ Count แสดง Raw trades 3,112 ตัว
  → ไม่สอดคล้องกัน! ดูเหมือน Prob สูงมากแต่ Count ก็เยอะมาก

ทางแก้:
  1. ใช้ Elite Count เมื่อใช้ Elite Prob% (จะได้ Count 62 แทน 3,112)
  2. หรือใช้ Raw Count + Raw Prob% (จะได้ Prob 58.5% แทน 77.4%)
  3. หรือใช้ Elite Count + Elite Prob% สำหรับหุ้นที่ Elite Count >= 30

แนะนำ: ใช้ Elite Count เมื่อใช้ Elite Prob% เพื่อให้สอดคล้องกัน
    """)
    print("=" * 160)

if __name__ == "__main__":
    check_count_prob_mismatch()

