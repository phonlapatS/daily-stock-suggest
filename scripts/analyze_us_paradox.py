#!/usr/bin/env python
"""
analyze_us_paradox.py - Investigate US Market Paradox
======================================================
Analyze why "Mean Reversion" appears to work in US trending markets.
Hypothesis: It's NOT Mean Reversion, but "Failed Breakout" detection.
"""
import pandas as pd
import numpy as np
import os
import sys

def analyze_trend_context(trade_history_path='logs/trade_history.csv'):
    """
    Verify if 'Mean Reversion' signals actually align with pullbacks
    in a larger uptrend (i.e., they're Trend Following in disguise).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(trade_history_path):
        trade_history_path = os.path.join(base_dir, trade_history_path)
    
    if not os.path.exists(trade_history_path):
        print(f"❌ File not found: {trade_history_path}")
        print("   Run backtest first: python scripts/backtest.py --quick")
        return
    
    df = pd.read_csv(trade_history_path)
    
    # Filter US stocks only
    us_stocks = df[df['symbol'].isin(['NVDA', 'AAPL', 'TSLA', 'MSFT', 'GOOGL'])]
    
    if len(us_stocks) == 0:
        print("❌ No US stocks found in trade history")
        return
    
    print("\n" + "=" * 70)
    print("🔬 US MARKET PARADOX ANALYSIS")
    print("=" * 70)
    print(f"Total US trades: {len(us_stocks)}")
    print(f"Stocks: {us_stocks['symbol'].unique().tolist()}")
    
    # Group by pattern
    pattern_analysis = us_stocks.groupby(['pattern', 'forecast']).agg({
        'correct': ['sum', 'count', 'mean'],
        'actual_return': 'mean'
    }).reset_index()
    
    pattern_analysis.columns = ['pattern', 'forecast', 'wins', 'total', 'accuracy', 'avg_return']
    pattern_analysis['accuracy_pct'] = (pattern_analysis['accuracy'] * 100).round(1)
    
    print(f"\n📊 PATTERN PERFORMANCE BREAKDOWN")
    print("-" * 70)
    print(f"{'Pattern':<10} {'Forecast':<10} {'Total':<8} {'Wins':<8} {'Acc%':<8} {'Avg Return':<12}")
    print("-" * 70)
    
    for _, row in pattern_analysis.sort_values('accuracy', ascending=False).iterrows():
        icon = "✅" if row['accuracy_pct'] > 60 else "⚠️" if row['accuracy_pct'] > 50 else "❌"
        print(f"{row['pattern']:<10} {row['forecast']:<10} {int(row['total']):<8} {int(row['wins']):<8} {row['accuracy_pct']:<8.1f} {row['avg_return']:<12.2f}% {icon}")
    
    # Hypothesis Test: Are "DOWN" forecasts after "+++" actually catching failed rallies?
    print("\n" + "=" * 70)
    print("📊 HYPOTHESIS TEST: Mean Reversion vs Failed Breakout")
    print("=" * 70)
    
    # Pattern: +++ or ++++ (Multiple Up Days) → Forecast DOWN
    mean_reversion_signals = us_stocks[
        (us_stocks['pattern'].str.contains(r'\+{3,}', regex=True)) &  # 3+ up days
        (us_stocks['forecast'] == 'DOWN')
    ]
    
    if len(mean_reversion_signals) > 0:
        mr_accuracy = (mean_reversion_signals['correct'].sum() / len(mean_reversion_signals)) * 100
        mr_avg_return = mean_reversion_signals['actual_return'].mean()
        
        print(f"\n🔴 'Mean Reversion' Signals (+++/++++ → DOWN):")
        print(f"   Total: {len(mean_reversion_signals)}")
        print(f"   Accuracy: {mr_accuracy:.1f}%")
        print(f"   Avg Return: {mr_avg_return:.2f}%")
        
        if mr_accuracy < 50:
            print("\n   ❌ VERDICT: Mean Reversion FAILS in US Market")
            print("      → System is NOT exploiting pullbacks in uptrends")
            print("      → It's getting whipsawed by trend continuation")
        else:
            print("\n   ✅ VERDICT: Mean Reversion works (unexpected!)")
    else:
        print("\n   ⚠️ No Mean Reversion signals found")
    
    # Pattern: -++ (Dip → Recovery) → Forecast DOWN
    failed_breakout_signals = us_stocks[
        (us_stocks['pattern'] == '-++') &
        (us_stocks['forecast'] == 'DOWN')
    ]
    
    if len(failed_breakout_signals) > 0:
        fb_accuracy = (failed_breakout_signals['correct'].sum() / len(failed_breakout_signals)) * 100
        fb_avg_return = failed_breakout_signals['actual_return'].mean()
        
        print(f"\n🟢 'Failed Breakout' Signals (-++ → DOWN):")
        print(f"   Total: {len(failed_breakout_signals)}")
        print(f"   Accuracy: {fb_accuracy:.1f}%")
        print(f"   Avg Return: {fb_avg_return:.2f}%")
        
        if fb_accuracy > 70:
            print("\n   ✅ VERDICT: This pattern works!")
            print("      → NOT Mean Reversion, it's a 'Weak Rally Rejection' pattern")
            print("      → System catches failed attempts to recover from dips")
        else:
            print("\n   ⚠️ VERDICT: Pattern needs more data or doesn't work")
    else:
        print("\n   ⚠️ No Failed Breakout signals found")
    
    # Overall US Market Performance
    print("\n" + "=" * 70)
    print("📈 OVERALL US MARKET PERFORMANCE")
    print("=" * 70)
    
    total_us = len(us_stocks)
    correct_us = us_stocks['correct'].sum()
    accuracy_us = (correct_us / total_us) * 100
    
    print(f"Total Trades: {total_us}")
    print(f"Correct: {correct_us}")
    print(f"Accuracy: {accuracy_us:.1f}%")
    
    if accuracy_us < 55:
        print("\n⚠️ WARNING: US Market accuracy is below 55%")
        print("   → After commissions (~0.5%), this is UNPROFITABLE")
        print("   → Recommendation: STOP trading US stocks with current logic")
    
    # Compare with Thai Market
    thai_stocks = df[df['symbol'].isin(['PTT', 'ADVANC', 'CPALL', 'AOT', 'KBANK'])]
    
    if len(thai_stocks) > 0:
        total_thai = len(thai_stocks)
        correct_thai = thai_stocks['correct'].sum()
        accuracy_thai = (correct_thai / total_thai) * 100
        
        print(f"\n🇹🇭 THAI MARKET COMPARISON:")
        print(f"   Total Trades: {total_thai}")
        print(f"   Accuracy: {accuracy_thai:.1f}%")
        print(f"   Difference: {accuracy_thai - accuracy_us:+.1f}%")
        
        if accuracy_thai > accuracy_us + 5:
            print("\n   ✅ Thai market performs significantly better")
            print("      → Focus on Thai stocks for Mean Reversion strategy")

if __name__ == "__main__":
    analyze_trend_context()
