
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_cache import get_data_with_cache

def run_long_only_test(symbol, exchange, bars=1000):
    tv = TvDatafeed()
    print(f"\n📈 TESTING LONG ONLY STRATEGY: {symbol} ({bars} bars)")
    print("=" * 60)
    
    # 1. Fetch Data
    df = get_data_with_cache(tv, symbol, exchange, Interval.in_daily, 5000)
    if df is None or len(df) < bars:
        print("❌ Insufficient Data")
        return

    # Slice relevant data
    df = df.iloc[-bars:].copy()
    close = df['close']
    pct_change = close.pct_change()
    threshold = 0.006 # US Floor 0.6%
    
    signals = []
    
    for i in range(50, len(df)-1):
        curr_date = df.index[i]
        next_ret = pct_change.iloc[i+1]
        
        # PATTERN MATCHING LOGIC (Simulated)
        # If today CLOSE > OPEN (Green) -> Pattern '+' -> Forecast UP (Long)
        # If today CLOSE < OPEN (Red)   -> Pattern '-' -> Forecast DOWN (Short)
        
        # Note: In real engine, we check dynamic threshold. Here we simulate the raw decision.
        
        # LONG SIGNAL (+)
        if pct_change.iloc[i] > threshold:
             signals.append({'Strategy': 'Long Only', 'Type': 'Long', 'Return': next_ret * 100})
             signals.append({'Strategy': 'Baseline (Long+Short)', 'Type': 'Long', 'Return': next_ret * 100})
             
        # SHORT SIGNAL (-)
        elif pct_change.iloc[i] < -threshold:
             # Baseline takes the short trade
             signals.append({'Strategy': 'Baseline (Long+Short)', 'Type': 'Short', 'Return': -next_ret * 100})
             # Long Only ignores it (0 return)
             signals.append({'Strategy': 'Long Only', 'Type': 'Avoided Short', 'Return': 0.0})

    # 4. Analyze Results
    results_df = pd.DataFrame(signals)
    
    if results_df.empty:
        print("No signals found.")
        return

    # Filter out 'Avoided Short' 0.0 returns from Average calculation to see "Win Rate of Taken Trades"
    # But keep them for Sum to see "Total Portfolio Impact" if needed (though here we just want trade quality)
    
    # Filter out 'Avoided Short' 0.0 returns from analysis
    df = results_df[results_df['Return'] != 0].copy()
    
    # Calculate detailed metrics
    stats = []
    for strategy, group in df.groupby('Strategy'):
        wins = group[group['Return'] > 0]['Return']
        losses = group[group['Return'] <= 0]['Return']
        
        n_wins = len(wins)
        n_losses = len(losses)
        total_trades = n_wins + n_losses
        
        avg_win = wins.mean() if n_wins > 0 else 0
        avg_loss = abs(losses.mean()) if n_losses > 0 else 0
        
        win_rate = (n_wins / total_trades * 100) if total_trades > 0 else 0
        rrr = (avg_win / avg_loss) if avg_loss > 0 else 0
        
        stats.append({
            'Strategy': strategy,
            'Total': total_trades,
            'WinRate%': round(win_rate, 2),
            'AvgWin%': round(avg_win, 2),
            'AvgLoss%': round(avg_loss, 2),
            'RRR': round(rrr, 2),
            'TotalReturn%': round(group['Return'].sum(), 2)
        })
    
    stats_df = pd.DataFrame(stats).set_index('Strategy')
    
    print("\n📊 DETAILED PERFORMANCE METRICS")
    print(stats_df)
    print("-" * 60)

if __name__ == "__main__":
    # Test on Major US Tech
    run_long_only_test('NVDA', 'NASDAQ', 1000)
    run_long_only_test('TSLA', 'NASDAQ', 1000)
    run_long_only_test('AAPL', 'NASDAQ', 1000)
    run_long_only_test('AMZN', 'NASDAQ', 1000)
