import pandas as pd
import numpy as np
from .base_engine import BasePatternEngine

class ThaiLogicThresholdOnlyEngine(BasePatternEngine):
    """
    Thai Market Engine - Logic Threshold Only
    Simplified version focusing on threshold-based pattern recognition
    without complex risk management
    """
    
    def __init__(self):
        super().__init__()
        # Thai market specific settings
        self.min_floor = 0.01  # 1.0% minimum move for Thai market (fractional)
        
    def analyze(self, df, settings):
        """
        Analyze Thai stocks with threshold-only logic.
        Uses Rule 2 (Dynamic Lookback) + Rule 3 (Best Fit Selection).
        Returns list format compatible with processor.py.
        
        Returns:
            list: At most 1 result dict per stock (anti-overlapping Rule 1)
        """
        # Calculate basic indicators
        pct_change = df['close'].pct_change()
        
        # Calculate dynamic threshold (min_floor = 1.0% for Thai)
        effective_std = self.calculate_dynamic_threshold(pct_change, self.min_floor)
        current_std = effective_std.iloc[-1]
        
        # Gate: Today's move must exceed threshold
        if abs(pct_change.iloc[-1]) < current_std:
            return []
        
        # Rule 2: Dynamic Lookback — Get Active Pattern
        active_pattern = self.get_active_pattern(pct_change, effective_std)
        if not active_pattern:
            return []
        
        # Direction: Mean Reversion (fade the move)
        last_char = active_pattern[-1]
        if last_char == '+':
            direction = "SHORT"
        elif last_char == '-':
            direction = "LONG"
        else:
            return []
        
        # Rule 3: Best Fit Selection (Count >= 30 for Thai market)
        best_fit = self.select_best_fit(
            df['close'], pct_change, effective_std, active_pattern,
            min_count=30, direction_override=direction
        )
        
        if not best_fit:
            return []
        
        stats = best_fit['stats']
        is_tradeable = self.check_trustworthy(stats, 60.0, 30)
        
        # Rule 1: Return SINGLE result (anti-overlapping)
        return [{
            'engine': 'THAI_LOGIC_THRESHOLD_ONLY',
            'pattern': best_fit['pattern'],
            'forecast': 'UP' if direction == "LONG" else "DOWN",
            'prob': stats['win_rate'],
            'rr': stats['rrr'],
            'matches': stats['total'],
            'avg_win': stats['avg_win'],
            'avg_loss': stats['avg_loss'],
            'is_reversal': True,
            'is_tradeable': is_tradeable,
            'threshold': round(current_std * 100, 2),
            'vr': 0,
            'filter_tags': [],
            'vol_target_size': None
        }]
    
    def get_trading_signals(self, df, settings):
        """
        Generate trading signals based on threshold-only logic
        
        Args:
            df: DataFrame with OHLCV data
            settings: Dictionary with signal generation parameters
            
        Returns:
            DataFrame with trading signals
        """
        signals = []
        
        # Calculate indicators
        df['returns'] = df['close'].pct_change()
        effective_std = self.calculate_dynamic_threshold(df['returns'], self.min_floor)
        
        # Get recent patterns
        recent_data = df.tail(20)  # Last 20 days
        
        for i in range(len(recent_data)):
            current_idx = len(df) - len(recent_data) + i
            
            # Check different pattern lengths
            for length in range(self.min_len, self.max_len + 1):
                if current_idx >= length:
                    window_returns = df['returns'].iloc[current_idx - length:current_idx]
                    window_threshold = effective_std.iloc[current_idx - length:current_idx]
                    
                    pattern = self.extract_pattern(window_returns, window_threshold)
                    
                    if pattern:
                        # Get pattern statistics
                        pattern_key = f'length_{length}'
                        if pattern_key in settings.get('pattern_stats', {}):
                            pattern_stats = settings['pattern_stats'][pattern_key]
                            
                            if pattern in pattern_stats:
                                stats = pattern_stats[pattern]
                                
                                # Check if pattern meets criteria
                                wr_threshold = settings.get('wr_threshold', 60)
                                count_threshold = settings.get('count_threshold', 10)
                                
                                if self.check_trustworthy(stats, wr_threshold, count_threshold):
                                    signals.append({
                                        'date': df.index[current_idx],
                                        'pattern': pattern,
                                        'length': length,
                                        'threshold': stats['threshold'],
                                        'win_rate': stats['win_rate'],
                                        'avg_return': stats['avg_return'],
                                        'signal_strength': stats['win_rate'] * stats['count'] / 100
                                    })
        
        return pd.DataFrame(signals)
