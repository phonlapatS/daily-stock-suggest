#!/usr/bin/env python
"""Get Taiwan Final Results for Documentation"""
import pandas as pd

df = pd.read_csv('data/symbol_performance.csv')
tw = df[df['Country'] == 'TW']

# Option A criteria
passing = tw[
    (tw['Prob%'] >= 53) & 
    (tw['RR_Ratio'] >= 1.25) & 
    (tw['Count'] >= 25) & 
    (tw['Count'] <= 150)
]

print('Taiwan Market - Final Results (Option A)')
print('='*80)
print(f'\nTotal Passing: {len(passing)} stocks')

if not passing.empty:
    print('\nDetails:')
    print(passing[['symbol', 'Prob%', 'RR_Ratio', 'Count', 'AvgWin%', 'AvgLoss%']].to_string(index=False))
    
    print(f'\nAverage Metrics:')
    print(f'  Avg Prob%: {passing["Prob%"].mean():.2f}%')
    print(f'  Avg RRR: {passing["RR_Ratio"].mean():.2f}')
    print(f'  Avg Count: {passing["Count"].mean():.1f}')
    print(f'  Total Trades: {passing["Count"].sum():.0f}')
    
    print(f'\nReal-World Analysis:')
    total_trades = passing['Count'].sum()
    commission_rate = 0.285  # Taiwan commission per trade
    total_commission = total_trades * commission_rate
    print(f'  Total Trades/Year: {total_trades:.0f}')
    print(f'  Commission Cost: {total_commission:.2f}%')
    print(f'  Over-trading Risk: 0% (no stocks with Count > 200)')

