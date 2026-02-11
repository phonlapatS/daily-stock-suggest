"""
Market Classifier - Auto Strategy Selection
Automatically classifies assets and selects optimal strategy based on market characteristics
"""
import pandas as pd
import numpy as np

class MarketClassifier:
    """
    จำแนกกลยุทธ์การเทรดอัตโนมัติตามลักษณะของตลาด
    """
    
    # Volatility Thresholds (% daily)
    HIGH_VOL_THRESHOLD = 2.5   # > 2.5% = High Volatility
    LOW_VOL_THRESHOLD = 1.5    # < 1.5% = Low Volatility
    
    def __init__(self, lookback_period=20):
        """
        Args:
            lookback_period (int): จำนวนวันที่ใช้คำนวณ Volatility
        """
        self.lookback_period = lookback_period
    
    def calculate_volatility(self, df):
        """
        คำนวณ Volatility (Standard Deviation of Returns)
        
        Args:
            df (DataFrame): OHLCV data with 'close' column
            
        Returns:
            float: Average volatility in percentage
        """
        returns = df['close'].pct_change()
        volatility = returns.rolling(self.lookback_period).std().mean() * 100
        return volatility
    
    def calculate_trend_strength(self, df):
        """
        คำนวณความแรงของเทรนด์ (ADX-like indicator)
        
        Args:
            df (DataFrame): OHLCV data
            
        Returns:
            float: Trend strength (0-100)
        """
        # Simple trend strength: ใช้ SMA slope
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        
        # ถ้า SMA20 > SMA50 และห่างกันมาก = Trend แรง
        if len(sma_20) < 50:
            return 0
        
        trend_strength = abs((sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100)
        return min(trend_strength * 10, 100)  # Scale to 0-100
    
    def classify(self, symbol, df, exchange='NASDAQ', verbose=False):
        """
        จำแนกกลยุทธ์อัตโนมัติ
        
        Args:
            symbol (str): Stock symbol
            df (DataFrame): OHLCV data
            exchange (str): Exchange name
            verbose (bool): Print classification details
            
        Returns:
            dict: Strategy configuration
        """
        # คำนวณ Market Characteristics
        volatility = self.calculate_volatility(df)
        trend_strength = self.calculate_trend_strength(df)
        
        # Classification Logic
        if volatility > self.HIGH_VOL_THRESHOLD:
            # High Volatility → Inverse + Dynamic
            strategy = {
                'inverse_logic': True,
                'fixed_threshold': None,
                'category': 'HIGH_VOLATILITY',
                'reason': f'Volatility {volatility:.2f}% > {self.HIGH_VOL_THRESHOLD}%'
            }
        elif volatility < self.LOW_VOL_THRESHOLD:
            # Low Volatility → Inverse + Fixed
            strategy = {
                'inverse_logic': True,
                'fixed_threshold': 0.6,
                'category': 'LOW_VOLATILITY',
                'reason': f'Volatility {volatility:.2f}% < {self.LOW_VOL_THRESHOLD}%'
            }
        else:
            # Medium Volatility → Direct (ลองเล่นตาม Pattern เดิม)
            strategy = {
                'inverse_logic': False,
                'fixed_threshold': None,
                'category': 'MEDIUM_VOLATILITY',
                'reason': f'Volatility {volatility:.2f}% (Medium)'
            }
        
        # เพิ่มข้อมูล Metrics
        strategy.update({
            'symbol': symbol,
            'exchange': exchange,
            'volatility': round(volatility, 2),
            'trend_strength': round(trend_strength, 2)
        })
        
        if verbose:
            threshold_str = 'Dynamic' if strategy['fixed_threshold'] is None else f"Fixed {strategy['fixed_threshold']}%"
            logic_str = 'Inverse' if strategy['inverse_logic'] else 'Direct'
            
            print(f"\n🔍 Market Classification: {symbol}")
            print(f"   Category: {strategy['category']}")
            print(f"   Volatility: {volatility:.2f}%")
            print(f"   Trend Strength: {trend_strength:.1f}/100")
            print(f"   Strategy: {logic_str} + {threshold_str}")
            print(f"   Reason: {strategy['reason']}")
        
        return strategy


def get_auto_strategy(symbol, df, exchange='NASDAQ', verbose=False):
    """
    Convenience function สำหรับเรียกใช้งานง่ายๆ
    
    Args:
        symbol (str): Stock symbol
        df (DataFrame): OHLCV data
        exchange (str): Exchange name
        verbose (bool): Print details
        
    Returns:
        dict: Strategy configuration
    """
    classifier = MarketClassifier()
    return classifier.classify(symbol, df, exchange, verbose)


# Example Usage
if __name__ == "__main__":
    from tvDatafeed import TvDatafeed
    
    tv = TvDatafeed()
    
    # Test with different stocks
    test_stocks = [
        ('NVDA', 'NASDAQ'),   # High Volatility
        ('AAPL', 'NASDAQ'),   # Low Volatility
        ('TSLA', 'NASDAQ'),   # Medium Volatility
    ]
    
    print("=" * 60)
    print("AUTO-CLASSIFICATION DEMO")
    print("=" * 60)
    
    for symbol, exchange in test_stocks:
        df = tv.get_hist(symbol, exchange, n_bars=500)
        if df is not None:
            strategy = get_auto_strategy(symbol, df, exchange, verbose=True)
