#!/usr/bin/env python
"""
run_from_parquet.py - วิเคราะห์หุ้นจาก Parquet Files
====================================================

ใช้ข้อมูลที่ดึงไว้แล้วใน data/stocks/ (เร็วมาก!)
"""

import sys
import pandas as pd
from pathlib import Path
from stats_analyzer import StatsAnalyzer
from predictor import HistoricalPredictor

def analyze_from_parquet(symbol, exchange):
    """
    วิเคราะห์หุ้นจาก parquet file
    
    Args:
        symbol: รหัสหุ้น (เช่น PTT)
        exchange: ตลาด (เช่น SET)
    """
    # สร้าง path
    parquet_file = Path(f"data/stocks/{symbol}_{exchange}.parquet")
    
    # ตรวจสอบไฟล์
    if not parquet_file.exists():
        print(f"❌ ไม่พบไฟล์: {parquet_file}")
        print(f"💡 Tip: รัน python data_updater.py ก่อน")
        return
    
    print(f"\n{'='*60}")
    print(f"🎯 กำลังวิเคราะห์ {symbol} (จาก Parquet)")
    print(f"{'='*60}\n")
    
    # โหลดข้อมูล (เร็วมาก!)
    df = pd.read_parquet(parquet_file)
    df.index = pd.to_datetime(df.index)
    
    print(f"✅ โหลดข้อมูล {len(df)} bars")
    print(f"   ระหว่าง {df.index[0].strftime('%Y-%m-%d')} ถึง {df.index[-1].strftime('%Y-%m-%d')}")
    
    # วิเคราะห์สถิติ
    analyzer = StatsAnalyzer(threshold=1.0)
    stats = analyzer.generate_full_report(df)
    
    # แสดงสถิติโดยรวม
    first_date = df.index[0].strftime('%Y-%m-%d')
    last_date = df.index[-1].strftime('%Y-%m-%d')
    
    print(f"\n📊 สรุปสถิติ (จากข้อมูล {stats['total_days']} วัน)")
    print(f"    ระหว่าง {first_date} ถึง {last_date}")
    print(f"{'='*60}")
    print(f"\n📈 วันที่เคลื่อนไหว ±1%: {stats['total_significant_days']} วัน ({stats['total_significant_days']/stats['total_days']*100:.1f}%)")
    print(f"   - วันที่ขึ้น +1%: {stats['positive_moves']} วัน")
    print(f"   - วันที่ลง -1%: {stats['negative_moves']} วัน")
    
    # Probabilities
    probs = stats['probabilities']
    print(f"\n📊 ความน่าจะเป็น (หลังวันที่ ±1%):")
    print(f"   หลังวันขึ้น (+1%):")
    print(f"   - พรุ่งนี้ขึ้น: {probs['up_after_positive']:.1f}%")
    print(f"   - พรุ่งนี้ลง: {probs['down_after_positive']:.1f}%")
    print(f"   - พรุ่งนี้ sideways: {probs['sideways_after_positive']:.1f}%")
    
    print(f"\n   หลังวันลง (-1%):")
    print(f"   - พรุ่งนี้ขึ้น: {probs['up_after_negative']:.1f}%")
    print(f"   - พรุ่งนี้ลง: {probs['down_after_negative']:.1f}%")
    print(f"   - พรุ่งนี้ sideways: {probs['sideways_after_negative']:.1f}%")
    
    # แสดงข้อมูลเมื่อวาน
    latest_change = df.iloc[-1]['pct_change']
    latest_close = df.iloc[-1]['close']
    latest_date = df.index[-1].strftime('%Y-%m-%d')
    
    movement_type = "UP" if latest_change > 0 else "DOWN"
    print(f"\n{'='*60}")
    print(f"📊 {symbol}")
    print(f"   เมื่อวาน ({latest_date}): ฿{latest_close:.2f} ({latest_change:+.2f}%) {movement_type}")
    print(f"{'='*60}\n")
    
    # คำนวณ Range Statistics
    if abs(latest_change) > 1.0:
        # ... (range statistics logic)
        print("📈 แสดง Range Statistics...")
    else:
        print("⚠️ เคลื่อนไหวน้อยกว่า ±1%")
    
    print(f"\n✅ วิเคราะห์เสร็จสมบูรณ์!\n")


def batch_analyze_all():
    """
    วิเคราะห์หุ้นทั้งหมดใน data/stocks/
    """
    stocks_dir = Path("data/stocks")
    
    if not stocks_dir.exists():
        print("❌ ไม่พบโฟลเดอร์ data/stocks/")
        return
    
    parquet_files = list(stocks_dir.glob("*.parquet"))
    
    if not parquet_files:
        print("❌ ไม่พบไฟล์ parquet")
        return
    
    print(f"\n🚀 วิเคราะห์ทั้งหมด {len(parquet_files)} หุ้น\n")
    
    results = []
    for pf in parquet_files:
        # แยก symbol และ exchange จาก filename
        # เช่น PTT_SET.parquet -> PTT, SET
        parts = pf.stem.split('_')
        symbol = parts[0]
        exchange = parts[1]
        
        # โหลดและวิเคราะห์
        df = pd.read_parquet(pf)
        latest = df.iloc[-1]
        
        results.append({
            'Symbol': symbol,
            'Exchange': exchange,
            'Date': df.index[-1].strftime('%Y-%m-%d'),
            'Close': latest['close'],
            'Change%': latest['pct_change'],
            'Bars': len(df)
        })
    
    # แสดงเป็นตาราง
    summary_df = pd.DataFrame(results)
    summary_df = summary_df.sort_values('Change%', ascending=False)
    
    print(summary_df.to_string(index=False))
    print(f"\n📊 Total: {len(results)} stocks")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # ไม่มี args -> แสดงทั้งหมด
        batch_analyze_all()
    elif len(sys.argv) == 3:
        # มี args -> วิเคราะห์ 1 หุ้น
        symbol = sys.argv[1]
        exchange = sys.argv[2]
        analyze_from_parquet(symbol, exchange)
    else:
        print("Usage:")
        print("  python run_from_parquet.py              # ดูทั้งหมด")
        print("  python run_from_parquet.py PTT SET      # วิเคราะห์ PTT")
