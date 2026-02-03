
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Mocking config for standalone run
VOLATILITY_WINDOW = 20

def debug_amata():
    print("🔬 DEBUGGING AMATA PATTERN")
    print("=" * 50)
    
    try:
        tv = TvDatafeed()
        df = tv.get_hist(symbol='AMATA', exchange='SET', interval=Interval.in_daily, n_bars=100)
        
        if df is None:
            with open("debug_amata_out.txt", "w") as f:
                f.write("❌ Fetch failed: tv.get_hist returned None\n")
            return

        # 1. Calculate Thresholds (Exact Logic)
        close = df['close']
        pct_change = close.pct_change()
        
        short_std = pct_change.rolling(window=VOLATILITY_WINDOW).std()
        long_std = pct_change.rolling(window=252).std()
        long_term_floor = long_std * 0.50
        effective_std = np.maximum(short_std, long_term_floor.fillna(0))
        effective_std = effective_std.fillna(short_term_std)
        threshold_series = effective_std * 1.25
        
        # Write to file
        with open("debug_amata_out.txt", "w") as f:
            f.write(f"Last 10 Days Data (AMATA):\n")
            f.write(f"{'Date':<12} {'Close':<10} {'Change(%)':<12} {'Threshold(%)':<12} {'Signal'}\n")
            f.write("-" * 65 + "\n")
            
            last_indices = range(len(df)-10, len(df))
            current_pattern_str = ""
            
            for i in last_indices:
                date_str = df.index[i].strftime('%Y-%m-%d')
                c = close.iloc[i]
                chg = pct_change.iloc[i]
                thresh = threshold_series.iloc[i]
                
                sig = "."
                if pd.isna(chg) or pd.isna(thresh):
                    sig = "NaN"
                elif chg > thresh:
                    sig = "+"
                elif chg < -thresh:
                    sig = "-"
                
                # Save for pattern reconstruction (Last 4 days)
                if i >= len(df) - 4:
                    if sig in ['+', '-']:
                        current_pattern_str += sig
                
                f.write(f"{date_str:<12} {c:<10.2f} {chg*100:>+9.2f}%   {thresh*100:>9.2f}%    {sig}\n")

            f.write("-" * 65 + "\n")
            f.write(f"Calculated Pattern (from last 4 windows): '{current_pattern_str}'\n")
        
        # Check specific hypothesis
        # User saw '---'
        # Check if the last 4 days produced '---'
        
    except Exception as e:
        with open("debug_amata_out.txt", "a") as f:
            f.write(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    debug_amata()
