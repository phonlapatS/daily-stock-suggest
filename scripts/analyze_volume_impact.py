import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

# Config
LOG_DIR = "e:/PredictPlus1/logs"
CACHE_DIR = "e:/PredictPlus1/data/cache"
OUTPUT_FILE = "e:/PredictPlus1/data/VOLUME_IMPACT_REPORT.md"

def load_all_trades():
    all_files = glob.glob(os.path.join(LOG_DIR, "trade_history_*.csv"))
    df_list = []
    
    for f in all_files:
        try:
            temp_df = pd.read_csv(f)
            # Add Market Source
            market_name = os.path.basename(f).replace("trade_history_", "").replace(".csv", "")
            temp_df['Market'] = market_name
            df_list.append(temp_df)
        except Exception as e:
            print(f"Skipping {f}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    full_df = pd.concat(df_list, ignore_index=True)
    
    # Normalize Date
    full_df['date'] = pd.to_datetime(full_df['date'])
    return full_df

def get_volume_data(symbol, market):
    # Try different naming conventions
    files_to_try = [
        f"TWSE_{symbol}.csv",
        f"OANDA_{symbol}.csv",
        f"OANDA_{symbol}_30m.csv",
        f"SET_{symbol}.csv",
        f"NASDAQ_{symbol}.csv",
        f"HKEX_{symbol}.csv",
        f"{market}_{symbol}.csv" # Fallback
    ]
    
    for f in files_to_try:
        path = os.path.join(CACHE_DIR, f)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                return df
            except:
                continue
    return None

def analyze_volume():
    print("🚀 Starting Volume Impact Analysis...")
    df = load_all_trades()
    print(f"📊 Total Trades: {len(df)}")
    
    results = []
    
    # Group by Market to analyze impact
    markets = df['Market'].unique()
    
    for market in markets:
        print(f"   > Analyzing {market}...")
        market_df = df[df['Market'] == market].copy()
        
        high_vol_wins = 0
        high_vol_total = 0
        normal_vol_wins = 0
        normal_vol_total = 0
        
        # Iterate trades
        for idx, row in market_df.iterrows():
            symbol = row['symbol']
            entry_date = row['date']
            
            # Outcome
            is_win = (row['forecast'] == row['actual'])
            
            # Get Cache
            cache = get_volume_data(symbol, market)
            
            if cache is not None:
                # Normalize cache index to remove time component for daily matching
                cache.index = cache.index.normalize()
                
                # Find date (Daily resolution for most)
                # For Metals (Intraday), we might need exact match or nearest
                
                # Simple logic: check if entry_date exists in index (or close to it)
                # For daily, normalize to midnight
                lookup_date = entry_date.normalize()
                
                if lookup_date in cache.index:
                    loc = cache.index.get_loc(lookup_date)
                    
                    # Need 20 bars for MA
                    if isinstance(loc, int) and loc >= 20:
                        vol_today = cache.iloc[loc]['volume']
                        vol_ma = cache.iloc[loc-20:loc]['volume'].mean()
                        
                        rvol = 0
                        if vol_ma > 0:
                            rvol = vol_today / vol_ma
                            
                        # Binning
                        if rvol >= 1.5:
                            high_vol_total += 1
                            if is_win: high_vol_wins += 1
                        else:
                            normal_vol_total += 1
                            if is_win: normal_vol_wins += 1
                            
                    # Handle slice (duplicate dates) - take first
                    elif isinstance(loc, slice):
                        pass # complicated, skip for now
                        
        # Calc Stats
        base_wr = (normal_vol_wins / normal_vol_total * 100) if normal_vol_total > 0 else 0
        high_vol_wr = (high_vol_wins / high_vol_total * 100) if high_vol_total > 0 else 0
        vol_score = high_vol_wr - base_wr
        
        dataset = {
            "Market": market,
            "Base_WR": base_wr,
            "High_Vol_WR": high_vol_wr,
            "Vol_Score": vol_score,
            "High_Vol_Count": high_vol_total
        }
        results.append(dataset)

    # Generate Report
    report_lines = []
    report_lines.append("# 📊 Volume Logic Optimization Report")
    report_lines.append(f"Generated: {datetime.now()}\n")
    report_lines.append("| Market | Base WR% | High Vol WR% | **Vol Score (Alpha)** | Status |")
    report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for r in results:
        score = r['Vol_Score']
        status = "neutral"
        if score > 5.0: status = "🔥 EDGE"
        elif score < -5.0: status = "⚠️ TRAP"
        
        report_lines.append(f"| {r['Market']} | {r['Base_WR']:.1f}% | {r['High_Vol_WR']:.1f}% | **{score:+.1f}%** | {status} |")
        
    # Recommendation Logic
    report_lines.append("\n## 🧠 Optimization Logic")
    report_lines.append("Based on the data above, here is the recommended configuration:")
    
    for r in results:
        if r['Vol_Score'] > 3.0:
            report_lines.append(f"- **{r['Market']}**: ✅ **ENABLE** Volume Confirmation (Adds +{r['Vol_Score']:.1f}% edge)")
        elif r['Vol_Score'] < -3.0:
            report_lines.append(f"- **{r['Market']}**: ❌ **DISABLE** or **INVERT** (Volume hurts performance by {r['Vol_Score']:.1f}%)")
        else:
            report_lines.append(f"- **{r['Market']}**: ⚪ **OPTIONAL** (Impact is minimal)")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\n✅ Report generated: {OUTPUT_FILE}")
    print(open(OUTPUT_FILE, "r", encoding="utf-8").read())

if __name__ == "__main__":
    analyze_volume()
