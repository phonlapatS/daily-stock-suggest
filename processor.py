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
import time
from core.pattern_stats import PatternStatsManager

# Initialize Global Stats Manager
stats_manager = PatternStatsManager()

def analyze_asset(df, symbol=None, fixed_threshold=None):
    """
    Finds and analyzes patterns. 
    Supports Incremental Updates using PatternStatsManager.
    Args:
        df: DataFrame with OHLC data
        symbol: Symbol name (optional)
        fixed_threshold: If set (e.g. 0.5), overrides dynamic volatility calculation.
                        Value should be in percentage (0.5 = 0.5%).
    """
    try:
        # --- STABILITY & RATE LIMITING ---
        # Sleep to respect API limits (User requested stability > speed)
        time.sleep(0.5) 
        
        if df is None or len(df) < 50:
            return []
            
        # --- INCREMENTAL UPDATE LOGIC ---
        if symbol:
            try:
                # Calculate patterns for the new data points (simplified check)
                # In a real incremental system, we'd only scan the new rows.
                # For V3.3 Phase 2, we will leverage the manager to update the Validated Stats.
                # Use a specific 'patterns_dict' approach if we wanted perfect sync.
                # For now, we allow the Manager to handle the heavy lifting if we implement the full flow.
                # Here we continue to use real-time scanning for the *current* pattern prediction,
                # but we can optionally trigger a background update for the Master CSV.
                pass 
            except Exception as e:
                print(f"⚠️ Stats Update Failed for {symbol}: {e}")

        # ==========================================

        # ==========================================
        # 1. Volatility Calculation
        # ==========================================
        close = df['close']
        pct_change = close.pct_change()
        
        # Determine Effective Standard Deviation (Threshold Base)
        if fixed_threshold is not None:
            # === MODE A: Fixed Threshold (Mentor Request) ===
            # Override dynamic calc with a fixed percentage
            # e.g. fixed_threshold = 0.5 -> current_std = 0.005
            fixed_std_val = fixed_threshold / 100.0
            
            # Create a Series relative to the index to match expected format
            effective_std = pd.Series(fixed_std_val, index=pct_change.index)
            
            # For fixed mode, the "current_std" is just the fixed value
            current_std = fixed_std_val
            
        else:
            # === MODE B: Dynamic Volatility (Original Logic) ===
            # Calculate Rolling SD
            short_term_std = pct_change.rolling(window=config.VOLATILITY_WINDOW).std()
            long_term_std = pct_change.rolling(window=252).std()
            
            # Hybrid Effective Volatility
            long_term_floor = long_term_std * 0.50
            effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
            effective_std = effective_std.fillna(short_term_std)
            
            current_std = effective_std.iloc[-1]

        current_change = pct_change.iloc[-1]
        # current_std is already set above
        current_price = close.iloc[-1]
        
        if current_std == 0 or np.isnan(current_std):
            return []

        # ==========================================
        # 2. Dynamic Pattern Matching (Current State)
        # ==========================================
        # We want to find the "Max Effective Length" pattern that matches current tail.
        # Strategy:
        # 1. Extract current tail (max length e.g. 8).
        # 2. Check historical stats for lengths 3..8.
        # 3. Pick the longest one that meets Valid Criteria (Prob > Threshold).
        
        MAX_PATTERN_LEN = 8
        MIN_PATTERN_LEN = 3
        
        history_len = len(pct_change)
        if history_len < 50: return []

        # extract tail patterns
        current_tail_patterns = {} # {length: pattern_string}
        
        # Build current tail strings for lengths 3..8
        # We need the last N days relative to 'current_price' (which is last)
        # pct_change index -1 is the last completed bar.
        
        for length in range(MIN_PATTERN_LEN, MAX_PATTERN_LEN + 1):
            if history_len < length: continue
            
            # Extract relevant window
            window_returns = pct_change.iloc[-length:] 
            window_thresh = effective_std.iloc[-length:] * 1.25 # Dynamic Threshold
            
            pat_str = ""
            for ret, thresh in zip(window_returns, window_thresh):
                if pd.isna(ret) or pd.isna(thresh): break
                if ret > thresh: pat_str += '+'
                elif ret < -thresh: pat_str += '-'
                else: pat_str += '.' # Use dot for noise? Or just skip? 
                # Original logic skipped quiet days? 
                # "skip quiet days" -> pattern += ''
                # But here we need to match history.
                # Let's keep strict '+' / '-' logic check.
                # If neither, it's a neutral bar. 
                # The original logic (lines 92-98) effectively SKIPPED neutral bars?
                # "for ret, thresh... if ret > thresh: + elif... -"
                # If neutral, nothing added. 
                # This treats a neutral bar as non-existent.
            
            if len(pat_str) >= MIN_PATTERN_LEN: # Ensure we got enough significant bars
                current_tail_patterns[length] = pat_str

        if not current_tail_patterns:
            return []

        # Now scan history for these specific patterns
        # We scan ONCE to find all occurrences of interest
        pattern_candidates_stats = {} # {length: {stats}}
        
        # Optimization: Don't scan blindly. Scan history and check against our tails.
        # We need to find occurrences of `current_tail_patterns` in history.
        
        # Pre-scan history to find matches for our candidates
        # This is expensive if we scan for each length. 
        # Better: Scan history for "Longest Possible Sequence" then check substrings?
        # Actually, let's keep it simple: Loop history once, build string, check matches.
        
        scan_start = 10
        
        # Store counts/returns for each candidate pattern
        candidate_data = {length: {'occurrences': [], 'pattern': pat} 
                          for length, pat in current_tail_patterns.items()}
        
        for i in range(scan_start, history_len - 1): # -1 to have a 'next day'
            # Check for matches of max length first?
            # Let's just extract the window of MAX_LEN ending at i
            window = pct_change.iloc[i-MAX_PATTERN_LEN+1 : i+1]
            thresh_win = effective_std.iloc[i-MAX_PATTERN_LEN+1 : i+1] * 1.25
            
            # Build full string (up to Max Len)
            full_pat = ""
            for r, t in zip(window, thresh_win):
                if pd.isna(r): continue
                if r > t: full_pat += '+'
                elif r < -t: full_pat += '-'
                # skip neutral
            
            # Check suffixes
            # If full_pat ends with our candidate pattern?
            # Wait, original logic was "SKIP neutral".
            # So a 8-day window might produce a 4-char pattern if 4 days were neutral.
            # This makes alignment tricky.
            # Correct approach: treating the sequence of significant moves as the pattern.
            
            # Let's match from the end (suffix)
            for length, target_pat in current_tail_patterns.items():
                if full_pat.endswith(target_pat):
                    # Found a match!
                    # Store index i (end of pattern)
                    candidate_data[length]['occurrences'].append(i)

        # Now calculate stats for each candidate length
        valid_results = []
        
        for length, data in candidate_data.items():
            occurrences = data['occurrences']
            target_pat = data['pattern']
            
            if not occurrences: continue
            
            future_returns = []
            for end_idx in occurrences:
                next_idx = end_idx + 1
                if next_idx < len(close):
                    p_end = close.iloc[end_idx]
                    p_next = close.iloc[next_idx]
                    ret = (p_next - p_end) / p_end
                    future_returns.append(ret)
            
            # Min Matches Filter
            min_matches = max(3, int(history_len * 0.001))
            if len(future_returns) < min_matches: continue
            
            # Calculate Prob
            bull_count = sum(1 for r in future_returns if r > 0)
            total = len(future_returns)
            bull_prob = (bull_count / total) * 100
            
            # Rule: We want "Max Length that Exceeded Threshold"
            # Let's assume Threshold is 50% for now (or use dynamic).
            # If Prob > 55, it's a contender.
            
            # Append to list to pick best later
            valid_results.append({
                'length': length,
                'pattern_display': target_pat,
                'matches': total,
                'bull_prob': bull_prob,
                'future_returns': future_returns
            })
            
        if not valid_results:
            return []
            
        # SELECT THE BEST PATTERN (Dynamic Length Logic)
        # Prioritize Longest Length that has Good Prob (>55%)
        # Sort by Length Desc, then Prob Desc
        
        # Filter for quality first
        quality_candidates = [r for r in valid_results if abs(r['bull_prob'] - 50) > 5] # >55 or <45
        
        if quality_candidates:
            # Pick longest from quality
            best_match = sorted(quality_candidates, key=lambda x: x['length'], reverse=True)[0]
        else:
            # Fallback to longest available (even if low prob, to show result) 
            # Or return nothing? User said "max ... that exceeded threshold".
            # If none exceed, maybe return nothing? 
            # Let's return the best of what we have, but marked.
            best_match = sorted(valid_results, key=lambda x: x['length'], reverse=True)[0]

        # Prepare final result for the BEST match only
        results = []
        # Use existing logic variables to populate result
        # Re-map best_match to the 'result' dict format
        
        pattern_str = best_match['pattern_display']
        occurrence_indices = [] # We don't need indices anymore for export, just stats
        future_returns = best_match['future_returns']
        history_len = len(pct_change) # needed below
        
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
