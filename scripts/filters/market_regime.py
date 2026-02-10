"""
market_regime.py - Market Trend Filter
=======================================
Filter Logic: Check if SPY and QQQ are above their SMA50.
Returns: True (BULL/Allow Trade) or False (BEAR/Block Trade)
"""

import pandas as pd

def calculate_sma(df, period=50):
    """Calculate Simple Moving Average."""
    return df['close'].rolling(period).mean()

def is_market_bullish(spy_df, qqq_df=None, use_sma200=False):
    """
    Check if market is in BULL mode.
    
    Args:
        spy_df: DataFrame with SPY price data (must have 'close' column)
        qqq_df: Optional DataFrame with QQQ price data
        use_sma200: If True, use SMA200 instead of SMA50
    
    Returns:
        bool: True if market is BULLISH (allow LONG trades)
    """
    period = 200 if use_sma200 else 50
    
    # SPY Check
    spy_sma = calculate_sma(spy_df, period)
    spy_current = spy_df['close'].iloc[-1]
    spy_bullish = spy_current > spy_sma.iloc[-1]
    
    # If QQQ provided, require both to be bullish
    if qqq_df is not None:
        qqq_sma = calculate_sma(qqq_df, period)
        qqq_current = qqq_df['close'].iloc[-1]
        qqq_bullish = qqq_current > qqq_sma.iloc[-1]
        return spy_bullish and qqq_bullish
    
    return spy_bullish

def get_regime_score(spy_df, qqq_df=None):
    """
    Get a numeric score for market regime.
    Score > 0 = BULL, Score <= 0 = BEAR
    """
    score = 0
    
    # SPY vs SMA50
    spy_sma50 = calculate_sma(spy_df, 50).iloc[-1]
    spy_sma200 = calculate_sma(spy_df, 200).iloc[-1]
    spy_price = spy_df['close'].iloc[-1]
    
    if spy_price > spy_sma50:
        score += 1
    if spy_price > spy_sma200:
        score += 1
    if spy_price < spy_sma50:
        score -= 1
    if spy_price < spy_sma200:
        score -= 1
        
    if qqq_df is not None:
        qqq_sma50 = calculate_sma(qqq_df, 50).iloc[-1]
        qqq_price = qqq_df['close'].iloc[-1]
        if qqq_price > qqq_sma50:
            score += 1
        else:
            score -= 1
            
    return score
