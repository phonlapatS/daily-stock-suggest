#!/usr/bin/env python3
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Configure paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from core.data_cache import get_data_with_cache
from processor import analyze_asset

def print_header(text):
    print("\n" + "=" * 80)
    print(f"📄 {text}")
    print("=" * 80)

def view_report(symbol):
    print(f"🚀 Generating Deep Dive Report for: {symbol} ...")
    
    # 1. Find Asset Config
    asset_info = None
    for group in config.ASSET_GROUPS.values():
        for asset in group['assets']:
            if asset['symbol'] == symbol:
                asset_info = asset
                break
        if asset_info: break
    
    if not asset_info:
        # Fallback for manual symbol
        print(f"⚠️ Symbol {symbol} not found in config. Using defaults (SET).")
        asset_info = {'symbol': symbol, 'exchange': 'SET'}
        interval = Interval.in_daily
    else:
        # Find interval from group
        for group in config.ASSET_GROUPS.values():
            if asset_info in group['assets']:
                interval = group['interval']
                break

    # 2. Fetch Data
    tv = TvDatafeed()
    df = get_data_with_cache(tv, asset_info['symbol'], asset_info['exchange'], interval, 5000, 50)
    
    if df is None or df.empty:
        print("❌ Error: No data found.")
        return

    # 3. Analyze Patterns
    # We use processor.py to get the BEST pattern
    results = analyze_asset(df, symbol=symbol)
    
    if not results:
        print("❌ No clear pattern found (Noise/Flat).")
        # Debug: Check volatility
        close = df['close']
        change = close.pct_change().iloc[-1] * 100
        
        # Recalculate threshold to see why it failed
        pct_change = close.pct_change()
        short_term_std = pct_change.rolling(window=20).std()
        long_term_std = pct_change.rolling(window=252).std()
        long_term_floor = long_term_std * 0.50
        effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
        threshold = effective_std.iloc[-1] * 1.25 * 100
        
        print(f"   Last Change: {change:.2f}%")
        print(f"   Threshold:   ±{threshold:.2f}% (Price change must exceed this)")
        return

    # 4. Display Report
    # Sort results by probability first, then matches
    results.sort(key=lambda x: (x['prob'], x['matches_found']), reverse=True)
    
    print_header(f"PART 1: MASTER PATTERN STATS (Tomorrow's Forecast) - {symbol}")
    print(f"Price: {df['close'].iloc[-1]:.2f}  |  Threshold: ±{results[0].get('threshold', 0):.2f}%")
    print("-" * 100)
    print(f"{'Pattern':<10} {'Category':<10} {'Chance':<10} {'Prob%':>8} {'Stats':>18} {'Exp.Move':>12}")
    print("-" * 100)
    
    for res in results:
        # Format Data
        pattern_str = res['pattern']
        category = "Cont." if pattern_str[-1] == pattern_str[-2] else "Rev."
        
        direction = "🟢 UP" if res['forecast'] == "UP" else "🔴 DOWN"
        prob_str = f"{res['prob']:.1f}%"
        
        # Stats: Win/TotalMatches (TotalBars)
        total_hist = 5000 # hardcoded or from config
        stats_str = f"{res.get('win_count', int(res['matches_found'] * res['prob']/100))}/{res['matches_found']} ({total_hist})"
        
        # Exp Move
        avg_ret = res['avg_win'] if res['forecast'] == "UP" else -res['avg_loss']
        exp_move = f"{avg_ret:+.2f}%"
        
        print(f"{pattern_str:<10} {category:<10} {direction:<10} {prob_str:>8} {stats_str:>18} {exp_move:>12}")

    print("-" * 100)
    
    # 5. Streak Profile (Simplified for V3.4)
    print_header("PART 2: STREAK PROFILE (Momentum)")
    # Calculate current streak
    closes = df['close'].values
    streak_type = "UP" if closes[-1] > closes[-2] else "DOWN"
    streak_len = 0
    for i in range(len(closes)-1, 0, -1):
        if (closes[i] > closes[i-1] and streak_type == "UP") or \
           (closes[i] < closes[i-1] and streak_type == "DOWN"):
            streak_len += 1
        else:
            break
            
    print(f"Current Streak: {streak_type} x {streak_len} Days")
    print("(Note: Full historical streak stats integration coming in V3.5)")

def view_all_report():
    file_path = 'data/pattern_results.csv'
    if not os.path.exists(file_path):
        print("❌ No daily report data found. Please run 'python3 main.py' first.")
        return

    df = pd.read_csv(file_path)
    if df.empty:
        print("❌ No patterns found in the latest run.")
        return

    # Sort by Probability (High -> Low), then Matches
    # Use 'bull_prob' or 'bear_prob' depending on direction, but simpler to use max prob or existing sort column if any
    # Let's create a 'display_prob' for sorting
    df['display_prob'] = df[['bull_prob', 'bear_prob']].max(axis=1)
    df = df.sort_values(by=['display_prob', 'matches'], ascending=[False, False])

    print_header("DAILY PATTERN REPORT (ALL SYMBOLS)")
    print(f"{'Symbol':<10} {'Price':>10} {'Chg%':>10} {'Threshold':>12} {'Pattern':^10} {'Chance':<10} {'Prob%':>7} {'Stats':>18} {'Exp.Move':>10}")
    print("-" * 110)

    for _, row in df.iterrows():
        # Prepare Data
        sym = row['symbol']
        price = row['price']
        chg = row['change_pct']
        thresh = row['threshold']
        pattern = row['pattern_display']
        
        # Forecast Logic
        if row['avg_return'] > 0:
            direction = "🟢 UP"
            prob = row['bull_prob']
            win = int(row['matches'] * prob / 100)
        else:
            direction = "🔴 DOWN"
            prob = row['bear_prob']
            win = int(row['matches'] * prob / 100)
            
        stats = f"{win}/{int(row['matches'])} ({int(row.get('total_bars', 5000))})"
        exp_move = f"{row['avg_return']:+.2f}%"

        print(f"{sym:<10} {price:>10.2f} {chg:>9.2f}% {thresh:>11.2f}% {pattern:^10} {direction:<10} {prob:>6.0f}% {stats:>18} {exp_move:>10}")
    
    print("-" * 110)
    print(f"Total: {len(df)} symbols")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].upper() == 'ALL':
        view_all_report()
    else:
        view_report(sys.argv[1])
