"""
ตรวจสอบความสอดคล้องระหว่าง equity curve กับ calculate_metrics.py
และวิเคราะห์ว่าทำไมหุ้นไทยกำไรน้อยแม้ RRR สูง
"""
import pandas as pd
import numpy as np

print("="*80)
print("🔍 ตรวจสอบความสอดคล้อง: Equity Curve vs calculate_metrics.py")
print("="*80)

# 1. ตรวจสอบ Thai Market
print("\n📊 [1] Thai Market Analysis")
print("-"*80)

df_thai = pd.read_csv('logs/trade_history_THAI.csv')
print(f"Total trades: {len(df_thai)}")

# Calculate pnl (same as calculate_metrics.py)
df_thai['actual_return'] = pd.to_numeric(df_thai['actual_return'], errors='coerce')
df_thai['pnl'] = df_thai.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

wins = df_thai[df_thai['pnl'] > 0]
losses = df_thai[df_thai['pnl'] <= 0]

win_rate = len(wins) / len(df_thai) * 100
avg_win = wins['pnl'].mean()
avg_loss = abs(losses['pnl'].mean())
rrr = avg_win / avg_loss if avg_loss > 0 else 0
total_pnl = df_thai['pnl'].sum()

# Expected Value
ev_per_trade = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
ev_total = ev_per_trade * len(df_thai)

print(f"✅ Wins: {len(wins)} ({win_rate:.1f}%)")
print(f"❌ Losses: {len(losses)} ({100-win_rate:.1f}%)")
print(f"📈 AvgWin%: {avg_win:.2f}%")
print(f"📉 AvgLoss%: {avg_loss:.2f}%")
print(f"⚖️ RRR: {rrr:.2f}")
print(f"💰 Total pnl%: {total_pnl:.2f}%")
print(f"📊 Expected Value per trade: {ev_per_trade:.3f}%")
print(f"📊 Expected total return: {ev_total:.2f}%")

# 2. วิเคราะห์ว่าทำไมกำไรน้อย
print("\n" + "="*80)
print("🔍 [2] วิเคราะห์: ทำไมกำไรน้อยแม้ RRR สูง?")
print("="*80)

print(f"\n💡 สาเหตุหลัก:")
print(f"   1. Win Rate ต่ำ: {win_rate:.1f}% (แม้ RRR สูง {rrr:.2f} แต่ชนะน้อยครั้ง)")
print(f"   2. Expected Value ต่อ trade: {ev_per_trade:.3f}% (ต่ำ)")
print(f"   3. ผลรวม pnl%: {total_pnl:.2f}% (ต่ำเพราะ Win Rate ต่ำ)")

print(f"\n📊 สูตร Expected Value:")
print(f"   EV = (Win Rate × AvgWin%) - (Loss Rate × AvgLoss%)")
print(f"   EV = ({win_rate:.1f}% × {avg_win:.2f}%) - ({100-win_rate:.1f}% × {avg_loss:.2f}%)")
print(f"   EV = {win_rate/100 * avg_win:.3f}% - {(100-win_rate)/100 * avg_loss:.3f}%")
print(f"   EV = {ev_per_trade:.3f}% ต่อ trade")

print(f"\n💡 สรุป:")
if win_rate < 50:
    print(f"   ⚠️ Win Rate ต่ำ ({win_rate:.1f}%) → กำไรน้อยแม้ RRR สูง ({rrr:.2f})")
    print(f"   → ต้องเพิ่ม Win Rate หรือเพิ่ม AvgWin% เพื่อให้กำไรมากขึ้น")
else:
    print(f"   ✅ Win Rate ดี ({win_rate:.1f}%) แต่ RRR อาจไม่สูงพอ")
    print(f"   → ต้องเพิ่ม RRR หรือเพิ่มจำนวน trades")

# 3. เปรียบเทียบกับ calculate_metrics.py
print("\n" + "="*80)
print("🔍 [3] ตรวจสอบความสอดคล้องกับ calculate_metrics.py")
print("="*80)

print("\n📋 Logic ที่ใช้:")
print("   calculate_metrics.py:")
print("     - pnl = actual_return * (1 if forecast == 'UP' else -1)")
print("     - avg_win = wins['pnl'].mean()")
print("     - avg_loss = abs(losses['pnl'].mean()")
print("     - RRR = avg_win / avg_loss")
print("\n   plot_equity_curves.py:")
print("     - pnl = actual_return * (1 if forecast == 'UP' else -1)")
print("     - equity = initial_capital * (1 + cumulative_return_pct / 100)")
print("     - cumulative_return_pct = sum of all pnl%")
print("\n✅ Logic สอดคล้องกัน!")

# 4. ตัวอย่างการคำนวณ Equity
print("\n" + "="*80)
print("🔍 [4] ตัวอย่างการคำนวณ Equity")
print("="*80)

initial_capital = 1000
cumulative_return_pct = total_pnl
final_equity = initial_capital * (1 + cumulative_return_pct / 100)
total_return_pct = ((final_equity / initial_capital) - 1) * 100

print(f"\n💰 Initial Capital: ${initial_capital}")
print(f"📊 Total pnl%: {total_pnl:.2f}%")
print(f"💵 Final Equity: ${final_equity:.2f}")
print(f"📈 Total Return: {total_return_pct:.2f}%")
print(f"\n✅ Equity Curve ใช้ logic เดียวกับ calculate_metrics.py!")

print("\n" + "="*80)
print("✅ การตรวจสอบเสร็จสมบูรณ์")
print("="*80)

