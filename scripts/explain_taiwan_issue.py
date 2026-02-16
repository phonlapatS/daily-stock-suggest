#!/usr/bin/env python
"""
Explain Taiwan Issue - อธิบายปัญหาหุ้นไต้หวัน
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def explain_taiwan_issue():
    """อธิบายปัญหาหุ้นไต้หวัน"""
    
    print("="*80)
    print("Explain Taiwan Issue - อธิบายปัญหาหุ้นไต้หวัน")
    print("="*80)
    print()
    
    print("🔍 สาเหตุที่หุ้นไต้หวันไม่ขึ้น:")
    print("-" * 80)
    print()
    print("1. ✅ มีหุ้นไต้หวัน 10 ตัวใน full_backtest_results.csv")
    print("   - 2330, 2454, 2317, 2303, 2308, 2382, 3711, 3008, 2357, 2395")
    print()
    print("2. ❌ แต่ไม่มี trade_history_TAIWAN.csv ใน logs/")
    print("   - calculate_metrics.py ใช้ trade_history_*.csv เพื่อคำนวณ metrics")
    print("   - ไม่มีไฟล์นี้ = ไม่สามารถคำนวณ Prob%, RRR, Count ได้")
    print()
    print("3. 🔄 เมื่อรัน backtest:")
    print("   - พบ 10 existing results → skip ทั้งหมด")
    print("   - ไม่ได้ process symbols ใหม่ → ไม่มี trades ที่จะบันทึก")
    print("   - ไม่มี trade_history_TAIWAN.csv → ไม่มี metrics")
    print()
    print("💡 วิธีแก้ไข:")
    print("-" * 80)
    print()
    print("Option 1: ลบ cache และรัน backtest ใหม่")
    print("   python scripts/clean_all_cache.py --market TAIWAN")
    print("   python scripts/backtest.py --full --bars 2500 --group TAIWAN")
    print()
    print("Option 2: ลบเฉพาะ full_backtest_results.csv entries")
    print("   - ลบ entries ของหุ้นไต้หวันออกจาก full_backtest_results.csv")
    print("   - รัน backtest ใหม่")
    print()
    print("Option 3: ใช้ข้อมูลจาก full_backtest_results.csv โดยตรง")
    print("   - แก้ไข calculate_metrics.py ให้อ่านจาก full_backtest_results.csv")
    print("   - แต่จะไม่มี detailed trade information")
    print()
    print("="*80)

if __name__ == '__main__':
    explain_taiwan_issue()

