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
    
    # --- TABLE 1: STRICT MODE (RR > 2.0) ---
    print(f"\n🏆 TABLE 1: STRICT SNIPER MODE (Prob > 60% & RR > 2.0)")
    print("=" * 105)
    print(f"{'Symbol':<10} {'Trades':>8} {'Prob%':>10} {'AvgWin%':>12} {'AvgLoss%':>12} {'RR':>8}   {'Status'}")
    print("-" * 105)
    
    strict_df = summary_df[ (summary_df['Prob%'] > 60) & (summary_df['RR_Ratio'] > 2.0) ]
    for _, row in strict_df.iterrows():
        print(f"{row['Symbol']:<10} {row['Trades']:>8} {row['Prob%']:>9.1f}% {row['Avg_Win%']:>11.2f}% {row['Avg_Loss%']:>11.2f}% {row['RR_Ratio']:>8.2f}   ✅ PASS")
        
    print(f"\n✅ Total Strict Candidates: {len(strict_df)}")
    print("-" * 105)

    # --- TABLE 2: BALANCED MODE (RR > 1.5) ---
    print(f"\n⚖️  TABLE 2: BALANCED MODE (Prob > 60% & RR > 1.5)")
    print("=" * 105)
    print(f"{'Symbol':<10} {'Trades':>8} {'Prob%':>10} {'AvgWin%':>12} {'AvgLoss%':>12} {'RR':>8}   {'Status'}")
    print("-" * 105)
    
    # Exclude those already shown in Strict Mode
    balanced_df = summary_df[ (summary_df['Prob%'] > 60) & (summary_df['RR_Ratio'] > 1.5) ]
    
    for _, row in balanced_df.iterrows():
        # Check if already in strict to mark differenlty or just show all
        is_strict = row['Symbol'] in strict_df['Symbol'].values
        icon = "🏆" if is_strict else "✅"
        print(f"{row['Symbol']:<10} {row['Trades']:>8} {row['Prob%']:>9.1f}% {row['Avg_Win%']:>11.2f}% {row['Avg_Loss%']:>11.2f}% {row['RR_Ratio']:>8.2f}   {icon} PASS")
        
    print(f"\n✅ Total Balanced Candidates: {len(balanced_df)} (Includes Strict)")
    print("-" * 105)
    
    print(f"💾 Full data saved to: {output_path}")


if __name__ == "__main__":
    calculate_metrics()
