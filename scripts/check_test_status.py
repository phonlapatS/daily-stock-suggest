#!/usr/bin/env python
"""
Check Test Status - ตรวจสอบสถานะการทดสอบ
"""

import sys
import os
import pandas as pd
import io
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_status():
    """Check test status"""
    results_file = 'data/china_realistic_settings_results.csv'
    log_file = 'logs/trade_history_CHINA.csv'
    
    print("="*100)
    print("Checking Test Status...")
    print("="*100)
    
    if os.path.exists(results_file):
        print("\n✅ Test Completed!")
        print(f"   Results file: {results_file}")
        
        df = pd.read_csv(results_file)
        print(f"\n   Total Results: {len(df)} combinations tested")
        
        if len(df) > 0:
            best = df.loc[df['score'].idxmax()]
            print(f"\n   Best Combination:")
            print(f"     TP: {best['tp']}%")
            print(f"     Max Hold: {best['max_hold']} days")
            print(f"     SL: {best['sl']}%")
            print(f"     Score: {best['score']}/13")
            print(f"     RRR: {best['rrr']:.2f}")
            print(f"     TP Rate: {best['tp_rate']:.1f}%")
            
            # Check if acceptable
            acceptable = (
                best['tp_rate'] >= 15 and
                best['max_hold_rate'] < 60 and
                best['rrr'] >= 1.2 and
                best['hold_over_7_pct'] < 30
            )
            
            if acceptable:
                print(f"\n   ✅ ✅ ✅ ACCEPTABLE - ผลลัพธ์พอรับได้!")
            else:
                print(f"\n   ⚠️  มีปัญหา - ต้องพิจารณา")
    else:
        print("\n⏳ Test Still Running...")
        
        if os.path.exists(log_file):
            df_log = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
            print(f"   Found {len(df_log)} trades in log file")
            print(f"   Test may be in progress...")
        else:
            print(f"   No log file yet - test may still be starting")
        
        print(f"\n   Please wait...")
        print(f"   Expected time: 30-60 minutes for 18 tests")

if __name__ == '__main__':
    check_status()

