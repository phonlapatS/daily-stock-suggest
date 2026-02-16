#!/usr/bin/env python
"""
Run China Market Analysis - รัน backtest และวิเคราะห์ผลลัพธ์อัตโนมัติ

เป้าหมาย: หาค่าที่เสี่ยงน้อยและได้กำไรจริง
"""

import sys
import os
import subprocess
import time
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run backtest and analyze"""
    print("="*80)
    print("China Market - Running Backtest & Analysis")
    print("="*80)
    
    # Step 1: Run backtest
    print(f"\n{'='*80}")
    print("Step 1: Running Backtest...")
    print(f"{'='*80}")
    
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', '2000',
        '--group', 'CHINA',
        '--fast'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("This may take several minutes...")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"❌ Backtest failed with exit code {result.returncode}")
        return
    
    print("\n✅ Backtest completed!")
    
    # Step 2: Calculate metrics
    print(f"\n{'='*80}")
    print("Step 2: Calculating Metrics...")
    print(f"{'='*80}")
    
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=False)
    
    print("\n✅ Metrics calculated!")
    
    # Step 3: Analyze performance
    print(f"\n{'='*80}")
    print("Step 3: Analyzing Performance...")
    print(f"{'='*80}")
    
    subprocess.run(['python', 'scripts/analyze_china_performance.py'], capture_output=False)
    
    # Step 4: Analyze exit reasons
    print(f"\n{'='*80}")
    print("Step 4: Analyzing Exit Reasons...")
    print(f"{'='*80}")
    
    subprocess.run(['python', 'scripts/analyze_china_exit_reasons.py'], capture_output=False)
    
    print(f"\n{'='*80}")
    print("Analysis Complete!")
    print(f"{'='*80}")
    print("\nNext Steps:")
    print("1. Review the analysis results above")
    print("2. If needed, run optimization:")
    print("   python scripts/optimize_china_risk_profit.py")
    print("3. Adjust parameters based on results")

if __name__ == '__main__':
    main()

