
"""
verify_prediction.py - The Auditor
==================================
Role: Verify past predictions against realized market data.
Mode: Runs daily (e.g., morning routine or pre-market).
Logic:
    1. Scan all individual stock logs in `data/logs/*.csv`.
    2. Check for rows with Status="OPEN".
    3. Fetch latest data (N+1 Close) from TradingView.
    4. Calculate P/L and update log with Exit Price/Date.
"""

import sys
import os
import glob
import time
from datetime import datetime
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ASSET_GROUPS
from scripts.stock_logger import StockLogger

def get_exchange_for_symbol(symbol):
    """Helper to find exchange for a symbol from config."""
    for group in ASSET_GROUPS.values():
        for asset in group['assets']:
            if asset['symbol'] == symbol:
                return asset['exchange']
    return 'SET' # Default fallback

def verify_all_logs():
    print("🚀 Starting Auditor: Verifying Open Trades...")
    
    # Initialize Tooling
    logger = StockLogger()
    tv = TvDatafeed()
    
    # 1. Scan Logs for Open Trades
    log_dir = "data/logs"
    if not os.path.exists(log_dir):
        print(f"❌ Log directory not found: {log_dir}")
        return

    csv_files = glob.glob(os.path.join(log_dir, "*.csv"))
    
    print(f"📂 Found {len(csv_files)} log files.")
    
    updated_count = 0
    
    for filepath in csv_files:
        try:
            df = pd.read_csv(filepath)
            if df.empty: continue
            
            # Check for OPEN trades
            open_trades = df[df['Status'] == 'OPEN']
            
            if open_trades.empty:
                continue
                
            symbol = os.path.splitext(os.path.basename(filepath))[0]
            exchange = get_exchange_for_symbol(symbol)
            
            # Process each OPEN trade
            for idx, row in open_trades.iterrows():
                entry_date_str = row['Entry Date']
                signal = row['Signal']
                entry_price = float(row['Entry Price'])
                
                print(f"🔍 Verifying {symbol} ({entry_date_str})...", end=" ")
                
                # Fetch Data (Daily resolution for verification)
                # We need data AFTER the entry date.
                # Simplest Logic: Get last 5 days. Check if we have a NEW candle with date > entry_date.
                
                hist = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=10)
                
                if hist is None or hist.empty:
                    print("❌ No Data")
                    continue
                
                # Convert Entry Date to Datetime
                try:
                    entry_dt = pd.to_datetime(entry_date_str)
                except:
                    print(f"❌ Date Error ({entry_date_str})")
                    continue
                
                # Find the NEXT Completed Candle after Entry
                # We look for a candle with date > entry_dt
                # hist index is Datetime
                
                future_data = hist[hist.index > entry_dt]
                
                if future_data.empty:
                    print("⏳ Pending (No new data yet)")
                    continue
                
                # We have a result! 
                # Use the CLOSE of the immediate next day (for N+1 strategy)
                # OR use the LATEST close if we are holding?
                # For N+1 Strategy: We exit at Close of Next Day.
                # So we take the first row of future_data.
                
                exit_candle = future_data.iloc[0]
                exit_price = exit_candle['close']
                exit_date = future_data.index[0].strftime("%Y-%m-%d")
                
                # Perform Close
                logger.close_trade(symbol, exit_price, exit_date)
                updated_count += 1
                
                time.sleep(0.2) # Rate limit
                
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            
    print("-" * 50)
    print(f"✅ Auditor Complete. Updated {updated_count} trades.")
    
if __name__ == "__main__":
    verify_all_logs()
