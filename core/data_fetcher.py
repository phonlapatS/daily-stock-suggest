"""
Data Fetcher Module - ดึงข้อมูลจาก TradingView
Pure data extraction - No predictions, pure historical data only
"""

from tvDatafeed import TvDatafeed, Interval
import pandas as pd
from datetime import datetime
from config import EXCHANGES, DEFAULT_N_BARS
from utils import add_percent_change_column


class StockDataFetcher:
    """
    Class สำหรับดึงข้อมูลหุ้นจาก TradingView
    """
    
    def __init__(self):
        """
        Initialize TvDatafeed connection
        """
        self.tv = TvDatafeed()
        print("✅ Connected to TradingView Data Feed")
    
    def fetch_daily_data(self, symbol, exchange, n_bars=DEFAULT_N_BARS):
        """
        ดึงข้อมูล daily OHLCV
        
        Args:
            symbol: รหัสหุ้น เช่น 'PTT', 'AAPL'
            exchange: ตลาด เช่น 'SET', 'NASDAQ'
            n_bars: จำนวน bars ที่ต้องการ
        
        Returns:
            DataFrame: with columns [datetime, open, high, low, close, volume, pct_change]
        """
        try:
            print(f"📊 Fetching daily data for {symbol} from {exchange}...")
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=n_bars
            )
            
            if df is None or df.empty:
                print(f"❌ No data received for {symbol}")
                return None
            
            # เพิ่ม % change column
            df = add_percent_change_column(df)
            
            # ลบ NA rows
            df = df.dropna()
            
            print(f"✅ Fetched {len(df)} daily bars for {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_intraday_data(self, symbol, exchange, interval='15', n_bars=DEFAULT_N_BARS):
        """
        ดึงข้อมูล intraday OHLCV
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            interval: '15' (15min), '30' (30min), '60' (1hr)
            n_bars: จำนวน bars
        
        Returns:
            DataFrame: with OHLCV + pct_change
        """
        try:
            # Map interval string to Interval enum
            interval_map = {
                '1': Interval.in_1_minute,
                '5': Interval.in_5_minute,
                '15': Interval.in_15_minute,
                '30': Interval.in_30_minute,
                '60': Interval.in_1_hour,
                '240': Interval.in_4_hour
            }
            
            tv_interval = interval_map.get(interval, Interval.in_15_minute)
            
            print(f"📊 Fetching {interval}min data for {symbol} from {exchange}...")
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=tv_interval,
                n_bars=n_bars
            )
            
            if df is None or df.empty:
                print(f"❌ No data received for {symbol}")
                return None
            
            # เพิ่ม % change column
            df = add_percent_change_column(df)
            
            # ลบ NA rows
            df = df.dropna()
            
            print(f"✅ Fetched {len(df)} {interval}min bars for {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching intraday data for {symbol}: {str(e)}")
            return None
    
    def get_stock_universe(self, market='thai'):
        """
        ดึงรายชื่อหุ้นทั้งหมดในตลาด
        
        Args:
            market: 'thai', 'us', etc.
        
        Returns:
            list: รายชื่อหุ้น
        """
        from config import DEFAULT_STOCKS
        
        if market.lower() == 'thai':
            exchange = EXCHANGES['thai']
            symbols = DEFAULT_STOCKS.get('thai', [])
            return [{'symbol': s, 'exchange': exchange} for s in symbols]
        
        elif market.lower() == 'us':
            return DEFAULT_STOCKS.get('us', [])
        
        else:
            print(f"⚠️ Unknown market: {market}")
            return []


# Example usage
if __name__ == "__main__":
    # ทดสอบการดึงข้อมูล
    fetcher = StockDataFetcher()
    
    # ทดสอบหุ้นไทย
    df_ptt = fetcher.fetch_daily_data('PTT', 'SET', n_bars=1000)
    if df_ptt is not None:
        print("\nSample data:")
        print(df_ptt.head())
        print(f"\nDate range: {df_ptt.index[0]} to {df_ptt.index[-1]}")
        print(f"Total rows: {len(df_ptt)}")
    
    # ทดสอบหุ้นสหรัฐ
    df_aapl = fetcher.fetch_daily_data('AAPL', 'NASDAQ', n_bars=1000)
    if df_aapl is not None:
        print("\nSample AAPL data:")
        print(df_aapl.head())
