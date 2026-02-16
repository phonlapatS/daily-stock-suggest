"""
วิเคราะห์: ไทย vs ไต้หวัน
- ไทย: ทายถูกเยอะ แต่ได้กำไรน้อย?
- ไต้หวัน: Prob% น้อย แต่พอทายถูกคือได้เยอะกว่า?
"""
import pandas as pd
import numpy as np

print("="*80)
print("Analysis: THAI vs TAIWAN - Correct vs Profit")
print("="*80)

# Load trades
thai = pd.read_csv('logs/trade_history_THAI.csv')
tw = pd.read_csv('logs/trade_history_TAIWAN.csv')

thai_qual = ['BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
             'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'NEX', 'FORTH',
             'PTG', 'STA', 'PSL', 'MAJOR', 'OR', 'BCH', 'RATCH',
             'TTB', 'TASCO']

tw_qual = [3711, 2330, 2303, 2382]  # ASE, TSMC, UMC, Quanta

thai_f = thai[thai['symbol'].isin(thai_qual)].copy()
tw_f = tw[tw['symbol'].isin(tw_qual)].copy()

# Ensure numeric
thai_f['actual_return'] = pd.to_numeric(thai_f['actual_return'], errors='coerce')
thai_f['correct'] = pd.to_numeric(thai_f['correct'], errors='coerce')
thai_f['pnl'] = thai_f.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

tw_f['actual_return'] = pd.to_numeric(tw_f['actual_return'], errors='coerce')
tw_f['correct'] = pd.to_numeric(tw_f['correct'], errors='coerce')
tw_f['pnl'] = tw_f.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

print("\n[1] THAI Market Analysis")
print("-"*80)

# THAI: When correct vs when incorrect
thai_correct = thai_f[thai_f['correct'] == 1]
thai_incorrect = thai_f[thai_f['correct'] == 0]

print(f"Total trades: {len(thai_f)}")
print(f"Correct: {len(thai_correct)} ({len(thai_correct)/len(thai_f)*100:.1f}%)")
print(f"Incorrect: {len(thai_incorrect)} ({len(thai_incorrect)/len(thai_f)*100:.1f}%)")

print(f"\nWhen CORRECT (forecast == actual):")
thai_correct_profit = thai_correct[thai_correct['pnl'] > 0]
thai_correct_loss = thai_correct[thai_correct['pnl'] <= 0]
print(f"  Profitable: {len(thai_correct_profit)} ({len(thai_correct_profit)/len(thai_correct)*100:.1f}%)")
print(f"  Avg Profit: {thai_correct_profit['pnl'].mean():.2f}%" if len(thai_correct_profit) > 0 else "  Avg Profit: 0.00%")
print(f"  Loss: {len(thai_correct_loss)} ({len(thai_correct_loss)/len(thai_correct)*100:.1f}%)")
print(f"  Avg Loss: {abs(thai_correct_loss['pnl'].mean()):.2f}%" if len(thai_correct_loss) > 0 else "  Avg Loss: 0.00%")
print(f"  Total PnL when correct: {thai_correct['pnl'].sum():.2f}%")
print(f"  Avg PnL per correct trade: {thai_correct['pnl'].mean():.2f}%")

print(f"\nWhen INCORRECT (forecast != actual):")
thai_incorrect_profit = thai_incorrect[thai_incorrect['pnl'] > 0]
thai_incorrect_loss = thai_incorrect[thai_incorrect['pnl'] <= 0]
print(f"  Profitable: {len(thai_incorrect_profit)} ({len(thai_incorrect_profit)/len(thai_incorrect)*100:.1f}%)")
print(f"  Avg Profit: {thai_incorrect_profit['pnl'].mean():.2f}%" if len(thai_incorrect_profit) > 0 else "  Avg Profit: 0.00%")
print(f"  Loss: {len(thai_incorrect_loss)} ({len(thai_incorrect_loss)/len(thai_incorrect)*100:.1f}%)")
print(f"  Avg Loss: {abs(thai_incorrect_loss['pnl'].mean()):.2f}%" if len(thai_incorrect_loss) > 0 else "  Avg Loss: 0.00%")
print(f"  Total PnL when incorrect: {thai_incorrect['pnl'].sum():.2f}%")
print(f"  Avg PnL per incorrect trade: {thai_incorrect['pnl'].mean():.2f}%")

print("\n[2] TAIWAN Market Analysis")
print("-"*80)

# TAIWAN: When correct vs when incorrect
tw_correct = tw_f[tw_f['correct'] == 1]
tw_incorrect = tw_f[tw_f['correct'] == 0]

print(f"Total trades: {len(tw_f)}")
print(f"Correct: {len(tw_correct)} ({len(tw_correct)/len(tw_f)*100:.1f}%)")
print(f"Incorrect: {len(tw_incorrect)} ({len(tw_incorrect)/len(tw_f)*100:.1f}%)")

print(f"\nWhen CORRECT (forecast == actual):")
tw_correct_profit = tw_correct[tw_correct['pnl'] > 0]
tw_correct_loss = tw_correct[tw_correct['pnl'] <= 0]
print(f"  Profitable: {len(tw_correct_profit)} ({len(tw_correct_profit)/len(tw_correct)*100:.1f}%)")
print(f"  Avg Profit: {tw_correct_profit['pnl'].mean():.2f}%" if len(tw_correct_profit) > 0 else "  Avg Profit: 0.00%")
print(f"  Loss: {len(tw_correct_loss)} ({len(tw_correct_loss)/len(tw_correct)*100:.1f}%)")
print(f"  Avg Loss: {abs(tw_correct_loss['pnl'].mean()):.2f}%" if len(tw_correct_loss) > 0 else "  Avg Loss: 0.00%")
print(f"  Total PnL when correct: {tw_correct['pnl'].sum():.2f}%")
print(f"  Avg PnL per correct trade: {tw_correct['pnl'].mean():.2f}%")

print(f"\nWhen INCORRECT (forecast != actual):")
tw_incorrect_profit = tw_incorrect[tw_incorrect['pnl'] > 0]
tw_incorrect_loss = tw_incorrect[tw_incorrect['pnl'] <= 0]
print(f"  Profitable: {len(tw_incorrect_profit)} ({len(tw_incorrect_profit)/len(tw_incorrect)*100:.1f}%)")
print(f"  Avg Profit: {tw_incorrect_profit['pnl'].mean():.2f}%" if len(tw_incorrect_profit) > 0 else "  Avg Profit: 0.00%")
print(f"  Loss: {len(tw_incorrect_loss)} ({len(tw_incorrect_loss)/len(tw_incorrect)*100:.1f}%)")
print(f"  Avg Loss: {abs(tw_incorrect_loss['pnl'].mean()):.2f}%" if len(tw_incorrect_loss) > 0 else "  Avg Loss: 0.00%")
print(f"  Total PnL when incorrect: {tw_incorrect['pnl'].sum():.2f}%")
print(f"  Avg PnL per incorrect trade: {tw_incorrect['pnl'].mean():.2f}%")

print("\n[3] Comparison")
print("-"*80)
print("THAI:")
print(f"  Correct Rate: {len(thai_correct)/len(thai_f)*100:.1f}%")
print(f"  Avg PnL when correct: {thai_correct['pnl'].mean():.2f}%")
print(f"  Profit Rate when correct: {len(thai_correct_profit)/len(thai_correct)*100:.1f}%")

print("\nTAIWAN:")
print(f"  Correct Rate: {len(tw_correct)/len(tw_f)*100:.1f}%")
print(f"  Avg PnL when correct: {tw_correct['pnl'].mean():.2f}%")
print(f"  Profit Rate when correct: {len(tw_correct_profit)/len(tw_correct)*100:.1f}%")

print("\nConclusion:")
print("  - THAI: Correct Rate สูง แต่ Avg PnL when correct ต่ำ (Risk Management ทำให้ขาดทุนแม้ทายถูก)")
print("  - TAIWAN: Correct Rate ต่ำกว่า แต่ Avg PnL when correct สูงกว่า (Risk Management ดีกว่า)")

print("\n" + "="*80)

