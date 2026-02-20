import pandas as pd
import os
from datetime import datetime, timedelta

LOG_FILE = 'logs/performance_log.csv'
TRADE_HISTORY_BACKUP = 'logs/trade_history.csv.bak'
TRADE_HISTORY_MAIN = 'logs/trade_history.csv'

# Dates to restore
TARGET_DATES = ['2026-02-12', '2026-02-13', '2026-02-16', '2026-02-17', '2026-02-18']

def restore_logs():
    print("🚑 Starting Log Restoration...")
    
    restored_records = []
    
    # Try multiple sources
    sources = [TRADE_HISTORY_MAIN, TRADE_HISTORY_BACKUP]
    
    for source in sources:
        if os.path.exists(source):
            print(f"📖 Reading source: {source}")
            try:
                df = pd.read_csv(source)
                # Filter for our target dates
                # Check column names - trade_history usually has 'date' or 'entry_date'
                date_col = 'date' if 'date' in df.columns else 'entry_date'
                
                if date_col in df.columns:
                    # Convert to datetime for comparison
                    df[date_col] = pd.to_datetime(df[date_col])
                    
                    for target_date_str in TARGET_DATES:
                        target_dt = pd.to_datetime(target_date_str)
                        # We want forecasts MADE on this date (scan_date)
                        matches = df[df[date_col].dt.date == target_dt.date()]
                        
                        if not matches.empty:
                            print(f"   found {len(matches)} records for {target_date_str}")
                            for _, row in matches.iterrows():
                                # Map trade_history columns to performance_log columns
                                # This depends on trade_history structure, making best guess + filling defaults
                                record = {
                                    'scan_date': target_date_str,
                                    'target_date': (target_dt + timedelta(days=1)).strftime('%Y-%m-%d'), # Approx
                                    'symbol': row.get('symbol', 'Unknown'),
                                    'exchange': row.get('exchange', 'SET'),
                                    'pattern': row.get('pattern', ''),
                                    'forecast': row.get('side', 'UP'), # 'side' usually UP/DOWN
                                    'prob': row.get('prob', 0),
                                    'conf': 0, # Might not be in trade history
                                    'stats': 0,
                                    'price_at_scan': row.get('price', 0),
                                    'change_pct': 0, # Missing
                                    'threshold': 0, # Missing
                                    'avg_return': 0, # Missing
                                    'total_bars': 0, # Missing
                                    'actual': row.get('outcome', 'PENDING'), # WIN/LOSS/PENDING
                                    'price_actual': row.get('exit_price', 0),
                                    'correct': 1 if row.get('outcome') == 'WIN' else (0 if row.get('outcome') == 'LOSS' else None),
                                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                restored_records.append(record)
            except Exception as e:
                print(f"❌ Error reading {source}: {e}")

    if not restored_records:
        print("⚠️ No records found in backups matching target dates.")
        return

    # Convert to DF
    df_restored = pd.DataFrame(restored_records)
    
    # Remove duplicates
    df_restored.drop_duplicates(subset=['scan_date', 'symbol'], inplace=True)
    
    print(f"✅ Recovered {len(df_restored)} unique forecast records.")
    
    # Merge with existing log if valid
    if os.path.exists(LOG_FILE):
        try:
            df_current = pd.read_csv(LOG_FILE)
            if not df_current.empty:
                print(f"   Merging with {len(df_current)} existing records...")
                df_final = pd.concat([df_current, df_restored], ignore_index=True)
                df_final.drop_duplicates(subset=['scan_date', 'symbol'], inplace=True)
            else:
                df_final = df_restored
        except:
            df_final = df_restored
    else:
        df_final = df_restored

    # Sort
    df_final.sort_values(by=['scan_date', 'symbol'], inplace=True)
    
    # Save
    df_final.to_csv(LOG_FILE, index=False)
    print(f"💾 Saved restored log to {LOG_FILE} ({len(df_final)} rows)")

if __name__ == "__main__":
    restore_logs()
