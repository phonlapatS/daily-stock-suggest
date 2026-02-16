"""
ตรวจสอบว่าทำไม Prob% ในตาราง (68.8% สำหรับ JTS) ถึงต่างจาก Profit Rate (32.5%)
"""
import pandas as pd
import numpy as np

print("="*80)
print("Check: Why Prob% in table (68.8% for JTS) differs from Profit Rate (32.5%)?")
print("="*80)

# Load Thai trades
df = pd.read_csv('logs/trade_history_THAI.csv')

# Analyze JTS and ICHI
symbols_to_check = ['JTS', 'ICHI']

for symbol in symbols_to_check:
    sym_trades = df[df['symbol'] == symbol].copy()
    if len(sym_trades) == 0:
        print(f"\n{symbol}: No trades found")
        continue
    
    print(f"\n=== {symbol} Analysis ===")
    print("-"*80)
    print(f"Total trades: {len(sym_trades)}")
    
    # Ensure numeric
    sym_trades['actual_return'] = pd.to_numeric(sym_trades['actual_return'], errors='coerce')
    sym_trades['correct'] = pd.to_numeric(sym_trades['correct'], errors='coerce')
    
    # Calculate Prob% (Correct Rate) - same as calculate_metrics.py
    correct_count = (sym_trades['correct'] == 1).sum()
    correct_rate = (correct_count / len(sym_trades)) * 100
    
    # Calculate Profit Rate (PnL > 0)
    sym_trades['pnl'] = sym_trades.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
    profit_count = (sym_trades['pnl'] > 0).sum()
    profit_rate = (profit_count / len(sym_trades)) * 100
    
    print(f"\n[1] Prob% Calculation (as in calculate_metrics.py):")
    print(f"    Correct (forecast == actual): {correct_count} ({correct_rate:.1f}%)")
    print(f"    This is what shows in the table as 'Prob%'")
    
    print(f"\n[2] Profit Rate Calculation (PnL > 0):")
    print(f"    Profit (PnL > 0): {profit_count} ({profit_rate:.1f}%)")
    print(f"    This is what we use in equity curve analysis")
    
    print(f"\n[3] Difference:")
    print(f"    Prob% (Correct Rate): {correct_rate:.1f}%")
    print(f"    Profit Rate: {profit_rate:.1f}%")
    print(f"    Difference: {correct_rate - profit_rate:.1f}%")
    
    # Show examples of trades that are correct but not profitable
    correct_not_profit = sym_trades[(sym_trades['correct'] == 1) & (sym_trades['pnl'] <= 0)]
    print(f"\n[4] Trades that are CORRECT but NOT PROFITABLE:")
    print(f"    Count: {len(correct_not_profit)} ({len(correct_not_profit)/len(sym_trades)*100:.1f}%)")
    if len(correct_not_profit) > 0:
        print(f"    Avg PnL: {correct_not_profit['pnl'].mean():.2f}%")
        print(f"    Example: Forecast correct but hit SL before TP")
    
    # Show examples of trades that are incorrect but profitable
    incorrect_but_profit = sym_trades[(sym_trades['correct'] == 0) & (sym_trades['pnl'] > 0)]
    print(f"\n[5] Trades that are INCORRECT but PROFITABLE:")
    print(f"    Count: {len(incorrect_but_profit)} ({len(incorrect_but_profit)/len(sym_trades)*100:.1f}%)")
    if len(incorrect_but_profit) > 0:
        print(f"    Avg PnL: {incorrect_but_profit['pnl'].mean():.2f}%")
        print(f"    Example: Forecast wrong but still profitable (e.g., hit TP before reversal)")

print("\n" + "="*80)
print("Conclusion:")
print("  - Prob% in table = Correct Rate (forecast == actual)")
print("  - Profit Rate = PnL > 0 (actual profit after Risk Management)")
print("  - They can differ because Risk Management (SL/TP) affects profitability")
print("  - Even if forecast is correct, you can still lose money if hit SL")
print("="*80)

