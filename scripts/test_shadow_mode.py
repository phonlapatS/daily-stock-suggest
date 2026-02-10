"""
test_shadow_mode.py - Shadow Mode Logging Simulation
=====================================================
Purpose: specific test to verify we can LOG Market Regime & Sector Data
         without affecting the actual trade signals (Shadow Mode).
Output: data/shadow_test_log.csv
"""

import sys
import os
import pandas as pd
import time
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.filters import market_regime, sector_rotation
from processor import analyze_asset

# Test Config
SYMBOLS = ['NVDA', 'MSFT', 'GOOGL', 'KO', 'PEP']
SECTORS = ['XLK', 'XLP']

def fetch_data_robust(tv, symbol, exchange='NASDAQ', n_bars=500):
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
        return df
    except:
        return None

def run_shadow_test():
    print("=" * 60)
    print("🕵️‍♂️ SHADOW MODE TEST RUNNER")
    print("=" * 60)
    print("Goal: Log Market Context without blocking trades.\n")
    
    tv = TvDatafeed()
    
    # 1. Fetch Market Context (SPY & Sectors)
    print("📊 Fetching Market Context...")
    spy_df = fetch_data_robust(tv, 'SPY', 'AMEX', 500)
    
    sector_data = {}
    for sec in SECTORS:
        df = fetch_data_robust(tv, sec, 'AMEX', 500)
        if df is not None:
            sector_data[sec] = df
            
    if spy_df is None:
        print("❌ Critical: Failed to fetch SPY. Cannot run shadow mode.")
        return

    # 2. Iterate Stocks & Simulate Prediction
    shadow_logs = []
    
    print(f"🚀 Processing {len(SYMBOLS)} stocks...")
    
    for symbol in SYMBOLS:
        print(f"   Analyzing {symbol}...", end="\r")
        exchange = 'NYSE' if symbol in ['KO', 'JNJ', 'PEP'] else 'NASDAQ'
        
        df = fetch_data_robust(tv, symbol, exchange, 500)
        if df is None: continue
        
        # Run Standard Analysis (The "Main Logic")
        # We simulate what main.py does: call analyze_asset()
        results = analyze_asset(df)
        
        if not results: continue
        
        # Take the best pattern result
        signal = results[0]
        
        # --- SHADOW MODE LOGIC STARTS HERE ---
        # We calculate context but DO NOT filter the signal
        
        # 1. Market Regime (SPY Trend)
        spy_sma50 = market_regime.calculate_sma(spy_df, 50).iloc[-1]
        spy_price = spy_df['close'].iloc[-1]
        market_status = 'BULL' if spy_price > spy_sma50 else 'BEAR'
        
        # 2. Sector Strength
        sector_status = 'N/A'
        sector_sym = sector_rotation.get_sector_for_symbol(symbol)
        if sector_sym and sector_sym in sector_data:
            sec_df = sector_data[sector_sym]
            # Simple check: Is Sector Price > SMA50?
            sec_sma50 = sec_df['close'].rolling(50).mean().iloc[-1]
            sec_price = sec_df['close'].iloc[-1]
            sector_status = 'STRONG' if sec_price > sec_sma50 else 'WEAK'
            
        # Log Everything
        log_entry = {
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'Symbol': symbol,
            'Signal': 'BUY' if signal['avg_return'] > 0 else 'SELL',
            'Win_Prob': f"{signal['bull_prob'] if signal['avg_return']>0 else signal['bear_prob']:.1f}%",
            # Shadow Columns
            'Shadow_Market_Regime': market_status,
            'Shadow_Sector_Status': sector_status,
            'Shadow_Action': 'LOGGED_ONLY' # Proof we didn't block it
        }
        shadow_logs.append(log_entry)
        time.sleep(0.5)

    # 3. Output Results
    print("\n\n✅ Shadow Mode Log Generated:")
    df_log = pd.DataFrame(shadow_logs)
    print(df_log.to_string(index=False))
    
    # Save to CSV
    output_file = 'data/shadow_test_log.csv'
    df_log.to_csv(output_file, index=False)
    print(f"\n💾 Log file saved to: {output_file}")
    print("Note: In real system, these 'Shadow' columns will be added to the main log CSV.")

if __name__ == "__main__":
    run_shadow_test()
