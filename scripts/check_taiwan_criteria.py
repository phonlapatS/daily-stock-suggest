#!/usr/bin/env python
"""
Check Taiwan Criteria - ตรวจสอบว่าหุ้นไต้หวันผ่านเกณฑ์หรือไม่
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_taiwan_criteria():
    """ตรวจสอบว่าหุ้นไต้หวันผ่านเกณฑ์หรือไม่"""
    
    print("="*80)
    print("Check Taiwan Criteria - ตรวจสอบหุ้นไต้หวัน")
    print("="*80)
    print()
    
    # 1. ตรวจสอบ full_backtest_results.csv
    print("1. ตรวจสอบ full_backtest_results.csv:")
    print("-" * 80)
    if os.path.exists('data/full_backtest_results.csv'):
        try:
            df = pd.read_csv('data/full_backtest_results.csv', on_bad_lines='skip', engine='python')
            tw = df[df['group'].str.contains('TAIWAN', case=False, na=False)]
            print(f"   Total Taiwan symbols: {len(tw)}")
            if len(tw) > 0:
                print(f"   Symbols: {', '.join(tw['symbol'].unique()[:20])}")
            else:
                print("   ❌ ไม่มีหุ้นไต้หวันใน full_backtest_results.csv")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("   ❌ ไม่พบไฟล์: data/full_backtest_results.csv")
    
    print()
    
    # 2. ตรวจสอบ symbol_performance.csv
    print("2. ตรวจสอบ symbol_performance.csv:")
    print("-" * 80)
    if os.path.exists('data/symbol_performance.csv'):
        try:
            df = pd.read_csv('data/symbol_performance.csv', on_bad_lines='skip', engine='python')
            tw = df[df['Country'] == 'TW']
            print(f"   Total Taiwan symbols: {len(tw)}")
            
            if len(tw) > 0:
                print()
                print("   Criteria: (Prob >= 49%, RRR >= 1.5) OR (Prob >= 55%, RRR >= 1.0), Count >= 15")
                print()
                
                # ตรวจสอบหุ้นที่ผ่านเกณฑ์
                passed = tw[
                    (
                        ((tw['Prob%'] >= 49.0) & (tw['RR_Ratio'] >= 1.5)) |
                        ((tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0))
                    ) &
                    (tw['Count'] >= 15) &
                    (tw['Count'] <= 2000)
                ]
                
                print(f"   ✅ Passed: {len(passed)} symbols")
                if len(passed) > 0:
                    print()
                    print(f"   {'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8}")
                    print("   " + "-" * 40)
                    for idx, row in passed.iterrows():
                        symbol = row.get('symbol', 'N/A')
                        prob = row.get('Prob%', 0)
                        rrr = row.get('RR_Ratio', 0)
                        count = row.get('Count', 0)
                        print(f"   {symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,}")
                else:
                    print()
                    print("   ❌ ไม่มีหุ้นที่ผ่านเกณฑ์")
                    print()
                    print("   ตรวจสอบหุ้นที่ใกล้เคียงเกณฑ์:")
                    print()
                    # หาหุ้นที่ใกล้เคียงเกณฑ์
                    near1 = tw[(tw['Prob%'] >= 49.0) & (tw['RR_Ratio'] >= 1.5) & (tw['Count'] >= 15)]
                    near2 = tw[(tw['Prob%'] >= 55.0) & (tw['RR_Ratio'] >= 1.0) & (tw['Count'] >= 15)]
                    near = pd.concat([near1, near2]).drop_duplicates()
                    
                    if len(near) > 0:
                        print(f"   {'Symbol':<10} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Issue':<20}")
                        print("   " + "-" * 60)
                        for idx, row in near.iterrows():
                            symbol = row.get('symbol', 'N/A')
                            prob = row.get('Prob%', 0)
                            rrr = row.get('RR_Ratio', 0)
                            count = row.get('Count', 0)
                            issues = []
                            if count > 2000:
                                issues.append("Count > 2000")
                            if not issues:
                                issues.append("OK")
                            print(f"   {symbol:<10} {prob:>7.1f}% {rrr:>7.2f} {count:>8,} {', '.join(issues)}")
                    else:
                        print("   ❌ ไม่มีหุ้นที่ใกล้เคียงเกณฑ์")
            else:
                print("   ❌ ไม่มีหุ้นไต้หวันใน symbol_performance.csv")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ❌ ไม่พบไฟล์: data/symbol_performance.csv")
    
    print()
    print("="*80)

if __name__ == '__main__':
    check_taiwan_criteria()

