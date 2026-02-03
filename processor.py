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
        threshold_series = effective_std * 1.25  # ปรับเป็น 1.25 SD เพื่อลด overfitting
        
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
            
            # Flexible Min Matches: อย่างน้อย 0.1% ของข้อมูล หรือ 3 ครั้ง
            min_matches = max(3, int(history_len * 0.001))  # 5000 bars × 0.001 = 5
                
            if not future_returns or len(future_returns) < min_matches:
                continue
            
            # 4. Advanced Statistics Calculation
            bull_count = sum(1 for r in future_returns if r > 0)
            bear_count = sum(1 for r in future_returns if r < 0)
            total = len(future_returns)
            
            bull_prob = (bull_count / total) * 100
            bear_prob = (bear_count / total) * 100
            
            # Avg Return (Expected Value)
            avg_return = np.mean(future_returns) * 100
            
            # === NEW: Mentor Metrics (Phase 1.5) ===
            # Determine forecast direction based on last character of pattern
            last_char = pattern_str[-1] if pattern_str else '+'
            forecast_dir = 1 if last_char == '+' else -1
            
            # Separate wins and losses based on forecast direction
            wins = [r for r in future_returns if (r > 0 and forecast_dir == 1) or (r < 0 and forecast_dir == -1)]
            losses = [r for r in future_returns if (r <= 0 and forecast_dir == 1) or (r >= 0 and forecast_dir == -1)]
            
            # Avg Win % (average gain when prediction is correct)
            avg_win_pct = abs(np.mean(wins)) * 100 if wins else 0
            
            # Avg Loss % (average loss when prediction is wrong)
            avg_loss_pct = abs(np.mean(losses)) * 100 if losses else 0
            
            # RR Ratio (Risk/Reward) = Avg Win / Avg Loss
            rr_ratio = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else float('inf')
            # === END Mentor Metrics ===
            
            # Max Risk (CVaR: Avg of worst 10% returns)
            negative_returns = [r for r in future_returns if r < 0]
            if negative_returns:
                # worst 10%
                k = max(1, int(len(negative_returns) * 0.10))
                worst_loss = sorted(negative_returns)[:k]
                max_risk = np.mean(worst_loss) * 100
            else:
                max_risk = 0

            # Confidence Score (0-100%)
            # Logic: Base probability * Sample Size Weight
            # Sample Size Weight: log2(matches) / log2(100) -> 10 matches=33%, 30=50%, 100=100%
            prob_score = abs(bull_prob - 50) * 2  # Scale 50-100% to 0-100
            
            # Logarithmic sample weighting (diminishing returns after 100 matches)
            sample_weight = min(1.0, np.log2(total) / np.log2(100))
            
            confidence = prob_score * sample_weight
            
            results.append({
                'status': 'MATCH_FOUND',
                'symbol': 'Unknown',
                'price': current_price,
                'change_pct': current_change * 100,
                'threshold': current_std * 100,
                'pattern_display': pattern_str,
                'matches': total,
                'total_bars': history_len,
                'bull_prob': bull_prob,
                'bear_prob': bear_prob,
                'avg_return': avg_return,
                'avg_win_pct': round(avg_win_pct, 2),
                'avg_loss_pct': round(avg_loss_pct, 2),
                'rr_ratio': round(rr_ratio, 2),
                'conf': confidence,
                'max_risk': max_risk
            })
        
        return results

    except Exception as e:
        return []
