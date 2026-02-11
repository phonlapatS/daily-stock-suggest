"""
plot_stock_comparison_detailed.py - Detailed Stock-by-Stock Comparison
======================================================================
Generates a two-view comparison (Time-Based and Trade-Count Based)
for representative stocks from each market.
"""
import pandas as pd
import matplotlib.pyplot as plt
import os

# Results Directory
RESULTS_DIR = r"C:\Users\manda\.gemini\antigravity\brain\a4ef2fa5-d372-4c88-a413-c56fa035f128"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Selection: [Market Name, File Path, Symbol Filter, Label, Color]
STOCKS = [
    ["THAI (SET)", "logs/trade_history_THAI.csv", "SUPER", "SUPER (Alpha | TH)", "#2ecc71"],
    ["US (NASDAQ)", "logs/trade_history_US.csv", "VRTX", "VRTX (Stable | US)", "#e74c3c"],
    ["CHINA (HKEX)", "logs/trade_history_CHINA.csv", "1810", "XIAOMI (Mean Rev | CN)", "#3498db"],
    ["TAIWAN (TWSE)", "logs/trade_history_TAIWAN.csv", "2395", "ADVANTECH (Growth | TW)", "#9b59b6"]
]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

for market, file_path, symbol, label, color in STOCKS:
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        continue
        
    df = pd.read_csv(file_path)
    
    # Filter for the specific symbol (Ticker)
    # Ensure symbol is compared as string
    subset = df[df['symbol'].astype(str) == str(symbol)].copy()
    
    # Filter for signals with edge (Prob >= 50.0)
    subset = subset[subset['prob'] >= 50.0]
    
    if len(subset) == 0:
        print(f"⚠️ No representative data for {symbol} ({label}) in {market}")
        continue
        
    subset['date'] = pd.to_datetime(subset['date'])
    subset = subset.sort_values('date')
    
    # Cumulative Sum
    subset['cum_return'] = subset['trader_return'].cumsum()
    
    # View 1: Time-Based
    ax1.plot(subset['date'], subset['cum_return'], label=f"{label} (N={len(subset)})", color=color, linewidth=1.8)
    # Add annotation at end for View 1
    ax1.text(subset['date'].iloc[-1], subset['cum_return'].iloc[-1], f" {subset['cum_return'].iloc[-1]:.0f}%", 
             color=color, fontsize=10, fontweight='bold', va='center')
    
    # View 2: Statistical Edge (Trade Count)
    subset_reset = subset.reset_index(drop=True)
    ax2.plot(subset_reset.index, subset_reset['cum_return'], label=f"{label}", color=color, linewidth=1.8)
    # Add annotation at end for View 2
    ax2.text(subset_reset.index[-1], subset_reset['cum_return'].iloc[-1], f" {subset_reset['cum_return'].iloc[-1]:.0f}%", 
             color=color, fontsize=10, fontweight='bold', va='center')

# View 1 Formatting
ax1.set_title("View 1: Growth over 10 Years (Time-Based)", fontsize=12, fontweight='bold')
ax1.set_ylabel("Gross Cumulative Return (%)")
ax1.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax1.grid(True, alpha=0.2)
ax1.legend(loc='upper left', fontsize='small')

# View 2 Formatting
ax2.set_title("View 2: Statistical Edge Comparison (Full Trade History)", fontsize=12, fontweight='bold')
ax2.set_ylabel("Gross Cumulative Return (%)")
ax2.set_xlabel("Trade Count (Selected Elite Trades)")
ax2.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax2.grid(True, alpha=0.2)
ax2.legend(loc='upper left', fontsize='small')

plt.tight_layout()

# Save locally and to project data
plot_name = "stock_comparison_detailed.png"
plot_path_artifact = os.path.join(RESULTS_DIR, plot_name)
plot_path_data = os.path.join("data", plot_name)

plt.savefig(plot_path_artifact, dpi=150)
plt.savefig(plot_path_data, dpi=150)

print(f"✅ Comparison plot saved to: {plot_path_artifact}")
print(f"✅ Comparison plot saved to: {plot_path_data}")
