#!/usr/bin/env python
"""
Run China Market V13.4 Backtest
ลบ cache เก่าและรัน backtest ใหม่
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
    print("="*100)
    print("Cleaning Old Results...")
    print("="*100)
    
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
                print(f"✅ Removed China stocks from {perf_file}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean {perf_file}: {e}")
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not remove {file_path}: {e}")
        else:
            print(f"ℹ️  Not found: {file_path} (skipping)")
    
    print("✅ Cleanup complete!")
    print("")

def run_backtest():
    """Run backtest for China Market"""
    print("="*100)
    print("Running China Market V13.4 Backtest...")
    print("="*100)
    print("")
    print("Parameters:")
    print("  - SL: 1.0%")
    print("  - TP: 4.0%")
    print("  - Max Hold: 3 days")
    print("  - min_prob: 50.0%")
    print("  - Display Criteria: RRR >= 1.0, Count >= 15")
    print("")
    
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', '2000',
        '--group', 'CHINA',
        '--fast'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("")
    print("⏳ Running backtest (this may take a while)...")
    print("")
    
    result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"❌ Backtest failed with exit code {result.returncode}")
        return False
    
    print("")
    print("✅ Backtest complete!")
    return True

def calculate_metrics():
    """Calculate metrics"""
    print("")
    print("="*100)
    print("Calculating Metrics...")
    print("="*100)
    print("")
    
    cmd = ['python', 'scripts/calculate_metrics.py']
    
    result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"❌ Calculate metrics failed with exit code {result.returncode}")
        return False
    
    print("")
    print("✅ Metrics calculated!")
    return True

def analyze_results():
    """Analyze results"""
    print("")
    print("="*100)
    print("Analyzing Results...")
    print("="*100)
    print("")
    
    # Run stability analysis
    cmd = ['python', 'scripts/analyze_china_stability.py']
    
    result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode != 0:
        print(f"⚠️ Warning: Stability analysis failed")
    
    # Show detailed metrics
    print("")
    cmd2 = ['python', 'scripts/show_china_detailed_metrics.py']
    
    result2 = subprocess.run(cmd2, capture_output=False, text=True, encoding='utf-8', errors='replace')
    
    if result2.returncode != 0:
        print(f"⚠️ Warning: Detailed metrics failed")
    
    return True

if __name__ == '__main__':
    print("="*100)
    print("China Market V13.4 Backtest")
    print("="*100)
    print("")
    
    # Step 1: Clean old results
    clean_old_results()
    
    # Step 2: Run backtest
    if not run_backtest():
        print("❌ Backtest failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Calculate metrics
    if not calculate_metrics():
        print("❌ Calculate metrics failed. Exiting.")
        sys.exit(1)
    
    # Step 4: Analyze results
    analyze_results()
    
    print("")
    print("="*100)
    print("✅ All steps complete!")
    print("="*100)

