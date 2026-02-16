#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
improved_filtering_logic.py - Logic Engine ที่ปรับปรุงแล้ว
================================================================================

ปรับปรุงจาก:
- ใช้ Prob > 60% AND RRR > 2.0 (เข้มงวดเกินไป → มีแค่ 3 หุ้น)
เป็น:
- ใช้ Expectancy หรือ Composite Score (ได้หุ้นมากขึ้นและดีกว่า)

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
OUTPUT_FILE = os.path.join(DATA_DIR, "improved_symbol_selection.csv")


def calculate_expectancy(df):
    """คำนวณ Expectancy"""
    df = df.copy()
    df['Win_Rate'] = df['Prob%'] / 100
    df['Loss_Rate'] = 1 - df['Win_Rate']
    df['Expectancy'] = (
        df['Win_Rate'] * df['AvgWin%'] - 
        df['Loss_Rate'] * df['AvgLoss%']
    )
    return df


def calculate_composite_score(df):
    """คำนวณ Composite Score"""
    df = df.copy()
    df['Composite_Score'] = (
        df['Prob%'] * 0.4 + 
        df['RR_Ratio'] * 20 + 
        df['Expectancy'] * 10
    )
    return df


def filter_by_tier(df):
    """กรองหุ้นตาม Tier System"""
    df = df.copy()
    
    # Tier 1 - ELITE
    tier1 = df[
        (df['Expectancy'] > 0.8) & 
        (df['Prob%'] >= 65.0) &
        (df['Count'] >= 10)
    ].copy()
    tier1['Tier'] = 'ELITE'
    
    # Tier 2 - GOOD
    tier2 = df[
        (df['Expectancy'] > 0.5) & 
        (df['Prob%'] >= 60.0) &
        (df['Count'] >= 10) &
        (~df.index.isin(tier1.index))
    ].copy()
    tier2['Tier'] = 'GOOD'
    
    # Tier 3 - FAIR
    tier3 = df[
        (df['Expectancy'] > 0.3) & 
        (df['Prob%'] >= 55.0) &
        (df['Count'] >= 10) &
        (~df.index.isin(tier1.index)) &
        (~df.index.isin(tier2.index))
    ].copy()
    tier3['Tier'] = 'FAIR'
    
    # Combine
    result = pd.concat([tier1, tier2, tier3], ignore_index=True)
    result = result.sort_values(['Tier', 'Expectancy'], ascending=[True, False])
    
    return result


def filter_by_market_custom(df):
    """กรองหุ้นตามตลาด (ปรับเกณฑ์ตามตลาด)"""
    df = df.copy()
    selected = []
    
    # THAI - Mean Reversion → เน้น Prob
    th = df[
        (df['Country'] == 'TH') & 
        (df['Prob%'] >= 58.0) & 
        (df['RR_Ratio'] >= 1.3) & 
        (df['Expectancy'] > 0.5) &
        (df['Count'] >= 10)
    ].copy()
    th['Filter_Type'] = 'THAI_CUSTOM'
    selected.append(th)
    
    # US - Trend Following → เน้น RRR
    us = df[
        (df['Country'] == 'US') & 
        (df['Prob%'] >= 52.0) & 
        (df['RR_Ratio'] >= 1.5) & 
        (df['Expectancy'] > 0.3) &
        (df['Count'] >= 10)
    ].copy()
    us['Filter_Type'] = 'US_CUSTOM'
    selected.append(us)
    
    # CHINA - Mean Reversion → เน้น Prob
    cn = df[
        (df['Country'] == 'CN') & 
        (df['Prob%'] >= 55.0) & 
        (df['RR_Ratio'] >= 1.3) & 
        (df['Expectancy'] > 0.4) &
        (df['Count'] >= 10)
    ].copy()
    cn['Filter_Type'] = 'CHINA_CUSTOM'
    selected.append(cn)
    
    # TAIWAN - Trend Following → เน้น RRR
    tw = df[
        (df['Country'] == 'TW') & 
        (df['Prob%'] >= 52.0) & 
        (df['RR_Ratio'] >= 1.4) & 
        (df['Expectancy'] > 0.3) &
        (df['Count'] >= 10)
    ].copy()
    tw['Filter_Type'] = 'TAIWAN_CUSTOM'
    selected.append(tw)
    
    # METALS
    gl = df[
        (df['Country'] == 'GL') & 
        (df['Prob%'] >= 50.0) & 
        (df['Expectancy'] > 0.3) &
        (df['Count'] >= 10)
    ].copy()
    gl['Filter_Type'] = 'METALS_CUSTOM'
    selected.append(gl)
    
    if selected:
        result = pd.concat(selected, ignore_index=True)
        result = result.sort_values(['Country', 'Expectancy'], ascending=[True, False])
        return result
    else:
        return pd.DataFrame()


def calculate_position_size(df):
    """คำนวณ Position Size ตาม Risk Management"""
    df = df.copy()
    
    # Base size = 1%
    base_size = 1.0
    
    # Calculate factors
    df['Prob_Factor'] = df['Prob%'] / 60.0
    df['RRR_Factor'] = df['RR_Ratio'] / 2.0
    df['Expectancy_Factor'] = df['Expectancy'] / 0.5
    
    # Combined factor (avoid zero RRR issues)
    df['Combined_Factor'] = (
        df['Prob_Factor'] * 
        df['RRR_Factor'].replace(0, 0.1) *  # Replace 0 RRR with small value
        df['Expectancy_Factor']
    )
    
    # Normalize to max 3x base size
    max_factor = df['Combined_Factor'].max()
    if max_factor > 0:
        df['Position_Size_Pct'] = (df['Combined_Factor'] / max_factor) * 3.0 * base_size
    else:
        df['Position_Size_Pct'] = base_size
    
    # Cap at 5% per stock
    df['Position_Size_Pct'] = df['Position_Size_Pct'].clip(upper=5.0)
    
    return df


def calculate_stop_loss_take_profit(df):
    """คำนวณ Stop Loss และ Take Profit"""
    df = df.copy()
    
    # Stop Loss = AvgLoss% × 1.5
    df['Stop_Loss_Pct'] = df['AvgLoss%'] * 1.5
    
    # Take Profit = AvgWin% × 0.8
    df['Take_Profit_Pct'] = df['AvgWin%'] * 0.8
    
    return df


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[IMPROVED FILTERING] Logic Engine ที่ปรับปรุงแล้ว")
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
    
    # Calculate metrics
    df = calculate_expectancy(df)
    df = calculate_composite_score(df)
    
    # Filter by Tier
    print("\n[1] กรองหุ้นตาม Tier System")
    print("-" * 80)
    tier_df = filter_by_tier(df)
    print(f"   Tier 1 (ELITE): {len(tier_df[tier_df['Tier'] == 'ELITE'])} symbols")
    print(f"   Tier 2 (GOOD): {len(tier_df[tier_df['Tier'] == 'GOOD'])} symbols")
    print(f"   Tier 3 (FAIR): {len(tier_df[tier_df['Tier'] == 'FAIR'])} symbols")
    print(f"   รวม: {len(tier_df)} symbols")
    
    # Filter by Market Custom
    print("\n[2] กรองหุ้นตามตลาด (ปรับเกณฑ์)")
    print("-" * 80)
    market_df = filter_by_market_custom(df)
    print(f"   THAI: {len(market_df[market_df['Country'] == 'TH'])} symbols")
    print(f"   US: {len(market_df[market_df['Country'] == 'US'])} symbols")
    print(f"   CHINA: {len(market_df[market_df['Country'] == 'CN'])} symbols")
    print(f"   TAIWAN: {len(market_df[market_df['Country'] == 'TW'])} symbols")
    print(f"   METALS: {len(market_df[market_df['Country'] == 'GL'])} symbols")
    print(f"   รวม: {len(market_df)} symbols")
    
    # Combine and add risk management
    print("\n[3] เพิ่ม Risk Management")
    print("-" * 80)
    
    # Use Tier as primary, add market custom
    combined = tier_df.copy()
    if not market_df.empty:
        # Add market custom that's not in tier
        market_only = market_df[~market_df['symbol'].isin(combined['symbol'])]
        if not market_only.empty:
            market_only['Tier'] = 'MARKET_CUSTOM'
            combined = pd.concat([combined, market_only], ignore_index=True)
    
    # Add risk management
    combined = calculate_position_size(combined)
    combined = calculate_stop_loss_take_profit(combined)
    
    # Sort by Tier and Expectancy
    tier_order = {'ELITE': 1, 'GOOD': 2, 'FAIR': 3, 'MARKET_CUSTOM': 4}
    combined['Tier_Order'] = combined['Tier'].map(tier_order)
    combined = combined.sort_values(['Tier_Order', 'Expectancy'], ascending=[True, False])
    combined = combined.drop('Tier_Order', axis=1)
    
    print(f"   รวมหุ้นที่เลือก: {len(combined)} symbols")
    
    # Save results
    output_cols = [
        'symbol', 'Country', 'Tier', 'Filter_Type',
        'Prob%', 'RR_Ratio', 'Expectancy', 'Composite_Score',
        'AvgWin%', 'AvgLoss%', 'Count',
        'Position_Size_Pct', 'Stop_Loss_Pct', 'Take_Profit_Pct'
    ]
    
    # Only include columns that exist
    available_cols = [col for col in output_cols if col in combined.columns]
    combined_output = combined[available_cols].copy()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    combined_output.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n💾 บันทึกผลลัพธ์: {OUTPUT_FILE}")
    
    # Print summary
    print("\n" + "="*100)
    print("[SUMMARY] สรุปผลลัพธ์")
    print("="*100)
    
    print("\n[Top 10 หุ้นที่ดีที่สุด (ตาม Expectancy)]")
    print("-" * 80)
    top10 = combined.nlargest(10, 'Expectancy')
    for _, row in top10.iterrows():
        print(f"   {row['symbol']:<10} {row['Country']:<4} Tier={row['Tier']:<12} "
              f"Exp={row['Expectancy']:>5.2f}% Prob={row['Prob%']:>5.1f}% "
              f"RRR={row['RR_Ratio']:>4.2f} Size={row['Position_Size_Pct']:>4.1f}%")
    
    print("\n[Top 10 หุ้นที่ดีที่สุด (ตาม Composite Score)]")
    print("-" * 80)
    top10_score = combined.nlargest(10, 'Composite_Score')
    for _, row in top10_score.iterrows():
        print(f"   {row['symbol']:<10} {row['Country']:<4} Tier={row['Tier']:<12} "
              f"Score={row['Composite_Score']:>6.1f} Exp={row['Expectancy']:>5.2f}% "
              f"Prob={row['Prob%']:>5.1f}% RRR={row['RR_Ratio']:>4.2f}")
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้น")
    print("="*100)


if __name__ == "__main__":
    main()

