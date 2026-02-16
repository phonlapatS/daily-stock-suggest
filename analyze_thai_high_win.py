"""
วิเคราะห์ว่าทำไมหุ้นไทยถึงมีกำไรน้อย แม้จะมีหุ้นที่มี Win Rate สูงเยอะ
"""
import pandas as pd
import numpy as np

print("="*80)
print("🔍 วิเคราะห์: ทำไมหุ้นไทยกำไรน้อยแม้มีหุ้น Win Rate สูงเยอะ?")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print(f"\n📊 Total Thai trades: {len(df)}")

# 1. วิเคราะห์ตาม Win Rate
print("\n" + "="*80)
print("📈 [1] วิเคราะห์ตาม Win Rate")
print("="*80)

# คำนวณ Win Rate และ Total Pnl สำหรับแต่ละ symbol
symbol_stats = []
for symbol in df['symbol'].unique():
    symbol_trades = df[df['symbol'] == symbol]
    wins = symbol_trades[symbol_trades['pnl'] > 0]
    win_rate = len(wins) / len(symbol_trades) * 100
    total_pnl = symbol_trades['pnl'].sum()
    symbol_stats.append({
        'symbol': symbol,
        'count': len(symbol_trades),
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'avg_pnl': symbol_trades['pnl'].mean()
    })

symbol_df = pd.DataFrame(symbol_stats).sort_values('win_rate', ascending=False)

# แบ่งเป็นกลุ่มตาม Win Rate
high_win = symbol_df[symbol_df['win_rate'] >= 70]
medium_win = symbol_df[(symbol_df['win_rate'] >= 60) & (symbol_df['win_rate'] < 70)]
low_win = symbol_df[symbol_df['win_rate'] < 60]

print(f"\n✅ High Win Rate (>= 70%): {len(high_win)} symbols")
if not high_win.empty:
    high_win_trades = df[df['symbol'].isin(high_win['symbol'])]
    print(f"   Trades: {len(high_win_trades)} ({len(high_win_trades)/len(df)*100:.1f}%)")
    print(f"   Total Pnl%: {high_win_trades['pnl'].sum():.2f}%")
    print(f"   Avg Pnl% per trade: {high_win_trades['pnl'].mean():.3f}%")
    print(f"   Top 5: {', '.join(high_win.head(5)['symbol'].tolist())}")

print(f"\n⚠️ Medium Win Rate (60-70%): {len(medium_win)} symbols")
if not medium_win.empty:
    medium_win_trades = df[df['symbol'].isin(medium_win['symbol'])]
    print(f"   Trades: {len(medium_win_trades)} ({len(medium_win_trades)/len(df)*100:.1f}%)")
    print(f"   Total Pnl%: {medium_win_trades['pnl'].sum():.2f}%")
    print(f"   Avg Pnl% per trade: {medium_win_trades['pnl'].mean():.3f}%")

print(f"\n❌ Low Win Rate (< 60%): {len(low_win)} symbols")
if not low_win.empty:
    low_win_trades = df[df['symbol'].isin(low_win['symbol'])]
    print(f"   Trades: {len(low_win_trades)} ({len(low_win_trades)/len(df)*100:.1f}%)")
    print(f"   Total Pnl%: {low_win_trades['pnl'].sum():.2f}%")
    print(f"   Avg Pnl% per trade: {low_win_trades['pnl'].mean():.3f}%")

# 2. วิเคราะห์หุ้นที่มี Win Rate สูงแต่กำไรน้อย
print("\n" + "="*80)
print("🔍 [2] วิเคราะห์: หุ้น Win Rate สูงแต่กำไรน้อย")
print("="*80)

# หาหุ้นที่มี Win Rate >= 70% แต่ Total Pnl ต่ำ
high_win_low_profit = high_win[high_win['total_pnl'] < 0].sort_values('total_pnl')
if not high_win_low_profit.empty:
    print(f"\n⚠️ หุ้น Win Rate >= 70% แต่ Total Pnl ติดลบ: {len(high_win_low_profit)} symbols")
    for _, row in high_win_low_profit.head(10).iterrows():
        symbol_trades = df[df['symbol'] == row['symbol']]
        wins = symbol_trades[symbol_trades['pnl'] > 0]
        losses = symbol_trades[symbol_trades['pnl'] <= 0]
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"   {row['symbol']}: Win Rate {row['win_rate']:.1f}%, Count {int(row['count'])}, "
              f"Total Pnl {row['total_pnl']:.2f}%, RRR {rrr:.2f}, "
              f"AvgWin {avg_win:.2f}%, AvgLoss {avg_loss:.2f}%")

# 3. วิเคราะห์สัดส่วนของหุ้น Win Rate สูง
print("\n" + "="*80)
print("📊 [3] สัดส่วนของหุ้น Win Rate สูงในพอร์ตโฟลิโอ")
print("="*80)

if not high_win.empty:
    high_win_symbols = high_win['symbol'].tolist()
    high_win_trades = df[df['symbol'].isin(high_win_symbols)]
    other_trades = df[~df['symbol'].isin(high_win_symbols)]
    
    print(f"\nHigh Win Rate Symbols (>= 70%):")
    print(f"   Symbols: {len(high_win_symbols)} symbols")
    print(f"   Trades: {len(high_win_trades)} ({len(high_win_trades)/len(df)*100:.1f}%)")
    print(f"   Total Pnl%: {high_win_trades['pnl'].sum():.2f}%")
    print(f"   Contribution: {high_win_trades['pnl'].sum() / df['pnl'].sum() * 100:.1f}% of total Pnl%")
    
    print(f"\nOther Symbols (< 70%):")
    print(f"   Trades: {len(other_trades)} ({len(other_trades)/len(df)*100:.1f}%)")
    print(f"   Total Pnl%: {other_trades['pnl'].sum():.2f}%")
    print(f"   Contribution: {other_trades['pnl'].sum() / df['pnl'].sum() * 100:.1f}% of total Pnl%")

# 4. สรุป
print("\n" + "="*80)
print("💡 [4] สรุป")
print("="*80)

total_pnl = df['pnl'].sum()
overall_win_rate = (df['pnl'] > 0).sum() / len(df) * 100

print(f"\n📊 Overall Thai Market:")
print(f"   Total Trades: {len(df)}")
print(f"   Overall Win Rate: {overall_win_rate:.1f}%")
print(f"   Total Pnl%: {total_pnl:.2f}%")
print(f"   Avg Pnl% per trade: {df['pnl'].mean():.3f}%")

if not high_win.empty:
    high_win_trades = df[df['symbol'].isin(high_win['symbol'])]
    high_win_pnl = high_win_trades['pnl'].sum()
    high_win_pct = len(high_win_trades) / len(df) * 100
    
    print(f"\n💡 สาเหตุที่กำไรน้อย:")
    if high_win_pct < 50:
        print(f"   ⚠️ หุ้น Win Rate สูงมีสัดส่วนน้อย ({high_win_pct:.1f}%)")
        print(f"   → หุ้น Win Rate ต่ำมีสัดส่วนมาก ({100-high_win_pct:.1f}%)")
        print(f"   → ทำให้ Overall Win Rate ต่ำ ({overall_win_rate:.1f}%)")
    else:
        print(f"   ✅ หุ้น Win Rate สูงมีสัดส่วนมาก ({high_win_pct:.1f}%)")
        print(f"   ⚠️ แต่หุ้น Win Rate สูงบางตัวอาจมี RRR ต่ำหรือ AvgWin% ต่ำ")
        print(f"   → ทำให้ Expected Value ต่อ trade ต่ำ")

print("\n" + "="*80)

