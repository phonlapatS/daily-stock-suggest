#!/usr/bin/env python3
"""
generate_master_stats.py - Generate Master Pattern Stats CSV
============================================================
Generates 'data/Master_Pattern_Stats_NewLogic.csv' by scanning the entire history 
of all assets in config.py.

Modes:
1. Default: Uses Dynamic Volatility Threshold (Standard Logic)
   - Only significant moves (> threshold) form patterns.
   - Neutral days break patterns.

2. No Threshold (--no-threshold):
   - Threshold = 0.0
   - Every day is + or - (unless exactly 0.0).
   - Captures raw price movement patterns without volatility filtering.

Usage:
  python scripts/generate_master_stats.py                   # Default (With Threshold)
  python scripts/generate_master_stats.py --no-threshold    # No Threshold Version
"""

import os
import sys
import pandas as pd
import numpy as np
import argparse
from tqdm import tqdm
from collections import defaultdict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core.data_cache import get_data_with_cache
from tvDatafeed import TvDatafeed, Interval
from core.engines.reversion_engine import MeanReversionEngine

# Output Path
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'data', 'Master_Pattern_Stats_NewLogic.csv')

def scan_history(df, engine, no_threshold=False, min_floor=0.0):
    """
    Scans the entire history of a stock to count pattern occurrences.
    """
    if df is None or len(df) < 50:
        return {}

    close = df['close']
    pct_change = close.pct_change()
    
    # Calculate Thresholds
    if no_threshold:
        # Version 2: No Threshold (All moves count)
        # Use a very small epsilon to validly compare floats, or just 0.0
        effective_std = pd.Series(0.0, index=pct_change.index)
    else:
        # Version 1: Dynamic Threshold (Standard Logic)
        effective_std = engine.calculate_dynamic_threshold(pct_change, min_floor)

    # Dictionary to count patterns: pattern -> {total, up, down, neutral}
    pattern_counts = {}
    
    # Sliding window over history
    # Start from index 50 to have enough history for volatility calc
    # Loop until the end
    n = len(df)
    
    # We want patterns ending at day `i`
    # We look back up to max_len (8)
    # Optimization: BasePatternEngine.extract_pattern takes a slice
    
    # Pre-calculate signals to speed up? 
    # extract_pattern logic: 
    # for r, t in zip(reversed(returns), reversed(thresh)): ...
    
    # Let's stick to the robust method: call extract_pattern for each day
    # It might be slow but it's correct.
    
    # Performance Optimization:
    # Convert series to numpy arrays for faster indexing
    pct_arr = pct_change.values
    thresh_arr = effective_std.values
    
    # Iterate through history
    # Start at max_len to ensure we can look back
    # End at n - 1 (because we need next day's outcome)
    for i in range(engine.max_len, n - 1):
        # Window ending at i (inclusive)
        # Extract pattern ending at i
        # We pass a window of max_len ending at i
        
        window_returns = pct_arr[i-engine.max_len+1 : i+1]
        window_thresh = thresh_arr[i-engine.max_len+1 : i+1]
        
        # We need to reverse because extract_pattern expects [oldest ... newest] 
        # BUT BasePatternEngine.extract_pattern iterates zip(returns, threshold)
        # and builds string: if r > t: + ...
        # So providing [oldest ... newest] builds string "Oldest...Newest"
        # Wait, let's check base_engine logic:
        # for r, t in zip(returns, threshold): ... pat_str += ...
        # So "Oldest" char comes first. Correct.
        
        # However, extract_pattern "breaks on neutral".
        # If we feed it [t-7, t-6, ... t], and t-4 is neutral, returns string for [t-7...t-5].
        # But we want the pattern ENDING at t.
        # So we should feed it REVERSED arrays: [t, t-1, t-2 ...]
        # And then reverse the result string.
        
        # Let's verify BasePatternEngine.get_active_pattern logic:
        # It walks backwards: for i in range(1, max_lookback+1): idx = len - i ...
        # And then reverses the chars.
        
        # So, to use extract_pattern correctly for "Tail Matching":
        # We should pass [t, t-1, ... t-7]
        # Then reverse the result string??
        
        # Actually, let's just implement the "Walk Backwards" logic here inline for speed and correctness.
        # This matches get_active_pattern.
        
        current_pattern_chars = []
        for back in range(engine.max_len):
            idx = i - back
            if idx < 0: break
            
            r = pct_arr[idx]
            t = thresh_arr[idx]
            
            if np.isnan(r) or np.isnan(t): break
            
            # Neutral Check
            if abs(r) <= t: # Use <= to handle 0.0 threshold case (0 is neutral)
                break
                
            if r > t:
                current_pattern_chars.append('+')
            elif r < -t:
                current_pattern_chars.append('-')
        
        if not current_pattern_chars:
            continue
            
        # Reverse to get chronological order (Old -> New)
        current_pattern_chars.reverse()
        full_pat = "".join(current_pattern_chars)
        
        # --------------------------------------------------
        # Determine NEXT DAY Outcome (i + 1)
        # --------------------------------------------------
        next_ret = pct_arr[i+1]
        threshold_at_scan = thresh_arr[i] 
        
        outcome = 'neutral'
        if next_ret > threshold_at_scan:
            outcome = 'up'
        elif next_ret < -threshold_at_scan:
            outcome = 'down'
        
        # --------------------------------------------------
        # Record Stats for All Suffixes
        # --------------------------------------------------
        
        # --------------------------------------------------
        # Record Stats for All Suffixes
        # --------------------------------------------------
        
        # Record ALL suffixes of the active pattern to ensure complete statistics
        # e.g. Active "++-" -> Record "++-", "+-", "-"
        
        # Loop through all valid lengths (min_len=1 to len)
        for length in range(1, len(full_pat) + 1):
            sub_pat = full_pat[-length:] # Suffix
            
            # Initialize if new
            if sub_pat not in pattern_counts:
                pattern_counts[sub_pat] = {'total': 0, 'up': 0, 'down': 0, 'neutral': 0}
            
            stats = pattern_counts[sub_pat]
            stats['total'] += 1
            stats[outcome] += 1

    return pattern_counts

def main():
    parser = argparse.ArgumentParser(description="Generate Master Pattern Stats")
    parser.add_argument('--no-threshold', action='store_true', help="Use 0.0 threshold (ignore volatility)")
    args = parser.parse_args()

    print("=" * 70)
    print("🏗️  GENERATING MASTER PATTERN STATS")
    print(f"   Mode: {'NO THRESHOLD (All moves count)' if args.no_threshold else 'DYNAMIC THRESHOLD (Standard)'}")
    print(f"   Output: {OUTPUT_FILE}")
    print("=" * 70)

    # Initialize Engine (used for calc methods)
    engine = MeanReversionEngine()
    
    # Initialize TV Datafeed
    tv = TvDatafeed()
    
    all_stats = []
    
    # 1. Collect Assets
    assets = []
    seen = set()
    
    # Iterate config groups
    for group_name, group_data in config.ASSET_GROUPS.items():
        market_name = group_name.replace('GROUP_', '').replace('_', ' ')
        
        # Determine Market Label for CSV
        if 'THAI' in group_name: market_label = 'THAI'
        elif 'US' in group_name: market_label = 'US'
        elif 'CHINA' in group_name: market_label = 'CHINA'
        elif 'TAIWAN' in group_name: market_label = 'TAIWAN'
        else: market_label = 'OTHER'
        
        min_floor = group_data.get('min_threshold', 0.0)
        
        for asset in group_data['assets']:
            sym = asset['symbol']
            exch = asset['exchange']
            key = (sym, exch)
            
            if key not in seen:
                seen.add(key)
                assets.append({
                    'symbol': sym, 
                    'exchange': exch, 
                    'market': market_label,
                    'interval': group_data.get('interval', Interval.in_daily),
                    'min_floor': min_floor
                })

    print(f"🔍 Found {len(assets)} assets to scan.")
    
    # 2. Process Assets
    with tqdm(total=len(assets), unit="stock") as pbar:
        for asset in assets:
            sym = asset['symbol']
            pbar.set_description(f"Scanning {sym}")
            
            try:
                # Fetch Data
                df = get_data_with_cache(tv, sym, asset['exchange'], asset['interval'], 5000, 30)
                
                # Scan History
                counts = scan_history(df, engine, no_threshold=args.no_threshold, min_floor=asset['min_floor'])
                
                # Append to list
                for pat, stats in counts.items():
                    total = stats['total']
                    if total == 0: continue
                    
                    # Reliability = Max(Up, Down) / Total
                    reliability = max(stats['up'], stats['down']) / total * 100
                    
                    all_stats.append({
                        'Symbol': sym,
                        'Market': asset['market'],
                        'Pattern': pat,
                        'Length': len(pat),
                        'Count': total,
                        'Next_Up': stats['up'],
                        'Next_Down': stats['down'],
                        'Next_Neutral': stats['neutral'],
                        'Reliability': round(reliability, 2)
                    })
                    
            except Exception as e:
                # print(f"Error {sym}: {e}")
                pass
            
            pbar.update(1)

    # 3. Save to CSV
    if not all_stats:
        print("❌ No stats generated!")
        sys.exit(1)
        
    df_stats = pd.DataFrame(all_stats)
    
    # Sort for tidiness
    df_stats = df_stats.sort_values(['Market', 'Symbol', 'Length', 'Pattern'])
    
    df_stats.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Successfully saved {len(df_stats):,} rows to {OUTPUT_FILE}")
    print(f"   Unique Patterns: {df_stats['Pattern'].nunique()}")
    print("-" * 70)

if __name__ == "__main__":
    main()
