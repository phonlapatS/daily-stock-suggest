#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบว่าทำไมบางหุ้น Raw Prob% = Elite Prob%
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

def check_raw_vs_elite_prob():
    """ตรวจสอบว่าทำไมบางหุ้น Raw Prob% = Elite Prob%"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("ตรวจสอบ: ทำไมบางหุ้น Raw Prob% = Elite Prob%?")
    print("=" * 160)
    
    # หาหุ้นที่ผ่านเกณฑ์ปัจจุบัน
    criteria = {
        'TH': {'prob': 60.0, 'rrr': 1.3, 'count': 30},
        'US': {'prob': 60.0, 'rrr': 1.5, 'count': 15},
        'CN': {'prob': 60.0, 'rrr': 1.5, 'count': 20},
        'TW': {'prob': 60.0, 'rrr': 1.25, 'count': 25},
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
        print(f"{country_name} - เปรียบเทียบ Raw Prob% vs Elite Prob%")
        print("=" * 160)
        print(f"{'Symbol':<12} {'Raw_Prob%':>12} {'Elite_Prob%':>14} {'Prob%':>8} {'Raw_Count':>12} {'Elite_Count':>14} {'Count':>8} {'เหตุผล':<40}")
        print("-" * 160)
        
        for _, row in filtered.sort_values('Prob%', ascending=False).iterrows():
            symbol = str(row['symbol'])
            raw_prob = row.get('Raw_Prob%', 0.0)
            elite_prob = row.get('Elite_Prob%', 0.0)
            prob = row.get('Prob%', 0.0)
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            count = int(row.get('Count', 0))
            
            # ตรวจสอบเหตุผล
            if abs(raw_prob - elite_prob) < 0.1:
                reason = "Raw Prob% ≈ Elite Prob% (เหมือนกัน)"
            elif elite_count == 0:
                reason = "Elite Count = 0 (ไม่มี Elite trades)"
            elif elite_count == raw_count:
                reason = "Elite Count = Raw Count (ทุก trades เป็น Elite)"
            elif elite_count >= raw_count * 0.9:
                reason = f"Elite Count ≈ Raw Count ({elite_count}/{raw_count})"
            else:
                diff = raw_prob - elite_prob
                reason = f"Raw Prob% < Elite Prob% ({diff:+.1f}%)"
            
            print(f"{symbol:<12} {raw_prob:>11.1f}% {elite_prob:>13.1f}% {prob:>7.1f}% {raw_count:>12} {elite_count:>14} {count:>8} {reason}")
        
        # สรุป
        print("\n" + "-" * 160)
        same_count = len(filtered[abs(filtered['Raw_Prob%'] - filtered['Elite_Prob%']) < 0.1])
        different_count = len(filtered) - same_count
        
        print(f"สรุป:")
        print(f"  Raw Prob% ≈ Elite Prob%: {same_count} หุ้น")
        print(f"  Raw Prob% ≠ Elite Prob%: {different_count} หุ้น")
        
        if same_count > 0:
            print(f"\n  หุ้นที่ Raw Prob% ≈ Elite Prob%:")
            same_stocks = filtered[abs(filtered['Raw_Prob%'] - filtered['Elite_Prob%']) < 0.1]
            for _, row in same_stocks.iterrows():
                symbol = str(row['symbol'])
                raw_prob = row.get('Raw_Prob%', 0.0)
                elite_prob = row.get('Elite_Prob%', 0.0)
                raw_count = int(row.get('Raw_Count', 0))
                elite_count = int(row.get('Elite_Count', 0))
                
                if elite_count == 0:
                    print(f"    - {symbol}: Elite Count = 0 → ใช้ Raw Prob%")
                elif elite_count == raw_count:
                    print(f"    - {symbol}: Elite Count = Raw Count ({elite_count}) → ทุก trades เป็น Elite")
                elif elite_count >= raw_count * 0.9:
                    print(f"    - {symbol}: Elite Count ≈ Raw Count ({elite_count}/{raw_count}) → เกือบทุก trades เป็น Elite")
                else:
                    print(f"    - {symbol}: Raw Prob% = {raw_prob:.1f}%, Elite Prob% = {elite_prob:.1f}% (ใกล้เคียง)")
    
    print("\n" + "=" * 160)
    print("สรุป:")
    print("=" * 160)
    print("""
ทำไมบางหุ้น Raw Prob% = Elite Prob%?

1. Elite Count = 0:
   - ไม่มี trades ที่ Prob >= 60%
   - ใช้ Raw Prob% แทน Elite Prob%
   - → Raw Prob% = Elite Prob% (เพราะ Elite Prob% = 0)

2. Elite Count = Raw Count:
   - ทุก trades เป็น Elite (Prob >= 60%)
   - → Raw Prob% = Elite Prob%

3. Elite Count ≈ Raw Count:
   - เกือบทุก trades เป็น Elite
   - → Raw Prob% ≈ Elite Prob%

4. Elite Count < Raw Count:
   - มี trades ที่ไม่ใช่ Elite
   - → Raw Prob% < Elite Prob% (ปกติ)
    """)
    print("=" * 160)

if __name__ == "__main__":
    check_raw_vs_elite_prob()

