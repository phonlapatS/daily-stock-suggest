"""
core/market_time.py - Market Close Time Checker
================================================
เช็คว่าตลาดปิดหรือยัง สำหรับแต่ละตลาด
แสดงเวลาใน ICT (Thailand timezone) เพื่อความสะดวก
"""

from datetime import datetime, time, timedelta
import pytz

# Market Close Times (Local Time of each market)
MARKET_CLOSE_TIMES = {
    'SET': time(16, 30),      # Thailand: 16:30 ICT (UTC+7) = 16:30 น.
    'MAI': time(16, 30),      # Thailand: 16:30 ICT (UTC+7) = 16:30 น.
    'NASDAQ': time(16, 0),    # US: 16:00 EST/EDT = ~03:00-04:00 ICT (วันถัดไป)
    'NYSE': time(16, 0),      # US: 16:00 EST/EDT = ~03:00-04:00 ICT (วันถัดไป)
    'TWSE': time(13, 30),     # Taiwan: 13:30 CST (UTC+8) = 12:30 ICT
    'HKEX': time(16, 0),      # Hong Kong: 16:00 HKT (UTC+8) = 15:00 ICT
    'SHSE': time(15, 0),      # Shanghai: 15:00 CST (UTC+8) = 14:00 ICT
    'SZSE': time(15, 0),      # Shenzhen: 15:00 CST (UTC+8) = 14:00 ICT
}

# Market Timezones
MARKET_TIMEZONES = {
    'SET': pytz.timezone('Asia/Bangkok'),      # UTC+7 (ICT)
    'MAI': pytz.timezone('Asia/Bangkok'),      # UTC+7 (ICT)
    'NASDAQ': pytz.timezone('America/New_York'), # EST/EDT (UTC-5/-4)
    'NYSE': pytz.timezone('America/New_York'),   # EST/EDT (UTC-5/-4)
    'TWSE': pytz.timezone('Asia/Taipei'),       # UTC+8 (CST)
    'HKEX': pytz.timezone('Asia/Hong_Kong'),    # UTC+8 (HKT)
    'SHSE': pytz.timezone('Asia/Shanghai'),     # UTC+8 (CST)
    'SZSE': pytz.timezone('Asia/Shanghai'),     # UTC+8 (CST)
}

# Thailand timezone (ICT) for reference
ICT_TZ = pytz.timezone('Asia/Bangkok')

def get_market_close_time(exchange):
    """
    Get market close time for an exchange.
    
    Args:
        exchange: Exchange code (e.g., 'SET', 'NASDAQ')
    
    Returns:
        time object or None if not found
    """
    exchange_upper = exchange.upper()
    
    # Try exact match first
    if exchange_upper in MARKET_CLOSE_TIMES:
        return MARKET_CLOSE_TIMES[exchange_upper]
    
    # Try partial match (e.g., 'SET' in 'SET100')
    for key, close_time in MARKET_CLOSE_TIMES.items():
        if key in exchange_upper or exchange_upper in key:
            return close_time
    
    # Default: assume 16:00 local time
    return time(16, 0)

def get_market_timezone(exchange):
    """
    Get market timezone for an exchange.
    
    Args:
        exchange: Exchange code (e.g., 'SET', 'NASDAQ')
    
    Returns:
        pytz timezone object or None if not found
    """
    exchange_upper = exchange.upper()
    
    # Try exact match first
    if exchange_upper in MARKET_TIMEZONES:
        return MARKET_TIMEZONES[exchange_upper]
    
    # Try partial match
    for key, tz in MARKET_TIMEZONES.items():
        if key in exchange_upper or exchange_upper in key:
            return tz
    
    # Default: UTC
    return pytz.UTC

def get_market_close_time_ict(exchange):
    """
    แปลงเวลาปิดตลาดเป็น ICT (Thailand timezone)
    
    Args:
        exchange: Exchange code (e.g., 'SET', 'NASDAQ')
    
    Returns:
        tuple: (close_time_ict: time, close_time_str: str)
    """
    market_tz = get_market_timezone(exchange)
    close_time_local = get_market_close_time(exchange)
    
    if market_tz is None or close_time_local is None:
        return None, "Unknown"
    
    # Create a datetime object for today with market's close time
    now = datetime.now()
    market_now = market_tz.localize(datetime.combine(now.date(), close_time_local))
    
    # Convert to ICT
    ict_time = market_now.astimezone(ICT_TZ)
    close_time_ict = ict_time.time()
    close_time_str = f"{close_time_ict.hour:02d}:{close_time_ict.minute:02d} ICT"
    
    return close_time_ict, close_time_str

def is_market_closed(exchange, check_time=None):
    """
    เช็คว่าตลาดปิดหรือยัง (เช็คตาม timezone ของแต่ละตลาด)
    
    Args:
        exchange: Exchange code (e.g., 'SET', 'NASDAQ')
        check_time: datetime object to check (default: now)
    
    Returns:
        tuple: (is_closed: bool, status_msg: str, close_time_ict: str)
    """
    if check_time is None:
        check_time = datetime.now(ICT_TZ)  # Use ICT as base
    elif check_time.tzinfo is None:
        check_time = ICT_TZ.localize(check_time)
    
    # Get market timezone
    market_tz = get_market_timezone(exchange)
    if market_tz is None:
        return (False, "Unknown market (assume open)", "Unknown")
    
    # Convert check_time to market timezone
    market_time = check_time.astimezone(market_tz)
    
    # Get close time
    close_time = get_market_close_time(exchange)
    if close_time is None:
        return (False, "Unknown close time (assume open)", "Unknown")
    
    # Get close time in ICT for display
    _, close_time_ict_str = get_market_close_time_ict(exchange)
    
    # Check if current time >= close time (in market's local time)
    current_time = market_time.time()
    is_closed = current_time >= close_time
    
    if is_closed:
        status_msg = f"Market closed (closes at {close_time_ict_str})"
    else:
        # Calculate hours until close
        close_datetime = market_tz.localize(
            datetime.combine(market_time.date(), close_time)
        )
        if current_time > close_time:
            # Close time already passed today, check tomorrow
            close_datetime = market_tz.localize(
                datetime.combine((market_time + datetime.timedelta(days=1)).date(), close_time)
            )
        
        time_until_close = close_datetime - market_time
        hours = time_until_close.total_seconds() / 3600
        if hours < 24:
            status_msg = f"Market still open (closes at {close_time_ict_str}, {hours:.1f}h remaining)"
        else:
            status_msg = f"Market still open (closes at {close_time_ict_str} tomorrow)"
    
    return (is_closed, status_msg, close_time_ict_str)

def should_skip_symbol(symbol, exchange, forecast_df=None, perf_log_df=None):
    """
    เช็คว่าควร skip symbol นี้หรือไม่
    
    Logic:
    1. เช็คว่ามีข้อมูลการทายวันพรุ่งนี้แล้วหรือยัง
    2. ถ้ามีแล้ว → เช็คว่าตลาดปิดหรือยัง
    3. ถ้ายังไม่ปิด → skip (รอให้ตลาดปิดก่อน)
    4. ถ้าปิดแล้ว → ไม่ skip (สามารถทายใหม่ได้)
    
    Args:
        symbol: Symbol to check
        exchange: Exchange code
        forecast_df: DataFrame from forecast_tomorrow.csv (optional)
        perf_log_df: DataFrame from performance_log.csv (optional)
    
    Returns:
        tuple: (should_skip: bool, reason: str)
    """
    from datetime import timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Check if forecast exists for tomorrow
    has_forecast = False
    
    if forecast_df is not None and not forecast_df.empty:
        if 'symbol' in forecast_df.columns:
            # Check if symbol has forecast for tomorrow
            symbol_forecasts = forecast_df[forecast_df['symbol'].str.upper() == symbol.upper()]
            if not symbol_forecasts.empty:
                # Check target_date if available
                if 'target_date' in forecast_df.columns:
                    has_forecast = tomorrow in symbol_forecasts['target_date'].values
                else:
                    # Assume forecast is for tomorrow if file is recent
                    has_forecast = True
    
    if perf_log_df is not None and not perf_log_df.empty:
        if 'symbol' in perf_log_df.columns and 'target_date' in perf_log_df.columns:
            symbol_logs = perf_log_df[
                (perf_log_df['symbol'].str.upper() == symbol.upper()) &
                (perf_log_df['target_date'] == tomorrow)
            ]
            if not symbol_logs.empty:
                has_forecast = True
    
    # If no forecast exists → don't skip (need to fetch)
    if not has_forecast:
        return (False, "No forecast exists")
    
    # If forecast exists → check if market is closed
    is_closed, status_msg, close_time_ict = is_market_closed(exchange)
    
    if is_closed:
        # Market closed → can update forecast
        return (False, f"Market closed (closes at {close_time_ict}), can update")
    else:
        # Market still open → skip (wait for market close)
        return (True, status_msg)

