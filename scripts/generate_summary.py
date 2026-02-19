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
    # Step 9: Determine Final Stock Bias
    # ──────────────────────────────────────────────────
    def determine_bias(row):
        if row['P_Win_Rate%'] > row['N_Win_Rate%']:
            return f"+ ({row['P_Win_Rate%']:.1f}%)"
        elif row['N_Win_Rate%'] > row['P_Win_Rate%']:
            return f"- ({row['N_Win_Rate%']:.1f}%)"
        else:
            return "Neutral (50.0%)"
    
    vote_counts['Summary_Result'] = vote_counts.apply(determine_bias, axis=1)
    
    # ──────────────────────────────────────────────────
    # Step 10: Export
    # ──────────────────────────────────────────────────
    output_cols = ['Symbol', 'Market', 'Total_Valid_Patterns', 'Predict_P', 'Predict_N',
                   'P_Win_Rate%', 'N_Win_Rate%', 'Summary_Result']
    
    result = vote_counts[output_cols].sort_values(['Market', 'Symbol']).reset_index(drop=True)
    result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    # ──────────────────────────────────────────────────
    # Display Results
    # ──────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"📊 STOCK PREDICTION HISTORY SUMMARY")
    print(f"{'=' * 70}")
    
    # Print by market
    for market in sorted(result['Market'].unique()):
        market_df = result[result['Market'] == market]
        
        # Count bias direction
        pos_bias = market_df['Summary_Result'].str.startswith('+').sum()
        neg_bias = market_df['Summary_Result'].str.startswith('-').sum()
        neutral = market_df['Summary_Result'].str.startswith('Neutral').sum()
        
        print(f"\n{'─' * 60}")
        print(f"🏷️  {market} ({len(market_df)} stocks) | +Bias:{pos_bias} | -Bias:{neg_bias} | Neutral:{neutral}")
        print(f"{'─' * 60}")
        print(f"  {'Symbol':12s} {'Patterns':>8s} {'Pred_+':>8s} {'Pred_-':>8s} {'+ Rate':>8s} {'- Rate':>8s}  {'Bias'}")
        print(f"  {'─' * 65}")
        
        for _, row in market_df.iterrows():
            print(f"  {row['Symbol']:12s} {row['Total_Valid_Patterns']:>8d} {row['Predict_P']:>8d} {row['Predict_N']:>8d} "
                  f"{row['P_Win_Rate%']:>7.1f}% {row['N_Win_Rate%']:>7.1f}%  {row['Summary_Result']}")
    
    # Overall summary
    total_pos = result['Summary_Result'].str.startswith('+').sum()
    total_neg = result['Summary_Result'].str.startswith('-').sum()
    total_neutral = result['Summary_Result'].str.startswith('Neutral').sum()
    
    print(f"\n{'=' * 70}")
    print(f"📈 OVERALL: {len(result)} stocks analyzed")
    print(f"   + Bias: {total_pos} stocks")
    print(f"   - Bias: {total_neg} stocks")
    print(f"   Neutral: {total_neutral} stocks")
    print(f"\n   💾 Saved: {OUTPUT_FILE}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
