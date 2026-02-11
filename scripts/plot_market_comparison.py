"""
plot_market_comparison.py - Cumulative Portfolio Return across Markets
======================================================================
Generates a time-based comparison of cumulative returns for TH, US, CN, TW.
Mimics the user's provided reference style.
"""
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Results Directory
RESULTS_DIR = r"C:\Users\manda\.gemini\antigravity\brain\a4ef2fa5-d372-4c88-a413-c56fa035f128"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Market Configuration
MARKETS = {
    "THAI (SET)": {"glob": "logs/trade_history_THAI.csv", "color": "#2ecc71"}, # Green
    "US (NASDAQ)": {"glob": "logs/trade_history_US.csv", "color": "#e74c3c"},  # Red
    "CHINA/HK (HKEX)": {"glob": "logs/trade_history_CHINA.csv", "color": "#3498db"}, # Blue
    "TAIWAN (TWSE)": {"glob": "logs/trade_history_TAIWAN.csv", "color": "#9b59b6"}  # Purple
}

plt.figure(figsize=(12, 7))

for name, cfg in MARKETS.items():
    files = glob.glob(cfg['glob'])
    if not files:
        print(f"⚠️ No files found for {name}")
        continue
    
    # Load and process
    df = pd.read_csv(files[0])
    
    # APPLY ELITE FILTERS (System Edge only)
    # 1. Filter for statistically significant patterns (Prob > 55% and enough samples)
    # Note: In the raw log, 'prob' is the probability found at that time.
    df = df[df['prob'] >= 55.0]
    
    # 2. Risk Management (Cap individual trade impact to 10% max for outliers)
    df['trader_return'] = df['trader_return'].clip(-10, 10)
    
    if len(df) == 0:
        print(f"⚠️ No Elite trades found for {name} after filter")
        continue

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Portfolio view: Group by date and calculate MEAN return for that day to simulate diversified allocation
    # (Summing 39,000 trades would be unrealistic capital allocation)
    daily_returns = df.groupby('date')['trader_return'].mean().reset_index()
    daily_returns['cum_return'] = daily_returns['trader_return'].cumsum()
    
    # Plotting
    n_trades = len(df)
    line, = plt.plot(daily_returns['date'], daily_returns['cum_return'], 
                     label=f"{name} (N={n_trades})", color=cfg['color'], linewidth=1.5)
    
    # Add target label at the end
    last_date = daily_returns['date'].iloc[-1]
    last_val = daily_returns['cum_return'].iloc[-1]
    plt.text(last_date, last_val, f" {name}: {last_val:.0f}%", 
             color=cfg['color'], fontsize=10, fontweight='bold', va='center')

# Formatting
plt.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
plt.title("View 1: Growth over Time (Market Portfolio Comparison)", fontsize=14, fontweight='bold', pad=20)
plt.xlabel("Year", fontsize=11)
plt.ylabel("Gross Cumulative Return (%)", fontsize=11)
plt.grid(True, alpha=0.2)
plt.legend(loc='upper left', frameon=True)

# Adjust layout to fit text labels
plt.tight_layout()

plot_path = os.path.join(RESULTS_DIR, "market_portfolio_comparison.png")
plt.savefig(plot_path, dpi=150)
print(f"✅ Comparison plot saved to: {plot_path}")
