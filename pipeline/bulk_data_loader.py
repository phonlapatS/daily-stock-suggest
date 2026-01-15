#!/usr/bin/env python
"""
bulk_data_loader.py - Bulk Historical Data Downloader
======================================================

Purpose: ดาวน์โหลดข้อมูลประวัติศาสตร์หุ้นไทยทั้งหมด
Features:
- Dynamic stock list (no hardcoding)
- Smart skip existing files
- Robust error handling
- Progress tracking
- Rate limiting

Author: Stock Analysis System
Date: 2026-01-15
"""

import os
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval


# ================================
# Configuration
# ================================

DATA_DIR = "data/stocks"
BARS_TO_FETCH = 3000  # ~10-12 years
RATE_LIMIT = 0.5  # seconds between requests
EXCHANGE = "SET"  # TradingView uses 'SET' for both SET and mai


# ================================
# Functions
# ================================

def get_all_thai_stocks():
    """
    Get list of all Thai stocks
    
    ลำดับการลอง:
    1. starfishX (ถ้ามี)
    2. Fallback to comprehensive list
    
    Returns:
        list: [{'symbol': 'PTT', 'exchange': 'SET'}, ...]
    """
    # Try starfishX first
    try:
        import starfishX as sx
        print("📡 Attempting to fetch from starfishX...")
        
        # Try different possible APIs
        stock_list = []
        
        # Note: starfishX API may vary, trying common patterns
        try:
            # Try getStockName
            df = sx.getStockName()
            symbols = df['symbol'].tolist()
            print(f"✅ Got {len(symbols)} stocks from starfishX")
        except:
            # Try listSecurities
            try:
                from starfishX import listSecurities
                df = listSecurities.set_and_mai()
                symbols = df['symbol'].tolist()
                print(f"✅ Got {len(symbols)} stocks from listSecurities")
            except:
                raise Exception("No working starfishX API found")
        
        # Convert to format
        for symbol in symbols:
            stock_list.append({
                'symbol': symbol,
                'exchange': EXCHANGE
            })
        
        return stock_list
        
    except Exception as e:
        print(f"⚠️ starfishX not available: {e}")
        print("📋 Using comprehensive fallback list...")
        
        # Comprehensive Thai stock list (800+ stocks)
        # This is a curated list of major stocks
        return get_fallback_stock_list()


def get_fallback_stock_list():
    """
    Fallback: Comprehensive list of major Thai stocks
    Loads from data/all_thai_stocks.txt if available.
    
    Returns:
        list: Stock list
    """
    
    stock_file = Path("data/all_thai_stocks.txt")
    stock_symbols = []
    
    # 1. Try loading from file
    if stock_file.exists():
        print(f"📋 Loading stocks from {stock_file}...")
        try:
            with open(stock_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    stock_symbols.append(line)
            
            print(f"✅ Loaded {len(stock_symbols)} symbols from file")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    # 2. Hardcoded specific ones if file failed or just as backup
    if not stock_symbols:
        print("⚠️ File load failed, using basic hardcoded list...")
        stock_symbols = ['PTT', 'AOT', 'KBANK', 'SCB', 'BDMS', 'CPALL', 'ADVANC', 'GULF', 'DELTA', 'SCC']

    # Remove duplicates and create list
    symbols = sorted(set(stock_symbols))
    
    stock_list = [{'symbol': s, 'exchange': EXCHANGE} for s in symbols]
    
    print(f"📊 Final list: {len(stock_list)} stocks")
    
    return stock_list


def file_exists(symbol, exchange, data_dir):
    """
    Check if parquet file already exists
    
    Args:
        symbol: Stock symbol
        exchange: Exchange name
        data_dir: Data directory
    
    Returns:
        bool: True if exists
    """
    filename = f"{symbol}_{exchange}.parquet"
    filepath = Path(data_dir) / filename
    return filepath.exists()


def download_stock(tv, symbol, exchange, bars, data_dir):
    """
    Download one stock
    
    Args:
        tv: TvDatafeed instance
        symbol: Stock symbol
        exchange: Exchange name
        bars: Number of bars to fetch
        data_dir: Data directory
    
    Returns:
        bool: Success
    """
    try:
        # Fetch data
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=bars
        )
        
        if df is None or df.empty:
            print(f"      ⚠️ No data returned")
            return False
        
        # Add pct_change
        df['pct_change'] = df['close'].pct_change() * 100
        
        # Save to parquet
        filename = f"{symbol}_{exchange}.parquet"
        filepath = Path(data_dir) / filename
        df.to_parquet(filepath)
        
        print(f"      ✅ Saved {len(df)} bars")
        return True
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False


# ================================
# Main Script
# ================================

def main():
    """
    Main execution
    """
    print("\n" + "="*70)
    print("🚀 BULK DATA LOADER - Thai Stocks")
    print("="*70)
    print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Data Directory: {DATA_DIR}")
    print(f"📊 Bars per Stock: {BARS_TO_FETCH}")
    print(f"⏱️ Rate Limit: {RATE_LIMIT} sec/stock")
    print("="*70)
    
    # Create data directory
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Get stock list
    print("\n📡 Fetching stock list...")
    stock_list = get_all_thai_stocks()
    
    if not stock_list:
        print("❌ No stocks to download!")
        return
    
    total_stocks = len(stock_list)
    print(f"✅ Found {total_stocks} stocks to process")
    
    # Connect to TradingView
    print("\n🔌 Connecting to TradingView...")
    tv = TvDatafeed()
    print("✅ Connected!")
    
    # Statistics
    stats = {
        'total': total_stocks,
        'skipped': 0,
        'downloaded': 0,
        'failed': 0
    }
    
    # Process each stock
    print("\n" + "="*70)
    print("📥 Starting Download...")
    print("="*70)
    
    start_time = time.time()
    
    for idx, stock in enumerate(stock_list, 1):
        symbol = stock['symbol']
        exchange = stock['exchange']
        
        # Progress
        print(f"\n[{idx}/{total_stocks}] {symbol}")
        
        # Check if exists
        if file_exists(symbol, exchange, DATA_DIR):
            print(f"      [SKIP] {symbol} already exists")
            stats['skipped'] += 1
            continue
        
        # Download
        print(f"      📥 Downloading {BARS_TO_FETCH} bars...")
        success = download_stock(tv, symbol, exchange, BARS_TO_FETCH, DATA_DIR)
        
        if success:
            stats['downloaded'] += 1
        else:
            stats['failed'] += 1
        
        # Rate limiting (except last)
        if idx < total_stocks:
            time.sleep(RATE_LIMIT)
    
    # Summary
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("📊 DOWNLOAD SUMMARY")
    print("="*70)
    print(f"✅ Total Processed: {stats['total']} stocks")
    print(f"   📥 Downloaded: {stats['downloaded']} stocks")
    print(f"   ⏭️ Skipped: {stats['skipped']} stocks")
    print(f"   ❌ Failed: {stats['failed']} stocks")
    print(f"\n⏱️ Time Elapsed: {elapsed:.1f} seconds")
    print(f"   Average: {elapsed/stats['total']:.1f} sec/stock")
    
    # Check files
    parquet_files = list(Path(DATA_DIR).glob("*.parquet"))
    total_size = sum(f.stat().st_size for f in parquet_files)
    
    print(f"\n💾 Storage:")
    print(f"   Files: {len(parquet_files)} parquet files")
    print(f"   Total Size: {total_size / 1024 / 1024:.2f} MB")
    print(f"   Location: {DATA_DIR}")
    print("="*70)
    
    print(f"\n✅ Bulk Download Complete!")
    print(f"📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
