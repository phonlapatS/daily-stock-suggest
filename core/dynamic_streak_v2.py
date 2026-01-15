"""
dynamic_streak_v2.py - Advanced Dynamic Threshold & Mixed Streak System
========================================================================

Implements:
1. 90th Percentile Dynamic Threshold (126 days)
2. Volatility Classification (Low/Med/High)
3. Mixed Streak Logic (direction-agnostic)
"""

import pandas as pd
import numpy as np


def apply_dynamic_logic(df):
    """
    Apply Dynamic Threshold and Mixed Streak Logic
    
    Args:
        df: DataFrame with 'close' and 'pct_change' columns
    
    Returns:
        df: DataFrame with new columns:
            - Threshold: Dynamic threshold per day
            - Vol_Type: Volatility classification
            - Streak: Mixed streak count
            - Status: Direction status
    """
    df = df.copy()
    
    # ========================================
    # Step 1: Dynamic Threshold Calculation
    # ========================================
    
    # Calculate 90th percentile of absolute % change (rolling 126 days)
    df['Threshold'] = df['pct_change'].abs().rolling(
        window=126, 
        min_periods=30  # At least 30 days
    ).quantile(0.90)
    
    # Apply floor of 1.0%
    df['Threshold'] = df['Threshold'].apply(lambda x: max(x, 1.0) if pd.notna(x) else 1.0)
    
    # ========================================
    # Step 2: Volatility Classification
    # ========================================
    
    # Calculate annualized volatility
    annual_vol = df['pct_change'].std() * np.sqrt(252)
    
    if annual_vol < 20:
        vol_type = 'Low'
    elif annual_vol <= 60:
        vol_type = 'Med'
    else:
        vol_type = 'High'
    
    df['Vol_Type'] = vol_type
    
    # ========================================
    # Step 3: Mixed Streak Logic
    # ========================================
    
    # Identify significant moves
    df['Significant'] = df['pct_change'].abs() > df['Threshold']
    
    # Calculate mixed streak
    df['Streak'] = 0
    current_streak = 0
    
    for i in range(len(df)):
        if df.iloc[i]['Significant']:
            current_streak += 1
        else:
            current_streak = 0  # Break streak
        
        df.iloc[i, df.columns.get_loc('Streak')] = current_streak
    
    # ========================================
    # Step 4: Status (based on today's direction)
    # ========================================
    
    df['Status'] = df.apply(lambda row: 
        '🟢 Up' if row['pct_change'] > 0 
        else '🔴 Down' if row['pct_change'] < 0 
        else '⚪ Neutral',
        axis=1
    )
    
    # Clean up temporary column
    df = df.drop('Significant', axis=1)
    
    return df


def calculate_historical_probability_mixed(df, threshold):
    """
    Calculate Historical Probability for Mixed Streaks
    
    Logic:
    1. Find all historical occurrences of current streak
    2. Look at next day return
    3. Calculate win rate
    
    Args:
        df: DataFrame with streak column
        threshold: Current threshold
    
    Returns:
        dict: {win_rate, avg_return, max_risk, sample_size}
    """
    if len(df) < 3:
        return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
    
    # Apply dynamic logic to get streak
    df = apply_dynamic_logic(df)
    
    # Get current streak
    current_streak = df['Streak'].iloc[-1]
    
    # If no streak, return zeros
    if current_streak == 0:
        return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
    
    # Add next_day_return
    df['next_day_return'] = df['pct_change'].shift(-1)
    
    # Find historical matches (exclude last row = today)
    history = df.iloc[:-1].copy()
    matching_events = history[history['Streak'] == current_streak]
    
    # Drop NaN in next_day_return
    matching_events = matching_events.dropna(subset=['next_day_return'])
    
    sample_size = len(matching_events)
    
    if sample_size == 0:
        return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
    
    # Calculate statistics
    wins = matching_events[matching_events['next_day_return'] > 0]
    win_rate = (len(wins) / sample_size) * 100
    avg_return = matching_events['next_day_return'].mean()
    max_risk = matching_events['next_day_return'].min()
    
    return {
        'win_rate': win_rate,
        'avg_return': avg_return,
        'max_risk': max_risk,
        'sample_size': sample_size
    }


# ========================================
# Demo Usage
# ========================================

if __name__ == "__main__":
    # Test with real parquet data
    import os
    
    parquet_file = 'data/stocks/PTT_SET.parquet'
    
    if os.path.exists(parquet_file):
        print("Loading real data from PTT...")
        df = pd.read_parquet(parquet_file)
        df.index = pd.to_datetime(df.index)
        
        if 'pct_change' not in df.columns:
            df['pct_change'] = df['close'].pct_change() * 100
        
        df = df.dropna()
        
        print(f"Loaded {len(df)} bars")
        print("\nBefore applying dynamic logic:")
        print(df[['close', 'pct_change']].tail())
        
        # Apply dynamic logic
        df_processed = apply_dynamic_logic(df)
        
        print("\n" + "="*70)
        print("After applying dynamic logic:")
        print("="*70)
        print(df_processed[['close', 'pct_change', 'Threshold', 'Vol_Type', 'Streak', 'Status']].tail(10))
        
        # Test probability calculation  
        if len(df_processed) > 0:
            prob = calculate_historical_probability_mixed(df, df_processed['Threshold'].iloc[-1])
            
            print("\n" + "="*70)
            print("Historical Probability (Mixed Streak):")
            print("="*70)
            print(f"Current Streak: {df_processed['Streak'].iloc[-1]}")
            print(f"Volatility Type: {df_processed['Vol_Type'].iloc[-1]}")
            print(f"Threshold: {df_processed['Threshold'].iloc[-1]:.2f}%")
            print(f"Win Rate: {prob['win_rate']:.1f}%")
            print(f"Avg Return: {prob['avg_return']:+.2f}%")
            print(f"Max Risk: {prob['max_risk']:+.2f}%")
            print(f"Sample Size: {prob['sample_size']}")
    else:
        print(f"File not found: {parquet_file}")
        print("Please run data_updater.py first")
