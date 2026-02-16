python scripts/plot_equity_curves.py"""
ตรวจสอบว่าทำไม Taiwan equity เติบโตเยอะมาก แม้ว่า Prob% และ RRR จะต่ำ
"""
import pandas as pd
import numpy as np

# Load Taiwan trades
df = pd.read_csv('logs/trade_history_TAIWAN.csv')
print(f"📊 Taiwan Total Trades: {len(df)}")
print(f"📅 Date Range: {df['date'].min()} to {df['date'].max()}\n")

# Calculate pnl (same as calculate_metrics.py)
df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

# Statistics
wins = df[df['pnl'] > 0]
losses = df[df['pnl'] <= 0]
print(f"✅ Wins: {len(wins)} ({len(wins)/len(df)*100:.1f}%)")
print(f"❌ Losses: {len(losses)} ({len(losses)/len(df)*100:.1f}%)")
print(f"📈 AvgWin%: {wins['pnl'].mean():.2f}%")
print(f"📉 AvgLoss%: {abs(losses['pnl'].mean()):.2f}%")
print(f"⚖️ RRR: {wins['pnl'].mean() / abs(losses['pnl'].mean()) if len(losses) > 0 else 0:.2f}\n")

# Calculate expected equity (fixed position size, no compound)
RISK_PER_TRADE = 0.02  # 2% of initial capital
initial_capital = 1000
total_pnl_pct = df['pnl'].sum()

print(f"💰 Sum of all pnl%: {total_pnl_pct:.2f}%")
print(f"💵 Expected final equity: ${initial_capital + initial_capital * RISK_PER_TRADE * (total_pnl_pct / 100):.2f}")
print(f"📊 Expected return%: {(initial_capital * RISK_PER_TRADE * (total_pnl_pct / 100) / initial_capital) * 100:.2f}%\n")

# Simulate equity curve step by step
equity = [initial_capital]
cumulative_pnl_dollar = 0

for pnl_pct in df['pnl'].values:
    trade_pnl_dollar = initial_capital * RISK_PER_TRADE * (pnl_pct / 100.0)
    cumulative_pnl_dollar += trade_pnl_dollar
    new_equity = initial_capital + cumulative_pnl_dollar
    equity.append(new_equity)

equity = equity[1:]  # Remove first element
final_equity = equity[-1]
total_return_pct = ((final_equity / initial_capital) - 1) * 100

print(f"🎯 Simulated Final Equity: ${final_equity:.2f}")
print(f"📈 Simulated Total Return: {total_return_pct:.2f}%\n")

# Check if there's a mismatch
print("="*60)
print("🔍 ANALYSIS:")
print("="*60)
print(f"With Prob% ~55% and RRR ~1.0-1.1:")
print(f"  - Expected edge per trade: ~{(wins['pnl'].mean() * len(wins) + losses['pnl'].mean() * len(losses)) / len(df):.3f}%")
print(f"  - With {len(df)} trades and 2% risk per trade:")
print(f"    Expected cumulative return: ~{total_pnl_pct * RISK_PER_TRADE:.2f}%")
print(f"    Expected final equity: ~${initial_capital * (1 + total_pnl_pct * RISK_PER_TRADE / 100):.2f}")

