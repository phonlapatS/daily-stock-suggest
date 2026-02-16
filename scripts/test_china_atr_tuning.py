#!/usr/bin/env python
"""
Test China ATR TP/SL Tuning - ทดสอบการปรับ ATR TP/SL เพื่อเพิ่ม RRR
"""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_atr_tuning():
    """ทดสอบการปรับ ATR TP/SL"""
    
    print("="*100)
    print("Test China ATR TP/SL Tuning - หาค่า ATR TP/SL ที่เหมาะสม")
    print("="*100)
    print()
    
    print("📋 Current Settings (V13.5):")
    print("   ATR SL: 1.0x")
    print("   ATR TP: 4.0x")
    print("   Theoretical RRR: 4.0")
    print("   Actual RRR: 0.99-1.15 (ต่ำกว่าเป้าหมาย 1.40)")
    print()
    
    print("="*100)
    print("Options to Test:")
    print("="*100)
    print()
    
    print("Option 1: เพิ่ม ATR TP multiplier")
    print("   - จาก 4.0x → 4.5x หรือ 5.0x")
    print("   - จะเพิ่ม Take Profit ทำให้ RRR สูงขึ้น")
    print("   - ผลลัพธ์: RRR จะเพิ่มขึ้น แต่ Prob% อาจจะลดลง (เพราะ TP สูงขึ้น)")
    print()
    
    print("Option 2: ลด ATR SL multiplier")
    print("   - จาก 1.0x → 0.8x หรือ 0.9x")
    print("   - จะลด Stop Loss ทำให้ RRR สูงขึ้น")
    print("   - ผลลัพธ์: RRR จะเพิ่มขึ้น แต่ Prob% อาจจะลดลง (เพราะ SL แคบขึ้น)")
    print()
    
    print("Option 3: เพิ่ม min_prob ใน gatekeeper")
    print("   - จาก 51.0% → 54.0% หรือ 55.0%")
    print("   - จะกรอง trades ที่มี Historical Prob% ต่ำกว่า threshold ออกไป")
    print("   - ผลลัพธ์: RRR จะเพิ่มขึ้นเล็กน้อย (0.99 → 1.15)")
    print()
    
    print("Option 4: Combined (min_prob + ATR TP)")
    print("   - min_prob: 54.0%")
    print("   - ATR TP: 4.5x หรือ 5.0x")
    print("   - ผลลัพธ์: RRR อาจจะเพิ่มขึ้นมากกว่า Option 1 หรือ 3 เพียงอย่างเดียว")
    print()
    
    print("="*100)
    print("💡 Recommended Test Plan:")
    print("="*100)
    print()
    print("1. ทดสอบ Option 3 ก่อน (เพิ่ม min_prob เป็น 54.0%):")
    print("   python scripts/backtest.py --full --bars 2000 --group CHINA --min_prob 54.0")
    print("   python scripts/calculate_metrics.py")
    print()
    print("2. ทดสอบ Option 1 (เพิ่ม ATR TP เป็น 4.5x):")
    print("   python scripts/backtest.py --full --bars 2000 --group CHINA --atr_tp_mult 4.5")
    print("   python scripts/calculate_metrics.py")
    print()
    print("3. ทดสอบ Option 4 (Combined - min_prob 54.0% + ATR TP 4.5x):")
    print("   python scripts/backtest.py --full --bars 2000 --group CHINA --min_prob 54.0 --atr_tp_mult 4.5")
    print("   python scripts/calculate_metrics.py")
    print()
    print("4. เปรียบเทียบผลลัพธ์และเลือกค่าที่เหมาะสม")
    print()
    
    print("="*100)
    print("⚠️  ข้อควรระวัง:")
    print("="*100)
    print()
    print("- Prob% จะยังสูงอยู่ (70-77%) เพราะเป็น Raw Prob% ของหุ้นที่ผ่านเกณฑ์แล้ว")
    print("- การเพิ่ม ATR TP จะทำให้ Prob% ลดลง (เพราะ TP สูงขึ้น)")
    print("- การลด ATR SL จะทำให้ Prob% ลดลง (เพราะ SL แคบขึ้น)")
    print("- ต้องทดสอบและเปรียบเทียบผลลัพธ์ก่อนใช้จริง")
    print()
    
    print("="*100)
    print("🎯 Target:")
    print("="*100)
    print()
    print("- RRR >= 1.40 (ดีขึ้นจาก 0.99-1.15)")
    print("- Prob% >= 60% (ยังสูงอยู่ แต่ realistic)")
    print("- Count >= 20 (น่าเชื่อถือทางสถิติ)")
    print("- Stocks >= 4 (มีหุ้นที่เทรดได้เพียงพอ)")

if __name__ == "__main__":
    test_atr_tuning()

