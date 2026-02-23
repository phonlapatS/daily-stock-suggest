#!/usr/bin/env python
import os
import sys
import pandas as pd
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import config
from core.data_cache import get_data_with_cache
from core.engines.reversion_engine import MeanReversionEngine
from scripts.core_reports.view_report import print_header

LOG_FILE = "logs/performance_log.csv"

def get_symbol_settings(symbol_to_find):
    """Find symbol or name in config and return its settings/market info"""
    s_upper = symbol_to_find.upper()
    for group_id, group in config.ASSET_GROUPS.items():
        for asset in group['assets']:
            if asset['symbol'].upper() == s_upper or asset.get('name', '').upper() == s_upper:
                settings = group.copy()
                # Ensure we have the correct ticker for TvDatafeed
                settings['exchange'] = asset['exchange']
                settings['ticker'] = asset['symbol'] 
                return settings
    return None

def analyze_historical_record(symbol_input, scan_date=None):
    """Reconstruct prediction logic for a past log entry"""
    if not os.path.exists(LOG_FILE):
        print("❌ Performance log not found.")
        return

    df_log = pd.read_csv(LOG_FILE)
    df_log.columns = df_log.columns.str.strip()
    
    # Filter for symbol (case insensitive) and verified
    s_upper = symbol_input.upper()
    mask = (df_log['symbol'].str.upper() == s_upper) & (df_log['actual'] != 'PENDING')
    if scan_date:
        mask = mask & (df_log['scan_date'] == scan_date)
    
    records = df_log[mask].sort_values('scan_date', ascending=False)
    
    if records.empty:
        print(f"❌ No verified history found for {symbol_input}" + (f" on {scan_date}" if scan_date else ""))
        return

    # Use the most recent matching record
    rec = records.iloc[0]
    scan_date = rec['scan_date']
    exchange_from_log = rec['exchange']
    logged_forecast = rec['forecast']
    logged_prob = rec['prob']

    print_header(f"HISTORY PROOF: {symbol_input} Scan Date: {scan_date}")
    print(f"📌 Logged Forecast: {logged_forecast} ({logged_prob}%)")
    print(f"🎯 Actual Outcome: {rec['actual']} (Correct: {rec['correct']})")
    print("-" * 80)

    # 1. Get Market Info - Use ticker from log if config search fails
    settings = get_symbol_settings(symbol_input)
    
    if not settings:
        # Fallback: Create minimal settings from log data
        print(f"⚠️ {symbol_input} not found in current config.py. Using log metadata...")
        settings = {
            'exchange': exchange_from_log,
            'interval': Interval.in_daily,
            'ticker': symbol_input, # Assume ticker is the symbol from log
            'min_matches': config.MIN_MATCHES_THRESHOLD
        }
    
    ticker = settings.get('ticker', symbol_input)

    # 2. Fetch Data
    tv = TvDatafeed()
    df = get_data_with_cache(
        tv=tv,
        symbol=ticker,
        exchange=settings['exchange'],
        interval=settings.get('interval', Interval.in_daily),
        full_bars=5000
    )

    if df is None or df.empty:
        print("❌ Could not fetch historical data.")
        return

    # 3. SLICE DATA AT SCAN DATE
    # We must only provide data available UP TO the scan date
    df_sliced = df[df.index.strftime('%Y-%m-%d') <= scan_date].copy()
    
    if df_sliced.empty:
        print(f"❌ No historical data found on or before {scan_date}")
        return

    print(f"📊 Re-analyzing using price action up to {df_sliced.index[-1].strftime('%Y-%m-%d')}...")

    # 4. RUN ENGINE
    engine = MeanReversionEngine()
    # Processor usually sets min_matches, we use the global config as default
    settings['min_matches'] = config.MIN_MATCHES_THRESHOLD
    
    results = engine.analyze(df_sliced, symbol, settings)
    
    if not results:
        print("⚠️ No patterns triggered threshold on this date during reconstruction.")
        return

    # 5. DISPLAY LIKE VIEW_REPORT.PY
    res = results[0] # Single result for Mean Reversion
    
    print("\n[ PATTERN BREAKDOWN ]")
    print("-" * 80)
    print(f"{'Suffix Pattern':<18} | {'UP (+)':>10} | {'DOWN (-)':>10} | {'Winner':^12}")
    print("-" * 80)
    
    breakdown_str = res.get('breakdown', '')
    parts = breakdown_str.split('; ')
    
    for part in parts:
        try:
            # Format: '++:15/10(P)'
            pattern_part = part.split(':')[0]
            numbers_part = part.split(':')[1] 
            counts_str = numbers_part.split('(')[0] 
            tag = numbers_part.split('(')[1].replace(')', '') 
            
            v1, v2 = map(int, counts_str.split('/'))
            
            is_weak = "W" in tag
            w_label = " (Weak)" if is_weak else ""
            
            if tag.startswith('P'):
                up_c, down_c = v1, v2
                winner_label = f"🟢 UP{w_label}"
            elif tag.startswith('N'):
                up_c, down_c = v2, v1
                winner_label = f"🔴 DOWN{w_label}"
            else:
                up_c, down_c = v1, v2
                winner_label = f"⚪ TIE{w_label}"
                
            print(f"{pattern_part:<18} | {up_c:>10} | {down_c:>10} | {winner_label:^12}")
        except:
            print(f"  {part}")

    print("-" * 80)
    forecast = res['forecast']
    f_icon = "🟢 UP" if forecast == 'UP' else "🔴 DOWN"
    print(f"🎯 Final Result: {f_icon}")
    print(f"UP                  : {res.get('total_p', 0)}")
    print(f"DOWN                : {res.get('total_n', 0)}")
    print(f"Total               : {res.get('total_events', 0)}")
    
    winning_count = res.get('winning_count', 0)
    total_events = res.get('total_events', 1)
    print(f"Calculation         : {winning_count} / {total_events} = {res['prob']}% Prob%")
    print("-" * 80)
    print("✅ Reconstruction Match Complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/analysis/verify_history_detail.py <SYMBOL> [SCAN_DATE]")
        print("Example: python scripts/analysis/verify_history_detail.py TTB")
        sys.exit(1)
        
    symbol = sys.argv[1].upper()
    scan_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_historical_record(symbol, scan_date)
