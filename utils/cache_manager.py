"""
cache_manager.py - Smart Incremental Cache Update
===================================================
จัดการ Cache อย่างชาญฉลาด:
1. ตรวจสอบข้อมูลที่มีอยู่
2. ดึงเฉพาะวันใหม่ที่ขาดหายไป
3. Append เข้า Cache

ประโยชน์: ลดเวลา Update จาก 2+ ชม. เหลือ 15-20 นาที
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Smart Cache Manager for Incremental Updates"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, symbol: str, exchange: str, interval_str: str = "daily") -> str:
        """Generate cache file path"""
        filename = f"{exchange}_{symbol}.csv"
        return os.path.join(self.cache_dir, filename)
    
    def get_cache_status(self, symbol: str, exchange: str, interval_str: str = "daily") -> Dict:
        """
        ตรวจสอบสถานะ Cache ของสินทรัพย์
        
        Returns:
            {
                'exists': bool,
                'last_date': datetime or None,
                'total_rows': int,
                'needs_update': bool,
                'missing_days': int
            }
        """
        path = self._get_cache_path(symbol, exchange, interval_str)
        today = datetime.now().date()
        
        if not os.path.exists(path):
            return {
                'exists': False,
                'last_date': None,
                'total_rows': 0,
                'needs_update': True,
                'missing_days': -1  # -1 means needs full reload
            }
        
        try:
            df = pd.read_csv(path, parse_dates=['datetime'])
            if df.empty:
                return {
                    'exists': False,
                    'last_date': None,
                    'total_rows': 0,
                    'needs_update': True,
                    'missing_days': -1
                }
            
            last_date = pd.to_datetime(df['datetime'].iloc[-1]).date()
            total_rows = len(df)
            
            # Calculate missing days (excluding weekends roughly)
            days_diff = (today - last_date).days
            # Rough estimate: ~5 trading days per 7 calendar days
            missing_days = max(0, int(days_diff * 5 / 7))
            
            return {
                'exists': True,
                'last_date': last_date,
                'total_rows': total_rows,
                'needs_update': missing_days > 0,
                'missing_days': missing_days
            }
        except Exception as e:
            logger.warning(f"Error reading cache {path}: {e}")
            return {
                'exists': False,
                'last_date': None,
                'total_rows': 0,
                'needs_update': True,
                'missing_days': -1
            }
    
    def load_cache(self, symbol: str, exchange: str, interval_str: str = "daily") -> Optional[pd.DataFrame]:
        """โหลดข้อมูลจาก Cache"""
        path = self._get_cache_path(symbol, exchange, interval_str)
        
        if not os.path.exists(path):
            return None
        
        try:
            df = pd.read_csv(path, parse_dates=['datetime'])
            df.set_index('datetime', inplace=True)
            return df
        except Exception as e:
            logger.warning(f"Error loading cache {path}: {e}")
            return None
    
    def save_cache(self, df: pd.DataFrame, symbol: str, exchange: str, interval_str: str = "daily"):
        """บันทึกข้อมูลลง Cache"""
        path = self._get_cache_path(symbol, exchange, interval_str)
        
        try:
            # Reset index if datetime is index
            df_save = df.reset_index() if 'datetime' not in df.columns else df.copy()
            df_save.to_csv(path, index=False)
            logger.info(f"Saved cache: {path} ({len(df_save)} rows)")
        except Exception as e:
            logger.error(f"Error saving cache {path}: {e}")
    
    def append_to_cache(self, new_data: pd.DataFrame, symbol: str, exchange: str, 
                        interval_str: str = "daily") -> pd.DataFrame:
        """เพิ่มข้อมูลใหม่เข้า Cache"""
        existing = self.load_cache(symbol, exchange, interval_str)
        
        if existing is None:
            self.save_cache(new_data, symbol, exchange, interval_str)
            return new_data
        
        # Combine and remove duplicates
        combined = pd.concat([existing, new_data])
        combined = combined[~combined.index.duplicated(keep='last')]
        combined = combined.sort_index()
        
        self.save_cache(combined, symbol, exchange, interval_str)
        return combined
    
    def get_data_with_update(self, tv, symbol: str, exchange: str, interval, 
                              min_bars: int = 5000, interval_str: str = "daily") -> Optional[pd.DataFrame]:
        """
        Main Function: ดึงข้อมูลแบบ Smart
        
        1. ถ้า Cache ครบ → ดึงเฉพาะวันใหม่
        2. ถ้า Cache ไม่ครบ/เก่าเกิน → Full Reload
        
        Returns:
            DataFrame with all historical data
        """
        status = self.get_cache_status(symbol, exchange, interval_str)
        
        # Case 1: No cache or corrupted → Full reload
        if not status['exists'] or status['missing_days'] == -1:
            logger.info(f"[{symbol}] No cache found, doing full reload ({min_bars} bars)")
            df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=min_bars)
            if df is not None and not df.empty:
                self.save_cache(df, symbol, exchange, interval_str)
            return df
        
        # Case 2: Cache too old (>30 days missing) → Full reload for data integrity
        if status['missing_days'] > 30:
            logger.info(f"[{symbol}] Cache too old ({status['missing_days']} days), doing full reload")
            df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=min_bars)
            if df is not None and not df.empty:
                self.save_cache(df, symbol, exchange, interval_str)
            return df
        
        # Case 3: Cache is up-to-date → Just load it
        if not status['needs_update']:
            logger.info(f"[{symbol}] Cache is current, loading from disk")
            return self.load_cache(symbol, exchange, interval_str)
        
        # Case 4: Cache needs small update → Fetch only new days
        n_bars_to_fetch = min(status['missing_days'] + 5, 50)  # Add buffer
        logger.info(f"[{symbol}] Fetching {n_bars_to_fetch} new bars (was missing {status['missing_days']} days)")
        
        try:
            new_data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars_to_fetch)
            
            if new_data is not None and not new_data.empty:
                combined = self.append_to_cache(new_data, symbol, exchange, interval_str)
                return combined
            else:
                # API failed, return existing cache
                return self.load_cache(symbol, exchange, interval_str)
        except Exception as e:
            logger.warning(f"[{symbol}] Error fetching new data: {e}, using cache")
            return self.load_cache(symbol, exchange, interval_str)


def print_cache_summary(cache_dir: str = "data/cache"):
    """Print summary of all cached data"""
    if not os.path.exists(cache_dir):
        print("No cache directory found")
        return
    
    files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
    
    print(f"\n{'='*60}")
    print(f"CACHE SUMMARY ({len(files)} files)")
    print(f"{'='*60}")
    
    total_rows = 0
    outdated = 0
    today = datetime.now().date()
    
    for f in sorted(files)[:20]:  # Show first 20
        path = os.path.join(cache_dir, f)
        try:
            df = pd.read_csv(path, parse_dates=['datetime'])
            last_date = pd.to_datetime(df['datetime'].iloc[-1]).date()
            days_old = (today - last_date).days
            status = "✅" if days_old <= 1 else "⚠️" if days_old <= 7 else "❌"
            print(f"{status} {f:<30} | {len(df):>6} rows | Last: {last_date} ({days_old}d ago)")
            total_rows += len(df)
            if days_old > 1:
                outdated += 1
        except Exception as e:
            print(f"❌ {f:<30} | ERROR: {e}")
    
    if len(files) > 20:
        print(f"... and {len(files) - 20} more files")
    
    print(f"{'='*60}")
    print(f"Total: {len(files)} files, {total_rows:,} rows, {outdated} need update")


if __name__ == "__main__":
    print_cache_summary()
