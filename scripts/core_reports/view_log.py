import pandas as pd
import os
from tabulate import tabulate
import sys

def view_performance_log(n=20, filter_pending=False, filter_verified=False):
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        return

    try:
        df = pd.read_csv(log_file)
        if df.empty:
            print("ℹ️ Log file is empty.")
            return

        # Sort by date (newest first)
        df['scan_date'] = pd.to_datetime(df['scan_date'])
        df = df.sort_values(by='scan_date', ascending=False)
        
        # Format Date
        df['scan_date'] = df['scan_date'].dt.strftime('%Y-%m-%d')
        
        # Filter Logic
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

        # Select Columns
        cols = ['scan_date', 'target_date', 'symbol', 'exchange', 'forecast', 'prob', 'actual', 'correct', 'price_at_scan', 'change_pct']
        
        # Check standard columns exist
        available_cols = [c for c in cols if c in df.columns]
        display_df = df[available_cols].copy()

        # Add Emoji
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
            print(tabulate(display_df, headers='keys', tablefmt='simple', showindex=False))
            
        print(f"\nTotal Log Entries: {len(pd.read_csv(log_file))}\n")

    except Exception as e:
        print(f"❌ Error reading log: {e}")

if __name__ == "__main__":
    import sys
    n_display = 20
    pending_only = False
    verified_only = False
    
    # Simple argument parsing
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'pending':
            pending_only = True
        elif arg == 'verified':
            verified_only = True
            # Optional: check if second arg is number
            if len(sys.argv) > 2:
                try:
                    n_display = int(sys.argv[2])
                except:
                    pass
        elif arg.isdigit():
            n_display = int(arg)
            
    view_performance_log(n=n_display, filter_pending=pending_only, filter_verified=verified_only)
