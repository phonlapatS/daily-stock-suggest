#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimal_filtering_logic.py - Logic Engine ที่เหมาะสมและตรงกับความต้องการของระบบ
================================================================================

ใช้ Prob%, AvgWin%, AvgLoss%, RRR ตามที่ Mentor ต้องการ
และเลือกเกณฑ์ที่เหมาะสมกับระบบ:

1. QUALITY (คุณภาพดี) - ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว
2. MARKET_SPECIFIC (ตามตลาด) - ปรับเกณฑ์ตามลักษณะของแต่ละตลาด

Author: Stock Analysis System
Date: 2026-01-XX
"""

import pandas as pd
import numpy as np
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
OUTPUT_FILE = os.path.join(DATA_DIR, "optimal_symbol_selection.csv")


def filter_by_quality_criteria(df):
    """
    เกณฑ์ QUALITY: ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว
    เหมาะกับ: หุ้นที่มีคุณภาพดีทุกด้าน
    """
    filtered = df[
        (df['Prob%'] >= 60.0) & 
        (df['AvgWin%'] > 1.5) &
        (df['AvgLoss%'] < 1.5) &
        (df['RR_Ratio'] >= 1.3) &
        (df['Count'] >= 10)
    ].copy()
    filtered['Filter_Type'] = 'QUALITY'
    filtered['Priority'] = 1  # ความสำคัญสูงสุด
    return filtered


def filter_by_market_specific(df):
    """
    เกณฑ์ MARKET_SPECIFIC: ปรับตามลักษณะของแต่ละตลาด
    ใช้ Prob%, AvgWin%, AvgLoss%, RRR ตามที่ Mentor ต้องการ
    """
    selected = []
    
    # THAI - Mean Reversion → เน้น Prob และ AvgWin (ชนะบ่อย, กำไรดี)
    # สอดคล้องกับระบบ: Prob >= 60% AND RRR >= 1.2
    th = df[
        (df['Country'] == 'TH') & 
        (df['Prob%'] >= 60.0) & 
        (df['RR_Ratio'] >= 1.2) &
        (df['AvgWin%'] > 1.0) &  # กำไรเฉลี่ยดี
        (df['AvgLoss%'] < 2.0) &  # ขาดทุนเฉลี่ยไม่มาก
        (df['Count'] >= 10)
    ].copy()
    th['Filter_Type'] = 'THAI_MARKET'
    th['Priority'] = 2
    selected.append(th)
    
    # US - Trend Following → เน้น RRR และ AvgWin (กำไรมาก, ความเสี่ยงต่ำ)
    # ปรับเกณฑ์: Prob Mean=52.1%, RRR Mean=1.01 → ลด Prob และ RRR requirement
    us = df[
        (df['Country'] == 'US') & 
        (df['Prob%'] >= 52.0) &  # ลดจาก 55% → 52% (เพราะ Trend Following มี Prob ต่ำ)
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0 (เพราะ US มี RRR ต่ำ)
        (df['AvgWin%'] > 1.0) &  # ลดจาก 1.5% → 1.0% (เพราะ US มี AvgWin ต่ำ)
        (df['AvgLoss%'] < 3.0) &  # เพิ่มจาก 2.5% → 3.0% (เพราะ US มี AvgLoss สูง)
        (df['Count'] >= 10)
    ].copy()
    us['Filter_Type'] = 'US_MARKET'
    us['Priority'] = 2
    selected.append(us)
    
    # CHINA - Mean Reversion → เน้น Prob
    # ปรับเกณฑ์: Prob Mean=54.0%, RRR Mean=1.02, AvgLoss Mean=2.89% → ลด Prob, RRR, เพิ่ม AvgLoss
    cn = df[
        (df['Country'] == 'CN') & 
        (df['Prob%'] >= 50.0) &  # ลดจาก 55% → 50% (เพราะ CN มี Prob ต่ำ)
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0 (เพราะ CN มี RRR ต่ำ)
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 3.0) &  # เพิ่มจาก 2.0% → 3.0% (เพราะ CN มี AvgLoss สูง)
        (df['Count'] >= 10)
    ].copy()
    cn['Filter_Type'] = 'CHINA_MARKET'
    cn['Priority'] = 2
    selected.append(cn)
    
    # TAIWAN - Trend Following → เน้น RRR
    # ปรับเกณฑ์: Prob Mean=51.5%, RRR Mean=1.14 → ลด Prob และ RRR requirement
    tw = df[
        (df['Country'] == 'TW') & 
        (df['Prob%'] >= 50.0) &  # ลดจาก 55% → 50% (เพราะ TW มี Prob ต่ำ)
        (df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0 (เพราะ TW มี RRR ต่ำ)
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 2.5) &
        (df['Count'] >= 10)
    ].copy()
    tw['Filter_Type'] = 'TAIWAN_MARKET'
    tw['Priority'] = 2
    selected.append(tw)
    
    # METALS - Mean Reversion
    # สอดคล้องกับระบบ: Prob >= 50%
    gl = df[
        (df['Country'] == 'GL') & 
        (df['Prob%'] >= 50.0) &
        (df['RR_Ratio'] >= 1.0) &
        (df['Count'] >= 10)
    ].copy()
    gl['Filter_Type'] = 'METALS_MARKET'
    gl['Priority'] = 2
    selected.append(gl)
    
    if selected:
        result = pd.concat(selected, ignore_index=True)
        return result
    else:
        return pd.DataFrame()


def calculate_mentor_score(df):
    """
    Mentor Score: ใช้ Prob%, AvgWin%, AvgLoss%, RRR
    สูตร: Score = (Prob% × 0.4) + (RRR × 15) + (AvgWin% × 2) - (AvgLoss% × 2)
    """
    df = df.copy()
    df['Mentor_Score'] = (
        df['Prob%'] * 0.4 + 
        df['RR_Ratio'] * 15 + 
        df['AvgWin%'] * 2 - 
        df['AvgLoss%'] * 2
    )
    return df


def calculate_risk_management(df):
    """
    Risk Management: ใช้ AvgWin% และ AvgLoss%
    """
    df = df.copy()
    
    # Stop Loss = AvgLoss% × 1.5 (เผื่อความผันผวน)
    df['Stop_Loss_Pct'] = df['AvgLoss%'] * 1.5
    
    # Take Profit = AvgWin% × 0.8 (รับกำไรก่อน)
    df['Take_Profit_Pct'] = df['AvgWin%'] * 0.8
    
    # Position Size ตาม Prob% และ RRR
    base_size = 1.0  # Base = 1% ของพอร์ต
    df['Prob_Factor'] = df['Prob%'] / 60.0
    df['RRR_Factor'] = df['RR_Ratio'] / 2.0
    
    # Combined factor
    df['Position_Size_Factor'] = df['Prob_Factor'] * df['RRR_Factor']
    
    # Normalize to max 3x
    max_factor = df['Position_Size_Factor'].max()
    if max_factor > 0:
        df['Position_Size_Pct'] = (df['Position_Size_Factor'] / max_factor) * 3.0 * base_size
    else:
        df['Position_Size_Pct'] = base_size
    
    # Cap at 5% per stock
    df['Position_Size_Pct'] = df['Position_Size_Pct'].clip(upper=5.0)
    
    return df


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[OPTIMAL FILTERING] Logic Engine ที่เหมาะสมและตรงกับความต้องการของระบบ")
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
    
    # Filter by QUALITY (Priority 1)
    print("\n[1] กรองหุ้นตามเกณฑ์ QUALITY (ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว)")
    print("-" * 80)
    quality = filter_by_quality_criteria(df)
    print(f"   QUALITY: Prob >= 60% AND AvgWin > 1.5% AND AvgLoss < 1.5% AND RRR >= 1.3")
    print(f"   ผลลัพธ์: {len(quality)} symbols")
    
    # Filter by MARKET_SPECIFIC (Priority 2)
    print("\n[2] กรองหุ้นตามตลาด (ปรับเกณฑ์ตามลักษณะของแต่ละตลาด)")
    print("-" * 80)
    market = filter_by_market_specific(df)
    print(f"   THAI: Prob >= 60% AND RRR >= 1.2 AND AvgWin > 1.0% AND AvgLoss < 2.0%")
    print(f"   US: Prob >= 52% AND RRR >= 1.0 AND AvgWin > 1.0% AND AvgLoss < 3.0%")
    print(f"   CHINA: Prob >= 50% AND RRR >= 1.0 AND AvgWin > 1.0% AND AvgLoss < 3.0%")
    print(f"   TAIWAN: Prob >= 50% AND RRR >= 1.0 AND AvgWin > 1.0% AND AvgLoss < 2.5%")
    print(f"   METALS: Prob >= 50% AND RRR >= 1.0")
    print(f"   ผลลัพธ์: {len(market)} symbols")
    
    # Combine (Priority: QUALITY first, then MARKET_SPECIFIC)
    print("\n[3] รวมผลลัพธ์ (QUALITY มี Priority สูงสุด)")
    print("-" * 80)
    
    # Start with QUALITY
    combined = quality.copy()
    
    # Add MARKET_SPECIFIC that's not in QUALITY
    if not market.empty:
        market_only = market[~market['symbol'].isin(combined['symbol'])]
        if not market_only.empty:
            combined = pd.concat([combined, market_only], ignore_index=True)
    
    print(f"   QUALITY: {len(quality)} symbols")
    print(f"   MARKET_SPECIFIC (ไม่ซ้ำ): {len(market[~market['symbol'].isin(quality['symbol'])])} symbols")
    print(f"   รวมทั้งหมด: {len(combined)} symbols")
    
    # Calculate Mentor Score
    combined = calculate_mentor_score(combined)
    
    # Add risk management
    combined = calculate_risk_management(combined)
    
    # Sort by Priority, then Mentor Score
    combined = combined.sort_values(['Priority', 'Mentor_Score'], ascending=[True, False])
    
    # Save results
    output_cols = [
        'symbol', 'Country', 'Filter_Type', 'Priority',
        'Prob%', 'AvgWin%', 'AvgLoss%', 'RR_Ratio',
        'Count', 'Mentor_Score',
        'Position_Size_Pct', 'Stop_Loss_Pct', 'Take_Profit_Pct'
    ]
    
    available_cols = [col for col in output_cols if col in combined.columns]
    combined_output = combined[available_cols].copy()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    combined_output.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n💾 บันทึกผลลัพธ์: {OUTPUT_FILE}")
    
    # Print summary
    print("\n" + "="*100)
    print("[SUMMARY] สรุปผลลัพธ์")
    print("="*100)
    
    print("\n[Top 20 หุ้นที่ดีที่สุด (QUALITY + MARKET_SPECIFIC)]")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Country':<6} {'Filter':<15} {'Priority':<8} {'Prob%':>6} {'AvgWin%':>8} {'AvgLoss%':>9} {'RRR':>5} {'Score':>7}")
    print("-" * 80)
    
    top20 = combined.head(20)
    for _, row in top20.iterrows():
        print(f"{row['symbol']:<10} {row['Country']:<6} {row['Filter_Type']:<15} "
              f"{int(row['Priority']):<8} {row['Prob%']:>5.1f}% {row['AvgWin%']:>7.2f}% "
              f"{row['AvgLoss%']:>8.2f}% {row['RR_Ratio']:>4.2f} {row['Mentor_Score']:>6.1f}")
    
    # Statistics by filter type
    print("\n[สถิติตาม Filter Type]")
    print("-" * 80)
    for filter_type in combined['Filter_Type'].unique():
        filtered = combined[combined['Filter_Type'] == filter_type]
        print(f"\n   [{filter_type}] {len(filtered)} symbols")
        if not filtered.empty:
            print(f"      Prob%: Mean={filtered['Prob%'].mean():.1f}%, Min={filtered['Prob%'].min():.1f}%, Max={filtered['Prob%'].max():.1f}%")
            print(f"      RRR: Mean={filtered['RR_Ratio'].mean():.2f}, Min={filtered['RR_Ratio'].min():.2f}, Max={filtered['RR_Ratio'].max():.2f}")
            print(f"      AvgWin%: Mean={filtered['AvgWin%'].mean():.2f}%, Max={filtered['AvgWin%'].max():.2f}%")
            print(f"      AvgLoss%: Mean={filtered['AvgLoss%'].mean():.2f}%, Max={filtered['AvgLoss%'].max():.2f}%")
    
    # Statistics by country
    print("\n[สถิติตามประเทศ]")
    print("-" * 80)
    for country in sorted(combined['Country'].unique()):
        country_df = combined[combined['Country'] == country]
        print(f"\n   [{country}] {len(country_df)} symbols")
        if not country_df.empty:
            print(f"      Prob%: Mean={country_df['Prob%'].mean():.1f}%")
            print(f"      RRR: Mean={country_df['RR_Ratio'].mean():.2f}")
            print(f"      AvgWin%: Mean={country_df['AvgWin%'].mean():.2f}%")
            print(f"      AvgLoss%: Mean={country_df['AvgLoss%'].mean():.2f}%")
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้น")
    print("="*100)
    print("\n💡 สรุป:")
    print("   ✅ ใช้ Prob%, AvgWin%, AvgLoss%, RRR ตามที่ Mentor ต้องการ")
    print("   ✅ เกณฑ์ QUALITY: ใช้ครบทุกตัว (Priority 1)")
    print("   ✅ เกณฑ์ MARKET_SPECIFIC: ปรับตามตลาด (Priority 2)")
    print("   ✅ สอดคล้องกับระบบปัจจุบัน (calculate_metrics.py)")
    print("   ✅ มี Mentor Score และ Risk Management")


if __name__ == "__main__":
    main()

