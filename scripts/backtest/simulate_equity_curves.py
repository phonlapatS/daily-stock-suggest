"""
simulate_equity_curves.py - Monte Carlo Simulation of Market Performance
========================================================================
Purpose: Visualize cumulative profits and determine the risk of hitting zero
based on current Prob (WR) and RRR metrics for each market.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

# Results Directory
RESULTS_DIR = r"C:\Users\manda\.gemini\antigravity\brain\a4ef2fa5-d372-4c88-a413-c56fa035f128"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Latest Market Metrics (Prob, RRR)
# Note: Using conservatively averaged metrics from Trustworthy lists
MARKETS = {
    "🇹🇭 THAI (SET)": {"wr": 0.73, "rrr": 1.45, "color": "blue"},
    "🇺🇸 US (NASDAQ)": {"wr": 0.62, "rrr": 1.37, "color": "green"},
    "🇨🇳 CHINA (HKEX)": {"wr": 0.597, "rrr": 1.59, "color": "red"},  # Xiaomi focus
    "🇹🇼 TAIWAN (TWSE)": {"wr": 0.588, "rrr": 1.26, "color": "orange"} # Advantech focus
}

N_TRADES = 200      # Simulate 200 trading signals
N_SIMULATIONS = 500 # Number of random paths to simulate per market
INITIAL_CAPITAL = 0 # Starting at 0 to see if it goes below baseline

def run_simulation(wr, rrr, n_trades, n_sims):
    paths = []
    for _ in range(n_sims):
        # Generate random win/loss outcomes
        outcomes = np.random.choice([rrr, -1.0], size=n_trades, p=[wr, 1-wr])
        cumulative = np.cumsum(outcomes)
        paths.append(cumulative)
    return np.array(paths)

plt.figure(figsize=(12, 10))

for idx, (market, cfg) in enumerate(MARKETS.items()):
    plt.subplot(2, 2, idx + 1)
    
    paths = run_simulation(cfg['wr'], cfg['rrr'], N_TRADES, N_SIMULATIONS)
    
    # Calculate stats
    mean_path = np.mean(paths, axis=0)
    p95 = np.percentile(paths, 95, axis=0)
    p05 = np.percentile(paths, 5, axis=0)
    
    # Plot individuals (subset for clarity)
    for i in range(15):
        plt.plot(paths[i], color=cfg['color'], alpha=0.1)
        
    # Plot Aggregates
    plt.plot(mean_path, color=cfg['color'], linewidth=2.5, label=f"Average Expectancy")
    plt.fill_between(range(N_TRADES), p05, p95, color=cfg['color'], alpha=0.15, label="90% Confidence Interval")
    
    # Probability of Hitting 0 (Breach) after start
    # We ignore the very first trades. Check if ending balance < 0
    final_balances = paths[:, -1]
    prob_loss = np.mean(final_balances < 0) * 100
    
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.title(f"{market}\nWR: {cfg['wr']*100:.1f}% | RRR: {cfg['rrr']:.2f}\nProb of Loss after 200 trades: {prob_loss:.1f}%", fontsize=11, fontweight='bold')
    plt.xlabel("Number of Trades")
    plt.ylabel("Cumulative Units (Risk Units)")
    plt.legend(loc='upper left', fontsize='small')
    plt.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.suptitle("PredictPlus V4.5: Cumulative Equity Simulation (Monte Carlo)", fontsize=16, fontweight='bold')

plot_path = os.path.join(RESULTS_DIR, "market_equity_simulations.png")
plt.savefig(plot_path, dpi=150)
print(f"✅ Simulation plot saved to: {plot_path}")

# Generate a summary markdown for the metrics
summary_path = os.path.join(RESULTS_DIR, "risk_simulation_report.md")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write("# 🎭 Risk Simulation Report: Probability of Ruin\n\n")
    f.write("Based on Monte Carlo simulation (500 iterations, 200 trades per path).\n\n")
    f.write("| Market | Win Rate | RRR | Risk of Breakeven/Loss | Expectancy (per trade) |\n")
    f.write("|---|---|---|---|---|\n")
    for market, cfg in MARKETS.items():
        exp = (cfg['wr'] * cfg['rrr']) - ((1 - cfg['wr']) * 1.0)
        # Probability simulation logic
        paths = run_simulation(cfg['wr'], cfg['rrr'], N_TRADES, N_SIMULATIONS)
        prob_loss = np.mean(paths[:, -1] < 0) * 100
        f.write(f"| {market} | {cfg['wr']*100:.1f}% | {cfg['rrr']:.2f} | {prob_loss:.1f}% | {exp:+.2f} R |\n")
    
    f.write(f"\n![Equity Simulation Plot](file:///{plot_path.replace(chr(92), '/')})\n")
    f.write("\n> **Note**: Expectancy > 0 means the system is mathematically profitable over the long run. \n")
    f.write("> **Thai Market** has the highest 'cushion' due to extreme win rates (Risk of loss ~0%). \n")
    f.write("> **China Market** (Xiaomi focus) shows very low risk of loss thanks to the high RRR (1.59).")
