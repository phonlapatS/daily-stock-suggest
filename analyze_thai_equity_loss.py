"""
วิเคราะห์ว่าทำไม Thai Market Equity Curve ถึงขาดทุนทั้งๆที่หุ้นที่ผ่านเกณฑ์ก็เยอะ
"""
import pandas as pd
import numpy as np

print("="*80)
print("🔍 วิเคราะห์: ทำไม Thai Market Equity Curve ถึงขาดทุน?")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
qualifying = ['BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
              'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'QH', 'NEX', 'FORTH',
              'PTG', 'STA', 'PSL', 'MAJOR', 'BANPU', 'OR', 'BCH', 'TPIPL', 'RATCH',
              'TTB', 'TASCO', 'BCPG']

df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

filtered = df[df['symbol'].isin(qualifying)].copy()

print(f"\n📊 [1] ภาพรวม")
print("-"*80)
print(f"Total trades: {len(df)}")
print(f"Qualifying trades: {len(filtered)} ({len(filtered)/len(df)*100:.1f}%)")
print(f"Other trades: {len(df)-len(filtered)} ({(len(df)-len(filtered))/len(df)*100:.1f}%)")

print(f"\n📊 [2] Qualifying Symbols Performance")
print("-"*80)

symbol_stats = []
for sym in qualifying:
    sym_trades = filtered[filtered['symbol'] == sym]
    if len(sym_trades) == 0:
        continue
    
    wins = sym_trades[sym_trades['pnl'] > 0]
    losses = sym_trades[sym_trades['pnl'] <= 0]
    
    prob = len(wins)/len(sym_trades)*100 if len(sym_trades) > 0 else 0
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
    rrr = avg_win/avg_loss if avg_loss > 0 else 0
    total_pnl = sym_trades['pnl'].sum()
    
    symbol_stats.append({
        'symbol': sym,
        'count': len(sym_trades),
        'prob': prob,
        'rrr': rrr,
        'total_pnl': total_pnl
    })

stats_df = pd.DataFrame(symbol_stats).sort_values('total_pnl')

print(f"\n✅ Top 5 Winners:")
print(stats_df.tail(5)[['symbol', 'count', 'prob', 'rrr', 'total_pnl']].to_string(index=False))

print(f"\n❌ Top 5 Losers:")
print(stats_df.head(5)[['symbol', 'count', 'prob', 'rrr', 'total_pnl']].to_string(index=False))

print(f"\n📊 [3] Overall Qualifying Performance")
print("-"*80)
overall_wr = (filtered['pnl'] > 0).sum()/len(filtered)*100 if len(filtered) > 0 else 0
overall_pnl = filtered['pnl'].sum()
overall_avg_win = filtered[filtered['pnl'] > 0]['pnl'].mean() if len(filtered[filtered['pnl'] > 0]) > 0 else 0
overall_avg_loss = abs(filtered[filtered['pnl'] <= 0]['pnl'].mean()) if len(filtered[filtered['pnl'] <= 0]) > 0 else 0

print(f"Win Rate: {overall_wr:.1f}%")
print(f"Total Pnl%: {overall_pnl:.2f}%")
print(f"Avg Win%: {overall_avg_win:.2f}%")
print(f"Avg Loss%: {overall_avg_loss:.2f}%")
if overall_avg_loss > 0:
    overall_rrr = overall_avg_win / overall_avg_loss
    print(f"RRR: {overall_rrr:.2f}")

# Expected Value per trade
if len(filtered) > 0:
    ev_per_trade = overall_pnl / len(filtered)
    print(f"Expected Value per Trade: {ev_per_trade:.3f}%")

print(f"\n📊 [4] วิเคราะห์สาเหตุ")
print("-"*80)

# วิเคราะห์ว่าทำไม Win Rate ถึงต่ำ
print(f"\n💡 สาเหตุที่ Win Rate ต่ำ ({overall_wr:.1f}%):")
print(f"   1. แม้จะมีหุ้นที่ผ่านเกณฑ์ 30 ตัว แต่ Win Rate โดยรวมยังต่ำ")
print(f"   2. Expected Value ต่อ trade: {ev_per_trade:.3f}% (ต่ำมาก)")
print(f"   3. RRR: {overall_rrr:.2f} (ดี) แต่ Win Rate ต่ำ → Expected Value ต่ำ")

# วิเคราะห์สัดส่วนหุ้นที่กำไร vs ขาดทุน
profitable_symbols = stats_df[stats_df['total_pnl'] > 0]
losing_symbols = stats_df[stats_df['total_pnl'] <= 0]

print(f"\n📈 หุ้นที่กำไร: {len(profitable_symbols)} ตัว")
if len(profitable_symbols) > 0:
    print(f"   Total Pnl%: {profitable_symbols['total_pnl'].sum():.2f}%")
    print(f"   Avg Win Rate: {profitable_symbols['prob'].mean():.1f}%")

print(f"\n📉 หุ้นที่ขาดทุน: {len(losing_symbols)} ตัว")
if len(losing_symbols) > 0:
    print(f"   Total Pnl%: {losing_symbols['total_pnl'].sum():.2f}%")
    print(f"   Avg Win Rate: {losing_symbols['prob'].mean():.1f}%")

print(f"\n💡 สรุป:")
print(f"   - หุ้นที่ผ่านเกณฑ์ใน calculate_metrics.py มี Prob% และ RRR ดี")
print(f"   - แต่เมื่อรวมทุก trades ของหุ้นเหล่านี้ → Win Rate โดยรวมต่ำ ({overall_wr:.1f}%)")
print(f"   - สาเหตุ: มีหุ้นบางตัวที่ผ่านเกณฑ์แต่ Win Rate ต่ำ หรือมี trades ที่ไม่ผ่านเกณฑ์แต่ยังถูกนับ")
print(f"   - หรือ: เกณฑ์ใน calculate_metrics.py อาจไม่เข้มงวดพอ (Prob >= 60%, RRR >= 1.3)")

print("\n" + "="*80)

