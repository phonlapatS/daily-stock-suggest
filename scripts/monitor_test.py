#!/usr/bin/env python
"""
Monitor Test Progress - ติดตามความคืบหน้าการทดสอบ
"""

import sys
import os
import time
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def monitor():
    """Monitor test progress"""
    results_file = 'data/china_realistic_settings_results.csv'
    log_file = 'logs/trade_history_CHINA.csv'
    
    print("="*100)
    print("Monitoring Test Progress...")
    print("="*100)
    print("\nPress Ctrl+C to stop monitoring")
    print("Test will continue running in background\n")
    
    last_count = 0
    check_count = 0
    
    try:
        while True:
            check_count += 1
            
            if os.path.exists(results_file):
                print(f"\n✅ Test Completed!")
                print(f"   Results file found: {results_file}")
                break
            
            if os.path.exists(log_file):
                # Count lines in log file
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = sum(1 for _ in f)
                    
                    if lines > last_count:
                        print(f"   [{check_count}] Progress: {lines} trades logged (increased by {lines - last_count})")
                        last_count = lines
                    else:
                        print(f"   [{check_count}] Waiting... ({lines} trades)")
                except:
                    print(f"   [{check_count}] Checking...")
            else:
                print(f"   [{check_count}] Waiting for test to start...")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped by user")
        print(f"Test is still running in background")
        print(f"Check status later with: python scripts/check_test_status.py")

if __name__ == '__main__':
    monitor()

