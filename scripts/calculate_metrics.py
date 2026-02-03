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
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Input file not found: {input_path}")
        print("   Please run 'python scripts/backtest.py --all' first.")
        return

    # Load trade logs
    df = pd.read_csv(input_path)
    
    if df.empty:
        print("❌ Error: Trade logs are empty.")
        return

    print(f"   Loaded {len(df)} trades.")

    # Group by Symbol
    results = []
    
    for symbol, group in df.groupby('symbol'):
        total_trades = len(group)
        
        # Win Rate (Pop)
        wins = group[group['correct'] == 1]
        losses = group[group['correct'] == 0]
        
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
        group['pnl'] = group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        real_wins = group[group['pnl'] > 0]
        real_losses = group[group['pnl'] <= 0]
        
        avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
        avg_loss = abs(real_losses['pnl'].mean()) if not real_losses.empty else 0 # Convert to positive for ratio
        
        # RR Ratio
        if avg_loss > 0:
            rr_ratio = avg_win / avg_loss
        else:
            rr_ratio = 999.0 if avg_win > 0 else 0.0
            
        # Filter Status
        is_pass = (pop > 60) and (rr_ratio > 2)
        status = "✅ PASS" if is_pass else "❌ Fail"
        
        results.append({
            'Symbol': symbol,
            'Group': group['group'].iloc[0],
            'Trades': total_trades,
            'Pop%': round(pop, 1),
            'Avg_Win%': round(avg_win, 2),
            'Avg_Loss%': round(avg_loss, 2),
            'RR_Ratio': round(rr_ratio, 2),
            'Status': status,
            '_is_pass': is_pass
        })
        
    # Create DataFrame
    summary_df = pd.DataFrame(results)
    
    # Sort by Passing first, then RR Ratio desc
    summary_df = summary_df.sort_values(by=['_is_pass', 'RR_Ratio'], ascending=[False, False])
    
    # Save Report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.drop(columns=['_is_pass']).to_csv(output_path, index=False)
    
    # Display Report
    print(f"\n📈 SYMBOL PERFORMANCE SUMMARY (Pop > 60% & RR > 2)")
    print("=" * 95)
    print(f"{'Symbol':<10} {'Trades':<8} {'Pop%':<8} {'AvgWin%':<10} {'AvgLoss%':<10} {'RR':<8} {'Status'}")
    print("-" * 95)
    
    for _, row in summary_df.head(20).iterrows():
        print(f"{row['Symbol']:<10} {row['Trades']:<8} {row['Pop%']:<8} {row['Avg_Win%']:<10} {row['Avg_Loss%']:<10} {row['RR_Ratio']:<8} {row['Status']}")
        
    print("-" * 95)
    
    pass_count = summary_df['_is_pass'].sum()
    print(f"✅ Qualifying Symbols: {pass_count} / {len(summary_df)}")
    print(f"💾 Report saved to: {output_path}")


if __name__ == "__main__":
    calculate_metrics()
