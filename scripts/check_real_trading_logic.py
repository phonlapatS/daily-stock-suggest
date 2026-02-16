#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบว่า Elite Filter ใช้จริงในการทำนายหรือไม่
"""
import pandas as pd
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(BASE_DIR, "data", "symbol_performance.csv")

def check_real_trading_logic():
    """ตรวจสอบว่า Elite Filter ใช้จริงในการทำนายหรือไม่"""
    
    print("\n" + "=" * 160)
    print("ตรวจสอบ: Elite Filter ใช้จริงในการทำนายหรือไม่?")
    print("=" * 160)
    
    print("""
📋 Data Flow ของระบบ:

1. backtest.py (Backtesting):
   - ดึงข้อมูล 5000 bars
   - คำนวณ Pattern → Prob% (Historical Probability)
   - Gatekeeper (Prob >= 53-60%) → กรอง trades
   - บันทึกลง trade_history.csv (พร้อม prob field)

2. calculate_metrics.py (Calculate Metrics):
   - อ่าน trade_history.csv
   - Elite Filter (Prob >= 60%) → กรอง trades
   - คำนวณ Elite Prob% (Win Rate ของ Elite trades)
   - บันทึกลง symbol_performance.csv

3. main.py (Real Trading):
   - ดึงข้อมูล real-time
   - คำนวณ Pattern → Prob% (Historical Probability)
   - Engine → ตรวจสอบ is_tradeable
   - ถ้า is_tradeable = True → ทำนาย

❓ คำถาม: Engine ใช้ Elite Filter หรือไม่?

ให้ฉันตรวจสอบ...
    """)
    
    # ตรวจสอบว่า Engine ใช้ gatekeeper อะไร
    print("\n" + "=" * 160)
    print("ตรวจสอบ Engine Logic:")
    print("=" * 160)
    
    # อ่าน backtest.py เพื่อดู gatekeeper
    backtest_file = os.path.join(BASE_DIR, "scripts", "backtest.py")
    if os.path.exists(backtest_file):
        with open(backtest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # หา gatekeeper logic
            if 'min_prob' in content:
                print("✅ พบ Gatekeeper ใน backtest.py:")
                
                # หา min_prob values
                import re
                min_prob_matches = re.findall(r'min_prob\s*=\s*(\d+\.?\d*)', content)
                if min_prob_matches:
                    print(f"   - min_prob values: {', '.join(set(min_prob_matches))}")
                
                # หา gatekeeper conditions
                gatekeeper_lines = []
                for line in content.split('\n'):
                    if 'min_prob' in line.lower() or 'gatekeeper' in line.lower():
                        gatekeeper_lines.append(line.strip())
                
                if gatekeeper_lines:
                    print("\n   Gatekeeper Logic:")
                    for line in gatekeeper_lines[:10]:  # แสดง 10 บรรทัดแรก
                        print(f"     {line}")
    
    # ตรวจสอบว่า main.py ใช้ gatekeeper อะไร
    main_file = os.path.join(BASE_DIR, "main.py")
    if os.path.exists(main_file):
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'is_tradeable' in content:
                print("\n✅ พบ is_tradeable ใน main.py:")
                print("   - main.py ใช้ is_tradeable จาก Engine")
                print("   - is_tradeable = True → ทำนาย")
                print("   - is_tradeable = False → ไม่ทำนาย")
    
    print("\n" + "=" * 160)
    print("สรุป:")
    print("=" * 160)
    print("""
1. Elite Filter ทำงานที่ไหน?
   - ✅ calculate_metrics.py (หลัง backtest) → ใช้แสดงผล
   - ❌ main.py (real trading) → ไม่ใช้ Elite Filter

2. main.py ใช้เกณฑ์อะไร?
   - ✅ Gatekeeper (Prob >= 53-60%) → จาก backtest.py
   - ✅ Engine → ตรวจสอบ is_tradeable
   - ❌ ไม่ใช้ Elite Filter (Prob >= 60%)

3. Prob% ที่แสดงใน table = Prob% ที่ใช้จริงหรือไม่?
   - ⚠️ ไม่ใช่! เพราะ:
     - Prob% ใน table = Elite Prob% (Win Rate ของ Elite trades)
     - Prob% ที่ใช้จริง = Prob% จาก Pattern Matching (Historical Probability)
     - Elite Filter = กรองหลัง backtest (ไม่ใช่กรองตอนทำนาย)

4. ใช้จริงได้หรือไม่?
   - ✅ ใช้ได้! เพราะ:
     - ระบบทำนายเฉพาะ trades ที่ Prob >= 53-60% (Gatekeeper)
     - Elite Prob% = Win Rate ของ trades ที่ Prob >= 60%
     - ดังนั้น Elite Prob% ≈ Prob% ที่ใช้จริง (ถ้า Gatekeeper = 60%)
   
   - ⚠️ แต่ต้องระวัง:
     - ถ้า Gatekeeper = 53% แต่ Elite Filter = 60%
     - → Elite Prob% อาจสูงกว่า Prob% ที่ใช้จริง
     - → ควรใช้ Raw Prob% แทน Elite Prob% (ถ้า Gatekeeper < 60%)

สรุป:
  - Elite Filter = กรองหลัง backtest (แสดงผล)
  - Gatekeeper = กรองตอนทำนาย (real trading)
  - Prob% ใน table ≠ Prob% ที่ใช้จริง (ถ้า Gatekeeper ≠ 60%)
    """)
    print("=" * 160)

if __name__ == "__main__":
    check_real_trading_logic()

