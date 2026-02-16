#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_logic_engine_comprehensive.py - วิเคราะห์ Logic Engine อย่างละเอียด
================================================================================

วิเคราะห์:
1. Logic Engine ที่ใช้คัดกรองหุ้นแต่ละประเทศ
2. Prob และ RRR ว่ามันสมเหตุสมผลไหม
3. ทำไมไม่มีหุ้นผ่านเกณฑ์ Prob > 60% และ RRR > 2
4. แนวทางปรับปรุง Logic
5. การบริหารความเสี่ยงเพื่อให้ได้กำไรมากกว่าเสีย

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
TRADE_HISTORY = os.path.join(BASE_DIR, "logs", "trade_history.csv")


def load_data():
    """โหลดข้อมูล"""
    df_metrics = pd.read_csv(METRICS_FILE) if os.path.exists(METRICS_FILE) else pd.DataFrame()
    
    # Try to load split trade history files
    trade_files = []
    if os.path.exists(TRADE_HISTORY):
        trade_files.append(TRADE_HISTORY)
    
    # Also try split files
    for country in ['THAI', 'US', 'CHINA', 'TAIWAN']:
        split_file = os.path.join(BASE_DIR, "logs", f"trade_history_{country}.csv")
        if os.path.exists(split_file):
            trade_files.append(split_file)
    
    df_trades_list = []
    for f in trade_files:
        try:
            df = pd.read_csv(f, engine='python', on_bad_lines='skip')
            if not df.empty:
                df_trades_list.append(df)
        except Exception as e:
            print(f"⚠️ Error loading {f}: {e}")
    
    df_trades = pd.concat(df_trades_list, ignore_index=True) if df_trades_list else pd.DataFrame()
    
    return df_metrics, df_trades


def analyze_prob_rrr_logic(df_metrics):
    """วิเคราะห์ว่า Prob และ RRR สมเหตุสมผลไหม"""
    print("\n" + "="*100)
    print("[ANALYSIS 1] วิเคราะห์ Logic ของ Prob และ RRR")
    print("="*100)
    
    print("\n[1.1] ความหมายของ Prob และ RRR")
    print("-" * 80)
    print("   Prob% (Probability):")
    print("   - คำนวณจาก Win Rate = (จำนวนครั้งที่ชนะ / จำนวนครั้งทั้งหมด) × 100")
    print("   - แสดงโอกาสที่การเทรดจะได้กำไร")
    print("   - Prob > 60% หมายความว่า ชนะมากกว่า 60% ของครั้ง")
    print()
    print("   RRR (Risk-Reward Ratio):")
    print("   - คำนวณจาก RRR = AvgWin% / AvgLoss%")
    print("   - แสดงว่ากำไรเฉลี่ยมากกว่าขาดทุนเฉลี่ยกี่เท่า")
    print("   - RRR > 2 หมายความว่า กำไรเฉลี่ยมากกว่าขาดทุนเฉลี่ย 2 เท่า")
    print()
    print("   [LOGIC CHECK]")
    print("   - Prob และ RRR เป็นตัวชี้วัดที่สมเหตุสมผล")
    print("   - แต่การใช้ AND (Prob > 60% AND RRR > 2) เข้มงวดมาก")
    print("   - ควรพิจารณา Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)")
    
    print("\n[1.2] วิเคราะห์ความสัมพันธ์ระหว่าง Prob และ RRR")
    print("-" * 80)
    
    if df_metrics.empty:
        print("   ⚠️ ไม่มีข้อมูล")
        return
    
    # คำนวณ Expectancy
    df_metrics['Win_Rate'] = df_metrics['Prob%'] / 100
    df_metrics['Loss_Rate'] = 1 - df_metrics['Win_Rate']
    df_metrics['Expectancy'] = (
        df_metrics['Win_Rate'] * df_metrics['AvgWin%'] - 
        df_metrics['Loss_Rate'] * df_metrics['AvgLoss%']
    )
    
    # Correlation
    correlation = df_metrics['Prob%'].corr(df_metrics['RR_Ratio'])
    print(f"   Correlation ระหว่าง Prob% และ RRR: {correlation:.3f}")
    print(f"   - ค่าใกล้ 0 หมายความว่า Prob และ RRR ไม่มีความสัมพันธ์กัน")
    print(f"   - นี่คือเหตุผลที่หุ้นที่มี Prob สูงอาจมี RRR ต่ำ และในทางกลับกัน")
    
    # วิเคราะห์หุ้นที่ผ่านเกณฑ์ต่างๆ
    strict = df_metrics[(df_metrics['Prob%'] > 60.0) & (df_metrics['RR_Ratio'] > 2.0)]
    high_prob = df_metrics[df_metrics['Prob%'] > 60.0]
    high_rrr = df_metrics[df_metrics['RR_Ratio'] > 2.0]
    high_expectancy = df_metrics[df_metrics['Expectancy'] > 0.5]
    
    print(f"\n   [FILTER RESULTS]")
    print(f"   Strict (Prob > 60% AND RRR > 2.0): {len(strict)} symbols")
    print(f"   High Prob (Prob > 60%): {len(high_prob)} symbols")
    print(f"   High RRR (RRR > 2.0): {len(high_rrr)} symbols")
    print(f"   High Expectancy (Expectancy > 0.5%): {len(high_expectancy)} symbols")
    
    if len(strict) == 0:
        print(f"\n   [PROBLEM] ไม่มีหุ้นผ่านเกณฑ์ Strict")
        print(f"   - มีหุ้น {len(high_prob)} ตัวที่มี Prob > 60% แต่ RRR <= 2.0")
        print(f"   - มีหุ้น {len(high_rrr)} ตัวที่มี RRR > 2.0 แต่ Prob <= 60%")
        print(f"   - แสดงว่า Prob และ RRR มักไม่มาคู่กัน")
        print(f"   - ควรใช้ Expectancy หรือ Composite Score แทน")


def analyze_market_filters(df_metrics):
    """วิเคราะห์ Logic Engine ที่ใช้คัดกรองหุ้นแต่ละประเทศ"""
    print("\n" + "="*100)
    print("[ANALYSIS 2] วิเคราะห์ Logic Engine ที่ใช้คัดกรองหุ้นแต่ละประเทศ")
    print("="*100)
    
    markets = {
        'TH': {
            'name': 'THAI',
            'engine': 'MEAN_REVERSION',
            'strategy': 'Fade the move',
            'filters': [
                {'name': 'Elite', 'prob': 55.0, 'rrr': 1.2, 'count': None},
                {'name': 'Balanced', 'prob': 60.0, 'rrr': 1.5, 'rrr_max': 2.0, 'count': None}
            ]
        },
        'US': {
            'name': 'US',
            'engine': 'TREND_MOMENTUM',
            'strategy': 'Follow the move (LONG ONLY)',
            'filters': [
                {'name': 'Standard', 'prob': 50.0, 'rrr': 1.0, 'count': None}
            ]
        },
        'CN': {
            'name': 'CHINA/HK',
            'engine': 'MEAN_REVERSION',
            'strategy': 'Fade the move',
            'filters': [
                {'name': 'Standard', 'prob': 50.0, 'rrr': 1.0, 'count': None}
            ]
        },
        'TW': {
            'name': 'TAIWAN',
            'engine': 'TREND_MOMENTUM',
            'strategy': 'Follow the move',
            'filters': [
                {'name': 'Standard', 'prob': 50.0, 'rrr': 1.0, 'count': None}
            ]
        },
        'GL': {
            'name': 'METALS',
            'engine': 'MEAN_REVERSION',
            'strategy': 'Fade the move',
            'filters': [
                {'name': 'Standard', 'prob': 50.0, 'rrr': None, 'count': None}
            ]
        }
    }
    
    for country_code, market_info in markets.items():
        market_df = df_metrics[df_metrics['Country'] == country_code]
        if market_df.empty:
            print(f"\n[{country_code}] {market_info['name']} Market: ไม่มีข้อมูล")
            continue
        
        print(f"\n[{country_code}] {market_info['name']} Market")
        print("-" * 80)
        print(f"   Engine: {market_info['engine']}")
        print(f"   Strategy: {market_info['strategy']}")
        print(f"   Total Symbols: {len(market_df)}")
        
        # สถิติพื้นฐาน
        print(f"\n   [STATS] สถิติพื้นฐาน:")
        print(f"   Prob%:  Mean={market_df['Prob%'].mean():.1f}%  "
              f"Median={market_df['Prob%'].median():.1f}%  "
              f"Min={market_df['Prob%'].min():.1f}%  Max={market_df['Prob%'].max():.1f}%")
        print(f"   RRR:    Mean={market_df['RR_Ratio'].mean():.2f}  "
              f"Median={market_df['RR_Ratio'].median():.2f}  "
              f"Min={market_df['RR_Ratio'].min():.2f}  Max={market_df['RR_Ratio'].max():.2f}")
        
        if 'Expectancy' in market_df.columns:
            print(f"   Expectancy: Mean={market_df['Expectancy'].mean():.2f}%  "
                  f"Median={market_df['Expectancy'].median():.2f}%")
        
        # ตรวจสอบหุ้นที่ผ่านเกณฑ์ปัจจุบัน
        print(f"\n   [CURRENT FILTERS] หุ้นที่ผ่านเกณฑ์:")
        for filter_def in market_info['filters']:
            filter_df = market_df.copy()
            if filter_def['prob'] is not None:
                filter_df = filter_df[filter_df['Prob%'] > filter_def['prob']]
            if filter_def.get('rrr') is not None:
                filter_df = filter_df[filter_df['RR_Ratio'] > filter_def['rrr']]
            if filter_def.get('rrr_max') is not None:
                filter_df = filter_df[filter_df['RR_Ratio'] <= filter_def['rrr_max']]
            if filter_def.get('count') is not None:
                filter_df = filter_df[filter_df['Count'] >= filter_def['count']]
            
            print(f"   {filter_def['name']}: {len(filter_df)} symbols")
        
        # ตรวจสอบหุ้นที่ผ่านเกณฑ์ Strict
        strict = market_df[(market_df['Prob%'] > 60.0) & (market_df['RR_Ratio'] > 2.0)]
        print(f"\n   [STRICT FILTER] Prob > 60% AND RRR > 2.0: {len(strict)} symbols")
        
        if len(strict) == 0:
            # วิเคราะห์ว่าทำไมไม่ผ่าน
            high_prob_low_rrr = market_df[(market_df['Prob%'] > 60.0) & (market_df['RR_Ratio'] <= 2.0)]
            high_rrr_low_prob = market_df[(market_df['RR_Ratio'] > 2.0) & (market_df['Prob%'] <= 60.0)]
            
            print(f"   - หุ้นที่มี Prob > 60% แต่ RRR <= 2.0: {len(high_prob_low_rrr)} symbols")
            if not high_prob_low_rrr.empty:
                top3 = high_prob_low_rrr.nlargest(3, 'Prob%')
                top3_str = ', '.join([f"{row['symbol']} (Prob={row['Prob%']:.1f}%, RRR={row['RR_Ratio']:.2f})" for _, row in top3.iterrows()])
                print(f"     Top 3: {top3_str}")
            
            print(f"   - หุ้นที่มี RRR > 2.0 แต่ Prob <= 60%: {len(high_rrr_low_prob)} symbols")
            if not high_rrr_low_prob.empty:
                top3 = high_rrr_low_prob.nlargest(3, 'RR_Ratio')
                top3_str = ', '.join([f"{row['symbol']} (Prob={row['Prob%']:.1f}%, RRR={row['RR_Ratio']:.2f})" for _, row in top3.iterrows()])
                print(f"     Top 3: {top3_str}")


def analyze_why_no_strict_matches(df_metrics):
    """วิเคราะห์ว่าทำไมไม่มีหุ้นผ่านเกณฑ์ Prob > 60% และ RRR > 2"""
    print("\n" + "="*100)
    print("[ANALYSIS 3] วิเคราะห์ว่าทำไมไม่มีหุ้นผ่านเกณฑ์ Prob > 60% AND RRR > 2")
    print("="*100)
    
    if df_metrics.empty:
        print("   ⚠️ ไม่มีข้อมูล")
        return
    
    # คำนวณ Expectancy
    if 'Expectancy' not in df_metrics.columns:
        df_metrics['Win_Rate'] = df_metrics['Prob%'] / 100
        df_metrics['Loss_Rate'] = 1 - df_metrics['Win_Rate']
        df_metrics['Expectancy'] = (
            df_metrics['Win_Rate'] * df_metrics['AvgWin%'] - 
            df_metrics['Loss_Rate'] * df_metrics['AvgLoss%']
        )
    
    strict = df_metrics[(df_metrics['Prob%'] > 60.0) & (df_metrics['RR_Ratio'] > 2.0)]
    
    print(f"\n[3.1] สถานการณ์ปัจจุบัน")
    print("-" * 80)
    print(f"   หุ้นที่ผ่านเกณฑ์ Strict (Prob > 60% AND RRR > 2.0): {len(strict)} symbols")
    print(f"   หุ้นทั้งหมด: {len(df_metrics)} symbols")
    
    if len(strict) == 0:
        print(f"\n[3.2] สาเหตุที่ไม่มีหุ้นผ่านเกณฑ์")
        print("-" * 80)
        
        # วิเคราะห์ตามประเทศ
        for country in ['TH', 'US', 'CN', 'TW', 'GL']:
            country_df = df_metrics[df_metrics['Country'] == country]
            if country_df.empty:
                continue
            
            strict_country = country_df[(country_df['Prob%'] > 60.0) & (country_df['RR_Ratio'] > 2.0)]
            high_prob = country_df[country_df['Prob%'] > 60.0]
            high_rrr = country_df[country_df['RR_Ratio'] > 2.0]
            
            print(f"\n   [{country}] Market:")
            print(f"   - Strict matches: {len(strict_country)}")
            print(f"   - High Prob only: {len(high_prob)}")
            print(f"   - High RRR only: {len(high_rrr)}")
            print(f"   - Mean Prob: {country_df['Prob%'].mean():.1f}%")
            print(f"   - Mean RRR: {country_df['RR_Ratio'].mean():.2f}")
        
        print(f"\n[3.3] ปัญหาหลัก")
        print("-" * 80)
        print("   1. Prob และ RRR ไม่มีความสัมพันธ์กัน (Correlation ≈ 0)")
        print("      - หุ้นที่มี Prob สูงมักมี RRR ต่ำ (ชนะบ่อยแต่กำไรน้อย)")
        print("      - หุ้นที่มี RRR สูงมักมี Prob ต่ำ (ชนะน้อยแต่กำไรมาก)")
        print()
        print("   2. การใช้ AND (Prob > 60% AND RRR > 2) เข้มงวดเกินไป")
        print("      - ต้องการทั้งความถี่สูง (Prob) และกำไรมาก (RRR)")
        print("      - ในความเป็นจริง หุ้นส่วนใหญ่มีคุณสมบัติอย่างใดอย่างหนึ่ง")
        print()
        print("   3. เกณฑ์อาจไม่เหมาะกับตลาดบางตลาด")
        print("      - US/TW (Trend Following): Prob มักต่ำกว่า Mean Reversion")
        print("      - TH/CN (Mean Reversion): RRR มักต่ำกว่า Trend Following")


def suggest_logic_improvements(df_metrics):
    """เสนอแนวทางปรับปรุง Logic"""
    print("\n" + "="*100)
    print("[IMPROVEMENTS] แนวทางปรับปรุง Logic Engine")
    print("="*100)
    
    if df_metrics.empty:
        print("   ⚠️ ไม่มีข้อมูล")
        return
    
    # คำนวณ Expectancy
    if 'Expectancy' not in df_metrics.columns:
        df_metrics['Win_Rate'] = df_metrics['Prob%'] / 100
        df_metrics['Loss_Rate'] = 1 - df_metrics['Win_Rate']
        df_metrics['Expectancy'] = (
            df_metrics['Win_Rate'] * df_metrics['AvgWin%'] - 
            df_metrics['Loss_Rate'] * df_metrics['AvgLoss%']
        )
    
    print("\n[1] เปลี่ยนจาก Prob + RRR เป็น Expectancy")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Filter: Prob >= 60% AND RRR >= 2.0")
    print("   - Problem: เข้มงวดเกินไป → ไม่มีหุ้นผ่าน")
    print()
    print("   [PROPOSED]")
    print("   - Filter: Expectancy > 0.5%")
    print("   - Formula: Expectancy = (Win Rate × Avg Win%) - (Loss Rate × Avg Loss%)")
    print("   - Benefit: บอกความคุ้มค่าได้ดีกว่า (รวมทั้ง Prob และ RRR)")
    
    # ตรวจสอบหุ้นที่ผ่าน Expectancy
    high_expectancy = df_metrics[df_metrics['Expectancy'] > 0.5]
    print(f"\n   [RESULTS]")
    print(f"   - หุ้นที่ผ่าน Expectancy > 0.5%: {len(high_expectancy)} symbols")
    if not high_expectancy.empty:
        top5 = high_expectancy.nlargest(5, 'Expectancy')
        print(f"   - Top 5:")
        for _, row in top5.iterrows():
            print(f"     {row['symbol']}: Expectancy={row['Expectancy']:.2f}%, Prob={row['Prob%']:.1f}%, RRR={row['RR_Ratio']:.2f}")
    
    print("\n[2] ใช้ Composite Score")
    print("-" * 80)
    print("   [FORMULA]")
    print("   Score = (Prob% × 0.4) + (RRR × 20) + (Expectancy × 10)")
    print("   - Prob% มีน้ำหนัก 40% (ความถี่)")
    print("   - RRR มีน้ำหนัก 20 เท่า (กำไรต่อความเสี่ยง)")
    print("   - Expectancy มีน้ำหนัก 10 เท่า (ความคุ้มค่า)")
    
    # คำนวณ Composite Score
    df_metrics['Composite_Score'] = (
        df_metrics['Prob%'] * 0.4 + 
        df_metrics['RR_Ratio'] * 20 + 
        df_metrics['Expectancy'] * 10
    )
    
    high_score = df_metrics[df_metrics['Composite_Score'] > 50]
    print(f"\n   [RESULTS]")
    print(f"   - หุ้นที่ผ่าน Composite Score > 50: {len(high_score)} symbols")
    if not high_score.empty:
        top5 = high_score.nlargest(5, 'Composite_Score')
        print(f"   - Top 5:")
        for _, row in top5.iterrows():
            print(f"     {row['symbol']}: Score={row['Composite_Score']:.1f}, Prob={row['Prob%']:.1f}%, RRR={row['RR_Ratio']:.2f}, Exp={row['Expectancy']:.2f}%")
    
    print("\n[3] ใช้ Tier System (หลายระดับ)")
    print("-" * 80)
    print("   [TIER 1 - ELITE]")
    print("   - Expectancy > 0.8% AND Prob >= 65%")
    elite = df_metrics[(df_metrics['Expectancy'] > 0.8) & (df_metrics['Prob%'] >= 65.0)]
    print(f"   - Matches: {len(elite)} symbols")
    
    print("\n   [TIER 2 - GOOD]")
    print("   - Expectancy > 0.5% AND Prob >= 60%")
    good = df_metrics[(df_metrics['Expectancy'] > 0.5) & (df_metrics['Prob%'] >= 60.0)]
    print(f"   - Matches: {len(good)} symbols")
    
    print("\n   [TIER 3 - FAIR]")
    print("   - Expectancy > 0.3% AND Prob >= 55%")
    fair = df_metrics[(df_metrics['Expectancy'] > 0.3) & (df_metrics['Prob%'] >= 55.0)]
    print(f"   - Matches: {len(fair)} symbols")
    
    print("\n[4] ปรับเกณฑ์ตามตลาด")
    print("-" * 80)
    print("   [THAI] Mean Reversion → เน้น Prob")
    print("   - Prob >= 58%, RRR >= 1.3, Expectancy > 0.5%")
    th_custom = df_metrics[
        (df_metrics['Country'] == 'TH') & 
        (df_metrics['Prob%'] >= 58.0) & 
        (df_metrics['RR_Ratio'] >= 1.3) & 
        (df_metrics['Expectancy'] > 0.5)
    ]
    print(f"   - Matches: {len(th_custom)} symbols")
    
    print("\n   [US] Trend Following → เน้น RRR")
    print("   - Prob >= 52%, RRR >= 1.5, Expectancy > 0.3%")
    us_custom = df_metrics[
        (df_metrics['Country'] == 'US') & 
        (df_metrics['Prob%'] >= 52.0) & 
        (df_metrics['RR_Ratio'] >= 1.5) & 
        (df_metrics['Expectancy'] > 0.3)
    ]
    print(f"   - Matches: {len(us_custom)} symbols")
    
    print("\n   [CHINA] Mean Reversion → เน้น Prob")
    print("   - Prob >= 55%, RRR >= 1.3, Expectancy > 0.4%")
    cn_custom = df_metrics[
        (df_metrics['Country'] == 'CN') & 
        (df_metrics['Prob%'] >= 55.0) & 
        (df_metrics['RR_Ratio'] >= 1.3) & 
        (df_metrics['Expectancy'] > 0.4)
    ]
    print(f"   - Matches: {len(cn_custom)} symbols")
    
    print("\n   [TAIWAN] Trend Following → เน้น RRR")
    print("   - Prob >= 52%, RRR >= 1.4, Expectancy > 0.3%")
    tw_custom = df_metrics[
        (df_metrics['Country'] == 'TW') & 
        (df_metrics['Prob%'] >= 52.0) & 
        (df_metrics['RR_Ratio'] >= 1.4) & 
        (df_metrics['Expectancy'] > 0.3)
    ]
    print(f"   - Matches: {len(tw_custom)} symbols")


def suggest_risk_management(df_metrics, df_trades):
    """เสนอการบริหารความเสี่ยงเพื่อให้ได้กำไรมากกว่าเสีย"""
    print("\n" + "="*100)
    print("[RISK MANAGEMENT] การบริหารความเสี่ยงเพื่อให้ได้กำไรมากกว่าเสีย")
    print("="*100)
    
    if df_metrics.empty:
        print("   ⚠️ ไม่มีข้อมูล")
        return
    
    # คำนวณ Expectancy
    if 'Expectancy' not in df_metrics.columns:
        df_metrics['Win_Rate'] = df_metrics['Prob%'] / 100
        df_metrics['Loss_Rate'] = 1 - df_metrics['Win_Rate']
        df_metrics['Expectancy'] = (
            df_metrics['Win_Rate'] * df_metrics['AvgWin%'] - 
            df_metrics['Loss_Rate'] * df_metrics['AvgLoss%']
        )
    
    print("\n[1] Position Sizing ตาม Expectancy")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - หุ้นที่มี Expectancy สูง → ลงทุนมากกว่า")
    print("   - หุ้นที่มี Expectancy ต่ำ → ลงทุนน้อยกว่า")
    print()
    print("   [FORMULA]")
    print("   Position Size = Base Size × (Expectancy / Max Expectancy)")
    print("   - Base Size = 1% ของพอร์ต")
    print("   - Max Expectancy = Expectancy สูงสุดในพอร์ต")
    
    # ตัวอย่าง
    if not df_metrics.empty:
        max_exp = df_metrics['Expectancy'].max()
        print(f"\n   [EXAMPLE]")
        print(f"   - Max Expectancy: {max_exp:.2f}%")
        high_exp_stocks = df_metrics[df_metrics['Expectancy'] > 0.5].nlargest(5, 'Expectancy')
        if not high_exp_stocks.empty:
            print(f"   - Top 5 หุ้นที่ควรลงทุนมาก:")
            for _, row in high_exp_stocks.iterrows():
                size = (row['Expectancy'] / max_exp) * 100 if max_exp > 0 else 0
                print(f"     {row['symbol']}: Expectancy={row['Expectancy']:.2f}%, Position Size={size:.1f}%")
    
    print("\n[2] Stop Loss ตาม AvgLoss%")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ตั้ง Stop Loss = AvgLoss% × 1.5 (เผื่อความผันผวน)")
    print("   - ป้องกันการขาดทุนมากเกินไป")
    print()
    print("   [EXAMPLE]")
    if not df_metrics.empty:
        sample = df_metrics[df_metrics['AvgLoss%'] > 0].head(5)
        for _, row in sample.iterrows():
            stop_loss = row['AvgLoss%'] * 1.5
            print(f"     {row['symbol']}: AvgLoss={row['AvgLoss%']:.2f}% → Stop Loss={stop_loss:.2f}%")
    
    print("\n[3] Take Profit ตาม AvgWin%")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ตั้ง Take Profit = AvgWin% × 0.8 (รับกำไรก่อน)")
    print("   - หรือใช้ Trailing Stop เมื่อได้กำไร")
    print()
    print("   [EXAMPLE]")
    if not df_metrics.empty:
        sample = df_metrics[df_metrics['AvgWin%'] > 0].head(5)
        for _, row in sample.iterrows():
            take_profit = row['AvgWin%'] * 0.8
            print(f"     {row['symbol']}: AvgWin={row['AvgWin%']:.2f}% → Take Profit={take_profit:.2f}%")
    
    print("\n[4] Portfolio Diversification")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - กระจายหุ้นตาม Tier (Elite, Good, Fair)")
    print("   - กระจายตามตลาด (TH, US, CN, TW)")
    print("   - จำกัดจำนวนหุ้นต่อตลาด (ไม่เกิน 5-10 ตัว)")
    print()
    print("   [ALLOCATION]")
    print("   - Tier 1 (Elite): 40% ของพอร์ต")
    print("   - Tier 2 (Good): 40% ของพอร์ต")
    print("   - Tier 3 (Fair): 20% ของพอร์ต")
    
    print("\n[5] Risk-Reward Ratio Management")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ใช้ RRR เพื่อกำหนด Position Size")
    print("   - RRR สูง → ลงทุนมากกว่า (เพราะความเสี่ยงต่ำ)")
    print("   - RRR ต่ำ → ลงทุนน้อยกว่า (เพราะความเสี่ยงสูง)")
    print()
    print("   [FORMULA]")
    print("   Position Size = Base Size × (RRR / 2.0)")
    print("   - RRR = 2.0 → Position Size = Base Size")
    print("   - RRR = 4.0 → Position Size = 2 × Base Size")
    print("   - RRR = 1.0 → Position Size = 0.5 × Base Size")
    
    print("\n[6] Win Rate Management")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - Prob สูง → ลงทุนบ่อยกว่า (เพราะชนะบ่อย)")
    print("   - Prob ต่ำ → ลงทุนน้อยกว่า (เพราะชนะน้อย)")
    print()
    print("   [STRATEGY]")
    print("   - Prob > 65%: ลงทุนเต็มที่")
    print("   - Prob 60-65%: ลงทุนปกติ")
    print("   - Prob 55-60%: ลงทุนน้อย (50% ของปกติ)")
    print("   - Prob < 55%: ไม่ลงทุน")
    
    print("\n[7] Combined Risk Management Formula")
    print("-" * 80)
    print("   [FORMULA]")
    print("   Final Position Size = Base Size × Prob_Factor × RRR_Factor × Expectancy_Factor")
    print()
    print("   Prob_Factor = Prob% / 60%")
    print("   RRR_Factor = RRR / 2.0")
    print("   Expectancy_Factor = Expectancy / 0.5%")
    print()
    print("   [EXAMPLE]")
    if not df_metrics.empty:
        sample = df_metrics[df_metrics['Expectancy'] > 0.3].head(3)
        for _, row in sample.iterrows():
            prob_factor = row['Prob%'] / 60.0
            rrr_factor = row['RR_Ratio'] / 2.0
            exp_factor = row['Expectancy'] / 0.5 if row['Expectancy'] > 0 else 0
            final_size = prob_factor * rrr_factor * exp_factor
            print(f"     {row['symbol']}:")
            print(f"       Prob={row['Prob%']:.1f}% → Factor={prob_factor:.2f}")
            print(f"       RRR={row['RR_Ratio']:.2f} → Factor={rrr_factor:.2f}")
            print(f"       Exp={row['Expectancy']:.2f}% → Factor={exp_factor:.2f}")
            print(f"       Final Size Factor={final_size:.2f}x")


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[MAIN] วิเคราะห์ Logic Engine อย่างละเอียด")
    print("="*100)
    
    # โหลดข้อมูล
    df_metrics, df_trades = load_data()
    
    if df_metrics.empty:
        print("[ERROR] ไม่สามารถโหลดข้อมูลได้")
        return
    
    print(f"\n📊 โหลดข้อมูลสำเร็จ:")
    print(f"   - Metrics: {len(df_metrics)} symbols")
    print(f"   - Trades: {len(df_trades)} trades")
    
    # วิเคราะห์
    analyze_prob_rrr_logic(df_metrics)
    analyze_market_filters(df_metrics)
    analyze_why_no_strict_matches(df_metrics)
    suggest_logic_improvements(df_metrics)
    suggest_risk_management(df_metrics, df_trades)
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้นการวิเคราะห์")
    print("="*100)
    print("\n💡 สรุป:")
    print("   1. Prob และ RRR สมเหตุสมผล แต่การใช้ AND เข้มงวดเกินไป")
    print("   2. ควรใช้ Expectancy หรือ Composite Score แทน")
    print("   3. ควรปรับเกณฑ์ตามตลาด (TH เน้น Prob, US เน้น RRR)")
    print("   4. ใช้ Position Sizing และ Risk Management ตาม Expectancy")


if __name__ == "__main__":
    main()

