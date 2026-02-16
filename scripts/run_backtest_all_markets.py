#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
รัน Backtest สำหรับทุกประเทศด้วย Settings Default (ค่าเดิม)
"""

import subprocess
import sys
import os
import glob
from datetime import datetime

def clear_cache():
    """ลบ cache และ trade_history เก่า"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, "data", "cache")
    logs_dir = os.path.join(base_dir, "logs")
    
    deleted_count = 0
    
    # ลบ cache files
    if os.path.exists(cache_dir):
        cache_files = glob.glob(os.path.join(cache_dir, "*.csv")) + glob.glob(os.path.join(cache_dir, "*.pkl"))
        for file_path in cache_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  ไม่สามารถลบ {os.path.basename(file_path)}: {e}")
    
    # ลบ trade_history เก่า (แต่เก็บ trade_history.csv ไว้เป็น backup)
    if os.path.exists(logs_dir):
        trade_history_files = glob.glob(os.path.join(logs_dir, "trade_history_*.csv"))
        for file_path in trade_history_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  ไม่สามารถลบ {os.path.basename(file_path)}: {e}")
    
    if deleted_count > 0:
        print(f"🗑️  ลบ cache และ trade_history เก่าแล้ว ({deleted_count} ไฟล์)")
        print("   Backtest จะดึงข้อมูลใหม่ทั้งหมด\n")
    else:
        print("ℹ️  ไม่พบไฟล์ cache หรือ trade_history ที่ต้องลบ\n")

def run_command(cmd, description):
    """รันคำสั่งและแสดงผลลัพธ์"""
    print("\n" + "=" * 80)
    print(f"🚀 {description}")
    print("=" * 80)
    print(f"คำสั่ง: {cmd}")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} - เสร็จสิ้น")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - เกิดข้อผิดพลาด: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  {description} - ถูกยกเลิกโดยผู้ใช้")
        return False

def main():
    """รัน backtest สำหรับทุกประเทศ"""
    
    print("\n" + "=" * 80)
    print("📊 BACKTEST ALL MARKETS - Settings Default")
    print("=" * 80)
    print(f"เวลาเริ่มต้น: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nการตั้งค่า: ใช้ค่า Default จากโค้ด")
    print("=" * 80)
    
    # เปลี่ยนไปที่ directory หลัก
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # ลบ cache และ trade_history เก่าก่อนรัน backtest
    print("\n" + "=" * 80)
    print("🧹 ลบ Cache และ Trade History เก่า")
    print("=" * 80)
    clear_cache()
    
    results = []
    
    # 1. THAI STOCK
    cmd_thai = "python scripts/backtest.py --full --bars 2500 --group THAI"
    results.append(("THAI STOCK", run_command(cmd_thai, "🇹🇭 THAI STOCK")))
    
    # 2. US STOCK
    cmd_us = "python scripts/backtest.py --full --bars 2500 --group US"
    results.append(("US STOCK", run_command(cmd_us, "🇺🇸 US STOCK")))
    
    # 3. CHINA/HK STOCK
    cmd_china = "python scripts/backtest.py --full --bars 2500 --group CHINA"
    results.append(("CHINA/HK STOCK", run_command(cmd_china, "🇨🇳 CHINA/HK STOCK")))
    
    # 4. TAIWAN STOCK
    cmd_taiwan = "python scripts/backtest.py --full --bars 2500 --group TAIWAN"
    results.append(("TAIWAN STOCK", run_command(cmd_taiwan, "🇹🇼 TAIWAN STOCK")))
    
    # สรุปผลลัพธ์
    print("\n" + "=" * 80)
    print("📊 สรุปผลลัพธ์")
    print("=" * 80)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for market, success in results:
        status = "✅ สำเร็จ" if success else "❌ ล้มเหลว"
        print(f"  {market:<20} {status}")
    
    print("-" * 80)
    print(f"รวม: {success_count}/{total_count} สำเร็จ")
    print(f"เวลาเสร็จสิ้น: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if success_count == total_count:
        print("\n✅ Backtest ทั้งหมดเสร็จสิ้นแล้ว!")
        print("\n📈 ขั้นตอนต่อไป:")
        print("  1. รันคำสั่ง: python scripts/calculate_metrics.py")
        print("  2. ตรวจสอบผลลัพธ์ใน logs/trade_history_*.csv")
        return 0
    else:
        print("\n⚠️  มีบาง backtest ที่ล้มเหลว กรุณาตรวจสอบข้อผิดพลาด")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  ถูกยกเลิกโดยผู้ใช้")
        sys.exit(1)
