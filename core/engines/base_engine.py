import pandas as pd
import numpy as np

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
        Note: Following User's request, we skip '.' (sideway) moves to focus on significant events.
        """
        pat_str = ""
        for r, t in zip(returns, threshold):
            if pd.isna(r) or pd.isna(t): break
            if r > t: pat_str += '+'
            elif r < -t: pat_str += '-'
            # Skip if move is within threshold (.)
        return pat_str

    def get_pattern_stats(self, prices, pct_change, effective_std, pattern_str, length, multiplier=1.0):
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

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
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
