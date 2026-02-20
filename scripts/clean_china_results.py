import pandas as pd
import os

RESULTS_FILE = "data/full_backtest_results.csv"
LOG_FILE = "e:/PredictPlus1/logs/trade_history_CHINA.csv"

def clean_china_results():
    print("🧹 Cleaning China Results...")
    
    # 1. Clean Results File (Tracking)
    if os.path.exists(RESULTS_FILE):
        try:
            df = pd.read_csv(RESULTS_FILE)
            initial_count = len(df)
            
            # Remove China Group
            if 'group' in df.columns:
                df = df[~df['group'].str.contains('CHINA', case=False, na=False)]
                # Also remove specific symbols just in case
                china_symbols = ['700', '9988', '3690', '1810', '9888', '9618', '1211', '2015', '9868', '9866', 
                                 'YUMC', 'HTHT', 'EDU', 'TAL', 'NTES', 'VIPS', 'PDD', 'TCOM', 'ZTO']
                df = df[~df['symbol'].isin(china_symbols)]
                
            final_count = len(df)
            print(f"Removed {initial_count - final_count} China entries from {RESULTS_FILE}")
            
            df.to_csv(RESULTS_FILE, index=False)
            print("✅ Results file updated.")
        except Exception as e:
            print(f"❌ Error cleaning results file: {e}")
            
    else:
        print(f"ℹ️ {RESULTS_FILE} not found (fresh start).")
        
    # 2. Delete Log File
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
            print(f"✅ Deleted {LOG_FILE}")
        except Exception as e:
            print(f"❌ Error deleting log file: {e}")

if __name__ == "__main__":
    clean_china_results()
