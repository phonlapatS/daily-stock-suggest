"""
ตรวจสอบความแตกต่างระหว่าง:
1. ทุก trades (ไม่กรอง) - ใช้ใน equity curve ปัจจุบัน
2. Trades ที่ผ่านเกณฑ์ (กรอง) - ใช้ใน calculate_metrics.py
"""
import pandas as pd
import numpy as np

print("="*80)
print("🔍 ตรวจสอบ: ทุก trades vs Trades ที่ผ่านเกณฑ์")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print(f"\n📊 [1] ทุก Trades (ไม่กรอง) - ใช้ใน equity curve ปัจจุบัน")
print("-"*80)
print(f"Total trades: {len(df)}")
wins_all = df[df['pnl'] > 0]
losses_all = df[df['pnl'] <= 0]
win_rate_all = len(wins_all) / len(df) * 100
total_pnl_all = df['pnl'].sum()
print(f"Win Rate: {win_rate_all:.1f}%")
print(f"Total Pnl%: {total_pnl_all:.2f}%")
print(f"Avg Pnl% per trade: {df['pnl'].mean():.3f}%")

# 2. คำนวณ metrics ตาม calculate_metrics.py
print(f"\n📊 [2] คำนวณ Metrics ตาม calculate_metrics.py")
print("-"*80)

# Group by symbol
symbol_metrics = []
for symbol in df['symbol'].unique():
    symbol_trades = df[df['symbol'] == symbol].copy()
    
    # Calculate metrics (same as calculate_metrics.py)
    wins = symbol_trades[symbol_trades['pnl'] > 0]
    losses = symbol_trades[symbol_trades['pnl'] <= 0]
    
    count = len(symbol_trades)
    prob = len(wins) / count * 100 if count > 0 else 0
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    symbol_metrics.append({
        'symbol': symbol,
        'count': count,
        'prob': prob,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rrr': rrr,
        'total_pnl': symbol_trades['pnl'].sum()
    })

metrics_df = pd.DataFrame(symbol_metrics)

# 3. กรองตามเกณฑ์ Thai Market (Prob >= 60%, RRR >= 1.3, Count >= 30)
print(f"\n📊 [3] Trades ที่ผ่านเกณฑ์ (Prob >= 60%, RRR >= 1.3, Count >= 30)")
print("-"*80)

filtered = metrics_df[
    (metrics_df['prob'] >= 60.0) & 
    (metrics_df['rrr'] >= 1.3) &
    (metrics_df['count'] >= 30)
]

print(f"Symbols ที่ผ่านเกณฑ์: {len(filtered)} symbols")
print(f"Trades ที่ผ่านเกณฑ์: {filtered['count'].sum()} trades ({filtered['count'].sum()/len(df)*100:.1f}%)")

# Get trades for filtered symbols
filtered_symbols = filtered['symbol'].tolist()
filtered_trades = df[df['symbol'].isin(filtered_symbols)]

if not filtered_trades.empty:
    wins_filtered = filtered_trades[filtered_trades['pnl'] > 0]
    losses_filtered = filtered_trades[filtered_trades['pnl'] <= 0]
    win_rate_filtered = len(wins_filtered) / len(filtered_trades) * 100
    total_pnl_filtered = filtered_trades['pnl'].sum()
    
    print(f"\n📈 Metrics ของ Trades ที่ผ่านเกณฑ์:")
    print(f"   Win Rate: {win_rate_filtered:.1f}%")
    print(f"   Total Pnl%: {total_pnl_filtered:.2f}%")
    print(f"   Avg Pnl% per trade: {filtered_trades['pnl'].mean():.3f}%")
    
    # 4. เปรียบเทียบ
    print(f"\n📊 [4] เปรียบเทียบ")
    print("-"*80)
    print(f"{'Metric':<30} {'ทุก Trades':>15} {'ผ่านเกณฑ์':>15} {'Difference':>15}")
    print("-"*80)
    print(f"{'Total Trades':<30} {len(df):>15} {len(filtered_trades):>15} {len(df)-len(filtered_trades):>15}")
    print(f"{'Win Rate':<30} {win_rate_all:>14.1f}% {win_rate_filtered:>14.1f}% {win_rate_filtered-win_rate_all:>14.1f}%")
    print(f"{'Total Pnl%':<30} {total_pnl_all:>14.2f}% {total_pnl_filtered:>14.2f}% {total_pnl_filtered-total_pnl_all:>14.2f}%")
    print(f"{'Avg Pnl% per trade':<30} {df['pnl'].mean():>14.3f}% {filtered_trades['pnl'].mean():>14.3f}% {filtered_trades['pnl'].mean()-df['pnl'].mean():>14.3f}%")
    
    print(f"\n💡 สรุป:")
    print(f"   ✅ Trades ที่ผ่านเกณฑ์มี Win Rate สูงกว่า {win_rate_filtered-win_rate_all:.1f}%")
    print(f"   ✅ Trades ที่ผ่านเกณฑ์มี Total Pnl% สูงกว่า {total_pnl_filtered-total_pnl_all:.2f}%")
    print(f"   ⚠️ แต่มีเพียง {len(filtered_trades)/len(df)*100:.1f}% ของ trades ทั้งหมด")
    print(f"\n   → Equity curve ควรใช้เฉพาะ trades ที่ผ่านเกณฑ์เพื่อให้สอดคล้องกับ calculate_metrics.py")

print("\n" + "="*80)

