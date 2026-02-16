#!/usr/bin/env python
"""
Run China Market Backtest (Final) - รัน backtest สำหรับ China Market V13.4
"""

import sys
import os
import subprocess
import time
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_old_results():
    """Clean old backtest results for China"""
    print("Cleaning old results...")
    
    files_to_remove = [
        'logs/trade_history_CHINA.csv',
        'data/full_backtest_results.csv'
    ]
    
    # Remove China stocks from symbol_performance.csv
    perf_file = 'data/symbol_performance.csv'
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            if 'Country' in df.columns:
                df = df[df['Country'] != 'CN']
                df.to_csv(perf_file, index=False)
                print("✅ Removed China stocks from symbol_performance.csv")
        except:
            pass
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except:
                pass

def run_backtest():
    """Run backtest for China Market V13.4"""
    print("\n" + "="*100)
    print("Running China Market V13.4 Backtest")
    print("="*100)
    print("\nConfiguration:")
    print("  - SL: 1.0%")
    print("  - TP: 4.0%")
    print("  - Max Hold: 3 days")
    print("  - min_prob: 50.0%")
    print("  - n_bars: 2000")
    print("  - Display Criteria: RRR >= 1.0, Count >= 15")
    print("")
    
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', '2000',
        '--group', 'CHINA',
        '--fast'
    ]
    
    print("⏳ Running backtest...")
    print("")
    
    result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"\n❌ Backtest failed")
        return False
    
    print("\n✅ Backtest complete!")
    return True

def calculate_metrics():
    """Calculate metrics"""
    print("\nCalculating metrics...")
    
    cmd = ['python', 'scripts/calculate_metrics.py']
    result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"❌ Calculate metrics failed")
        return False
    
    print("✅ Metrics calculated!")
    return True

if __name__ == '__main__':
    print("="*100)
    print("China Market V13.4 - Final Backtest")
    print("="*100)
    
    # Clean old results
    clean_old_results()
    
    # Run backtest
    if run_backtest():
        # Calculate metrics
        calculate_metrics()
        
        print("\n" + "="*100)
        print("✅ All steps complete!")
        print("="*100)
        print("\nView results:")
        print("  - python scripts/show_china_detailed_metrics.py")
        print("  - python scripts/analyze_china_v13_4_stability.py")
    else:
        print("\n❌ Backtest failed")

