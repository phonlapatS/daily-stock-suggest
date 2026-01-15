"""
processor.py - Core Logic for Fractal N+1 Prediction
====================================================
Implements:
1. Volatility Tagging (Z-Score)
2. Fractal Pattern Matching (Pearson)
3. Smart Direction Prediction (Unbiased)
"""

import pandas as pd
import numpy as np
from scipy.stats import zscore
import config

def analyze_asset(df):
    """
    Performs full technical & fractal analysis on the dataframe.
    Returns a dictionary of results or None if failed.
    """
    try:
        if df is None or len(df) < 50:
            return None

        # ==========================================
        # 1. Volatility Classification (Z-Score)
        # ==========================================
        close = df['close']
        pct_change = close.pct_change()
        
        # Calculate Rolling SD (20 periods)
        rolling_mean = pct_change.rolling(window=config.VOLATILITY_WINDOW).mean()
        rolling_std = pct_change.rolling(window=config.VOLATILITY_WINDOW).std()
        
        current_change = pct_change.iloc[-1]
        current_std = rolling_std.iloc[-1]
        
        # Avoid division by zero
        if current_std == 0 or np.isnan(current_std):
            z_score_val = 0
        else:
            # Z-Score = (Current - Mean) / SD
            # Simplified: (Current Change) / SD  (Assuming mean ~ 0 for short term)
            z_score_val = current_change / current_std

        # Tagging
        abs_z = abs(z_score_val)
        if abs_z > 1.5:
            vol_tag = "HIGH_VOLATILITY"
        else:
            vol_tag = "LOW_VOLATILITY"

        # ==========================================
        # 2. Fractal Pattern Matching
        # ==========================================
        SEQ_LEN = config.FRACTAL_WINDOW
        
        # Extract current sequence & normalize
        current_seq = close.iloc[-SEQ_LEN:].values
        if len(current_seq) < SEQ_LEN: return None
        
        curr_mean = np.mean(current_seq)
        curr_std_seq = np.std(current_seq)
        
        if curr_std_seq == 0: return None
        current_seq_norm = (current_seq - curr_mean) / curr_std_seq

        # Sliding Window (Vectorized)
        history = close.values[:-1] # Exclude today
        if len(history) < SEQ_LEN + 1: return None
            
        windows = np.lib.stride_tricks.sliding_window_view(history, SEQ_LEN)
        w_mean = np.mean(windows, axis=1, keepdims=True)
        w_std = np.std(windows, axis=1, keepdims=True)
        
        valid_mask = w_std.flatten() > 0
        windows = windows[valid_mask]
        w_mean = w_mean[valid_mask]
        w_std = w_std[valid_mask]
        indices = np.arange(len(history) - SEQ_LEN + 1)[valid_mask]
        
        windows_norm = (windows - w_mean) / w_std
        corr = np.dot(windows_norm, current_seq_norm) / SEQ_LEN
        
        # Filter Matches
        match_mask = corr >= config.MIN_CORRELATION
        match_indices = indices[match_mask]
        match_scores = corr[match_mask]
        
        if len(match_indices) == 0:
            return {
                'vol_tag': vol_tag, 
                'z_score': z_score_val, 
                'status': 'NO_MATCH',
                'price': close.iloc[-1]
            }

        # Top Matches
        sorted_idx_locs = np.argsort(match_scores)[::-1][:config.TOP_MATCHES]
        top_indices = match_indices[sorted_idx_locs]
        
        # ==========================================
        # 3. Smart Direction Logic (Enhanced)
        # ==========================================
        future_returns = []
        max_drawdowns = []
        
        for idx in top_indices:
            next_day_idx = idx + SEQ_LEN
            if next_day_idx < len(history):
                # Calculate simple return of the NEXT candle/day
                price_after = history[next_day_idx]
                price_end_match = history[next_day_idx - 1]
                ret = (price_after - price_end_match) / price_end_match
                future_returns.append(ret)
                
                # Simple Risk Estimate (Worst move in next 5 days for this match)
                # Look ahead up to 5 days
                lookahead_prices = history[next_day_idx:min(next_day_idx+5, len(history))]
                if len(lookahead_prices) > 0:
                    min_price = np.min(lookahead_prices)
                    dd = (min_price - price_end_match) / price_end_match
                    max_drawdowns.append(min(0, dd)) # Only count negative moves

        if not future_returns:
            return {'vol_tag': vol_tag, 'z_score': z_score_val, 'status': 'NO_DATA'}

        if not future_returns:
            return {'vol_tag': vol_tag, 'z_score': z_score_val, 'status': 'NO_DATA'}

        # Probability Calculation
        bull_count = sum(1 for r in future_returns if r > 0)
        bear_count = sum(1 for r in future_returns if r < 0)
        total = len(future_returns)
        
        bull_prob = (bull_count / total) * 100
        bear_prob = (bear_count / total) * 100
        avg_return = np.mean(future_returns) * 100
        max_risk = np.min(max_drawdowns) * 100 if max_drawdowns else 0.0
        
        # Streak Calculation (V2 Logic)
        streak = 0
        streak_status = "Quiet"
        try:
            curr_close = close.iloc[-1]
            prev_close = close.iloc[-2]
            diff = curr_close - prev_close
            
            if diff > 0: # UP
                streak = 1
                for i in range(2, 6):
                    if close.iloc[-i] > close.iloc[-i-1]: streak += 1
                    else: break
            elif diff < 0: # DOWN
                streak = -1
                for i in range(2, 6):
                    if close.iloc[-i] < close.iloc[-i-1]: streak -= 1
                    else: break
            
            # Formatted String for Main.py to use or override
            if streak > 0: streak_status = f"Up {streak}"
            elif streak < 0: streak_status = f"Down {abs(streak)}"
            else: streak_status = "Quiet"
                 
        except:
             streak_status = "Unknown"

        return {
            'status': 'MATCH_FOUND',
            'symbol': 'Unknown', 
            'price': close.iloc[-1],
            'change_pct': current_change * 100,
            'vol_tag': vol_tag,
            'z_score': z_score_val,
            'matches': len(match_indices),
            'avg_return': avg_return,
            'bull_prob': bull_prob,
            'bear_prob': bear_prob,
            'threshold': current_std * 100,
            'streak': streak,
            'streak_status': streak_status,
            'max_risk': max_risk
        } # End Return

    except Exception as e:
        # print(f"Error in processor: {e}") 
        return None
