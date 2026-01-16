"""
processor.py - Core Logic for Fractal N+1 Prediction (Pattern-Based Edition)
==============================================================================
Implements:
1. Pattern Detection (Find all unique patterns in history)
2. Pattern-Specific Statistics (Each pattern gets its own Prob/Stats)
3. Volatility-Based Threshold
"""

import pandas as pd
import numpy as np
import config

def analyze_asset(df):
    """
    Finds all unique patterns in history and calculates statistics for each.
    Returns a LIST of pattern results (one per unique pattern found).
    """
    try:
        if df is None or len(df) < 50:
            return []

        # ==========================================
        # 1. Volatility Calculation
        # ==========================================
        close = df['close']
        pct_change = close.pct_change()
        
        # Calculate Rolling SD
        short_term_std = pct_change.rolling(window=config.VOLATILITY_WINDOW).std()
        long_term_std = pct_change.rolling(window=252).std()
        
        # Hybrid Effective Volatility
        long_term_floor = long_term_std * 0.50
        effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
        effective_std = effective_std.fillna(short_term_std)

        current_change = pct_change.iloc[-1]
        current_std = effective_std.iloc[-1]
        current_price = close.iloc[-1]
        
        if current_std == 0 or np.isnan(current_std):
            return []

        # ==========================================
        # 2. Find All Unique Patterns in History
        # ==========================================
        pattern_occurrences = {}  # {pattern_string: [list of end indices]}
        
        history_len = len(pct_change)
        if history_len < 10:
            return []
        
        # Scan ALL history for patterns (no limit for better accuracy)
        scan_start = 5  # Start after having enough data
        threshold_series = effective_std * 2.0
        
        for i in range(scan_start, history_len):
            # Get 4-day window ending at day i
            if i < 4:
                continue
            window_returns = pct_change.iloc[i-3:i+1]  # 4 days
            window_thresh = threshold_series.iloc[i-3:i+1]
            
            # Convert to pattern string (skip quiet days)
            pattern = ""
            for ret, thresh in zip(window_returns, window_thresh):
                if pd.isna(ret) or pd.isna(thresh):
                    continue
                if ret > thresh:
                    pattern += '+'
                elif ret < -thresh:
                    pattern += '-'
            
            # Only store non-empty patterns
            if pattern and pattern != '':
                if pattern not in pattern_occurrences:
                    pattern_occurrences[pattern] = []
                pattern_occurrences[pattern].append(i)
        
        if not pattern_occurrences:
            return []
        
        # ==========================================
        # 3. Calculate Statistics for Each Pattern
        # ==========================================
        results = []
        
        for pattern_str, occurrence_indices in pattern_occurrences.items():
            # For each occurrence, check what happened the NEXT day
            future_returns = []
            
            for end_idx in occurrence_indices:
                next_idx = end_idx + 1
                if next_idx < len(close):
                    price_at_pattern_end = close.iloc[end_idx]
                    price_next_day = close.iloc[next_idx]
                    ret = (price_next_day - price_at_pattern_end) / price_at_pattern_end
                    future_returns.append(ret)
            
            # Adaptive Threshold logic
            # Pure 1-2 char patterns: Need high statistical significance (>=10 matches)
            # Complex 3+ char patterns: Rare, so we accept fewer matches (>=3 or 5)
            min_matches = 10
            if len(pattern_str) == 3:
                min_matches = 5
            elif len(pattern_str) >= 4:
                min_matches = 3
                
            if not future_returns or len(future_returns) < min_matches:
                continue
            
            # Calculate pattern-specific statistics
            bull_count = sum(1 for r in future_returns if r > 0)
            bear_count = sum(1 for r in future_returns if r < 0)
            total = len(future_returns)
            
            bull_prob = (bull_count / total) * 100
            bear_prob = (bear_count / total) * 100
            avg_return = np.mean(future_returns) * 100
            
            # Simple filter: Just need enough data (adaptive)
            results.append({
                'status': 'MATCH_FOUND',
                'symbol': 'Unknown',
                'price': current_price,
                'change_pct': current_change * 100,
                'threshold': current_std * 100,
                'pattern_display': pattern_str,
                'matches': total,
                'bull_prob': bull_prob,
                'bear_prob': bear_prob,
                'avg_return': avg_return,
                'vol_tag': 'NORMAL',
                'z_score': 0,
                'max_risk': 0
            })
        
        return results

    except Exception as e:
        return []
