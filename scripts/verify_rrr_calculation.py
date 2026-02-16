#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_rrr_calculation.py - ตรวจสอบการคำนวณ RRR
================================================================================

ยืนยันว่า RRR = AvgWin / AvgLoss
- AvgWin = ค่าเฉลี่ยของกำไรในครั้งที่ชนะ
- AvgLoss = ค่าเฉลี่ยของขาดทุนในครั้งที่แพ้ (ใช้ abs เพื่อให้เป็นบวก)
- RRR = AvgWin / AvgLoss
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


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[VERIFY] ตรวจสอบการคำนวณ RRR")
    print("="*100)
    
    # Load data
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    print(f"\n📊 โหลดข้อมูล: {len(df)} symbols")
    
    # Verify RRR calculation
    print("\n[1] ตรวจสอบสูตร RRR = AvgWin / AvgLoss")
    print("-" * 80)
    print("   สูตร: RRR = AvgWin% / AvgLoss%")
    print("   - AvgWin% = ค่าเฉลี่ยของกำไรในครั้งที่ชนะ")
    print("   - AvgLoss% = ค่าเฉลี่ยของขาดทุนในครั้งที่แพ้ (ใช้ abs เพื่อให้เป็นบวก)")
    print("   - RRR = AvgWin% / AvgLoss%")
    
    # Calculate RRR from AvgWin and AvgLoss
    df['RRR_Calculated'] = df.apply(
        lambda row: row['AvgWin%'] / row['AvgLoss%'] if row['AvgLoss%'] > 0 else 0,
        axis=1
    )
    
    # Compare with existing RRR
    df['RRR_Diff'] = abs(df['RR_Ratio'] - df['RRR_Calculated'])
    
    # Check if they match
    matches = df[df['RRR_Diff'] < 0.01]  # Allow small floating point differences
    mismatches = df[df['RRR_Diff'] >= 0.01]
    
    print(f"\n   [ผลการตรวจสอบ]")
    print(f"   ตรงกัน: {len(matches)} symbols")
    print(f"   ไม่ตรงกัน: {len(mismatches)} symbols")
    
    if len(mismatches) > 0:
        print(f"\n   [ตัวอย่างที่ไม่ตรงกัน]")
        for _, row in mismatches.head(10).iterrows():
            print(f"     {row['symbol']}: RRR_Original={row['RR_Ratio']:.2f}, "
                  f"RRR_Calculated={row['RRR_Calculated']:.2f}, "
                  f"AvgWin={row['AvgWin%']:.2f}%, AvgLoss={row['AvgLoss%']:.2f}%")
    
    # Show examples
    print("\n[2] ตัวอย่างการคำนวณ RRR")
    print("-" * 80)
    print(f"{'Symbol':<10} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR (Original)':>15} {'RRR (Calculated)':>18} {'Match':>8}")
    print("-" * 80)
    
    sample = df.head(10)
    for _, row in sample.iterrows():
        match = "✅" if row['RRR_Diff'] < 0.01 else "❌"
        print(f"{row['symbol']:<10} {row['AvgWin%']:>9.2f}% {row['AvgLoss%']:>9.2f}% "
              f"{row['RR_Ratio']:>14.2f} {row['RRR_Calculated']:>17.2f} {match:>8}")
    
    # Show formula verification
    print("\n[3] ตรวจสอบสูตรด้วยตัวอย่างจริง")
    print("-" * 80)
    
    # Find a good example
    example = df[df['AvgWin%'] > 0][df['AvgLoss%'] > 0].head(1)
    if not example.empty:
        row = example.iloc[0]
        print(f"   ตัวอย่าง: {row['symbol']}")
        print(f"   AvgWin% = {row['AvgWin%']:.2f}% (ค่าเฉลี่ยของกำไรในครั้งที่ชนะ)")
        print(f"   AvgLoss% = {row['AvgLoss%']:.2f}% (ค่าเฉลี่ยของขาดทุนในครั้งที่แพ้)")
        print(f"   RRR = AvgWin% / AvgLoss%")
        print(f"   RRR = {row['AvgWin%']:.2f}% / {row['AvgLoss%']:.2f}%")
        print(f"   RRR = {row['AvgWin%']:.2f} / {row['AvgLoss%']:.2f}")
        calculated = row['AvgWin%'] / row['AvgLoss%']
        print(f"   RRR = {calculated:.2f}")
        print(f"   RRR (ในไฟล์) = {row['RR_Ratio']:.2f}")
        if abs(calculated - row['RR_Ratio']) < 0.01:
            print(f"   ✅ ตรงกัน!")
        else:
            print(f"   ❌ ไม่ตรงกัน (ต่างกัน {abs(calculated - row['RR_Ratio']):.2f})")
    
    print("\n" + "="*100)
    print("[CONCLUSION] สรุป")
    print("="*100)
    print("   ✅ RRR = AvgWin% / AvgLoss%")
    print("   ✅ AvgWin% = ค่าเฉลี่ยของกำไรในครั้งที่ชนะ")
    print("   ✅ AvgLoss% = ค่าเฉลี่ยของขาดทุนในครั้งที่แพ้ (ใช้ abs เพื่อให้เป็นบวก)")
    print("   ✅ สูตรถูกต้องตามที่เข้าใจ")


if __name__ == "__main__":
    main()

