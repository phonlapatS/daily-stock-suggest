
import os
import pandas as pd
from datetime import datetime

# List of names Windows won't allow as filenames
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}

class StockLogger:
    def __init__(self, log_dir="data/logs"):
        # Use absolute path relative to project root (normpath fixes mixed / and \ on Windows)
        self.log_dir = os.path.normpath(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), log_dir)
        )
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_filename(self, symbol, market):
        """Returns a safe filename, handling Windows reserved names."""
        if symbol.upper() in RESERVED_NAMES:
            return f"{symbol}_{market}.csv"
        return f"{symbol}.csv"

    def log_trade(self, symbol, signal, entry_price, entry_date=None, market="Other", silent=False):
        """
        Logs a NEW trade entry for a specific stock using User's Excel format.
        Organizes files into subdirectories by market.
        """
        market_dir = os.path.join(self.log_dir, market)
        os.makedirs(market_dir, exist_ok=True)
            
        csv_name = self._get_filename(symbol, market)
        filename = os.path.join(market_dir, csv_name)
        
        # User's exact Spreadsheet Columns
        columns = [
            "Entry Date", "Exit Date", "Diff Date", "Signal", 
            "Stock", "Open", "Close", "P/L", "%P/L", "Status"
        ]
        
        # Load or Create DataFrame
        if os.path.exists(filename):
            df = pd.read_csv(filename)
        else:
            df = pd.DataFrame(columns=columns)
        
        # Check if there is already an OPEN trade
        if not df.empty and df.iloc[-1]['Status'] == 'OPEN':
            if not silent: 
                print(f"⚠️ {symbol} already has an OPEN trade in {market}. Skipping new entry.")
            return

        # Create New Entry
        if entry_date is None:
            entry_date = datetime.now().strftime("%Y-%m-%d")
            
        new_row = {
            "Entry Date": entry_date,
            "Exit Date": "",
            "Diff Date": "",
            "Signal": signal,
            "Stock": symbol, 
            "Open": entry_price,
            "Close": "",
            "P/L": "",
            "%P/L": "",
            "Status": "OPEN"
        }
        
        new_df = pd.DataFrame([new_row])
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)
        
        # Ensure directory exists RIGHT before write (belt + suspenders)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            if not silent:
                print(f"📝 Logged {symbol} ({market}): {signal} @ {entry_price}")
        except Exception as e:
            print(f"❌ WRITE FAILED: {filename}")
            print(f"   Dir exists: {os.path.exists(os.path.dirname(filename))}")
            print(f"   Error: {e}")
            # Last resort: try writing to project root as fallback
            fallback = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "logs", market)
            os.makedirs(fallback, exist_ok=True)
            fallback_file = os.path.join(fallback, f"{symbol}.csv")
            df.to_csv(fallback_file, index=False, encoding='utf-8-sig')
            print(f"📝 Logged to fallback: {fallback_file}")

    def close_trade(self, symbol, exit_price, exit_date=None, market="Other", silent=False):
        """
        Closes the OPEN trade for a specific stock.
        """
        market_dir = os.path.join(self.log_dir, market)
        csv_name = self._get_filename(symbol, market)
        filename = os.path.join(market_dir, csv_name)
        
        if not os.path.exists(filename):
            # Normal: No previous trade to close for this symbol
            return

        df = pd.read_csv(filename)
        
        if df.empty or df.iloc[-1]['Status'] != 'OPEN':
            # Silence this to reduce console noise during main scan
            # print(f"ℹ️ No OPEN trade to close for {symbol} in {market}.")
            return

        # V4.5 Rule: Only close if the trade was opened BEFORE today
        # (We want to check yesterday's homework, not today's newly opened signals)
        entry_date_str = df.at[df.index[-1], 'Entry Date']
        if exit_date is None:
            exit_date = datetime.now().strftime("%Y-%m-%d")
        
        if entry_date_str == exit_date:
            # Same day, don't close yet (Wait for N+1)
            return

        # Close the last row
        idx = df.index[-1]
        
        entry_price = float(df.at[idx, 'Open'])
        signal = df.at[idx, 'Signal']
        entry_date_str = df.at[idx, 'Entry Date']
        
        if exit_date is None:
            exit_date = datetime.now().strftime("%Y-%m-%d")
            
        # Calculate Duration
        try:
            d1 = datetime.strptime(str(entry_date_str), "%Y-%m-%d")
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
        if 'Exit Date' in df.columns:
            df['Exit Date'] = df['Exit Date'].astype(object)
        
        df.at[idx, 'Exit Date'] = exit_date
        # In the user excel, Close is the exit price
        df.at[idx, 'Close'] = exit_price
        df.at[idx, 'Diff Date'] = duration
        df.at[idx, 'P/L'] = round(pnl_value, 2)
        df.at[idx, '%P/L'] = round(pnl_pct, 2)
        df.at[idx, 'Status'] = 'CLOSED'
        
        df.to_csv(filename, index=False)
        if not silent:
            print(f"✅ Closed {symbol}: {pnl_pct:.2f}% ({duration} days)")


if __name__ == "__main__":
    # Test
    logger = StockLogger()
    # logger.log_trade("TEST", "UP", 100)
    # logger.close_trade("TEST", 105)
