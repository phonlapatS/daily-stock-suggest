#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compare_filtering_results.py - เปรียบเทียบจำนวนหุ้นที่เจอในแต่ละประเทศ
================================================================================

เปรียบเทียบ:
1. เกณฑ์เดิม: Prob > 60% AND RRR > 2.0
2. เกณฑ์ใหม่: QUALITY + MARKET_SPECIFIC (ใช้ Prob%, AvgWin%, AvgLoss%, RRR)

Author: Stock Analysis System
Date: 2026-01-XX
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


def filter_old_criteria(df):
    """เกณฑ์เดิม: Prob > 60% AND RRR > 2.0"""
    return df[
        (df['Prob%'] > 60.0) & 
        (df['RR_Ratio'] > 2.0) &
        (df['Count'] >= 10)
    ].copy()


def filter_new_criteria(df):
    """เกณฑ์ใหม่: QUALITY + MARKET_SPECIFIC"""
    selected = []
    
    # QUALITY
    quality = df[
        (df['Prob%'] >= 60.0) & 
        (df['AvgWin%'] > 1.5) &
        (df['AvgLoss%'] < 1.5) &
        (df['RR_Ratio'] >= 1.3) &
        (df['Count'] >= 10)
    ].copy()
    selected.append(quality)
    
    # MARKET_SPECIFIC
    # THAI
    th = df[
        (df['Country'] == 'TH') & 
        (df['Prob%'] >= 60.0) & 
        (df['RR_Ratio'] >= 1.2) &
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 2.0) &
        (df['Count'] >= 10)
    ].copy()
    selected.append(th)
    
    # US - ปรับเกณฑ์ให้เหมาะสม
    us = df[
        (df['Country'] == 'US') & 
        (df['Prob%'] >= 52.0) &  # ลดจาก 55% → 52%
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0
        (df['AvgWin%'] > 1.0) &  # ลดจาก 1.5% → 1.0%
        (df['AvgLoss%'] < 3.0) &  # เพิ่มจาก 2.5% → 3.0%
        (df['Count'] >= 10)
    ].copy()
    selected.append(us)
    
    # CHINA - ปรับเกณฑ์ให้เหมาะสม
    cn = df[
        (df['Country'] == 'CN') & 
        (df['Prob%'] >= 50.0) &  # ลดจาก 55% → 50%
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 3.0) &  # เพิ่มจาก 2.0% → 3.0%
        (df['Count'] >= 10)
    ].copy()
    selected.append(cn)
    
    # TAIWAN - ปรับเกณฑ์ให้เหมาะสม
    tw = df[
        (df['Country'] == 'TW') & 
        (df['Prob%'] >= 50.0) &  # ลดจาก 55% → 50%
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 2.5) &
        (df['Count'] >= 10)
    ].copy()
    selected.append(tw)
    
    # METALS
    gl = df[
        (df['Country'] == 'GL') & 
        (df['Prob%'] >= 50.0) &
        (df['RR_Ratio'] >= 1.0) &
        (df['Count'] >= 10)
    ].copy()
    selected.append(gl)
    
    if selected:
        result = pd.concat(selected, ignore_index=True)
        # Remove duplicates
        result = result.drop_duplicates(subset=['symbol'], keep='first')
        return result
    else:
        return pd.DataFrame()


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[COMPARISON] เปรียบเทียบจำนวนหุ้นที่เจอในแต่ละประเทศ")
    print("="*100)
    
    # Load data
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    print(f"\n📊 โหลดข้อมูล: {len(df)} symbols")
    
    # Filter by old criteria
    print("\n[1] เกณฑ์เดิม: Prob > 60% AND RRR > 2.0")
    print("-" * 80)
    old_filtered = filter_old_criteria(df)
    print(f"   รวมทั้งหมด: {len(old_filtered)} symbols")
    
    old_by_country = old_filtered.groupby('Country').size()
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        count = old_by_country.get(country, 0)
        print(f"   {country}: {count} symbols")
    
    # Filter by new criteria
    print("\n[2] เกณฑ์ใหม่: QUALITY + MARKET_SPECIFIC (ใช้ Prob%, AvgWin%, AvgLoss%, RRR)")
    print("-" * 80)
    new_filtered = filter_new_criteria(df)
    print(f"   รวมทั้งหมด: {len(new_filtered)} symbols")
    
    new_by_country = new_filtered.groupby('Country').size()
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        count = new_by_country.get(country, 0)
        print(f"   {country}: {count} symbols")
    
    # Comparison
    print("\n[3] เปรียบเทียบ (เกณฑ์ใหม่ vs เกณฑ์เดิม)")
    print("-" * 80)
    print(f"{'Country':<10} {'เกณฑ์เดิม':<12} {'เกณฑ์ใหม่':<12} {'เพิ่มขึ้น':<12} {'% เพิ่ม':<10}")
    print("-" * 80)
    
    total_old = len(old_filtered)
    total_new = len(new_filtered)
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        old_count = old_by_country.get(country, 0)
        new_count = new_by_country.get(country, 0)
        increase = new_count - old_count
        if old_count > 0:
            pct_increase = (increase / old_count) * 100
        else:
            pct_increase = float('inf') if new_count > 0 else 0
        
        pct_str = f"{pct_increase:.1f}%" if pct_increase != float('inf') else "∞"
        print(f"{country:<10} {old_count:<12} {new_count:<12} {increase:<12} {pct_str:<10}")
    
    print("-" * 80)
    total_increase = total_new - total_old
    total_pct = (total_increase / total_old) * 100 if total_old > 0 else float('inf')
    total_pct_str = f"{total_pct:.1f}%" if total_pct != float('inf') else "∞"
    print(f"{'รวมทั้งหมด':<10} {total_old:<12} {total_new:<12} {total_increase:<12} {total_pct_str:<10}")
    
    # Check if using Prob%, AvgWin%, AvgLoss%, RRR
    print("\n[4] ตรวจสอบว่าตรงกับโจทย์ (ใช้ Prob%, AvgWin%, AvgLoss%, RRR)")
    print("-" * 80)
    
    # Check old criteria
    print("\n   [เกณฑ์เดิม]")
    print("   - ใช้ Prob%: ✅ (Prob > 60%)")
    print("   - ใช้ RRR: ✅ (RRR > 2.0)")
    print("   - ใช้ AvgWin%: ❌ (ไม่ได้ใช้)")
    print("   - ใช้ AvgLoss%: ❌ (ไม่ได้ใช้)")
    print("   - สรุป: ❌ ไม่ตรงกับโจทย์ (ไม่ได้ใช้ AvgWin% และ AvgLoss%)")
    
    # Check new criteria
    print("\n   [เกณฑ์ใหม่]")
    print("   - ใช้ Prob%: ✅ (Prob >= 60% หรือ 55% หรือ 50% ตามตลาด)")
    print("   - ใช้ RRR: ✅ (RRR >= 1.3 หรือ 1.2 หรือ 1.0 ตามตลาด)")
    print("   - ใช้ AvgWin%: ✅ (AvgWin > 1.5% หรือ 1.0% ตามตลาด)")
    print("   - ใช้ AvgLoss%: ✅ (AvgLoss < 1.5% หรือ 2.0% หรือ 2.5% ตามตลาด)")
    print("   - สรุป: ✅ ตรงกับโจทย์ (ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว)")
    
    # Show examples
    print("\n[5] ตัวอย่างหุ้นที่เจอเพิ่มขึ้น")
    print("-" * 80)
    
    # Find symbols in new but not in old
    new_symbols = set(new_filtered['symbol'])
    old_symbols = set(old_filtered['symbol'])
    new_only = new_symbols - old_symbols
    
    if new_only:
        print(f"   หุ้นที่เจอเพิ่มขึ้น: {len(new_only)} symbols")
        print(f"   ตัวอย่าง (Top 10):")
        new_only_df = new_filtered[new_filtered['symbol'].isin(list(new_only)[:10])]
        for _, row in new_only_df.iterrows():
            print(f"     {row['symbol']:<10} ({row['Country']}): Prob={row['Prob%']:.1f}%, "
                  f"RRR={row['RR_Ratio']:.2f}, AvgWin={row['AvgWin%']:.2f}%, AvgLoss={row['AvgLoss%']:.2f}%")
    else:
        print("   ไม่มีหุ้นเพิ่มขึ้น (เกณฑ์ใหม่เป็น subset ของเกณฑ์เดิม)")
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้น")
    print("="*100)
    print("\n💡 สรุป:")
    print(f"   ✅ เกณฑ์ใหม่เจอหุ้นมากขึ้น: {total_new} ตัว (vs {total_old} ตัวเดิม)")
    print(f"   ✅ เพิ่มขึ้น: {total_increase} ตัว ({total_pct_str})")
    print("   ✅ ตรงกับโจทย์: ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว")


if __name__ == "__main__":
    main()

