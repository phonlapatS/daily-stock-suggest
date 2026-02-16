#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
improve_us_market_trend_following.py - ปรับปรุงตลาดหุ้นอเมริกาให้เหมาะสมกับ Trend Following Long Only
================================================================================

เป้าหมาย:
1. เสถียร (Stable)
2. ไม่เจอ noise เยอะ (Less Noise)
3. ไม่เสี่ยง overfit (Avoid Overfitting)
4. ได้กำไรมากกว่าเสีย (Positive Expectancy)
5. มีความเสี่ยงน้อย (Low Risk)
6. ตรงกับพฤติกรรม Trend Following Long Only

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


def analyze_current_us_market(df):
    """วิเคราะห์สถานการณ์ปัจจุบันของ US Market"""
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์สถานการณ์ปัจจุบันของ US Market")
    print("="*100)
    
    us_df = df[df['Country'] == 'US']
    if us_df.empty:
        print("❌ ไม่มีข้อมูล US Market")
        return None
    
    print(f"\n📊 สถิติ US Market ({len(us_df)} symbols)")
    print("-" * 80)
    print(f"   Prob%: Mean={us_df['Prob%'].mean():.1f}%, Min={us_df['Prob%'].min():.1f}%, Max={us_df['Prob%'].max():.1f}%")
    print(f"   RRR: Mean={us_df['RR_Ratio'].mean():.2f}, Min={us_df['RR_Ratio'].min():.2f}, Max={us_df['RR_Ratio'].max():.2f}")
    print(f"   AvgWin%: Mean={us_df['AvgWin%'].mean():.2f}%, Max={us_df['AvgWin%'].max():.2f}%")
    print(f"   AvgLoss%: Mean={us_df['AvgLoss%'].mean():.2f}%, Max={us_df['AvgLoss%'].max():.2f}%")
    print(f"   Count: Mean={us_df['Count'].mean():.0f}, Min={us_df['Count'].min():.0f}, Max={us_df['Count'].max():.0f}")
    
    # Calculate Expectancy
    us_df['Win_Rate'] = us_df['Prob%'] / 100
    us_df['Loss_Rate'] = 1 - us_df['Win_Rate']
    us_df['Expectancy'] = (
        us_df['Win_Rate'] * us_df['AvgWin%'] - 
        us_df['Loss_Rate'] * us_df['AvgLoss%']
    )
    
    print(f"\n   Expectancy: Mean={us_df['Expectancy'].mean():.2f}%, Min={us_df['Expectancy'].min():.2f}%, Max={us_df['Expectancy'].max():.2f}%")
    
    # Problems
    print(f"\n   [ปัญหาที่พบ]")
    print(f"   1. Prob Mean={us_df['Prob%'].mean():.1f}% ต่ำ (Trend Following มี Prob ต่ำ)")
    print(f"   2. RRR Mean={us_df['RR_Ratio'].mean():.2f} ต่ำ (ใกล้ 1.0)")
    print(f"   3. AvgLoss Mean={us_df['AvgLoss%'].mean():.2f}% สูง (ความเสี่ยงสูง)")
    print(f"   4. Expectancy Mean={us_df['Expectancy'].mean():.2f}% ต่ำ (กำไรน้อย)")
    
    return us_df


def suggest_improvements():
    """เสนอแนวทางปรับปรุง"""
    print("\n" + "="*100)
    print("[IMPROVEMENTS] แนวทางปรับปรุง US Market สำหรับ Trend Following Long Only")
    print("="*100)
    
    print("\n[1] ปรับ Engine Settings")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - ADX >= 20 (เข้มงวดเกินไป → signal น้อย)")
    print("   - Threshold: 0.6% (อาจสูงเกินไป → noise มาก)")
    print("   - Gatekeeper: Prob >= 60%, Count >= 15 (เข้มงวด)")
    print("   - LONG ONLY ✅")
    print("   - Regime-Aware History Scan ✅")
    
    print("\n   [PROPOSED CHANGES]")
    print("   1. ADX Threshold: 20 → 15 (เพิ่มโอกาสหา signal)")
    print("      - หรือใช้ Adaptive ADX: ADX >= 15 AND ADX < 40 (หลีกเลี่ยง extreme)")
    print("   2. Threshold: 0.6% → 0.5% (ลด noise แต่ยังคงความหมาย)")
    print("      - หรือใช้ Dynamic Threshold: max(SD20, SD252, 0.5%)")
    print("   3. Gatekeeper: Prob >= 55%, Count >= 10 (ลดความเข้มงวด)")
    print("      - หรือใช้ Expectancy > 0.3% แทน Prob")
    
    print("\n[2] เพิ่ม Volume Confirmation")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ต้องมี Volume Spike เพื่อยืนยัน Trend")
    print("   - Volume > 1.2x Average Volume (20-day)")
    print("   - ลด noise จาก false breakout")
    
    print("\n   [IMPLEMENTATION]")
    print("   - เพิ่ม Volume Ratio Filter")
    print("   - Volume Ratio = Current Volume / Average Volume (20-day)")
    print("   - Require: Volume Ratio >= 1.2")
    
    print("\n[3] เพิ่ม Multi-Timeframe Analysis")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ดู Trend ในหลาย Timeframe")
    print("   - Daily: Signal Entry")
    print("   - Weekly: Trend Context")
    print("   - Monthly: Major Trend")
    
    print("\n   [IMPLEMENTATION]")
    print("   - Daily: ADX >= 15, Price > SMA50")
    print("   - Weekly: Price > SMA20 (weekly), Uptrend")
    print("   - Monthly: Price > SMA12 (monthly), Uptrend")
    print("   - Entry เมื่อ Daily + Weekly + Monthly อยู่ใน Uptrend")
    
    print("\n[4] เพิ่ม Momentum Filter (Volume-based แทน RSI)")
    print("-" * 80)
    print("   [NOTE]")
    print("   - RSI ถูกถอดออกจาก Engine แล้ว (V5.0: conflicts with core concept)")
    print("   - แต่สำหรับ Trend Following อาจใช้ Volume-based Momentum แทน")
    
    print("\n   [CONCEPT]")
    print("   - ใช้ Volume Confirmation เพื่อยืนยัน Momentum")
    print("   - Volume Spike = Momentum Strong")
    print("   - Volume Ratio > 1.2x = Strong Trend")
    
    print("\n   [IMPLEMENTATION]")
    print("   - Volume Ratio Filter: Volume > 1.2x Average Volume (20-day)")
    print("   - Price Momentum: Price > SMA20 (short-term trend)")
    print("   - หรือใช้ ADX > 15 (trend strength) แทน RSI")
    
    print("\n[5] ปรับ Position Sizing ตาม Volatility")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - หุ้นที่มี Volatility สูง → ลงทุนน้อยกว่า")
    print("   - หุ้นที่มี Volatility ต่ำ → ลงทุนมากกว่า")
    print("   - ลดความเสี่ยงจาก Volatility")
    
    print("\n   [IMPLEMENTATION]")
    print("   - Position Size = Base Size × (Target Volatility / Current Volatility)")
    print("   - Target Volatility = 20% (annual)")
    print("   - Current Volatility = 20-day Rolling SD × sqrt(252)")
    print("   - Cap: Min=0.5%, Max=3%")
    
    print("\n[6] ใช้ Trailing Stop Loss")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - Trend Following ต้องให้กำไรเดินทาง")
    print("   - ใช้ Trailing Stop เพื่อ lock profit")
    print("   - Trailing Stop = High - (ATR × 2)")
    
    print("\n   [IMPLEMENTATION]")
    print("   - Initial Stop Loss = Entry - (ATR × 2)")
    print("   - Trailing Stop = High - (ATR × 2)")
    print("   - Update เมื่อ High ใหม่")
    
    print("\n[7] ปรับ Filtering Criteria")
    print("-" * 80)
    print("   [CURRENT]")
    print("   - Prob >= 55%, RRR >= 1.2, AvgWin > 1.5%, AvgLoss < 2.5%")
    
    print("\n   [PROPOSED]")
    print("   - Prob >= 52% (ลดจาก 55% - เพราะ Trend Following มี Prob ต่ำ)")
    print("   - RRR >= 1.0 (ลดจาก 1.2 - เพราะ US มี RRR ต่ำ)")
    print("   - AvgWin > 1.0% (ลดจาก 1.5% - เพราะ US มี AvgWin ต่ำ)")
    print("   - AvgLoss < 3.0% (เพิ่มจาก 2.5% - เพราะ US มี AvgLoss สูง)")
    print("   - Expectancy > 0.2% (เพิ่ม - เพื่อให้ได้กำไรมากกว่าเสีย)")
    print("   - Count >= 10 (ลดจาก 15 - เพื่อให้ได้หุ้นมากขึ้น)")
    
    print("\n[8] หลีกเลี่ยง Overfitting")
    print("-" * 80)
    print("   [CONCEPT]")
    print("   - ใช้ Simple Rules (ไม่ซับซ้อน)")
    print("   - ใช้ Out-of-Sample Testing")
    print("   - ใช้ Walk-Forward Analysis")
    print("   - หลีกเลี่ยง Curve Fitting")
    
    print("\n   [IMPLEMENTATION]")
    print("   - ใช้ Fixed Rules (ไม่ปรับตามผลลัพธ์)")
    print("   - Test on Different Time Periods")
    print("   - Use Cross-Validation")
    print("   - Monitor Performance Over Time")


def create_improved_filter(df):
    """สร้าง Filter ที่ปรับปรุงแล้ว"""
    print("\n" + "="*100)
    print("[FILTER] Filter ที่ปรับปรุงแล้วสำหรับ US Market")
    print("="*100)
    
    us_df = df[df['Country'] == 'US'].copy()
    if us_df.empty:
        print("❌ ไม่มีข้อมูล US Market")
        return None
    
    # Calculate Expectancy
    us_df['Win_Rate'] = us_df['Prob%'] / 100
    us_df['Loss_Rate'] = 1 - us_df['Win_Rate']
    us_df['Expectancy'] = (
        us_df['Win_Rate'] * us_df['AvgWin%'] - 
        us_df['Loss_Rate'] * us_df['AvgLoss%']
    )
    
    # Current filter
    current = us_df[
        (us_df['Prob%'] >= 55.0) & 
        (us_df['RR_Ratio'] >= 1.2) &
        (us_df['AvgWin%'] > 1.5) &
        (us_df['AvgLoss%'] < 2.5) &
        (us_df['Count'] >= 10)
    ]
    
    # Improved filter
    improved = us_df[
        (us_df['Prob%'] >= 52.0) &  # ลดจาก 55%
        (us_df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2
        (us_df['AvgWin%'] > 1.0) &  # ลดจาก 1.5%
        (us_df['AvgLoss%'] < 3.0) &  # เพิ่มจาก 2.5%
        (us_df['Expectancy'] > 0.2) &  # เพิ่ม - เพื่อให้ได้กำไรมากกว่าเสีย
        (us_df['Count'] >= 10)  # ลดจาก 15
    ]
    
    print(f"\n[1] เกณฑ์ปัจจุบัน")
    print("-" * 80)
    print(f"   Prob >= 55%, RRR >= 1.2, AvgWin > 1.5%, AvgLoss < 2.5%, Count >= 10")
    print(f"   ผลลัพธ์: {len(current)} symbols")
    
    print(f"\n[2] เกณฑ์ปรับปรุงแล้ว")
    print("-" * 80)
    print(f"   Prob >= 52%, RRR >= 1.0, AvgWin > 1.0%, AvgLoss < 3.0%, Expectancy > 0.2%, Count >= 10")
    print(f"   ผลลัพธ์: {len(improved)} symbols")
    
    print(f"\n[3] เปรียบเทียบ")
    print("-" * 80)
    print(f"   เพิ่มขึ้น: {len(improved) - len(current)} symbols ({((len(improved) - len(current)) / len(us_df) * 100):.1f}% ของทั้งหมด)")
    
    if not improved.empty:
        print(f"\n[4] Top 10 หุ้นที่ผ่านเกณฑ์ปรับปรุงแล้ว")
        print("-" * 80)
        top10 = improved.nlargest(10, 'Expectancy')
        print(f"{'Symbol':<10} {'Prob%':>6} {'RRR':>5} {'AvgWin%':>8} {'AvgLoss%':>9} {'Expectancy':>10} {'Count':>6}")
        print("-" * 80)
        for _, row in top10.iterrows():
            print(f"{row['symbol']:<10} {row['Prob%']:>5.1f}% {row['RR_Ratio']:>4.2f} "
                  f"{row['AvgWin%']:>7.2f}% {row['AvgLoss%']:>8.2f}% {row['Expectancy']:>9.2f}% {row['Count']:>5.0f}")
    
    return improved


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[IMPROVE US MARKET] ปรับปรุงตลาดหุ้นอเมริกาให้เหมาะสมกับ Trend Following Long Only")
    print("="*100)
    
    # Load data
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    # Analyze
    us_df = analyze_current_us_market(df)
    
    # Suggest improvements
    suggest_improvements()
    
    # Create improved filter
    improved = create_improved_filter(df)
    
    print("\n" + "="*100)
    print("[SUMMARY] สรุป")
    print("="*100)
    print("\n💡 แนวทางปรับปรุงหลัก:")
    print("   1. ✅ ลด ADX: 20 → 15 (เพิ่มโอกาสหา signal)")
    print("   2. ✅ ลด Threshold: 0.6% → 0.5% (ลด noise)")
    print("   3. ✅ เพิ่ม Volume Confirmation (ลด false breakout)")
    print("   4. ✅ เพิ่ม Multi-Timeframe Analysis (ยืนยัน trend)")
    print("   5. ✅ เพิ่ม Momentum Filter (Volume-based แทน RSI)")
    print("   6. ✅ ปรับ Position Sizing ตาม Volatility (ลดความเสี่ยง)")
    print("   7. ✅ ใช้ Trailing Stop Loss (lock profit)")
    print("   8. ✅ ปรับ Filtering Criteria (Prob 52%, RRR 1.0, Expectancy > 0.2%)")
    print("   9. ✅ หลีกเลี่ยง Overfitting (ใช้ Simple Rules)")
    
    print("\n🎯 ผลลัพธ์:")
    if improved is not None and not improved.empty:
        print(f"   - ได้หุ้นมากขึ้น: {len(improved)} symbols")
        print(f"   - Expectancy Mean: {improved['Expectancy'].mean():.2f}%")
        print(f"   - Prob Mean: {improved['Prob%'].mean():.1f}%")
        print(f"   - RRR Mean: {improved['RR_Ratio'].mean():.2f}")


if __name__ == "__main__":
    main()

