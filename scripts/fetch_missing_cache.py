"""
scripts/fetch_missing_cache.py
==============================
Fetch missing cache files for symbols that don't have cache yet.

Usage:
    python scripts/fetch_missing_cache.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from tvDatafeed import TvDatafeed, Interval
from core.data_cache import has_cache, save_cache, get_data_with_cache
import time

def find_missing_cache():
    """Find symbols that don't have cache."""
    missing = []
    for group_name, group_config in config.ASSET_GROUPS.items():
        for asset in group_config['assets']:
            symbol = asset['symbol']
            exchange = asset.get('exchange', 'SET')
            if not has_cache(symbol, exchange):
                missing.append((symbol, exchange, group_name))
    return missing

def fetch_missing_symbols():
    """Fetch data for symbols that don't have cache."""
    print("="*80)
    print("Fetching Missing Cache Files")
    print("="*80)
    
    missing = find_missing_cache()
    
    if not missing:
        print("✅ All symbols have cache!")
        return
    
    print(f"\nFound {len(missing)} symbols without cache:")
    for symbol, exchange, group in missing:
        print(f"  {symbol:15} ({exchange:8}) - {group}")
    
    print(f"\n{'='*80}")
    print("Connecting to TradingView...")
    print("="*80)
    
    try:
        tv = TvDatafeed()
        print("✅ Connected to TradingView")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\n{'='*80}")
    print(f"Fetching {len(missing)} symbols...")
    print("="*80)
    
    success = 0
    failed = 0
    
    for i, (symbol, exchange, group) in enumerate(missing, 1):
        print(f"\n[{i}/{len(missing)}] Fetching {symbol} ({exchange})...")
        
        try:
            # Try to fetch data
            df = get_data_with_cache(tv, symbol, exchange, Interval.in_daily, 5000, 50)
            
            if df is not None and not df.empty:
                print(f"  ✅ Success: {len(df)} bars cached")
                success += 1
            else:
                print(f"  ❌ Failed: No data returned")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n{'='*80}")
    print("Summary:")
    print(f"  ✅ Success: {success}")
    print(f"  ❌ Failed: {failed}")
    print(f"{'='*80}")

if __name__ == "__main__":
    fetch_missing_symbols()

