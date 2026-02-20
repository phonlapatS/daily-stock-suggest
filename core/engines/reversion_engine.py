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
            
        close = df['close']
        volume = df['volume']
        pct_change = close.pct_change()
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
            future_returns = self.get_pattern_stats(close, pct_change, effective_std, pat_str, length)
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
