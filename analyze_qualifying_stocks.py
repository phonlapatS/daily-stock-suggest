"""
วิเคราะห์: หุ้นที่ผ่านเกณฑ์ (Prob% >= 60%, RRR >= 1.5) ควรจะกำไร แต่ทำไมถึงขาดทุน?
และ trades ที่ทายถูกแต่ขาดทุนคือยังไง?
"""
import pandas as pd
import numpy as np

print("="*80)
print("Analysis: Why qualifying stocks (Prob% >= 60%, RRR >= 1.5) are losing money?")
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

print("\n[1] Overall Qualifying Stocks Performance")
print("-"*80)
print(f"Total trades: {len(filtered)}")
print(f"Correct Rate: {(filtered['correct'] == 1).sum()/len(filtered)*100:.1f}%")
print(f"Profit Rate: {(filtered['pnl'] > 0).sum()/len(filtered)*100:.1f}%")
print(f"Total Pnl%: {filtered['pnl'].sum():.2f}%")

print("\n[2] Trades that are CORRECT but LOSE MONEY")
print("-"*80)
correct_but_loss = filtered[(filtered['correct'] == 1) & (filtered['pnl'] <= 0)]
print(f"Count: {len(correct_but_loss)} ({len(correct_but_loss)/len(filtered)*100:.1f}% of total)")
print(f"Avg PnL: {correct_but_loss['pnl'].mean():.2f}%")
print(f"Total PnL: {correct_but_loss['pnl'].sum():.2f}%")

if len(correct_but_loss) > 0:
    print("\nSample trades (first 10):")
    sample = correct_but_loss.head(10)[['symbol', 'forecast', 'actual', 'actual_return', 'pnl', 'exit_reason']]
    print(sample.to_string(index=False))
    
    # Analyze exit reasons
    if 'exit_reason' in correct_but_loss.columns:
        print("\nExit reasons for correct but losing trades:")
        exit_reasons = correct_but_loss['exit_reason'].value_counts()
        print(exit_reasons)

print("\n[3] Per Symbol Analysis")
print("-"*80)

symbol_stats = []
for sym in qualifying:
    sym_trades = filtered[filtered['symbol'] == sym]
    if len(sym_trades) == 0:
        continue
    
    correct = sym_trades[sym_trades['correct'] == 1]
    correct_rate = len(correct)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    
    profit = sym_trades[sym_trades['pnl'] > 0]
    profit_rate = len(profit)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    
    correct_but_loss = sym_trades[(sym_trades['correct'] == 1) & (sym_trades['pnl'] <= 0)]
    correct_but_loss_rate = len(correct_but_loss)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    
    total_pnl = sym_trades['pnl'].sum()
    
    symbol_stats.append({
        'symbol': sym,
        'count': len(sym_trades),
        'correct_rate': correct_rate,
        'profit_rate': profit_rate,
        'correct_but_loss_rate': correct_but_loss_rate,
        'total_pnl': total_pnl
    })

stats_df = pd.DataFrame(symbol_stats).sort_values('correct_but_loss_rate', ascending=False)

print("Stocks with highest 'Correct but Loss' rate:")
print(stats_df.head(10)[['symbol', 'count', 'correct_rate', 'profit_rate', 'correct_but_loss_rate', 'total_pnl']].to_string(index=False))

print("\n[4] Why Qualifying Stocks Are Losing Money?")
print("-"*80)
print("Qualifying criteria:")
print("  - Prob% >= 60% (Correct Rate)")
print("  - RRR >= 1.5")
print("\nProblem:")
print("  - Prob% in table = Correct Rate (forecast == actual)")
print("  - But Profit Rate (PnL > 0) is much lower!")
print("  - Many trades are CORRECT but LOSE MONEY due to Risk Management")
print("\nSolution:")
print("  - Should filter by Profit Rate instead of Correct Rate")
print("  - Or adjust Risk Management (SL/TP) to match Correct Rate")

print("\n" + "="*80)

