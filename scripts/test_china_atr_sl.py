#!/usr/bin/env python
"""
Test China Market with ATR-based Stop Loss
ทดสอบการใช้ ATR-based SL แทน fixed SL เพื่อให้ AvgLoss% ยืดหยุ่นขึ้น
"""

import sys
import os
import subprocess
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_backtest(atr_sl_mult, atr_tp_mult, n_bars=2000):
    """
    Run backtest with ATR-based SL/TP
    
    Args:
        atr_sl_mult: ATR multiplier for SL (e.g., 1.0, 1.5, 2.0)
        atr_tp_mult: ATR multiplier for TP (e.g., 3.0, 4.0, 5.0)
        n_bars: Number of test bars
    """
    print(f"\n{'='*100}")
    print(f"Testing: ATR SL = {atr_sl_mult}x, ATR TP = {atr_tp_mult}x")
    print(f"{'='*100}")
    
    # Modify backtest.py temporarily to use ATR for China
    backtest_file = os.path.join('scripts', 'backtest.py')
    
    # Read current file
    with open(backtest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find China RM section and modify to use ATR
    # We need to change:
    # - RM_USE_ATR = False → True
    # - RM_ATR_SL = None → atr_sl_mult
    # - RM_ATR_TP = None → atr_tp_mult
    
    import re
    
    # Pattern to find China RM section
    pattern = r"(elif is_china_market:.*?RM_TRAIL_DISTANCE = kwargs\.get\('trail_distance', 40\.0\)  # V13\.4: Keep at 40% \(let profits run\))"
    
    replacement = f"""elif is_china_market:
        # ========================================================================
        # CHINA MARKET RISK MANAGEMENT - ATR-based (Dynamic)
        # ========================================================================
        # China/HK V13.5: ATR-based SL/TP for flexibility
        # - ATR SL: {atr_sl_mult}x (dynamic based on volatility)
        # - ATR TP: {atr_tp_mult}x (dynamic based on volatility)
        # - Max Hold: 3 days (based on actual hold period)
        # - Early trailing (1.0%) to lock profits quickly
        # - Target: RRR > 1.2, AvgWin% > AvgLoss%, Count > 50, Stability Score > 60
        # ========================================================================
        RM_STOP_LOSS = None  # Use ATR instead
        RM_TAKE_PROFIT = None  # Use ATR instead
        RM_MAX_HOLD = kwargs.get('max_hold', 3)           # V13.4: Keep at 3 days
        RM_ATR_SL = {atr_sl_mult}  # ATR multiplier for SL
        RM_ATR_TP = {atr_tp_mult}  # ATR multiplier for TP
        RM_USE_ATR = True  # Enable ATR-based SL/TP
        RM_USE_TRAILING = True
        RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 1.0)   # V13.4: Keep at 1.0% (activate early)
        RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)  # V13.4: Keep at 40% (let profits run)"""
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Backup original
    backup_file = backtest_file + '.bak'
    if not os.path.exists(backup_file):
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Write modified file
    with open(backtest_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    try:
        # Run backtest
        cmd = [
            'python', 'scripts/backtest.py',
            '--full',
            '--bars', str(n_bars),
            '--group', 'CHINA',
            '--fast'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
            print(f"❌ Backtest failed: {result.stderr}")
            return None
        
        # Calculate metrics
        cmd_metrics = ['python', 'scripts/calculate_metrics.py']
        subprocess.run(cmd_metrics, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        # Read results
        perf_file = 'data/symbol_performance.csv'
        if os.path.exists(perf_file):
            df = pd.read_csv(perf_file)
            china = df[df['Country'] == 'CN']
            passing = china[
                (china['Prob%'] >= 53.0) & 
                (china['RR_Ratio'] >= 1.0) & 
                (china['Count'] >= 15)
            ]
            
            if len(passing) > 0:
                avg_loss = passing['AvgLoss%'].mean()
                avg_win = passing['AvgWin%'].mean()
                rrr = passing['RR_Ratio'].mean()
                count = passing['Count'].mean()
                min_count = passing['Count'].min()
                
                return {
                    'atr_sl_mult': atr_sl_mult,
                    'atr_tp_mult': atr_tp_mult,
                    'stocks_passing': len(passing),
                    'avg_loss': avg_loss,
                    'avg_win': avg_win,
                    'rrr': rrr,
                    'count': count,
                    'min_count': min_count
                }
        
        return None
        
    finally:
        # Restore original file
        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(backtest_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            os.remove(backup_file)

def main():
    print("="*100)
    print("China Market - ATR-based SL/TP Testing")
    print("="*100)
    print("\nเป้าหมาย: ทดสอบ ATR-based SL/TP เพื่อให้ AvgLoss% ยืดหยุ่นขึ้น")
    print("(แทน fixed SL 1.0% ที่ lock AvgLoss% ไว้ที่ ~1.0%)")
    print("")
    
    # Test combinations
    test_cases = [
        # (ATR SL mult, ATR TP mult)
        (1.0, 4.0),  # Similar to current (1.0% SL, 4.0% TP)
        (1.5, 6.0),  # Wider SL/TP
        (2.0, 8.0),  # Even wider
        (0.8, 3.2),  # Tighter SL/TP
    ]
    
    results = []
    
    for atr_sl, atr_tp in test_cases:
        result = run_backtest(atr_sl, atr_tp, n_bars=2000)
        if result:
            results.append(result)
            print(f"\n✅ Result:")
            print(f"   ATR SL: {atr_sl}x, ATR TP: {atr_tp}x")
            print(f"   Stocks Passing: {result['stocks_passing']}")
            print(f"   AvgLoss%: {result['avg_loss']:.2f}%")
            print(f"   AvgWin%: {result['avg_win']:.2f}%")
            print(f"   RRR: {result['rrr']:.2f}")
            print(f"   Count: {result['count']:.1f} (Min: {result['min_count']})")
    
    # Summary
    if results:
        print("\n" + "="*100)
        print("Summary Comparison")
        print("="*100)
        print(f"{'ATR SL':<10} {'ATR TP':<10} {'Stocks':<10} {'AvgLoss%':<12} {'AvgWin%':<12} {'RRR':<10} {'Count':<10}")
        print("-"*100)
        for r in results:
            print(f"{r['atr_sl_mult']:<10.1f} {r['atr_tp_mult']:<10.1f} {r['stocks_passing']:<10} {r['avg_loss']:<12.2f} {r['avg_win']:<12.2f} {r['rrr']:<10.2f} {r['count']:<10.1f}")
        print("="*100)
        
        # Find best option
        best = max(results, key=lambda x: x['rrr'] * (1 if x['stocks_passing'] >= 2 else 0.5))
        print(f"\n🏆 Best Option: ATR SL {best['atr_sl_mult']}x, ATR TP {best['atr_tp_mult']}x")
        print(f"   AvgLoss%: {best['avg_loss']:.2f}% (ยืดหยุ่นขึ้นจาก fixed 1.0%)")
        print(f"   RRR: {best['rrr']:.2f}")
        print(f"   Stocks Passing: {best['stocks_passing']}")

if __name__ == '__main__':
    main()

