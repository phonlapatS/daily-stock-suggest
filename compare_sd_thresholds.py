
import sys
import os
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from scripts.backtest import backtest_single

# Override print to suppress output during test
class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def run_comparison():
    print("\n⚔️ COMPARISON: Fixed 0.6% vs Dynamic (1.25SD) on NVDA ⚔️")
    print("=" * 60)
    
    tv = TvDatafeed()
    symbol = 'NVDA'
    exchange = 'NASDAQ'
    bars = 500
    
    # 1. Test Fixed 0.6% (Inverse)
    print(f"Running Fixed 0.6% (Inverse)...", end=" ")
    try:
        with SuppressPrint():
            res_fixed = backtest_single(tv, symbol, exchange, n_bars=bars, fixed_threshold=0.6, inverse_logic=True, verbose=False)
        print("✅ Done")
    except Exception as e:
        print(f"❌ Error: {e}")
        res_fixed = None

    # 2. Test Dynamic (Inverse)
    print(f"Running Dynamic 1.25SD (Inverse)...", end=" ")
    try:
        with SuppressPrint():
            res_dynamic = backtest_single(tv, symbol, exchange, n_bars=bars, fixed_threshold=None, inverse_logic=True, verbose=False)
        print("✅ Done")
    except Exception as e:
        print(f"❌ Error: {e}")
        res_dynamic = None

    # Print Comparison Table
    print("\n📊 RESULTS (NVDA - Last 500 Bars)")
    print("-" * 60)
    print(f"{'Metric':<20} | {'Fixed (0.6%)':<15} | {'Dynamic (1.25SD)':<15}")
    print("-" * 60)
    
    if res_fixed:
        acc_fixed = f"{res_fixed['accuracy']:.1f}%"
        count_fixed = res_fixed['total']
        win_fixed = res_fixed['correct']
    else:
        acc_fixed = "N/A"
    
    if res_dynamic:
        acc_dynamic = f"{res_dynamic['accuracy']:.1f}%"
        count_dynamic = res_dynamic['total']
        win_dynamic = res_dynamic['correct']
    else:
        acc_dynamic = "N/A"
        
    print(f"{'Accuracy':<20} | {acc_fixed:<15} | {acc_dynamic:<15}")
    print(f"{'Total Trades':<20} | {count_fixed:<15} | {count_dynamic:<15}")
    print(f"{'Correct Picks':<20} | {win_fixed:<15} | {win_dynamic:<15}")
    print("-" * 60)
    
    # Conclusion
    print("\n💡 Analysis:")
    if res_fixed and res_dynamic:
        diff = res_dynamic['accuracy'] - res_fixed['accuracy']
        if diff > 0:
            print(f"Dynamic outperformed Fixed by +{diff:.1f}% points.")
            print("Why? 0.6% is too small for NVDA (High Volatility). It captures noise.")
            print("Dynamic adapts to ~2-3% daily moves, filtering only significant patterns.")
        else:
            print(f"Fixed outperformed Dynamic by +{abs(diff):.1f}% points.")

if __name__ == "__main__":
    run_comparison()
