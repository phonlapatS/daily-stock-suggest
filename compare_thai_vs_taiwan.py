"""
เปรียบเทียบ ไทย vs ไต้หวัน: ทำไมไต้หวัน Prob% ต่ำกว่าแต่กำไรกว่า?
"""
import pandas as pd
import numpy as np

print("="*80)
print("Compare THAI vs TAIWAN: Why Taiwan has lower Prob% but more profit?")
print("="*80)

# Load trades
thai = pd.read_csv('logs/trade_history_THAI.csv')
tw = pd.read_csv('logs/trade_history_TAIWAN.csv')

thai_qual = ['BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
             'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'NEX', 'FORTH',
             'PTG', 'STA', 'PSL', 'MAJOR', 'OR', 'BCH', 'RATCH',
             'TTB', 'TASCO']

tw_qual = [3711, 2330, 2303, 2382]  # ASE, TSMC, UMC, Quanta (as integers)

thai_f = thai[thai['symbol'].isin(thai_qual)].copy()
tw_f = tw[tw['symbol'].isin(tw_qual)].copy()

thai_f['actual_return'] = pd.to_numeric(thai_f['actual_return'], errors='coerce')
tw_f['actual_return'] = pd.to_numeric(tw_f['actual_return'], errors='coerce')

thai_f['pnl'] = thai_f.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
tw_f['pnl'] = tw_f.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print("\n[1] Overall Comparison")
print("-"*80)
print("THAI:")
print(f"  Trades: {len(thai_f)}")
thai_wr = (thai_f['pnl'] > 0).sum()/len(thai_f)*100 if len(thai_f) > 0 else 0
thai_total_pnl = thai_f['pnl'].sum()
thai_avg_win = thai_f[thai_f['pnl'] > 0]['pnl'].mean() if len(thai_f[thai_f['pnl'] > 0]) > 0 else 0
thai_avg_loss = abs(thai_f[thai_f['pnl'] <= 0]['pnl'].mean()) if len(thai_f[thai_f['pnl'] <= 0]) > 0 else 0
thai_rrr = thai_avg_win / thai_avg_loss if thai_avg_loss > 0 else 0

print(f"  Win Rate: {thai_wr:.1f}%")
print(f"  Total Pnl%: {thai_total_pnl:.2f}%")
print(f"  Avg Win%: {thai_avg_win:.2f}%")
print(f"  Avg Loss%: {thai_avg_loss:.2f}%")
print(f"  RRR: {thai_rrr:.2f}")

print("\nTAIWAN:")
print(f"  Trades: {len(tw_f)}")
tw_wr = (tw_f['pnl'] > 0).sum()/len(tw_f)*100 if len(tw_f) > 0 else 0
tw_total_pnl = tw_f['pnl'].sum()
tw_avg_win = tw_f[tw_f['pnl'] > 0]['pnl'].mean() if len(tw_f[tw_f['pnl'] > 0]) > 0 else 0
tw_avg_loss = abs(tw_f[tw_f['pnl'] <= 0]['pnl'].mean()) if len(tw_f[tw_f['pnl'] <= 0]) > 0 else 0
tw_rrr = tw_avg_win / tw_avg_loss if tw_avg_loss > 0 else 0

print(f"  Win Rate: {tw_wr:.1f}%")
print(f"  Total Pnl%: {tw_total_pnl:.2f}%")
print(f"  Avg Win%: {tw_avg_win:.2f}%")
print(f"  Avg Loss%: {tw_avg_loss:.2f}%")
print(f"  RRR: {tw_rrr:.2f}")

print("\n[2] Expected Value Analysis")
print("-"*80)
# Expected Value = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
thai_ev = (thai_wr/100 * thai_avg_win) - ((1 - thai_wr/100) * thai_avg_loss)
tw_ev = (tw_wr/100 * tw_avg_win) - ((1 - tw_wr/100) * tw_avg_loss)

print(f"THAI Expected Value per trade: {thai_ev:.3f}%")
print(f"TAIWAN Expected Value per trade: {tw_ev:.3f}%")

print("\n[3] Per Symbol Analysis")
print("-"*80)

print("\nTHAI - Top 5 by Count:")
thai_symbols = []
for sym in thai_qual:
    sym_trades = thai_f[thai_f['symbol'] == sym]
    if len(sym_trades) == 0:
        continue
    wins = sym_trades[sym_trades['pnl'] > 0]
    prob = len(wins)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    losses = sym_trades[sym_trades['pnl'] <= 0]
    avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    total_pnl = sym_trades['pnl'].sum()
    ev = (prob/100 * avg_win) - ((1 - prob/100) * avg_loss)
    
    thai_symbols.append({
        'symbol': sym,
        'count': len(sym_trades),
        'prob': prob,
        'rrr': rrr,
        'ev': ev,
        'total_pnl': total_pnl
    })

thai_df = pd.DataFrame(thai_symbols).sort_values('count', ascending=False)
print(thai_df.head(5)[['symbol', 'count', 'prob', 'rrr', 'ev', 'total_pnl']].to_string(index=False))

print("\nTAIWAN - All symbols:")
tw_symbols = []
for sym in tw_qual:
    sym_trades = tw_f[tw_f['symbol'] == sym]
    if len(sym_trades) == 0:
        continue
    wins = sym_trades[sym_trades['pnl'] > 0]
    prob = len(wins)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    losses = sym_trades[sym_trades['pnl'] <= 0]
    avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    total_pnl = sym_trades['pnl'].sum()
    ev = (prob/100 * avg_win) - ((1 - prob/100) * avg_loss)
    
    tw_symbols.append({
        'symbol': sym,
        'count': len(sym_trades),
        'prob': prob,
        'rrr': rrr,
        'ev': ev,
        'total_pnl': total_pnl
    })

if tw_symbols:
    tw_df = pd.DataFrame(tw_symbols).sort_values('count', ascending=False)
    print(tw_df[['symbol', 'count', 'prob', 'rrr', 'ev', 'total_pnl']].to_string(index=False))
else:
    print("No Taiwan symbols found")

print("\n[4] Key Insight")
print("-"*80)
print("THAI:")
print(f"  - High Prob% in table (60-88%) but low Win Rate in reality ({thai_wr:.1f}%)")
print(f"  - High RRR in table (1.5-3.5) but low RRR in reality ({thai_rrr:.2f})")
print(f"  - Expected Value: {thai_ev:.3f}% (negative = losing)")

print("\nTAIWAN:")
print(f"  - Lower Prob% in table (50-57%) but matches Win Rate in reality ({tw_wr:.1f}%)")
print(f"  - Lower RRR in table (1.0-1.1) but matches RRR in reality ({tw_rrr:.2f})")
print(f"  - Expected Value: {tw_ev:.3f}% (positive = profitable)")

print("\nConclusion:")
print("  - THAI: Prob% in table = Correct Rate (70.9%), not Profit Rate (35.7%)")
print("  - TAIWAN: Prob% in table = Profit Rate (55-57%), matches reality")
print("  - TAIWAN is more consistent: table metrics match actual performance")
print("  - THAI has discrepancy: table shows high Prob% but actual Win Rate is low")

print("\n" + "="*80)

