"""
momentum.py - Momentum Indicator Filter
========================================
Filter Logic: Use RSI, MACD, ADX to confirm momentum.
Returns: True (Momentum Confirmed) or False (Weak/Against Momentum)
"""

import pandas as pd
import numpy as np

def calculate_rsi(df, period=14):
    """Calculate Relative Strength Index."""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD and Signal line."""
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_adx(df, period=14):
    """Calculate Average Directional Index (simplified)."""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    # Directional Movement
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    
    return adx

def is_momentum_bullish(df):
    """
    Check if momentum indicators support a BULLISH trade.
    
    Conditions:
    - RSI > 30 (not oversold, or recovering)
    - MACD > Signal (bullish crossover)
    - ADX > 20 (trend exists)
    
    Returns:
        bool: True if momentum is bullish
    """
    rsi = calculate_rsi(df)
    macd, signal, _ = calculate_macd(df)
    adx = calculate_adx(df)
    
    current_rsi = rsi.iloc[-1]
    current_macd = macd.iloc[-1]
    current_signal = signal.iloc[-1]
    current_adx = adx.iloc[-1]
    
    # Check conditions
    rsi_ok = current_rsi > 30 and current_rsi < 70  # Not overbought/oversold
    macd_ok = current_macd > current_signal  # Bullish crossover
    adx_ok = current_adx > 20  # Trend exists
    
    return rsi_ok and macd_ok and adx_ok

def is_momentum_bearish(df):
    """
    Check if momentum indicators support a BEARISH trade.
    """
    rsi = calculate_rsi(df)
    macd, signal, _ = calculate_macd(df)
    adx = calculate_adx(df)
    
    current_rsi = rsi.iloc[-1]
    current_macd = macd.iloc[-1]
    current_signal = signal.iloc[-1]
    current_adx = adx.iloc[-1]
    
    rsi_ok = current_rsi < 70 and current_rsi > 30
    macd_ok = current_macd < current_signal  # Bearish crossover
    adx_ok = current_adx > 20
    
    return rsi_ok and macd_ok and adx_ok

def is_signal_confirmed(df, signal_direction):
    """
    Main function: Check if signal is confirmed by momentum.
    
    Args:
        df: Price DataFrame
        signal_direction: 'UP' or 'DOWN'
    
    Returns:
        bool: True if momentum confirms the signal
    """
    if signal_direction == 'UP':
        return is_momentum_bullish(df)
    elif signal_direction == 'DOWN':
        return is_momentum_bearish(df)
    return False
