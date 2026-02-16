#!/usr/bin/env python
"""
verify_failed_symbols.py - Verify and remove invalid stock symbols
===================================================================
ตรวจสอบว่าหุ้นที่ดึงข้อมูลไม่ได้มีอยู่จริงหรือไม่
ถ้าไม่มีจริงจะลบออกจากรายชื่อ
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import time

# หุ้นที่ต้องตรวจสอบ
FAILED_SYMBOLS = {
    'INTUCH': 'SET',      # Thai
    'ESSO': 'SET',        # Thai
    'STARK': 'SET',       # Thai
    'STEC': 'SET',        # Thai
    'AZN': 'NASDAQ',      # US
    'SGEN': 'NASDAQ',     # US
    'WBA': 'NASDAQ',      # US
    '0981': 'HKEX',       # Hong Kong
}

def verify_symbol(tv, symbol, exchange):
    """
    ตรวจสอบว่าหุ้นนี้มีข้อมูลใน TradingView หรือไม่
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        print(f"  Checking {symbol} ({exchange})...", end=' ', flush=True)
        
        # ลองดึงข้อมูลเล็กน้อย (10 bars) เพื่อตรวจสอบ
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=10
        )
        
        if df is None or df.empty:
            print("[FAIL] Empty data")
            return False, "Empty data returned"
        
        if len(df) < 5:
            print(f"[WARN] Insufficient data ({len(df)} bars)")
            return False, f"Insufficient data: {len(df)} bars"
        
        print(f"[OK] Valid ({len(df)} bars available)")
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"[FAIL] Error: {error_msg[:50]}")
        return False, error_msg

def main():
    import sys
    import io
    # Fix encoding for Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*80)
    print("VERIFYING FAILED SYMBOLS")
    print("="*80)
    print(f"Checking {len(FAILED_SYMBOLS)} symbols...\n")
    
    # Connect to TradingView
    print("Connecting to TradingView...")
    try:
        tv = TvDatafeed()
        print("Connected!\n")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return
    
    results = {}
    
    for symbol, exchange in FAILED_SYMBOLS.items():
        is_valid, error = verify_symbol(tv, symbol, exchange)
        results[symbol] = {
            'exchange': exchange,
            'is_valid': is_valid,
            'error': error
        }
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    valid_symbols = [s for s, r in results.items() if r['is_valid']]
    invalid_symbols = [s for s, r in results.items() if not r['is_valid']]
    
    print(f"\nValid symbols ({len(valid_symbols)}):")
    for symbol in valid_symbols:
        print(f"   - {symbol} ({results[symbol]['exchange']})")
    
    print(f"\nInvalid symbols ({len(invalid_symbols)}):")
    for symbol in invalid_symbols:
        error = results[symbol]['error']
        print(f"   - {symbol} ({results[symbol]['exchange']}): {error}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if invalid_symbols:
        print("\nThese symbols should be REMOVED from stock lists:")
        for symbol in invalid_symbols:
            exchange = results[symbol]['exchange']
            if exchange == 'SET':
                print(f"   - Remove '{symbol}' from data/thai_set100.txt")
            elif exchange == 'NASDAQ':
                print(f"   - Remove '{symbol}' from data/nasdaq_stocks.txt")
            elif exchange == 'HKEX':
                print(f"   - Remove '{symbol}' from config.py (CHINA_ADR_STOCKS or similar)")
    else:
        print("\nAll symbols are valid. The issue might be temporary or rate limiting.")
    
    print()

if __name__ == "__main__":
    main()

