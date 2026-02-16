#!/usr/bin/env python
"""
Debug China Backtest - ตรวจสอบว่าทำไม backtest ไม่แสดงผลลัพธ์
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def debug_china_backtest():
    """ตรวจสอบว่าทำไม backtest ไม่แสดงผลลัพธ์"""
    
    print("="*80)
    print("Debug China Backtest")
    print("="*80)
    print()
    
    # 1. ตรวจสอบ group name
    print("1. ตรวจสอบ Group Name:")
    print("-" * 80)
    for group_name, group_config in config.ASSET_GROUPS.items():
        if 'CHINA' in group_name.upper() or 'HK' in group_name.upper():
            print(f"   ✅ {group_name}")
            print(f"      Description: {group_config.get('description', 'N/A')}")
            print(f"      Assets: {len(group_config.get('assets', []))} symbols")
            for asset in group_config.get('assets', [])[:5]:
                print(f"         - {asset.get('symbol', 'N/A')} ({asset.get('exchange', 'N/A')})")
            print()
    
    # 2. ตรวจสอบ full_backtest_results.csv
    print("2. ตรวจสอบ full_backtest_results.csv:")
    print("-" * 80)
    output_file = 'data/full_backtest_results.csv'
    if os.path.exists(output_file):
        try:
            df = pd.read_csv(output_file, on_bad_lines='skip', engine='python')
            print(f"   ✅ พบ: {output_file}")
            print(f"   Total entries: {len(df)}")
            
            if 'group' in df.columns:
                # หา China/HK entries
                china_mask = df['group'].str.contains('CHINA|HK', case=False, na=False)
                china_entries = df[china_mask]
                
                print(f"   China/HK entries: {len(china_entries)}")
                
                if len(china_entries) > 0:
                    print("   ⚠️  พบ China/HK entries:")
                    for idx, row in china_entries.head(5).iterrows():
                        symbol = row.get('symbol', 'N/A')
                        group = row.get('group', 'N/A')
                        total = row.get('total', 0)
                        print(f"      - {symbol} ({group}): {total} trades")
                else:
                    print("   ✅ ไม่มี China/HK entries (พร้อมรัน backtest ใหม่)")
            else:
                print("   ⚠️  ไม่มี column 'group'")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"   ℹ️  ไม่พบ: {output_file}")
    
    print()
    
    # 3. ตรวจสอบ processed_symbols logic
    print("3. ตรวจสอบ Processed Symbols Logic:")
    print("-" * 80)
    target_group = 'CHINA'
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file, on_bad_lines='skip', engine='python')
            if 'symbol' in df_existing.columns:
                if 'group' in df_existing.columns:
                    group_filter = df_existing['group'].str.upper().str.contains(target_group.upper(), na=False)
                    processed_symbols = set(df_existing[group_filter]['symbol'].tolist())
                    print(f"   Processed symbols (จะถูก skip): {len(processed_symbols)}")
                    if processed_symbols:
                        print(f"   Symbols: {list(processed_symbols)[:10]}")
                    else:
                        print("   ✅ ไม่มี symbols ที่จะถูก skip (พร้อมรัน backtest ใหม่)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print()
    print("="*80)
    print("สรุป:")
    print("="*80)
    print("ถ้าไม่มี China/HK entries และไม่มี processed symbols")
    print("→ backtest ควรรันได้ปกติ")
    print()
    print("ถ้า backtest ยังไม่แสดงผลลัพธ์ อาจเป็นเพราะ:")
    print("  1. ไม่มี trades ที่ผ่าน gatekeeper")
    print("  2. มีปัญหาในการดึงข้อมูล")
    print("  3. มี error ที่ไม่แสดง")
    print("="*80)

if __name__ == '__main__':
    debug_china_backtest()

