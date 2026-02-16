#!/usr/bin/env python
"""
Check China Cache - ตรวจสอบ cache สำหรับ China market
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_china_cache():
    """ตรวจสอบ cache สำหรับ China market"""
    
    print("="*80)
    print("Check China Cache - ตรวจสอบ cache สำหรับ China Market")
    print("="*80)
    print()
    
    # 1. ตรวจสอบ full_backtest_results.csv
    output_file = 'data/full_backtest_results.csv'
    if os.path.exists(output_file):
        try:
            df = pd.read_csv(output_file, on_bad_lines='skip', engine='python')
            print(f"✅ พบ: {output_file}")
            print(f"   Total entries: {len(df)}")
            
            if 'group' in df.columns:
                # หา China/HK entries
                china_mask = df['group'].str.contains('CHINA|HK', case=False, na=False)
                china_entries = df[china_mask]
                
                print(f"   China/HK entries: {len(china_entries)}")
                
                if len(china_entries) > 0:
                    print()
                    print("   ⚠️  พบ China/HK entries ที่จะทำให้ backtest skip symbols:")
                    print()
                    for idx, row in china_entries.iterrows():
                        symbol = row.get('symbol', 'N/A')
                        group = row.get('group', 'N/A')
                        print(f"      - {symbol} ({group})")
                    print()
                    print("   💡 ต้องลบ entries เหล่านี้ออกเพื่อให้ backtest รันใหม่")
                else:
                    print("   ✅ ไม่มี China/HK entries")
            else:
                print("   ⚠️  ไม่มี column 'group' - ไม่สามารถ filter ได้")
                
        except Exception as e:
            print(f"❌ Error reading {output_file}: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {output_file}")
    
    print()
    
    # 2. ตรวจสอบ trade_history_CHINA.csv
    trade_history_file = 'logs/trade_history_CHINA.csv'
    if os.path.exists(trade_history_file):
        try:
            df = pd.read_csv(trade_history_file, on_bad_lines='skip', engine='python')
            print(f"✅ พบ: {trade_history_file}")
            print(f"   Total trades: {len(df)}")
        except Exception as e:
            print(f"❌ Error reading {trade_history_file}: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {trade_history_file}")
    
    print()
    print("="*80)

if __name__ == '__main__':
    check_china_cache()

