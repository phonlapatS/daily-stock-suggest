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
        
        # STRICT INTRADAY LOGIC
        pct_change = ((close - open_price) / open_price)
        exchange = settings.get('exchange', '').upper()
        
        is_us = any(ex in exchange for ex in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX'])
        is_tw = any(ex in exchange for ex in ['TWSE', 'TW'])
        
        # 1. ADX FILTER
        adx = calculate_adx(high, low, close)
        current_adx = adx.iloc[-1]
        if (is_us or is_tw) and current_adx < 20:
            return []

        # 2. TREND CONTEXT
        sma50 = close.rolling(50).mean()
        current_trend = "BULL" if close.iloc[-1] > sma50.iloc[-1] else "BEAR"
        
        # 3. THRESHOLD LOGIC
        min_floor = 0.006 if is_us else 0.005
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        if abs(pct_change.iloc[-1]) < current_std:
            return []
            
        active_pattern = self.get_active_pattern(pct_change, effective_std)
        if not active_pattern:
            return []

        # =====================================================
        # V4.4: AGGREGATE VOTING (Winner-Takes-All)
        # =====================================================
        vote_result = self.aggregate_voting(
            df, pct_change, effective_std, active_pattern, min_count=30,
            sma50=sma50, current_trend=current_trend
        )
        
        if not vote_result:
            return []

        # Quality Flag
        stats_mock = {'win_rate': vote_result['prob'], 'total': vote_result['total_events']}
        is_tradeable = self.check_trustworthy(stats_mock, 60.0, 15)

        results = [{
            'engine': 'TREND_MOMENTUM',
            'pattern': active_pattern,
            'forecast': vote_result['forecast'],
            'prob': vote_result['prob'],
            'total_p': vote_result['total_p'],
            'total_n': vote_result['total_n'],
            'total_events': vote_result['total_events'],
            'breakdown': vote_result['breakdown'],
            'is_trend_follow': True,
            'is_tradeable': is_tradeable,
            'adx': round(current_adx, 1),
            'threshold': round(current_std * 100, 2),
            'vol_target_size': None,
            'rr': 1.0
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
