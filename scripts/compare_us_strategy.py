
import sys
import os
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.backtest import backtest_single

class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def run_comparison():
    print("# US Market Strategy Comparison (Inverse Logic)")
    print("> Date: 2026-02-10 | Benchmark: 500 Bars (Daily)\n")
    
    target_stocks = ['NVDA', 'TSLA']
    
    tv = TvDatafeed()
    exchange = 'NASDAQ'
    n_bars = 500
    
    data = []
    
    print(f"| {'Stock':<6} | {'Mode':<10} | {'Acc%':<6} | {'AvgWin%':<8} | {'AvgLoss%':<8} | {'RRR':<5} | {'Trades':<6} |")
    print(f"| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    
    import time
    
    for symbol in target_stocks:
        # Run Fixed
        print(f"\nProcessing {symbol} (Fixed)...")
        time.sleep(2)
        try:
            # Removed SuppressPrint to see errors
            res_fixed = backtest_single(tv, symbol, exchange, n_bars=n_bars, fixed_threshold=0.6, inverse_logic=True, verbose=False)
            
            if res_fixed:
                acc_f = res_fixed['accuracy']
                win_f = res_fixed['avg_win']
                loss_f = res_fixed['avg_loss']
                rrr_f = res_fixed['risk_reward']
                cnt_f = res_fixed['total']
            else:
                acc_f, win_f, loss_f, rrr_f, cnt_f = 0, 0, 0, 0, 0
        except Exception as e:
            print(f"Error: {e}")
            acc_f, win_f, loss_f, rrr_f, cnt_f = 0, 0, 0, 0, 0
            
        # Run Dynamic
        print(f"Processing {symbol} (Dynamic)...")
        time.sleep(2)
        try:
            # Removed SuppressPrint
            res_dyn = backtest_single(tv, symbol, exchange, n_bars=n_bars, fixed_threshold=None, inverse_logic=True, verbose=False)
            
            if res_dyn:
                acc_d = res_dyn['accuracy']
                win_d = res_dyn['avg_win']
                loss_d = res_dyn['avg_loss']
                rrr_d = res_dyn['risk_reward']
                cnt_d = res_dyn['total']
            else:
                acc_d, win_d, loss_d, rrr_d, cnt_d = 0, 0, 0, 0, 0
        except:
            acc_d, win_d, loss_d, rrr_d, cnt_d = 0, 0, 0, 0, 0
            
        # Print Rows
        print(f"| **{symbol}** | Fixed 0.6% | {acc_f:.1f}% | {win_f:.2f}% | {loss_f:.2f}% | {rrr_f:.2f} | {cnt_f} |")
        print(f"|        | **Dynamic** | **{acc_d:.1f}%** | **{win_d:.2f}%** | **{loss_d:.2f}%** | **{rrr_d:.2f}** | **{cnt_d}** |")
        print("|---|---|---|---|---|---|---|")

    print("\n### Summary Analysis")
    print("- **Comparision:** Dynamic vs Fixed 0.6% (Inverse Logic)")
    print("- **Goal:** Higher Accuracy and Better Risk/Reward (RRR)")

if __name__ == "__main__":
    run_comparison()
