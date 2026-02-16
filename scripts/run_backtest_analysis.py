#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_backtest_analysis.py - รัน Backtest และวิเคราะห์ผลลัพธ์อัตโนมัติ
================================================================================
สคริปต์ที่รันง่ายสำหรับทดสอบและตรวจสอบผลลัพธ์

Usage:
    python scripts/run_backtest_analysis.py              # รัน quick test (4 หุ้น, 1000 bars)
    python scripts/run_backtest_analysis.py --bars 500 # ระบุจำนวน bars
    python scripts/run_backtest_analysis.py --all       # รันทุกหุ้น (sample)
"""

import sys
import os
import subprocess

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_backtest(n_bars=1000, mode='quick'):
    """รัน backtest"""
    print("\n" + "=" * 80)
    print("🚀 เริ่มรัน Backtest")
    print("=" * 80)
    print(f"Mode: {mode}")
    print(f"Test Bars: {n_bars}")
    print("=" * 80)
    
    if mode == 'quick':
        cmd = ['python', 'scripts/backtest.py', '--quick', '--bars', str(n_bars)]
    elif mode == 'all':
        cmd = ['python', 'scripts/backtest.py', '--all', '--bars', str(n_bars)]
    else:
        cmd = ['python', 'scripts/backtest.py', '--quick', '--bars', str(n_bars)]
    
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        return False

def run_analysis():
    """รันการวิเคราะห์ผลลัพธ์"""
    print("\n" + "=" * 80)
    print("📊 เริ่มวิเคราะห์ผลลัพธ์")
    print("=" * 80)
    
    cmd = ['python', 'scripts/analyze_backtest_results.py']
    
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="รัน Backtest และวิเคราะห์ผลลัพธ์อัตโนมัติ")
    parser.add_argument('--bars', type=int, default=1000, help='จำนวน test bars (default: 1000)')
    parser.add_argument('--mode', type=str, default='quick', choices=['quick', 'all'], 
                       help='Mode: quick (4 หุ้น) หรือ all (ทุกหุ้น)')
    parser.add_argument('--skip-backtest', action='store_true', 
                       help='ข้ามการรัน backtest (วิเคราะห์ผลลัพธ์เก่า)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🔬 BACKTEST & ANALYSIS TOOL")
    print("=" * 80)
    print(f"Test Bars: {args.bars}")
    print(f"Mode: {args.mode}")
    print("=" * 80)
    
    # Step 1: Run Backtest
    if not args.skip_backtest:
        print("\n📝 Step 1: Running Backtest...")
        success = run_backtest(args.bars, args.mode)
        if not success:
            print("❌ Backtest failed!")
            return
        print("✅ Backtest completed!")
    else:
        print("\n⏭️  ข้ามการรัน Backtest (ใช้ผลลัพธ์เก่า)")
    
    # Step 2: Run Analysis
    print("\n📊 Step 2: Analyzing Results...")
    success = run_analysis()
    if not success:
        print("❌ Analysis failed!")
        return
    print("✅ Analysis completed!")
    
    print("\n" + "=" * 80)
    print("✅ เสร็จสิ้น!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("   - ดูผลลัพธ์ใน logs/trade_history.csv")
    print("   - ปรับ filter criteria ใน scripts/backtest.py")
    print("   - รันอีกครั้งด้วย: python scripts/run_backtest_analysis.py --bars 1000")
    print("=" * 80)

if __name__ == "__main__":
    main()

