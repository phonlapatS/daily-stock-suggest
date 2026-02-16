"""
ตรวจสอบว่าทำไมหุ้นไทยถึงมีกำไรน้อย แม้ว่าจะมี RRR สูง
"""
import pandas as pd
import numpy as np

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
print(f"📊 Thai Total Trades: {len(df)}")
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

# Calculate expected equity (simple cumulative sum)
initial_capital = 1000
total_pnl_pct = df['pnl'].sum()

print(f"💰 Sum of all pnl%: {total_pnl_pct:.2f}%")
print(f"💵 Expected final equity: ${initial_capital * (1 + total_pnl_pct / 100):.2f}")
print(f"📊 Expected return%: {total_pnl_pct:.2f}%\n")

# Simulate equity curve step by step
equity = [initial_capital]
cumulative_return_pct = 0

for pnl_pct in df['pnl'].values:
    cumulative_return_pct += pnl_pct
    new_equity = initial_capital * (1 + cumulative_return_pct / 100.0)
    equity.append(new_equity)

equity = equity[1:]  # Remove first element
final_equity = equity[-1]
total_return_pct = ((final_equity / initial_capital) - 1) * 100

print(f"🎯 Simulated Final Equity: ${final_equity:.2f}")
print(f"📈 Simulated Total Return: {total_return_pct:.2f}%\n")

# Analysis: Why low profit despite high RRR?
print("="*60)
print("🔍 ANALYSIS: ทำไมกำไรน้อยแม้ RRR สูง?")
print("="*60)
print(f"RRR = {wins['pnl'].mean() / abs(losses['pnl'].mean()) if len(losses) > 0 else 0:.2f}")
print(f"Win Rate = {len(wins)/len(df)*100:.1f}%")
print(f"Expected Edge per Trade = {(wins['pnl'].mean() * len(wins) + losses['pnl'].mean() * len(losses)) / len(df):.3f}%")
print(f"\n💡 สาเหตุที่กำไรน้อย:")
print(f"   1. Win Rate ต่ำ: {len(wins)/len(df)*100:.1f}% (แม้ RRR สูง แต่ชนะน้อยครั้ง)")
print(f"   2. Expected Edge ต่อ trade: {(wins['pnl'].mean() * len(wins) + losses['pnl'].mean() * len(losses)) / len(df):.3f}%")
print(f"   3. จำนวน trades: {len(df)} trades")
print(f"   4. ผลรวม pnl%: {total_pnl_pct:.2f}% (ต่ำเพราะ Win Rate ต่ำ)")

# Check if RRR is misleading
if len(wins) > 0 and len(losses) > 0:
    avg_win = wins['pnl'].mean()
    avg_loss = abs(losses['pnl'].mean())
    rrr = avg_win / avg_loss
    win_rate = len(wins) / len(df)
    
    # Expected Value per trade
    ev = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    print(f"\n📊 Expected Value per Trade: {ev:.3f}%")
    print(f"   (Win Rate {win_rate*100:.1f}% × AvgWin {avg_win:.2f}%) - (Loss Rate {(1-win_rate)*100:.1f}% × AvgLoss {avg_loss:.2f}%)")
    print(f"\n💡 สรุป: RRR สูงแต่กำไรน้อยเพราะ Win Rate ต่ำ")
    print(f"   RRR = {rrr:.2f} แต่ Win Rate = {win_rate*100:.1f}%")
    print(f"   → Expected Value = {ev:.3f}% ต่อ trade (ต่ำ)")

