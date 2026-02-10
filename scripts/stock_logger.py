
import os
import pandas as pd
from datetime import datetime

class StockLogger:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_trade(self, symbol, signal, entry_price, entry_date=None):
        """
        Logs a NEW trade entry for a specific stock.
        """
        filename = os.path.join(self.log_dir, f"{symbol}.csv")
        
        # Define Columns
        columns = [
            "Entry Date", "Signal", "Entry Price", "Status", 
            "Exit Date", "Exit Price", "P/L Value", "% P/L", "Duration (Days)"
        ]
        
        # Load or Create DataFrame
        if os.path.exists(filename):
            df = pd.read_csv(filename)
        else:
            df = pd.DataFrame(columns=columns)
        
        # Check if there is already an OPEN trade?
        # If open, we don't open another one (Simple strategy: 1 position at a time)
        # Or we can allow multiple. For simplicity, let's warn if OPEN exists.
        if not df.empty and df.iloc[-1]['Status'] == 'OPEN':
            print(f"⚠️ {symbol} already has an OPEN trade. Skipping new entry.")
            return

        # Create New Entry
        if entry_date is None:
            entry_date = datetime.now().strftime("%Y-%m-%d")
            
        new_row = {
            "Entry Date": entry_date,
            "Signal": signal,
            "Entry Price": entry_price,
            "Status": "OPEN",
            "Exit Date": "",
            "Exit Price": "",
            "P/L Value": "",
            "% P/L": "",
            "Duration (Days)": ""
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(filename, index=False)
        print(f"📝 Logged {symbol}: {signal} @ {entry_price} in {filename}")

    def close_trade(self, symbol, exit_price, exit_date=None):
        """
        Closes the OPEN trade for a specific stock.
        """
        filename = os.path.join(self.log_dir, f"{symbol}.csv")
        
        if not os.path.exists(filename):
            print(f"❌ Log file for {symbol} not found.")
            return

        df = pd.read_csv(filename)
        
        if df.empty or df.iloc[-1]['Status'] != 'OPEN':
            print(f"ℹ️ No OPEN trade to close for {symbol}.")
            return

        # Close the last row
        idx = df.index[-1]
        
        entry_price = float(df.at[idx, 'Entry Price'])
        signal = df.at[idx, 'Signal']
        entry_date_str = df.at[idx, 'Entry Date']
        
        if exit_date is None:
            exit_date = datetime.now().strftime("%Y-%m-%d")
            
        # Calculate Duration
        try:
            d1 = datetime.strptime(entry_date_str, "%Y-%m-%d")
            d2 = datetime.strptime(exit_date, "%Y-%m-%d")
            duration = (d2 - d1).days
        except:
            duration = 0
            
        # Calculate P/L
        if signal == 'UP':
            pnl_value = exit_price - entry_price
            pnl_pct = (pnl_value / entry_price) * 100
        else: # DOWN
            pnl_value = entry_price - exit_price
            pnl_pct = (pnl_value / entry_price) * 100
            
        # Update Row
        df.at[idx, 'Exit Date'] = exit_date
        df.at[idx, 'Exit Price'] = exit_price
        df.at[idx, 'P/L Value'] = round(pnl_value, 2)
        df.at[idx, '% P/L'] = round(pnl_pct, 2)
        df.at[idx, 'Duration (Days)'] = duration
        df.at[idx, 'Status'] = 'CLOSED'
        
        df.to_csv(filename, index=False)
        print(f"✅ Closed {symbol}: {pnl_pct:.2f}% ({duration} days)")

if __name__ == "__main__":
    # Test
    logger = StockLogger()
    # logger.log_trade("TEST", "UP", 100)
    # logger.close_trade("TEST", 105)
