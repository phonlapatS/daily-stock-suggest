import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
import numpy as np

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def compare_tables(trade_file='logs/trade_history.csv', output_file='data/table_comparison.png'):
    print(f"📊 Generating TABLE 3 vs TABLE 4 Comparison...")
    
    if not os.path.exists(trade_file):
        print(f"❌ Error: {trade_file} not found.")
        return

    df = pd.read_csv(trade_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # --- Step 1: Classify Symbols into Tables ---
    # We need to calculate metrics per symbol first to know which table they belong to.
    
    def classify_symbol(group):
        total_trades = len(group)
        if total_trades < 30: return None
        
        # Calculate Metrics
        correct_trades = group[group['correct'] == True]
        prob = (len(correct_trades) / total_trades) * 100
        
        # Calculate PnL logic
        group = group.copy()
        group['actual_return'] = pd.to_numeric(group['actual_return'], errors='coerce').fillna(0)
        group['pnl'] = group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        avg_win = group[group['pnl'] > 0]['pnl'].mean() if not group[group['pnl'] > 0].empty else 0
        avg_loss = abs(group[group['pnl'] <= 0]['pnl'].mean()) if not group[group['pnl'] <= 0].empty else 0
        
        if avg_loss > 0:
            rr_ratio = avg_win / avg_loss
        else:
            rr_ratio = 999.0 # Infinite
            
        return pd.Series({
            'Prob%': prob,
            'RR_Ratio': rr_ratio,
            'Avg_Win%': avg_win,
            'Signals': total_trades,
            'Group': group['group'].iloc[0]
        })

    # Groupby Symbol to get metrics
    metrics = df.groupby('symbol').apply(classify_symbol).dropna()
    
    # Define Tables (Using EXACT Same Logic as calculate_metrics.py)
    # Exclude THAI (Focus on Global for this comparison as per user request context)
    # Actually, let's include all non-THAI to be consistent with "Table 3/4" definition.
    
    # Filter 1: Non-Thai
    global_metrics = metrics[~metrics['Group'].str.contains('THAI', na=False)]
    
    # TABLE 3: WINNERS (Prob > 50 | RRR > 1.0 | Avg Win >= 1.0)
    table3_symbols = global_metrics[
        (global_metrics['Prob%'] > 50.0) & 
        (global_metrics['RR_Ratio'] > 1.0) &
        (global_metrics['Avg_Win%'] >= 1.0)
    ].index.tolist()
    
    # TABLE 4: WATCHLIST (Prob > 50 | 0.5 < RRR <= 1.0)
    # Note: Also captures those with Avg Win < 1.0 but RRR > 1.0? 
    # Logic in metircs script: 
    # Table 4: Prob > 50 & 0.5 < RRR <= 1.0
    # What about RRR > 1.0 but Avg Win < 1.0? (e.g. Gold) -> They are currently ORPHANED.
    # Let's stick to the script's strict definition for Table 4.
    table4_symbols = global_metrics[
        (global_metrics['Prob%'] > 50.0) & 
        (global_metrics['RR_Ratio'] > 0.5) & 
        (global_metrics['RR_Ratio'] <= 1.0)
    ].index.tolist()
    
    print(f"🔹 Table 3 Symbols: {len(table3_symbols)} (e.g. {table3_symbols[:3]})")
    print(f"🔸 Table 4 Symbols: {len(table4_symbols)} (e.g. {table4_symbols[:3]})")
    
    # --- Step 2: Build Equity Curves ---
    # We want valid trades only (Prob > 50 context is implied by symbol selection)
    
    # Filter main DF
    t3_trades = df[df['symbol'].isin(table3_symbols)].copy()
    t4_trades = df[df['symbol'].isin(table4_symbols)].copy()
    
    # Sort by date
    t3_trades = t3_trades.sort_values('date')
    t4_trades = t4_trades.sort_values('date')
    
    # Calculate PnL
    t3_trades['pnl'] = t3_trades.apply(lambda row: row['actual_return'] if row['forecast'] == 'UP' else -row['actual_return'], axis=1)
    t4_trades['pnl'] = t4_trades.apply(lambda row: row['actual_return'] if row['forecast'] == 'UP' else -row['actual_return'], axis=1)
    
    # Cumulative Sum (Portfolio Equity)
    # We assume 1 unit bet per trade.
    t3_trades['equity'] = t3_trades['pnl'].cumsum()
    t4_trades['equity'] = t4_trades['pnl'].cumsum()
    
    # --- Step 3: Plotting ---
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot Table 3
    ax.plot(t3_trades['date'], t3_trades['equity'], label=f'Table 3: Global Winners (N={len(table3_symbols)})', 
            color='#2ecc71', linewidth=2)
            
    # Plot Table 4
    ax.plot(t4_trades['date'], t4_trades['equity'], label=f'Table 4: Watchlist/Risk (N={len(table4_symbols)})', 
            color='#e74c3c', linewidth=2)
    
    # Add Annotations
    if not t3_trades.empty:
        final_t3 = t3_trades['equity'].iloc[-1]
        last_date_t3 = t3_trades['date'].iloc[-1]
        ax.annotate(f"Winners: +{final_t3:,.0f}%", xy=(last_date_t3, final_t3), xytext=(10, 0), 
                     textcoords='offset points', color='#2ecc71', fontweight='bold', fontsize=12)
        
    if not t4_trades.empty:
        final_t4 = t4_trades['equity'].iloc[-1]
        last_date_t4 = t4_trades['date'].iloc[-1]
        ax.annotate(f"Watchlist: {final_t4:,.0f}%", xy=(last_date_t4, final_t4), xytext=(10, 0), 
                     textcoords='offset points', color='#e74c3c', fontweight='bold', fontsize=12)

    ax.set_title('Global Strategy Comparison: Winners (RRR>1.0) vs Watchlist (RRR<=1.0)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Cumulative Gross Return (%)', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper left', fontsize=12)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"✅ Saved Comparison Plot to: {output_file}")

if __name__ == "__main__":
    compare_tables()
