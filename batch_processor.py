#!/usr/bin/env python
"""
batch_processor.py - Batch Pattern Statistical Calculator (REAL DATA)
======================================================================
Analyzes historical stock data from tvDatafeed and calculates pattern 
probabilities. Outputs results in "Long Format" CSV.

Version: 3.0 (Production)
"""

import pandas as pd
import numpy as np
import itertools
from typing import List, Dict
import time
import sys

# Import from existing project
from tvDatafeed import TvDatafeed
import config

# ============================================================
# CONFIGURATION
# ============================================================
OUTPUT_FILE = "data/Master_Pattern_Stats.csv"
VOLATILITY_WINDOW = 20  # Days for threshold calculation

# ============================================================
# REAL DATA FUNCTION (Using tvDatafeed)
# ============================================================
def get_stock_data(tv: TvDatafeed, symbol: str, exchange: str, 
                   interval, n_bars: int = 5000) -> pd.DataFrame:
    """
    Fetch real stock data from TradingView via tvDatafeed.
    """
    for attempt in range(3):
        try:
            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars
            )
            if df is not None and not df.empty:
                return df
        except Exception as e:
            time.sleep(1)
    return None


# ============================================================
# PATTERN GENERATION (Dynamic Length)
# ============================================================
def generate_patterns(max_length: int = 4) -> List[Dict]:
    """
    Generate patterns dynamically based on max_length.
    - 1-4 days: All combinations (2^n patterns)
    - 5+ days: Streak patterns only (all + or all -)
    
    Args:
        max_length: Maximum pattern length for this stock (default 4)
    
    Returns:
        List of dicts with: pattern, pattern_name, category
    """
    patterns = []
    
    # Ensure minimum of 3, cap at reasonable maximum
    max_length = max(3, min(max_length, 10))
    
    # Level 1-4: All combinations
    combo_limit = min(4, max_length)
    for length in range(1, combo_limit + 1):
        for combo in itertools.product(['+', '-'], repeat=length):
            pattern_str = ''.join(combo)
            
            # Determine name and category
            up_count = pattern_str.count('+')
            down_count = pattern_str.count('-')
            
            if up_count == length:
                name = f"{length}_Days_Up"
                category = "Trend"
            elif down_count == length:
                name = f"{length}_Days_Down"
                category = "Trend"
            elif pattern_str.endswith('+') and pattern_str.startswith('-'):
                name = f"{length}D_Reversal_Up"
                category = "Reversal"
            elif pattern_str.endswith('-') and pattern_str.startswith('+'):
                name = f"{length}D_Reversal_Down"
                category = "Reversal"
            else:
                name = f"{length}D_Mixed_{pattern_str}"
                category = "Mixed"
            
            patterns.append({
                'pattern': pattern_str,
                'pattern_name': name,
                'category': category
            })
    
    # Level 5+: Streak patterns only (all + or all -)
    for length in range(5, max_length + 1):
        # All Up streak
        patterns.append({
            'pattern': '+' * length,
            'pattern_name': f'Streak_Up_{length}',
            'category': 'Breakout'
        })
        # All Down streak
        patterns.append({
            'pattern': '-' * length,
            'pattern_name': f'Streak_Down_{length}',
            'category': 'Breakout'
        })
    
    return patterns


# ============================================================
# STOCK DNA CALCULATION
# ============================================================
def calculate_stock_dna(df: pd.DataFrame) -> Dict:
    """
    Calculate static "DNA" values for a stock:
    - Threshold (volatility-based)
    - Max_Streak_Pos (longest consecutive green days)
    - Max_Streak_Neg (longest consecutive red days)
    """
    close = df['close']
    pct_change = close.pct_change()
    
    # Threshold: 20-day rolling STD * 1.25 (Standard V2 Logic)
    recent_std = pct_change.iloc[-VOLATILITY_WINDOW:].std()
    threshold = recent_std * 1.25 * 100  # Convert to percentage
    threshold_str = f"±{threshold:.1f}%"
    
    # Max Streak Calculations (Threshold Based)
    # Only count streaks where change exceeds the volatility threshold
    is_green = pct_change > (threshold / 100)
    is_red = pct_change < (-threshold / 100)
    
    max_streak_pos = _calculate_max_streak(is_green)
    max_streak_neg = _calculate_max_streak(is_red)
    
    return {
        'threshold': threshold_str,
        'threshold_pct': threshold / 100,
        'max_streak_pos': max_streak_pos,
        'max_streak_neg': max_streak_neg,
        'total_bars': len(df)
    }

def _calculate_max_streak(bool_series: pd.Series) -> int:
    """Calculate longest consecutive True streak in a boolean Series."""
    if bool_series.empty:
        return 0
    
    groups = (bool_series != bool_series.shift()).cumsum()
    streak_lengths = bool_series.groupby(groups).apply(
        lambda x: x.sum() if x.iloc[0] else 0
    )
    
    return int(streak_lengths.max()) if not streak_lengths.empty else 0


# ============================================================
# STREAK PROFILE CALCULATION (Survival Analysis)
# ============================================================
def calculate_streak_profile(df: pd.DataFrame, symbol: str, threshold_pct: float) -> List[Dict]:
    """
    Calculate Streak Survival Profile for a stock.
    Returns probability of streak continuing from n → n+1 days.
    """
    close = df['close']
    pct_change = close.pct_change()
    
    # Determine Direction (same logic as Pattern detection)
    conditions = [
        (pct_change > threshold_pct),
        (pct_change < -threshold_pct)
    ]
    direction = np.select(conditions, [1, -1], default=0)
    
    # Strict Mode: Use full dataframe, including 0s
    work_df = pd.DataFrame({'direction': direction, 'pct_change': pct_change})
    
    if work_df.empty:
        return []
    
    # Identify Streaks (group consecutive same directions)
    work_df['grp_change'] = (work_df['direction'] != work_df['direction'].shift(1))
    work_df['streak_id'] = work_df['grp_change'].cumsum()
    
    # Calculate max length AND avg intensity of each streak
    # Avg intensity = mean of (pct_change * 100) inside the streak
    streak_summary = work_df.groupby(['streak_id', 'direction']).agg(
        max_length=('direction', 'size'),
        avg_intensity=('pct_change', 'mean')
    ).reset_index()
    
    streak_summary['avg_intensity'] = streak_summary['avg_intensity'] * 100
    
    # Survival Calculation
    results = []
    for direction_val in [1, -1]:
        streak_type = 'UP' if direction_val == 1 else 'DOWN'
        sub_data = streak_summary[streak_summary['direction'] == direction_val]
        
        if sub_data.empty:
            continue
        
        max_days = sub_data['max_length'].max()
        
        for n in range(1, max_days + 1):
            reached_grp = sub_data[sub_data['max_length'] >= n]
            reached = len(reached_grp)
            
            # Count continued
            continued = (sub_data['max_length'] >= n + 1).sum()
            prob = (continued / reached * 100) if reached > 0 else 0.0
            
            # Avg Intensity of streaks that survived at least n days
            avg_int_n = reached_grp['avg_intensity'].mean()
            
            results.append({
                'Symbol': symbol,
                'Streak_Type': streak_type,
                'Day_Count_n': n,
                'Reached_Count': reached,
                'Continued_to_n_plus_1': continued,
                'Next_Day_Prob_Percent': round(prob, 2),
                'Avg_Intensity': round(avg_int_n, 2)
            })
    
    return results


# ============================================================
# PATTERN SCANNING
# ============================================================
def scan_pattern(df: pd.DataFrame, pattern: str, dna: Dict) -> Dict:
    """
    Scan dataframe for a specific pattern and calculate statistics.
    Win = Next Day is positive (GREEN)
    """
    close = df['close']
    pct_change = close.pct_change()
    
    threshold = dna['threshold_pct']
    pattern_len = len(pattern)
    wins = 0
    total = 0
    

    
    returns = []
    # Scan through history
    for i in range(pattern_len, len(pct_change) - 1):
        window = pct_change.iloc[i - pattern_len:i]
        
        # Convert to pattern string efficiently
        # (This inner loop is the bottleneck, but fine for now)
        window_pattern = ''
        for ret in window:
            if pd.isna(ret): break
            if ret > threshold: window_pattern += '+'
            elif ret < -threshold: window_pattern += '-'
        
        if len(window_pattern) != pattern_len: continue # Skip if incomplete/break

        if window_pattern == pattern:
            next_ret = pct_change.iloc[i]
            returns.append(next_ret)

    total = len(returns)
    up_count = sum(1 for r in returns if r > 0)
    down_count = sum(1 for r in returns if r < 0)
    
    # Total decisive days (exclude FLAT)
    decisive_total = up_count + down_count
    
    # Determine which outcome is more frequent (excluding FLAT)
    if up_count >= down_count:
        dominant_direction = 'UP'
        dominant_count = up_count
    else:
        dominant_direction = 'DOWN'
        dominant_count = down_count
    
    # Probability based on decisive days only (UP vs DOWN, not FLAT)
    prob = (dominant_count / decisive_total * 100) if decisive_total > 0 else 0
        
    # Calculate Average Return (Next Day)
    avg_return = pd.Series(returns).mean() * 100 if returns else 0.0
    
    return {
        'up_count': up_count,
        'down_count': down_count,
        'total': total,
        'dominant_direction': dominant_direction,
        'dominant_count': dominant_count,
        'prob': f"{int(prob)}%",
        'stats': f"{dominant_count}/{decisive_total} ({dna['total_bars']})",
        'avg_return': avg_return
    }


# ============================================================
# MAIN BATCH PROCESSOR
# ============================================================
def process_all_assets() -> pd.DataFrame:
    """
    Main batch processing function.
    Processes all assets from config.py and all patterns.
    """
    print("🚀 Starting Batch Pattern Processor (REAL DATA)...")
    
    # Connect to TradingView
    try:
        tv = TvDatafeed()
        print("✅ Connected to TradingView")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return pd.DataFrame()
    
    # Note: Patterns are now generated per-stock based on their DNA
    print("📊 Dynamic pattern generation enabled (based on stock DNA)")
    
    all_results = []
    all_streak_results = []  # NEW: For Streak Profile
    total_assets = 0
    success_count = 0
    
    # Count total assets
    for group_name, settings in config.ASSET_GROUPS.items():
        total_assets += len(settings['assets'])
    
    print(f"📂 Total assets to process: {total_assets}")
    print("=" * 60)
    
    current_idx = 0
    
    # Process each asset group
    for group_name, settings in config.ASSET_GROUPS.items():
        group_desc = settings['description']
        interval = settings['interval']
        history_bars = settings['history_bars']
        assets = settings['assets']
        
        print(f"\n📁 {group_desc} ({len(assets)} assets)")
        
        for asset in assets:
            current_idx += 1
            symbol = asset['symbol']
            exchange = asset['exchange']
            display_name = asset.get('name', symbol)
            
            sys.stdout.write(f"\r   [{current_idx}/{total_assets}] Processing {display_name}...")
            sys.stdout.flush()
            
            # Fetch data
            df = get_stock_data(tv, symbol, exchange, interval, history_bars)
            
            if df is None or len(df) < 50:
                continue
            
            success_count += 1
            
            # Calculate Stock DNA
            dna = calculate_stock_dna(df)
            
            # Dynamic pattern length based on stock DNA
            max_length = max(dna['max_streak_pos'], dna['max_streak_neg'], 3)
            
            # Generate patterns for this stock
            patterns = generate_patterns(max_length)
            
            # Scan all patterns
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                stats = scan_pattern(df, pattern, dna)
                
                # Skip patterns with no occurrences
                if stats['total'] == 0:
                    continue
                
                # Determine Chance (based on more frequent outcome)
                if stats['dominant_direction'] == 'UP':
                    chance = "🟢 UP"
                else:
                    chance = "🔴 DOWN"
                
                # Build result row
                row = {
                    'Symbol': display_name,
                    'Threshold': dna['threshold'],
                    'Max_Streak_Pos': dna['max_streak_pos'],
                    'Max_Streak_Neg': dna['max_streak_neg'],
                    'Pattern': pattern,
                    'Pattern_Name': pattern_info['pattern_name'],
                    'Category': pattern_info['category'],
                    'Chance': chance,
                    'Prob': stats['prob'],
                    'Stats': stats['stats'],
                    'avg_return': stats['avg_return']
                }
                all_results.append(row)
            
            # ============================================================
            # 2. STREAK PROFILE GENERATION (New)
            # ============================================================
            try:
                streak_stats = calculate_streak_profile(df, display_name, dna['threshold_pct'])
                all_streak_results.extend(streak_stats)
            except Exception as e:
                print(f"   ⚠️ Error generating streak profile: {e}")

            time.sleep(0.3)  # Rate limit

            # Incremental Save (Every 5 assets)
            if success_count % 5 == 0:
                # Save Master Stats
                if all_results:
                    columns_master = [
                        'Symbol', 'Threshold', 'Max_Streak_Pos', 'Max_Streak_Neg',
                        'Pattern', 'Pattern_Name', 'Category', 'Chance', 'Prob', 'Stats', 'avg_return'
                    ]
                    try:
                        pd.DataFrame(all_results, columns=columns_master).to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
                    except Exception as e:
                        print(f"   ⚠️ Could not save Master Stats CSV: {e}")
                
                # Save Streak Profile
                if all_streak_results:
                    columns_streak = [
                        'Symbol', 'Streak_Type', 'Day_Count_n', 'Reached_Count', 'Continued_to_n_plus_1', 'Next_Day_Prob_Percent', 'Avg_Intensity'
                    ]
                    try:
                        pd.DataFrame(all_streak_results, columns=columns_streak).to_csv("data/Streak_Profile.csv", index=False, encoding='utf-8-sig')
                    except Exception as e:
                        print(f"   ⚠️ Could not save Streak Profile CSV: {e}")
    
    print(f"\n\n{'=' * 60}")
    print(f"✅ Processed: {success_count}/{total_assets} assets")
    
    # Create DataFrames
    columns_master = [
        'Symbol', 'Threshold', 'Max_Streak_Pos', 'Max_Streak_Neg',
        'Pattern', 'Pattern_Name', 'Category', 'Chance', 'Prob', 'Stats', 'avg_return'
    ]
    columns_streak = [
        'Symbol', 'Streak_Type', 'Day_Count_n', 'Reached_Count', 'Continued_to_n_plus_1', 'Next_Day_Prob_Percent', 'Avg_Intensity'
    ]
    
    df_master = pd.DataFrame(all_results, columns=columns_master)
    df_streak = pd.DataFrame(all_streak_results, columns=columns_streak)
    
    # Final Save
    df_streak.to_csv("data/Streak_Profile.csv", index=False, encoding='utf-8-sig')
    
    return df_master


def print_formatted_table(df: pd.DataFrame, max_rows: int = 30):
    """
    Print DataFrame as a nicely formatted table.
    Columns: Symbol, Threshold, Max_Streak_Pos, Max_Streak_Neg, Pattern, Pattern_Name, Category, Prob, Stats
    """
    print("\n" + "=" * 120)
    print("📊 MASTER PATTERN STATS (Sample)")
    print("=" * 120)
    
    # Header
    header = f"{'Symbol':<10} {'Threshold':>10} {'MaxUp':>6} {'MaxDown':>8} {'Pattern':^8} {'Pattern_Name':<20} {'Category':<10} {'Prob':>6} {'Stats':>18}"
    print("-" * 120)
    print(header)
    print("-" * 120)
    
    # Rows
    for idx, row in df.head(max_rows).iterrows():
        symbol = str(row['Symbol'])[:10]
        threshold = str(row['Threshold'])
        max_up = int(row['Max_Streak_Pos'])
        max_down = int(row['Max_Streak_Neg'])
        pattern = str(row['Pattern'])
        pattern_name = str(row['Pattern_Name'])[:20]
        category = str(row['Category'])[:10]
        prob = str(row['Prob'])
        stats = str(row['Stats'])
        
        print(f"{symbol:<10} {threshold:>10} {max_up:>6} {max_down:>8} {pattern:^8} {pattern_name:<20} {category:<10} {prob:>6} {stats:>18}")
    
    print("-" * 120)
    
    if len(df) > max_rows:
        print(f"... and {len(df) - max_rows} more rows")


def main():
    """Main entry point."""
    start_time = time.time()
    
    # Run batch processing
    result_df = process_all_assets()
    
    if result_df.empty:
        print("❌ No data processed.")
        return
    
    # Save to CSV
    result_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved {len(result_df)} rows to {OUTPUT_FILE}")
    
    # Show formatted table
    print_formatted_table(result_df, max_rows=30)
    
    # Execution time
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n⏱️ Total time: {minutes}m {seconds}s")


if __name__ == "__main__":
    main()

