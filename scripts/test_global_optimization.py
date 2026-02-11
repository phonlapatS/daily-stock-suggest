
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.backtest import backtest_single

def calculate_sma(df, window=50):
    return df['close'].rolling(window=window).mean()

def test_optimization(symbol, exchange, n_bars=1000):
    print(f"\n🔬 OPTIMIZATION TEST: {symbol} ({exchange})")
    print("="*60)
    
    tv = TvDatafeed()
    
    # 1. Baseline Run (Current Logic)
    print("1️⃣ Baseline (Current Logic)")
    res_base = backtest_single(tv, symbol, exchange, n_bars=n_bars, verbose=False)
    acc_base = res_base['accuracy'] if res_base else 0
    print(f"   Accuracy: {acc_base}%")
    
    if not res_base or 'detailed_predictions' not in res_base:
        print("   ❌ No data or predictions")
        return

    # Extract Trade Data for detailed analysis
    trades = pd.DataFrame(res_base['detailed_predictions'])
    
    # Needs historical data to calculate proper SMA
    # We will simulate SMA effect by checking price relative to an approximation or re-fetching
    # Ideally, we should modify backtest logic, but here we can try to filter the LOGS if we have price data.
    # Current logs don't have historical price series, so we need to fetch data.
    
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars+200)
    if df is None: return
    
    df['sma50'] = calculate_sma(df, 50)
    df['trend'] = np.where(df['close'] > df['sma50'], 'UP', 'DOWN')
    
    # Merge trend data into trades based on date
    trades['date'] = pd.to_datetime(trades['date'])
    df.index = pd.to_datetime(df.index)
    
    # 2. Trend Filter Test (SMA50)
    print("\n2️⃣ Trend Filter (SMA50)")
    # Logic: Only take LONG if Trend UP, SHORT if Trend DOWN
    
    filtered_trades = []
    
    for _, t in trades.iterrows():
        trade_date = t['date']
        # Find price on trade date (or previous day if signal generated then)
        # Assuming trade date is the 'Signal Date'
        if trade_date not in df.index: continue
        
        trend = df.loc[trade_date]['trend']
        
        # Filter condition
        if t['forecast'] == trend:
            filtered_trades.append(t)
            
    if filtered_trades:
        df_filt = pd.DataFrame(filtered_trades)
        correct = df_filt['correct'].sum()
        total = int(df_filt.shape[0])
        acc_filt = (correct/total)*100
        print(f"   Filtered Count: {total} (Original: {len(trades)})")
        print(f"   Accuracy: {acc_filt:.1f}% (Diff: {acc_filt - float(str(acc_base).strip('%')):.1f}%)")
    else:
        print("   ❌ No trades matched trend filter")

    # 3. Inverse Logic Test
    print("\n3️⃣ Inverse Logic (Contrarian)")
    # What if we did the opposite?
    # Correct becomes Incorrect, Incorrect becomes Correct (roughly, assuming binary outcome)
    # Actually, if Forecast UP -> Actual DOWN (Loss). Inverse: Forecast DOWN -> Actual DOWN (Win).
    inverse_correct = len(trades) - res_base['correct']
    acc_inv = (inverse_correct / len(trades)) * 100
    print(f"   Accuracy: {acc_inv:.1f}%")
    
    # 4. Pattern Length Hypothesis (Requires logic change, skipping in this quick check)
    # But we can infer: if Baseline is random, and Trend Filter improves it, then it's a Regime issue.

if __name__ == "__main__":
    # Test Candidates
    targets = [
        ('NVDA', 'NASDAQ'),
        ('TSMC', 'TWSE'),
        ('BABA', 'NYSE')
    ]
    
    for sym, ex in targets:
        test_optimization(sym, ex, n_bars=1000)
