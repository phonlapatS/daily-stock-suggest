#!/usr/bin/env python
"""
Check Taiwan Cache - ตรวจสอบ cache สำหรับ Taiwan market
"""

import sys
import os
import pandas as pd
import io
import glob

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_taiwan_cache():
    """ตรวจสอบ cache สำหรับ Taiwan market"""
    
    print("="*80)
    print("Check Taiwan Cache - ตรวจสอบ cache สำหรับ Taiwan Market")
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
                # หา Taiwan entries
                taiwan_mask = df['group'].str.contains('TAIWAN|TW', case=False, na=False)
                taiwan_entries = df[taiwan_mask]
                
                print(f"   Taiwan entries: {len(taiwan_entries)}")
                
                if len(taiwan_entries) > 0:
                    print()
                    print("   ⚠️  พบ Taiwan entries ที่จะทำให้ backtest skip symbols:")
                    print()
                    for idx, row in taiwan_entries.iterrows():
                        symbol = row.get('symbol', 'N/A')
                        group = row.get('group', 'N/A')
                        total = row.get('total', 0)
                        print(f"      - {symbol} ({group}): {total} trades")
                    print()
                    print("   💡 ต้องลบ entries เหล่านี้ออกเพื่อให้ backtest รันใหม่")
                else:
                    print("   ✅ ไม่มี Taiwan entries")
            else:
                print("   ⚠️  ไม่มี column 'group' - ไม่สามารถ filter ได้")
                
        except Exception as e:
            print(f"❌ Error reading {output_file}: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {output_file}")
    
    print()
    
    # 2. ตรวจสอบ trade_history_TAIWAN.csv
    trade_history_file = 'logs/trade_history_TAIWAN.csv'
    if os.path.exists(trade_history_file):
        try:
            df = pd.read_csv(trade_history_file, on_bad_lines='skip', engine='python')
            print(f"✅ พบ: {trade_history_file}")
            print(f"   Total trades: {len(df)}")
            if 'symbol' in df.columns:
                symbols = df['symbol'].unique()
                print(f"   Symbols: {len(symbols)} symbols")
                print(f"   Sample: {list(symbols[:5])}")
        except Exception as e:
            print(f"❌ Error reading {trade_history_file}: {e}")
    else:
        print(f"ℹ️  ไม่พบ: {trade_history_file}")
    
    print()
    
    # 3. ตรวจสอบ cache files สำหรับ TWSE
    cache_dir = 'data/cache'
    if os.path.exists(cache_dir):
        cache_files = glob.glob(os.path.join(cache_dir, 'TWSE_*.csv'))
        print(f"✅ พบ cache files: {len(cache_files)} ไฟล์")
        if cache_files:
            print(f"   Sample: {[os.path.basename(f) for f in cache_files[:5]]}")
    
    print()
    
    # 4. ตรวจสอบ processed_symbols logic
    print("4. ตรวจสอบ Processed Symbols Logic:")
    print("-" * 80)
    target_group = 'TAIWAN'
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

if __name__ == '__main__':
    check_taiwan_cache()

