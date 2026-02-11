
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_cache import get_data_with_cache
from core.indicators import calculate_adx, calculate_volume_adv

def run_strategy_comparison(symbol, exchange, bars=1000):
    tv = TvDatafeed()
    print(f"\n📉 COMPARING SHORT STRATEGIES: {symbol} ({bars} bars)")
    print("=" * 60)
    
    # 1. Fetch Data
    df = get_data_with_cache(tv, symbol, exchange, Interval.in_daily, 5000)
    if df is None or len(df) < bars:
        print("❌ Insufficient Data")
        return

    # Slice relevant data
    df = df.iloc[-bars:].copy()
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    # 2. Indicators
    adx = calculate_adx(high, low, close)
    vol_avg = calculate_volume_adv(volume)
    sma50 = close.rolling(50).mean()
    
    # 3. Pattern Recognition (simplified for script)
    # Using simple returns for "Short Signal" simulation
    pct_change = close.pct_change()
    threshold = 0.006 # US Floor 0.6%
    
    signals = []
    
    # Debug Counters
    debug_counts = {'Pattern(-)': 0, 'BreakLow': 0, 'VolSpike': 0, 'ADX_Strict': 0, 'BelowSMA50': 0}

    for i in range(50, len(df)-1):
        # Current Context
        curr_date = df.index[i]
        curr_close = close.iloc[i]
        prev_close = close.iloc[i-1]
        prev_low = low.iloc[i-1]
        curr_vol = volume.iloc[i]
        curr_vol_avg = vol_avg.iloc[i]
        curr_adx = adx.iloc[i]
        curr_sma = sma50.iloc[i]
        
        next_ret = pct_change.iloc[i+1]
        
        if pct_change.iloc[i] < -threshold:
            debug_counts['Pattern(-)'] += 1
            
            # --- STRATEGY A: BASELINE ---
            signals.append({'Strategy': 'Baseline', 'Return': -next_ret * 100})
            
            # Filter Checks
            is_break_low = curr_close < prev_low
            is_vol_strict = curr_vol > (curr_vol_avg * 1.5)
            is_adx_strict = curr_adx > 40
            is_below_sma = curr_close < curr_sma
            
            if is_break_low: debug_counts['BreakLow'] += 1
            if is_vol_strict: debug_counts['VolSpike'] += 1
            if is_adx_strict: debug_counts['ADX_Strict'] += 1
            if is_below_sma: debug_counts['BelowSMA50'] += 1
            
            # --- STRATEGY B: STRICT (Crash Hunter) ---
            if is_break_low and is_vol_strict and is_adx_strict:
                 signals.append({'Strategy': 'Strict (Crash)', 'Return': -next_ret * 100})

            # --- STRATEGY D: REGIME FILTER (Smart Short) ---
            # Logic: Only Short if market is already technically weak (Below SMA50) AND Break Low
            if is_below_sma and is_break_low:
                 signals.append({'Strategy': 'Regime (Below SMA50)', 'Return': -next_ret * 100})

    print(f"Debug: {debug_counts}")

    # 4. Analyze Results
    results_df = pd.DataFrame(signals)
    
    if results_df.empty:
        print("No signals found.")
        return

    summary = results_df.groupby('Strategy')['Return'].agg(['count', 'mean', 'sum', 'min', 'max'])
    # Calculate Win Rate
    def win_rate(x):
        return (x > 0).sum() / len(x) * 100
    
    win_rates = results_df.groupby('Strategy')['Return'].apply(win_rate)
    summary['WinRate%'] = win_rates
    
    print("\n📊 PERFORMANCE COMPARISON")
    print(summary[['count', 'WinRate%', 'mean', 'sum']])
    print("-" * 60)
    print("Interpretation:")
    print("Baseline: Represents current 'Short everything that looks red' logic.")
    print("Strict: Represents proposed 'Only Short if Panic detected' logic.")

if __name__ == "__main__":
    # Test on Volatile US Tech Stocks (Good for crash testing)
    run_strategy_comparison('NVDA', 'NASDAQ', 1000)
    run_strategy_comparison('TSLA', 'NASDAQ', 1000)
    run_strategy_comparison('QQQ', 'NASDAQ', 1000)
