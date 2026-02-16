#!/usr/bin/env python
"""
Run China V13.9 Backtest - ลบ cache และรัน backtest ใหม่ด้วย V13.9 settings
"""

import sys
import os
import shutil
import subprocess
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_cache():
    """ลบ cache files สำหรับ China/HK"""
    
    print("="*100)
    print("Cleaning Cache Files - ลบ cache files")
    print("="*100)
    print()
    
    files_to_clean = [
        'logs/trade_history_CHINA.csv',
        'data/symbol_performance.csv',
        'data/full_backtest_results.csv'
    ]
    
    # Also clean specific China/HK entries from full_backtest_results.csv if exists
    cleaned_count = 0
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                # For full_backtest_results.csv, we might want to keep other markets
                # But for clean test, let's remove China/HK entries only
                if file_path == 'data/full_backtest_results.csv':
                    import pandas as pd
                    try:
                        df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
                        if 'group' in df.columns:
                            # Remove China/HK entries
                            before = len(df)
                            df = df[~df['group'].str.contains('CHINA|HK', case=False, na=False)]
                            after = len(df)
                            if before > after:
                                df.to_csv(file_path, index=False)
                                print(f"✅ Cleaned {before - after} China/HK entries from {file_path}")
                                cleaned_count += 1
                            else:
                                print(f"ℹ️  No China/HK entries found in {file_path}")
                        else:
                            # No group column, remove entire file
                            os.remove(file_path)
                            print(f"✅ Removed {file_path}")
                            cleaned_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not clean {file_path}: {e}")
                        # Fallback: remove entire file
                        os.remove(file_path)
                        print(f"✅ Removed {file_path} (fallback)")
                        cleaned_count += 1
                else:
                    # For other files, remove entirely
                    os.remove(file_path)
                    print(f"✅ Removed {file_path}")
                    cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")
        else:
            print(f"ℹ️  {file_path} does not exist (skip)")
    
    print()
    if cleaned_count > 0:
        print(f"✅ Cleaned {cleaned_count} file(s)")
    else:
        print("ℹ️  No files to clean")
    print()

def run_backtest():
    """รัน backtest ด้วย V13.9 settings"""
    
    print("="*100)
    print("Running China Backtest with V13.9 Settings")
    print("="*100)
    print()
    print("V13.9 Settings:")
    print("  - Min Prob: 54.0%")
    print("  - ATR TP: 5.0x (เพิ่มจาก 4.5x)")
    print("  - ATR SL: 1.0x")
    print("  - Max Hold: 3 days")
    print("  - Bars: 2000")
    print()
    print("Target:")
    print("  - RRR >= 1.40")
    print("  - Prob% >= 60%")
    print("  - Count >= 20")
    print("  - Stocks >= 4")
    print()
    
    # Run backtest
    print("="*100)
    print("Step 1: Running Backtest...")
    print("="*100)
    print()
    
    cmd = ['python', 'scripts/backtest.py', '--full', '--bars', '2000', '--group', 'CHINA']
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print()
        print("✅ Backtest completed successfully")
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Backtest failed with exit code {e.returncode}")
        return False
    
    print()
    print("="*100)
    print("Step 2: Calculating Metrics...")
    print("="*100)
    print()
    
    cmd = ['python', 'scripts/calculate_metrics.py']
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print()
        print("✅ Metrics calculation completed successfully")
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Metrics calculation failed with exit code {e.returncode}")
        return False
    
    return True

def main():
    """Main function"""
    
    print("="*100)
    print("China V13.9 Backtest - Clean and Run")
    print("="*100)
    print()
    print("This script will:")
    print("  1. Clean cache files (trade_history_CHINA.csv, symbol_performance.csv, etc.)")
    print("  2. Run backtest with V13.9 settings (min_prob 54.0%, ATR TP 5.0x)")
    print("  3. Calculate metrics")
    print()
    
    # Clean cache
    clean_cache()
    
    # Run backtest
    success = run_backtest()
    
    print()
    print("="*100)
    if success:
        print("✅ All steps completed successfully!")
        print()
        print("Next steps:")
        print("  1. Check the results in the terminal output above")
        print("  2. Run: python scripts/analyze_china_current_results.py")
        print("     to see detailed analysis")
    else:
        print("❌ Some steps failed. Please check the error messages above.")
    print("="*100)

if __name__ == "__main__":
    main()

