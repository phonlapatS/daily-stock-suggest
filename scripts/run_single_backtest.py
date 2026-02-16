#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
รัน backtest ทีละตลาด (ง่ายกว่า - ไม่งง)
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
    """ลบ cache ทั้งหมด"""
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
        print(f"🗑️  ลบ cache แล้ว ({deleted_count} ไฟล์)\n")
    else:
        print("ℹ️  ไม่พบไฟล์ cache\n")

def clean_trade_history(market):
    """ลบไฟล์ trade_history สำหรับตลาดที่ระบุ"""
    file_path = os.path.join(LOGS_DIR, f'trade_history_{market}.csv')
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"🗑️  ลบไฟล์เก่า: trade_history_{market}.csv")
        except Exception as e:
            print(f"⚠️  ไม่สามารถลบไฟล์: {e}")

def run_backtest(market_name, group_name, tp, trail, max_hold):
    """รัน backtest สำหรับตลาดเดียว"""
    print("\n" + "=" * 80)
    print(f"🚀 เริ่ม Backtest: {market_name}")
    print("=" * 80)
    print(f"TP: {tp}x | Trailing: {trail}% | Max Hold: {max_hold} days")
    print("=" * 80)
    
    command = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', '2500',  # ใช้ 2500 bars เพื่อข้อมูลมากขึ้น
        '--group', group_name,
        '--atr_tp_mult', str(tp),
        '--trail_activate', str(trail),
        '--max_hold', str(max_hold),
        '--fast'
    ]
    
    print(f"คำสั่ง: {' '.join(command)}")
    print("=" * 80 + "\n")
    
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
        print(f"\n❌ Error: {e}")
        return False

def main():
    """รัน backtest ทีละตลาด"""
    
    print("\n" + "=" * 80)
    print("📊 Backtest ทีละตลาด (ค่าเดิม)")
    print("=" * 80)
    
    # ตลาดทั้งหมด (ค่าเดิม)
    markets = {
        '1': {
            'name': 'US STOCK',
            'group': 'US',
            'tp': 5.0,  # ค่าเดิม
            'trail': 1.5,  # ค่าเดิม
            'max_hold': 5,
            'file_key': 'US'
        },
        '2': {
            'name': 'CHINA/HK STOCK',
            'group': 'CHINA',
            'tp': 5.0,  # ค่าเดิม
            'trail': 1.0,  # ค่าเดิม
            'max_hold': 3,
            'file_key': 'CHINA'
        },
        '3': {
            'name': 'TAIWAN STOCK',
            'group': 'TAIWAN',
            'tp': 6.5,  # ค่าเดิม
            'trail': 1.0,  # ค่าเดิม
            'max_hold': 10,
            'file_key': 'TAIWAN'
        },
        '4': {
            'name': 'THAI STOCK',
            'group': 'THAI',
            'tp': 3.5,  # ค่าเดิม
            'trail': 1.5,  # ค่าเดิม
            'max_hold': 5,
            'file_key': 'THAI'
        }
    }
    
    print("\nเลือกตลาดที่จะรัน:")
    print("-" * 80)
    for key, market in markets.items():
        print(f"  {key}. {market['name']} (TP {market['tp']}x, Trailing {market['trail']}%, Max Hold {market['max_hold']} days)")
    print("  5. รันทั้งหมด")
    print("  0. ออก")
    print("-" * 80)
    
    choice = input("\nเลือก (0-5): ").strip()
    
    if choice == '0':
        print("ออกจากโปรแกรม")
        return
    
    # ลบ cache
    print("\n🧹 กำลังลบ cache...")
    clear_cache()
    
    if choice == '5':
        # รันทั้งหมด
        print("\n🚀 เริ่มรัน backtest ทั้งหมด...\n")
        for key, market in markets.items():
            clean_trade_history(market['file_key'])
            run_backtest(
                market['name'],
                market['group'],
                market['tp'],
                market['trail'],
                market['max_hold']
            )
            print("\n" + "=" * 80 + "\n")
    elif choice in markets:
        # รันตลาดเดียว
        market = markets[choice]
        clean_trade_history(market['file_key'])
        run_backtest(
            market['name'],
            market['group'],
            market['tp'],
            market['trail'],
            market['max_hold']
        )
        
        # แสดงผลลัพธ์
        print("\n" + "=" * 80)
        print("📊 ตรวจสอบผลลัพธ์:")
        print("=" * 80)
        print(f"python scripts/compare_before_after_tp_adjustment.py")
        print("=" * 80)
    else:
        print("❌ เลือกไม่ถูกต้อง")

if __name__ == "__main__":
    main()

