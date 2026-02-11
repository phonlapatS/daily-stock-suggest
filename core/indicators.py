import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    """Simple RSI Calculation."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_adx(high, low, close, period=14):
    """
    Average Directional Index (ADX) calculation.
    """
    plus_dm = high.diff()
    minus_dm = low.diff()
    
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = abs(minus_dm)
    
    # Simple DM mask
    plus_dm_mask = (plus_dm > minus_dm) & (plus_dm > 0)
    minus_dm_mask = (minus_dm > plus_dm) & (minus_dm > 0)
    
    true_plus_dm = np.where(plus_dm_mask, plus_dm, 0)
    true_minus_dm = np.where(minus_dm_mask, minus_dm, 0)
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Smoothing
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (pd.Series(true_plus_dm, index=close.index).rolling(window=period).mean() / atr)
    minus_di = 100 * (pd.Series(true_minus_dm, index=close.index).rolling(window=period).mean() / atr)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return pd.Series(adx, index=close.index)

def calculate_volume_adv(volume, period=20):
    """Average Daily Volume."""
    return volume.rolling(window=period).mean()
