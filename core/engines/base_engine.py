import pandas as pd
import numpy as np
import os
from collections import defaultdict

class BasePatternEngine:
    """
    Base class for all market-specific trading engines.
    Provides common utilities for pattern recognition and statistical analysis.
    """
    def __init__(self, min_len=1, max_len=8):
        self.min_len = min_len
        self.max_len = max_len

    def extract_pattern(self, returns, threshold):
        """Convert a series of returns and thresholds into a +/- pattern string.
        Core Logic 1: Break on neutral day (|return| < threshold).
        Mixed signs (+/-) are allowed within a streak.
        """
        pat_str = ""
        for r, t in zip(returns, threshold):
            if pd.isna(r) or pd.isna(t): break
            if r > t: pat_str += '+'
            elif r < -t: pat_str += '-'
            else: break  # Neutral day = STOP (Core Logic 1)
        return pat_str

    def get_active_pattern(self, pct_change, effective_std, max_lookback=15):
        """
        Rule 2: Dynamic Lookback — Pure Streak Extraction (Non-Fixed)
        
        Walks backwards from today, building a pattern string of ALL consecutive
        significant moves. Breaks immediately on the first 'Neutral' day.
        """
        pattern_chars = []
        
        # Increase safety lookback or remove fixed loop if strictly streak-based
        for i in range(1, max_lookback + 1):
            idx = len(pct_change) - i
            if idx < 0:
                break
                
            ret = pct_change.iloc[idx]
            thresh = effective_std.iloc[idx]
            
            if pd.isna(ret) or pd.isna(thresh):
                break
            
            # Neutral day = STOP (strict rule)
            if abs(ret) < thresh:
                break
            
            # Significant move: classify
            if ret > thresh:
                pattern_chars.append('+')
            elif ret < -thresh:
                pattern_chars.append('-')
        
        if not pattern_chars:
            return ""
        
        # Reverse because we walked backwards (most recent → oldest)
        # Pattern reads left-to-right: oldest → newest
        pattern_chars.reverse()
        return ''.join(pattern_chars)
    
    def select_best_fit(self, prices, pct_change, effective_std, active_pattern, 
                        min_count=30, direction_override=None):
        """
        Rule 3: Best Fit Sub-pattern Selection (V7.2 — Hybrid Approach)
        
        Top-Down Fallback with Confidence Tie-breaker:
        - MIN_COUNT = 30:   Bare minimum to be considered
        - STRONG_COUNT = 50: High confidence threshold
        - MIN_PROB = 55.0:  Minimum prob% to trust marginal data
        
        Algorithm (longest → shortest):
        1. Count < MIN_COUNT → skip
        2. Marginal (30 ≤ Count < 50) → store as fallback_candidate, continue
        3. Strong (Count ≥ 50):
           - No fallback → return immediately (longest + strong)
           - Has fallback → compare probs → return winner
        4. End of loop:
           - Fallback exists + prob ≥ MIN_PROB → return fallback
           - Otherwise → No Trade / Pass
        """
        if not active_pattern:
            return None
        
        STRONG_COUNT = 50   # High confidence threshold
        MIN_PROB = 55.0     # Minimum prob% for marginal-only fallback
        
        # Generate sub-patterns from longest to shortest
        # e.g., '-+-' → ['-+-', '+-', '-']
        sub_patterns = []
        for i in range(len(active_pattern)):
            sub = active_pattern[i:]
            if sub:
                sub_patterns.append(sub)
        
        fallback_candidate = None  # Stores the first marginal pattern found
        
        for sub_pat in sub_patterns:
            length = len(sub_pat)
            
            # Mode A: Overlapping sliding window scan
            future_returns = self.get_pattern_stats(
                prices, pct_change, effective_std, sub_pat, length
            )
            
            if not future_returns:
                continue
            
            count = len(future_returns)
            
            # Step 1: Count < MIN_COUNT → skip
            if count < min_count:
                continue
            
            # Determine direction from last character of sub-pattern
            last_char = sub_pat[-1]
            if direction_override:
                direction = direction_override
            else:
                direction = "LONG" if last_char == '-' else "SHORT"
            
            stats = self.calculate_stats(future_returns, direction)
            
            result = {
                'pattern': sub_pat,
                'length': length,
                'stats': stats,
                'future_returns': future_returns,
            }
            
            # Step 2: Marginal Case (30 ≤ Count < 50)
            if count < STRONG_COUNT:
                if fallback_candidate is None:
                    # First marginal pattern (longest) → store, don't commit yet
                    fallback_candidate = result
                # If fallback already set, skip shorter marginal patterns
                continue
            
            # Step 3: Strong Case (Count ≥ 50)
            if fallback_candidate is None:
                # This is the longest valid pattern AND it has strong confidence
                return result
            else:
                # Compare: shorter strong vs longer marginal fallback
                if stats['win_rate'] >= fallback_candidate['stats']['win_rate']:
                    # Shorter pattern has strong confidence AND better/equal prob
                    return result
                else:
                    # Longer fallback had better prob despite lower count
                    return fallback_candidate
        
        # Step 4: End of loop — check fallback
        if fallback_candidate:
            # Marginal-only: trust only if prob is good enough
            if fallback_candidate['stats']['win_rate'] >= MIN_PROB:
                return fallback_candidate
            # Prob too low + data too thin → not confident enough, skip
            return None
        
        # No sub-pattern met Count >= min_count → No Trade / Pass
        return None

    def aggregate_voting(self, df, pct_change, effective_std, active_pattern, min_count=30, **kwargs):
        """
        V4.4: Winner-Takes-All Per-Suffix Voting Logic.
        1. Break active_pattern into suffixes (e.g., '++-', '+-', '-')
        2. For each suffix, get historical Up/Down counts
        3. Identify the 'local winner' for that suffix
        4. Add ONLY the winner's count to the global tally
        5. Return consolidated result
        """
        if not active_pattern:
            return None
            
        total_p_weight = 0
        total_n_weight = 0
        suffix_details = []

        # Generate sub-patterns from longest to shortest
        # e.g., '++-' -> ['++-', '+-', '-']
        suffixes = []
        for i in range(len(active_pattern)):
            sub = active_pattern[i:]
            if sub:
                suffixes.append(sub)

        for sub_pat in suffixes:
            # 1. Get history for this suffix (using child-implemented get_pattern_stats)
            # Reversion: needs df, pct, std, pat, len
            # Trend: needs df, pct, std, pat, len, sma50, trend
            future_returns = self.get_pattern_stats(df, pct_change, effective_std, sub_pat, len(sub_pat), **kwargs)
            
            if not future_returns or len(future_returns) < min_count:
                continue
                
            # 2. Count P (+) and N (-)
            p_count = sum(1 for r in future_returns if r > 0)
            n_count = sum(1 for r in future_returns if r < 0)
            
            if p_count == 0 and n_count == 0:
                continue

            # 3. Global Tally (Weighted Average)
            # Sum BOTH counts into global weights to get a true statistical average
            total_p_weight += p_count
            total_n_weight += n_count
            
            # Local winner identifier for breakdown display
            if p_count > n_count:
                local_winner = 'P'
            elif n_count > p_count:
                local_winner = 'N'
            else:
                local_winner = 'TIE'
                
            suffix_details.append(f"{sub_pat}:{p_count}/{n_count}({local_winner})")

        # Handle case where no suffixes were found
        if total_p_weight == 0 and total_n_weight == 0:
            return None

        # 4. Final Aggregation
        total_weight = total_p_weight + total_n_weight
        if total_p_weight >= total_n_weight:
            forecast = 'UP'
            final_prob = (total_p_weight / total_weight) * 100
        else:
            forecast = 'DOWN'
            final_prob = (total_n_weight / total_weight) * 100

        return {
            'pattern': active_pattern,
            'forecast': forecast,
            'prob': final_prob,
            'total_p': total_p_weight,
            'total_n': total_n_weight,
            'total_events': total_weight,
            'breakdown': "; ".join(suffix_details)
        }

    def get_pattern_stats(self, prices, pct_change, effective_std, pattern_str, length, multiplier=1.0):
        """
        Mode A: Overlapping Sliding Window — Streak-based pattern counting.
        
        1. Build signal series: '+', '-', '.' for every bar
        2. Find continuous streaks (broken only by '.')
        3. Enumerate all sub-patterns within each streak
        4. If sub-pattern matches target, record N+1 future return
        
        This is consistent with generate_master_stats.py scanning logic.
        """
        n = len(pct_change)
        future_returns = []
        
        # Step 1: Build full signal series
        signals = []
        for i in range(n):
            ret = pct_change.iloc[i]
            thresh = effective_std.iloc[i] * multiplier
            
            if pd.isna(ret) or pd.isna(thresh):
                signals.append('.')
            elif ret > thresh:
                signals.append('+')
            elif ret < -thresh:
                signals.append('-')
            else:
                signals.append('.')  # Neutral
        
        # Step 2: Scan streaks (continuous non-neutral runs)
        i = 252  # Start after warmup
        while i < n - 1:  # -1 because we need N+1 return
            if signals[i] == '.':
                i += 1
                continue
            
            # Find streak boundaries
            streak_start = i
            while i < n and signals[i] != '.':
                i += 1
            streak_end = i
            
            streak_chars = signals[streak_start:streak_end]
            streak_len = len(streak_chars)
            
            # Step 3: Enumerate all sub-patterns (overlapping, step=1)
            for start_pos in range(streak_len):
                for end_pos in range(start_pos + 1, min(start_pos + 8, streak_len + 1)):
                    sub = ''.join(streak_chars[start_pos:end_pos])
                    
                    # Check if this sub-pattern matches our target
                    if sub == pattern_str:
                        # The absolute index of the last char of this sub-pattern
                        abs_idx = streak_start + end_pos - 1
                        
                        # Step 4: Record N+1 future return (if available)
                        if abs_idx + 1 < n:
                            next_ret = (prices.iloc[abs_idx + 1] - prices.iloc[abs_idx]) / prices.iloc[abs_idx]
                            future_returns.append(next_ret)
        
        return future_returns

    def calculate_dynamic_threshold(self, pct_change, min_floor=None):
        """
        Calculates the adaptive threshold based on:
        1. Case 2: 20-day Rolling SD (Adaptive)
        2. Case 1: 252-day Rolling SD (Yearly Base Floor)
        3. Config Floor: Absolute minimum move (e.g., 0.6% for US, 1.0% for Thai)
        """
        short_std = pct_change.rolling(20).std()
        long_std = pct_change.rolling(252).std()
        
        # Merge Case 1 and Case 2
        effective_std = np.maximum(short_std, long_std.fillna(0))
        
        # Apply Market Minimum Floor if provided
        if min_floor is not None:
             effective_std = np.maximum(effective_std, min_floor)
             
        return effective_std

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def calculate_rvol(self, volume, period=20):
        """
        Calculate Relative Volume (RVol)
        RVol = Current Volume / Average Volume (period)
        """
        vol_avg = volume.rolling(window=period).mean()
        # Avoid division by zero
        rvol = volume / vol_avg.replace(0, 1)
        return rvol
    
    def simulate_trailing_stop_exit(self, df, entry_idx, direction, atr_multiplier=2.0, max_hold_days=10, take_profit_pct=None):
        """
        Simulate Trailing Stop Loss Exit
        
        Args:
            df: DataFrame with 'close', 'high', 'low'
            entry_idx: Entry bar index
            direction: 1 for LONG, -1 for SHORT
            atr_multiplier: ATR multiplier for stop distance
            max_hold_days: Maximum holding period
        
        Returns:
            dict with exit_idx, exit_price, return_pct, exit_reason
        """
        if entry_idx >= len(df) - 1:
            return None
        
        entry_price = df['close'].iloc[entry_idx]
        atr_series = self.calculate_atr(df['high'], df['low'], df['close'])
        current_atr = atr_series.iloc[entry_idx]
        
        # Fallback if ATR is NaN
        if pd.isna(current_atr) or current_atr == 0:
            current_atr = entry_price * 0.02  # 2% fallback
        
        # Initial stop loss and take profit
        if direction == 1:  # LONG
            initial_stop = entry_price - (current_atr * atr_multiplier)
            trailing_stop = initial_stop
            highest_price = entry_price
            take_profit_price = entry_price * (1 + take_profit_pct / 100) if take_profit_pct else None
        else:  # SHORT
            initial_stop = entry_price + (current_atr * atr_multiplier)
            trailing_stop = initial_stop
            lowest_price = entry_price
            take_profit_price = entry_price * (1 - take_profit_pct / 100) if take_profit_pct else None
        
        # Simulate holding
        for i in range(entry_idx + 1, min(entry_idx + max_hold_days + 1, len(df))):
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            current_close = df['close'].iloc[i]
            current_atr_val = atr_series.iloc[i] if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else current_atr
            
            if direction == 1:  # LONG
                # Check Take Profit first
                if take_profit_price and current_high >= take_profit_price:
                    exit_price = take_profit_price
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                        'exit_reason': 'TAKE_PROFIT',
                        'hold_days': i - entry_idx
                    }
                
                # Update highest price
                if current_high > highest_price:
                    highest_price = current_high
                    # Update trailing stop (never goes down)
                    new_stop = highest_price - (current_atr_val * atr_multiplier)
                    trailing_stop = max(trailing_stop, new_stop)
                
                # Check if stop hit
                if current_low <= trailing_stop:
                    exit_price = trailing_stop
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                        'exit_reason': 'TRAILING_STOP',
                        'hold_days': i - entry_idx
                    }
                
                # Check if max hold days reached
                if i == entry_idx + max_hold_days:
                    exit_price = current_close
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                        'exit_reason': 'MAX_HOLD',
                        'hold_days': max_hold_days
                    }
            else:  # SHORT
                # Check Take Profit first
                if take_profit_price and current_low <= take_profit_price:
                    exit_price = take_profit_price
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                        'exit_reason': 'TAKE_PROFIT',
                        'hold_days': i - entry_idx
                    }
                
                # Update lowest price
                if current_low < lowest_price:
                    lowest_price = current_low
                    # Update trailing stop (never goes up)
                    new_stop = lowest_price + (current_atr_val * atr_multiplier)
                    trailing_stop = min(trailing_stop, new_stop)
                
                # Check if stop hit
                if current_high >= trailing_stop:
                    exit_price = trailing_stop
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                        'exit_reason': 'TRAILING_STOP',
                        'hold_days': i - entry_idx
                    }
                
                # Check if max hold days reached
                if i == entry_idx + max_hold_days:
                    exit_price = current_close
                    return {
                        'exit_idx': i,
                        'exit_price': exit_price,
                        'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                        'exit_reason': 'MAX_HOLD',
                        'hold_days': max_hold_days
                    }
        
        # End of data
        exit_price = df['close'].iloc[-1]
        return {
            'exit_idx': len(df) - 1,
            'exit_price': exit_price,
            'return_pct': ((exit_price - entry_price) / entry_price) * 100 * direction,
            'exit_reason': 'END_OF_DATA',
            'hold_days': len(df) - 1 - entry_idx
        }

    def calculate_stats(self, future_returns, direction):
        """
        Calculates performance metrics for a specific direction (LONG or SHORT).
        Returns Realized statistics based on actual trade outcomes from backtest results.
        
        Logic:
        - LONG: Profit = Price Change %
        - SHORT: Profit = - (Price Change %) <- Price drop is positive profit
        
        Realized Metrics:
        - Avg Win (%): Average percentage gain of winning trades
        - Avg Loss (%): Average percentage loss of losing trades (positive value)
        - Realized RRR: Actual Risk-Reward Ratio = Avg Win / Avg Loss
        """
        if not future_returns:
            return {'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 'rrr': 0, 'total': 0}
            
        trader_profits = []
        for ret in future_returns:
            # ret is fractional return (e.g. 0.02 for +2%)
            if direction == "LONG":
                profit = ret * 100
            else: # SHORT
                # If ret = -0.05 (Stock dropped 5%), profit = -(-5) = +5% Win
                # If ret = 0.03 (Stock rose 3%), profit = -(3) = -3% Loss
                profit = -ret * 100
            trader_profits.append(profit)
        
        # Separate trader_profits into wins (value > 0) and losses (value <= 0)
        wins = [p for p in trader_profits if p > 0]
        losses = [p for p in trader_profits if p <= 0]
        
        total = len(trader_profits)
        win_rate = (len(wins) / total * 100) if total > 0 else 0
        
        # Calculate Realized Statistics from actual trade outcomes
        # Avg Win (%): Mean of wins (default to 0 if no wins)
        avg_win = np.mean(wins) if wins else 0
        
        # Avg Loss (%): Absolute Mean of losses (default to 0 if no losses)
        # Must be a positive value representing the average loss percentage
        avg_loss = abs(np.mean(losses)) if losses else 0
        
        # Realized RRR: Actual Risk-Reward Ratio = Avg Win / Avg Loss
        # Safety Check: If avg_loss is 0, set realized_rrr to 0 to avoid division by zero
        realized_rrr = (avg_win / avg_loss) if avg_loss > 0 else 0
        
        return {
            'win_rate': win_rate,
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'rrr': round(realized_rrr, 2),  # Using realized RRR value
            'total': total
        }

    def check_trustworthy(self, stats, wr_threshold, count_threshold, rrr_threshold=None):
        """
        V5.1: Gatekeeper - ใช้แค่ WR + Count
        RRR ไม่ใช้เป็น gatekeeper แล้ว (วัดผลตอน forward testing แทน)
        แต่ยังรับ rrr_threshold เพื่อ backward compatibility (ถ้าไม่ส่ง = ไม่เช็ค)
        """
        if rrr_threshold is not None:
            # Legacy mode: เช็ค RRR ด้วย (ถ้าส่งมา)
            return (
                stats['win_rate'] >= wr_threshold and 
                stats['rrr'] >= rrr_threshold and 
                stats['total'] >= count_threshold
            )
        else:
            # V5.1: ใช้แค่ WR + Count
            return (
                stats['win_rate'] >= wr_threshold and 
                stats['total'] >= count_threshold
            )

    def analyze(self, df, settings):
        """To be implemented by specialized engines."""
        raise NotImplementedError("Each engine must implement the analyze method.")
