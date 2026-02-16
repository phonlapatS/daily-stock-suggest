#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
รัน backtest ด้วยค่าใหม่และเปรียบเทียบผลลัพธ์
"""
import subprocess
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_backtest_and_compare():
    """รัน backtest และเปรียบเทียบผลลัพธ์"""
    
    print("\n" + "=" * 160)
    print("Backtest ด้วยค่าใหม่ (TP 3.5x, Trailing 2.0%) และเปรียบเทียบผลลัพธ์")
    print("=" * 160)
    
    # คำสั่ง backtest สำหรับแต่ละประเทศ
    backtest_commands = {
        'US': [
            'python', 'scripts/backtest.py',
            '--group', 'US_STOCK',
            '--atr_tp_mult', '3.5',
            '--trail_activate', '2.0',
            '--max_hold', '7'
        ],
        'CHINA': [
            'python', 'scripts/backtest.py',
            '--group', 'CHINA_STOCK',
            '--atr_tp_mult', '3.5',
            '--trail_activate', '2.0',
            '--max_hold', '8'
        ],
        'TAIWAN': [
            'python', 'scripts/backtest.py',
            '--group', 'TAIWAN_STOCK',
            '--atr_tp_mult', '3.5',
            '--trail_activate', '2.0',
            '--max_hold', '10'
        ]
    }
    
    print("\n⚠️  หมายเหตุ:")
    print("   - การ backtest อาจใช้เวลานาน (10-30 นาทีต่อประเทศ)")
    print("   - ต้องการ backtest ทันทีหรือไม่? (y/n)")
    print("   - หรือต้องการคำสั่ง backtest เพื่อรันเอง? (c)")
    
    # สำหรับ demo ให้แสดงคำสั่ง
    print("\n" + "=" * 160)
    print("คำสั่ง Backtest สำหรับแต่ละประเทศ:")
    print("=" * 160)
    
    for market, cmd in backtest_commands.items():
        print(f"\n{market}:")
        print(f"  {' '.join(cmd)}")
    
    print("\n" + "=" * 160)
    print("หลัง backtest เสร็จ ให้รัน:")
    print("=" * 160)
    print("  python scripts/compare_before_after_tp_adjustment.py")
    print("=" * 160)

if __name__ == "__main__":
    run_backtest_and_compare()

