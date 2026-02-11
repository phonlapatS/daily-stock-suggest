
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np

def visualize_equity(trade_file='logs/trade_history.csv', output_file='data/equity_curve_markets.png'):
    print(f"📊 Generating EQUITY CURVES by Market Representatives...")
    
    if not os.path.exists(trade_file):
        print(f"❌ Error: {trade_file} not found.")
        return

    df = pd.read_csv(trade_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Target Assets (1 representative per market)
    targets = [
        {'symbol': 'TPIPP',  'label': 'TH: TPIPP (Thai Alpha)'}, 
        {'symbol': 'GOOGL',  'label': 'US: GOOGL (US Winner)'},
        {'symbol': 'BABA',   'label': 'CN: BABA (China ADR)'},
        {'symbol': '2330',   'label': 'TW: TSMC (Taiwan)'},   # 2330.TWSE in cache
        {'symbol': 'XAUUSD', 'label': 'GL: XAUUSD (Gold)'}
    ]
    
    # Create 3 Subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 16))
    
    # Soft Colors for readability (one per market)
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f1c40f'] 
    
    for i, target in enumerate(targets):
        symbol = target['symbol']
        label = target['label']
        
        trades = df[df['symbol'] == symbol].copy()
        
        if trades.empty:
            continue
            
        trades = trades.sort_values('date')
        
        # Gross PnL Logic
        trades['pnl'] = trades.apply(
            lambda row: row['actual_return'] if row['forecast'] == 'UP' else -row['actual_return'], 
            axis=1
        )
        trades['equity'] = trades['pnl'].cumsum()
        
        trade_count = len(trades)
        final_ret = trades['equity'].iloc[-1]
        last_date = trades['date'].iloc[-1]
        
        # STANDARD LINE STYLE (All Equal, Normal Width)
        line_width = 1.5 
        alpha_val = 1.0

        # --- PLOT 1: Time-Based ---
        ax1.plot(trades['date'], trades['equity'], label=f"{symbol} (N={trade_count})", 
                 linewidth=line_width, color=colors[i], alpha=alpha_val)
        
        ax1.annotate(f"{symbol}: {final_ret:.0f}%", xy=(last_date, final_ret), xytext=(10, 0), 
                     textcoords='offset points', color=colors[i], fontweight='bold', fontsize=10)

        # --- PLOT 2: Full Trade-Based ---
        ax2.plot(range(len(trades)), trades['equity'], label=f"{label}", 
                 linewidth=line_width, color=colors[i], alpha=alpha_val)

        # --- PLOT 3: Zoomed Trade-Based (0-300) ---
        ax3.plot(range(len(trades)), trades['equity'], label=f"{label}", 
                 linewidth=line_width, color=colors[i], alpha=alpha_val)

    # Format Plot 1
    ax1.set_title('View 1: Growth over 10 Years (Time-Based)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Gross Cumulative Return (%)', fontsize=12)
    ax1.axhline(0, color='black', linewidth=1, linestyle='--')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.xaxis.set_major_locator(mdates.YearLocator(1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Format Plot 2 (Full)
    ax2.set_title('View 2: Statistical Edge Comparison (Full Trade History)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Gross Cumulative Return (%)', fontsize=12)
    ax2.set_xlabel('Trade Count (All Trades)', fontsize=12)
    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', fontsize=10)

    # Format Plot 3 (Zoomed)
    ax3.set_title('View 3: Detailed Accuracy Check (Zoomed to First 200 Trades)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Gross Cumulative Return (%)', fontsize=12)
    ax3.set_xlabel('Trade Count (0-200)', fontsize=12)
    ax3.axhline(0, color='black', linewidth=1, linestyle='--')
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.legend(loc='upper left', fontsize=10)
    
    # ZOOM LIMIT: Changed to 200 per user request
    ax3.set_xlim(0, 200)
    
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"✅ Saved Standard Normal-Line Plot to: {output_file}")

if __name__ == "__main__":
    visualize_equity()
