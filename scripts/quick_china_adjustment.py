#!/usr/bin/env python
"""
Quick China Market Adjustment - ปรับให้ตรงกับความเป็นจริง

แนะนำค่าที่เหมาะสมสำหรับหุ้นรายวัน:
- TP: 4.0-4.5% (ลดจาก 5.5%)
- Max Hold: 10 days (เพิ่มจาก 8)
- SL: 1.2% (คงที่)
"""

import sys
import os
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    """Show recommendations"""
    print("="*100)
    print("China Market - Quick Adjustment Recommendations")
    print("="*100)
    
    print(f"\n📊 Current Settings (V13.2):")
    print(f"  TP: 5.5%")
    print(f"  SL: 1.2%")
    print(f"  Max Hold: 8 days")
    print(f"  RRR: 1.14 (ต่ำ)")
    
    print(f"\n❌ ปัญหา:")
    print(f"  1. TP 5.5% อาจสูงเกินไปสำหรับหุ้นรายวัน")
    print(f"  2. Max Hold 8 วันอาจสั้นเกินไป")
    print(f"  3. RRR ต่ำ (1.14) อาจเป็นเพราะไม่ค่อยถึง TP")
    
    print(f"\n💡 Recommended Adjustments:")
    print(f"\n  Option A: Conservative (แนะนำ)")
    print(f"    TP: 4.0%")
    print(f"    Max Hold: 10 days")
    print(f"    SL: 1.2%")
    print(f"    Expected: TP Hit Rate 25-30%, RRR 1.3-1.4")
    
    print(f"\n  Option B: Balanced (Best)")
    print(f"    TP: 4.5%")
    print(f"    Max Hold: 10 days")
    print(f"    SL: 1.2%")
    print(f"    Expected: TP Hit Rate 20-25%, RRR 1.4-1.5")
    
    print(f"\n  Option C: Aggressive")
    print(f"    TP: 5.0%")
    print(f"    Max Hold: 12 days")
    print(f"    SL: 1.2%")
    print(f"    Expected: TP Hit Rate 15-20%, RRR 1.5-1.6")
    
    print(f"\n🧪 Testing:")
    print(f"  Run: python scripts/test_china_realistic_tp.py")
    print(f"  This will test all combinations and find the best one")
    
    print(f"\n📋 Action Plan:")
    print(f"  1. รันทดสอบ: python scripts/test_china_realistic_tp.py")
    print(f"  2. วิเคราะห์ผลลัพธ์")
    print(f"  3. เลือกค่าที่ดีที่สุด")
    print(f"  4. ปรับ backtest.py")
    print(f"  5. ทดสอบอีกครั้งเพื่อยืนยัน")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    main()

