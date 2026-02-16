#!/usr/bin/env python
"""
Analyze Current Prob% and Recommend Settings - วิเคราะห์ Prob% ปัจจุบันและแนะนำค่าที่ควรทดสอบ
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_current_prob():
    """วิเคราะห์ Prob% ปัจจุบันและแนะนำค่าที่ควรทดสอบ"""
    
    print("="*100)
    print("Analyze Current Prob% and Recommend Settings")
    print("="*100)
    print()
    
    # Load trade history
    trade_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(trade_file):
        print(f"❌ File not found: {trade_file}")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA")
        return
    
    if not os.path.exists(perf_file):
        print(f"❌ File not found: {perf_file}")
        print("   Please run calculate_metrics first:")
        print("   python scripts/calculate_metrics.py")
        return
    
    # Load data
    df_trades = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    df_perf = pd.read_csv(perf_file, on_bad_lines='skip', engine='python')
    
    print(f"✅ Loaded {len(df_trades)} trades from {trade_file}")
    print(f"✅ Loaded {len(df_perf)} symbols from {perf_file}")
    print()
    
    # Filter China/HK
    china_perf = df_perf[(df_perf['Country'].isin(['CN', 'HK']))].copy()
    display_criteria = china_perf[
        (china_perf['Prob%'] >= 60.0) &
        (china_perf['RR_Ratio'] >= 1.0) &
        (china_perf['Count'] >= 20)
    ]
    
    # Calculate current metrics
    df_trades['correct'] = pd.to_numeric(df_trades['correct'], errors='coerce').fillna(0)
    df_trades['prob'] = pd.to_numeric(df_trades['prob'], errors='coerce').fillna(0)
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce').fillna(0)
    
    total_trades = len(df_trades)
    raw_wins = int(df_trades['correct'].sum())
    raw_prob = (raw_wins / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate RRR
    df_trades['pnl'] = df_trades.apply(
        lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
        axis=1
    )
    wins = df_trades[df_trades['pnl'] > 0]
    losses = df_trades[df_trades['pnl'] <= 0]
    avg_win = wins['pnl'].mean() if not wins.empty else 0
    avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Calculate average Prob% from display criteria
    avg_prob = display_criteria['Prob%'].mean() if len(display_criteria) > 0 else 0
    avg_rrr = display_criteria['RR_Ratio'].mean() if len(display_criteria) > 0 else 0
    total_count = display_criteria['Count'].sum() if len(display_criteria) > 0 else 0
    
    # Analyze prob distribution
    prob_ranges = [
        (0, 50, "0-50%"),
        (50, 54, "50-54%"),
        (54, 55, "54-55%"),
        (55, 56, "55-56%"),
        (56, 60, "56-60%"),
        (60, 65, "60-65%"),
        (65, 70, "65-70%"),
        (70, 100, "70%+")
    ]
    
    print("="*100)
    print("Current Results - ผลลัพธ์ปัจจุบัน")
    print("="*100)
    print()
    print(f"Total Trades: {total_trades}")
    print(f"Raw Prob%: {raw_prob:.1f}%")
    print(f"Avg Prob% (Display Criteria): {avg_prob:.1f}%")
    print(f"Avg RRR: {avg_rrr:.2f}")
    print(f"Number of Stocks: {len(display_criteria)}")
    print(f"Total Count: {total_count}")
    print()
    
    print("="*100)
    print("Prob Distribution - การกระจาย Prob%")
    print("="*100)
    print(f"{'Prob Range':<15} {'Trades':<10} {'Wins':<10} {'Accuracy':<12} {'% of Total':<12}")
    print("-" * 100)
    
    for min_prob, max_prob, label in prob_ranges:
        range_df = df_trades[(df_trades['prob'] >= min_prob) & (df_trades['prob'] < max_prob)].copy()
        if len(range_df) > 0:
            range_trades = len(range_df)
            range_wins = int(range_df['correct'].sum())
            range_acc = (range_wins / range_trades * 100) if range_trades > 0 else 0
            pct_total = (range_trades / total_trades * 100) if total_trades > 0 else 0
            print(f"{label:<15} {range_trades:<10} {range_wins:<10} {range_acc:<12.1f} {pct_total:<12.1f}%")
    
    print()
    
    # Check if Prob% is too high
    print("="*100)
    print("Assessment - การประเมิน")
    print("="*100)
    print()
    
    if raw_prob >= 70.0:
        print("⚠️  WARNING: Raw Prob% is very high (>= 70%)")
        print("   → This may not be realistic for real trading")
        print("   → Real trading may achieve only 60-65% due to:")
        print("      - Slippage and execution delays")
        print("      - Market conditions changes")
        print("      - Psychological factors")
        print("      - Pattern degradation over time")
        print()
        recommendation = "HIGH"
    elif raw_prob >= 65.0:
        print("⚠️  CAUTION: Raw Prob% is high (65-70%)")
        print("   → Still may be optimistic for real trading")
        print("   → Consider reducing to 60-65% for more realistic expectations")
        print()
        recommendation = "MEDIUM"
    elif raw_prob >= 60.0:
        print("✅ GOOD: Raw Prob% is in realistic range (60-65%)")
        print("   → This is a good target for real trading")
        print()
        recommendation = "LOW"
    else:
        print("✅ EXCELLENT: Raw Prob% is conservative (< 60%)")
        print("   → Very realistic for real trading")
        print()
        recommendation = "NONE"
    
    # Recommendations
    print("="*100)
    print("Recommendations - คำแนะนำ")
    print("="*100)
    print()
    
    if recommendation == "HIGH":
        print("🎯 Goal: Reduce Prob% from {:.1f}% to 60-65%".format(raw_prob))
        print()
        print("Strategy 1: Increase threshold_multiplier (Most Effective)")
        print("   → Makes pattern detection more strict")
        print("   → Will reduce number of trades but improve quality")
        print("   → Recommended values:")
        print("      - threshold_multiplier: 1.0 (from 0.9)")
        print("      - threshold_multiplier: 1.1 (more aggressive)")
        print()
        print("Strategy 2: Increase min_stats")
        print("   → Requires patterns to have more historical occurrences")
        print("   → Will filter out less reliable patterns")
        print("   → Recommended values:")
        print("      - min_stats: 35 (from 30)")
        print("      - min_stats: 40 (more aggressive)")
        print()
        print("Strategy 3: Combined Approach (Recommended)")
        print("   → Combine threshold_multiplier + min_stats")
        print("   → Most balanced approach")
        print("   → Recommended combinations:")
        print("      1. threshold_multiplier=1.0, min_stats=35, min_prob=54.0")
        print("      2. threshold_multiplier=1.0, min_stats=40, min_prob=54.0")
        print("      3. threshold_multiplier=1.1, min_stats=35, min_prob=54.0")
        print()
        print("⚠️  Note: Increasing min_prob (gatekeeper) may not help much")
        print("   → Gatekeeper only filters trades, doesn't change pattern quality")
        print("   → Focus on threshold_multiplier and min_stats instead")
        print()
    elif recommendation == "MEDIUM":
        print("🎯 Goal: Reduce Prob% from {:.1f}% to 60-65%".format(raw_prob))
        print()
        print("Strategy: Slight increase in threshold_multiplier or min_stats")
        print("   → Recommended values:")
        print("      - threshold_multiplier: 1.0 (from 0.9)")
        print("      - OR min_stats: 35 (from 30)")
        print()
    else:
        print("✅ Current Prob% is already in good range")
        print("   → No major adjustments needed")
        print("   → May consider fine-tuning if needed")
        print()
    
    # Test commands
    print("="*100)
    print("Test Commands - คำสั่งทดสอบ")
    print("="*100)
    print()
    
    if recommendation in ["HIGH", "MEDIUM"]:
        print("Quick Test (ทดสอบเฉพาะค่าที่สำคัญ):")
        print("   python scripts/test_china_realistic_prob_quick.py")
        print()
        print("Full Test (ทดสอบทุกค่า):")
        print("   python scripts/test_china_realistic_prob.py")
        print()
        print("Manual Test (ทดสอบทีละค่า):")
        print("   # Test 1: threshold_multiplier=1.0")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --multiplier 1.0 --min_stats 30 --min_prob 54.0")
        print("   python scripts/calculate_metrics.py")
        print()
        print("   # Test 2: min_stats=35")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --multiplier 0.9 --min_stats 35 --min_prob 54.0")
        print("   python scripts/calculate_metrics.py")
        print()
        print("   # Test 3: Combined")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --multiplier 1.0 --min_stats 35 --min_prob 54.0")
        print("   python scripts/calculate_metrics.py")
        print()
    else:
        print("✅ Current settings are good, no testing needed")
        print()
    
    # Expected impact
    print("="*100)
    print("Expected Impact - ผลกระทบที่คาดหวัง")
    print("="*100)
    print()
    
    if recommendation in ["HIGH", "MEDIUM"]:
        print("When increasing threshold_multiplier or min_stats:")
        print("   ✅ Prob% should decrease (more realistic)")
        print("   ⚠️  Number of trades may decrease")
        print("   ⚠️  Number of stocks may decrease")
        print("   ✅ RRR should remain stable or improve")
        print()
        print("Target Metrics:")
        print("   - Raw Prob%: 60-65% (realistic for real trading)")
        print("   - Avg RRR: >= 1.40 (maintain current level)")
        print("   - Stocks: >= 4 (maintain current level)")
        print("   - Count: >= 20 per stock (maintain current level)")
        print()

if __name__ == "__main__":
    analyze_current_prob()

