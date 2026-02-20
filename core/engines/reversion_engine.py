import numpy as np
import pandas as pd
from .base_engine import BasePatternEngine

class MeanReversionEngine(BasePatternEngine):
    """
    Engine optimized for Mean Reversion (Thai SET, China/HK HKEX).
    
    Core Philosophy: Volatility-Based Anomaly Detection
    - Signal = Price move exceeds Dynamic SD Threshold
    - Direction = FADE (bet against the anomaly move)
    - NO RSI filter (V5.0: removed - conflicts with core concept)
    - Strict Gatekeeper at the end ensures quality
    """
    def analyze(self, df, symbol, settings):
        if df is None or len(df) < 50:
            return []
            
        open_price = df['open']
        close = df['close']
        volume = df['volume']
        
        # STRICT INTRADAY LOGIC: (Close - Open) / Open
        # Measures "Candle Body Strength" (Who won the day?)
        pct_change = ((close - open_price) / open_price)
        
        exchange = settings.get('exchange', '').upper()
        
        # Market Detection
        is_thai = any(ex in exchange for ex in ['SET', 'MAI', 'TH'])
        is_china = any(ex in exchange for ex in ['HKEX', 'SHSE', 'SZSE', 'CHINA'])
        
        # 1. INDICATORS (No RSI - pure SD approach)
        # CN Specific Indicators
        sma50 = close.rolling(50).mean()
        vol_avg_20 = volume.rolling(20).mean()
        vr = (volume.iloc[-1] / vol_avg_20.iloc[-1]) if vol_avg_20.iloc[-1] > 0 else 1.0
        
        # 2. THRESHOLD LOGIC (Dynamic SD with Market Floor)
        min_floor = 0.01 if is_thai else 0.005  # TH: 1.0%, CN: 0.5%
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        # Gate: If today's move is within threshold, no anomaly detected
        if abs(pct_change.iloc[-1]) < current_std:
            return []
            
        results = []
        for length in range(self.min_len, self.max_len + 1):
            window_returns = pct_change.iloc[-length:]
            window_thresh = effective_std.iloc[-length:]
            
            pat_str = self.extract_pattern(window_returns, window_thresh)
            if not pat_str or len(pat_str) < self.min_len:
                continue
            
            # 4. DATA-DRIVEN VALIDATION (Dynamic Direction)
            # Compare LONG vs SHORT performance
            # Note: get_pattern_stats needs open price for future return calc
            # But get_pattern_stats signature expects prices, pct_change...
            # We need to ensure get_pattern_stats uses Intraday Return for Future Profit too!
            
            # Since get_pattern_stats is in base_engine (or overridden?), let's check.
            # BaseEngine.get_pattern_stats typically uses (price[i+1]-price[i])/price[i].
            # We need to Override it or pass a specialized price series?
            # Actually, let's look at BasePatternEngine.get_pattern_stats.
            
            # For now, let's pass a 'prices' argument that helps calculate Intraday Return?
            # No, standard prices are close.
            
            # If we want N+1 Intraday Return, we need Open and Close of N+1.
            # BasePatternEngine.get_pattern_stats might not support this directly if it only takes 'prices'.
            
            # Solution: We should override get_pattern_stats in this engine or modify base?
            # Or simpler: Is 'pct_change' series enough?
            # BasePatternEngine.get_pattern_stats logic:
            # next_ret = (prices.iloc[abs_idx + 1] - prices.iloc[abs_idx]) / prices.iloc[abs_idx]
            # This is Inter-day! 
            
            # CRITICAL: We need to pass a "Future Return Series" to get_pattern_stats instead of raw prices.
            # But get_pattern_stats calculates it internally.
            
            # WAITING: Check BasePatternEngine first?
            # Assuming I can't see base right now.
            # Let's Implement a local get_pattern_stats if needed.
            
            # Actually, we can pass "Open" and "Close" to a modified get_pattern_stats?
            # Or... we can cheat. 
            # If we pass 'prices' as a list of objects? No.
            
            # Let's stick to updating the CALL first.
            future_returns = self.get_pattern_stats_intraday(df, pct_change, effective_std, pat_str, length)
            
            if not future_returns:
                continue
            
            # Test both directions
            stats_long = self.calculate_stats(future_returns, "LONG")
            stats_short = self.calculate_stats(future_returns, "SHORT")
            
            # Select winner
            if stats_long['win_rate'] >= stats_short['win_rate']:
                direction = "LONG"
                stats = stats_long
            else:
                direction = "SHORT"
                stats = stats_short
                
            # Filter Loop Continue equivalent (previously continued if loop didn't match)
            # Now we always have a direction, so we proceed to filtering.
                
            # 3. MARKET-SPECIFIC FILTERS (No RSI — only structural filters)
            filter_tags = []
            
            if is_china:
                # Volume Ratio (VR) Filter: Skip dead liquidity zones
                if vr < 0.5:
                    continue  # Dead Zone — no liquidity
                if vr > 3.0:
                    filter_tags.append("FOMO_REVERSION")
                
                # Regime Filter: LONG only if Price > SMA50 (healthy uptrend)
                if direction == "LONG" and close.iloc[-1] < sma50.iloc[-1]:
                    continue
                
            # (Stats already calculated above in Dynamic step)
            
            # 5. QUALITY FLAG (V5.2: Late Filtering)
            # -------------------------------------------------------
            # คืนทุก pattern ที่เกิน threshold (ไม่ filter)
            # is_tradeable = quality flag สำหรับ sorting/display เท่านั้น
            # Forward testing จะเป็นคนตัดสินว่า pattern ไหนดีจริงๆ
            # -------------------------------------------------------
            if is_thai:
                is_tradeable = self.check_trustworthy(stats, 60.0, 30)  # WR≥60%, Count≥30
            elif is_china:
                is_tradeable = self.check_trustworthy(stats, 60.0, 15)  # WR≥60%, Count≥15
            else:
                is_tradeable = self.check_trustworthy(stats, 60.0, 15)  # WR≥60%, Count≥15
            
            # CN Volatility Targeting: position size scalar = 2% / Daily_Volatility
            vol_target_size = None
            if is_china:
                vol_target_size = round(2.0 / (current_std * 100), 2)

            # V5.2: Return ALL patterns (no filtering here - late filtering in report)
            results.append({
                'engine': 'MEAN_REVERSION',
                'pattern': pat_str,
                'forecast': 'UP' if direction == "LONG" else "DOWN",
                'prob': stats['win_rate'],
                'rr': stats['rrr'],
                'matches': stats['total'],
                'avg_win': stats['avg_win'],
                'avg_loss': stats['avg_loss'],
                'is_reversal': True,
                'is_tradeable': is_tradeable,  # Quality flag only (not a gatekeeper)
                'threshold': round(current_std * 100, 2),
                'vr': round(vr, 2),
                'filter_tags': filter_tags,
                'vol_target_size': vol_target_size
            })
            
        return results

    def get_pattern_stats_intraday(self, df, pct_change, effective_std, pattern_str, length):
        """
        Custom Intraday version of get_pattern_stats.
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
        # Match base_engine logic (Start at min scan index)
        start_idx = math.ceil(max(50, length)) # Ensure enough history
        # Correct import
        import math
        start_idx = 252 # Use standard warmup
        
        # Naive Loop for exact match (Simpler than streak logic for this override, or copy streak logic?)
        # Let's copy the strict logic from base_engine to be safe, but simplified for exact pattern match
        
        # We need to find ALL occurrences of pattern_str
        # A simple sliding window is easiest and correct for Exact Match
        
        target_len = len(pattern_str)
        
        for i in range(start_idx, n - 1): # -1 for next day
             # Extract pattern ending at i
             # Slice: [i-target_len+1 : i+1]
             if i - target_len + 1 < 0: continue
             
             window_sigs = signals[i-target_len+1 : i+1]
             # Check for any neutral? 
             # Base logic: "Streak" implies no neutrals.
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
