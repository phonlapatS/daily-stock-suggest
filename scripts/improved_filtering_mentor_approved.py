#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
improved_filtering_mentor_approved.py - Logic Engine ที่ใช้ Prob%, AvgWin%, AvgLoss%, RRR
================================================================================

ใช้ตามที่ Mentor ต้องการ:
- Prob% (Win Rate)
- AvgWin% (Average Win Percentage)
- AvgLoss% (Average Loss Percentage)
- RRR (Risk-Reward Ratio = AvgWin% / AvgLoss%)

ปรับปรุงจาก:
- เกณฑ์เดิม: Prob > 60% AND RRR > 2.0 (เข้มงวดเกินไป → 3 หุ้น)
เป็น:
- หลายเกณฑ์ที่ใช้ Prob%, AvgWin%, AvgLoss%, RRR ตามที่ Mentor ต้องการ

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
OUTPUT_FILE = os.path.join(DATA_DIR, "mentor_approved_symbol_selection.csv")


def filter_by_strict_criteria(df):
    """เกณฑ์ Strict: Prob > 60% AND RRR > 2.0 (ตามที่ Mentor ต้องการ)"""
    filtered = df[
        (df['Prob%'] > 60.0) & 
        (df['RR_Ratio'] > 2.0) &
        (df['Count'] >= 10)  # ต้องมี sample size เพียงพอ
    ].copy()
    filtered['Filter_Type'] = 'STRICT'
    return filtered


def filter_by_balanced_criteria(df):
    """เกณฑ์ Balanced: ใช้ Prob%, AvgWin%, AvgLoss%, RRR แบบสมดุล"""
    # เกณฑ์: Prob >= 58% AND RRR >= 1.5 AND AvgWin > 1.5% AND AvgLoss < 2.0%
    filtered = df[
        (df['Prob%'] >= 58.0) & 
        (df['RR_Ratio'] >= 1.5) &
        (df['AvgWin%'] > 1.5) &
        (df['AvgLoss%'] < 2.0) &
        (df['Count'] >= 10)
    ].copy()
    filtered['Filter_Type'] = 'BALANCED'
    return filtered


def filter_by_high_prob_criteria(df):
    """เกณฑ์ High Prob: เน้น Prob% สูง (ใช้ AvgWin%, AvgLoss%, RRR เป็นตัวช่วย)"""
    # เกณฑ์: Prob >= 65% AND RRR >= 1.2 AND AvgWin > AvgLoss
    filtered = df[
        (df['Prob%'] >= 65.0) & 
        (df['RR_Ratio'] >= 1.2) &
        (df['AvgWin%'] > df['AvgLoss%']) &  # กำไรเฉลี่ยมากกว่าขาดทุนเฉลี่ย
        (df['Count'] >= 10)
    ].copy()
    filtered['Filter_Type'] = 'HIGH_PROB'
    return filtered


def filter_by_high_rrr_criteria(df):
    """เกณฑ์ High RRR: เน้น RRR สูง (ใช้ Prob%, AvgWin%, AvgLoss% เป็นตัวช่วย)"""
    # เกณฑ์: RRR >= 2.0 AND Prob >= 55% AND AvgWin > 2.0%
    filtered = df[
        (df['RR_Ratio'] >= 2.0) & 
        (df['Prob%'] >= 55.0) &
        (df['AvgWin%'] > 2.0) &
        (df['Count'] >= 10)
    ].copy()
    filtered['Filter_Type'] = 'HIGH_RRR'
    return filtered


def filter_by_quality_criteria(df):
    """เกณฑ์ Quality: ใช้ Prob%, AvgWin%, AvgLoss%, RRR ครบทุกตัว"""
    # เกณฑ์: Prob >= 60% AND AvgWin > 1.5% AND AvgLoss < 1.5% AND RRR >= 1.3
    filtered = df[
        (df['Prob%'] >= 60.0) & 
        (df['AvgWin%'] > 1.5) &
        (df['AvgLoss%'] < 1.5) &
        (df['RR_Ratio'] >= 1.3) &
        (df['Count'] >= 10)
    ].copy()
    filtered['Filter_Type'] = 'QUALITY'
    return filtered


def filter_by_market_specific(df):
    """กรองตามตลาด (ใช้ Prob%, AvgWin%, AvgLoss%, RRR)"""
    selected = []
    
    # THAI - Mean Reversion → เน้น Prob และ AvgWin
    th = df[
        (df['Country'] == 'TH') & 
        (df['Prob%'] >= 58.0) & 
        (df['RR_Ratio'] >= 1.3) &
        (df['AvgWin%'] > 1.0) &
        (df['AvgLoss%'] < 2.0) &
        (df['Count'] >= 10)
    ].copy()
    th['Filter_Type'] = 'THAI_MARKET'
    selected.append(th)
    
    # US - Trend Following → เน้น RRR และ AvgWin
    us = df[
        (df['Country'] == 'US') & 
        (df['Prob%'] >= 52.0) & 
        (df['RR_Ratio'] >= 1.5) &
        (df['AvgWin%'] > 1.5) &
        (df['AvgLoss%'] < 2.5) &
        (df['Count'] >= 10)
    ].copy()
    us['Filter_Type'] = 'US_MARKET'
    selected.append(us)
    
    # CHINA - Mean Reversion → เน้น Prob
    cn = df[
        (df['Country'] == 'CN') & 
        (df['Prob%'] >= 55.0) & 
        (df['RR_Ratio'] >= 1.3) &
        (df['AvgWin%'] > 1.0) &
        (df['Count'] >= 10)
    ].copy()
    cn['Filter_Type'] = 'CHINA_MARKET'
    selected.append(cn)
    
    # TAIWAN - Trend Following → เน้น RRR
    tw = df[
        (df['Country'] == 'TW') & 
        (df['Prob%'] >= 52.0) & 
        (df['RR_Ratio'] >= 1.4) &
        (df['AvgWin%'] > 1.0) &
        (df['Count'] >= 10)
    ].copy()
    tw['Filter_Type'] = 'TAIWAN_MARKET'
    selected.append(tw)
    
    # METALS
    gl = df[
        (df['Country'] == 'GL') & 
        (df['Prob%'] >= 50.0) &
        (df['RR_Ratio'] >= 1.0) &
        (df['Count'] >= 10)
    ].copy()
    gl['Filter_Type'] = 'METALS_MARKET'
    selected.append(gl)
    
    if selected:
        result = pd.concat(selected, ignore_index=True)
        return result
    else:
        return pd.DataFrame()


def calculate_mentor_score(df):
    """
    คำนวณ Mentor Score ที่ใช้ Prob%, AvgWin%, AvgLoss%, RRR
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
    """คำนวณ Risk Management ตาม AvgWin% และ AvgLoss%"""
    df = df.copy()
    
    # Stop Loss = AvgLoss% × 1.5 (เผื่อความผันผวน)
    df['Stop_Loss_Pct'] = df['AvgLoss%'] * 1.5
    
    # Take Profit = AvgWin% × 0.8 (รับกำไรก่อน)
    df['Take_Profit_Pct'] = df['AvgWin%'] * 0.8
    
    # Position Size ตาม RRR และ Prob%
    # Base = 1%
    base_size = 1.0
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
    print("[MENTOR APPROVED FILTERING] ใช้ Prob%, AvgWin%, AvgLoss%, RRR")
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
    
    # Filter by different criteria (all using Prob%, AvgWin%, AvgLoss%, RRR)
    print("\n[1] กรองหุ้นตามเกณฑ์ต่างๆ (ใช้ Prob%, AvgWin%, AvgLoss%, RRR)")
    print("-" * 80)
    
    strict = filter_by_strict_criteria(df)
    print(f"   [STRICT] Prob > 60% AND RRR > 2.0: {len(strict)} symbols")
    
    balanced = filter_by_balanced_criteria(df)
    print(f"   [BALANCED] Prob >= 58% AND RRR >= 1.5 AND AvgWin > 1.5% AND AvgLoss < 2.0%: {len(balanced)} symbols")
    
    high_prob = filter_by_high_prob_criteria(df)
    print(f"   [HIGH_PROB] Prob >= 65% AND RRR >= 1.2 AND AvgWin > AvgLoss: {len(high_prob)} symbols")
    
    high_rrr = filter_by_high_rrr_criteria(df)
    print(f"   [HIGH_RRR] RRR >= 2.0 AND Prob >= 55% AND AvgWin > 2.0%: {len(high_rrr)} symbols")
    
    quality = filter_by_quality_criteria(df)
    print(f"   [QUALITY] Prob >= 60% AND AvgWin > 1.5% AND AvgLoss < 1.5% AND RRR >= 1.3: {len(quality)} symbols")
    
    market = filter_by_market_specific(df)
    print(f"   [MARKET_SPECIFIC] ตามตลาด: {len(market)} symbols")
    
    # Combine all (remove duplicates)
    print("\n[2] รวมผลลัพธ์ (ลบซ้ำ)")
    print("-" * 80)
    
    all_filters = pd.concat([
        strict, balanced, high_prob, high_rrr, quality, market
    ], ignore_index=True)
    
    # Remove duplicates (keep first occurrence)
    all_filters = all_filters.drop_duplicates(subset=['symbol'], keep='first')
    
    # Calculate Mentor Score
    all_filters = calculate_mentor_score(all_filters)
    
    # Add risk management
    all_filters = calculate_risk_management(all_filters)
    
    # Sort by Mentor Score
    all_filters = all_filters.sort_values(['Mentor_Score', 'Prob%', 'RR_Ratio'], ascending=[False, False, False])
    
    print(f"   รวมหุ้นที่เลือก: {len(all_filters)} symbols")
    
    # Save results
    output_cols = [
        'symbol', 'Country', 'Filter_Type',
        'Prob%', 'AvgWin%', 'AvgLoss%', 'RR_Ratio',
        'Count', 'Mentor_Score',
        'Position_Size_Pct', 'Stop_Loss_Pct', 'Take_Profit_Pct'
    ]
    
    available_cols = [col for col in output_cols if col in all_filters.columns]
    all_filters_output = all_filters[available_cols].copy()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    all_filters_output.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n💾 บันทึกผลลัพธ์: {OUTPUT_FILE}")
    
    # Print summary
    print("\n" + "="*100)
    print("[SUMMARY] สรุปผลลัพธ์")
    print("="*100)
    
    print("\n[Top 20 หุ้นที่ดีที่สุด (ตาม Mentor Score)]")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Country':<6} {'Filter':<15} {'Prob%':>6} {'AvgWin%':>8} {'AvgLoss%':>9} {'RRR':>5} {'Score':>7}")
    print("-" * 80)
    
    top20 = all_filters.head(20)
    for _, row in top20.iterrows():
        print(f"{row['symbol']:<10} {row['Country']:<6} {row['Filter_Type']:<15} "
              f"{row['Prob%']:>5.1f}% {row['AvgWin%']:>7.2f}% {row['AvgLoss%']:>8.2f}% "
              f"{row['RR_Ratio']:>4.2f} {row['Mentor_Score']:>6.1f}")
    
    # Statistics by filter type
    print("\n[สถิติตาม Filter Type]")
    print("-" * 80)
    for filter_type in all_filters['Filter_Type'].unique():
        filtered = all_filters[all_filters['Filter_Type'] == filter_type]
        print(f"\n   [{filter_type}] {len(filtered)} symbols")
        if not filtered.empty:
            print(f"      Prob%: Mean={filtered['Prob%'].mean():.1f}%, Min={filtered['Prob%'].min():.1f}%, Max={filtered['Prob%'].max():.1f}%")
            print(f"      RRR: Mean={filtered['RR_Ratio'].mean():.2f}, Min={filtered['RR_Ratio'].min():.2f}, Max={filtered['RR_Ratio'].max():.2f}")
            print(f"      AvgWin%: Mean={filtered['AvgWin%'].mean():.2f}%, Max={filtered['AvgWin%'].max():.2f}%")
            print(f"      AvgLoss%: Mean={filtered['AvgLoss%'].mean():.2f}%, Max={filtered['AvgLoss%'].max():.2f}%")
    
    # Statistics by country
    print("\n[สถิติตามประเทศ]")
    print("-" * 80)
    for country in all_filters['Country'].unique():
        country_df = all_filters[all_filters['Country'] == country]
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
    print("   - ใช้ Prob%, AvgWin%, AvgLoss%, RRR ตามที่ Mentor ต้องการ")
    print("   - มีหลายเกณฑ์ให้เลือก (Strict, Balanced, High Prob, High RRR, Quality)")
    print("   - มี Mentor Score ที่ใช้ Prob%, AvgWin%, AvgLoss%, RRR")
    print("   - มี Risk Management (Position Size, Stop Loss, Take Profit)")


if __name__ == "__main__":
    main()

