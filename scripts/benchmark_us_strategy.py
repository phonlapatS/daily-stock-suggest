"""
US Strategy Benchmark: Fixed 0.6% vs Dynamic Threshold (Inverse Logic)
Tests 10 representative US stocks and generates comparison table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed
from scripts.backtest import backtest_single
import time

def run_benchmark():
    # Top 10 US Tech Stocks (mix of high/medium volatility)
    stocks = [
        'NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT',
        'GOOGL', 'META', 'AMZN', 'NFLX', 'INTC'
    ]
    
    tv = TvDatafeed()
    results = []
    
    print("=" * 80)
    print("US STRATEGY BENCHMARK: Fixed 0.6% vs Dynamic (Inverse Logic)")
    print("=" * 80)
    print(f"Testing {len(stocks)} stocks with 500 bars each...\n")
    
    for i, symbol in enumerate(stocks, 1):
        print(f"[{i}/{len(stocks)}] Processing {symbol}...", end=" ", flush=True)
        
        # Test Fixed 0.6%
        try:
            res_fixed = backtest_single(tv, symbol, 'NASDAQ', n_bars=500, 
                                       fixed_threshold=0.6, inverse_logic=True, verbose=False)
            time.sleep(1)
        except:
            res_fixed = None
            
        # Test Dynamic
        try:
            res_dynamic = backtest_single(tv, symbol, 'NASDAQ', n_bars=500, 
                                         fixed_threshold=None, inverse_logic=True, verbose=False)
            time.sleep(1)
        except:
            res_dynamic = None
        
        if res_fixed and res_dynamic:
            results.append({
                'symbol': symbol,
                'fixed_acc': res_fixed['accuracy'],
                'fixed_win': res_fixed['avg_win'],
                'fixed_loss': res_fixed['avg_loss'],
                'fixed_rrr': res_fixed['risk_reward'],
                'fixed_trades': res_fixed['total'],
                'dyn_acc': res_dynamic['accuracy'],
                'dyn_win': res_dynamic['avg_win'],
                'dyn_loss': res_dynamic['avg_loss'],
                'dyn_rrr': res_dynamic['risk_reward'],
                'dyn_trades': res_dynamic['total']
            })
            print("✅")
        else:
            print("❌ (Data Error)")
    
    # Print Summary Table
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n{'Stock':<8} | {'Strategy':<12} | {'Acc%':<6} | {'AvgWin%':<8} | {'AvgLoss%':<8} | {'RRR':<6} | {'Trades':<6}")
    print("-" * 80)
    
    for r in results:
        # Fixed row
        print(f"{r['symbol']:<8} | Fixed 0.6%   | {r['fixed_acc']:<6.1f} | {r['fixed_win']:<8.2f} | {r['fixed_loss']:<8.2f} | {r['fixed_rrr']:<6.2f} | {r['fixed_trades']:<6}")
        # Dynamic row
        diff = r['dyn_acc'] - r['fixed_acc']
        marker = "✅" if diff > 0 else "❌"
        print(f"{'':8} | Dynamic      | {r['dyn_acc']:<6.1f} | {r['dyn_win']:<8.2f} | {r['dyn_loss']:<8.2f} | {r['dyn_rrr']:<6.2f} | {r['dyn_trades']:<6} {marker}")
        print("-" * 80)
    
    # Calculate Averages
    if results:
        avg_fixed_acc = sum(r['fixed_acc'] for r in results) / len(results)
        avg_dyn_acc = sum(r['dyn_acc'] for r in results) / len(results)
        avg_fixed_rrr = sum(r['fixed_rrr'] for r in results) / len(results)
        avg_dyn_rrr = sum(r['dyn_rrr'] for r in results) / len(results)
        
        print(f"\n{'AVERAGE':<8} | Fixed 0.6%   | {avg_fixed_acc:<6.1f} | {'':8} | {'':8} | {avg_fixed_rrr:<6.2f} |")
        print(f"{'':8} | Dynamic      | {avg_dyn_acc:<6.1f} | {'':8} | {'':8} | {avg_dyn_rrr:<6.2f} |")
        
        print("\n" + "=" * 80)
        print("CONCLUSION")
        print("=" * 80)
        improvement = avg_dyn_acc - avg_fixed_acc
        winner = "Dynamic" if improvement > 0 else "Fixed 0.6%"
        print(f"Winner: {winner} (+{abs(improvement):.1f}% average accuracy)")
        print(f"Dynamic wins in: {sum(1 for r in results if r['dyn_acc'] > r['fixed_acc'])}/{len(results)} stocks")
        print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
