import pandas as pd
import os
from tabulate import tabulate
import sys

def view_performance_log(n=20, filter_pending=False, filter_verified=False, symbol=None):
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        return

    try:
        df = pd.read_csv(log_file)
        if df.empty:
            print("ℹ️ Log file is empty.")
            return

        # V4.6.3: Symbol Filtering (Audit Trail)
        title = ""
        if symbol:
            symbol = symbol.upper()
            df = df[df['symbol'] == symbol]
            if df.empty:
                print(f"❌ No records found for symbol: {symbol}")
                return
            title = f"🔍 AUDIT TRAIL: {symbol} (Full History)"
            # For audit, we usually want chronological order (oldest to newest) 
            # or reverse chronological depending on preference. 
            # Let's keep reverse chronological to see recent first.
            df['scan_date'] = pd.to_datetime(df['scan_date'])
            df = df.sort_values(by='scan_date', ascending=False)
        else:
            # Sort by date (newest first)
            df['scan_date'] = pd.to_datetime(df['scan_date'])
            df = df.sort_values(by='scan_date', ascending=False)
        
        # Format Date
        df['scan_date'] = df['scan_date'].dt.strftime('%Y-%m-%d')
        
        # Filter Logic (Only if not symbol-specific)
        if not symbol:
            if filter_pending:
                df = df[df['actual'] == 'PENDING']
                title = f"📋 PENDING FORECASTS ({len(df)})"
            elif filter_verified:
                df = df[df['actual'] != 'PENDING']
                title = f"✅ VERIFIED FORECASTS (Last {n})"
                df = df.head(n) # Limit for verified
            else:
                title = f"📋 PERFORMANCE LOG (Last {n} entries)"
                df = df.head(n)

        # V4.6.3: Calculate PnL for auditing
        if 'actual' in df.columns and 'price_at_scan' in df.columns and 'price_actual' in df.columns:
            # Drop rows where price is missing/pending for PnL calculation
            pnl_df = df.copy()
            # Realized change: (Actual final price - Price when scanned) / Price when scanned
            pnl_df['realized_change'] = (pnl_df['price_actual'] - pnl_df['price_at_scan']) / pnl_df['price_at_scan'] * 100.0
            # Profit: if forecast UP then pnl is realized_change, if DOWN then -realized_change
            df['PnL%'] = np.where(pnl_df['forecast'] == 'UP', 
                                  pnl_df['realized_change'], 
                                  -pnl_df['realized_change'])
            # Round for display
            df['PnL%'] = df['PnL%'].round(2).apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "")

        # Select Columns (V4.6.6: Added target_date for Audit)
        cols = ['scan_date', 'symbol', 'pattern', 'forecast', 'prob', 'actual', 'correct', 'target_date', 'PnL%']
        
        # Check standard columns exist
        available_cols = [c for c in cols if c in df.columns]
        display_df = df[available_cols].copy()

        # Add Emoji (V4.6.5: Moved into grouping logic for better control)
        if symbol:
            if 'correct' in display_df.columns:
                display_df['correct'] = display_df['correct'].apply(lambda x: '✅' if x==1 else ('❌' if x==0 else '⏳'))
            
            if 'forecast' in display_df.columns:
                display_df['forecast'] = display_df['forecast'].apply(lambda x: f"🟢 {x}" if x=='UP' else (f"🔴 {x}" if x=='DOWN' else x))

            if 'actual' in display_df.columns:
                 display_df['actual'] = display_df['actual'].fillna('PENDING')
                 display_df['actual'] = display_df['actual'].apply(lambda x: f"🟢 {x}" if x=='UP' else (f"🔴 {x}" if x=='DOWN' else (f"⚪ {x}" if x=='NEUTRAL' else f"⏳ {x}")))

        print("\n" + "="*len(title))
        print(title)
        print("="*len(title))
        
        if display_df.empty:
            print("No records found matching criteria.")
        else:
            # V4.6.5: Split by Market and Date
            if symbol:
                print(tabulate(display_df, headers='keys', tablefmt='simple', showindex=False))
            else:
                exchanges = df['exchange'].unique()
                for ex in exchanges:
                    ex_df = df[df['exchange'] == ex]
                    if not ex_df.empty:
                        print(f"\n🌍 MARKET: {ex}")
                        print("=" * 30)
                        
                        # Group by Date
                        dates = ex_df['scan_date'].unique()
                        for d in dates:
                            date_df = ex_df[ex_df['scan_date'] == d]
                            # V4.6.6: Add 'Target' (Predict For) column for absolute clarity
                            sub_cols = ['symbol', 'pattern', 'forecast', 'prob', 'actual', 'correct', 'target_date', 'PnL%']
                            display_sub = date_df[sub_cols].copy()
                            
                            # Rename target_date for better UX
                            display_sub = display_sub.rename(columns={'target_date': 'Target'})
                            
                            # Add grouping labels
                            if 'correct' in display_sub.columns:
                                display_sub['correct'] = display_sub['correct'].apply(lambda x: '✅' if x==1 else ('❌' if x==0 else '⏳'))
                            
                            if 'forecast' in display_sub.columns:
                                display_sub['forecast'] = display_sub['forecast'].apply(lambda x: f"🟢 {x}" if x=='UP' else (f"🔴 {x}" if x=='DOWN' else x))

                            if 'actual' in display_sub.columns:
                                 display_sub['actual'] = display_sub['actual'].fillna('PENDING')
                                 display_sub['actual'] = display_sub['actual'].apply(lambda x: f"🟢 {x}" if x=='UP' else (f"🔴 {x}" if x=='DOWN' else (f"⚪ {x}" if x=='NEUTRAL' else f"⏳ {x}")))

                            print(f"\n📅 Date: {d}")
                            print("-" * 15)
                            print(tabulate(display_sub, headers='keys', tablefmt='simple', showindex=False))
                        
                        print("-" * 80)
            
        print(f"\nTotal Log Entries: {len(pd.read_csv(log_file))}\n")

    except Exception as e:
        print(f"❌ Error reading log: {e}")

if __name__ == "__main__":
    import numpy as np
    n_display = 100 # Increased default for "showing every day"
    pending_only = False
    verified_only = False
    symbol_filter = None
    
    # Simple argument parsing
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        if arg == 'PENDING':
            pending_only = True
        elif arg == 'VERIFIED':
            verified_only = True
            if len(sys.argv) > 2:
                try: n_display = int(sys.argv[2])
                except: pass
        elif arg.isdigit():
            n_display = int(arg)
        else:
            # Assume it's a symbol
            symbol_filter = arg
            
    view_performance_log(n=n_display, filter_pending=pending_only, filter_verified=verified_only, symbol=symbol_filter)
