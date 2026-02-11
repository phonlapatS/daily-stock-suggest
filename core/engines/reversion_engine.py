import numpy as np
import pandas as pd
from .base_engine import BasePatternEngine
from core.indicators import calculate_rsi

class MeanReversionEngine(BasePatternEngine):
    """
    Engine optimized for Mean Reversion (e.g., Thai Market).
    Bias: Always bet AGAINST the trend of the last candle.
    Filters: RSI Overbought/Oversold levels.
    """
    def analyze(self, df, symbol, settings):
        if df is None or len(df) < 50:
            return []
            
        close = df['close']
        pct_change = close.pct_change()
        
        # 1. INDICATORS
        rsi = calculate_rsi(close)
        current_rsi = rsi.iloc[-1]
        
        # 2. THRESHOLD LOGIC (V4.2 Hybrid)
        min_floor = settings.get('min_threshold')
        # Use BaseEngine's adaptive threshold (Max of 20d, 252d, and Floor)
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        results = []
        for length in range(self.min_len, self.max_len + 1):
            window_returns = pct_change.iloc[-length:]
            window_thresh = effective_std.iloc[-length:]
            
            pat_str = self.extract_pattern(window_returns, window_thresh)
            if not pat_str or len(pat_str) < self.min_len: continue
            
            # STRATEGIC BIAS: Mean Reversion (Fade) (Thai Market)
            # Last char '+' -> Predict DOWN (SHORT), '-' -> Predict UP (LONG)
            last_char = pat_str[-1]
            if last_char == '+':
                direction = "SHORT"
            elif last_char == '-':
                direction = "LONG"
            else:
                continue # Skip neutral patterns for reversion fade
                
            # 3. RSI VALIDATION
            # Only bet Short if Overbought, Long if Oversold
            is_rsi_valid = False
            if direction == "SHORT" and current_rsi > 70:
                is_rsi_valid = True
            elif direction == "LONG" and current_rsi < 30:
                is_rsi_valid = True
            
            # Data-Driven Validation
            future_returns = self.get_pattern_stats(close, pct_change, effective_std, pat_str, length)
            if not future_returns: continue
            
            # Use base class for standardized math
            stats = self.calculate_stats(future_returns, direction)
            
            # Final Tradeability (Thai Market: RRR and RSI Confirmation)
            is_tradeable = stats['win_rate'] >= 60 and stats['rrr'] >= 2.0 and is_rsi_valid

            results.append({
                'engine': 'MEAN_REVERSION',
                'pattern': pat_str,
                'forecast': 'UP' if direction == "LONG" else "DOWN",
                'prob': stats['win_rate'],
                'rr': stats['rrr'],
                'matches': stats['total'],
                'is_reversal': True,
                'is_tradeable': is_tradeable,
                'rsi': round(current_rsi, 1),
                'threshold': round(current_std * 100, 2)
            })
            
        return results
