#!/usr/bin/env python
"""
run.py - Simple wrapper สำหรับใช้งานระบบ
รันแค่: python run.py
"""

import sys
from data_cache import OptimizedDataFetcher
from stats_analyzer import StatsAnalyzer
from predictor import HistoricalPredictor
from visualizer import StatsVisualizer
from utils import save_to_json, format_stats_report, ensure_directories
from config import RESULTS_DIR
import os


def analyze_stock(symbol, exchange='SET', show_plots=False):
    """
    วิเคราะห์หุ้นแบบง่าย
    """
    print(f"\n{'='*60}")
    print(f"🎯 กำลังวิเคราะห์ {symbol} ({exchange})")
    print(f"{'='*60}\n")
    
    # 1. ดึงข้อมูล (ใช้ cache อัตโนมัติ)
    fetcher = OptimizedDataFetcher(use_cache=True)
    df = fetcher.fetch_daily_data(symbol, exchange, n_bars=1250)
    
    if df is None:
        print(f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้")
        return
    
    # 2. วิเคราะห์สถิติ
    analyzer = StatsAnalyzer(threshold=1.0)
    stats = analyzer.generate_full_report(df)
    
    # แสดงสถิติที่สำคัญ
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
    
    # Risk metrics
    risk = stats.get('risk_metrics', {})
    if risk:
        print(f"\n⚠️ ความเสี่ยง:")
        print(f"   หลังวันขึ้น: เฉลี่ย {stats['next_day_stats']['after_positive']['avg_change']:+.2f}%, worst case {risk.get('max_loss_after_positive', 0):+.2f}%")
        print(f"   หลังวันลง: เฉลี่ย {stats['next_day_stats']['after_negative']['avg_change']:+.2f}%, worst case {risk.get('max_gain_after_negative', 0):+.2f}%")
    
    
    # Streaks
    streak_stats = stats.get('streak_stats', {})
    total_streaks = streak_stats.get('total_streaks', 0) if streak_stats else 0
    print(f"\n🔥 Streaks: พบ {total_streaks} ครั้ง (4+ วันติดต่อกัน)")

    
    # 3. แสดงสถิติแบบ Range
    latest_change = df.iloc[-1]['pct_change']
    latest_close = df.iloc[-1]['close']
    latest_date = df.index[-1].strftime('%Y-%m-%d')
    
    # แสดงข้อมูลเมื่อวาน
    movement_type = "UP" if latest_change > 0 else "DOWN"
    print(f"\n{'='*60}")
    print(f"📊 {symbol}")
    print(f"   เมื่อวาน ({latest_date}): ฿{latest_close:.2f} ({latest_change:+.2f}%) {movement_type}")
    print(f"{'='*60}\n")
    
    # คำนวณ Range Statistics - แสดงทั้ง 2 ฝั่ง
    if abs(latest_change) > 1.0:  # เกิน 1% (ไม่รวมพอดี 1%)
        # หาวันที่เกิน 1% ทั้งหมด
        significant_indices = df[abs(df['pct_change']) > 1.0].index
        
        # แยกเป็น 2 ฝั่ง
        positive_days = []
        negative_days = []
        
        for idx in significant_indices:
            current_change = df.loc[idx, 'pct_change']
            
            # หาวันถัดไป
            idx_pos = df.index.get_loc(idx)
            if idx_pos < len(df) - 1:
                next_idx = df.index[idx_pos + 1]
                next_change = df.loc[next_idx, 'pct_change']
                
                if current_change > 1.0:
                    positive_days.append(next_change)
                elif current_change < -1.0:
                    negative_days.append(next_change)
        
        # แบ่ง range
        ranges = [
            (1.0, float('inf'), '+1.0% ขึ้นไป'),
            (0.5, 1.0, '+0.5% ถึง +1.0%'),
            (0.0, 0.5, '0% ถึง +0.5%'),
            (-0.5, 0.0, '0% ถึง -0.5%'),
            (-1.0, -0.5, '-0.5% ถึง -1.0%'),
            (float('-inf'), -1.0, '-1.0% ลงไป'),
        ]
        
        # แสดงฝั่ง +
        if positive_days:
            print(f"📈 สถิติหลังวันที่ +เกิน 1%:")
            print(f"   วันถัดไป:")
            total = len(positive_days)
            for min_val, max_val, label in ranges:
                if max_val == float('inf'):
                    count = sum(1 for x in positive_days if x >= min_val)
                elif min_val == float('-inf'):
                    count = sum(1 for x in positive_days if x < max_val)
                else:
                    count = sum(1 for x in positive_days if min_val <= x < max_val)
                
                if count > 0:
                    pct = count / total * 100
                    print(f"   • {label:20s}: {count:3d} ครั้ง ({pct:5.1f}%)")
            print(f"\n   รวม: {total} ครั้งในอดีต")
        
        print(f"\n{'='*60}\n")
        
        # แสดงฝั่ง -
        if negative_days:
            print(f"📉 สถิติหลังวันที่ -เกิน 1%:")
            print(f"   วันถัดไป:")
            total = len(negative_days)
            for min_val, max_val, label in ranges:
                if max_val == float('inf'):
                    count = sum(1 for x in negative_days if x >= min_val)
                elif min_val == float('-inf'):
                    count = sum(1 for x in negative_days if x < max_val)
                else:
                    count = sum(1 for x in negative_days if min_val <= x < max_val)
                
                if count > 0:
                    pct = count / total * 100
                    print(f"   • {label:20s}: {count:3d} ครั้ง ({pct:5.1f}%)")
            print(f"\n   รวม: {total} ครั้งในอดีต")


        
    else:
        print(f"⚠️ เคลื่อนไหวน้อยกว่า ±1%")



    
    print(f"\n{'='*60}")
    
    # แสดงสถิติโดยรวม
    print(f"\n💡 สถิติโดยรวม ({stats['total_days']} วัน):")
    print(f"{'='*60}")
    print(f"   ✓ วันที่เคลื่อนไหว ±1%: {stats['total_significant_days']} วัน ({stats['total_significant_days']/stats['total_days']*100:.1f}%)")
    print(f"   ✓ Streaks (4+ วัน): {total_streaks} ครั้ง")

    
    probs = stats['probabilities']
    print(f"\n   📊 หลังวันขึ้น +1%:")
    print(f"      พรุ่งนี้ขึ้น: {probs['up_after_positive']:.1f}% | ลง: {probs['down_after_positive']:.1f}% | sideways: {probs['sideways_after_positive']:.1f}%")
    
    print(f"\n   📊 หลังวันลง -1%:")
    print(f"      พรุ่งนี้ขึ้น: {probs['up_after_negative']:.1f}% | ลง: {probs['down_after_negative']:.1f}% | sideways: {probs['sideways_after_negative']:.1f}%")
    
    # 4. สร้างกราฟ (ถ้าต้องการ)
    if show_plots:
        visualizer = StatsVisualizer()
        visualizer.create_full_report_plots(df, stats, symbol)
    
    # 5. บันทึกผลลัพธ์
    filename = f"{symbol}_{exchange}_report.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    save_to_json(stats, filepath)
    
    print(f"\n{'='*60}")
    print(f"✅ เสร็จสิ้น! ผลลัพธ์บันทึกที่: {filepath}")
    print(f"{'='*60}\n")


def main():
    """
    Interactive mode
    """
    ensure_directories()
    
    print("\n" + "="*60)
    print("📊 ระบบทำนายหุ้น - Stock Prediction System")
    print("="*60)
    
    # ตัวอย่างหุ้นยอดนิยม
    popular = {
        '1': {'symbol': 'PTT', 'exchange': 'SET', 'name': 'PTT (ไทย)'},
        '2': {'symbol': 'CPALL', 'exchange': 'SET', 'name': 'CP ALL (ไทย)'},
        '3': {'symbol': 'AAPL', 'exchange': 'NASDAQ', 'name': 'Apple (สหรัฐ)'},
        '4': {'symbol': 'TSLA', 'exchange': 'NASDAQ', 'name': 'Tesla (สหรัฐ)'},
        '5': {'symbol': 'MSFT', 'exchange': 'NASDAQ', 'name': 'Microsoft (สหรัฐ)'},
    }
    
    print("\n📋 เลือกหุ้น:")
    print("1. PTT (ไทย)")
    print("2. CPALL (ไทย)")
    print("3. AAPL - Apple (สหรัฐ)")
    print("4. TSLA - Tesla (สหรัฐ)")
    print("5. MSFT - Microsoft (สหรัฐ)")
    print("6. กรอกเองเลือก")
    
    choice = input("\nเลือก (1-6): ").strip()
    
    if choice in popular:
        stock = popular[choice]
        analyze_stock(stock['symbol'], stock['exchange'])
    
    elif choice == '6':
        symbol = input("รหัสหุ้น (เช่น PTT, AAPL): ").strip().upper()
        exchange = input("Exchange (SET, NASDAQ, NYSE): ").strip().upper()
        analyze_stock(symbol, exchange)
    
    else:
        print("❌ ตัวเลือกไม่ถูกต้อง")


if __name__ == "__main__":
    # ถ้า run โดยไม่มี argument = interactive mode
    if len(sys.argv) == 1:
        main()
    
    # ถ้ามี argument = direct mode
    elif len(sys.argv) >= 3:
        symbol = sys.argv[1]
        exchange = sys.argv[2] if len(sys.argv) > 2 else 'SET'
        analyze_stock(symbol, exchange)
    
    else:
        print("Usage:")
        print("  python run.py                    # Interactive mode")
        print("  python run.py PTT SET            # Direct mode")
        print("  python run.py AAPL NASDAQ        # Direct mode")
