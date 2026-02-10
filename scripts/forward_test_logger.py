
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ASSET_GROUPS
from processor import MarketDataProcessor

# --- Configuration ---
LOG_FILE = "data/forward_test_log.csv"

def initialize_log():
    """Creates the log file if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=[
            "timestamp", "symbol", "signal_price", "direction", 
            "threshold", "status", "exit_price", "result", "pnl_pct"
        ])
        df.to_csv(LOG_FILE, index=False)
        print(f"✅ Created new log file: {LOG_FILE}")
    else:
        print(f"ℹ️  Log file exists: {LOG_FILE}")

def log_prediction(symbol, direction, price, threshold):
    """Logs a new prediction signal."""
    df = pd.read_csv(LOG_FILE)
    
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "signal_price": price,
        "direction": direction, # 'UP' or 'DOWN'
        "threshold": threshold,
        "status": "PENDING", # Waiting for next close to verify
        "exit_price": 0.0,
        "result": 0, # 0 = Pending/Loss, 1 = Win (Correct Direction)
        "pnl_pct": 0.0
    }
    
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)
    print(f"📝 Logged Signal: {symbol} {direction} @ {price:.2f}")

def verify_pending_signals(processor):
    """Checks pending signals against current market data to verify outcome."""
    if not os.path.exists(LOG_FILE):
        return

    df = pd.read_csv(LOG_FILE)
    pending_mask = df['status'] == 'PENDING'
    
    if not pending_mask.any():
        print("✅ No pending signals to verify.")
        return

    print(f"🔍 Verifying {pending_mask.sum()} pending signals...")
    
    updated_count = 0
    
    for index, row in df[pending_mask].iterrows():
        symbol = row['symbol']
        direction = row['direction']
        entry_price = float(row['signal_price'])
        timestamp = row['timestamp']
        
        # Determine Interval (assuming Daily for simplicity, or look up from Config)
        # In a real real-time run, we would need to know the interval. 
        # For now, let's fetch the latest candle.
        
        # Find asset group to get interval
        interval = None
        for group in ASSET_GROUPS.values():
            for asset in group['assets']:
                if asset['symbol'] == symbol:
                    interval = group['interval']
                    break
        
        if not interval:
            continue
            
        # Fetch latest data
        data = processor.tv.get_hist(
            symbol=symbol,
            exchange='SET', # Defaulting to SET for now, need robust lookup
            interval=interval,
            n_bars=2
        )
        
        if data is None or data.empty:
            continue

        # Check if we have a NEW closed candle since the signal
        # Logic: If current time > signal time + interval duration? 
        # Simplified Verification Logic: 
        # Compare Entry Price with Current Close.
        # IF (Direction UP AND Current > Entry) -> WIN (1)
        # IF (Direction DOWN AND Current < Entry) -> WIN (1)
        # ELSE -> LOSS (0)
        
        current_price = data['close'].iloc[-1]
        
        # Calculate Percentage Move
        move_pct = (current_price - entry_price) / entry_price * 100
        
        # Determine Result
        is_win = False
        if direction == "UP" and current_price > entry_price:
            is_win = True
        elif direction == "DOWN" and current_price < entry_price:
            is_win = True
            
        # Update Record
        df.at[index, 'exit_price'] = current_price
        df.at[index, 'pnl_pct'] = move_pct
        df.at[index, 'result'] = 1 if is_win else 0
        df.at[index, 'status'] = 'COMPLETED'
        
        updated_count += 1
        print(f"   👉 Verified {symbol}: {'WIN ✅' if is_win else 'LOSS ❌'} ({move_pct:.2f}%)")

    if updated_count > 0:
        df.to_csv(LOG_FILE, index=False)
        print(f"💾 Updated {updated_count} signals in log.")

def run_forward_test():
    """Main loop to simulate forward testing."""
    initialize_log()
    processor = MarketDataProcessor()
    
    print("\n--- 🚀 Starting Forward Test Logger ---")
    
    # 1. Verify Old Signals
    verify_pending_signals(processor)
    
    # 2. Scan for New Signals (Simulated loop over groups)
    # This part would normally be loop through all assets.
    # For demonstration, we will let the user run it periodically.
    
    print("\n✅ Verification Done. Waiting for next run to log new signals.")

if __name__ == "__main__":
    run_forward_test()
