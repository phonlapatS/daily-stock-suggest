#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
รัน backtest ทั้งหมดด้วยค่าใหม่ (TP 3.5x, Trailing 2.0%) และเปรียบเทียบผลลัพธ์
"""
import subprocess
import sys
import os
import time

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")

def clear_cache():
    """ลบ cache ทั้งหมดเพื่อให้ backtest ดึงข้อมูลใหม่"""
    if not os.path.exists(CACHE_DIR):
        print("ℹ️  ไม่พบ cache directory")
        return
    
    cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.csv') or f.endswith('.pkl')]
    
    if not cache_files:
        print("ℹ️  ไม่พบไฟล์ cache")
        return
    
    deleted_count = 0
    for filename in cache_files:
        file_path = os.path.join(CACHE_DIR, filename)
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            print(f"⚠️  ไม่สามารถลบ {filename}: {e}")
    
    if deleted_count > 0:
        print(f"🗑️  ลบ cache ไฟล์แล้ว ({deleted_count} ไฟล์)")
        print("   Backtest จะดึงข้อมูลใหม่ทั้งหมด\n")
    else:
        print("ℹ️  ไม่พบไฟล์ cache ที่ต้องลบ\n")

def clean_old_trade_history():
    """ลบไฟล์ trade_history และ backtest results เก่าก่อนรัน backtest ใหม่"""
    trade_history_files = [
        'trade_history_US.csv',
        'trade_history_CHINA.csv',
        'trade_history_TAIWAN.csv',
        'trade_history_THAI.csv',
        'trade_history_METALS.csv'
    ]
    
    # ไฟล์ backtest results ที่ทำให้ backtest skip symbols
    data_dir = os.path.join(BASE_DIR, "data")
    backtest_results_file = os.path.join(data_dir, "full_backtest_results.csv")
    
    deleted_count = 0
    
    # ลบ trade_history files
    for filename in trade_history_files:
        file_path = os.path.join(LOGS_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"🗑️  ลบไฟล์เก่า: {filename}")
            except Exception as e:
                print(f"⚠️  ไม่สามารถลบ {filename}: {e}")
    
    # ลบ backtest results file เพื่อให้ backtest รันใหม่ทั้งหมด
    if os.path.exists(backtest_results_file):
        try:
            os.remove(backtest_results_file)
            deleted_count += 1
            print(f"🗑️  ลบไฟล์เก่า: data/full_backtest_results.csv")
        except Exception as e:
            print(f"⚠️  ไม่สามารถลบ backtest results: {e}")
    
    if deleted_count > 0:
        print(f"\n✅ ลบไฟล์เก่าเสร็จสิ้น ({deleted_count} ไฟล์)")
        print("   ข้อมูลใหม่จะถูกบันทึกหลังจาก backtest เสร็จ\n")
    else:
        print("\nℹ️  ไม่พบไฟล์เก่า (พร้อมสำหรับ backtest ใหม่)\n")

def run_backtest(market_name, command):
    """รัน backtest สำหรับแต่ละ market"""
    print("\n" + "=" * 160)
    print(f"🚀 เริ่ม Backtest: {market_name}")
    print("=" * 160)
    print(f"คำสั่ง: {' '.join(command)}")
    print("=" * 160)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {market_name} Backtest เสร็จสิ้น (ใช้เวลา: {elapsed_time/60:.1f} นาที)")
            return True
        else:
            print(f"\n❌ {market_name} Backtest มีปัญหา (Exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {market_name} backtest: {e}")
        return False

def main():
    """รัน backtest ทั้งหมดและเปรียบเทียบผลลัพธ์"""
    
    print("\n" + "=" * 160)
    print("Backtest (RRR Ratio >= 60%, Count >= 30)")
    print("=" * 160)
    print("\n⚠️  หมายเหตุ:")
    print("   - ใช้ --full (Full Scan) → รันทุกหุ้นในกลุ่ม")
    print("   - การ backtest อาจใช้เวลานาน (30-120 นาทีต่อประเทศ)")
    print("   - รวมทั้งหมดประมาณ 2-8 ชั่วโมง")
    print("   - หลัง backtest เสร็จ จะรันการเปรียบเทียบผลลัพธ์อัตโนมัติ")
    print("\n" + "=" * 160)
    
    # ลบ cache ก่อน
    print("\n🧹 กำลังลบ cache...")
    clear_cache()
    
    # ลบไฟล์ trade_history เก่าก่อนรัน backtest ใหม่
    print("\n🧹 กำลังลบไฟล์ trade_history เก่า...")
    clean_old_trade_history()
    
    # คำสั่ง backtest สำหรับแต่ละประเทศ
    backtest_commands = [
        {
            'name': 'US STOCK',
            'command': [
                'python', 'scripts/backtest.py',
                '--full',  # รันทุกหุ้นในกลุ่ม (Full Scan)
                '--bars', '2500',  # ใช้ 2500 bars เพื่อข้อมูลมากขึ้น
                '--group', 'US',  # ใช้ "US" เพื่อ match GROUP_B_US
                '--atr_tp_mult', '5.0',  # ค่าเดิม
                '--trail_activate', '1.5',  # ค่าเดิม
                '--max_hold', '5',
                '--fast'
            ]
        },
        {
            'name': 'CHINA/HK STOCK',
            'command': [
                'python', 'scripts/backtest.py',
                '--full',  # รันทุกหุ้นในกลุ่ม (Full Scan)
                '--bars', '2500',  # ใช้ 2500 bars เพื่อข้อมูลมากขึ้น
                '--group', 'CHINA',  # ใช้ "CHINA" เพื่อ match GROUP_C_CHINA_HK
                '--atr_tp_mult', '5.0',  # ค่าเดิม
                '--trail_activate', '1.0',  # ค่าเดิม
                '--max_hold', '3',
                '--fast'
            ]
        },
        {
            'name': 'TAIWAN STOCK',
            'command': [
                'python', 'scripts/backtest.py',
                '--full',  # รันทุกหุ้นในกลุ่ม (Full Scan)
                '--bars', '2500',  # ใช้ 2500 bars เพื่อข้อมูลมากขึ้น
                '--group', 'TAIWAN',  # ใช้ "TAIWAN" เพื่อ match GROUP_D_TAIWAN
                '--atr_tp_mult', '6.5',  # ค่าเดิม
                '--trail_activate', '1.0',  # ค่าเดิม
                '--max_hold', '10',
                '--fast'
            ]
        },
        {
            'name': 'THAI STOCK',
            'command': [
                'python', 'scripts/backtest.py',
                '--full',  # รันทุกหุ้นในกลุ่ม (Full Scan)
                '--bars', '2500',  # ใช้ 2500 bars เพื่อข้อมูลมากขึ้น
                '--group', 'THAI',  # ใช้ "THAI" เพื่อ match GROUP_A_THAI
                '--take_profit', '3.5',  # ค่าเดิม
                '--trail_activate', '1.5',  # ค่าเดิม
                '--max_hold', '5',
                '--fast'
            ]
        }
    ]
    
    # รัน backtest ทั้งหมด
    results = {}
    total_start_time = time.time()
    
    for i, market in enumerate(backtest_commands, 1):
        print(f"\n📊 Progress: {i}/{len(backtest_commands)}")
        success = run_backtest(market['name'], market['command'])
        results[market['name']] = success
        
        if not success:
            print(f"\n⚠️  {market['name']} backtest มีปัญหา แต่จะดำเนินการต่อ...")
    
    total_elapsed_time = time.time() - total_start_time
    
    # สรุปผล
    print("\n" + "=" * 160)
    print("สรุปผล Backtest")
    print("=" * 160)
    print(f"ใช้เวลาทั้งหมด: {total_elapsed_time/60:.1f} นาที")
    print("\nผลลัพธ์:")
    for market_name, success in results.items():
        status = "✅ สำเร็จ" if success else "❌ มีปัญหา"
        print(f"  - {market_name}: {status}")
    
    # รันการเปรียบเทียบผลลัพธ์
    print("\n" + "=" * 160)
    print("🔍 เริ่มการเปรียบเทียบผลลัพธ์...")
    print("=" * 160)
    
    try:
        compare_result = subprocess.run(
            ['python', 'scripts/compare_before_after_tp_adjustment.py'],
            cwd=BASE_DIR,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if compare_result.returncode == 0:
            print("\n✅ การเปรียบเทียบผลลัพธ์เสร็จสิ้น")
        else:
            print("\n⚠️  การเปรียบเทียบผลลัพธ์มีปัญหา")
            
    except Exception as e:
        print(f"\n❌ Error running comparison: {e}")
    
    print("\n" + "=" * 160)
    print("✅ กระบวนการเสร็จสิ้น")
    print("=" * 160)
    print("\n💡 คำแนะนำ:")
    print("   - ตรวจสอบผลลัพธ์ในตารางเปรียบเทียบด้านบน")
    print("   - รัน 'python scripts/create_comparison_table_final.py' เพื่อดูตารางสรุป")
    print("=" * 160)

if __name__ == "__main__":
    main()

