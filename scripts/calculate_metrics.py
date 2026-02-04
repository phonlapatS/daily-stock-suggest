#!/usr/bin/env python
"""
calculate_metrics.py - Symbol Performance Metrics (Pop & RR)
============================================================
Processes trade logs from 'logs/trade_history.csv' to calculate
statistical metrics favored by professional quants:
- Pop (Win Rate)
- Avg Win / Avg Loss
- Risk-Reward Ratio (RR)

Target: Identify symbols with Pop > 60% AND RR > 2
"""

import pandas as pd
import numpy as np
import os
import sys

def calculate_metrics(input_path='logs/trade_history.csv', output_path='data/symbol_performance.csv'):
    print(f"\n📊 Calculates Metrics from: {input_path}")
    
    # Resolve absolute path for robustness
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(input_path):
        input_path = os.path.join(base_dir, input_path)
    if not os.path.isabs(output_path):
        output_path = os.path.join(base_dir, output_path)

    if not os.path.exists(input_path):
        print(f"❌ Error: Input file not found: {input_path}")
        print("   Please run 'python scripts/backtest.py --all' (or --quick) first.")
        return

    # Load trade logs
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    if df.empty:
        print("❌ Error: Trade logs are empty.")
        return

    print(f"   Loaded {len(df)} trades.")

    # Group by Symbol
    results = []
    
    for symbol, group in df.groupby('symbol'):
        total_trades = len(group)
        if total_trades == 0: continue
        
        # Win Rate (Pop)
        wins = group[group['correct'] == 1]
        pop = (len(wins) / total_trades) * 100
        
        # Avg Win (Positive returns)
        # Note: We use actual_return column (which is % change next day)
        # Assuming direction match logic is handled in 'correct' column, 
        # but for RR we care about magnitude.
        # Logic: If correct=1, return is positive profit. If correct=0, return is negative loss.
        # But wait! 'actual_return' is the RAW price change % of next day.
        # If we short (DOWN forecast) and price drops (-2%), that's a WIN of +2%.
        # If we short (DOWN forecast) and price rises (+2%), that's a LOSS of -2%.
        
        # Let's refine the PnL logic based on Forecast:
        # PnL = actual_return * (1 if Forecast='UP' else -1)
        
        group = group.copy()
        # Ensure actual_return is numeric
        group['actual_return'] = pd.to_numeric(group['actual_return'], errors='coerce').fillna(0)
        
        group['pnl'] = group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        real_wins = group[group['pnl'] > 0]
        real_losses = group[group['pnl'] <= 0]
        
        # Calculate Avg Win / Avg Loss magnitude
        avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
        avg_loss = abs(real_losses['pnl'].mean()) if not real_losses.empty else 0 # Convert to positive for ratio
        
        # RR Ratio
        if avg_loss > 0:
            rr_ratio = avg_win / avg_loss
        else:
            rr_ratio = 999.0 if avg_win > 0 else 0.0
            
        # Filter Status (Mentor's Criteria)
        is_pass = (pop > 60) and (rr_ratio > 2)
        status = "✅ PASS" if is_pass else "❌ Fail"
        
        results.append({
            'Symbol': symbol,
            'Group': group['group'].iloc[0] if 'group' in group.columns else 'N/A',
            'Trades': total_trades,
            'Prob%': round(pop, 1),
            'Avg_Win%': round(avg_win, 2),
            'Avg_Loss%': round(avg_loss, 2),
            'RR_Ratio': round(rr_ratio, 2),
            'Status': status,
            '_is_pass': is_pass
        })
        
    # Create DataFrame
    summary_df = pd.DataFrame(results)
    
    if summary_df.empty:
        print("⚠️ No symbols processed.")
        return

    # Sort by Prob% desc for better viewing
    summary_df = summary_df.sort_values(by=['Prob%', 'RR_Ratio'], ascending=[False, False])
    
    # Save Full Report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.drop(columns=['_is_pass']).to_csv(output_path, index=False)
    
# Resolve path for config import
import sys
import os
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

# ==============================================================================
# Helper Function: Print Standardized Table
# ==============================================================================
def print_table(df, title, icon="✅"):
    """
    Prints a formatted table of stock performance metrics.
    
    Args:
        df (pd.DataFrame): The filtered dataframe to display.
        title (str): The header title for the table.
        icon (str): Emoji icon to display in the Status column.
    """
    print(f"\n{title}")
    print("=" * 105)
    print(f"{'Symbol':<15} {'Signals':>8} {'Prob%':>10} {'AvgWin%':>12} {'AvgLoss%':>12} {'RR':>8}   {'Status'}")
    print("-" * 105)
    
    if df.empty:
        print(f"{'No candidates found matching criteria.':^105}")
    else:
        for _, row in df.iterrows():
            # Resolve display name
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            
            # Use lowercase 'symbol' because it comes from reset_index() on groupby key
            print(f"{display_name:<15} {row['Signals']:>8} {row['Prob%']:>9.1f}% {row['Avg_Win%']:>11.2f}% {row['Avg_Loss%']:>11.2f}% {row['RR_Ratio']:>8.2f}   {icon} PASS")
        
    print("-" * 105)
    print(f"Count: {len(df)}")


def calculate_metrics(input_path='logs/trade_history.csv', output_path='data/symbol_performance.csv'):
    """
    Main function to audit trade logs and generate performance reports.
    
    Process:
    1. Load 'trade_history.csv' (generated by backtest.py).
    2. Group by Symbol to calculate aggregated metrics:
       - Prob% (Win Rate): % of trades where forecast matches actual direction.
       - Avg Win/Loss: Magnitude of returns.
       - RR Ratio: Reward-to-Risk ratio based on actual PnL.
    3. Output 3 distinct tables:
       - Strict Mode: The 'Elite' (Prob > 60, RR > 2).
       - Balanced Mode: The 'Candidates' (Prob > 60, RR > 1.5).
       - Global Watchlist: For non-Thai stocks (Prob > 55).
    """
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return

    print(f"\n📊 Calculating Metrics from: {input_path}")
    
    try:
        df = pd.read_csv(input_path)
        print(f"   Loaded {len(df)} trades.")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return

    # --- Step 1: Metrics Calculation Logic ---
    def calculate_symbol_metrics(group):
        total_trades = len(group)
        if total_trades < 10: return None  # Skip if too few samples
        
        # 1. Probability (Win Rate)
        # Definition: Correct Prediction / Total Trades
        correct_trades = group[group['correct'] == True]
        pop = (len(correct_trades) / total_trades) * 100
        
        # 2. Real PnL (Risk/Reward)
        # We assume:
        # - Long (UP): PnL = Actual Return
        # - Short (DOWN): PnL = -1 * Actual Return
        group = group.copy()
        group['actual_return'] = pd.to_numeric(group['actual_return'], errors='coerce').fillna(0)
        group['pnl'] = group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        real_wins = group[group['pnl'] > 0]
        real_losses = group[group['pnl'] <= 0]
        
        avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
        avg_loss = abs(real_losses['pnl'].mean()) if not real_losses.empty else 0
        
        # 3. RR Ratio Calculation
        if avg_loss > 0:
            rr_ratio = avg_win / avg_loss
        else:
            rr_ratio = 999.0 if avg_win > 0 else 0.0
            
        # 4. Preliminary Classification (Strict)
        is_pass = (pop > 60) and (rr_ratio > 2.0)
        status = "PASS" if is_pass else "FAIL"
        
        return pd.Series({
            'Group': group['group'].iloc[0] if 'group' in group.columns else 'N/A',
            'Signals': total_trades,
            'Prob%': round(pop, 1),
            'Avg_Win%': round(avg_win, 2),
            'Avg_Loss%': round(avg_loss, 2),
            'RR_Ratio': round(rr_ratio, 2),
            'Status': status
        })

    # --- Step 2: Aggregation ---
    # Group by Symbol + Group to preserve metadata
    summary_df = df.groupby(['symbol', 'group']).apply(calculate_symbol_metrics).reset_index()
    
    if summary_df.empty:
        print("⚠️ No valid symbols found (min 10 trades).")
        return

    # Flatten the multi-index columns if necessary (though reset_index handles it mostly)
    # The 'apply' returns a dataframe with columns from the Series keys.
    
    # Sort for better readability (High Prob, High RR first)
    summary_df = summary_df.sort_values(by=['Prob%', 'RR_Ratio'], ascending=[False, False])
    
    # Save raw data for further analysis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False)

    # --- Step 3: Reporting (Consolidated Master Table) ---
    
    # Define Criteria Masks
    mask_strict = (summary_df['Prob%'] > 60.0) & (summary_df['RR_Ratio'] > 2.0)
    mask_balanced = (summary_df['Prob%'] > 60.0) & (summary_df['RR_Ratio'] > 1.5)
    mask_global = (~summary_df['Group'].str.contains('THAI', na=False)) & (summary_df['Prob%'] > 55.0) & (summary_df['RR_Ratio'] > 1.3)
    
    # Create copies to avoid SettingWithCopy warnings
    strict_df = summary_df[mask_strict].copy()
    strict_df['Criteria'] = 'Strict'
    
    balanced_df = summary_df[mask_balanced & ~mask_strict].copy() # Exclude strict to avoid dupes in logic, but user wants inclusive?
    # Actually, let's just label them based on highest tier passed.
    
    # Better approach: Iterate and assign 'Tier'
    # strict_df is subset of balanced_df usually.
    
    master_results = []
    
    # --- REPORT GENERATION ---
    print(f"\n📊 METRICS REPORT")
    print("=" * 105)

    # --- REPORT GENERATION ---
    print(f"\n📊 METRICS REPORT")
    print("=" * 105)

    # TABLE 1: THAI MARKET - STRICT (Elite)
    # Criteria: Prob > 60% AND RR > 2.0
    thai_strict = summary_df[
        (summary_df['Group'].str.contains('THAI', na=False)) & 
        (summary_df['Prob%'] > 60.0) & 
        (summary_df['RR_Ratio'] > 2.0)
    ].sort_values(by=['RR_Ratio', 'Prob%'], ascending=[False, False])
    
    print_table(thai_strict, "💎 TABLE 1: THAI STRICT (Prob > 60% | RR > 2.0)", icon="✅")

    # TABLE 2: THAI MARKET - BALANCED (Candidates)
    # Criteria: Prob > 60% AND 1.5 < RR <= 2.0 (Exclusive of Strict)
    thai_balanced = summary_df[
        (summary_df['Group'].str.contains('THAI', na=False)) & 
        (summary_df['Prob%'] > 60.0) & 
        (summary_df['RR_Ratio'] > 1.5) &
        (summary_df['RR_Ratio'] <= 2.0)
    ].sort_values(by=['RR_Ratio', 'Prob%'], ascending=[False, False])
    
    print_table(thai_balanced, "🇹🇭 TABLE 2: THAI BALANCED (Prob > 60% | 1.5 < RR <= 2.0)", icon="✅")

    # TABLE 3: INTERNATIONAL MARKET (Observation)
    # Criteria: Prob > 55% AND RR > 1.1 
    inter_df = summary_df[
        (~summary_df['Group'].str.contains('THAI', na=False)) & 
        (summary_df['Prob%'] > 55.0) & 
        (summary_df['RR_Ratio'] > 1.1)
    ].sort_values(by=['RR_Ratio', 'Prob%'], ascending=[False, False])
    
    # User requested no warning icon for Table 3
    print_table(inter_df, "🌍 TABLE 3: INTERNATIONAL OBSERVATION (Prob > 55% | RR > 1.1)", icon="✅")

    print(f"\n💾 Detailed report saved to: {output_path}")

if __name__ == "__main__":
    calculate_metrics()
