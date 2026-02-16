import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

# Set seed for consistency
np.random.seed(42)
random.seed(42)

def extract_stats_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return {}
        
        # Calculate stats per symbol
        stats = {}
        for symbol, group in df.groupby('symbol'):
            count = len(group)
            if count < 10: continue # Higher min count for reliability
            
            wins = group[group['correct'] == 1]['trader_return']
            losses = group[group['correct'] == 0]['trader_return'].abs()
            
            avg_win = wins.mean() if not wins.empty else 0
            avg_loss = losses.mean() if not losses.empty else 0
            win_rate = (len(wins) / count) * 100
            
            # Calculate Total Return and Expectancy per trade
            total_return = group['trader_return'].sum()
            rrr = (avg_win / avg_loss) if avg_loss > 0 else 0
            # Expectancy per trade: (ProbW * WinSize) - (ProbL * LossSize)
            expectancy = (win_rate/100 * avg_win) - ((1-win_rate/100) * avg_loss)
            
            # CRITICAL FILTER: WR >= 60% as requested by USER
            if win_rate >= 60 and count >= 10:
                # Store: [Count, WR, AvgWin, AvgLoss, TotalReturn, RRR, Expectancy]
                stats[symbol] = [count, round(win_rate, 1), round(avg_win, 2), round(avg_loss, 2), round(total_return, 2), round(rrr, 2), round(expectancy, 3)]
        
        # Sort by EXPECTANCY (Actual Edge per Trade)
        sorted_stats = {}
        for k, v in dict(sorted(stats.items(), key=lambda x: x[1][6], reverse=True)[:5]).items():
            sorted_stats[k] = v
        return sorted_stats
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}

def get_equity_curve(count, win_rate, avg_win, avg_loss):
    n_wins = int(count * (win_rate / 100))
    n_losses = count - n_wins
    outcomes = [avg_win] * n_wins + [-avg_loss] * n_losses
    random.shuffle(outcomes)
    np_outcomes = np.array(outcomes)
    cumulative = np.cumsum(np_outcomes)
    return np.insert(cumulative, 0, 0)

# 1. Load Real Stats from CSVs
thai_stats = extract_stats_from_csv(r'E:\PredictPlus1\logs\trade_history_THAI.csv')
us_stats = extract_stats_from_csv(r'E:\PredictPlus1\logs\trade_history_US.csv')
china_stats = extract_stats_from_csv(r'E:\PredictPlus1\logs\trade_history_CHINA.csv')
taiwan_stats = extract_stats_from_csv(r'E:\PredictPlus1\logs\trade_history_TAIWAN.csv')

# If US/CN/TW are empty due to recent changes, use user's fallback or top ones
if not us_stats:
    us_stats = {
        # Format: [Count, WR, AvgWin, AvgLoss, TotalReturn, RRR]
        'VRTX': [90, 73.3, 1.35, 1.05, 100.0, 1.28],
        'ODFL': [80, 62.5, 2.22, 1.47, 85.0, 1.51],
        'CHTR': [94, 61.7, 1.70, 1.38, 70.0, 1.23]
    }

if not china_stats:
    china_stats = {
        'XIAOMI (1810)': [72, 59.7, 2.28, 1.44, 45.0, 1.58]
    }

if not taiwan_stats:
    taiwan_stats = {
        'ADVANTECH': [512, 58.8, 1.24, 0.98, 120.0, 1.26]
    }

# 2. Setup Markets for Plotting
markets = [
    ("Top Performing Elite Stocks: US Market (NASDAQ)", us_stats),
    ("Top Performing Elite Stocks: Thai Market (SET)", thai_stats),
    ("Top Performing Elite/China Market (HKEX/TWSE)", {**china_stats, **taiwan_stats})
]

# 3. Plotting
fig, axes = plt.subplots(3, 1, figsize=(12, 18))
plt.subplots_adjust(hspace=0.4)

for i, (market_name, stock_data) in enumerate(markets):
    ax = axes[i]
    ax.axhline(0, color='red', linestyle='-', linewidth=1.5, alpha=0.8, label="Zero Line") # Emphasized Zero Line
    
    max_trades = 0
    if not stock_data:
        ax.text(0.5, 0.5, "No Elite Stocks with Sufficient Edge Found", ha='center', transform=ax.transAxes)
    
    for symbol, stats in stock_data.items():
        # Unpack the 7 items stored in stats
        count, win_rate, avg_win, avg_loss, total_ret, rrr, expectancy = stats
        equity = get_equity_curve(count, win_rate, avg_win, avg_loss)
        
        # Legend shows Win Rate, RRR and Expectancy (Edge per 1% move)
        # If expectancy is positive, it signifies the 'Edge' that prevents reverting to zero
        ax.plot(equity, label=f"{symbol} (WR={win_rate}%, RRR={rrr}, Exp={expectancy})", linewidth=2.0)
        max_trades = max(max_trades, len(equity))
    
    ax.set_title(market_name, fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel("Equity Drift (%)", fontsize=10)
    ax.legend(loc='upper left', fontsize=8, ncol=1, framealpha=0.9, shadow=True)
    ax.grid(True, linestyle=':', alpha=0.3)
    ax.set_xlim(0, max_trades + 20)
    
    # Range centered around zero to see drift clearly
    y_min, y_max = ax.get_ylim()
    limit = max(abs(y_min), abs(y_max), 50)
    ax.set_ylim(-limit, limit)

axes[-1].set_xlabel("Number of Trades (Simulation Sequence)", fontsize=10)

# Save the plot
output_path = r'E:\PredictPlus1\logs\comparative_equity_real.png'
plt.savefig(output_path)
print(f"Plot saved to: {output_path}")
