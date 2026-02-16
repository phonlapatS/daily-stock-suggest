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
            
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        pct_change = close.pct_change()
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
            
        # Volume context (informational tagging)
        vol_adv = calculate_volume_adv(volume)
        current_vol = volume.iloc[-1]
        current_adv = vol_adv.iloc[-1]
        
        results = []
        for length in range(self.min_len, self.max_len + 1):
            window_returns = pct_change.iloc[-length:]
            window_thresh = effective_std.iloc[-length:]
            
            pat_str = self.extract_pattern(window_returns, window_thresh)
            if not pat_str or len(pat_str) < self.min_len:
                continue
            
            # STRATEGIC BIAS: Trend Following (Ride the move)
            # + (Up anomaly) -> LONG (momentum continues up)
            # - (Down anomaly) -> SHORT (momentum continues down)
            last_char = pat_str[-1]
            if last_char == '+':
                direction = "LONG"
            elif last_char == '-':
                direction = "SHORT"
            else:
                continue
                
            # US Market: LONG ONLY — ignore short signals
            if is_us and direction == "SHORT":
                continue
                
            # 4. REGIME-AWARE VALIDATION
            # Only compare with past events in the SAME trend regime (Price vs SMA50)
            filter_tags = []
            if is_us or is_tw:
                filter_tags.append("ADX_FILTER")
            
            is_vol_spike = current_vol > (current_adv * 1.25)
            
            # Context-Aware History Scan (same trend regime = Apples to Apples)
            future_returns = self.get_pattern_stats(
                close, pct_change, effective_std, pat_str, length, sma50, current_trend
            )
            if not future_returns:
                continue
            
            stats = self.calculate_stats(future_returns, direction)
            
            # 5. QUALITY FLAG (V5.2: Late Filtering)
            # -------------------------------------------------------
            # คืนทุก pattern ที่เกิน threshold (ไม่ filter)
            # is_tradeable = quality flag สำหรับ sorting/display เท่านั้น
            # Forward testing จะเป็นคนตัดสินว่า pattern ไหนดีจริงๆ
            # -------------------------------------------------------
            is_tradeable = self.check_trustworthy(stats, 60.0, 15)  # WR≥60%, Count≥15
            
            # V5.2: Return ALL patterns (no filtering here - late filtering in report)
            results.append({
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
                'vol_target_size': None  # Not used for Trend markets
            })
            
        return results

    def get_pattern_stats(self, prices, pct_change, effective_std, pattern_str, length, sma50, current_trend):
        """
        Regime-Aware History Scan.
        Only counts historical pattern matches that occurred in the SAME trend context
        (BULL or BEAR relative to SMA50) as the current market condition.
        This ensures "Apples to Apples" comparison.
        """
        history_len = len(pct_change)
        future_returns = []
        
        scan_start = 50
        for i in range(scan_start, history_len - 1):
            # Check Trend Context at that historical point
            hist_trend = "BULL" if prices.iloc[i] > sma50.iloc[i] else "BEAR"
            if hist_trend != current_trend:
                continue
            
            window = pct_change.iloc[i-length+1 : i+1]
            thresh_win = effective_std.iloc[i-length+1 : i+1]
            
            if self.extract_pattern(window, thresh_win) == pattern_str:
                next_ret = (prices.iloc[i+1] - prices.iloc[i]) / prices.iloc[i]
                future_returns.append(next_ret)
        
        return future_returns
