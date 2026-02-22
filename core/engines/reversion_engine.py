import numpy as np
import pandas as pd
import math
from .base_engine import BasePatternEngine

class MeanReversionEngine(BasePatternEngine):
    """
    Engine optimized for Mean Reversion (Thai SET, China/HK HKEX).
    
    Core Philosophy: Volatility-Based Anomaly Detection
    - Signal = Price move exceeds Dynamic SD Threshold
    - Direction = FADE (bet against the anomaly move)
    - Strict Gatekeeper at the end ensures quality
    """
    def analyze(self, df, symbol, settings):
        if df is None or len(df) < 50:
            return []
            
        open_price = df['open']
        close = df['close']
        volume = df['volume']
        
        # STRICT INTRADAY LOGIC
        pct_change = ((close - open_price) / open_price)
        exchange = settings.get('exchange', '').upper()
        
        # Market Detection
        is_thai = any(ex in exchange for ex in ['SET', 'MAI', 'TH'])
        is_china = any(ex in exchange for ex in ['HKEX', 'SHSE', 'SZSE', 'CHINA'])
        
        # 2. THRESHOLD LOGIC
        min_floor = 0.01 if is_thai else 0.005
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        if abs(pct_change.iloc[-1]) < current_std:
            return []
            
        # =====================================================
        # Rule 2: Dynamic Lookback — Get Active Pattern
        # =====================================================
        active_pattern = self.get_active_pattern(pct_change, effective_std)
        if not active_pattern:
            return []
 
        # =====================================================
        # V4.4: AGGREGATE VOTING (Winner-Takes-All)
        # =====================================================
        min_matches = settings.get('min_matches', 30)
        vote_result = self.aggregate_voting(df, pct_change, effective_std, active_pattern, min_count=min_matches)
        
        if not vote_result:
            return []
 
        # 4. QUALITY FLAG
        stats_mock = {'win_rate': vote_result['prob'], 'total': vote_result['total_events']}
        is_tradeable = self.check_trustworthy(stats_mock, 60.0, min_matches)
 
        results = [{
            'engine': 'MEAN_REVERSION',
            'pattern': active_pattern,
            'forecast': vote_result['forecast'],
            'prob': vote_result['prob'],
            'total_p': vote_result['total_p'],
            'total_n': vote_result['total_n'],
            'total_events': vote_result['total_events'],
            'winning_count': vote_result['winning_count'],
            'avg_return': vote_result['avg_return'],
            'breakdown': vote_result['breakdown'],
            'is_reversal': True,
            'is_tradeable': is_tradeable,
            'threshold': round(current_std * 100, 2),
            'change_pct': round(pct_change.iloc[-1] * 100, 2),
            'rr': 1.0
        }]
        
        return results

    def get_pattern_stats(self, df, pct_change, effective_std, pattern_str, length, **kwargs):
        """
        V4.3/V4.4: Standardized Intraday History Scan for Mean Reversion.
        Calculates Profit based on (NextClose - NextOpen)/NextOpen
        """
        n = len(pct_change)
        future_returns = []
        
        # Prepare arrays
        pct_arr = pct_change.values
        thresh_arr = effective_std.values
        open_arr = df['open'].values
        close_arr = df['close'].values
        
        # Step 1: Build full signal series
        signals = []
        for i in range(n):
            ret = pct_arr[i]
            thresh = thresh_arr[i]
            
            if np.isnan(ret) or np.isnan(thresh):
                signals.append('.')
            elif ret > thresh:
                signals.append('+')
            elif ret < -thresh:
                signals.append('-')
            else:
                signals.append('.')  # Neutral
        
        # Step 2: Scan streaks
        start_idx = 252 # Use standard warmup
        target_len = len(pattern_str)
        
        for i in range(start_idx, n - 1): # -1 for next day
             if i - target_len + 1 < 0: continue
             
             window_sigs = signals[i-target_len+1 : i+1]
             if '.' in window_sigs:
                 continue
                  
             current_pat = "".join(window_sigs)
             
             if current_pat == pattern_str:
                  # MATCH FOUND
                  # Calculate N+1 Intraday Return
                  next_o = open_arr[i+1]
                  next_c = close_arr[i+1]
                  next_ret = (next_c - next_o) / next_o
                  future_returns.append(next_ret)
                  
        return future_returns
