#!/usr/bin/env python
"""
incremental_update.py - Smart Cache Update Script
==================================================
ดึงเฉพาะข้อมูลใหม่ที่ขาดหายไป แทนการ Reload ทั้งหมด

Usage:
    python scripts/incremental_update.py

เวลาโดยประมาณ: 15-20 นาที (แทน 2+ ชั่วโมง)
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
from utils.cache_manager import CacheManager, print_cache_summary
import config

def run_incremental_update():
    """Run incremental update for all asset groups"""
    start_time = time.time()
    
    print("=" * 70)
    print(f"INCREMENTAL CACHE UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Initialize
    tv = TvDatafeed()
    cache_mgr = CacheManager()
    
    # Stats
    total_assets = 0
    updated = 0
    skipped = 0
    errors = 0
    
    # Process each group
    for group_name, settings in config.ASSET_GROUPS.items():
        print(f"\n📊 {group_name}: {settings.get('description', '')}")
        print("-" * 50)
        
        assets = settings.get('assets', [])
        interval = settings.get('interval', Interval.in_daily)
        min_bars = settings.get('history_bars', 5000)
        
        # Determine interval string
        if interval == Interval.in_daily:
            interval_str = "daily"
        elif interval == Interval.in_30_minute:
            interval_str = "30m"
        elif interval == Interval.in_15_minute:
            interval_str = "15m"
        else:
            interval_str = "other"
        
        for asset in assets:
            total_assets += 1
            symbol = asset.get('symbol') if isinstance(asset, dict) else asset
            exchange = asset.get('exchange', 'SET') if isinstance(asset, dict) else 'SET'
            name = asset.get('name', symbol) if isinstance(asset, dict) else symbol
            
            try:
                # Check cache status first
                status = cache_mgr.get_cache_status(symbol, exchange, interval_str)
                
                if not status['needs_update']:
                    print(f"  ✅ {name:<15} | Up-to-date ({status['total_rows']} rows)")
                    skipped += 1
                    continue
                
                # Do incremental update
                df = cache_mgr.get_data_with_update(
                    tv, symbol, exchange, interval, 
                    min_bars=min_bars, interval_str=interval_str
                )
                
                if df is not None and not df.empty:
                    print(f"  ⬆️  {name:<15} | Updated to {len(df)} rows")
                    updated += 1
                else:
                    print(f"  ⚠️  {name:<15} | No data returned")
                    errors += 1
                
                # Small delay to avoid API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ {name:<15} | Error: {str(e)[:40]}")
                errors += 1
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Assets:  {total_assets}")
    print(f"Updated:       {updated}")
    print(f"Skipped:       {skipped} (already up-to-date)")
    print(f"Errors:        {errors}")
    print(f"Time:          {elapsed/60:.1f} minutes")
    print("=" * 70)
    
    # Show final cache status
    print("\n📁 CACHE STATUS AFTER UPDATE:")
    print_cache_summary()


if __name__ == "__main__":
    run_incremental_update()
