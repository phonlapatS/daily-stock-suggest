import pandas as pd
import os

LOG_FILE = 'logs/performance_log.csv'
FORECAST_FILE = 'data/forecast_tomorrow.csv'

def backfill():
    if not os.path.exists(LOG_FILE) or not os.path.exists(FORECAST_FILE):
        print("❌ Missing files.")
        return

    print("📖 Loading files...")
    perf_df = pd.read_csv(LOG_FILE)
    fore_df = pd.read_csv(FORECAST_FILE)

    # Ensure columns exist in perf_df
    new_cols = ['change_pct', 'threshold', 'avg_return', 'total_bars']
    for col in new_cols:
        if col not in perf_df.columns:
            perf_df[col] = 0.0

    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    print(f"🔄 Updating entries for scan_date: {today}")

    # Create lookup
    lookup = {}
    for _, row in fore_df.iterrows():
        key = (str(row['symbol']), str(row['pattern']))
        lookup[key] = row

    updated_count = 0
    for idx, row in perf_df.iterrows():
        if str(row['scan_date']) == today:
            key = (str(row['symbol']), str(row['pattern']))
            if key in lookup:
                f_row = lookup[key]
                perf_df.loc[idx, 'change_pct'] = f_row.get('change_pct', 0)
                perf_df.loc[idx, 'threshold'] = f_row.get('threshold', 0)
                perf_df.loc[idx, 'avg_return'] = f_row.get('avg_return', 0)
                perf_df.loc[idx, 'total_bars'] = f_row.get('total_bars', 0)
                updated_count += 1

    perf_df.to_csv(LOG_FILE, index=False)
    print(f"✅ Success! Updated {updated_count} rows in {LOG_FILE}")

if __name__ == "__main__":
    backfill()
