#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
อธิบาย Elite Filter vs Real Trading
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

def explain_elite_vs_real():
    """อธิบาย Elite Filter vs Real Trading"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("อธิบาย Elite Filter vs Real Trading")
    print("=" * 160)
    
    # หาหุ้นที่ Prob% สูงแต่ Count น้อย
    high_prob_low_count = df[
        (df['Prob%'] >= 70.0) &
        (df['Count'] < 100)
    ].sort_values('Prob%', ascending=False)
    
    if not high_prob_low_count.empty:
        print(f"\nหุ้นที่ Prob% >= 70% แต่ Count < 100 ({len(high_prob_low_count)} หุ้น):")
        print(f"{'Symbol':<12} {'Country':<8} {'Prob%':>8} {'Count':>8} {'Raw_Prob%':>12} {'Elite_Prob%':>14} {'Raw_Count':>12} {'Elite_Count':>14} {'อธิบาย':<50}")
        print("-" * 160)
        
        for _, row in high_prob_low_count.head(10).iterrows():
            symbol = str(row['symbol'])
            country = str(row.get('Country', 'N/A'))
            prob = row.get('Prob%', 0.0)
            count = int(row.get('Count', 0))
            raw_prob = row.get('Raw_Prob%', 0.0)
            elite_prob = row.get('Elite_Prob%', 0.0)
            raw_count = int(row.get('Raw_Count', 0))
            elite_count = int(row.get('Elite_Count', 0))
            
            # อธิบาย
            if prob == elite_prob and count == elite_count:
                explanation = f"Prob {prob:.1f}% มาจาก Elite ({elite_count} trades) - ใช้ได้จริง"
            elif prob == elite_prob and count == raw_count:
                explanation = f"Prob {prob:.1f}% มาจาก Elite แต่ Count มาจาก Raw - ไม่สอดคล้อง"
            elif prob == raw_prob:
                explanation = f"Prob {prob:.1f}% มาจาก Raw ({raw_count} trades) - ใช้ได้จริง"
            else:
                explanation = f"Prob {prob:.1f}% ไม่ชัดเจน"
            
            print(f"{symbol:<12} {country:<8} {prob:>7.1f}% {count:>8} {raw_prob:>11.1f}% {elite_prob:>13.1f}% {raw_count:>12} {elite_count:>14} {explanation}")
    
    print("\n" + "=" * 160)
    print("คำอธิบาย:")
    print("=" * 160)
    print("""
1. Elite Filter คืออะไร?
   - Elite Filter = กรอง trades ที่มี Prob% (Historical Probability) >= 60%
   - Prob% = ความน่าจะเป็นที่ pattern นี้จะชนะ (จาก historical data)
   - ไม่ใช่: เอา trade ที่ชนะมาแสดง
   - คือ: เอา trade ที่ทำนายว่าจะชนะสูง (Prob >= 60%) มาแสดง

2. ตัวอย่าง ENPH (Prob 80%, Count 30):
   - Raw Count: 1,116 trades (ทั้งหมด)
   - Elite Count: 30 trades (trades ที่ Prob >= 60%)
   - Elite Prob%: 80% (Win Rate ของ Elite trades 30 ตัว)
   - Raw Prob%: 69.8% (Win Rate ของ Raw trades 1,116 ตัว)
   
   → Prob 80% มาจาก Elite trades 30 ตัว (ชนะ 24 ตัว)
   → แต่จริงๆ มี trades ทั้งหมด 1,116 ตัว (ชนะ 779 ตัว = 69.8%)

3. ใช้จริงได้หรือเปล่า?
   - ✅ ใช้ได้! เพราะ:
     - ระบบจะทำนายเฉพาะ pattern ที่ Prob >= 60% (Elite Filter)
     - Gatekeeper ใน main.py จะกรอง trades ที่ Prob >= 53-60% (ขึ้นอยู่กับประเทศ)
     - ดังนั้น Prob 80% มาจาก trades ที่ Prob >= 60% ซึ่งระบบจะทำนายจริงๆ
   
   - ⚠️ แต่ต้องระวัง:
     - Elite Count 30 อาจจะน้อยเกินไป (ไม่น่าเชื่อถือทางสถิติ)
     - ควรใช้ Elite Count >= 30 เพื่อความน่าเชื่อถือ

4. ระบบทำนายอย่างไร?
   - main.py → Gatekeeper (Prob >= 53-60%) → ทำนายเฉพาะ trades ที่ผ่าน
   - Elite Filter → กรอง trades ที่ Prob >= 60% → ใช้แสดงผล
   - ดังนั้น Prob% ที่แสดง = Prob% ของ trades ที่ระบบจะทำนายจริงๆ

5. ทำไม Count 30 แต่ Prob 80%?
   - เพราะ Elite Filter กรองเฉพาะ trades ที่ Prob >= 60%
   - จาก 1,116 trades → เหลือ 30 trades ที่ Prob >= 60%
   - จาก 30 trades → ชนะ 24 trades (80%)
   - → Prob 80% มาจาก Elite trades 30 ตัว

สรุป:
  - Elite Filter = กรอง trades ที่ Prob >= 60% (ไม่ใช่กรอง trades ที่ชนะ)
  - Prob 80% = Win Rate ของ Elite trades (trades ที่ Prob >= 60%)
  - ระบบจะทำนายเฉพาะ trades ที่ Prob >= 60% (ผ่าน Gatekeeper)
  - ดังนั้น Prob 80% = Prob% ที่ใช้จริงในการทำนาย
    """)
    print("=" * 160)

if __name__ == "__main__":
    explain_elite_vs_real()

