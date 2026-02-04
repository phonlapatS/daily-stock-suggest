"""
core/data_cache.py - Local OHLC Data Cache Manager
===================================================
Stores raw OHLC data locally to avoid fetching 5000 bars every run.
Only fetches delta (new bars) when cache exists.
"""
import os
import pandas as pd
from datetime import datetime, timedelta

# Cache Configuration
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
CACHE_STALE_HOURS = 12  # Consider cache stale after 12 hours

def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(symbol, exchange):
    """Get the file path for a symbol's cache."""
    ensure_cache_dir()
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    return os.path.join(CACHE_DIR, f"{exchange}_{safe_symbol}.csv")

def has_cache(symbol, exchange):
    """Check if cache exists for a symbol."""
    return os.path.exists(get_cache_path(symbol, exchange))

def load_cache(symbol, exchange):
    """Load cached OHLC data for a symbol."""
    cache_path = get_cache_path(symbol, exchange)
    if not os.path.exists(cache_path):
        return None
    
    try:
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        return df
    except Exception as e:
        print(f"⚠️ Cache read error for {symbol}: {e}")
        return None

def save_cache(symbol, exchange, df):
    """Save OHLC data to local cache."""
    cache_path = get_cache_path(symbol, exchange)
    try:
        df.to_csv(cache_path)
        return True
    except Exception as e:
        print(f"⚠️ Cache write error for {symbol}: {e}")
        return False

def get_last_cached_date(symbol, exchange):
    """Get the last date in the cache."""
    df = load_cache(symbol, exchange)
    if df is None or df.empty:
        return None
    return df.index[-1]

def is_cache_stale(symbol, exchange):
    """Check if cache needs updating (older than CACHE_STALE_HOURS)."""
    cache_path = get_cache_path(symbol, exchange)
    if not os.path.exists(cache_path):
        return True
    
    # Check file modification time
    mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
    age = datetime.now() - mtime
    return age > timedelta(hours=CACHE_STALE_HOURS)

def update_cache(symbol, exchange, new_df):
    """
    Update cache with new data.
    If cache exists, append only new rows.
    If no cache, save entire DataFrame.
    """
    existing = load_cache(symbol, exchange)
    
    if existing is None or existing.empty:
        # No cache - save entire DataFrame
        save_cache(symbol, exchange, new_df)
        return new_df
    
    # Merge: keep existing + add new rows
    # Use index (datetime) to avoid duplicates
    combined = pd.concat([existing, new_df])
    combined = combined[~combined.index.duplicated(keep='last')]
    combined = combined.sort_index()
    
    # Limit to last 5500 bars to prevent unbounded growth
    if len(combined) > 5500:
        combined = combined.tail(5500)
    
    save_cache(symbol, exchange, combined)
    return combined

def get_data_with_cache(tv, symbol, exchange, interval, full_bars=5000, delta_bars=50):
    """
    Smart data fetching with cache.
    
    Args:
        tv: TvDatafeed instance
        symbol: Stock symbol
        exchange: Exchange name
        interval: Timeframe interval
        full_bars: Number of bars for initial full fetch
        delta_bars: Number of bars for incremental fetch
    
    Returns:
        DataFrame with OHLC data (from cache + delta)
    """
    import time
    
    # Check if cache exists and is fresh
    if has_cache(symbol, exchange) and not is_cache_stale(symbol, exchange):
        # Cache exists - just fetch delta (recent bars)
        cached = load_cache(symbol, exchange)
        
        try:
            time.sleep(0.5)  # Rate limit
            new_data = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=delta_bars
            )
            
            if new_data is not None and not new_data.empty:
                # Merge with cache
                combined = update_cache(symbol, exchange, new_data)
                return combined
            else:
                # Fetch failed, return cached data
                return cached
                
        except Exception as e:
            # On error, return cached data
            return cached
    
    else:
        # No cache or stale - do full fetch
        try:
            time.sleep(1.0)  # Rate limit (longer for full fetch)
            full_data = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=full_bars
            )
            
            if full_data is not None and not full_data.empty:
                save_cache(symbol, exchange, full_data)
                return full_data
            else:
                return None
                
        except Exception as e:
            # Try to return stale cache if exists
            cached = load_cache(symbol, exchange)
            return cached

def get_cache_stats():
    """Get statistics about the cache."""
    ensure_cache_dir()
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.csv')]
    
    total_size = 0
    for f in files:
        path = os.path.join(CACHE_DIR, f)
        total_size += os.path.getsize(path)
    
    return {
        'total_files': len(files),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'cache_dir': CACHE_DIR
    }

def clear_cache():
    """Clear all cached data."""
    ensure_cache_dir()
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.csv')]
    for f in files:
        os.remove(os.path.join(CACHE_DIR, f))
    return len(files)
