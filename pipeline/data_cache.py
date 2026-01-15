"""
Data Cache Manager - เก็บข้อมูลเพื่อไม่ต้องดึงซ้ำ
Optimization: ลด API calls และเวลาในการประมวลผล
"""

import os
import pickle
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


class DataCacheManager:
    """
    จัดการ cache ของข้อมูลหุ้น
    - เก็บข้อมูลที่ดึงมาแล้ว
    - อัพเดทเฉพาะข้อมูลใหม่
    - ลด API calls
    """
    
    def __init__(self, cache_dir='data/cache'):
        """
        Args:
            cache_dir: โฟลเดอร์เก็บ cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Cache directory: {self.cache_dir}")
    
    def _get_cache_path(self, symbol, exchange, timeframe):
        """
        สร้าง path สำหรับ cache file
        """
        filename = f"{symbol}_{exchange}_{timeframe}.pkl"
        return self.cache_dir / filename
    
    def get_cached_data(self, symbol, exchange, timeframe='daily', max_age_hours=24):
        """
        ดึงข้อมูลจาก cache (ถ้ามีและยังไม่หมดอายุ)
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            timeframe: daily หรือ intraday interval
            max_age_hours: อายุสูงสุดของ cache (ชั่วโมง)
        
        Returns:
            DataFrame or None
        """
        cache_path = self._get_cache_path(symbol, exchange, timeframe)
        
        if not cache_path.exists():
            return None
        
        # ตรวจสอบอายุ
        file_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age_hours = (datetime.now() - file_mtime).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            print(f"   ⌛ Cache หมดอายุ ({age_hours:.1f} ชม.) - จะดึงใหม่")
            return None
        
        # โหลด cache
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            print(f"   ✅ ใช้ cache ({len(data)} bars, อายุ {age_hours:.1f} ชม.)")
            return data
        
        except Exception as e:
            print(f"   ❌ Error loading cache: {e}")
            return None
    
    def save_to_cache(self, symbol, exchange, timeframe, data):
        """
        บันทึกข้อมูลลง cache
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            timeframe: daily หรือ interval
            data: DataFrame
        """
        cache_path = self._get_cache_path(symbol, exchange, timeframe)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"   💾 บันทึก cache: {cache_path.name}")
        
        except Exception as e:
            print(f"   ❌ Error saving cache: {e}")
    
    def clear_cache(self, symbol=None, exchange=None):
        """
        ลบ cache
        
        Args:
            symbol: ลบเฉพาะหุ้นนี้ (ถ้าระบุ)
            exchange: ลบเฉพาะตลาดนี้ (ถ้าระบุ)
        """
        if symbol and exchange:
            # ลบเฉพาะหุ้นนี้
            pattern = f"{symbol}_{exchange}_*.pkl"
        elif exchange:
            # ลบเฉพาะตลาด
            pattern = f"*_{exchange}_*.pkl"
        else:
            # ลบทั้งหมด
            pattern = "*.pkl"
        
        deleted = 0
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
            deleted += 1
        
        print(f"🗑️ ลบ cache {deleted} ไฟล์")
    
    def get_cache_info(self):
        """
        แสดงข้อมูลเกี่ยวกับ cache
        """
        cache_files = list(self.cache_dir.glob("*.pkl"))
        
        if not cache_files:
            print("📭 ไม่มี cache")
            return
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        print(f"\n📊 Cache Info:")
        print(f"   - จำนวนไฟล์: {len(cache_files)}")
        print(f"   - ขนาดรวม: {total_size / 1024 / 1024:.2f} MB")
        print(f"   - Location: {self.cache_dir}")
        
        # แสดง 5 cache ล่าสุด
        cache_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        print(f"\n   📝 Cache ล่าสุด:")
        for cache_file in cache_files[:5]:
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age = datetime.now() - mtime
            size_kb = cache_file.stat().st_size / 1024
            
            print(f"   - {cache_file.name[:30]:30s} | {size_kb:6.1f} KB | {age.total_seconds()/3600:.1f} ชม.")


# Optimized Data Fetcher with Cache
class OptimizedDataFetcher:
    """
    Data Fetcher ที่มี cache
    """
    
    def __init__(self, use_cache=True, cache_max_age_hours=24):
        """
        Args:
            use_cache: ใช้ cache หรือไม่
            cache_max_age_hours: อายุสูงสุดของ cache
        """
        from data_fetcher import StockDataFetcher
        
        self.fetcher = StockDataFetcher()
        self.use_cache = use_cache
        self.cache_max_age_hours = cache_max_age_hours
        
        if use_cache:
            self.cache_manager = DataCacheManager()
        else:
            self.cache_manager = None
    
    def fetch_daily_data(self, symbol, exchange, n_bars=5000, force_refresh=False):
        """
        ดึงข้อมูล daily พร้อม cache
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            n_bars: จำนวน bars
            force_refresh: บังคับดึงใหม่ (ไม่ใช้ cache)
        
        Returns:
            DataFrame
        """
        # ลอง cache ก่อน
        if self.use_cache and not force_refresh:
            cached = self.cache_manager.get_cached_data(
                symbol, exchange, 'daily', 
                max_age_hours=self.cache_max_age_hours
            )
            
            if cached is not None:
                return cached
        
        # ดึงใหม่
        print(f"   🌐 Fetching from TradingView...")
        df = self.fetcher.fetch_daily_data(symbol, exchange, n_bars)
        
        # บันทึก cache
        if df is not None and self.use_cache:
            self.cache_manager.save_to_cache(symbol, exchange, 'daily', df)
        
        return df
    
    def fetch_intraday_data(self, symbol, exchange, interval='15', n_bars=5000, force_refresh=False):
        """
        ดึงข้อมูล intraday พร้อม cache
        """
        timeframe = f"intraday_{interval}m"
        
        # ลอง cache
        if self.use_cache and not force_refresh:
            cached = self.cache_manager.get_cached_data(
                symbol, exchange, timeframe,
                max_age_hours=self.cache_max_age_hours
            )
            
            if cached is not None:
                return cached
        
        # ดึงใหม่
        print(f"   🌐 Fetching from TradingView...")
        df = self.fetcher.fetch_intraday_data(symbol, exchange, interval, n_bars)
        
        # บันทึก cache
        if df is not None and self.use_cache:
            self.cache_manager.save_to_cache(symbol, exchange, timeframe, df)
        
        return df


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("🧪 Testing Cache System")
    print("="*80)
    
    # สร้าง fetcher with cache
    fetcher = OptimizedDataFetcher(use_cache=True, cache_max_age_hours=24)
    
    # Test 1: ดึงครั้งแรก (จะช้า)
    print("\n📊 Test 1: ดึงข้อมูลครั้งแรก")
    import time
    start = time.time()
    df1 = fetcher.fetch_daily_data('AAPL', 'NASDAQ', n_bars=500)
    time1 = time.time() - start
    print(f"   ⏱️ ใช้เวลา: {time1:.2f} วินาที")
    
    # Test 2: ดึงอีกครั้ง (จะเร็ว - ใช้ cache)
    print("\n📊 Test 2: ดึงข้อมูลอีกครั้ง (ควรใช้ cache)")
    start = time.time()
    df2 = fetcher.fetch_daily_data('AAPL', 'NASDAQ', n_bars=500)
    time2 = time.time() - start
    print(f"   ⏱️ ใช้เวลา: {time2:.2f} วินาที")
    print(f"   🚀 เร็วขึ้น: {time1/time2:.1f}x")
    
    # Cache info
    print("\n" + "="*80)
    fetcher.cache_manager.get_cache_info()
