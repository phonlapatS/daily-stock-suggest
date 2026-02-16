#!/usr/bin/env python
"""
Clean All Cache - ลบ cache ทั้งหมดเพื่อรัน backtest ใหม่

หลังจากแก้ไข logic ใน backtest.py แล้ว ควรลบ cache เพื่อให้:
1. Backtest ดึงข้อมูลใหม่ทั้งหมด
2. ใช้ค่าที่แก้ไขแล้ว (threshold, RM, gatekeeper)
3. ไม่ใช้ผลลัพธ์เก่าที่ผิดพลาด
"""

import sys
import os
import glob
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_all_cache():
    """ลบ cache ทั้งหมด"""
    
    print("="*100)
    print("Clean All Cache - ลบ cache ทั้งหมด")
    print("="*100)
    print()
    
    deleted_count = 0
    errors = []
    
    # 1. ลบ cache files ใน data/cache/
    cache_dir = 'data/cache'
    if os.path.exists(cache_dir):
        cache_files = glob.glob(os.path.join(cache_dir, '*.csv')) + glob.glob(os.path.join(cache_dir, '*.pkl'))
        for file_path in cache_files:
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"✅ ลบ: {file_path}")
            except Exception as e:
                errors.append(f"❌ ไม่สามารถลบ {file_path}: {e}")
    
    # 2. ลบ trade_history files (แต่เก็บ trade_history.csv ไว้เป็น backup)
    logs_dir = 'logs'
    if os.path.exists(logs_dir):
        trade_history_files = glob.glob(os.path.join(logs_dir, 'trade_history_*.csv'))
        for file_path in trade_history_files:
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"✅ ลบ: {file_path}")
            except Exception as e:
                errors.append(f"❌ ไม่สามารถลบ {file_path}: {e}")
    
    # 3. ลบหรือทำความสะอาด symbol_performance.csv (ลบเฉพาะ entries ที่เกี่ยวข้อง)
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            # อ่านไฟล์
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            original_count = len(df)
            
            # ลบทั้งหมด (จะสร้างใหม่เมื่อรัน backtest)
            os.remove(perf_file)
            deleted_count += 1
            print(f"✅ ลบ: {perf_file} ({original_count} entries)")
        except Exception as e:
            errors.append(f"❌ ไม่สามารถลบ {perf_file}: {e}")
    
    # 4. ลบหรือทำความสะอาด full_backtest_results.csv (ลบเฉพาะ entries ที่เกี่ยวข้อง)
    full_results_file = 'data/full_backtest_results.csv'
    if os.path.exists(full_results_file):
        try:
            # อ่านไฟล์
            df = pd.read_csv(full_results_file, on_bad_lines='skip', engine='python')
            original_count = len(df)
            
            # ลบทั้งหมด (จะสร้างใหม่เมื่อรัน backtest)
            os.remove(full_results_file)
            deleted_count += 1
            print(f"✅ ลบ: {full_results_file} ({original_count} entries)")
        except Exception as e:
            errors.append(f"❌ ไม่สามารถลบ {full_results_file}: {e}")
    
    # 5. แสดงผลสรุป
    print()
    print("="*100)
    print("สรุปผลการลบ Cache")
    print("="*100)
    print()
    
    if deleted_count > 0:
        print(f"✅ ลบ cache แล้ว: {deleted_count} ไฟล์")
        print()
        print("📋 ไฟล์ที่ลบ:")
        print("   - data/cache/*.csv, *.pkl (cache files)")
        print("   - logs/trade_history_*.csv (trade history)")
        print("   - data/symbol_performance.csv (performance summary)")
        print("   - data/full_backtest_results.csv (full results)")
        print()
        print("💡 ขั้นตอนต่อไป:")
        print("   1. รัน backtest ใหม่สำหรับแต่ละประเทศ:")
        print("      python scripts/backtest.py --full --bars 2000 --group THAI")
        print("      python scripts/backtest.py --full --bars 2000 --group US")
        print("      python scripts/backtest.py --full --bars 2000 --group CHINA")
        print("      python scripts/backtest.py --full --bars 2000 --group TAIWAN")
        print()
        print("   2. รัน calculate_metrics เพื่อสร้าง performance summary:")
        print("      python scripts/calculate_metrics.py")
        print()
    else:
        print("ℹ️  ไม่พบไฟล์ cache ที่ต้องลบ")
        print()
    
    if errors:
        print("⚠️  ข้อผิดพลาด:")
        for error in errors:
            print(f"   {error}")
        print()
    
    return deleted_count

def clean_market_cache(market_group):
    """ลบ cache เฉพาะประเทศ"""
    
    print("="*100)
    print(f"Clean Cache for {market_group} - ลบ cache เฉพาะ {market_group}")
    print("="*100)
    print()
    
    deleted_count = 0
    errors = []
    
    # 1. ลบ trade_history สำหรับประเทศนั้น
    trade_history_file = f'logs/trade_history_{market_group}.csv'
    if os.path.exists(trade_history_file):
        try:
            os.remove(trade_history_file)
            deleted_count += 1
            print(f"✅ ลบ: {trade_history_file}")
        except Exception as e:
            errors.append(f"❌ ไม่สามารถลบ {trade_history_file}: {e}")
    
    # 2. ลบ entries จาก symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
            original_count = len(df)
            
            # Filter by market group
            if 'Country' in df.columns:
                # Map market_group to country codes
                country_map = {
                    'THAI': ['TH'],
                    'US': ['US'],
                    'CHINA': ['CN', 'HK'],
                    'TAIWAN': ['TW']
                }
                
                countries_to_remove = country_map.get(market_group, [])
                if countries_to_remove:
                    df_cleaned = df[~df['Country'].isin(countries_to_remove)]
                    df_cleaned.to_csv(perf_file, index=False)
                    deleted_count += original_count - len(df_cleaned)
                    print(f"✅ ทำความสะอาด: {perf_file} (ลบ {original_count - len(df_cleaned)} entries)")
        except Exception as e:
            errors.append(f"❌ ไม่สามารถทำความสะอาด {perf_file}: {e}")
    
    # 3. ลบ entries จาก full_backtest_results.csv
    full_results_file = 'data/full_backtest_results.csv'
    if os.path.exists(full_results_file):
        try:
            df = pd.read_csv(full_results_file, on_bad_lines='skip', engine='python')
            original_count = len(df)
            
            # Filter by market group (check both 'country' and 'group' columns)
            country_map = {
                'THAI': ['TH', 'GROUP_A_THAI'],
                'US': ['US', 'GROUP_B_US'],
                'CHINA': ['CN', 'HK', 'GROUP_C_CHINA_HK'],
                'TAIWAN': ['TW', 'GROUP_D_TAIWAN']
            }
            
            countries_to_remove = country_map.get(market_group, [])
            if countries_to_remove:
                # Try 'country' column first
                if 'country' in df.columns:
                    df_cleaned = df[~df['country'].isin(countries_to_remove)]
                # Try 'group' column (for full_backtest_results.csv)
                elif 'group' in df.columns:
                    df_cleaned = df[~df['group'].str.contains('|'.join(countries_to_remove), case=False, na=False)]
                else:
                    df_cleaned = df
                
                if len(df_cleaned) < original_count:
                    df_cleaned.to_csv(full_results_file, index=False)
                    deleted_count += original_count - len(df_cleaned)
                    print(f"✅ ทำความสะอาด: {full_results_file} (ลบ {original_count - len(df_cleaned)} entries)")
        except Exception as e:
            errors.append(f"❌ ไม่สามารถทำความสะอาด {full_results_file}: {e}")
    
    # 4. แสดงผลสรุป
    print()
    print("="*100)
    print(f"สรุปผลการลบ Cache สำหรับ {market_group}")
    print("="*100)
    print()
    
    if deleted_count > 0:
        print(f"✅ ลบ cache แล้ว: {deleted_count} ไฟล์/entries")
        print()
        print(f"💡 ขั้นตอนต่อไป:")
        print(f"   1. รัน backtest ใหม่สำหรับ {market_group}:")
        print(f"      python scripts/backtest.py --full --bars 2000 --group {market_group}")
        print()
        print(f"   2. รัน calculate_metrics เพื่ออัพเดท performance summary:")
        print(f"      python scripts/calculate_metrics.py")
        print()
    else:
        print("ℹ️  ไม่พบไฟล์ cache ที่ต้องลบ")
        print()
    
    if errors:
        print("⚠️  ข้อผิดพลาด:")
        for error in errors:
            print(f"   {error}")
        print()
    
    return deleted_count

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean cache files for backtest')
    parser.add_argument('--market', type=str, help='Clean cache for specific market (THAI, US, CHINA, TAIWAN)')
    parser.add_argument('--all', action='store_true', help='Clean all cache files')
    
    args = parser.parse_args()
    
    if args.all:
        clean_all_cache()
    elif args.market:
        clean_market_cache(args.market.upper())
    else:
        print("="*100)
        print("Clean Cache - ลบ cache files")
        print("="*100)
        print()
        print("Usage:")
        print("  # ลบ cache ทั้งหมด")
        print("  python scripts/clean_all_cache.py --all")
        print()
        print("  # ลบ cache เฉพาะประเทศ")
        print("  python scripts/clean_all_cache.py --market THAI")
        print("  python scripts/clean_all_cache.py --market US")
        print("  python scripts/clean_all_cache.py --market CHINA")
        print("  python scripts/clean_all_cache.py --market TAIWAN")
        print()
        print("="*100)
        print()
        print("⚠️  หมายเหตุ:")
        print("   - หลังจากแก้ไข logic ใน backtest.py แล้ว ควรลบ cache")
        print("   - เพื่อให้ backtest รันใหม่ด้วยค่าที่ถูกต้อง")
        print("   - ไม่ใช้ผลลัพธ์เก่าที่ผิดพลาด")
        print()

if __name__ == "__main__":
    main()

