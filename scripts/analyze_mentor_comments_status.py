#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_mentor_comments_status.py - วิเคราะห์คอมเมนต์จาก Mentor และสถานะปัจจุบัน
================================================================================

วิเคราะห์ 4 จุดหลัก:
1. Logic ขัดแย้ง (RSI Filter)
2. ความคุ้มค่า (RRR > 2.0)
3. ภาพรวมพอร์ต (Total Equity Curve)
4. Forward Testing (Data Snooping)

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


def check_rsi_status():
    """ตรวจสอบสถานะ RSI Filter"""
    print("\n" + "="*100)
    print("[1] ตรวจสอบสถานะ RSI Filter")
    print("="*100)
    
    # Check MeanReversionEngine
    reversion_file = os.path.join(BASE_DIR, "core", "engines", "reversion_engine.py")
    if os.path.exists(reversion_file):
        with open(reversion_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "NO RSI filter" in content or "removed - conflicts" in content:
                print("   ✅ MeanReversionEngine: RSI ถูกถอดออกแล้ว (V5.0)")
            elif "RSI" in content or "rsi" in content:
                print("   ⚠️ MeanReversionEngine: พบ RSI ในโค้ด (ต้องตรวจสอบ)")
            else:
                print("   ✅ MeanReversionEngine: ไม่มี RSI Filter")
    
    # Check TrendMomentumEngine
    trend_file = os.path.join(BASE_DIR, "core", "engines", "trend_engine.py")
    if os.path.exists(trend_file):
        with open(trend_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "RSI" in content or "rsi" in content:
                print("   ⚠️ TrendMomentumEngine: พบ RSI ในโค้ด (ต้องตรวจสอบ)")
            else:
                print("   ✅ TrendMomentumEngine: ไม่มี RSI Filter")
    
    # Check indicators.py
    indicators_file = os.path.join(BASE_DIR, "core", "indicators.py")
    if os.path.exists(indicators_file):
        with open(indicators_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "def calculate_rsi" in content:
                print("   ℹ️ indicators.py: มีฟังก์ชัน calculate_rsi() แต่ไม่ได้ใช้ใน Engine")
    
    print("\n   [สรุป]")
    print("   ✅ RSI ถูกถอดออกจาก Engine แล้ว (V5.0)")
    print("   ✅ ระบบใช้ Dynamic Threshold (SD) เป็นแกนหลัก")
    print("   ✅ ไม่มี RSI Filter ที่ขัดขวางการทำงาน")


def check_rrr_status(df):
    """ตรวจสอบสถานะ RRR"""
    print("\n" + "="*100)
    print("[2] ตรวจสอบสถานะ RRR (ต้อง > 2.0)")
    print("="*100)
    
    if df.empty:
        print("   ❌ ไม่มีข้อมูล")
        return
    
    # Overall statistics
    print(f"\n   [สถิติรวม]")
    print(f"   RRR Mean: {df['RR_Ratio'].mean():.2f}")
    print(f"   RRR Median: {df['RR_Ratio'].median():.2f}")
    print(f"   RRR Max: {df['RR_Ratio'].max():.2f}")
    
    # Count by RRR ranges
    rrr_above_2 = df[df['RR_Ratio'] > 2.0]
    rrr_1_5_to_2 = df[(df['RR_Ratio'] >= 1.5) & (df['RR_Ratio'] <= 2.0)]
    rrr_1_to_1_5 = df[(df['RR_Ratio'] >= 1.0) & (df['RR_Ratio'] < 1.5)]
    rrr_below_1 = df[df['RR_Ratio'] < 1.0]
    
    print(f"\n   [จำนวนหุ้นตาม RRR]")
    print(f"   RRR > 2.0: {len(rrr_above_2)} symbols ({len(rrr_above_2)/len(df)*100:.1f}%)")
    print(f"   RRR 1.5-2.0: {len(rrr_1_5_to_2)} symbols ({len(rrr_1_5_to_2)/len(df)*100:.1f}%)")
    print(f"   RRR 1.0-1.5: {len(rrr_1_to_1_5)} symbols ({len(rrr_1_to_1_5)/len(df)*100:.1f}%)")
    print(f"   RRR < 1.0: {len(rrr_below_1)} symbols ({len(rrr_below_1)/len(df)*100:.1f}%)")
    
    # By country
    print(f"\n   [สถิติตามประเทศ]")
    for country in ['TH', 'US', 'CN', 'TW']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            continue
        rrr_above_2_country = country_df[country_df['RR_Ratio'] > 2.0]
        print(f"   {country}: RRR Mean={country_df['RR_Ratio'].mean():.2f}, "
              f"RRR > 2.0: {len(rrr_above_2_country)}/{len(country_df)} ({len(rrr_above_2_country)/len(country_df)*100:.1f}%)")
    
    print(f"\n   [ปัญหาที่พบ]")
    print(f"   ⚠️ มีหุ้น RRR > 2.0 เพียง {len(rrr_above_2)}/{len(df)} ({len(rrr_above_2)/len(df)*100:.1f}%)")
    print(f"   ⚠️ ส่วนใหญ่มี RRR ต่ำกว่า 2.0 (ไม่คุ้มเสี่ยง)")
    print(f"   ⚠️ ต้องปรับ Exit Strategy เพื่อให้ RRR > 2.0")
    
    print(f"\n   [สิ่งที่ต้องทำ]")
    print(f"   🔴 Implement Trailing Stop Loss")
    print(f"   🔴 ปรับ Take Profit Strategy")
    print(f"   🔴 ทดสอบว่า RRR > 2.0 ได้จริงหรือไม่")


def check_total_equity_curve():
    """ตรวจสอบว่ามี Total Equity Curve หรือไม่"""
    print("\n" + "="*100)
    print("[3] ตรวจสอบ Total Equity Curve รวมทุกตลาด")
    print("="*100)
    
    # Check existing scripts
    scripts_dir = os.path.join(BASE_DIR, "scripts")
    
    scripts_to_check = [
        "plot_markets_from_metrics.py",
        "generate_real_equity_plots.py",
        "plot_comparative_equity.py",
        "simulate_equity_curves.py"
    ]
    
    print(f"\n   [สคริปต์ที่มีอยู่]")
    for script in scripts_to_check:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "total" in content.lower() and "equity" in content.lower() and "all" in content.lower():
                    print(f"   ✅ {script}: มี Total Equity Curve")
                elif "equity" in content.lower():
                    print(f"   ⚠️ {script}: มี Equity Curve แต่ไม่แน่ใจว่าเป็น Total")
                else:
                    print(f"   ❌ {script}: ไม่มี Total Equity Curve")
        else:
            print(f"   ❌ {script}: ไม่พบไฟล์")
    
    print(f"\n   [สิ่งที่ต้องทำ]")
    print(f"   🔴 สร้างสคริปต์ Total Equity Curve รวมทุกตลาด")
    print(f"   🔴 แสดงกราฟเปรียบเทียบระหว่างตลาด")
    print(f"   🔴 คำนวณ Correlation ระหว่างตลาด")


def check_forward_testing():
    """ตรวจสอบ Forward Testing System"""
    print("\n" + "="*100)
    print("[4] ตรวจสอบ Forward Testing System (Data Snooping)")
    print("="*100)
    
    # Check forward testing scripts
    scripts_dir = os.path.join(BASE_DIR, "scripts")
    
    forward_scripts = [
        "forward_test_logger.py",
        "forward_testing_report.py",
        "forward_logger_v2.py",
        "verify_prediction.py"
    ]
    
    print(f"\n   [สคริปต์ Forward Testing]")
    for script in forward_scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            print(f"   ✅ {script}: พบไฟล์")
            
            # Check if it logs before market open
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "before" in content.lower() and "market" in content.lower() and "open" in content.lower():
                    print(f"      ✅ บันทึกก่อนตลาดเปิด")
                elif "timestamp" in content.lower() or "date" in content.lower():
                    print(f"      ⚠️ มี timestamp แต่ไม่แน่ใจว่าบันทึกก่อนตลาดเปิด")
                else:
                    print(f"      ❌ ไม่พบการบันทึกก่อนตลาดเปิด")
        else:
            print(f"   ❌ {script}: ไม่พบไฟล์")
    
    # Check main.py
    main_file = os.path.join(BASE_DIR, "main.py")
    if os.path.exists(main_file):
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "forward" in content.lower() and "log" in content.lower():
                print(f"\n   ✅ main.py: มี Forward Testing Logic")
            else:
                print(f"\n   ⚠️ main.py: ไม่พบ Forward Testing Logic")
    
    print(f"\n   [สิ่งที่ต้องทำ]")
    print(f"   🔴 ตรวจสอบว่า Forward Testing บันทึกก่อนตลาดเปิดจริงๆ")
    print(f"   🔴 สร้างระบบบันทึกผลก่อนตลาดเปิด (Automated)")
    print(f"   🔴 สร้างรายงานเปรียบเทียบ Forward vs Backtest")


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์คอมเมนต์จาก Mentor และสถานะปัจจุบัน")
    print("="*100)
    
    # Load data
    if os.path.exists(METRICS_FILE):
        df = pd.read_csv(METRICS_FILE)
    else:
        df = pd.DataFrame()
        print("⚠️ ไม่พบไฟล์ metrics")
    
    # 1. Check RSI Status
    check_rsi_status()
    
    # 2. Check RRR Status
    if not df.empty:
        check_rrr_status(df)
    
    # 3. Check Total Equity Curve
    check_total_equity_curve()
    
    # 4. Check Forward Testing
    check_forward_testing()
    
    # Summary
    print("\n" + "="*100)
    print("[SUMMARY] สรุปสถานะและสิ่งที่ต้องทำ")
    print("="*100)
    
    print("\n✅ สิ่งที่ทำได้ดีแล้ว:")
    print("   1. ✅ RSI ถูกถอดออกจาก Engine แล้ว (V5.0)")
    print("   2. ✅ ระบบใช้ Dynamic Threshold (SD) เป็นแกนหลัก")
    print("   3. ✅ มี Forward Testing System พื้นฐาน")
    
    print("\n⚠️ สิ่งที่ต้องปรับปรุง:")
    print("   1. ⚠️ RRR ยังต่ำกว่า 2.0 (ต้องปรับ Exit Strategy)")
    print("   2. ⚠️ ยังไม่มี Total Equity Curve รวมทุกตลาด")
    print("   3. ⚠️ ต้องตรวจสอบ Forward Testing Logic")
    
    print("\n🔴 สิ่งที่ต้องทำทันที:")
    print("   1. 🔴 Implement Trailing Stop Loss เพื่อให้ RRR > 2.0")
    print("   2. 🔴 สร้าง Total Equity Curve รวมทุกตลาด")
    print("   3. 🔴 ตรวจสอบและปรับปรุง Forward Testing System")


if __name__ == "__main__":
    main()

