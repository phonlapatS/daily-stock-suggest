"""
Basic Pattern Matcher - สถิติเพียวๆ
===================================
Pattern matching และคำนวณสถิติแบบเรียบง่าย
ไม่ใช้ risk management, multi-day hold, หรือ trade simulation
"""

import pandas as pd
import numpy as np


class BasicPatternMatcher:
    """
    Pattern Matcher แบบเรียบง่าย
    - หา pattern ในประวัติ
    - คำนวณสถิติเพียวๆ (Prob%, AvgWin%, AvgLoss%, RRR, match_count)
    """
    
    def __init__(self, lookback=5000):
        """
        Args:
            lookback: จำนวน bars ที่จะสแกนย้อนหลัง (default: 5000)
        """
        self.lookback = lookback
    
    def _get_market_threshold(self, exchange):
        """
        กำหนด threshold ตามประเทศ
        
        Args:
            exchange: Exchange name (SET, NASDAQ, TWSE, HKEX, etc.)
        
        Returns:
            tuple: (market_floor, threshold_multiplier)
        """
        if exchange is None:
            # Default: 0.5% floor, 0.9x multiplier
            return (0.005, 0.9)
        
        ex = exchange.upper()
        
        # THAI Market
        if any(x in ex for x in ['SET', 'MAI', 'TH']):
            return (0.007, 1.0)  # Floor: 0.7%, Multiplier: 1.0x
        
        # US Market
        elif any(x in ex for x in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX']):
            return (0.006, 0.9)  # Floor: 0.6%, Multiplier: 0.9x
        
        # Taiwan Market
        elif any(x in ex for x in ['TWSE', 'TW']):
            return (0.005, 0.9)  # Floor: 0.5%, Multiplier: 0.9x
        
        # China/HK Market (ปรับเพื่อให้ Prob สูงขึ้น)
        elif any(x in ex for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN']):
            return (0.006, 1.0)  # Floor: 0.6%, Multiplier: 1.0x (เพิ่มจาก 0.5%, 0.9x)
        
        # Default
        else:
            return (0.005, 0.9)  # Floor: 0.5%, Multiplier: 0.9x
    
    def extract_pattern(self, pct_change, threshold):
        """
        แปลง pct_change เป็น pattern string (+/-)
        
        Args:
            pct_change: Series ของ % change
            threshold: Series ของ threshold (dynamic)
        
        Returns:
            list: Pattern strings (เช่น ['+', '-', '+', '+'])
        """
        patterns = []
        for i in range(len(pct_change)):
            if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
                patterns.append(None)
            elif pct_change.iloc[i] > threshold.iloc[i]:
                patterns.append('+')
            elif pct_change.iloc[i] < -threshold.iloc[i]:
                patterns.append('-')
            else:
                patterns.append(None)  # Sideway - ไม่นับ
        return patterns
    
    def find_pattern_matches(self, df, pattern_str, min_len=3, max_len=8, exchange=None):
        """
        หา pattern ในประวัติ
        
        Args:
            df: DataFrame with OHLCV data
            pattern_str: Pattern string ที่ต้องการหา (เช่น "++--")
            min_len: ความยาวขั้นต่ำของ pattern
            max_len: ความยาวสูงสุดของ pattern
            exchange: Exchange name (เพื่อกำหนด threshold ตามประเทศ)
        
        Returns:
            list: Indices ที่ pattern match (pattern ends at this index)
        """
        if len(df) < 50:
            return []
        
        # Calculate threshold
        pct_change = df['close'].pct_change()
        
        # Dynamic threshold (20-day SD, 252-day SD, market floor)
        short_std = pct_change.rolling(20).std()
        long_std = pct_change.rolling(252).std()
        effective_std = np.maximum(short_std, long_std.fillna(0))
        
        # Market floor และ multiplier ตามประเทศ
        market_floor, threshold_multiplier = self._get_market_threshold(exchange)
        effective_std = np.maximum(effective_std, market_floor)
        
        # Threshold = effective_std * multiplier
        threshold = effective_std * threshold_multiplier
        
        # Extract patterns
        raw_patterns = self.extract_pattern(pct_change, threshold)
        
        # Find matches
        matches = []
        pattern_len = len(pattern_str)
        
        if pattern_len < min_len or pattern_len > max_len:
            return matches
        
        # Scan history (skip first 50 bars for stability)
        scan_start = 50
        for i in range(scan_start, len(raw_patterns) - 1):
            # Get window
            window_slice = raw_patterns[i-pattern_len+1 : i+1] if i-pattern_len+1 >= 0 else raw_patterns[:i+1]
            window_pattern = ''.join([p for p in window_slice if p is not None])
            
            # Check match
            if window_pattern == pattern_str:
                matches.append(i)
        
        return matches
    
    def calculate_stats(self, df, matches, direction="LONG"):
        """
        คำนวณสถิติเพียวๆ จาก matches
        
        Args:
            df: DataFrame with OHLCV data
            matches: List of indices ที่ pattern match
            direction: "LONG" หรือ "SHORT"
        
        Returns:
            dict: {
                'prob': float,        # Win Rate (%)
                'avg_win': float,      # AvgWin% (average of winning trades)
                'avg_loss': float,     # AvgLoss% (average of losing trades, absolute)
                'rrr': float,         # Risk-Reward Ratio
                'match_count': int,    # จำนวน match
                'wins': int,           # จำนวน winning trades
                'losses': int          # จำนวน losing trades
            }
        """
        if not matches:
            return {
                'prob': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'rrr': 0.0,
                'match_count': 0,
                'wins': 0,
                'losses': 0
            }
        
        # Get next day returns
        next_returns = []
        close = df['close']
        
        for match_idx in matches:
            if match_idx + 1 >= len(df):
                continue
            
            # N+1 return
            next_return = (close.iloc[match_idx+1] - close.iloc[match_idx]) / close.iloc[match_idx]
            next_returns.append(next_return)
        
        if not next_returns:
            return {
                'prob': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'rrr': 0.0,
                'match_count': 0,
                'wins': 0,
                'losses': 0
            }
        
        # Calculate trader profits (based on direction)
        trader_profits = []
        for ret in next_returns:
            if direction == "LONG":
                profit = ret * 100  # % return
            else:  # SHORT
                profit = -ret * 100  # Inverse return
        
            trader_profits.append(profit)
        
        # Separate wins and losses
        wins = [p for p in trader_profits if p > 0]
        losses = [p for p in trader_profits if p <= 0]
        
        # Calculate statistics
        total = len(trader_profits)
        win_count = len(wins)
        loss_count = len(losses)
        
        prob = (win_count / total * 100) if total > 0 else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = abs(np.mean(losses)) if losses else 0.0
        rrr = (avg_win / avg_loss) if avg_loss > 0 else 0.0
        
        return {
            'prob': round(prob, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'rrr': round(rrr, 2),
            'match_count': total,
            'wins': win_count,
            'losses': loss_count
        }
    
    def get_best_pattern(self, df, min_len=3, max_len=8, min_stats=30, exchange=None):
        """
        หา pattern ที่ดีที่สุด (Prob สูงสุด, match_count >= min_stats)
        
        Strategy:
        1. Scan ทุก pattern ใน training data (เก็บสถิติ)
        2. ใช้ last pattern (วันนี้) เพื่อหา best match
        3. Return pattern ที่มี match_count >= min_stats และ prob สูงสุด
        
        Args:
            df: DataFrame with OHLCV data
            min_len: ความยาวขั้นต่ำของ pattern
            max_len: ความยาวสูงสุดของ pattern
            min_stats: จำนวน match ขั้นต่ำ
            exchange: Exchange name (เพื่อกำหนด threshold ตามประเทศ)
        
        Returns:
            dict: {
                'pattern': str,
                'direction': str,
                'stats': dict
            } or None
        """
        if len(df) < 50:
            return None
        
        # Calculate threshold (ใช้ threshold ตามประเทศ)
        pct_change = df['close'].pct_change()
        
        # ตรวจสอบว่าเป็นจีน/ฮ่องกงหรือไม่ (ใช้ SD จากทั้งหมด 5000 bars)
        is_china_hk = exchange and any(x in exchange.upper() for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN'])
        
        if is_china_hk:
            # จีน/ฮ่องกง: ใช้ SD จากทั้งหมด 5000 bars (ไม่ใช่ rolling window)
            # เพื่อลด threshold และให้ได้ pattern มากขึ้น
            overall_std = pct_change.std()  # SD จากทั้งหมด
            effective_std = pd.Series([overall_std] * len(df), index=df.index)
        else:
            # อื่นๆ: ใช้ rolling window (20-day, 252-day)
            short_std = pct_change.rolling(20).std()
            long_std = pct_change.rolling(252).std()
            effective_std = np.maximum(short_std, long_std.fillna(0))
        
        market_floor, threshold_multiplier = self._get_market_threshold(exchange)
        
        if is_china_hk:
            # จีน/ฮ่องกง: ลด threshold multiplier (0.8x แทน 1.0x) เพื่อให้ได้ pattern มากขึ้น
            threshold_multiplier = 0.8
        
        effective_std = np.maximum(effective_std, market_floor)
        threshold = effective_std * threshold_multiplier
        
        # Extract patterns
        raw_patterns = self.extract_pattern(pct_change, threshold)
        
        # 1. TRAINING PHASE: Scan ทุก pattern ใน training data (เก็บสถิติ)
        pattern_stats = {}  # {pattern_str: [next_returns]}
        scan_start = 50
        
        for i in range(scan_start, len(df) - 1):
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            for length in range(min_len, max_len + 1):
                if i - length + 1 < 0:
                    continue
                
                # Get pattern window
                window_slice = raw_patterns[i-length+1 : i+1]
                pattern_str = ''.join([p for p in window_slice if p is not None])
                
                if not pattern_str:
                    continue
                
                # Store next return for this pattern
                if pattern_str not in pattern_stats:
                    pattern_stats[pattern_str] = []
                pattern_stats[pattern_str].append(next_ret)
        
        # 2. TEST PHASE: ใช้ last pattern (วันนี้) เพื่อหา best match
        # ตรวจสอบว่าเป็นจีน/ฮ่องกงหรือไม่ (ใช้ reversion logic)
        is_china_hk = exchange and any(x in exchange.upper() for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN'])
        
        best_pattern = None
        best_stats = None
        best_direction = None
        best_prob = 0.0
        
        # Try different pattern lengths (from last pattern)
        for length in range(min_len, max_len + 1):
            if len(raw_patterns) < length:
                continue
            
            # Get last pattern (วันนี้)
            window_slice = raw_patterns[-length:] if len(raw_patterns) >= length else raw_patterns
            pattern_str = ''.join([p for p in window_slice if p is not None])
            
            if not pattern_str or pattern_str not in pattern_stats:
                continue
            
            # Get historical returns for this pattern
            next_returns = pattern_stats[pattern_str]
            
            if len(next_returns) < min_stats:
                continue
            
            # กำหนด direction ตาม strategy
            if is_china_hk:
                # China/HK: Mean Reversion (Fade the move)
                # + (Up anomaly) -> SHORT (expect reversion down)
                # - (Down anomaly) -> LONG (expect reversion up)
                last_char = pattern_str[-1] if pattern_str else None
                if last_char == '+':
                    directions_to_try = ["SHORT"]
                elif last_char == '-':
                    directions_to_try = ["LONG"]
                else:
                    continue  # Skip if no clear direction
            else:
                # อื่นๆ: Try both directions (เลือก Prob สูงสุด)
                directions_to_try = ["LONG", "SHORT"]
            
            # Try directions
            for direction in directions_to_try:
                # Calculate stats from historical returns
                stats = self.calculate_stats_from_returns(next_returns, direction)
                
                if stats['prob'] > best_prob and stats['match_count'] >= min_stats:
                    best_pattern = pattern_str
                    best_stats = stats
                    best_direction = direction
                    best_prob = stats['prob']
        
        if best_pattern is None:
            return None
        
        return {
            'pattern': best_pattern,
            'direction': best_direction,
            'stats': best_stats
        }
    
    def calculate_stats_from_returns(self, next_returns, direction="LONG"):
        """
        คำนวณสถิติจาก next_returns โดยตรง (ไม่ต้องหา matches)
        
        Args:
            next_returns: List of next day returns (fractional, e.g. 0.02 for +2%)
            direction: "LONG" หรือ "SHORT"
        
        Returns:
            dict: Statistics
        """
        if not next_returns:
            return {
                'prob': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'rrr': 0.0,
                'match_count': 0,
                'wins': 0,
                'losses': 0
            }
        
        # Calculate trader profits (based on direction)
        trader_profits = []
        for ret in next_returns:
            if direction == "LONG":
                profit = ret * 100  # % return
            else:  # SHORT
                profit = -ret * 100  # Inverse return
        
            trader_profits.append(profit)
        
        # Separate wins and losses
        wins = [p for p in trader_profits if p > 0]
        losses = [p for p in trader_profits if p <= 0]
        
        # Calculate statistics
        total = len(trader_profits)
        win_count = len(wins)
        loss_count = len(losses)
        
        prob = (win_count / total * 100) if total > 0 else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = abs(np.mean(losses)) if losses else 0.0
        rrr = (avg_win / avg_loss) if avg_loss > 0 else 0.0
        
        return {
            'prob': round(prob, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'rrr': round(rrr, 2),
            'match_count': total,
            'wins': win_count,
            'losses': loss_count
        }

