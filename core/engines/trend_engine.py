import pandas as pd
from .base_engine import BasePatternEngine
from core.indicators import calculate_adx, calculate_volume_adv

class TrendMomentumEngine(BasePatternEngine):
    """
    Engine optimized for Trend Following & Momentum (US NASDAQ, Taiwan TWSE).
    
    Core Philosophy: Volatility-Based Anomaly Detection
    - Signal = Price move exceeds Dynamic SD Threshold
    - Direction = FOLLOW (ride the momentum)
    - ADX >= 20 required (must be in a trending environment)
    - US Market: LONG ONLY
    - Regime Context: Historical stats only compare same-trend events
    - Strict Gatekeeper at the end ensures quality
    """
    def analyze(self, df, symbol, settings):
        if df is None or len(df) < 50:
            return []
            
        open_price = df['open']
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # STRICT INTRADAY LOGIC: (Close - Open) / Open
        # Measures "Candle Body Strength" (Who won the day?)
        pct_change = ((close - open_price) / open_price)
        
        exchange = settings.get('exchange', '').upper()
        
        # Market Detection
        is_us = any(ex in exchange for ex in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX'])
        is_tw = any(ex in exchange for ex in ['TWSE', 'TW'])
        
        # 1. ADX FILTER (Pre-scan: Must be trending)
        adx = calculate_adx(high, low, close)
        current_adx = adx.iloc[-1]
        
        if (is_us or is_tw) and current_adx < 20:
            return []

        # 2. TREND CONTEXT (for Regime-Aware history scan)
        sma50 = close.rolling(50).mean()
        current_trend = "BULL" if close.iloc[-1] > sma50.iloc[-1] else "BEAR"
        
        # 3. THRESHOLD LOGIC (Dynamic SD with Market Floor)
        min_floor = 0.006 if is_us else 0.005  # US: 0.6%, TW: 0.5%
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        # Gate: If today's move is within threshold, no anomaly detected
        if abs(pct_change.iloc[-1]) < current_std:
            return []
            
        # =====================================================
        # Rule 2: Dynamic Lookback — Get Active Pattern
        # (Cut at neutral day, only + and - characters)
        # =====================================================
        active_pattern = self.get_active_pattern(pct_change, effective_std)
        if not active_pattern:
            return []  # No active streak → no signal
        
        # Determine direction from LAST character
        # Trend Following: RIDE the momentum
        # + (Up anomaly) → LONG, - (Down anomaly) → SHORT
        last_char = active_pattern[-1]
        if last_char == '+':
            direction = "LONG"
        elif last_char == '-':
            direction = "SHORT"
        else:
            return []
            
        # US Market: LONG ONLY — ignore short signals
        if is_us and direction == "SHORT":
            return []
        
        # Volume context (informational tagging)
        vol_adv = calculate_volume_adv(volume)
        current_vol = volume.iloc[-1]
        current_adv = vol_adv.iloc[-1]
        
        filter_tags = []
        if is_us or is_tw:
            filter_tags.append("ADX_FILTER")
        
        is_vol_spike = current_vol > (current_adv * 1.25)
        
        # =====================================================
        # Rule 3: Best Fit Selection (V7.2 — Hybrid Approach)
        # Generate sub-patterns → query history in SAME trend regime
        # Hybrid: Longest Context First + Confidence Tie-breaker
        # Note: Lower thresholds for trend engine (regime-filtered = less data)
        # =====================================================
        TREND_MIN_COUNT = 15     # Bare minimum for trend-filtered data
        TREND_STRONG_COUNT = 30  # Strong confidence for trend-filtered
        MIN_PROB = 55.0          # Minimum prob% for marginal fallback
        
        sub_patterns = []
        for i in range(len(active_pattern)):
            sub = active_pattern[i:]
            if sub:
                sub_patterns.append(sub)
        
        fallback_candidate = None
        
        for sub_pat in sub_patterns:
            length = len(sub_pat)
            
            # Context-Aware History Scan (same trend regime = Apples to Apples)
            # Pass df to get Open/Close for Intraday Return
            future_returns = self.get_pattern_stats(
                df, pct_change, effective_std, sub_pat, length, sma50, current_trend
            )
            if not future_returns:
                continue
            
            count = len(future_returns)
            if count < TREND_MIN_COUNT:
                continue
            
            stats = self.calculate_stats(future_returns, direction)
            
            result = {
                'pattern': sub_pat,
                'length': length,
                'stats': stats,
            }
            
            # Marginal Case (15 ≤ Count < 30 for trend)
            if count < TREND_STRONG_COUNT:
                if fallback_candidate is None:
                    fallback_candidate = result
                continue
            
            # Strong Case (Count ≥ 30 for trend)
            if fallback_candidate is None:
                best_result = result
            elif stats['win_rate'] >= fallback_candidate['stats']['win_rate']:
                best_result = result
            else:
                best_result = fallback_candidate
            break
        else:
            # Loop finished without Strong — check fallback
            if fallback_candidate and fallback_candidate['stats']['win_rate'] >= MIN_PROB:
                best_result = fallback_candidate
            else:
                best_result = None
        
        if not best_result:
            return []
        
        pat_str = best_result['pattern']
        stats = best_result['stats']
        
        # Quality Flag (V5.2: Late Filtering)
        is_tradeable = self.check_trustworthy(stats, 60.0, 15)  # WR≥60%, Count≥15
        
        # Rule 1: Return SINGLE best-fit result (anti-overlapping)
        results = [{
            'engine': 'TREND_MOMENTUM',
            'pattern': pat_str,
            'forecast': 'UP' if direction == "LONG" else "DOWN",
            'prob': stats['win_rate'],
            'rr': stats['rrr'],
            'matches': stats['total'],
            'avg_win': stats['avg_win'],
            'avg_loss': stats['avg_loss'],
            'is_trend_follow': True,
            'is_tradeable': is_tradeable,
            'adx': round(current_adx, 1),
            'vol_spike': is_vol_spike,
            'threshold': round(current_std * 100, 2),
            'filter_tags': filter_tags,
            'vol_target_size': None
        }]
            
        return results

    def get_pattern_stats(self, df, pct_change, effective_std, pattern_str, length, sma50, current_trend):
        """
        Regime-Aware History Scan (Mode A: Overlapping Sliding Window).
        
        Uses streak-based scanning consistent with Core Logic 1:
        1. Build signal series: '+', '-', '.' for every bar
        2. Find continuous streaks (broken only by '.')
        3. Enumerate all sub-patterns within each streak
        4. Only count matches in the SAME trend context (BULL/BEAR)
        
        This ensures "Apples to Apples" comparison with proper streak detection.
        """
        n = len(pct_change)
        future_returns = []
        
        pct_arr = pct_change.values
        eff_std_arr = effective_std.values
        open_arr = df['open'].values
        close_arr = df['close'].values
        
        # Step 1: Build full signal series
        signals = []
        for i in range(n):
            ret = pct_arr[i]
            thresh = eff_std_arr[i]
            
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
                        
                        # Regime filter: only count if same trend context
                        if not pd.isna(sma50.iloc[abs_idx]):
                            hist_trend = "BULL" if close_arr[abs_idx] > sma50.iloc[abs_idx] else "BEAR"
                            if hist_trend != current_trend:
                                continue
                        
                        # Step 4: Record N+1 Intraday Return
                        if abs_idx + 1 < n:
                            next_o = open_arr[abs_idx + 1]
                            next_c = close_arr[abs_idx + 1]
                            next_ret = (next_c - next_o) / next_o
                            future_returns.append(next_ret)
        
        return future_returns
