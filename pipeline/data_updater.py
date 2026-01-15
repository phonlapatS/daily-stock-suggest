#!/usr/bin/env python
"""
data_updater.py - Scalable Stock Data Pipeline
===============================================

Purpose: ดึงและอัพเดทข้อมูลหุ้นแบบ Incremental (ดึงเฉพาะข้อมูลใหม่)
- รองรับ 100+ หุ้น
- ใช้ Parquet format (เร็ว, ประหยัด)
- Smart Update (ดึงครั้งแรกเต็ม, ครั้งต่อไปเฉพาะใหม่)
- Error Handling (1 หุ้นพังไม่กระทบอื่น)
- Rate Limiting (ไม่โดน ban)

Author: Stock Prediction System
Date: 2026-01-14
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# ================================
# Configuration
# ================================

DATA_DIR = "data/stocks"  # โฟลเดอร์เก็บข้อมูล
INITIAL_BARS = 3000  # ดึงครั้งแรก (ประมาณ 12 ปี สำหรับ daily)
UPDATE_BARS = 100  # ดึงเพิ่มเติม (ประมาณ 100 วันทำการ)
RATE_LIMIT_SECONDS = 1.0  # หน่วงเวลาระหว่างดึง (ไม่โดน ban)

# ================================
# Dynamic Stock List Generation
# ================================

def get_all_thai_stocks():
    """
    ดึงรายชื่อหุ้นไทยทั้งหมดจาก starfishX
    
    Returns:
        list: List of {'symbol': 'PTT', 'exchange': 'SET'}
    """
    try:
        import starfishX as sx
        
        print("📡 Fetching all Thai stocks from starfishX...")
        
        # ดึงข้อมูลหุ้นทั้งหมด
        stocks_df = sx.getStockName()
        
        if stocks_df is None or stocks_df.empty:
            raise ValueError("No stocks returned from starfishX")
        
        # แปลงเป็น format ที่ต้องการ
        stock_list = []
        
        for symbol in stocks_df['symbol'].tolist():
            # TradingView ใช้ 'SET' สำหรับหุ้นไทยทั้งหมด (SET + mai)
            stock_list.append({
                'symbol': symbol,
                'exchange': 'SET'
            })
        
        print(f"✅ Found {len(stock_list)} Thai stocks")
        return stock_list
        
    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch from starfishX: {e}")
        print("📋 Using fallback stock list...")
        
        # Fallback: รายการหุ้นพื้นฐาน
        return [
            {'symbol': 'PTT', 'exchange': 'SET'},
            {'symbol': 'DELTA', 'exchange': 'SET'},
            {'symbol': 'AOT', 'exchange': 'SET'},
            {'symbol': 'KBANK', 'exchange': 'SET'},
            {'symbol': 'CPALL', 'exchange': 'SET'},
            {'symbol': 'ADVANC', 'exchange': 'SET'},
            {'symbol': 'BDMS', 'exchange': 'SET'},
            {'symbol': 'BBL', 'exchange': 'SET'},
            {'symbol': 'SCB', 'exchange': 'SET'},
            {'symbol': 'TOP', 'exchange': 'SET'},
        ]


# ดึงรายการหุ้นแบบ Dynamic
STOCK_LIST = get_all_thai_stocks()


class StockDataUpdater:
    """
    Data Pipeline สำหรับอัพเดทข้อมูลหุ้น
    
    Features:
    - Incremental Update (ดึงเฉพาะใหม่)
    - Parquet Storage (ประหยัดพื้นที่ 10x กว่า CSV)
    - Deduplication (ลบข้อมูลซ้ำ)
    - Error Recovery (ข้ามหุ้นที่ error)
    """
    
    def __init__(self, data_dir=DATA_DIR):
        """
        Args:
            data_dir: โฟลเดอร์เก็บข้อมูล
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # เชื่อมต่อ TradingView
        print("🔌 Connecting to TradingView...")
        self.tv = TvDatafeed()
        print("✅ Connected!")
        
        self.stats = {
            'total': 0,
            'initial_load': 0,
            'incremental_update': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def get_file_path(self, symbol, exchange):
        """
        สร้าง path สำหรับ parquet file
        
        Returns:
            Path: data/stocks/PTT_SET.parquet
        """
        filename = f"{symbol}_{exchange}.parquet"
        return self.data_dir / filename
    
    def load_existing_data(self, file_path):
        """
        โหลดข้อมูลเก่าจาก parquet
        
        Returns:
            DataFrame or None
        """
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_parquet(file_path)
            df.index = pd.to_datetime(df.index)
            return df
        except Exception as e:
            print(f"      ❌ Error loading file: {e}")
            return None
    
    def fetch_data(self, symbol, exchange, n_bars):
        """
        ดึงข้อมูลจาก TradingView
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            n_bars: จำนวน bars
        
        Returns:
            DataFrame or None
        """
        try:
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=n_bars
            )
            
            if df is not None and not df.empty:
                # เพิ่ม % change
                df['pct_change'] = df['close'].pct_change() * 100
                return df
            
            return None
            
        except Exception as e:
            print(f"      ❌ Error fetching: {e}")
            return None
    
    def merge_and_deduplicate(self, old_df, new_df):
        """
        รวมข้อมูลเก่า + ใหม่ และลบข้อมูลซ้ำ
        
        Logic:
        1. Concatenate old + new
        2. Remove duplicates (keep last = ใช้ข้อมูลใหม่)
        3. Sort by date
        
        Args:
            old_df: DataFrame เก่า
            new_df: DataFrame ใหม่
        
        Returns:
            DataFrame: ข้อมูลที่รวมแล้ว
        """
        # รวมกัน
        combined = pd.concat([old_df, new_df])
        
        # ลบซ้ำ (ถ้า date เดียวกัน เก็บตัวใหม่)
        combined = combined[~combined.index.duplicated(keep='last')]
        
        # เรียงตาม date
        combined = combined.sort_index()
        
        return combined
    
    def update_stock(self, symbol, exchange, index, total):
        """
        อัพเดทข้อมูล 1 หุ้น
        
        Strategy:
        - ถ้าไม่มีไฟล์ → ดึงเต็ม (Initial Load)
        - ถ้ามีไฟล์ → ดึงเฉพาะใหม่ (Incremental Update)
        
        Args:
            symbol: รหัสหุ้น
            exchange: ตลาด
            index: ลำดับปัจจุบัน
            total: จำนวนทั้งหมด
        """
        print(f"\n[{index}/{total}] 📊 {symbol} ({exchange})")
        
        file_path = self.get_file_path(symbol, exchange)
        old_data = self.load_existing_data(file_path)
        
        # ตัดสินใจว่าจะดึงกี่ bars
        if old_data is None:
            # Case A: Initial Load
            print(f"      🆕 Initial Load - Fetching {INITIAL_BARS} bars...")
            n_bars = INITIAL_BARS
            mode = "initial"
        else:
            # Case B: Incremental Update
            old_count = len(old_data)
            latest_date = old_data.index[-1].strftime('%Y-%m-%d')
            print(f"      ♻️ Update Mode - Last date: {latest_date} ({old_count} existing bars)")
            print(f"      📥 Fetching {UPDATE_BARS} recent bars...")
            n_bars = UPDATE_BARS
            mode = "update"
        
        # ดึงข้อมูล
        new_data = self.fetch_data(symbol, exchange, n_bars)
        
        if new_data is None:
            print(f"      ❌ Failed - Skipping")
            self.stats['failed'] += 1
            return False
        
        # ประมวลผล
        if mode == "initial":
            final_data = new_data
            self.stats['initial_load'] += 1
            print(f"      ✅ Saved {len(final_data)} bars (Initial)")
        else:
            # Merge + Deduplicate
            final_data = self.merge_and_deduplicate(old_data, new_data)
            new_rows = len(final_data) - len(old_data)
            
            if new_rows > 0:
                print(f"      ✅ Added {new_rows} new bars (Total: {len(final_data)})")
                self.stats['incremental_update'] += 1
            else:
                print(f"      ⏭️ No new data (Already up-to-date)")
                self.stats['skipped'] += 1
        
        # บันทึก
        final_data.to_parquet(file_path)
        
        return True
    
    def run(self, stock_list, skip_existing=False):
        """
        รัน Data Pipeline สำหรับหุ้นทั้งหมด
        
        Args:
            stock_list: List of {'symbol': 'PTT', 'exchange': 'SET'}
            skip_existing: ถ้า True จะข้ามหุ้นที่มีไฟล์อยู่แล้ว
        """
        print("\n" + "="*70)
        print("🚀 Stock Data Pipeline - Starting Update")
        print("="*70)
        print(f"📁 Data Directory: {self.data_dir}")
        print(f"📊 Target Stocks: {len(stock_list)}")
        
        # ========================================
        # Incremental Download Logic
        # ========================================
        
        if skip_existing:
            print(f"⚙️ Mode: Incremental (Skip Existing)")
            
            # 1. Scan existing files
            existing_files = list(self.data_dir.glob("*.parquet"))
            existing_symbols = set()
            
            for file in existing_files:
                # Extract symbol from filename (e.g., PTT_SET.parquet -> PTT)
                symbol = file.stem.split('_')[0]
                existing_symbols.add(symbol)
            
            # 2. Filter missing stocks
            missing_stocks = [
                stock for stock in stock_list 
                if stock['symbol'] not in existing_symbols
            ]
            
            # 3. Summary
            print(f"📦 Found {len(existing_files)} existing files")
            print(f"⬇️ Downloading {len(missing_stocks)} missing stocks...")
            
            # Update stock list to only missing ones
            stock_list = missing_stocks
            
            if not stock_list:
                print("✅ All stocks already downloaded!")
                return
        else:
            print(f"⚙️ Mode: Full Update (All Stocks)")
        
        print(f"⏱️ Rate Limit: {RATE_LIMIT_SECONDS} sec/stock")
        print("="*70)
        
        start_time = time.time()
        self.stats['total'] = len(stock_list)
        
        for idx, stock in enumerate(stock_list, 1):
            try:
                self.update_stock(
                    stock['symbol'],
                    stock['exchange'],
                    idx,
                    len(stock_list)
                )
            except Exception as e:
                print(f"      ❌ Unexpected error: {e}")
                self.stats['failed'] += 1
            
            # Rate Limiting (ยกเว้นตัวสุดท้าย)
            if idx < len(stock_list):
                time.sleep(RATE_LIMIT_SECONDS)
        
        elapsed = time.time() - start_time
        
        # สรุปผลลัพธ์
        self.print_summary(elapsed)
    
    def print_summary(self, elapsed):
        """
        แสดงสรุปผลการทำงาน
        """
        print("\n" + "="*70)
        print("📊 Update Summary")
        print("="*70)
        print(f"✅ Completed: {self.stats['total']} stocks")
        print(f"   🆕 Initial Load: {self.stats['initial_load']} stocks")
        print(f"   ♻️ Incremental Update: {self.stats['incremental_update']} stocks")
        print(f"   ⏭️ Already Up-to-date: {self.stats['skipped']} stocks")
        print(f"   ❌ Failed: {self.stats['failed']} stocks")
        print(f"\n⏱️ Time Elapsed: {elapsed:.1f} seconds")
        print(f"   Average: {elapsed/self.stats['total']:.1f} sec/stock")
        print("="*70)
        
        # ตรวจสอบไฟล์ที่สร้าง
        parquet_files = list(self.data_dir.glob("*.parquet"))
        total_size = sum(f.stat().st_size for f in parquet_files)
        
        print(f"\n💾 Storage:")
        print(f"   Files: {len(parquet_files)} parquet files")
        print(f"   Total Size: {total_size / 1024 / 1024:.2f} MB")
        print(f"   Location: {self.data_dir}")
        print("="*70)


def main(skip_existing=True):
    """
    Main execution
    
    Args:
        skip_existing: ถ้า True จะข้ามหุ้นที่มีไฟล์แล้ว (Default: True)
    """
    print("\n🎯 Stock Data Updater")
    print(f"📅 Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # สร้าง updater
    updater = StockDataUpdater(data_dir=DATA_DIR)
    
    # รัน pipeline
    updater.run(STOCK_LIST, skip_existing=skip_existing)
    
    print("\n✅ Data Pipeline Complete!")
    print("💡 Tip: รันทุกวันเพื่ออัพเดทข้อมูลใหม่\n")


if __name__ == "__main__":
    import sys
    
    # Check command line args
    skip_existing = True  # Default
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            skip_existing = False
            print("🔄 Running in FULL mode (update all stocks)")
        elif sys.argv[1] == "--skip":
            skip_existing = True
            print("⚡ Running in INCREMENTAL mode (skip existing)")
    
    main(skip_existing=skip_existing)
