import subprocess
import pandas as pd
import os
import sys

def run_test(multiplier, symbol, exchange):
    print(f"Running multiplier={multiplier} for {symbol}...")
    cmd = [
        sys.executable, "scripts/backtest.py", 
        symbol, exchange, 
        "--bars", "200", 
        "--multiplier", str(multiplier)
    ]
    subprocess.run(cmd, capture_output=True)
    
    # After backtest, we need to calculate metrics for this run
    # Note: backtest saves to logs/trade_history.csv
    # We should run calculate_metrics and capture the output
    cmd_metrics = [sys.executable, "scripts/calculate_metrics.py"]
    subprocess.run(cmd_metrics, capture_output=True)
    
    # Load data/symbol_performance.csv to get the results
    perf_path = "data/symbol_performance.csv"
    if os.path.exists(perf_path):
        df = pd.read_csv(perf_path)
        # Filter for our symbol
        match = df[df['symbol'] == symbol]
        if not match.empty:
            row = match.iloc[0]
            return {
                'Multiplier': multiplier,
                'Raw%': row['Raw_Prob%'],
                'Elite%': row['Elite_Prob%'],
                'RRR': row['RR_Ratio'],
                'Signals': row['Raw_Count']
            }
    return None

def main():
    multipliers = [1.0, 1.25, 1.5, 2.0]
    # Test on one Thai and one US stock for clear comparison
    targets = [
        ('DOHOME', 'SET'),
        ('NVDA', 'NASDAQ'),
        ('TSMC', 'TWSE')
    ]
    
    all_results = []
    
    for symbol, exchange in targets:
        print(f"\n🔍 Comparing Thresholds for {symbol}")
        print("-" * 30)
        for m in multipliers:
            res = run_test(m, symbol, exchange)
            if res:
                res['Symbol'] = symbol
                all_results.append(res)
                
    if all_results:
        df_final = pd.DataFrame(all_results)
        print("\n\n📊 THRESHOLD SENSITIVITY COMPARISON")
        print("=" * 80)
        print(df_final.to_string(index=False))
        print("=" * 80)
        print("\nInsight: Larger multipliers (e.g. 2.0) act as 'Strict Filters', reducing noise but also signal count.")

if __name__ == "__main__":
    main()
