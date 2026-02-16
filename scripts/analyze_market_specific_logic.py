#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_market_specific_logic.py - วิเคราะห์และปรับ Logic Engine ให้เข้ากับแต่ละตลาด
================================================================================

ปัญหาที่พบ:
1. ระบบเก่งกับตลาดหุ้นไทย (Mean Reversion) แต่ไม่เก่งกับตลาดอื่น
2. US Stocks ใช้ Trend Following แต่ Prob และ RRR ต่ำมาก
3. China/HK ใช้ Mean Reversion แต่ก็ไม่ดี
4. Taiwan ใช้ Trend Following แต่ก็ไม่ดี
5. ไม่มีหุ้นผ่านเกณฑ์ Prob 60% AND RRR > 2

วัตถุประสงค์:
1. วิเคราะห์ว่าทำไม Trend Following ไม่ทำงานกับ US
2. วิเคราะห์ว่าทำไม Mean Reversion ไม่ทำงานกับ China
3. เสนอแนวทางปรับ logic ให้เข้ากับแต่ละตลาด

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
    df_trades = pd.read_csv(TRADE_HISTORY, engine='python', on_bad_lines='skip') if os.path.exists(TRADE_HISTORY) else pd.DataFrame()
    return df_metrics, df_trades


def analyze_market_performance(df_metrics, df_trades):
    """วิเคราะห์ผลการทำงานของแต่ละตลาด"""
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์ผลการทำงานของแต่ละตลาด")
    print("="*100)
    
    # แยกตามประเทศ
    markets = {
        'TH': {'name': 'THAI', 'engine': 'MEAN_REVERSION', 'strategy': 'Fade the move'},
        'US': {'name': 'US', 'engine': 'TREND_MOMENTUM', 'strategy': 'Follow the move (LONG ONLY)'},
        'CN': {'name': 'CHINA/HK', 'engine': 'MEAN_REVERSION', 'strategy': 'Fade the move'},
        'TW': {'name': 'TAIWAN', 'engine': 'TREND_MOMENTUM', 'strategy': 'Follow the move'}
    }
    
    for country_code, market_info in markets.items():
        market_df = df_metrics[df_metrics['Country'] == country_code]
        if market_df.empty:
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
        
        # หุ้นที่ผ่านเกณฑ์ต่างๆ
        strict = market_df[(market_df['Prob%'] > 60.0) & (market_df['RR_Ratio'] > 2.0)]
        relaxed = market_df[(market_df['Prob%'] >= 55.0) & (market_df['RR_Ratio'] >= 1.2)]
        very_relaxed = market_df[(market_df['Prob%'] >= 50.0) & (market_df['RR_Ratio'] >= 1.0)]
        
        print(f"\n   [FILTERS] หุ้นที่ผ่านเกณฑ์:")
        print(f"   Strict (Prob > 60% AND RRR > 2.0): {len(strict)} symbols")
        print(f"   Relaxed (Prob >= 55% AND RRR >= 1.2): {len(relaxed)} symbols")
        print(f"   Very Relaxed (Prob >= 50% AND RRR >= 1.0): {len(very_relaxed)} symbols")
        
        # วิเคราะห์ปัญหา
        if len(strict) == 0:
            print(f"\n   [PROBLEM] ไม่มีหุ้นผ่านเกณฑ์ Strict")
            
            # หุ้นที่มี Prob > 60% แต่ RRR <= 2.0
            high_prob_low_rrr = market_df[(market_df['Prob%'] > 60.0) & (market_df['RR_Ratio'] <= 2.0)]
            if not high_prob_low_rrr.empty:
                print(f"   - หุ้นที่มี Prob > 60% แต่ RRR <= 2.0: {len(high_prob_low_rrr)} symbols")
                print(f"     Top 3: {', '.join(high_prob_low_rrr.nlargest(3, 'Prob%')['symbol'].tolist())}")
            
            # หุ้นที่มี RRR > 2.0 แต่ Prob <= 60%
            high_rrr_low_prob = market_df[(market_df['RR_Ratio'] > 2.0) & (market_df['Prob%'] <= 60.0)]
            if not high_rrr_low_prob.empty:
                print(f"   - หุ้นที่มี RRR > 2.0 แต่ Prob <= 60%: {len(high_rrr_low_prob)} symbols")
                print(f"     Top 3: {', '.join(high_rrr_low_prob.nlargest(3, 'RR_Ratio')['symbol'].tolist())}")


def analyze_trade_details(df_trades):
    """วิเคราะห์รายละเอียดการเทรด"""
    print("\n" + "="*100)
    print("[DETAIL] วิเคราะห์รายละเอียดการเทรด")
    print("="*100)
    
    if df_trades.empty:
        print("[WARNING] ไม่มีข้อมูล trade history")
        return
    
        # แยกตามประเทศ
        for country in ['TH', 'US', 'CN', 'TW']:
            if 'Country' not in df_trades.columns:
                break
            country_trades = df_trades[df_trades['Country'] == country]
            if country_trades.empty:
                continue
        
        print(f"\n[{country}] {len(country_trades)} trades")
        print("-" * 80)
        
        # วิเคราะห์ตาม engine/strategy
        if 'engine' in country_trades.columns:
            engine_counts = country_trades['engine'].value_counts()
            print(f"   Engines: {dict(engine_counts)}")
        
        # วิเคราะห์ตาม forecast
        if 'forecast' in country_trades.columns:
            forecast_counts = country_trades['forecast'].value_counts()
            print(f"   Forecasts: {dict(forecast_counts)}")
        
        # วิเคราะห์ผลลัพธ์
        if 'actual_return' in country_trades.columns:
            country_trades['actual_return'] = pd.to_numeric(country_trades['actual_return'], errors='coerce')
            avg_return = country_trades['actual_return'].mean()
            win_rate = (country_trades['actual_return'] > 0).mean() * 100
            print(f"   Avg Return: {avg_return:.3f}%")
            print(f"   Win Rate: {win_rate:.1f}%")


def analyze_engine_issues(df_metrics, df_trades):
    """วิเคราะห์ปัญหาของแต่ละ Engine"""
    print("\n" + "="*100)
    print("[ENGINE ISSUES] วิเคราะห์ปัญหาของแต่ละ Engine")
    print("="*100)
    
    # 1. TREND_MOMENTUM (US, TW)
    print("\n[1] TREND_MOMENTUM Engine (US, TW)")
    print("-" * 80)
    
    us_tw = df_metrics[df_metrics['Country'].isin(['US', 'TW'])]
    if not us_tw.empty:
        print(f"   Total Symbols: {len(us_tw)}")
        print(f"   Prob Mean: {us_tw['Prob%'].mean():.1f}% (Target: >= 55%)")
        print(f"   RRR Mean: {us_tw['RR_Ratio'].mean():.2f} (Target: >= 1.2)")
        
        # ปัญหาที่เป็นไปได้
        print(f"\n   [PROBLEMS] ปัญหาที่เป็นไปได้:")
        print(f"   1. ADX Filter (>= 20) อาจเข้มงวดเกินไป → ลดโอกาสหา signal")
        print(f"   2. Regime-Aware History Scan อาจลด sample size มากเกินไป")
        print(f"   3. LONG ONLY สำหรับ US อาจพลาดโอกาส SHORT")
        print(f"   4. Threshold 0.6% อาจสูงเกินไปสำหรับ US")
        print(f"   5. Trend Following อาจไม่เหมาะกับตลาดที่ volatile สูง")
    
    # 2. MEAN_REVERSION (TH, CN)
    print("\n[2] MEAN_REVERSION Engine (TH, CN)")
    print("-" * 80)
    
    th_cn = df_metrics[df_metrics['Country'].isin(['TH', 'CN'])]
    if not th_cn.empty:
        th = df_metrics[df_metrics['Country'] == 'TH']
        cn = df_metrics[df_metrics['Country'] == 'CN']
        
        print(f"   THAI: {len(th)} symbols, Prob Mean: {th['Prob%'].mean():.1f}%, RRR Mean: {th['RR_Ratio'].mean():.2f}")
        print(f"   CHINA: {len(cn)} symbols, Prob Mean: {cn['Prob%'].mean():.1f}%, RRR Mean: {cn['RR_Ratio'].mean():.2f}")
        
        print(f"\n   [PROBLEMS] ปัญหาที่เป็นไปได้:")
        print(f"   THAI: ทำงานดีมาก (Prob 58.2%, RRR 1.37)")
        print(f"   CHINA:")
        print(f"   1. Volume Ratio Filter (VR < 0.5) อาจเข้มงวดเกินไป")
        print(f"   2. Regime Filter (LONG only if Price > SMA50) อาจพลาดโอกาส")
        print(f"   3. Threshold 0.5% อาจต่ำเกินไป → noise มาก")
        print(f"   4. Mean Reversion อาจไม่เหมาะกับตลาดที่ trending มาก")


def suggest_improvements():
    """เสนอแนวทางปรับปรุง"""
    print("\n" + "="*100)
    print("[IMPROVEMENTS] แนวทางปรับปรุง Logic Engine")
    print("="*100)
    
    # 1. US Market (Trend Following)
    print("\n[1] US Market - Trend Following Improvements")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Engine: TREND_MOMENTUM")
    print("   - ADX >= 20 (เข้มงวด)")
    print("   - LONG ONLY")
    print("   - Threshold: 0.6%")
    print("   - Regime-Aware History Scan")
    print("   - Gatekeeper: Prob >= 60%, Count >= 15")
    
    print("\n   [PROPOSED CHANGES]")
    print("   1. ลด ADX Threshold: 20 → 15 (เพิ่มโอกาสหา signal)")
    print("   2. เพิ่ม Multi-Timeframe Analysis: ดู trend ในหลาย timeframe")
    print("   3. ใช้ Volume Confirmation: ต้องมี volume spike")
    print("   4. ปรับ Threshold: 0.6% → 0.5% (ลด noise แต่เพิ่มโอกาส)")
    print("   5. ใช้ Expectancy แทน RRR: เน้นความคุ้มค่า")
    print("   6. ลด Gatekeeper: Prob >= 55%, Count >= 10")
    print("   7. เพิ่ม Momentum Filter: ใช้ RSI หรือ MACD")
    print("   8. ใช้ Partial Entry: เข้า 50% ที่ signal, 50% ที่ pullback")
    
    # 2. China Market (Mean Reversion)
    print("\n[2] China Market - Mean Reversion Improvements")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Engine: MEAN_REVERSION")
    print("   - VR Filter: VR < 0.5 (skip)")
    print("   - Regime Filter: LONG only if Price > SMA50")
    print("   - Threshold: 0.5%")
    print("   - Gatekeeper: Prob >= 60%, Count >= 15")
    
    print("\n   [PROPOSED CHANGES]")
    print("   1. ลด VR Filter: 0.5 → 0.3 (เพิ่มโอกาส)")
    print("   2. เพิ่ม Volume Spike Filter: VR > 1.5 (ต้องมี volume)")
    print("   3. ใช้ Bollinger Bands: เข้าเมื่อ price แตะ upper/lower band")
    print("   4. ปรับ Threshold: 0.5% → 0.7% (ลด noise)")
    print("   5. เพิ่ม RSI Filter: RSI > 70 (SHORT), RSI < 30 (LONG)")
    print("   6. ใช้ Support/Resistance: เข้าเมื่อ price แตะ S/R")
    print("   7. ลด Gatekeeper: Prob >= 55%, Count >= 10")
    print("   8. ใช้ Volatility Targeting: ปรับ position size ตาม volatility")
    
    # 3. Taiwan Market (Trend Following)
    print("\n[3] Taiwan Market - Trend Following Improvements")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Engine: TREND_MOMENTUM")
    print("   - ADX >= 20")
    print("   - Threshold: 0.5%")
    
    print("\n   [PROPOSED CHANGES]")
    print("   1. ลด ADX Threshold: 20 → 15")
    print("   2. ใช้ Sector Rotation: เน้นหุ้น tech/semiconductor")
    print("   3. เพิ่ม Volume Confirmation")
    print("   4. ใช้ Multi-Timeframe: ดู trend ใน daily + weekly")
    print("   5. ลด Gatekeeper: Prob >= 52%, Count >= 10")


def suggest_new_engines():
    """เสนอ Engine ใหม่ที่เหมาะกับแต่ละตลาด"""
    print("\n" + "="*100)
    print("[NEW ENGINES] เสนอ Engine ใหม่ที่เหมาะกับแต่ละตลาด")
    print("="*100)
    
    # 1. Hybrid Engine สำหรับ US
    print("\n[1] Hybrid Trend-Momentum Engine (US)")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - รวม Trend Following + Momentum + Volume Confirmation")
    print("   - ใช้ Multi-Timeframe Analysis")
    print("   - ใช้ Expectancy แทน RRR")
    print("   - LONG ONLY แต่มี Short Hedge")
    
    print("\n   [LOGIC]")
    print("   1. ADX >= 15 (ลดจาก 20)")
    print("   2. Price > SMA50 (uptrend)")
    print("   3. Volume > 1.2x Average Volume")
    print("   4. RSI 40-60 (ไม่ overbought/oversold)")
    print("   5. MACD Bullish Crossover")
    print("   6. Threshold: 0.5% (dynamic)")
    print("   7. Gatekeeper: Expectancy > 0.3%, Count >= 10")
    
    # 2. Smart Reversion Engine สำหรับ China
    print("\n[2] Smart Reversion Engine (China)")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - Mean Reversion + Volume + Support/Resistance")
    print("   - ใช้ Bollinger Bands")
    print("   - ใช้ RSI Filter")
    print("   - Volatility Targeting")
    
    print("\n   [LOGIC]")
    print("   1. Price แตะ Upper/Lower Bollinger Band")
    print("   2. RSI > 70 (SHORT) หรือ RSI < 30 (LONG)")
    print("   3. Volume > 1.5x Average (volume spike)")
    print("   4. Price ใกล้ Support/Resistance")
    print("   5. Threshold: 0.7% (dynamic)")
    print("   6. Gatekeeper: Expectancy > 0.4%, Count >= 10")
    
    # 3. Adaptive Engine สำหรับ Taiwan
    print("\n[3] Adaptive Engine (Taiwan)")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - เปลี่ยนระหว่าง Trend และ Reversion ตาม Market Regime")
    print("   - ใช้ ADX เพื่อตัดสินใจ")
    print("   - ADX > 25 → Trend Following")
    print("   - ADX < 25 → Mean Reversion")
    
    print("\n   [LOGIC]")
    print("   1. Calculate ADX")
    print("   2. If ADX > 25: ใช้ Trend Following")
    print("   3. If ADX < 25: ใช้ Mean Reversion")
    print("   4. Threshold: 0.5% (dynamic)")
    print("   5. Gatekeeper: Expectancy > 0.3%, Count >= 10")


def suggest_filtering_changes():
    """เสนอการปรับ Filtering Logic"""
    print("\n" + "="*100)
    print("[FILTERING] เสนอการปรับ Filtering Logic")
    print("="*100)
    
    print("\n[1] เปลี่ยนจาก Prob + RRR เป็น Expectancy")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Filter: Prob >= 60% AND RRR >= 2.0")
    print("   - Problem: เข้มงวดเกินไป → ไม่มีหุ้นผ่าน")
    
    print("\n   [PROPOSED]")
    print("   - Filter: Expectancy > 0.5%")
    print("   - Formula: Expectancy = (Win Rate × Avg Win%) - (Loss Rate × Avg Loss%)")
    print("   - Benefit: บอกความคุ้มค่าได้ดีกว่า")
    
    print("\n[2] ใช้ Tier System")
    print("-" * 80)
    print("   - Tier 1 (Elite): Expectancy > 0.8%, Prob >= 65%")
    print("   - Tier 2 (Good): Expectancy > 0.5%, Prob >= 60%")
    print("   - Tier 3 (Fair): Expectancy > 0.3%, Prob >= 55%")
    
    print("\n[3] ใช้ Composite Score")
    print("-" * 80)
    print("   - Score = (Prob% × 0.4) + (RRR × 20) + (Expectancy × 10)")
    print("   - Filter: Score > 50")
    
    print("\n[4] ปรับเกณฑ์ตามตลาด")
    print("-" * 80)
    print("   - THAI: Prob >= 58%, RRR >= 1.3, Expectancy > 0.5%")
    print("   - US: Prob >= 52%, RRR >= 1.5, Expectancy > 0.3%")
    print("   - CHINA: Prob >= 55%, RRR >= 1.3, Expectancy > 0.4%")
    print("   - TAIWAN: Prob >= 52%, RRR >= 1.4, Expectancy > 0.3%")


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[MAIN] วิเคราะห์และปรับ Logic Engine ให้เข้ากับแต่ละตลาด")
    print("="*100)
    
    # โหลดข้อมูล
    df_metrics, df_trades = load_data()
    
    if df_metrics.empty:
        print("[ERROR] ไม่สามารถโหลดข้อมูลได้")
        return
    
    # วิเคราะห์
    analyze_market_performance(df_metrics, df_trades)
    analyze_trade_details(df_trades)
    analyze_engine_issues(df_metrics, df_trades)
    suggest_improvements()
    suggest_new_engines()
    suggest_filtering_changes()
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้นการวิเคราะห์")
    print("="*100)


if __name__ == "__main__":
    main()

