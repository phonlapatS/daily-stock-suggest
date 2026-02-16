"""
วิเคราะห์ว่าทำไม Win Rate โดยรวมถึงต่ำ (35.7%) ทั้งๆที่แต่ละหุ้นมี Prob% สูง (60-88%)
"""
import pandas as pd
import numpy as np

print("="*80)
print("🔍 วิเคราะห์: ทำไม Win Rate โดยรวมถึงต่ำทั้งๆที่แต่ละหุ้นมี Prob% สูง?")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')
qualifying = ['BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
              'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'NEX', 'FORTH',
              'PTG', 'STA', 'PSL', 'MAJOR', 'OR', 'BCH', 'RATCH',
              'TTB', 'TASCO']

df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

filtered = df[df['symbol'].isin(qualifying)].copy()
filtered['pnl'] = filtered.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print(f"\n📊 [1] ภาพรวม")
print("-"*80)
overall_wr = (filtered['pnl'] > 0).sum()/len(filtered)*100 if len(filtered) > 0 else 0
print(f"Total qualifying trades: {len(filtered)}")
print(f"Overall Win Rate: {overall_wr:.1f}%")

print(f"\n📊 [2] Win Rate ต่อหุ้น (เรียงตาม Count)")
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

print(stats_df.to_string(index=False))

# Calculate weighted average
weighted_avg = (stats_df['prob'] * stats_df['count']).sum() / stats_df['count'].sum()
simple_avg = stats_df['prob'].mean()

print(f"\n📊 [3] เปรียบเทียบ Prob%")
print("-"*80)
print(f"Weighted Average Prob% (ตาม Count): {weighted_avg:.1f}%")
print(f"Simple Average Prob% (เฉลี่ยธรรมดา): {simple_avg:.1f}%")
print(f"Overall Win Rate (จริง): {overall_wr:.1f}%")

print(f"\n💡 [4] วิเคราะห์สาเหตุ")
print("-"*80)

# หาหุ้นที่มี Count สูงแต่ Prob% ต่ำ
high_count_low_prob = stats_df[(stats_df['count'] >= 200) & (stats_df['prob'] < 70)]
if not high_count_low_prob.empty:
    print(f"\nหุ้นที่มี Count สูง (>= 200) แต่ Prob% ต่ำ (< 70%):")
    print(high_count_low_prob[['symbol', 'count', 'prob']].to_string(index=False))
    total_trades_low_prob = high_count_low_prob['count'].sum()
    print(f"Total trades จากหุ้นเหล่านี้: {total_trades_low_prob} ({total_trades_low_prob/len(filtered)*100:.1f}% ของทั้งหมด)")

# หาหุ้นที่มี Prob% สูงแต่ Count ต่ำ
high_prob_low_count = stats_df[(stats_df['prob'] >= 80) & (stats_df['count'] < 50)]
if not high_prob_low_count.empty:
    print(f"\nหุ้นที่มี Prob% สูง (>= 80%) แต่ Count ต่ำ (< 50):")
    print(high_prob_low_count[['symbol', 'count', 'prob']].to_string(index=False))
    total_trades_high_prob = high_prob_low_count['count'].sum()
    print(f"Total trades จากหุ้นเหล่านี้: {total_trades_high_prob} ({total_trades_high_prob/len(filtered)*100:.1f}% ของทั้งหมด)")

print(f"\n💡 สรุป:")
print(f"   - Prob% ในตาราง = Win Rate ของหุ้นนั้นๆ (ค่าเฉลี่ย)")
print(f"   - แต่ Win Rate โดยรวม = Win Rate ของทุก trades รวมกัน")
print(f"   - ถ้าหุ้นที่มี Count สูงมี Prob% ต่ำ → จะดึง Win Rate โดยรวมลงมา")
print(f"   - ถ้าหุ้นที่มี Prob% สูงมี Count ต่ำ → จะไม่ช่วย Win Rate โดยรวมมาก")

print("\n" + "="*80)

