#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py - Fractal N+1 Prediction Runner (Categorized Edition)
=============================================================
Orchestrates the entire pipeline: 
Fetch -> Process -> Categorize -> Report -> Forget.
"""
import sys
import time
import os
import pandas as pd
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed
import config
import processor
import requests
import re
from core.data_cache import (
    get_data_with_cache, 
    get_cache_stats, 
    has_cache, 
    is_cache_fresh, 
    load_cache, 
    is_connection_healthy,
    set_connection_healthy
)
from core.performance import log_forecast, verify_forecast

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Rate Limiting Config (reduced since cache handles most requests)
REQUEST_DELAY = 0.3  # V4.8: Optimized for Delta fetch
BACKOFF_BASE = 2.0   # Exponential backoff multiplier

# Import thresholds from config (V6.0 - Configurable)
# สามารถปรับได้ใน config.py โดยไม่ต้องแก้ code
MIN_MATCHES_THRESHOLD = config.MIN_MATCHES_THRESHOLD
MIN_PROB_THRESHOLD = config.MIN_PROB_THRESHOLD
USE_TIER_CLASSIFICATION = config.USE_TIER_CLASSIFICATION

def _is_true_flag(val) -> bool:
    """
    Robust boolean coercion for values coming from:
    - engine results (bool)
    - CSV Smart Resume (strings / numbers / NaN)
    """
    if val is True:
        return True
    if val is False or val is None:
        return False
    # Pandas/NumPy NaN should be treated as False
    try:
        if pd.isna(val):
            return False
    except Exception:
        pass
    if isinstance(val, (int, float)):
        return val == 1
    if isinstance(val, str):
        v = val.strip().lower()
        return v in ("true", "1", "yes", "y", "t")
    return False

def fetch_and_analyze(tv, asset_info, history_bars, interval, fixed_threshold=None):
    """
    Fetch data with smart caching and analyze.
    All retry/timeout/fallback logic is handled by data_cache.py.
    """
    symbol = asset_info['symbol']
    exchange = asset_info['exchange']
    
    try:
        df = get_data_with_cache(
            tv=tv,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            full_bars=history_bars,
            delta_bars=50
        )
        
        if df is not None and not df.empty:
            results_list = processor.analyze_asset(df, symbol=symbol, exchange=exchange, fixed_threshold=fixed_threshold)
            display_name = asset_info.get('name', symbol)
            for res in results_list:
                res['symbol'] = display_name
            return results_list
        else:
            return None # V4.8: Return None to indicate fetch failure
            
    except Exception:
        return None



def show_all_forecasts(results):
    """
    แสดงทุก forecast ที่ระบบทายมา (กรอง matches น้อยเกินไป)
    """
    if not results:
        return
    
    # Use global threshold
    MIN_MATCHES = MIN_MATCHES_THRESHOLD
    
    print("\n" + "=" * 90)
    print(f"📋 ALL FORECASTS (Filtered: matches >= {MIN_MATCHES})")
    print("=" * 90)
    
    total_before_filter = 0
    total_after_filter = 0
    
    for group_key, settings in config.ASSET_GROUPS.items():
        title = settings['description'].upper()
        
        # Add Emoji based on group key
        if "THAI" in group_key: title = f"🇹🇭 {title}"
        elif "US" in group_key: title = f"🇺🇸 {title}"
        elif "CHINA" in group_key: title = f"🇨🇳 {title}"
        elif "INDICES" in group_key: title = f"🌍 {title}"
        elif "METALS" in group_key: title = f"⚡ {title}"
        
        group_results = [r for r in results if r['group'] == group_key]
        total_before_filter += len(group_results)
        
        # Filter: matches >= MIN_MATCHES (sample size น้อยเกินไป - ดูเหมือนชนะเปล่าๆ)
        filtered_results = [r for r in group_results if r.get('matches', 0) >= MIN_MATCHES]
        total_after_filter += len(filtered_results)
        
        if not filtered_results:
            continue
        
        print(f"\n{title}")
        print("-" * 100)
        header = f"{'Symbol':<12} {'Forecast':^10} {'Bull%':>8} {'Bear%':>8} {'Matches':>8} {'Total Bars':>12} {'Tradeable':>10} {'Price':>10}"
        print(header)
        print("-" * 100)
        
        # Sort by symbol
        filtered_results.sort(key=lambda x: x.get('symbol', ''))
        
        for r in filtered_results:
            symbol = r.get('symbol', 'Unknown')
            prob = r.get('acc_score', 50.0)
            forecast = r.get('forecast_label', 'NEUTRAL')
            matches = r.get('total_events', 0)
            is_tradeable = _is_true_flag(r.get('is_tradeable', False))
            price = r.get('price', 0)
            
            tradeable_str = "✅ YES" if is_tradeable else "❌ NO"
            
            print(f"{symbol:<12} {forecast:^10} {prob:>7.1f}% {int(matches):>8} {tradeable_str:>10} {price:>10.2f}")
        
        print("-" * 100)
        filtered_count = len(filtered_results)
        skipped_count = len(group_results) - filtered_count
        if skipped_count > 0:
            print(f"Total: {filtered_count} forecasts (skipped {skipped_count} with matches < {MIN_MATCHES})")
        else:
            print(f"Total: {filtered_count} forecasts")
    
    print("\n" + "=" * 90)
    if total_before_filter > total_after_filter:
        skipped_total = total_before_filter - total_after_filter
        print(f"📊 Summary: {total_after_filter} forecasts shown (skipped {skipped_total} with matches < {MIN_MATCHES})")
    else:
        print(f"📊 Summary: {total_after_filter} forecasts shown")
    print("=" * 90)

def _show_pending_verified_forecasts():
    """
    แสดง forecast ที่ยัง pending หรือ verified จาก performance_log.csv
    เพื่อให้ user เห็น forecast ที่เคยทำนายไว้ (เช่น GILD, TMUS, WHA)
    """
    import os
    from datetime import datetime, timedelta
    from core.performance import LOG_FILE
    
    if not os.path.exists(LOG_FILE):
        return
    
    try:
        perf_df = pd.read_csv(LOG_FILE)
        if perf_df.empty:
            return
        
        # Filter: target_date = วันพรุ่งนี้ (forecast ที่ยังรอผล)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        # แสดงเฉพาะ forecast ที่ target_date = วันพรุ่งนี้ หรือ วันนี้ (ยังรอ verify)
        relevant = perf_df[
            (perf_df['target_date'] == tomorrow) | 
            ((perf_df['target_date'] == today) & (perf_df['actual'] == 'PENDING'))
        ].copy()
        
        if relevant.empty:
            return
        
        # Group by exchange/market
        pending_forecasts = []
        verified_forecasts = []
        
        for _, row in relevant.iterrows():
            forecast_data = {
                'symbol': row.get('symbol', ''),
                'exchange': row.get('exchange', ''),
                'pattern': row.get('pattern', ''),
                'forecast': row.get('forecast', ''),
                'prob': row.get('prob', 0),
                'matches': row.get('stats', 0),
                'actual': row.get('actual', 'PENDING'),
                'correct': row.get('correct', None),
                'target_date': row.get('target_date', '')
            }
            
            if row.get('actual') == 'PENDING':
                pending_forecasts.append(forecast_data)
            else:
                verified_forecasts.append(forecast_data)
        
        # แสดงเฉพาะถ้ามี forecast ที่ยัง pending หรือ verified
        if pending_forecasts or verified_forecasts:
            print("\n" + "=" * 90)
            print("📋 FORECASTS FROM FORWARD TESTING LOG")
            print("=" * 90)
            
            # Group by exchange
            from collections import defaultdict
            by_exchange = defaultdict(lambda: {'pending': [], 'verified': []})
            
            for f in pending_forecasts:
                ex = f['exchange']
                by_exchange[ex]['pending'].append(f)
            
            for f in verified_forecasts:
                ex = f['exchange']
                by_exchange[ex]['verified'].append(f)
            
            # Display by exchange
            for exchange, data in by_exchange.items():
                if not data['pending'] and not data['verified']:
                    continue
                
                # Exchange name
                if exchange == 'SET':
                    title = "🇹🇭 THAI MARKET (SET)"
                elif exchange == 'NASDAQ':
                    title = "🇺🇸 US MARKET (NASDAQ)"
                elif exchange == 'HKEX':
                    title = "🇭🇰 HONG KONG (HKEX)"
                elif exchange == 'TWSE':
                    title = "🇹🇼 TAIWAN (TWSE)"
                else:
                    title = f"📊 {exchange}"
                
                # Pending forecasts
                if data['pending']:
                    print(f"\n{title} - ⏳ PENDING")
                    print(f"{'Symbol':<12} {'Forecast':<15} {'Prob%':>8} {'Matches':>10} {'Target Date':<12}")
                    print("-" * 65)
                    for f in sorted(data['pending'], key=lambda x: (x['prob'], x['matches']), reverse=True):
                        forecast_str = f"🟢 {f['forecast']}" if f['forecast'] == 'UP' else f"🔴 {f['forecast']}"
                        print(f"{f['symbol']:<12} {forecast_str:<15} {f['prob']:>7.1f}% {f['matches']:>10} {f['target_date']:<12}")
                    print("-" * 65)
                
                # Verified forecasts (แสดงเฉพาะที่ verify แล้ววันนี้)
                if data['verified']:
                    print(f"\n{title} - ✅ VERIFIED")
                    print(f"{'Symbol':<12} {'Forecast':<15} {'Actual':<15} {'Result':<10} {'Prob%':>8}")
                    print("-" * 65)
                    for f in sorted(data['verified'], key=lambda x: x['symbol']):
                        forecast_str = f"🟢 {f['forecast']}" if f['forecast'] == 'UP' else f"🔴 {f['forecast']}"
                        actual_str = f"🟢 {f['actual']}" if f['actual'] == 'UP' else f"🔴 {f['actual']}"
                        result_str = "✅ YES" if f['correct'] == 1 else "❌ NO"
                        print(f"{f['symbol']:<12} {forecast_str:<15} {actual_str:<15} {result_str:<10} {f['prob']:>7.1f}%")
                    print("-" * 65)
            
            print("=" * 90)
    except Exception as e:
        # Silent fail - ไม่ต้องแสดง error ถ้า performance_log.csv มีปัญหา
        pass

def generate_report(results):
    """
    V5.0: Single-Gate Report
    ========================
    ใช้ is_tradeable จาก Engine เป็นเกณฑ์เดียว
    Engine ตัดสินจากข้อมูลในอดีตล้วนๆ (WR, RRR, Count)
    ไม่สนสภาพหุ้น ณ ตอนนั้น — purely data-driven
    """
    print("=" * 90)
    print(f"📊 PREDICT N+1 REPORT")
    print("=" * 90)
    
    for group_key, settings in config.ASSET_GROUPS.items():
        title = settings['description'].upper()
        
        # Add Emoji based on group key
        if "THAI" in group_key: title = f"🇹🇭 {title}"
        elif "US" in group_key: title = f"🇺🇸 {title}"
        elif "CHINA" in group_key: title = f"🇨🇳 {title}"
        elif "INDICES" in group_key: title = f"🌍 {title}"
        elif "METALS" in group_key: title = f"⚡ {title}"

        # -------------------------------------------------------------
        # 1. Forward Testing Display: แสดงทุกหุ้นที่ทำนาย (ไม่กรอง RRR)
        # -------------------------------------------------------------
        # Forward Testing = ทำนายวันพรุ่งนี้และตรวจสอบว่าทายถูกไหม
        # ไม่ใช่กรองหุ้นคุณภาพ (RRR) - นั่นคือหน้าที่ของ calculate_metrics.py
        # 
        # เกณฑ์การแสดงผล:
        #   - matches >= 30 (sample size น้อยเกินไป - ดูเหมือนชนะเปล่าๆ)
        #   - แสดงเฉพาะฝั่งที่ชนะ (prob สูงกว่า) และชนะชัดเจน (prob >= 55%, ต่างกัน >= 5%)
        #   - ไม่กรอง RRR (เพราะเราต้องการตรวจสอบว่าทายถูกไหม ไม่ใช่กรองหุ้นคุณภาพ)
        # -------------------------------------------------------------
        
        filtered_data = []
        for r in results:
            if r['group'] != group_key: continue
            
            # V4.4: Use consolidated accuracy score from voting
            prob = r.get('acc_score', 0)
            
            # Show all forecasts that meet basic probability threshold (>= 50%)
            # to ensure consistency with view_report ALL
            if prob < 50:
                continue
                
            r['_sort_prob'] = prob
            filtered_data.append(r)
        
        if not filtered_data:
            print(f"\n{title}")
            print("   (No signals found)")
            continue
            
        print(f"\n{title}")
        
        # 2. Deduplication (V4.4: Best Fit per Symbol)
        seen_keys = {}
        for r in filtered_data:
            symbol = r.get('symbol', '')
            if symbol not in seen_keys or r['_sort_prob'] > seen_keys[symbol]['_sort_prob']:
                seen_keys[symbol] = r
        
        filtered_data = list(seen_keys.values())
        
        # 3. Sorting (Prob DESC)
        filtered_data.sort(key=lambda x: -x.get('prob', 0))
        
        # 4. Table Layout - Concise Format
        header = f"{'Symbol':<15} {'Predict':^15} {'Prob%':>10}"
        
        print("-" * 45)
        print(header)
        print("-" * 45)

        for r in filtered_data:
            forecast = r.get('forecast', r.get('forecast_label', ''))
            chance = "🟢 UP" if forecast == 'UP' else "🔴 DOWN"
            
            prob_val = r.get('prob', r.get('acc_score', 0.0))
            print(f"{r['symbol']:<15} {chance:^15} {prob_val:>9.0f}%")
        print("-" * 45)

    # Export ALL results to CSV (both tradeable and not — for analysis/debug)
    df = pd.DataFrame(results)
    df.to_csv('data/forecast_tomorrow.csv', index=False, encoding='utf-8-sig')
    tradeable_count = sum(1 for r in results if _is_true_flag(r.get('is_tradeable', False)))
    print(f"\n💾 Saved {len(results)} patterns ({tradeable_count} tradeable) to data/forecast_tomorrow.csv")
    
    # V5.3: แสดง forecast ที่ยัง pending/verified จาก performance_log.csv
    _show_pending_verified_forecasts()
    
    print("\n✅ Report Generated.")

def get_auth_token(session_id):
    """
    Exchange session_id cookie for a valid auth_token by scraping the TradingView homepage.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': f'sessionid={session_id}'
    }
    try:
        response = requests.get('https://www.tradingview.com/', headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for auth_token in the page source
            match = re.search(r'"auth_token":"(.*?)"', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"⚠️ Failed to exchange Session ID for Token: {e}")
    return None

def main():
    import time
    import os
    start_time = time.time()
    
    
    print("🚀 Starting Fractal N+1 Prediction System...")
    
    # Connect TV - Prioritize Session ID for stability
    tv = TvDatafeed() # Default to guest first
    
    try:
        session_id = os.getenv("TV_SESSIONID")
        username = os.getenv("TV_USERNAME")
        password = os.getenv("TV_PASSWORD")
        
        token = None
        if session_id:
            print("🍪 Found Session ID. Fetching Auth Token...")
            token = get_auth_token(session_id)
            if token:
                tv.token = token
                print("✅ Authenticated via Session ID!")
            else:
                print("⚠️ Invalid Session ID or Token not found. Falling back...")
        
        # Fallback to User/Pass if no session or failed
        if not token and username and password:
             # Try legacy login but catch errors
             try: 
                print(f"🔐 Logging in as {username}...")
                tv = TvDatafeed(username, password)
             except Exception as e:
                print(f"⚠️ User/Pass login failed: {e}")
             
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # =========================================================
    # STARTUP: Legacy cleanup + Health check + Cache stats
    # =========================================================
    from core.data_cache import cleanup_legacy_pkl, check_connection_health, get_cache_stats
    
    # Clean up old .pkl files (runs once, harmless if none exist)
    cleanup_legacy_pkl()
    
    # Quick connection test
    if not check_connection_health(tv):
        print("⚠️ Connection unstable — will rely on cached data where possible")
    else:
        print("✅ TradingView connection healthy")
    
    # Show cache status
    cache_info = get_cache_stats()
    print(f"📦 Cache: {cache_info['total_files']} files ({cache_info['fresh']} fresh, {cache_info['stale']} stale) | {cache_info['total_size_mb']} MB")

    all_results = []
    
    # =========================================================
    # Session-level tracking: เก็บ symbols ที่ดึงไปแล้วใน session นี้ (V5.2)
    # =========================================================
    session_fetched = set()  # Track symbols fetched in this session
    
    # =========================================================
    # Skip symbols already scanned for today's target date (V5.2)
    # =========================================================
    import datetime
    from datetime import timedelta
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    results_file = "data/forecast_tomorrow.csv"
    perf_log_file = "logs/performance_log.csv"
    already_scanned = set()
    
    # V5.2: Logic - เมื่อวานรัน → ทายผลของวันนี้ → วันนี้รันอีกรอบ → skip
    # เช็คจาก performance_log.csv (มี target_date) หรือ forecast_tomorrow.csv (file timestamp)
    
    # Priority 1: เช็คจาก performance_log.csv (มี scan_date column)
    if os.path.exists(perf_log_file):
        try:
            perf_df = pd.read_csv(perf_log_file)
            if not perf_df.empty:
                # เช็คว่า scan_date = วันนี้ (scan วันนี้แล้ว)
                if 'scan_date' in perf_df.columns:
                    scan_dates = perf_df['scan_date'].unique()
                    if today_str in scan_dates:
                        # CSV scan วันนี้แล้ว → skip symbols ทั้งหมด
                        if 'symbol' in perf_df.columns:
                            csv_symbols = set(perf_df[perf_df['scan_date'] == today_str]['symbol'].unique())
                            already_scanned.update(csv_symbols)
                            print(f"⚡ Smart Resume: Found {len(already_scanned)} symbols already scanned today (from performance_log). Skipping them!")
                # Fallback: เช็ค target_date = วันนี้ (ทายผลของวันนี้)
                elif 'target_date' in perf_df.columns:
                    target_dates = perf_df['target_date'].unique()
                    if today_str in target_dates:
                        if 'symbol' in perf_df.columns:
                            csv_symbols = set(perf_df[perf_df['target_date'] == today_str]['symbol'].unique())
                            already_scanned.update(csv_symbols)
                            print(f"⚡ Smart Resume: Found {len(already_scanned)} symbols already scanned for target date {today_str}. Skipping them!")
        except Exception:
            pass
    
    # Priority 2: เช็คจาก forecast_tomorrow.csv (file timestamp)
    # V5.2: เพิ่ม logic เช็คตลาดปิดหรือยัง
    forecast_df = None
    perf_log_df = None
    csv_results_for_display = []  # เก็บผลจาก CSV เพื่อแสดง (แม้ไม่มีผลใหม่)
    
    if os.path.exists(results_file):
        try:
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(results_file))
            file_date = file_mtime.strftime("%Y-%m-%d")
            forecast_df = pd.read_csv(results_file)
            
            if not forecast_df.empty and 'symbol' in forecast_df.columns:
                # Pre-load cached results with NaN protection (สำหรับแสดงผล)
                for _, row in forecast_df.iterrows():
                    d = row.to_dict()
                    if pd.isna(d.get('total_bars')): d['total_bars'] = 0
                    d['is_tradeable'] = _is_true_flag(d.get('is_tradeable', False))
                    csv_results_for_display.append(d)
                
                # ถ้า CSV เป็นของวันนี้ → เช็คว่ามี symbols ครบพอสมควร → skip
                if file_date == today_str:
                    csv_symbols = set(forecast_df['symbol'].unique())
                    if len(csv_symbols) >= 20:  # Threshold: ถ้ามี symbols ครบพอสมควร → skip
                        already_scanned.update(csv_symbols)
                        # เพิ่มเข้า all_results เพื่อแสดงผล
                        all_results.extend(csv_results_for_display)
                        print(f"⚡ Smart Resume: Found {len(csv_symbols)} symbols in forecast CSV (file date: {file_date}). Added to skip list!")
        except Exception:
            pass  # If file is corrupted, scan everything fresh
    
    # Priority 3: เช็คจาก cache files โดยตรง (V5.2 - New!)
    # ถ้ามี cache fresh → skip (ไม่ต้อง fetch ใหม่)
    from core.data_cache import has_cache, is_cache_fresh
    cache_skipped = 0
    for group_name, settings in config.ASSET_GROUPS.items():
        for asset in settings['assets']:
            symbol = asset['symbol']
            exchange = asset.get('exchange', 'SET')
            # เช็คว่ามี cache และ fresh
            if has_cache(symbol, exchange) and is_cache_fresh(symbol, exchange):
                # เช็คว่ายังไม่ได้อยู่ใน already_scanned
                if symbol not in already_scanned:
                    already_scanned.add(symbol)
                    cache_skipped += 1
    
    if cache_skipped > 0:
        print(f"⚡ Smart Resume: Found {cache_skipped} symbols with fresh cache. Added to skip list!")
    
    # Load perf_log_df for market time check
    if os.path.exists(perf_log_file):
        try:
            perf_log_df = pd.read_csv(perf_log_file)
        except Exception:
            pass
    
    if already_scanned:
        print(f"⚡ Smart Resume: Found {len(already_scanned)} symbols already scanned today (from cache + CSV). Skipping them!")
    
    # Fetch Summary Tracking
    fetch_summary = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'failed_symbols': [],
        'skipped': 0
    }
    
    # Global Price Map for Performance Update (N+1)
    price_map = {} # symbol -> latest_price
    
    consecutive_failures = 0
    
    # Iterate through Asset Groups
    for group_name, settings in config.ASSET_GROUPS.items():
        print(f"\n📂 Processing {settings['description']}...")
        
        assets = settings['assets']
        interval = settings['interval']
        history = settings['history_bars']
        
        for i, asset in enumerate(assets):
            display_name = asset.get('name', asset['symbol'])
            
            # V5.0: Smart Cooldown - ถ้า connection bad แล้ว → ไม่ต้อง cooldown (ใช้ cache อยู่แล้ว)
            if consecutive_failures >= 10 and is_connection_healthy():
                print(f"\n⚠️ Too many failures ({consecutive_failures}). Pausing for 10s and reconnecting...")
                time.sleep(10) # Reduced from 20s
                # Re-initialize TvDatafeed
                tv = TvDatafeed()
                consecutive_failures = 0
            elif consecutive_failures >= 10:
                # Connection bad → switch to cache-only mode (no cooldown needed)
                print(f"\n⚠️ Connection unstable. Switching to cache-only mode...")
                set_connection_healthy(False)
                consecutive_failures = 0
            
            # SMART SKIP: Multi-level check (V5.2)
            # 1. Session-level: already fetched in this session
            # 2. Day-level: already scanned today
            # 3. Market-time check: มี forecast แล้ว + ตลาดยังไม่ปิด → skip
            symbol_upper = asset['symbol'].upper()
            display_upper = display_name.upper() if display_name else symbol_upper
            exchange = asset.get('exchange', '')
            
            # Level 1: Session-level skip
            if (symbol_upper in session_fetched or asset['symbol'] in session_fetched):
                sys.stdout.write(f"\r   [{i+1}/{len(assets)}] ⚡ {asset['symbol']} (already fetched in session)")
                sys.stdout.flush()
                fetch_summary['skipped'] += 1
                fetch_summary['total'] += 1
                continue
            
            # Level 2: Day-level skip (already scanned today)
            if (symbol_upper in already_scanned or 
                display_upper in already_scanned or
                asset['symbol'] in already_scanned or
                display_name in already_scanned):
                sys.stdout.write(f"\r   [{i+1}/{len(assets)}] ⚡ {asset['symbol']} (already scanned today)")
                sys.stdout.flush()
                fetch_summary['skipped'] += 1
                fetch_summary['total'] += 1
                continue
            
            # Level 3: Market-time check (V5.2 - New!)
            # เช็คว่ามี forecast แล้ว + ตลาดยังไม่ปิด → skip (รอให้ตลาดปิดก่อน)
            from core.market_time import should_skip_symbol
            should_skip, skip_reason = should_skip_symbol(
                asset['symbol'], 
                exchange, 
                forecast_df=forecast_df,
                perf_log_df=perf_log_df
            )
            if should_skip:
                sys.stdout.write(f"\r   [{i+1}/{len(assets)}] ⏸️ {asset['symbol']} ({skip_reason})")
                sys.stdout.flush()
                fetch_summary['skipped'] += 1
                fetch_summary['total'] += 1
                continue
            
            sys.stdout.write(f"\r   [{i+1}/{len(assets)}] Scanning {asset['symbol']}...")
            sys.stdout.flush()
            
            fetch_summary['total'] += 1
            
            # Check for fixed threshold override in config
            fixed_thresh = settings.get('fixed_threshold', None)
            
            # V5.0: Smart Fetch - เช็ค cache ก่อน, retry เฉพาะเมื่อจำเป็น
            # Fast path: ถ้ามี cache fresh และ connection bad → ใช้ cache เลย (ไม่ต้อง fetch)
            symbol = asset['symbol']
            exchange = asset['exchange']
            has_fresh_cache = has_cache(symbol, exchange) and is_cache_fresh(symbol, exchange)
            connection_bad = not is_connection_healthy()
            
            if has_fresh_cache and connection_bad:
                # ใช้ cache โดยตรง ไม่ต้อง fetch
                cached_df = load_cache(symbol, exchange)
                if cached_df is not None and not cached_df.empty:
                    results_list = processor.analyze_asset(cached_df, symbol=symbol, exchange=exchange, fixed_threshold=fixed_thresh)
                    display_name = asset.get('name', symbol)
                    for res in results_list:
                        res['symbol'] = display_name
                    pattern_results = results_list
                    # Mark as fetched (ใช้ cache = ดึงข้อมูลสำเร็จ)
                    session_fetched.add(symbol_upper)
                    session_fetched.add(asset['symbol'])
                else:
                    pattern_results = None
            else:
                # Normal fetch (data_cache.py จะจัดการ retry เอง)
                pattern_results = fetch_and_analyze(tv, asset, history, interval, fixed_thresh)
            
            # Update results
            if pattern_results is not None:
                fetch_summary['success'] += 1
                consecutive_failures = 0 # Reset on success
                # Mark as fetched in this session (ถ้ายังไม่ได้ mark จาก cache path)
                session_fetched.add(symbol_upper)
                session_fetched.add(asset['symbol'])
                for res in pattern_results:
                    res['group'] = group_name
                    res['exchange'] = asset['exchange'] # Add actual exchange
                    all_results.append(res)
                    # Update Price Map for Global Homework Check
                    price_map[res['symbol']] = res['price']
            else:
                fetch_summary['failed'] += 1
                consecutive_failures += 1 # Increment failure count
                # ไม่ mark เป็น fetched (ให้ลองใหม่ได้ถ้า retry)
                fetch_summary['failed_symbols'].append(asset['symbol'])
            
            # Rate limiting: ถ้า connection bad → delay น้อยลง (ใช้ cache อยู่แล้ว)
            delay = 0.1 if connection_bad else REQUEST_DELAY
            time.sleep(delay)
    
    # Print Fetch Summary
    print("\n")
    print("=" * 50)
    print("📊 FETCH SUMMARY")
    print("=" * 50)
    success_rate = (fetch_summary['success'] / fetch_summary['total'] * 100) if fetch_summary['total'] > 0 else 0
    print(f"✅ Success: {fetch_summary['success']}/{fetch_summary['total']} ({success_rate:.1f}%)")
    print(f"⚡ Skipped: {fetch_summary['skipped']} (already scanned today)")
    print(f"❌ Failed:  {fetch_summary['failed']}")
    if fetch_summary['failed_symbols']:
        # Show first 10 failed symbols
        shown = fetch_summary['failed_symbols'][:10]
        print(f"   Failed symbols: {', '.join(shown)}", end='')
        if len(fetch_summary['failed_symbols']) > 10:
            print(f" ... and {len(fetch_summary['failed_symbols']) - 10} more")
        else:
            print()
    print("=" * 50)
    
    # -------------------------------------------------------------
    # Forward Testing: ตรวจการบ้าน (Always run, even if no new results)
    # -------------------------------------------------------------
    # V5.0: Forward Testing - ตรวจการบ้าน + Log ใหม่
    # -------------------------------------------------------------
    # Step 1: ตรวจการบ้านก่อน (verify forecasts ที่ target_date <= วันนี้)
    print("\n" + "="*80)
    print("📊 Forward Testing: ตรวจการบ้าน (เช็คผลจริง vs ทาย)")
    print("="*80)
    try:
        verify_result = verify_forecast(tv=tv)
        if verify_result:
            verified = verify_result.get('verified', 0)
            correct = verify_result.get('correct', 0)
            incorrect = verify_result.get('incorrect', 0)
            if verified > 0:
                accuracy = (correct / verified * 100) if verified > 0 else 0
                print(f"✅ Verified: {verified} forecasts | ✅ Correct: {correct} | ❌ Incorrect: {incorrect} | 📈 Accuracy: {accuracy:.1f}%")
            else:
                print("ℹ️ No pending forecasts to verify (all are already verified or target_date is in future)")
    except Exception as e:
        print(f"⚠️ Verify failed: {e}")
    
    # Final Report
    # ถ้ามีผลใหม่ → ใช้ all_results
    # ถ้าไม่มีผลใหม่ → แสดงผลจาก CSV ที่มีอยู่แล้ว (เพื่อให้ user เห็นว่าวันนี้ระบบทายอะไร)
    display_results = all_results if all_results else csv_results_for_display
    
    if display_results:
        # แสดงเฉพาะ PREDICT N+1 REPORT (มี Forecast ชัดเจน UP/DOWN)
        # ไม่แสดง ALL FORECASTS เพราะไม่ได้บอกทิศทางและมีข้อมูลซ้ำ
        generate_report(display_results)

        # Step 3: Log forecasts based on configurable thresholds (V6.0)
        # Note: Log เฉพาะผลใหม่ (all_results) ไม่ใช่จาก CSV
        # V6.0: ใช้ Prob > MIN_PROB_THRESHOLD + Matches >= MIN_MATCHES_THRESHOLD
        # แทนที่จะใช้ is_tradeable (Prob≥60%) เพื่อให้ยืดหยุ่นกว่า
        if all_results:
            try:
                # Filter by configurable thresholds
                eligible = []
                for r in all_results:
                    # Get the winning side (higher prob)
                    bull_prob = r.get('bull_prob', 50)
                    bear_prob = r.get('bear_prob', 50)
                    max_prob = max(bull_prob, bear_prob)
                    matches = r.get('matches', 0)
                    
                    # Check thresholds
                    if max_prob > MIN_PROB_THRESHOLD and matches >= MIN_MATCHES_THRESHOLD:
                        # Add tier classification if enabled
                        if USE_TIER_CLASSIFICATION:
                            r['tier'] = 'A' if max_prob >= 60.0 else 'B'
                        # Store max_prob for deduplication
                        r['_max_prob'] = max_prob
                        eligible.append(r)
                
                # V6.1: Deduplicate - ถ้ามี (symbol, pattern, forecast) ซ้ำ → เลือกอันที่มี max_prob สูงสุด
                if eligible:
                    from collections import defaultdict
                    dedup_dict = defaultdict(list)
                    
                    # Group by (symbol, pattern, forecast)
                    for r in eligible:
                        symbol = r.get('symbol', '')
                        pattern = r.get('pattern', '')
                        forecast = r.get('forecast_label', 'UP')
                        key = (symbol, pattern, forecast)
                        dedup_dict[key].append(r)
                    
                    # Select best (highest acc_score) for each group
                    deduplicated = []
                    for key, records in dedup_dict.items():
                        if len(records) > 1:
                            # Sort by acc_score descending, then by total_events descending
                            records.sort(key=lambda x: (x.get('acc_score', 0), x.get('total_events', 0)), reverse=True)
                            # Keep only the best one
                            deduplicated.append(records[0])
                        else:
                            deduplicated.append(records[0])
                    
                    if deduplicated:
                        log_forecast(deduplicated)
                        tier_a = sum(1 for r in deduplicated if r.get('tier') == 'A') if USE_TIER_CLASSIFICATION else 0
                        tier_b = sum(1 for r in deduplicated if r.get('tier') == 'B') if USE_TIER_CLASSIFICATION else 0
                        if USE_TIER_CLASSIFICATION:
                            print(f"📝 Logged {len(deduplicated)} new forecasts (Tier A: {tier_a}, Tier B: {tier_b}) for verification tomorrow")
                        else:
                            print(f"📝 Logged {len(deduplicated)} new forecasts (Prob>{MIN_PROB_THRESHOLD}%, Matches>={MIN_MATCHES_THRESHOLD}) for verification tomorrow")
            except Exception as e:
                print(f"⚠️ Forward log failed: {e}")
        
        # -------------------------------------------------------------
        # 4. Global Performance Check (N+1 Accuracy)
        # -------------------------------------------------------------
        # V4.4: All forward testing and verification is handled by 
        # core.performance.verify_forecast() and log_forecast() above.
        
        # -------------------------------------------------------------
        # 6. Market Health Summary (The "Heartbeat")
        # -------------------------------------------------------------
        # V5.0: Heartbeat counts ALL patterns found (success) 
        # but only is_tradeable as actionable UP/DOWN signals
        import datetime
        market_stats = {}
        
        for r in display_results:
            group = r['group']
            if "THAI" in group: m_key = "SET"
            elif "US" in group: m_key = "NASDAQ"
            elif "CHINA" in group: m_key = "HKEX"
            elif "TAIWAN" in group: m_key = "TWSE"
            elif "METALS" in group: m_key = "GOLD"
            else: m_key = "Other"
            
            if m_key not in market_stats:
                market_stats[m_key] = {'scanned': 0, 'tradeable': 0, 'up': 0, 'down': 0, 'best_pattern': '', 'best_prob': 0}
            
            market_stats[m_key]['scanned'] += 1
            
            # Only count is_tradeable as actionable signals
            if not _is_true_flag(r.get('is_tradeable', False)):
                continue
                
            market_stats[m_key]['tradeable'] += 1
            
            forecast_label = r.get('forecast_label', 'UP')
            prob = r.get('acc_score', 0)
            
            # Track best pattern per market
            if prob > market_stats[m_key]['best_prob']:
                market_stats[m_key]['best_prob'] = prob
                pat_display = r.get('pattern', r.get('pattern_display', '???'))
                market_stats[m_key]['best_pattern'] = f"{r['symbol']} ({pat_display}) {prob:.0f}%"

            if forecast_label == 'UP': 
                market_stats[m_key]['up'] += 1
            else: 
                market_stats[m_key]['down'] += 1

        # Print Heartbeat Table
        if market_stats:
            now_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            print("\n" + "=" * 85)
            print(f"🏥 SYSTEM HEARTBEAT | Last Update: {now_dt}")
            print("=" * 85)
            print(f"{'Market':<10} {'Patterns':>10} {'Tradeable':>10} {'UP':>6} {'DOWN':>6}   {'Top Signal'}")
            print("-" * 85)
            
            for m_key, s in market_stats.items():
                print(f"{m_key:<10} {s['scanned']:>10} {s['tradeable']:>10} {s['up']:>6} {s['down']:>6}   {s['best_pattern']}")
            print("-" * 85)
            print("✅ Reports & Logs updated.")
            
            # Save Heartbeat to file
            with open("data/system_heartbeat.txt", "w", encoding="utf-8") as f:
                f.write(f"SYSTEM HEARTBEAT | Updated: {now_dt}\n")
                f.write("=" * 85 + "\n")
                f.write(f"{'Market':<10} {'Patterns':>10} {'Tradeable':>10} {'UP':>6} {'DOWN':>6}   {'Top Signal'}\n")
                for m_key, s in market_stats.items():
                    f.write(f"{m_key:<10} {s['scanned']:>10} {s['tradeable']:>10} {s['up']:>6} {s['down']:>6}   {s['best_pattern']}\n")
                f.write("-" * 85 + "\n")

            # -------------------------------------------------------------
            # 7. Final Status
            # -------------------------------------------------------------
            if all_results:
                print(f"✅ All systems updated. Results synced to logs/performance_log.csv")

    else:
        print("\n❌ No matching patterns found in any asset (and no CSV data available).")
    
    # Print execution time
    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n⏱️ Total execution time: {minutes}m {seconds}s")

if __name__ == "__main__":
    main()
