#!/usr/bin/env python
"""
Fix Test China - แก้ไขปัญหาการทดสอบ

ปัญหาที่พบ:
- Backtest ข้ามหุ้นเพราะมีผลลัพธ์เก่า
- ต้องลบไฟล์เก่าก่อนรันทดสอบ
"""

import os
import sys

def clean_old_results():
    """Clean old results before testing"""
    files_to_clean = [
        'data/full_backtest_results.csv',
        'logs/trade_history_CHINA.csv',
        'data/china_realistic_settings_results.csv'
    ]
    
    print("Cleaning old results...")
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"  ✅ Removed: {file}")
        else:
            print(f"  ⏭️  Not found: {file}")
    
    # Also clean China entries from symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            import pandas as pd
            df = pd.read_csv(perf_file)
            df = df[df['Country'] != 'CN']
            df.to_csv(perf_file, index=False)
            print(f"  ✅ Cleaned China entries from {perf_file}")
        except Exception as e:
            print(f"  ⚠️  Could not clean {perf_file}: {e}")
    
    print("\n✅ Cleanup complete!")
    print("Now you can run: python scripts/test_china_realistic_settings.py")

if __name__ == '__main__':
    clean_old_results()

