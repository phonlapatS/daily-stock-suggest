"""
core/data_cache.py - Local OHLC Data Cache Manager (V3 - Performance)
=====================================================================
V3 Changes (Performance Fix):
- Cache-Only Mode: skip network when connection is known bad
- Single-attempt fetch: no more progressive 3-step fallback
- Connection state tracking: auto-switch to cache-only after failures
- Reduced timeout waste: ~90s → ~10s per failed symbol
"""
import os
import glob
import pandas as pd
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache Configuration
CACHE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache")
)
MAX_DATA_AGE_DAYS = 3       # Cache สดถ้าข้อมูลล่าสุดไม่เกิน 3 วัน (covers weekends)
MAX_CACHE_BARS = 5500       # จำกัดขนาด cache ไม่ให้บวมเกิน
RATE_LIMIT_DELTA = 0.3      # delay หลัง delta fetch (s)
RATE_LIMIT_FULL = 0.5       # delay หลัง full fetch (s)

# ===================================================================
# CONNECTION STATE TRACKER
# ===================================================================
_connection_state = {
    'healthy': True,
    'consecutive_failures': 0,
    'failure_threshold': 3,    # Switch to cache-only after 3 consecutive failures
}

def is_connection_healthy():
    """Check if connection is currently considered healthy."""
    return _connection_state['healthy']

def report_fetch_success():
    """Report a successful fetch to reset failure counter."""
    _connection_state['consecutive_failures'] = 0
    _connection_state['healthy'] = True

def report_fetch_failure():
    """Report a failed fetch. Auto-switches to cache-only after threshold."""
    _connection_state['consecutive_failures'] += 1
    if _connection_state['consecutive_failures'] >= _connection_state['failure_threshold']:
        _connection_state['healthy'] = False

def set_connection_healthy(healthy):
    """Manually set connection state (from health check)."""
    _connection_state['healthy'] = healthy
    if not healthy:
        _connection_state['consecutive_failures'] = _connection_state['failure_threshold']

# ===================================================================
# CACHE FILE OPERATIONS
# ===================================================================
def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(symbol, exchange):
    """Get the file path for a symbol's cache."""
    ensure_cache_dir()
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    return os.path.normpath(os.path.join(CACHE_DIR, f"{exchange}_{safe_symbol}.csv"))

def cleanup_legacy_pkl():
    """Auto-convert legacy .pkl files to .csv and remove them."""
    ensure_cache_dir()
    pkl_files = glob.glob(os.path.join(CACHE_DIR, "*.pkl"))
    converted = 0
    for pkl_path in pkl_files:
        try:
            df = pd.read_pickle(pkl_path)
            basename = os.path.basename(pkl_path).replace(".pkl", "")
            parts = basename.split("_")
            if len(parts) >= 2:
                csv_name = f"{parts[1]}_{parts[0]}.csv"
                csv_path = os.path.normpath(os.path.join(CACHE_DIR, csv_name))
                if not os.path.exists(csv_path):
                    df.to_csv(csv_path)
            os.remove(pkl_path)
            converted += 1
        except Exception:
            pass
    if converted > 0:
        print(f"🔄 Converted {converted} legacy .pkl cache files to .csv")

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
        if df.empty:
            return None
        return df
    except Exception:
        return None

def save_cache(symbol, exchange, df):
    """Save OHLC data to local cache."""
    cache_path = get_cache_path(symbol, exchange)
    try:
        df.to_csv(cache_path)
        return True
    except Exception:
        return False

def get_last_cached_date(symbol, exchange):
    """Get the last date in the cache."""
    df = load_cache(symbol, exchange)
    if df is None or df.empty:
        return None
    return df.index[-1]

def is_cache_fresh(symbol, exchange):
    """
    Smart Stale Check: ดูจาก "วันล่าสุดของข้อมูล" แทน file timestamp
    ครอบคลุม weekend (ศุกร์ปิดตลาด → จันทร์รันก็ยังสดอยู่)
    """
    cached = load_cache(symbol, exchange)
    if cached is None or cached.empty:
        return False
    try:
        last_date = pd.Timestamp(cached.index[-1])
        now = pd.Timestamp(datetime.now())
        days_old = (now - last_date).days
        return days_old <= MAX_DATA_AGE_DAYS
    except Exception:
        return False

def update_cache(symbol, exchange, new_df):
    """Update cache with new data (merge existing + new, deduplicate)."""
    existing = load_cache(symbol, exchange)
    
    if existing is None or existing.empty:
        save_cache(symbol, exchange, new_df)
        return new_df
    
    combined = pd.concat([existing, new_df])
    combined = combined[~combined.index.duplicated(keep='last')]
    combined = combined.sort_index()
    
    if len(combined) > MAX_CACHE_BARS:
        combined = combined.tail(MAX_CACHE_BARS)
    
    save_cache(symbol, exchange, combined)
    return combined

# ===================================================================
# SAFE FETCH: Single attempt with graceful error handling
# ===================================================================
def safe_fetch(tv, symbol, exchange, interval, n_bars, delay=RATE_LIMIT_DELTA):
    """
    Safely fetch data from TradingView. Returns None on any error.
    Single attempt only — no internal retry.
    """
    try:
        time.sleep(delay)
        data = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=n_bars
        )
        if data is not None and not data.empty:
            report_fetch_success()
            return data
        report_fetch_failure()
        return None
    except Exception:
        report_fetch_failure()
        return None

# ===================================================================
# MAIN ENTRY POINT: Smart data fetching with cache
# ===================================================================
def get_data_with_cache(tv, symbol, exchange, interval, full_bars=5000, delta_bars=50):
    """
    Smart data fetching with cache (V3 - Performance).
    
    Strategy:
    1. Connection bad → return cache immediately (no network)
    2. Has cache + Fresh → Delta fetch (1 attempt), fallback to cache
    3. Has cache + Stale → Delta fetch (1 attempt), fallback to stale cache
    4. No cache → Single full fetch (1 attempt)
    5. Everything fails → None
    
    Key change from V2: NO progressive_fetch (was 3 attempts).
    Network failure = use cache. No cache = skip.
    """
    cached = load_cache(symbol, exchange) if has_cache(symbol, exchange) else None
    
    # === FAST PATH: Connection is bad → use cache directly ===
    if not is_connection_healthy():
        if cached is not None and not cached.empty:
            return cached
        return None  # No cache + no connection = skip
    
    # === Connection is healthy: try to fetch ===
    if cached is not None and not cached.empty:
        # Has cache → try delta only (fast, 50 bars)
        new_data = safe_fetch(tv, symbol, exchange, interval, delta_bars)
        if new_data is not None:
            return update_cache(symbol, exchange, new_data)
        else:
            # Delta failed → use existing cache (still valid data)
            return cached
    else:
        # No cache → single full fetch attempt
        full_data = safe_fetch(tv, symbol, exchange, interval, full_bars, delay=RATE_LIMIT_FULL)
        if full_data is not None:
            save_cache(symbol, exchange, full_data)
            return full_data
        return None  # Complete failure

# ===================================================================
# CONNECTION HEALTH CHECK
# ===================================================================
def check_connection_health(tv, test_symbol="AAPL", test_exchange="NASDAQ"):
    """
    Quick health check: try to fetch 5 bars from a known symbol.
    Sets connection state accordingly.
    """
    data = safe_fetch(tv, test_symbol, test_exchange, None, 5, delay=0.1)
    healthy = data is not None
    set_connection_healthy(healthy)
    return healthy

# ===================================================================
# CACHE STATISTICS
# ===================================================================
def get_cache_stats():
    """Get statistics about the cache."""
    ensure_cache_dir()
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.csv')]
    
    total_size = 0
    fresh = 0
    stale = 0
    
    for f in files:
        path = os.path.join(CACHE_DIR, f)
        total_size += os.path.getsize(path)
        
        parts = f.replace(".csv", "").split("_", 1)
        if len(parts) == 2:
            exchange, symbol = parts
            if is_cache_fresh(symbol, exchange):
                fresh += 1
            else:
                stale += 1
    
    return {
        'total_files': len(files),
        'fresh': fresh,
        'stale': stale,
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
