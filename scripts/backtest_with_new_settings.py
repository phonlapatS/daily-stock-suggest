#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backtest ด้วยค่าใหม่ (TP 3.5x, Trailing 2.0%) และเปรียบเทียบผลลัพธ์
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def print_backtest_commands():
    """แสดงคำสั่ง backtest สำหรับแต่ละประเทศ"""
    
    print("\n" + "=" * 160)
    print("คำสั่ง Backtest ด้วยค่าใหม่ (TP 3.5x, Trailing 2.0%)")
    print("=" * 160)
    
    print("""
📋 คำสั่ง Backtest สำหรับแต่ละประเทศ:

1. 🇹🇭 THAI (ไม่ต้อง backtest - ใช้ค่าเดิม):
   python scripts/backtest.py --group THAI_STOCK

2. 🇺🇸 US (TP 3.5x, Trailing 2.0%, Max Hold 7 days):
   python scripts/backtest.py --group US_STOCK --atr_tp_mult 3.5 --trail_activate 2.0 --max_hold 7

3. 🇨🇳 CHINA/HK (TP 3.5x, Trailing 2.0%, Max Hold 8 days):
   python scripts/backtest.py --group CHINA_STOCK --atr_tp_mult 3.5 --trail_activate 2.0 --max_hold 8

4. 🇹🇼 TAIWAN (TP 3.5x, Trailing 2.0%, Max Hold 10 days):
   python scripts/backtest.py --group TAIWAN_STOCK --atr_tp_mult 3.5 --trail_activate 2.0 --max_hold 10

⚠️  หมายเหตุ:
   - การ backtest อาจใช้เวลานาน (10-30 นาทีต่อประเทศ)
   - หลัง backtest เสร็จ ให้รัน: python scripts/compare_before_after_tp_adjustment.py
   - เพื่อดูผลลัพธ์เปรียบเทียบ
    """)
    print("=" * 160)
    
    # ถามว่าต้องการ backtest ทันทีหรือไม่
    print("\nต้องการ backtest ทันทีหรือไม่? (y/n)")
    print("(ถ้า y จะ backtest ทีละประเทศ - อาจใช้เวลานาน)")

if __name__ == "__main__":
    print_backtest_commands()

