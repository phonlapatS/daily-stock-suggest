from .base_engine import BasePatternEngine
from core.indicators import calculate_adx, calculate_volume_adv

class TrendMomentumEngine(BasePatternEngine):
    """
    Engine optimized for Trend Following and Momentum (e.g., US Market).
    Bias: Always follow the trend of the last candle.
    Filters: ADX Trend Strength, Volume Spike.
    """
    def analyze(self, df, symbol, settings):
        if df is None or len(df) < 50:
            return []
            
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        pct_change = close.pct_change()
        
        # 1. ADX FILTER (PRE-SCAN)
        adx = calculate_adx(high, low, close)
        current_adx = adx.iloc[-1]
        if current_adx < 20: # Relaxed from 25 to 20 (V4.2 Optimization)
            return []  # No Trend, No Trade (Abort early for efficiency)
            
        # 2. THRESHOLD LOGIC (V4.2 Hybrid)
        min_floor = settings.get('min_threshold')
        # Use BaseEngine's adaptive threshold (Max of 20d, 252d, and Floor)
        effective_std = self.calculate_dynamic_threshold(pct_change, min_floor)
        current_std = effective_std.iloc[-1]
        
        # Other indicators for context
        vol_adv = calculate_volume_adv(volume)
        current_vol = volume.iloc[-1]
        current_adv = vol_adv.iloc[-1]
        
        results = []
        for length in range(self.min_len, self.max_len + 1):
            window_returns = pct_change.iloc[-length:]
            window_thresh = effective_std.iloc[-length:]
            
            pat_str = self.extract_pattern(window_returns, window_thresh)
            if not pat_str or len(pat_str) < self.min_len: continue
            
            # STRATEGIC BIAS: Trend Following (US Market)
            # Last char '+' -> Predict UP (LONG), '-' -> Predict DOWN (SHORT)
            last_char = pat_str[-1]
            if last_char == '+':
                direction = "LONG"
            elif last_char == '-':
                direction = "SHORT"
            else:
                continue # Skip neutral patterns for trend strategy
                
            # 3. VALIDATION & STATS
            is_vol_spike = current_vol > (current_adv * 1.25)
            
            # Context-Aware History Scan
            future_returns = self.get_pattern_stats(close, pct_change, effective_std, pat_str, length)
            if not future_returns: continue
            
            # Use base class for standardized math (Correct Short Selling)
            stats = self.calculate_stats(future_returns, direction)
            
            # Final Tradeability (Must meet RRR target and trend quality)
            is_tradeable = stats['win_rate'] >= 60 and stats['rrr'] >= 2.0
            
            results.append({
                'engine': 'TREND_MOMENTUM',
                'pattern': pat_str,
                'forecast': 'UP' if direction == "LONG" else "DOWN",
                'prob': stats['win_rate'],
                'rr': stats['rrr'],
                'matches': stats['total'],
                'is_trend_follow': True,
                'is_tradeable': is_tradeable,
                'adx': round(current_adx, 1),
                'vol_spike': is_vol_spike,
                'threshold': round(current_std * 100, 2)
            })
            
        return results

    def get_pattern_stats(self, prices, pct_change, effective_std, pattern_str, length):
        """Scans history for pattern matches."""
        history_len = len(pct_change)
        future_returns = []
        
        scan_start = 50
        for i in range(scan_start, history_len - 1):
            # Check Trend Context at that time to ensure "Apples to Apples"
            hist_trend = "BULL" if prices.iloc[i] > sma50.iloc[i] else "BEAR"
            if hist_trend != current_trend: continue
            
            window = pct_change.iloc[i-length+1 : i+1]
            thresh_win = effective_std.iloc[i-length+1 : i+1] * 1.25
            
            if self.extract_pattern(window, thresh_win) == pattern_str:
                next_ret = (prices.iloc[i+1] - prices.iloc[i]) / prices.iloc[i]
                future_returns.append(next_ret)
        
        return future_returns
