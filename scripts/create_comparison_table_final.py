#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
สร้างตารางเปรียบเทียบผลลัพธ์ก่อนและหลังการปรับ TP/Trailing Stop
"""
import pandas as pd
import glob
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def create_comparison_table():
    """สร้างตารางเปรียบเทียบ"""
    
    print("\n" + "=" * 200)
    print("ตารางเปรียบเทียบ: ก่อนและหลังการปรับ TP/Trailing Stop")
    print("=" * 200)
    
    # ข้อมูลก่อนปรับ (จากผลการวิเคราะห์)
    before_data = {
        'US': {
            'tp': 5.0, 'trail_act': 1.5, 'max_hold': 5,
            'tp_exits': 0.0, 'trailing_pct': 72.0, 'sl_pct': 24.9,
            'rrr_actual': 1.10, 'rrr_theoretical': 5.0, 'rrr_ratio': 22.0
        },
        'CHINA': {
            'tp': 5.0, 'trail_act': 1.0, 'max_hold': 3,
            'tp_exits': 0.0, 'trailing_pct': 72.0, 'sl_pct': 24.9,
            'rrr_actual': 1.10, 'rrr_theoretical': 5.0, 'rrr_ratio': 22.0
        },
        'TAIWAN': {
            'tp': 6.5, 'trail_act': 1.0, 'max_hold': 10,
            'tp_exits': 0.1, 'trailing_pct': 65.3, 'sl_pct': 34.4,
            'rrr_actual': 1.06, 'rrr_theoretical': 6.5, 'rrr_ratio': 16.3
        },
        'THAI': {
            'tp': 3.5, 'trail_act': 1.5, 'max_hold': 5,
            'tp_exits': 0.5, 'trailing_pct': 57.1, 'sl_pct': 40.6,
            'rrr_actual': 1.06, 'rrr_theoretical': 2.33, 'rrr_ratio': 45.4
        }
    }
    
    # ข้อมูลหลังปรับ (ค่าที่ตั้งไว้)
    after_data = {
        'US': {
            'tp': 3.5, 'trail_act': 2.0, 'max_hold': 7,
            'tp_exits': 'TBD', 'trailing_pct': 'TBD', 'sl_pct': 'TBD',
            'rrr_actual': 'TBD', 'rrr_theoretical': 3.5, 'rrr_ratio': 'TBD'
        },
        'CHINA': {
            'tp': 3.5, 'trail_act': 2.0, 'max_hold': 8,
            'tp_exits': 'TBD', 'trailing_pct': 'TBD', 'sl_pct': 'TBD',
            'rrr_actual': 'TBD', 'rrr_theoretical': 3.5, 'rrr_ratio': 'TBD'
        },
        'TAIWAN': {
            'tp': 3.5, 'trail_act': 2.0, 'max_hold': 10,
            'tp_exits': 'TBD', 'trailing_pct': 'TBD', 'sl_pct': 'TBD',
            'rrr_actual': 'TBD', 'rrr_theoretical': 3.5, 'rrr_ratio': 'TBD'
        },
        'THAI': {
            'tp': 3.5, 'trail_act': 1.5, 'max_hold': 5,
            'tp_exits': 0.5, 'trailing_pct': 57.1, 'sl_pct': 40.6,
            'rrr_actual': 1.06, 'rrr_theoretical': 2.33, 'rrr_ratio': 45.4
        }
    }
    
    # Table 1: การตั้งค่า
    print("\n" + "=" * 200)
    print("1. การตั้งค่า (Settings) - ก่อนและหลังการปรับ")
    print("=" * 200)
    print(f"{'Market':<12} {'TP (Before)':>15} {'TP (After)':>15} {'Trail Act (Before)':>20} {'Trail Act (After)':>20} {'Max Hold (Before)':>20} {'Max Hold (After)':>20}")
    print("-" * 200)
    
    for market in ['US', 'CHINA', 'TAIWAN', 'THAI']:
        before = before_data[market]
        after = after_data[market]
        print(f"{market:<12} {before['tp']:>14.1f}x {after['tp']:>14.1f}x {before['trail_act']:>19.1f}% {after['trail_act']:>19.1f}% {before['max_hold']:>19.0f} days {after['max_hold']:>19.0f} days")
    
    # Table 2: ผลลัพธ์
    print("\n" + "=" * 200)
    print("2. ผลลัพธ์ (Results) - ก่อนและหลังการปรับ")
    print("=" * 200)
    print(f"{'Market':<12} {'TP Exits (Before)':>20} {'TP Exits (After)':>20} {'Trailing % (Before)':>22} {'Trailing % (After)':>22} {'RRR Actual (Before)':>22} {'RRR Actual (After)':>22} {'RRR Ratio (Before)':>22} {'RRR Ratio (After)':>22}")
    print("-" * 200)
    
    for market in ['US', 'CHINA', 'TAIWAN', 'THAI']:
        before = before_data[market]
        after = after_data[market]
        
        tp_before = f"{before['tp_exits']:.1f}%"
        tp_after = str(after['tp_exits']) if isinstance(after['tp_exits'], str) else f"{after['tp_exits']:.1f}%"
        
        trail_before = f"{before['trailing_pct']:.1f}%"
        trail_after = str(after['trailing_pct']) if isinstance(after['trailing_pct'], str) else f"{after['trailing_pct']:.1f}%"
        
        rrr_before = f"{before['rrr_actual']:.2f}"
        rrr_after = str(after['rrr_actual']) if isinstance(after['rrr_actual'], str) else f"{after['rrr_actual']:.2f}"
        
        ratio_before = f"{before['rrr_ratio']:.1f}%"
        ratio_after = str(after['rrr_ratio']) if isinstance(after['rrr_ratio'], str) else f"{after['rrr_ratio']:.1f}%"
        
        print(f"{market:<12} {tp_before:>19} {tp_after:>19} {trail_before:>21} {trail_after:>21} {rrr_before:>21} {rrr_after:>21} {ratio_before:>21} {ratio_after:>21}")
    
    # Table 3: สรุปการเปลี่ยนแปลง
    print("\n" + "=" * 200)
    print("3. สรุปการเปลี่ยนแปลง")
    print("=" * 200)
    print(f"{'Market':<12} {'TP Change':>15} {'Trail Act Change':>20} {'Max Hold Change':>20} {'Expected TP Exits':>22} {'Expected RRR Ratio':>22}")
    print("-" * 200)
    
    for market in ['US', 'CHINA', 'TAIWAN', 'THAI']:
        before = before_data[market]
        after = after_data[market]
        
        tp_change = f"{before['tp']:.1f}x → {after['tp']:.1f}x"
        trail_change = f"{before['trail_act']:.1f}% → {after['trail_act']:.1f}%"
        hold_change = f"{before['max_hold']:.0f} → {after['max_hold']:.0f} days"
        
        # Expected improvements
        if market == 'THAI':
            expected_tp = "0.5% (no change)"
            expected_rrr = "45.4% (no change)"
        else:
            expected_tp = "5-15% (from 0.0-0.1%)"
            expected_rrr = "50-70% (from 16-31%)"
        
        print(f"{market:<12} {tp_change:>14} {trail_change:>19} {hold_change:>19} {expected_tp:>21} {expected_rrr:>21}")
    
    print("\n" + "=" * 200)
    print("สรุป:")
    print("=" * 200)
    print("""
📊 การปรับปรุงที่ทำ:

1. ลด TP:
   - US: 5.0x → 3.5x ATR
   - CHINA: 5.0x → 3.5x ATR
   - TAIWAN: 6.5x → 3.5x ATR
   - THAI: 3.5x (ไม่เปลี่ยน)

2. ปรับ Trailing Stop:
   - US: 1.5% → 2.0% (activate ช้าลง)
   - CHINA: 1.0% → 2.0% (activate ช้าลง)
   - TAIWAN: 1.0% → 2.0% (activate ช้าลง)
   - THAI: 1.5% (ไม่เปลี่ยน)

3. เพิ่ม Max Hold:
   - US: 5 → 7 days
   - CHINA: 3 → 8 days
   - TAIWAN: 10 days (ไม่เปลี่ยน)

🎯 ผลลัพธ์ที่คาดหวัง:

1. TP Exits เพิ่มขึ้น:
   - จาก 0.0-0.5% → 5-15%
   - เพราะ TP ต่ำลง (3.5x แทน 5.0-6.5x)

2. RRR Actual เพิ่มขึ้น:
   - จาก 16-31% ของ Theoretical → 50-70%
   - เพราะ TP ต่ำลง + Trailing activate ช้าลง

3. Trailing Stop ยังเป็นหลัก:
   - 50-60% (ลดลงเล็กน้อยจาก 57-72%)
   - แต่ lock กำไรดีขึ้น (Distance 40% แทน 50%)

⚠️  หมายเหตุ:
   - ข้อมูล "After" ยังเป็น "TBD" (To Be Determined)
   - ต้อง backtest ใหม่ด้วยค่าใหม่เพื่อดูผลลัพธ์จริง
   - หลัง backtest เสร็จ ให้รัน: python scripts/compare_before_after_tp_adjustment.py
    """)
    print("=" * 200)

if __name__ == "__main__":
    create_comparison_table()

