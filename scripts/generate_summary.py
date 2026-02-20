#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_summary.py — Stock-Level Summary via N+1 Prediction Bias
====================================================================
Updates:
- Implements "Sum of Winning Frequencies" logic (User Request).
- Instead of 1-pattern-1-vote, we sum the actual occurrences involved in the winning side.
- Filter: Base Pattern Total Count >= 30.

Methodology:
1. For each Base Pattern (e.g. "++-"), compare P_Count (+) vs N_Count (-).
2. Determine Winner:
   - If P > N: Winning_P = P_Count
   - If N > P: Winning_N = N_Count
   - Tie: 0
3. Sum these winning counts per Symbol.
   - Sum_Winning_P = Sum(Winning_P of all valid patterns)
   - Sum_Winning_N = Sum(Winning_N of all valid patterns)
4. Calculate Bias % based on these sums.
"""

import sys
import os
import pandas as pd
import numpy as np

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

MASTER_STATS_FILE = os.path.join(DATA_DIR, 'Master_Pattern_Stats_NewLogic.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'Stock_Prediction_History_Summary.csv')

# Threshold: minimum combined count for a Base Pattern to be considered valid
MIN_BASE_COUNT = 30


def main():
    print("=" * 80)
    print("📊 N+1 PREDICTION BIAS — Stock-Level Summary Generator")
    print("   Logic: Sum of Winning Frequencies")
    print("=" * 80)
    
    # ──────────────────────────────────────────────────
    # Step 1: Load Data
    # ──────────────────────────────────────────────────
    if not os.path.exists(MASTER_STATS_FILE):
        print(f"❌ Master stats not found: {MASTER_STATS_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(MASTER_STATS_FILE)
    print(f"\n📂 Loaded: {MASTER_STATS_FILE}")
    print(f"   Total rows: {len(df):,}")
    
    # ──────────────────────────────────────────────────
    # Step 2: Filter valid lengths & Extract Base/Outcome
    # ──────────────────────────────────────────────────
    # Only Length >= 2 can supply a history base
    df_valid = df[df['Length'] >= 2].copy()
    
    df_valid['Base_Pattern'] = df_valid['Pattern'].str[:-1]
    df_valid['Outcome'] = df_valid['Pattern'].str[-1]
    
    print(f"🔍 Filtered Length >= 2: {len(df_valid):,} rows")
    
    # ──────────────────────────────────────────────────
    # Step 3: Group & Pivot
    # ──────────────────────────────────────────────────
    pivot = df_valid.pivot_table(
        index=['Symbol', 'Market', 'Base_Pattern'],
        columns='Outcome',
        values='Count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Ensure columns exist
    if '+' not in pivot.columns: pivot['+'] = 0
    if '-' not in pivot.columns: pivot['-'] = 0
    
    pivot = pivot.rename(columns={'+': 'P_Count', '-': 'N_Count'})
    
    # ──────────────────────────────────────────────────
    # Step 4: Apply Threshold & Determine Winning Frequency
    # ──────────────────────────────────────────────────
    pivot['Total_Base_Count'] = pivot['P_Count'] + pivot['N_Count']
    
    before_filter = len(pivot)
    pivot_valid = pivot[pivot['Total_Base_Count'] >= MIN_BASE_COUNT].copy()
    after_filter = len(pivot_valid)
    
    print(f"📋 Base Patterns Valid (Count >= {MIN_BASE_COUNT}): {after_filter:,} / {before_filter:,}")
    
    # Logic: Winning Frequency
    def get_winning_counts(row):
        p, n = row['P_Count'], row['N_Count']
        win_p, win_n = 0, 0
        
        if p > n:
            win_p = p  # Add full P count to P bucket
        elif n > p:
            win_n = n  # Add full N count to N bucket
        # Ties contribute 0 to both
            
        return pd.Series([win_p, win_n, 1])

    pivot_valid[['Winning_P', 'Winning_N', 'Valid_Flag']] = pivot_valid.apply(get_winning_counts, axis=1)
    
    # ──────────────────────────────────────────────────
    # Step 5: Aggregate at Symbol Level
    # ──────────────────────────────────────────────────
    symbol_stats = pivot_valid.groupby(['Symbol', 'Market']).agg({
        'Winning_P': 'sum',
        'Winning_N': 'sum',
        'Valid_Flag': 'sum'
    }).reset_index()
    
    symbol_stats = symbol_stats.rename(columns={'Valid_Flag': 'Valid_Patterns'})
    
    # ──────────────────────────────────────────────────
    # Step 6: Map Readable Names (Optional)
    # ──────────────────────────────────────────────────
    # Attempt to load config for names
    try:
        sys.path.append(PROJECT_DIR)
        import config
        symbol_map = {}
        for group in config.ASSET_GROUPS.values():
            for asset in group['assets']:
                if 'name' in asset:
                    symbol_map[asset['symbol']] = asset['name']
        
        # Apply Mapping
        symbol_stats['Display_Symbol'] = symbol_stats['Symbol'].astype(str).map(symbol_map).fillna(symbol_stats['Symbol'])
        
    except:
        symbol_stats['Display_Symbol'] = symbol_stats['Symbol']

    # ──────────────────────────────────────────────────
    # Step 7: Calculate Bias %
    # ──────────────────────────────────────────────────
    symbol_stats['Total_Wins'] = symbol_stats['Winning_P'] + symbol_stats['Winning_N']
    
    # Avoid div by zero
    symbol_stats['Pct_P'] = np.where(symbol_stats['Total_Wins'] > 0, 
                                     (symbol_stats['Winning_P'] / symbol_stats['Total_Wins'] * 100), 0)
    symbol_stats['Pct_N'] = np.where(symbol_stats['Total_Wins'] > 0, 
                                     (symbol_stats['Winning_N'] / symbol_stats['Total_Wins'] * 100), 0)
    
    def determine_bias_str(row):
        if row['Total_Wins'] == 0:
            return "⬜ Neutral"
        
        if row['Pct_P'] > row['Pct_N']:
            return f"🟩 + ({row['Pct_P']:.1f}%)"
        elif row['Pct_N'] > row['Pct_P']:
            return f"🟥 - ({row['Pct_N']:.1f}%)"
        else:
            return "⬜ Neutral"
            
    symbol_stats['Bias'] = symbol_stats.apply(determine_bias_str, axis=1)
    
    # Sorting for Display
    # Sort by Bias Group (+ first, then -), then by Strength%, then by Count
    symbol_stats['Sort_Key'] = symbol_stats['Pct_P']  # High P% = top, Low P% (High N%) = bottom
    symbol_stats = symbol_stats.sort_values(by=['Sort_Key', 'Valid_Patterns'], ascending=[False, False])
    
    # ──────────────────────────────────────────────────
    # Step 8: Final Output & Save
    # ──────────────────────────────────────────────────
    output_df = symbol_stats[[
        'Display_Symbol', 'Market', 'Valid_Patterns', 'Winning_P', 'Winning_N', 'Bias'
    ]].rename(columns={
        'Display_Symbol': 'Symbol',
        'Winning_P': 'Sum_Winning_+',
        'Winning_N': 'Sum_Winning_-'
    })
    
    output_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved Summary to: {OUTPUT_FILE}")
    
    # Display
    markets = sorted(output_df['Market'].unique())
    for m in markets:
        m_df = output_df[output_df['Market'] == m]
        print(f"\n🌍 MARKET: {m} ({len(m_df)} stocks)")
        print("-" * 95)
        print(f"{'Symbol':<15} {'Patterns':<10} {'Sum(+)':<10} {'Sum(-)':<10} {'Bias (Strength)':<20}")
        print("-" * 95)
        for _, row in m_df.iterrows():
            print(f"{row['Symbol']:<15} {row['Valid_Patterns']:<10} {int(row['Sum_Winning_+']):<10} {int(row['Sum_Winning_-']):<10} {row['Bias']:<20}")
    
    print("\n✅ Report Complete.")

if __name__ == "__main__":
    main()
