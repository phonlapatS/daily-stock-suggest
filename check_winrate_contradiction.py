"""
Check why Win Rate is low even though each stock wins more than loses
"""
import pandas as pd
import numpy as np

print("="*80)
print("Check: Why is Win Rate low even though each stock wins more than loses?")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
qualifying = ['BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
              'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'NEX', 'FORTH',
              'PTG', 'STA', 'PSL', 'MAJOR', 'OR', 'BCH', 'RATCH',
              'TTB', 'TASCO']

filtered = df[df['symbol'].isin(qualifying)].copy()
filtered['actual_return'] = pd.to_numeric(filtered['actual_return'], errors='coerce')
filtered['correct'] = pd.to_numeric(filtered['correct'], errors='coerce')
filtered['pnl'] = filtered.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print(f"\n[1] Compare Correct vs PnL > 0")
print("-"*80)
print(f"Total trades: {len(filtered)}")
print(f"Correct (forecast == actual): {(filtered['correct'] == 1).sum()} ({(filtered['correct'] == 1).sum()/len(filtered)*100:.1f}%)")
print(f"PnL > 0 (profit): {(filtered['pnl'] > 0).sum()} ({(filtered['pnl'] > 0).sum()/len(filtered)*100:.1f}%)")

# Check if there are trades that differ
diff = (filtered['correct'] == 1) != (filtered['pnl'] > 0)
print(f"\nTrades that differ (Correct != PnL > 0): {diff.sum()} ({diff.sum()/len(filtered)*100:.1f}%)")

if diff.sum() > 0:
    print("\nReason for difference:")
    print("   - Correct = 1: forecast is correct (UP/DOWN matches actual)")
    print("   - PnL > 0: profit (actual_return * direction > 0)")
    print("   - May differ due to Risk Management (SL/TP) affecting profit/loss")

print(f"\n[2] Analyze Win Rate per stock")
print("-"*80)

symbol_stats = []
for sym in qualifying:
    sym_trades = filtered[filtered['symbol'] == sym]
    if len(sym_trades) == 0:
        continue
    
    wins = sym_trades[sym_trades['pnl'] > 0]
    prob = len(wins)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    
    symbol_stats.append({
        'symbol': sym,
        'count': len(sym_trades),
        'prob': prob
    })

stats_df = pd.DataFrame(symbol_stats).sort_values('count', ascending=False)

print("Top 10 stocks with high Count:")
print(stats_df.head(10)[['symbol', 'count', 'prob']].to_string(index=False))

# Calculate weighted average
weighted_avg = (stats_df['prob'] * stats_df['count']).sum() / stats_df['count'].sum()
simple_avg = stats_df['prob'].mean()
overall_wr = (filtered['pnl'] > 0).sum()/len(filtered)*100

print(f"\n[3] Compare Prob%")
print("-"*80)
print(f"Simple Average Prob% (simple average): {simple_avg:.1f}%")
print(f"Weighted Average Prob% (by Count): {weighted_avg:.1f}%")
print(f"Overall Win Rate (actual): {overall_wr:.1f}%")

print(f"\n[4] Analysis")
print("-"*80)

# Find stocks with high Count but low Prob%
high_count_low_prob = stats_df[(stats_df['count'] >= 200) & (stats_df['prob'] < 70)]
if not high_count_low_prob.empty:
    print(f"\nStocks with high Count (>= 200) but low Prob% (< 70%):")
    print(high_count_low_prob[['symbol', 'count', 'prob']].to_string(index=False))
    total_trades_low_prob = high_count_low_prob['count'].sum()
    print(f"Total trades: {total_trades_low_prob} ({total_trades_low_prob/len(filtered)*100:.1f}% of total)")
    
    # Calculate Win Rate of these stocks
    low_prob_trades = filtered[filtered['symbol'].isin(high_count_low_prob['symbol'])]
    low_prob_wr = (low_prob_trades['pnl'] > 0).sum() / len(low_prob_trades) * 100
    print(f"Win Rate of these stocks: {low_prob_wr:.1f}%")

# Find stocks with high Prob% but low Count
high_prob_low_count = stats_df[(stats_df['prob'] >= 80) & (stats_df['count'] < 100)]
if not high_prob_low_count.empty:
    print(f"\nStocks with high Prob% (>= 80%) but low Count (< 100):")
    print(high_prob_low_count[['symbol', 'count', 'prob']].to_string(index=False))
    total_trades_high_prob = high_prob_low_count['count'].sum()
    print(f"Total trades: {total_trades_high_prob} ({total_trades_high_prob/len(filtered)*100:.1f}% of total)")

print(f"\nSummary:")
print(f"   - If Weighted Average Prob% ≈ Overall Win Rate -> No contradiction")
print(f"   - If Weighted Average Prob% >> Overall Win Rate -> May have calculation issue")
print(f"   - Check if Prob% in table is calculated from 'correct' or 'pnl > 0'")

print("\n" + "="*80)
