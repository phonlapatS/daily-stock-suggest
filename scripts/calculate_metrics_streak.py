#!/usr/bin/env python
"""
calculate_metrics_streak.py (Refactored to Holding Period Analysis)
===================================================================

Analyzes trade performance over fixed holding periods (N+1, N+3, N+5 days)
to determine the optimal exit strategy for each market.

This script:
1. Loads trade history from logs/trade_history_*.csv
2. Groups trades by Symbol
3. Fetches historical price data using proper cache/TVDatafeed
4. Calculates returns for held positions (1d, 3d, 5d)
5. Generates a comparative report (Win Rate, Avg Win/Loss, RRR)
"""

import os
import sys
import pandas as pd
import numpy as np
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache

# Initialize TV Datafeed (Global)
tv = TvDatafeed()

def load_all_trade_logs():
    """Load and merge all trade_history_*.csv files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        # Fallback to single file
        single = os.path.join(base_dir, "logs", "trade_history.csv")
        if os.path.exists(single):
            return pd.read_csv(single)
        return pd.DataFrame()
        
    dfs = []
    print(f"📂 Loading trade logs from {len(files)} files...")
    for f in files:
        try:
            df = pd.read_csv(f)
            # Add country/group info if missing, based on filename
            filename = os.path.basename(f).upper()
            if 'THAI' in filename: df['Country'] = 'TH'
            elif 'US' in filename: df['Country'] = 'US'
            elif 'CHINA' in filename: df['Country'] = 'CN'
            elif 'TAIWAN' in filename: df['Country'] = 'TW'
            elif 'METALS' in filename: df['Country'] = 'GL'
            else: df['Country'] = 'GL'
            
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ Error reading {f}: {e}")
            
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def process_symbol_metrics(symbol, exchange, trades):
    """
    Calculate N+1, N+3, N+5 returns for a single symbol.
    Returns a list of result dicts (one for each trade).
    """
    if trades.empty: return []
    
    # Ensure symbol is string (may be int from CSV)
    symbol = str(symbol)
    exchange = str(exchange) if exchange else 'SET'
    
    # 1. Fetch Historical Data
    # We need enough history to cover the last trade + 5 days
    # Defaulting to 5000 bars to be safe
    df = get_data_with_cache(tv, symbol, exchange, Interval.in_daily, 5000)
    
    if df is None or df.empty:
        return []

    df = df.copy()
    df['next_close'] = df['close'].shift(-1)
    df['close_3d'] = df['close'].shift(-3)
    df['close_5d'] = df['close'].shift(-5)
    
    # Ensure index is datetime (remove timezone if present for safe comparison)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    
    results = []
    
    for _, trade in trades.iterrows():
        try:
            trade_date = pd.to_datetime(trade['date']).tz_localize(None)
            forecast = trade['forecast'] # UP or DOWN
            
            # Find the row for this trade date
            # We use 'asof' or exact match. Since backtest is daily, exact match should work
            # or finding the closest index.
            if trade_date not in df.index:
                continue
                
            idx = df.index.get_loc(trade_date)
            row = df.iloc[idx]
            
            # Get Future Prices
            # Note: The 'row' is the signal candle. Entry is implicitly at Close (or next Open).
            # The system calculates return based on:
            # Entry = Close of Signal Day
            # Exit N+1 = Close of Next Day
            # Exit N+3 = Close of N+3 Day
            
            entry_price = row['close']
            price_1d = row['next_close']
            price_3d = row['close_3d']
            price_5d = row['close_5d']
            
            if pd.isna(price_1d): continue # Data ends
            
            # Calculate Returns (%)
            # Direction Multiplier: UP = 1, DOWN = -1
            direction = 1 if forecast == 'UP' else -1
            
            ret_1d = ((price_1d - entry_price) / entry_price) * direction * 100
            ret_3d = ((price_3d - entry_price) / entry_price) * direction * 100 if not pd.isna(price_3d) else np.nan
            ret_5d = ((price_5d - entry_price) / entry_price) * direction * 100 if not pd.isna(price_5d) else np.nan
            
            results.append({
                'Country': trade.get('Country', 'GL'),
                'Group': trade.get('group', 'N/A'),
                'Symbol': symbol,
                'Date': trade_date,
                'Forecast': forecast,
                'Return_1d': ret_1d,
                'Return_3d': ret_3d,
                'Return_5d': ret_5d
            })
            
        except Exception as e:
            continue
            
    return results

def analyze_holding_periods():
    print("\n📊 ANALYZING HOLDING PERIODS (N+1, N+3, N+5)...")
    print("=" * 60)
    
    # 1. Load Data
    all_trades = load_all_trade_logs()
    if all_trades.empty:
        print("❌ No trade data found.")
        return

    print(f"✅ Loaded {len(all_trades)} trades. Fetching price history...")
    
    # 2. Process per Symbol (Parallel)
    # Ensure symbol and exchange are strings (may be int/float from CSV)
    all_trades['symbol'] = all_trades['symbol'].astype(str)
    all_trades['exchange'] = all_trades['exchange'].astype(str)
    
    grouped = all_trades.groupby(['symbol', 'exchange'])
    all_results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_symbol_metrics, sym, exc, group): sym for (sym, exc), group in grouped}
        
        for future in as_completed(futures):
            res = future.result()
            if res:
                all_results.extend(res)
                
    if not all_results:
        print("❌ Could not calculate returns (Missing data).")
        return
        
    # 3. Aggregate Results
    df_res = pd.DataFrame(all_results)
    
    # Define Metrics Calculation
    def calc_stats(series):
        valid = series.dropna()
        if valid.empty: return np.nan, np.nan, np.nan, np.nan
        
        count = len(valid)
        wins = valid[valid > 0]
        losses = valid[valid <= 0]
        
        win_rate = (len(wins) / count) * 100
        avg_win = wins.mean() if not wins.empty else 0
        avg_loss = abs(losses.mean()) if not losses.empty else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        return win_rate, avg_win, avg_loss, rrr
    
    # 4. Generate Report Table
    print("\n🏆 HOLDING PERIOD PERFORMANCE REPORT")
    print("=" * 100)
    print(f"{'Market':<15} {'Holding':<12} {'Win Rate':>8} {'Avg Win':>10} {'Avg Loss':>10} {'RRR':>6}   {'Note'}")
    print("-" * 100)
    
    # Analysis by Country (Group)
    groups = {
        'US': 'US (Trend)',
        'TH': 'TH (Revert)',
        'CN': 'CN (Trend)',
        'TW': 'TW (Trend)',
        'GL': 'Global'
    }
    
    for country_code, label in groups.items():
        subset = df_res[df_res['Country'] == country_code]
        if subset.empty: continue
        
        periods = [('N+1 (1 Day)', 'Return_1d'), ('N+3 (3 Days)', 'Return_3d'), ('N+5 (5 Days)', 'Return_5d')]
        
        first_row = True
        for p_label, col in periods:
            wr, aw, al, rr = calc_stats(subset[col])
            
            if np.isnan(wr): continue
            
            # Simple Heuristic Note
            if rr > 2.0: note = "(จุดนี้แหละ! 🚀)"
            elif rr > 1.5: note = "(ใช้ได้ ✅)"
            elif rr < 1.0: note = "(ไม่คุ้มความเสี่ยง ❌)"
            elif wr < 45.0: note = "(แม่นยำต่ำ ⚠️)"
            else: note = ""
            
            # Format Output
            market_str = label if first_row else ""
            print(f"{market_str:<15} {p_label:<12} {wr:>7.0f}% {aw:>9.1f}% {al:>9.1f}% {rr:>6.2f}   {note}")
            first_row = False
            
        print("-" * 100)

    # Save to CSV
    output_path = "data/holding_period_analysis.csv"
    os.makedirs("data", exist_ok=True)
    df_res.to_csv(output_path, index=False)
    print(f"\n💾 Detailed analysis saved to: {output_path}")

if __name__ == "__main__":
    analyze_holding_periods()


