#!/usr/bin/env python
"""
Clean China Cache - ลบ cache สำหรับ China market
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

def clean_china_cache():
    """ลบ cache สำหรับ China market"""
    
    print("="*80)
    print("Clean China Cache - ลบ cache สำหรับ China Market")
    print("="*80)
    print()
    
    deleted_count = 0
    
    # 1. ลบ cache files สำหรับ HKEX (China/HK stocks)
    cache_dir = 'data/cache'
    if os.path.exists(cache_dir):
        cache_files = glob.glob(os.path.join(cache_dir, 'HKEX_*.csv'))
        if cache_files:
            for file_path in cache_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"✅ ลบ: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"❌ ไม่สามารถลบ {os.path.basename(file_path)}: {e}")
        else:
            print("ℹ️  ไม่พบ HKEX cache files")
    
    # 2. ลบ trade_history_CHINA.csv
    trade_history_file = 'logs/trade_history_CHINA.csv'
    if os.path.exists(trade_history_file):
        try:
            os.remove(trade_history_file)
            deleted_count += 1
            print(f"✅ ลบ: {trade_history_file}")
        except Exception as e:
            print(f"❌ ไม่สามารถลบ {trade_history_file}: {e}")
    
    # 3. ทำความสะอาด full_backtest_results.csv (ลบ entries ที่เป็น China)
    full_results_file = 'data/full_backtest_results.csv'
    if os.path.exists(full_results_file):
        try:
            df = pd.read_csv(full_results_file, on_bad_lines='skip', engine='python')
            original_count = len(df)
            
            # Filter out China/HK entries
            if 'group' in df.columns:
                df_cleaned = df[~df['group'].str.contains('CHINA|HK', case=False, na=False)]
                df_cleaned.to_csv(full_results_file, index=False)
                deleted_entries = original_count - len(df_cleaned)
                if deleted_entries > 0:
                    deleted_count += 1
                    print(f"✅ ทำความสะอาด: {full_results_file} (ลบ {deleted_entries} entries)")
        except Exception as e:
            print(f"❌ ไม่สามารถทำความสะอาด {full_results_file}: {e}")
    
    # 4. แสดงผลสรุป
    print()
    print("="*80)
    print("สรุปผลการลบ Cache")
    print("="*80)
    print()
    
    if deleted_count > 0:
        print(f"✅ ลบ cache แล้ว: {deleted_count} ไฟล์/entries")
        print()
        print("💡 ขั้นตอนต่อไป:")
        print("   python scripts/backtest.py --full --bars 2500 --group CHINA")
        print()
    else:
        print("ℹ️  ไม่พบไฟล์ cache ที่ต้องลบ")
        print()
    
    print("="*80)

if __name__ == '__main__':
    clean_china_cache()

