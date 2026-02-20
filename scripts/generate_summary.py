#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_summary.py — Stock-Level Summary via N+1 Prediction Voting
====================================================================
อ่าน Master_Pattern_Stats_NewLogic.csv แล้วสร้าง Summary ว่าหุ้นแต่ละตัว
มี "ทิศทางเชิงประวัติศาสตร์" (Historical Directional Bias) เป็น + หรือ -

หลักการ N+1 Voting:
  1. Pattern "+-+" (Length=3) → Base="+-", Outcome="+"
     หมายความว่า: "ถ้าเจอ +- แล้ว วันถัดไป(N+1) ขึ้น(+)"
  
  2. รวม count ของ Outcome + กับ - สำหรับแต่ละ Base Pattern
     ตัวไหน count สูงกว่า = Vote ของ Base นั้น
  
  3. นับ Vote ทั้งหมดต่อหุ้น → สรุปว่า + หรือ - ชนะ

Usage:
  python scripts/generate_summary.py
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
    print("=" * 70)
    print("📊 N+1 PREDICTION VOTING — Stock-Level Summary Generator")
    print("=" * 70)
    
    # ──────────────────────────────────────────────────
    # Step 1: Load Data
    # ──────────────────────────────────────────────────
    if not os.path.exists(MASTER_STATS_FILE):
        print(f"❌ Master stats not found: {MASTER_STATS_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(MASTER_STATS_FILE)
    print(f"\n📂 Loaded: {MASTER_STATS_FILE}")
    print(f"   Total rows: {len(df):,}")
    print(f"   Unique symbols: {df['Symbol'].nunique()}")
    print(f"   Markets: {', '.join(df['Market'].unique())}")
    
    # ──────────────────────────────────────────────────
    # Step 2: Filter valid lengths (Length >= 2)
    # Pattern must have at least 2 chars to extract Base + Outcome
    # e.g., "++" → Base="+", Outcome="+"
    # Single-char patterns like "+" have no predictive base
    # ──────────────────────────────────────────────────
    df_valid = df[df['Length'] >= 2].copy()
    print(f"\n🔍 After filtering Length >= 2: {len(df_valid):,} rows")
    
    # ──────────────────────────────────────────────────
    # Step 3: Extract Base Pattern & Outcome
    # Pattern "+-+" → Base_Pattern = "+-", Outcome = "+"
    # This represents: "After seeing '+-', the N+1 day was '+'"
    # ──────────────────────────────────────────────────
    df_valid['Base_Pattern'] = df_valid['Pattern'].str[:-1]   # ทุกตัวยกเว้นตัวสุดท้าย
    df_valid['Outcome'] = df_valid['Pattern'].str[-1]          # ตัวสุดท้าย (+ or -)
    
    print(f"   Extracted Base_Pattern + Outcome")
    print(f"   Sample: Pattern='{df_valid.iloc[0]['Pattern']}' → Base='{df_valid.iloc[0]['Base_Pattern']}', Outcome='{df_valid.iloc[0]['Outcome']}'")
    
    # ──────────────────────────────────────────────────
    # Step 4: Group and Pivot — Count + vs - outcomes per Base
    # For each (Symbol, Base_Pattern):
    #   P_Count = how many times Outcome was "+"
    #   N_Count = how many times Outcome was "-"
    # ──────────────────────────────────────────────────
    pivot = df_valid.pivot_table(
        index=['Symbol', 'Market', 'Base_Pattern'],
        columns='Outcome',
        values='Count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Ensure both + and - columns exist
    if '+' not in pivot.columns:
        pivot['+'] = 0
    if '-' not in pivot.columns:
        pivot['-'] = 0
    
    pivot = pivot.rename(columns={'+': 'P_Count', '-': 'N_Count'})
    
    # ──────────────────────────────────────────────────
    # Step 5: Apply Strict Threshold (Total_Base_Count >= 30)
    # Only keep Base Patterns with enough data to be statistically meaningful
    # ──────────────────────────────────────────────────
    pivot['Total_Base_Count'] = pivot['P_Count'] + pivot['N_Count']
    
    before_filter = len(pivot)
    pivot_valid = pivot[pivot['Total_Base_Count'] >= MIN_BASE_COUNT].copy()
    after_filter = len(pivot_valid)
    
    print(f"\n📋 Base Patterns before threshold: {before_filter:,}")
    print(f"   After Count >= {MIN_BASE_COUNT} filter: {after_filter:,}")
    print(f"   Dropped: {before_filter - after_filter:,} (insufficient data)")
    
    # ──────────────────────────────────────────────────
    # Step 6: Determine the Base Pattern Winner (Vote)
    # For each Base Pattern:
    #   P_Count > N_Count → vote "+"
    #   N_Count > P_Count → vote "-"
    #   Tied → discard (no clear edge)
    # ──────────────────────────────────────────────────
    def determine_vote(row):
        if row['P_Count'] > row['N_Count']:
            return '+'
        elif row['N_Count'] > row['P_Count']:
            return '-'
        else:
            return None  # Tied → discard
    
    pivot_valid['Vote'] = pivot_valid.apply(determine_vote, axis=1)
    
    # Remove ties
    tied = pivot_valid['Vote'].isna().sum()
    pivot_voted = pivot_valid.dropna(subset=['Vote']).copy()
    
    print(f"\n🗳️  Voting Results:")
    print(f"   Valid votes: {len(pivot_voted):,}")
    print(f"   Tied (discarded): {tied:,}")
    
    # Show some examples
    print(f"\n   --- Sample votes (first 10) ---")
    for _, row in pivot_voted.head(10).iterrows():
        winner = row['Vote']
        p, n = int(row['P_Count']), int(row['N_Count'])
        print(f"   {row['Symbol']:12s} Base='{row['Base_Pattern']:6s}' → +:{p:>4d} vs -:{n:>4d} → Vote: {winner}")
    
    # ──────────────────────────────────────────────────
    # Step 7: Tally Votes per Stock
    # Count how many Base Patterns voted + vs - per Symbol
    # ──────────────────────────────────────────────────
    vote_counts = pivot_voted.groupby(['Symbol', 'Market', 'Vote']).size().unstack(fill_value=0).reset_index()
    
    # Ensure both columns exist
    if '+' not in vote_counts.columns:
        vote_counts['+'] = 0
    if '-' not in vote_counts.columns:
        vote_counts['-'] = 0
    
    vote_counts = vote_counts.rename(columns={'+': 'Predict_P', '-': 'Predict_N'})
    
    # ──────────────────────────────────────────────────
    # Step 8: Calculate Summary Percentages
    # ──────────────────────────────────────────────────
    vote_counts['Total_Valid_Patterns'] = vote_counts['Predict_P'] + vote_counts['Predict_N']
    vote_counts['P_Win_Rate%'] = (vote_counts['Predict_P'] / vote_counts['Total_Valid_Patterns'] * 100).round(1)
    vote_counts['N_Win_Rate%'] = (vote_counts['Predict_N'] / vote_counts['Total_Valid_Patterns'] * 100).round(1)
    
    # ──────────────────────────────────────────────────
    # Step 9: Determine Final Stock Bias & Win Rate
    # ──────────────────────────────────────────────────
    # ──────────────────────────────────────────────────
    # Step 10: Final Data Preparation (Include ALL Stocks)
    # ──────────────────────────────────────────────────
    # Get list of all unique symbols/markets from original DF to ensure no one is left behind
    all_stocks = df[['Symbol', 'Market']].drop_duplicates()
    
    # Merge voting results back to all_stocks
    # Symbols with no valid votes (due to low count or tie) will have NaNs
    final_df = pd.merge(all_stocks, vote_counts, on=['Symbol', 'Market'], how='left')
    
    # Fill NaNs
    final_df['Predict_P'] = final_df['Predict_P'].fillna(0).astype(int)
    final_df['Predict_N'] = final_df['Predict_N'].fillna(0).astype(int)
    final_df['Total_Valid_Patterns'] = final_df['Total_Valid_Patterns'].fillna(0).astype(int)
    
    # Recalculate rates (handle divide by zero)
    final_df['P_Win_Rate%'] = (final_df['Predict_P'] / final_df['Total_Valid_Patterns'] * 100).fillna(0).round(1)
    final_df['N_Win_Rate%'] = (final_df['Predict_N'] / final_df['Total_Valid_Patterns'] * 100).fillna(0).round(1)

    # Function to determine Bias with format "🟩 P (XX%)", "🟥 N (XX%)"
    def determine_bias_final(row):
        total_valid = row['Total_Valid_Patterns']
        if total_valid == 0:
            return "⬜ ." # Insufficient Data
            
        p_rate = row['P_Win_Rate%']
        n_rate = row['N_Win_Rate%']
        
        if p_rate > n_rate:
            return f"🟩 P ({int(round(p_rate))}%)"
        elif n_rate > p_rate:
            return f"🟥 N ({int(round(n_rate))}%)"
        else:
            return f"⬜ = ({int(round(p_rate))}%)"

    final_df['Bias'] = final_df.apply(determine_bias_final, axis=1)

    # Rename for output
    rename_map = {
        'Total_Valid_Patterns': 'Valid Pattern',
        'Predict_P': '+ Pattern',
        'Predict_N': '- Pattern',
    }
    final_df = final_df.rename(columns=rename_map)
    
    # Select Columns
    output_cols = ['Symbol', 'Market', 'Valid Pattern', '+ Pattern', '- Pattern', 'Bias']
    final_df = final_df[output_cols]
    
    # ──────────────────────────────────────────────────
    # Step 10.5: Map Symbols to Readable Names
    # ──────────────────────────────────────────────────
    # Load mapping from config
    try:
        sys.path.append(PROJECT_DIR) # Ensure we can import config from root
        import config
        symbol_map = {}
        for group in config.ASSET_GROUPS.values():
            for asset in group['assets']:
                if 'name' in asset:
                    symbol_map[asset['symbol']] = asset['name']
        
        # Force Symbol to string to match config keys (which are strings like '700')
        final_df['Symbol'] = final_df['Symbol'].astype(str)
        
        # Apply mapping (if not found, keep original)
        final_df['Symbol'] = final_df['Symbol'].map(symbol_map).fillna(final_df['Symbol'])
        print(f"✅ Mapped {len(symbol_map)} symbols to readable names.")
        
    except ImportError:
        print("⚠️ Could not import config.py. Skipping symbol mapping.")
    
    # Save to CSV
    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved summary to: {OUTPUT_FILE}")

    # ──────────────────────────────────────────────────
    # Step 11: Display Tables by Market
    # ──────────────────────────────────────────────────
    markets = sorted(final_df['Market'].unique())
    
    for market in markets:
        market_df = final_df[final_df['Market'] == market].sort_values(by='Symbol')
        
        print(f"\n{'=' * 80}")
        print(f"🌍 MARKET: {market} ({len(market_df)} stocks)")
        print(f"{'=' * 80}")
        print(f"{'Symbol':<12} {'Valid Pattern':<15} {'+ Pattern':<12} {'- Pattern':<12} {'Bias':<15}")
        print("-" * 80)
        
        for _, row in market_df.iterrows():
            print(f"{row['Symbol']:<12} {row['Valid Pattern']:<15} {row['+ Pattern']:<12} {row['- Pattern']:<12} {row['Bias']:<15}")
        
        print("-" * 80)

    print(f"\n✅ Report Generated Successfully.")

if __name__ == '__main__':
    main()
