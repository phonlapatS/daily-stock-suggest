#!/usr/bin/env python
"""
Notify When Test Done - แจ้งเมื่อทดสอบเสร็จ

รอให้การทดสอบเสร็จแล้วแสดงผลลัพธ์
"""

import sys
import os
import pandas as pd
import time
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def wait_and_notify():
    """Wait for test to complete and notify"""
    results_file = 'data/china_realistic_settings_results.csv'
    
    print("="*100)
    print("Waiting for Test to Complete...")
    print("="*100)
    print("\nTest Parameters:")
    print("  TP: 3.5%, 4.0%, 4.5%")
    print("  Max Hold: 5, 6, 7 days")
    print("  SL: 1.0%, 1.2%")
    print("  Total: 18 combinations")
    print("\nExpected Time: 30-60 minutes")
    print("\nMonitoring... (Press Ctrl+C to stop monitoring)")
    print("="*100)
    
    check_count = 0
    last_size = 0
    
    try:
        while True:
            check_count += 1
            
            if os.path.exists(results_file):
                # Check if file is complete (not being written)
                current_size = os.path.getsize(results_file)
                time.sleep(2)  # Wait a bit
                new_size = os.path.getsize(results_file)
                
                if current_size == new_size:
                    # File is complete
                    print(f"\n\n{'='*100}")
                    print("✅ ✅ ✅ TEST COMPLETED!")
                    print(f"{'='*100}\n")
                    
                    # Read and display results
                    df = pd.read_csv(results_file)
                    
                    print(f"Total Results: {len(df)} combinations tested\n")
                    
                    # Sort by score
                    df_sorted = df.sort_values('score', ascending=False)
                    
                    # Display top 5
                    print("Top 5 Combinations:")
                    print("="*100)
                    print(f"{'Rank':<6} {'TP':<6} {'Max Hold':<10} {'SL':<6} {'Score':<8} {'RRR':<8} {'TP Rate':<10} {'MAX_HOLD Rate':<12} {'Avg Hold':<10}")
                    print("-" * 100)
                    
                    for idx, (i, row) in enumerate(df_sorted.head(5).iterrows(), 1):
                        print(f"{idx:<6} {row['tp']:<6} {row['max_hold']:<10} {row['sl']:<6} {row['score']:<8} {row['rrr']:>6.2f}   {row['tp_rate']:>6.1f}%     {row['max_hold_rate']:>10.1f}%        {row['avg_hold_days']:>8.1f}")
                    
                    # Best combination
                    best = df_sorted.iloc[0]
                    
                    print(f"\n{'='*100}")
                    print("BEST COMBINATION")
                    print(f"{'='*100}")
                    print(f"  TP: {best['tp']}%")
                    print(f"  Max Hold: {best['max_hold']} days")
                    print(f"  SL: {best['sl']}%")
                    print(f"  Score: {best['score']}/13")
                    print(f"\n  Performance:")
                    print(f"    Stocks Passing: {best['stocks_passing']}")
                    print(f"    Total Trades: {best['total_trades']}")
                    print(f"    Win Rate: {best['win_rate']:.1f}%")
                    print(f"    RRR: {best['rrr']:.2f}")
                    print(f"    Expectancy: {best['expectancy']:.2f}%")
                    print(f"    TP Hit Rate: {best['tp_rate']:.1f}%")
                    print(f"    MAX_HOLD Rate: {best['max_hold_rate']:.1f}%")
                    print(f"    Avg Hold Days: {best['avg_hold_days']:.1f} days")
                    print(f"    Max Hold Days: {best['max_hold_days']:.0f} days")
                    print(f"    Hold >7 days: {best['hold_over_7_pct']:.1f}%")
                    
                    # Assessment
                    print(f"\n  Assessment:")
                    acceptable = (
                        best['tp_rate'] >= 15 and
                        best['max_hold_rate'] < 60 and
                        best['rrr'] >= 1.2 and
                        best['hold_over_7_pct'] < 30
                    )
                    
                    if acceptable:
                        print(f"    ✅ ✅ ✅ ACCEPTABLE - ผลลัพธ์พอรับได้!")
                        print(f"\n  Recommendations:")
                        print(f"    1. ✅ ใช้ค่าที่ดีที่สุดนี้")
                        print(f"    2. ✅ อัพเดท backtest.py")
                        print(f"    3. ✅ ทดสอบอีกครั้งเพื่อยืนยัน")
                    else:
                        print(f"    ⚠️  มีปัญหา:")
                        if best['tp_rate'] < 15:
                            print(f"      - TP Hit Rate ต่ำ ({best['tp_rate']:.1f}%)")
                        if best['max_hold_rate'] >= 60:
                            print(f"      - MAX_HOLD Rate สูง ({best['max_hold_rate']:.1f}%)")
                        if best['rrr'] < 1.2:
                            print(f"      - RRR ต่ำ ({best['rrr']:.2f})")
                        if best['hold_over_7_pct'] >= 30:
                            print(f"      - Hold >7 days สูง ({best['hold_over_7_pct']:.1f}%)")
                        print(f"\n  Recommendations:")
                        print(f"    1. ⚠️  พิจารณาปรับ parameters")
                        print(f"    2. ⚠️  ทดสอบเพิ่มเติม")
                    
                    print(f"\n{'='*100}")
                    print("Results saved to: data/china_realistic_settings_results.csv")
                    print(f"{'='*100}")
                    
                    break
                else:
                    # File is still being written
                    print(f"   [{check_count}] File being written... ({current_size} bytes)")
            
            else:
                # Check log file for progress
                log_file = 'logs/trade_history_CHINA.csv'
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = sum(1 for _ in f)
                        print(f"   [{check_count}] Progress: {lines} trades logged...")
                    except:
                        print(f"   [{check_count}] Checking...")
                else:
                    if check_count % 10 == 0:  # Print every 10 checks
                        print(f"   [{check_count}] Waiting for test to start...")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped by user")
        print(f"Test may still be running in background")
        print(f"Check status later with: python scripts/check_test_status.py")

if __name__ == '__main__':
    wait_and_notify()

