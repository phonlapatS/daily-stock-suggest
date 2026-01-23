
import pandas as pd
import numpy as np
import time
from tvDatafeed import TvDatafeed, Interval

# reuse logic from batch_processor
def calculate_qs_threshold(series, window=20, std_dev_multiplier=1.25):
    pct_change = series.pct_change()
    rolling_std = pct_change.rolling(window=window).std()
    long_term_std = pct_change.rolling(window=252).std().fillna(method='bfill')
    
    # Hybrid volatility
    effective_std = np.maximum(rolling_std, long_term_std * 0.5)
    effective_std = effective_std.fillna(method='bfill')
    
    current_std = effective_std.iloc[-1]
    threshold = current_std * std_dev_multiplier
    return threshold, pct_change

def scan_pattern_strict(pct_change, threshold):
    # Strict Logic: FLAT (within threshold) breaks the streak
    
    # Convert to signals: 1 (UP), -1 (DOWN), 0 (FLAT)
    signals = np.zeros(len(pct_change))
    signals[pct_change > threshold] = 1
    signals[pct_change < -threshold] = -1
    
    # Find current streak
    # Walk backwards from the last closed bar (iloc[-2] since iloc[-1] is current forming bar? 
    # Actually for intraday, iloc[-1] is the latest bar. If it's forming, we might want to check it.
    # But usually pattern prediction is based on *completed* bars.
    # Let's use the last COMPLETED bar for pattern detection.
    # But wait, the user wants "Current Status". If the current bar is forming, it's not a pattern yet.
    # Let's use the sequence ending at iloc[-2] as "Recent Pattern" for prediction of iloc[-1] (current bar?).
    # Or prediction for the NEXT bar (iloc[-1] + 1)?
    
    # PREDICTPLUS LOGIC:
    # Pattern is detected from historical bars.
    # Predicts the NEXT bar.
    
    # For Intraday:
    # If 15m candle closes at 10:00. We analyze pattern ending 10:00. We predict 10:15 bar.
    # So we should look at signals up to the last *completed* bar.
    
    # Let's assume the fetched data includes the latest bar. 
    # TvDatafeed usually returns incomplete current bar unless specified?
    # Let's use all data and treat the last row as the "latest known state".
    
    # Find streak ending at index -1
    current_signal = signals[-1]
    if current_signal == 0:
        return "FLAT", signals
        
    streak_len = 0
    pattern_sign = current_signal
    
    for i in range(len(signals)-1, -1, -1):
        if signals[i] == pattern_sign:
            streak_len += 1
        else:
            break
            
    pattern_str = ("+" if pattern_sign == 1 else "-") * streak_len
    return pattern_str, signals

def calculate_stats(signals, pattern_str):
    # Find all occurrences of this pattern in history (strict)
    # Pattern: "++" means signal sequence [1, 1]
    
    target_seq = []
    for char in pattern_str:
        if char == '+': target_seq.append(1)
        else: target_seq.append(-1)
        
    pat_len = len(target_seq)
    n = len(signals)
    
    occurrences = [] # indices where pattern ends
    
    # Simple sliding window
    for i in range(pat_len, n-1): # n-1 because we need target (next bar)
        window = signals[i-pat_len+1 : i+1]
        
        # Check match
        match = True
        for j in range(pat_len):
            if window[j] != target_seq[j]:
                match = False
                break
        
        if match:
             occurrences.append(i)
             
    # Calculate stats for next bar (i+1)
    up_count = 0
    down_count = 0
    
    next_day_returns = [] # We don't have pct_change here easily passed, skip Avg_Ret for now for speed
    
    for idx in occurrences:
        if idx+1 >= n: continue
        
        outcome = signals[idx+1]
        if outcome == 1: up_count += 1
        elif outcome == -1: down_count += 1
        
    # Prob Logic V3.1: Dominant / (Up + Down)
    decisive_total = up_count + down_count
    
    if decisive_total == 0:
        return "N/A", 0, "0/0"
        
    if up_count >= down_count:
        chance = "🟢 UP"
        prob = (up_count / decisive_total) * 100
        stats = f"{up_count}/{decisive_total} ({len(occurrences)})"
    else:
        chance = "🔴 DOWN"
        prob = (down_count / decisive_total) * 100
        stats = f"{down_count}/{decisive_total} ({len(occurrences)})"
        
    return chance, prob, stats

def analyze_symbol(tv, symbol, exchange, interval_name, interval_obj):
    print(f"\n🔍 Analyzing {symbol} ({interval_name})...")
    
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval_obj, n_bars=5000)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    if df is None or df.empty:
        print("No data found.")
        return

    # 1. Calc Threshold
    threshold, pct_change = calculate_qs_threshold(df['close'], std_dev_multiplier=1.25)
    
    # 2. Scan Current Pattern
    pattern_str, signals = scan_pattern_strict(pct_change, threshold)
    
    print(f"   Threshold: ±{threshold*100:.2f}%")
    print(f"   Current Pattern: {pattern_str}")
    
    if pattern_str == "FLAT":
        print("   Status: Market is FLAT (no clear trend)")
        return

    # 3. Stats
    chance, prob, stats = calculate_stats(signals, pattern_str)
    
    print(f"   Chance: {chance}")
    print(f"   Prob:   {prob:.1f}%")
    print(f"   Stats:  {stats}")


def main():
    tv = TvDatafeed()
    
    # Gold
    analyze_symbol(tv, 'XAUUSD', 'OANDA', '15 Min', Interval.in_15_minute)
    analyze_symbol(tv, 'XAUUSD', 'OANDA', '30 Min', Interval.in_30_minute)
    
    # Silver
    analyze_symbol(tv, 'XAGUSD', 'OANDA', '15 Min', Interval.in_15_minute)
    analyze_symbol(tv, 'XAGUSD', 'OANDA', '30 Min', Interval.in_30_minute)

if __name__ == "__main__":
    main()
