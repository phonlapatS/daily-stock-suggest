#!/usr/bin/env python
from collections import defaultdict
import pandas as pd
import numpy as np
import os
import sys

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Helper to build symbol name map
def get_symbol_map():
    mapping = {}
    for group in config.ASSET_GROUPS.values():
        for asset in group['assets']:
            if 'name' in asset:
                mapping[asset['symbol']] = asset['name']
    return mapping

SYMBOL_MAP = get_symbol_map()

def get_country_code(group_name, symbol=None):
    """
    Determine country code from group name or symbol.
    Priority: group_name > symbol lookup in config
    """
    # Try group name first
    if isinstance(group_name, str):
        if 'THAI' in group_name: return 'TH'
        if 'US' in group_name: return 'US'
        if 'CHINA' in group_name: return 'CN'
        if 'HK' in group_name: return 'HK'
        if 'TAIWAN' in group_name: return 'TW'
        if 'METAL' in group_name or 'GOLD' in group_name or 'SILVER' in group_name:
            return 'GL'
    
    # Fallback: lookup symbol in config
    if symbol:
        for group_key, group_data in config.ASSET_GROUPS.items():
            for asset in group_data.get('assets', []):
                if asset.get('symbol') == symbol:
                    if 'THAI' in group_key: return 'TH'
                    if 'US' in group_key: return 'US'
                    if 'CHINA' in group_key: return 'CN'
                    if 'HK' in group_key: return 'HK'
                    if 'TAIWAN' in group_key: return 'TW'
                    if 'METAL' in group_key or 'GOLD' in group_key or 'SILVER' in group_key:
                        return 'GL'
    
    return 'GL'  # Default to Global/Metals


# ==============================================================================
# Helper Functions: Print Tables
# ==============================================================================
def print_table(df, title, icon="✅"):
    """
    Detailed table: Raw vs Elite comparison (used mainly for System Edge / debug).
    """
    if df.empty:
        print(f"\n{title}")
        print("=" * 100)
        print("   (No Data)")
        return

    print(f"\n{title}")
    print("=" * 100)
    print(f"{'Symbol':<10} {'Ctry':<6} {'Count':>6} {'Prob%':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>6}")
    print("-" * 100)
    
    for _, row in df.iterrows():
        print(f"{str(row.get('Symbol',row.get('symbol','?'))):<10} "
              f"{str(row.get('Country','?')):<6} "
              f"{int(row.get('Count',0)):>6} "
              f"{float(row.get('Prob%',0)):>7.1f}% "
              f"{float(row.get('AvgWin%',0)):>9.2f}% "
              f"{float(row.get('AvgLoss%',0)):>9.2f}% "
              f"{float(row.get('RRR',row.get('RR_Ratio',0))):>6.2f}")
    print("-" * 100)

import glob

def load_trade_data(file_path):
    """
    Load trade data from CSV(s). Prioritizes merging multiple logs/trade_history_*.csv 
    over a single file, to ensure latest data is used.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Check for Split Files First (Priority)
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    
    # Filter out the main "trade_history.csv" if it exists in the glob results 
    # (though glob usually won't match it if pattern has _*)
    files = [f for f in files if "trade_history.csv" not in os.path.basename(f)]

    if files:
        print(f"📂 Found {len(files)} split logs. Prioritizing over single file.")
        dfs = []
        for f in files:
            try:
                # Robust loading with error correction
                df = pd.read_csv(f, on_bad_lines='skip', engine='python')
                print(f"   > Loaded {len(df)} rows from {os.path.basename(f)}")
                if not df.empty:
                    # Normalize columns if needed (e.g. handle missing 'Country')
                    if 'Country' not in df.columns:
                        filename = os.path.basename(f).upper()
                        if 'THAI' in filename: df['Country'] = 'TH'
                        elif 'US' in filename: df['Country'] = 'US'
                        elif 'CHINA' in filename: df['Country'] = 'CN'
                        elif 'TAIWAN' in filename: df['Country'] = 'TW'
                        elif 'METALS' in filename: df['Country'] = 'GL'
                        else: df['Country'] = 'GL'
                    dfs.append(df)
            except Exception as e:
                print(f"⚠️ Error reading {os.path.basename(f)}: {e}")
        
        if dfs: 
            return pd.concat(dfs, ignore_index=True)

    # 2. Fallback: Standard single file load
    if os.path.exists(file_path):
        try:
            print(f"📂 Loading single file (Fallback): {os.path.basename(file_path)}")
            df = pd.read_csv(file_path, on_bad_lines='skip', engine='python') # Skip malformed lines automatically
            return df
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return pd.DataFrame()
            
    print(f"❌ No trade history files found.")
    return pd.DataFrame()

def print_raw_vs_elite_table(df, title):
    print(f"\n{title}")
    print("=" * 140)
    print(f"{'Symbol':<15} {'Ctry':<8} {'Raw Cnt':>8} {'Raw%':>8} {'Elite Cnt':>10} {'Elite%':>8} {'Δ Prob':>8} {'RRR':>8}")
    print("-" * 140)
    
    if df.empty:
        print(f"{'No candidates found matching criteria.':^140}")
    else:
        processed_data = []
        seen_keys = {} 
        
        for _, row in df.iterrows():
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            
            delta_prob = row['Elite_Prob%'] - row['Raw_Prob%']
            
            stats_key = (
                display_name,
                row['Raw_Count'],
                row['Elite_Count'],
                row['Raw_Prob%'],
                row['Elite_Prob%']
            )
            
            country_code = row['Country'] if 'Country' in row else 'GL'
            
            if stats_key in seen_keys:
                idx = seen_keys[stats_key]
                existing_country = processed_data[idx]['Country']
                if country_code not in existing_country:
                     processed_data[idx]['Country'] = f"{existing_country}, {country_code}"
            else:
                entry = row.to_dict()
                entry['display_name'] = display_name
                entry['Country'] = country_code
                entry['Delta'] = delta_prob
                processed_data.append(entry)
                seen_keys[stats_key] = len(processed_data) - 1

        for row in processed_data:
            print(f"{row['display_name']:<15} {row['Country']:<8} {int(row['Raw_Count']):>8} {row['Raw_Prob%']:>7.1f}% {int(row['Elite_Count']):>10} {row['Elite_Prob%']:>7.1f}% {row['Delta']:>7.1f}% {row['RR_Ratio']:>8.2f}")
        
    print("-" * 140)


def print_simple_table(df, title):
    """
    Simple table for Mentor-facing reports.
    Columns: Symbol, Ctry, Count, Prob%, AvgWin%, AvgLoss%, RRR
    """
    print(f"\n{title}")
    print("=" * 120)
    print(f"{'Symbol':<10} {'Ctry':<6} {'Count':>8} {'Prob%':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>6}")
    print("-" * 120)

    if df.empty:
        print(f"{'No candidates found matching criteria.':^120}")
    else:
        for _, row in df.iterrows():
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            country = row.get('Country', 'GL')
            count = int(row.get('Count', 0))
            prob = row.get('Prob%', 0.0)
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)

            print(
                f"{display_name:<10} {country:<6} {count:>8d} "
                f"{prob:>7.1f}% {avg_win:>9.2f}% {avg_loss:>9.2f}% {rrr:>6.2f}"
            )

    print("-" * 120)


def calculate_metrics(input_path='logs/trade_history.csv', output_path='data/symbol_performance.csv'):
    # Resolve input path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(input_path):
        input_path = os.path.join(base_dir, input_path)
    if not os.path.isabs(output_path):
        output_path = os.path.join(base_dir, output_path)

    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return

    print(f"\n📊 Calculating Metrics from: {input_path}")
    
    df = load_trade_data(input_path)

    if df.empty:
        print("❌ No trade data loaded. Exiting.")
        return

    print(f"   Loaded {len(df)} trades (malformed rows auto-skipped).")

    # --- Step 1: Metrics Calculation Logic ---
    def calculate_symbol_metrics(group):
        raw_count = len(group)
        if group.empty:
            return None
        
        # Ensure numeric returns
        group['actual_return'] = pd.to_numeric(group['actual_return'], errors='coerce')
        group = group.dropna(subset=['actual_return'])
        
        if group.empty:
            return None

        # --- Step 1: Segmentation ---
        total = len(group)
        raw_count = total
        
        # Win Rate for Raw
        # Forecast is 'UP'/'DOWN', Actual is 'UP'/'DOWN'
        # Or check 'correct' column if available
        if 'correct' in group.columns:
            group['correct'] = pd.to_numeric(group['correct'], errors='coerce').fillna(0)
            raw_correct = group[group['correct'] == 1]
        else:
            # Fallback logic
            raw_correct = group[group['forecast'] == group['actual']]
            
        raw_prob = (len(raw_correct) / raw_count) * 100 if raw_count > 0 else 0
        
        # Elite Filter: Prob >= 60%
        # This requires historical probability field 'prob'
        if 'prob' in group.columns:
            group['prob'] = pd.to_numeric(group['prob'], errors='coerce').fillna(0)
            elite_group = group[group['prob'] >= 60.0]
        else:
            elite_group = pd.DataFrame()
            
        elite_count = len(elite_group)
        
        if elite_count == 0:
            elite_prob = 0
            # Fallback to reported group being the raw group if elite is empty
            report_group = group
        else:
            if 'correct' in elite_group.columns:
                elite_correct = elite_group[elite_group['correct'] == 1]
            else:
                elite_correct = elite_group[elite_group['forecast'] == elite_group['actual']]
                
            elite_prob = (len(elite_correct) / elite_count) * 100
            report_group = elite_group
            
        # Calculation for PnL using whichever group we want to report (Elite if possible)
        # Fix: Ensure report_group is a copy and handle missing actual_return
        report_group = report_group.copy()
        report_group['actual_return'] = pd.to_numeric(report_group['actual_return'], errors='coerce').fillna(0)
        report_group['pnl'] = report_group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        real_wins = report_group[report_group['pnl'] > 0]
        real_losses = report_group[report_group['pnl'] <= 0]
        avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
        avg_loss = abs(report_group[report_group['pnl'] <= 0]['pnl'].mean()) if not real_losses.empty else 0
        
        rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        group_name = group['group'].iloc[0] if 'group' in group.columns else 'N/A'
        symbol = group['symbol'].iloc[0] if 'symbol' in group.columns else None
        
        return pd.Series({
            'Group': group_name,
            'Country': get_country_code(str(group_name), symbol),
            'Raw_Count': raw_count,
            'Raw_Prob%': round(raw_prob, 1),
            'Elite_Count': elite_count,
            'Elite_Prob%': round(elite_prob, 1),
            'RR_Ratio': round(rr_ratio, 2),
            # avg_win / avg_loss already in percent units (e.g. 2.5 = +2.5%),
            # so we keep them as-is for mentor-facing tables.
            'AvgWin%': round(avg_win, 2) if avg_win is not None else 0.0,
            'AvgLoss%': round(avg_loss, 2) if avg_loss is not None else 0.0,
            # Keep Prob% as Elite_Prob for sorting and filtering tables
            'Prob%': round(elite_prob if elite_count >= 5 else raw_prob, 1) 
        })

    # --- Step 2: Aggregation ---
    # Group by Symbol + Group to preserve metadata
    # Use include_groups=False or explicit selection to avoid FutureWarning
    summary_df = df.groupby(['symbol', 'group']).apply(calculate_symbol_metrics).reset_index()
    
    if summary_df.empty:
        print("⚠️ No valid symbols found (min 10 trades).")
        return

    # Derive Count used in Mentor-facing tables:
    # If Elite_Count is available (>=5), use it; otherwise fall back to Raw_Count.
    summary_df['Count'] = summary_df.apply(
        lambda row: row['Elite_Count'] if row['Elite_Count'] >= 5 else row['Raw_Count'],
        axis=1
    )

    # Sort for better readability (High Prob, High RR first)
    summary_df = summary_df.sort_values(by=['Prob%', 'RR_Ratio'], ascending=[False, False])
    
    # Save raw data for further analysis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False)

    # --- REPORT GENERATION ---
    print(f"\n📊 METRICS REPORT: MARKET OVERVIEW")
    print("=" * 140)

    # 1. DATA HEALTH CHECK
    print(f"🔎 DATA HEALTH CHECK (Trades Loaded per Market)")
    print("-" * 60)
    market_counts = summary_df.groupby('Country')['Count'].sum()
    if market_counts.empty:
        print("   (No trades found in any market)")
    else:
        for ctry, count in market_counts.items():
            print(f"   {ctry:<6}: {count:>6} trades")
    print("-" * 60)

    # Helper to print fallback if empty
    def print_market_section(df_subset, market_name, strict_rule="Prob > 50% | RRR > 1.0"):
        if not df_subset.empty:
            print_simple_table(df_subset, f"{market_name} (Matches: {strict_rule})")
        else:
            # Fallback: Top 5 by Activity
            fallback = summary_df[summary_df['Country'] == market_name[:2]].sort_values(by='Count', ascending=False).head(5)
            if not fallback.empty:
                print_simple_table(fallback, f"{market_name} (Top 5 by Activity - No Strict Matches)")
            else:
                 print(f"\n{market_name}: No trades found.")

    # ========================================
    # 🇹🇭 THAI MARKET (Reversion -> High Prob needed)
    # ========================================
    # ========================================
    # 🇹🇭 THAI MARKET (Reversion -> Higher Frequency & Accuracy)
    # ========================================
    thai_trend = summary_df[
        (summary_df['Country'] == 'TH') & 
        (summary_df['Prob%'] >= 60.0) & 
        (summary_df['RR_Ratio'] >= 1.2) &
        (summary_df['Count'] >= 30)  # Filter for statistical significance (High Freq)
    ].head(10)
    print_market_section(thai_trend, "🇹🇭 THAI MARKET", "Prob >= 60% | RRR >= 1.2 | Count >= 30")

    # ========================================
    # 🇺🇸 US STOCK (Trend -> Lower Frequency, High Impact)
    # ========================================
    us_trend = summary_df[
        (summary_df['Country'] == 'US') & 
        (summary_df['Prob%'] >= 55.0) & 
        (summary_df['RR_Ratio'] >= 1.2) &
        (summary_df['Count'] >= 15) # Filter for reliability (Trend trades less often)
    ].head(15)
    print_market_section(us_trend, "🇺🇸 US STOCK", "Prob >= 55% | RRR >= 1.2 | Count >= 15")

    # ========================================
    # 🇨🇳 CHINA MARKET (Trend)
    # ========================================
    china_trend = summary_df[
        (summary_df['Country'] == 'CN') & 
        (summary_df['Prob%'] >= 55.0) & 
        (summary_df['RR_Ratio'] >= 1.2) &
        (summary_df['Count'] >= 15)
    ].head(10)
    print_market_section(china_trend, "🇨🇳 CHINA & HK MARKET", "Prob >= 55% | RRR >= 1.2 | Count >= 15")

    # ========================================
    # 🇹🇼 TAIWAN MARKET (Trend)
    # ========================================
    tw_trend = summary_df[
        (summary_df['Country'] == 'TW') & 
        (summary_df['Prob%'] >= 55.0) & 
        (summary_df['RR_Ratio'] >= 1.2) &
        (summary_df['Count'] >= 15)
    ].head(10)
    print_market_section(tw_trend, "🇹🇼 TAIWAN MARKET", "Prob >= 55% | RRR >= 1.2 | Count >= 15")

    # ========================================
    # 🥇 METALS (Reversion)
    # ========================================
    metals = summary_df[
        (summary_df['Country'] == 'GL') & 
        (summary_df['Prob%'] >= 50.0)
    ].head(5)
    print_market_section(metals, "🥇 METALS", "Prob >= 50%")

    print(f"\n💾 Detailed report saved to: {output_path}")

if __name__ == "__main__":
    calculate_metrics()
