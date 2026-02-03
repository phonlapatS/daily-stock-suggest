#!/usr/bin/env python
"""
view_report_v2.py - Advanced Statistical Report Generator
==========================================================
Implements Mentor's "Strict Mode" requirements:
1. Master Pattern Stats with Risk/Reward Ratio
2. Streak Survival Profile (n+1 Probability)
3. Fact Check Log (CSV Verification)

Author: Senior Python Data Engineer (Quant Trading)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ============================================================
# SECTION 0: Mock Data Generator (For Standalone Testing)
# ============================================================

def get_mock_data(symbol='PTT', days=500):
    """
    Generate realistic mock stock data for testing.
    Includes: Date, Close, Dynamic_Threshold
    """
    np.random.seed(42)  # Reproducible
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Simulate price movement (random walk with drift)
    returns = np.random.normal(0.0005, 0.015, days)  # Mean 0.05%, SD 1.5%
    close = 100 * np.cumprod(1 + returns)
    
    # Calculate pct_change
    pct_change = np.diff(close) / close[:-1] * 100
    pct_change = np.insert(pct_change, 0, 0)  # First day is 0
    
    # Calculate Dynamic Threshold (SD * 1.25)
    df = pd.DataFrame({
        'Date': dates,
        'Symbol': symbol,
        'Close': close,
        'Change_Pct': pct_change
    })
    
    # Rolling SD (20-day) * 1.25
    df['Dynamic_Threshold'] = df['Change_Pct'].rolling(window=20).std() * 1.25
    df['Dynamic_Threshold'] = df['Dynamic_Threshold'].fillna(df['Change_Pct'].std() * 1.25)
    
    return df


# ============================================================
# SECTION 1: Core Logic - Direction Classification
# ============================================================

def classify_direction(change_pct, threshold):
    """
    Strict Mode: Classify daily change into Direction.
    
    Returns:
        1  = UP (Significant Positive)
        -1 = DOWN (Significant Negative)
        0  = NOISE (Not Significant)
    """
    if change_pct > threshold:
        return 1
    elif change_pct < -threshold:
        return -1
    else:
        return 0


def apply_strict_direction(df):
    """
    Apply Strict Direction logic to entire DataFrame.
    Adds columns: Direction, Is_Pass_Threshold
    """
    df = df.copy()
    
    df['Direction'] = df.apply(
        lambda row: classify_direction(row['Change_Pct'], row['Dynamic_Threshold']),
        axis=1
    )
    
    df['Is_Pass_Threshold'] = df['Direction'] != 0
    
    return df


# ============================================================
# SECTION 2: Pattern Detection & Stats (Task 1)
# ============================================================

def build_pattern_string(directions, lookback=4):
    """
    Convert Direction sequence to Pattern String.
    Example: [1, 1, -1, 0] -> '++' (skips 0s, takes last 4 non-zero)
    
    V2 Logic: Only include significant days (non-zero)
    """
    # Filter out noise (0s)
    significant = [d for d in directions if d != 0]
    
    if len(significant) < 2:
        return None
    
    # Take last 'lookback' significant days
    recent = significant[-lookback:] if len(significant) >= lookback else significant
    
    pattern = ''
    for d in recent:
        if d == 1:
            pattern += '+'
        elif d == -1:
            pattern += '-'
    
    return pattern if len(pattern) >= 2 else None


def calculate_master_pattern_stats(df, min_occurrences=5):
    """
    Task 1: Master Pattern Stats with Risk/Reward Focus.
    
    Returns DataFrame with:
    - Pattern
    - Occurrences
    - Win_Prob
    - Avg_Win_Pct
    - Avg_Loss_Pct
    - RR_Ratio
    """
    df = apply_strict_direction(df)
    
    # Build patterns for each day
    patterns = []
    next_returns = []
    
    for i in range(10, len(df) - 1):
        # Get last 4 days' directions
        lookback_dirs = df['Direction'].iloc[i-3:i+1].tolist()
        pattern = build_pattern_string(lookback_dirs)
        
        if pattern:
            # Next day's return
            next_ret = df['Change_Pct'].iloc[i + 1]
            patterns.append(pattern)
            next_returns.append(next_ret)
    
    if not patterns:
        return pd.DataFrame()
    
    # Create analysis DataFrame
    analysis = pd.DataFrame({
        'Pattern': patterns,
        'Next_Return': next_returns
    })
    
    # Group by pattern
    results = []
    for pattern, group in analysis.groupby('Pattern'):
        occurrences = len(group)
        
        if occurrences < min_occurrences:
            continue
        
        # Determine forecast direction based on pattern
        # Last character of pattern determines expected direction
        last_char = pattern[-1]
        forecast_dir = 1 if last_char == '+' else -1
        
        # Win = next day moves in forecasted direction
        wins = group[group['Next_Return'] * forecast_dir > 0]
        losses = group[group['Next_Return'] * forecast_dir <= 0]
        
        win_prob = len(wins) / occurrences * 100
        
        avg_win_pct = wins['Next_Return'].abs().mean() if len(wins) > 0 else 0
        avg_loss_pct = losses['Next_Return'].abs().mean() if len(losses) > 0 else 0
        
        # Risk/Reward Ratio
        rr_ratio = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else np.inf
        
        results.append({
            'Pattern': pattern,
            'Forecast': 'UP' if forecast_dir == 1 else 'DOWN',
            'Occurrences': occurrences,
            'Win_Prob': round(win_prob, 1),
            'Avg_Win_Pct': round(avg_win_pct, 2),
            'Avg_Loss_Pct': round(avg_loss_pct, 2),
            'RR_Ratio': round(rr_ratio, 2)
        })
    
    return pd.DataFrame(results).sort_values('Win_Prob', ascending=False)


# ============================================================
# SECTION 3: Streak Survival Profile (Task 2)
# ============================================================

def calculate_streak_survival(df):
    """
    Task 2: Streak Survival Profile.
    
    Calculates conditional probability:
    "If stock reaches Day n streak, what % chance it continues to Day n+1?"
    
    Returns DataFrame with:
    - Streak_Type (UP/DOWN)
    - Day_n
    - Reached_Count
    - Continued_Count
    - Next_Day_Prob
    - Avg_Intensity
    """
    df = apply_strict_direction(df)
    
    # Calculate streaks
    streaks = []
    current_streak = 0
    current_dir = 0
    intensity_sum = 0
    
    for i in range(len(df)):
        direction = df['Direction'].iloc[i]
        change = abs(df['Change_Pct'].iloc[i])
        
        if direction == 0:
            # NOISE: streak breaks
            if current_streak > 0:
                streaks.append({
                    'end_idx': i - 1,
                    'length': current_streak,
                    'type': 'UP' if current_dir == 1 else 'DOWN',
                    'avg_intensity': intensity_sum / current_streak
                })
            current_streak = 0
            current_dir = 0
            intensity_sum = 0
        elif current_dir == 0 or direction == current_dir:
            # Start or continue streak
            current_dir = direction
            current_streak += 1
            intensity_sum += change
        else:
            # Reversal: streak breaks
            if current_streak > 0:
                streaks.append({
                    'end_idx': i - 1,
                    'length': current_streak,
                    'type': 'UP' if current_dir == 1 else 'DOWN',
                    'avg_intensity': intensity_sum / current_streak
                })
            # Start new streak in opposite direction
            current_dir = direction
            current_streak = 1
            intensity_sum = change
    
    # Handle last streak
    if current_streak > 0:
        streaks.append({
            'end_idx': len(df) - 1,
            'length': current_streak,
            'type': 'UP' if current_dir == 1 else 'DOWN',
            'avg_intensity': intensity_sum / current_streak
        })
    
    if not streaks:
        return pd.DataFrame()
    
    # Calculate survival probabilities for each day
    results = []
    
    for streak_type in ['UP', 'DOWN']:
        type_streaks = [s for s in streaks if s['type'] == streak_type]
        
        if not type_streaks:
            continue
        
        max_length = max(s['length'] for s in type_streaks)
        
        for day in range(1, min(max_length + 1, 11)):  # Cap at 10 days
            reached = sum(1 for s in type_streaks if s['length'] >= day)
            continued = sum(1 for s in type_streaks if s['length'] >= day + 1)
            
            if reached == 0:
                continue
            
            # Conditional probability
            next_day_prob = continued / reached * 100
            
            # Average intensity at this day
            day_intensities = [s['avg_intensity'] for s in type_streaks if s['length'] >= day]
            avg_intensity = np.mean(day_intensities) if day_intensities else 0
            
            results.append({
                'Streak_Type': streak_type,
                'Day_n': day,
                'Reached_Count': reached,
                'Continued_Count': continued,
                'Next_Day_Prob': round(next_day_prob, 1),
                'Avg_Intensity': round(avg_intensity, 2)
            })
    
    return pd.DataFrame(results)


# ============================================================
# SECTION 4: Fact Check Log (Task 3)
# ============================================================

def generate_fact_check_log(df, output_path='fact_check_log.csv'):
    """
    Task 3: Generate Verification CSV.
    
    Exports row-by-row data for manual verification.
    """
    df = apply_strict_direction(df)
    
    log_df = df[['Date', 'Symbol', 'Close', 'Change_Pct', 'Dynamic_Threshold', 
                  'Direction', 'Is_Pass_Threshold']].copy()
    
    # Add human-readable direction label
    log_df['Direction_Label'] = log_df['Direction'].map({
        1: 'UP',
        -1: 'DOWN',
        0: 'NOISE'
    })
    
    # Round for readability
    log_df['Close'] = log_df['Close'].round(2)
    log_df['Change_Pct'] = log_df['Change_Pct'].round(2)
    log_df['Dynamic_Threshold'] = log_df['Dynamic_Threshold'].round(2)
    
    # Save to CSV
    log_df.to_csv(output_path, index=False)
    print(f"📁 Saved: {output_path} ({len(log_df)} rows)")
    
    return log_df


# ============================================================
# SECTION 5: Report Printer
# ============================================================

def print_master_pattern_stats(df_stats):
    """Pretty print Master Pattern Stats."""
    print("\n" + "=" * 80)
    print("📊 MASTER PATTERN STATS (Risk/Reward Focus)")
    print("=" * 80)
    
    if df_stats.empty:
        print("❌ No patterns found with sufficient occurrences.")
        return
    
    print(f"{'Pattern':<10} {'Forecast':<8} {'Occur':<8} {'Win%':<8} {'AvgWin%':<10} {'AvgLoss%':<10} {'RR_Ratio':<10}")
    print("-" * 80)
    
    for _, row in df_stats.head(15).iterrows():
        icon = '🟢' if row['Forecast'] == 'UP' else '🔴'
        print(f"{row['Pattern']:<10} {icon} {row['Forecast']:<5} {row['Occurrences']:<8} "
              f"{row['Win_Prob']:<8} {row['Avg_Win_Pct']:<10} {row['Avg_Loss_Pct']:<10} {row['RR_Ratio']:<10}")
    
    print("-" * 80)
    print(f"Total Patterns: {len(df_stats)}")


def print_streak_survival(df_survival):
    """Pretty print Streak Survival Profile."""
    print("\n" + "=" * 80)
    print("📈 STREAK SURVIVAL PROFILE (n+1 Probability)")
    print("=" * 80)
    
    if df_survival.empty:
        print("❌ No streaks found.")
        return
    
    for streak_type in ['UP', 'DOWN']:
        type_data = df_survival[df_survival['Streak_Type'] == streak_type]
        if type_data.empty:
            continue
        
        icon = '🟢' if streak_type == 'UP' else '🔴'
        print(f"\n{icon} {streak_type} STREAKS:")
        print(f"{'Day':<6} {'Reached':<10} {'Continued':<12} {'Prob%':<10} {'Avg_Intensity':<12}")
        print("-" * 50)
        
        for _, row in type_data.iterrows():
            prob_bar = '█' * int(row['Next_Day_Prob'] / 10)
            print(f"Day {row['Day_n']:<3} {row['Reached_Count']:<10} {row['Continued_Count']:<12} "
                  f"{row['Next_Day_Prob']:<10} {row['Avg_Intensity']:<12} {prob_bar}")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("\n" + "=" * 80)
    print("🔬 VIEW REPORT V2 (Mentor's Strict Mode)")
    print("=" * 80)
    print("Implementing: Single Source of Truth, RR Ratio, Streak Survival, Fact Check")
    print("=" * 80)
    
    # Generate mock data for testing
    print("\n📊 Loading Mock Data...")
    df = get_mock_data('PTT', days=1000)
    print(f"   Loaded: {len(df)} rows")
    print(f"   Date Range: {df['Date'].min().date()} → {df['Date'].max().date()}")
    
    # Task 1: Master Pattern Stats
    print("\n⏳ Calculating Master Pattern Stats...")
    df_stats = calculate_master_pattern_stats(df, min_occurrences=5)
    print_master_pattern_stats(df_stats)
    
    # Task 2: Streak Survival Profile
    print("\n⏳ Calculating Streak Survival Profile...")
    df_survival = calculate_streak_survival(df)
    print_streak_survival(df_survival)
    
    # Task 3: Fact Check Log
    print("\n⏳ Generating Fact Check Log...")
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'fact_check_log.csv')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    generate_fact_check_log(df, log_path)
    
    print("\n" + "=" * 80)
    print("✅ REPORT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
