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

def get_country_code(group_name):
    if not isinstance(group_name, str): return 'GL'
    if 'THAI' in group_name: return 'TH'
    if 'US' in group_name: return 'US'
    if 'CHINA' in group_name: return 'CN'
    if 'HK' in group_name: return 'HK'
    if 'TAIWAN' in group_name: return 'TW'
    return 'GL'

# ==============================================================================
# Helper Function: Print Standardized Table
# ==============================================================================
def print_table(df, title, icon="✅"):
    """
    Prints a formatted table of stock performance metrics.
    """
    print(f"\n{title}")
    print("=" * 110)
    print(f"{'Symbol':<15} {'Ctry':<4} {'Signals':>8} {'Prob%':>10} {'AvgWin%':>12} {'AvgLoss%':>12} {'RR':>8}   {'Status'}")
    print("-" * 110)
    
    if df.empty:
        print(f"{'No candidates found matching criteria.':^110}")
    else:
        for _, row in df.iterrows():
            # Resolve display name
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            country = row['Country'] if 'Country' in row else 'GL'
            
            # Use lowercase 'symbol' because it comes from reset_index() on groupby key
            print(f"{display_name:<15} {country:<4} {row['Signals']:>8} {row['Prob%']:>9.1f}% {row['Avg_Win%']:>11.2f}% {row['Avg_Loss%']:>11.2f}% {row['RR_Ratio']:>8.2f}   {icon} PASS")
        
    print("-" * 110)
    print(f"Count: {len(df)}")


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
        
        group_name = group['group'].iloc[0] if 'group' in group.columns else 'N/A'
        
        return pd.Series({
            'Group': group_name,
            'Country': get_country_code(str(group_name)),
            'Signals': total_trades,
            'Prob%': round(pop, 1),
            'Avg_Win%': round(avg_win, 2),
            'Avg_Loss%': round(avg_loss, 2),
            'RR_Ratio': round(rr_ratio, 2),
            'Status': status
        })

    # --- Step 2: Aggregation ---
    # Group by Symbol + Group to preserve metadata
    # Use include_groups=False or explicit selection to avoid FutureWarning
    summary_df = df.groupby(['symbol', 'group']).apply(calculate_symbol_metrics).reset_index()
    
    if summary_df.empty:
        print("⚠️ No valid symbols found (min 10 trades).")
        return

    # Sort for better readability (High Prob, High RR first)
    summary_df = summary_df.sort_values(by=['Prob%', 'RR_Ratio'], ascending=[False, False])
    
    # Save raw data for further analysis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False)

    # --- REPORT GENERATION ---
    print(f"\n📊 METRICS REPORT")
    print("=" * 110)

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
    
    print_table(inter_df, "🌍 TABLE 3: INTERNATIONAL OBSERVATION (Prob > 55% | RR > 1.1)", icon="✅")

    # TABLE 4: INTERNATIONAL SENSITIVITY (Deep Dive)
    # Criteria: Prob > 50% (Lower for deep dive) AND 0.5 < RR <= 1.1
    inter_low_df = summary_df[
        (~summary_df['Group'].str.contains('THAI', na=False)) & 
        (summary_df['Prob%'] > 50.0) & 
        (summary_df['RR_Ratio'] > 0.5) &
        (summary_df['RR_Ratio'] <= 1.1)
    ].sort_values(by=['RR_Ratio', 'Prob%'], ascending=[False, False])
    
    print_table(inter_low_df, "📉 TABLE 4: INTERNATIONAL SENSITIVITY (Prob > 50% | 0.5 < RR <= 1.1)", icon="✅")

    print(f"\n💾 Detailed report saved to: {output_path}")

if __name__ == "__main__":
    calculate_metrics()
