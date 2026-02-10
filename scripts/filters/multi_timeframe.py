"""
multi_timeframe.py - Multi-Timeframe Confirmation Filter
=========================================================
Filter Logic: Confirm Daily signal with Weekly trend direction.
Returns: True (Confirmed) or False (Rejected)
"""

import pandas as pd

def resample_to_weekly(df):
    """
    Resample daily data to weekly OHLC.
    Assumes df has datetime index.
    """
    weekly = df.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    return weekly

def get_weekly_trend(df, lookback=4):
    """
    Determine weekly trend based on last N weeks.
    
    Args:
        df: Daily DataFrame (will be resampled to weekly)
        lookback: Number of weeks to analyze
    
    Returns:
        str: 'UP', 'DOWN', or 'SIDEWAYS'
    """
    weekly = resample_to_weekly(df)
    
    if len(weekly) < lookback:
        return 'SIDEWAYS'
    
    # Check if making higher highs/lows (UP) or lower highs/lows (DOWN)
    recent = weekly.tail(lookback)
    
    # Simple logic: Compare first and last close
    start_close = recent['close'].iloc[0]
    end_close = recent['close'].iloc[-1]
    
    change_pct = (end_close - start_close) / start_close * 100
    
    if change_pct > 2.0:  # 2% threshold
        return 'UP'
    elif change_pct < -2.0:
        return 'DOWN'
    else:
        return 'SIDEWAYS'

def is_signal_confirmed(df, daily_signal):
    """
    Check if daily signal is confirmed by weekly trend.
    
    Args:
        df: Daily DataFrame for the stock
        daily_signal: 'UP' or 'DOWN' (the signal from daily analysis)
    
    Returns:
        bool: True if weekly trend matches daily signal direction
    """
    weekly_trend = get_weekly_trend(df)
    
    # Confirm only if trends align
    if daily_signal == 'UP' and weekly_trend == 'UP':
        return True
    if daily_signal == 'DOWN' and weekly_trend == 'DOWN':
        return True
    
    # SIDEWAYS allows either direction (neutral)
    if weekly_trend == 'SIDEWAYS':
        return True
        
    return False
