import pandas as pd
import numpy as np

class BasePatternEngine:
    """
    Base class for all market-specific trading engines.
    Provides common utilities for pattern recognition and statistical analysis.
    """
    def __init__(self, min_len=3, max_len=8):
        self.min_len = min_len
        self.max_len = max_len

    def extract_pattern(self, returns, threshold):
        """Convert a series of returns and thresholds into a +/-/. pattern string."""
        pat_str = ""
        for r, t in zip(returns, threshold):
            if pd.isna(r) or pd.isna(t): break
            if r > t: pat_str += '+'
            elif r < -t: pat_str += '-'
            else: pat_str += '.'
        return pat_str

    def get_pattern_stats(self, prices, pct_change, effective_std, pattern_str, length, multiplier=1.25):
        """Scans history for occurrences of a specific pattern and returns future outcomes."""
        history_len = len(pct_change)
        future_returns = []
        
        # Define threshold window for scanning
        # Note: Scanning is computationally expensive, but necessary for data-driven logic
        scan_start = 50 
        for i in range(scan_start, history_len - 1):
            window = pct_change.iloc[i-length+1 : i+1]
            thresh_win = effective_std.iloc[i-length+1 : i+1] * multiplier
            
            # Fast check: only join if it matches target string length
            full_pat = self.extract_pattern(window, thresh_win)
            if full_pat == pattern_str:
                next_ret = (prices.iloc[i+1] - prices.iloc[i]) / prices.iloc[i]
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

    def calculate_stats(self, future_returns, direction):
        """
        Calculates performance metrics for a specific direction (LONG or SHORT).
        Logic:
        - LONG: Profit = Price Change %
        - SHORT: Profit = - (Price Change %) <- Price drop is positive profit
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
            
        wins = [p for p in trader_profits if p > 0]
        losses = [p for p in trader_profits if p <= 0]
        
        total = len(trader_profits)
        win_rate = (len(wins) / total * 100) if total > 0 else 0
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        rrr = (avg_win / avg_loss) if avg_loss > 0 else 0
        
        return {
            'win_rate': win_rate,
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'rrr': round(rrr, 2),
            'total': total
        }

    def analyze(self, df, settings):
        """To be implemented by specialized engines."""
        raise NotImplementedError("Each engine must implement the analyze method.")
