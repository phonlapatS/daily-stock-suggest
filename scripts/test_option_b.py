#!/usr/bin/env python
"""Test Option B: RRR >= 1.25, Count <= 400"""
import pandas as pd

df = pd.read_csv('data/symbol_performance.csv')
tw = df[df['Country'] == 'TW']

# Option B criteria: Keep RRR 1.25, increase Count to 400
test = tw[
    (tw['Prob%'] >= 53) & 
    (tw['RR_Ratio'] >= 1.25) & 
    (tw['Count'] >= 25) & 
    (tw['Count'] <= 400)
]

print('='*80)
print('Option B Test Results: RRR >= 1.25, Count <= 400')
print('='*80)
print(f'\nTotal Passing: {len(test)} stocks')

if not test.empty:
    print('\nDetails:')
    print(test[['symbol', 'Prob%', 'RR_Ratio', 'Count', 'AvgWin%', 'AvgLoss%']].to_string(index=False))
    
    print(f'\nAverage Metrics:')
    print(f'  Avg Prob%: {test["Prob%"].mean():.2f}%')
    print(f'  Avg RRR: {test["RR_Ratio"].mean():.2f}')
    print(f'  Avg Count: {test["Count"].mean():.1f}')
    print(f'  Total Trades: {test["Count"].sum():.0f}')
    
    print(f'\nQuality Check:')
    print(f'  Stocks with Prob >= 60%: {len(test[test["Prob%"] >= 60])}')
    print(f'  Stocks with RRR >= 1.5: {len(test[test["RR_Ratio"] >= 1.5])}')
    print(f'  Stocks with Count > 200: {len(test[test["Count"] > 200])} (over-trading risk)')
    print(f'  Stocks with Count > 300: {len(test[test["Count"] > 300])} (high over-trading risk)')
    
    print(f'\nOver-trading Analysis:')
    high_count = test[test['Count'] > 200]
    if not high_count.empty:
        print(f'  Stocks with Count > 200:')
        for _, row in high_count.iterrows():
            print(f'    {row["symbol"]}: Count {row["Count"]:.0f}, Prob {row["Prob%"]:.1f}%, RRR {row["RR_Ratio"]:.2f}')
            print(f'      → Over-trading risk: {"HIGH" if row["Count"] > 300 else "MODERATE"}')
    
    print(f'\nRisk Assessment:')
    avg_prob = test["Prob%"].mean()
    avg_rrr = test["RR_Ratio"].mean()
    high_count_ratio = len(test[test["Count"] > 200]) / len(test) * 100
    very_high_count_ratio = len(test[test["Count"] > 300]) / len(test) * 100
    
    print(f'  Average Prob%: {avg_prob:.2f}% {"✅ Good" if avg_prob >= 60 else "⚠️ Moderate" if avg_prob >= 55 else "❌ Low"}')
    print(f'  Average RRR: {avg_rrr:.2f} {"✅ Good" if avg_rrr >= 1.5 else "⚠️ Moderate" if avg_rrr >= 1.3 else "❌ Low"}')
    print(f'  Over-trading Risk (>200): {high_count_ratio:.1f}% {"⚠️ High" if high_count_ratio > 50 else "✅ Low" if high_count_ratio < 30 else "⚠️ Moderate"}')
    print(f'  High Over-trading Risk (>300): {very_high_count_ratio:.1f}% {"❌ Very High" if very_high_count_ratio > 30 else "⚠️ High" if very_high_count_ratio > 0 else "✅ None"}')
    
    print(f'\nOverfitting Risk Assessment:')
    # Overfitting risk: High count + High Prob% might indicate overfitting
    potential_overfit = test[(test['Count'] > 200) & (test['Prob%'] > 65)]
    if not potential_overfit.empty:
        print(f'  Potential Overfitting (Count > 200, Prob > 65%):')
        for _, row in potential_overfit.iterrows():
            print(f'    {row["symbol"]}: Count {row["Count"]:.0f}, Prob {row["Prob%"]:.1f}%')
            print(f'      → Risk: {"HIGH" if row["Count"] > 300 else "MODERATE"}')
    else:
        print(f'  ✅ No obvious overfitting risk')
    
    print(f'\nRecommendation:')
    if avg_prob >= 60 and avg_rrr >= 1.5 and high_count_ratio < 30 and very_high_count_ratio == 0:
        print('  ✅ GOOD - Quality is acceptable, over-trading risk is low')
    elif avg_prob >= 55 and avg_rrr >= 1.3 and high_count_ratio < 50 and very_high_count_ratio < 30:
        print('  ⚠️ MODERATE - Quality is acceptable but monitor over-trading/overfitting')
    else:
        print('  ❌ POOR - Quality is low or over-trading/overfitting risk is high')
else:
    print('\nNo stocks passing criteria')

