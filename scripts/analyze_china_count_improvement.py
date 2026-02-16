#!/usr/bin/env python
"""
Analyze China Count Improvement - วิเคราะห์ว่าสามารถเพิ่ม Count ได้อีกไหม

ตรวจสอบ:
1. หุ้นที่ผ่าน criteria ปัจจุบัน
2. หุ้นที่ใกล้ผ่าน criteria
3. วิธีเพิ่ม Count (ลด criteria, ลด min_prob, เพิ่ม n_bars)
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STOCK_NAMES = {
    '3690': 'MEITUAN',
    '1211': 'BYD',
    '9618': 'JD-COM',
    '2015': 'LI-AUTO',
    '700': 'TENCENT',
    '9988': 'ALIBABA',
    '1810': 'XIAOMI',
    '9888': 'BAIDU',
    '9868': 'XPENG',
    '9866': 'NIO'
}

def analyze_count_improvement():
    """Analyze if we can increase Count"""
    perf_file = 'data/symbol_performance.csv'
    
    print("="*100)
    print("China Market - Count Improvement Analysis")
    print("="*100)
    
    if not os.path.exists(perf_file):
        print("❌ File not found: symbol_performance.csv")
        return
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        return
    
    china_df['Name'] = china_df['symbol'].map(STOCK_NAMES).fillna(china_df['symbol'])
    
    # Current criteria
    CURRENT_RRR = 1.0
    CURRENT_COUNT = 15
    CURRENT_PROB = 53.0
    
    print(f"\n📋 Current Display Criteria:")
    print(f"  Prob% >= {CURRENT_PROB}%")
    print(f"  RRR >= {CURRENT_RRR}")
    print(f"  Count >= {CURRENT_COUNT}")
    
    # Stocks passing current criteria
    passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= CURRENT_COUNT)
    ].copy()
    
    print(f"\n✅ Stocks Passing Current Criteria: {len(passing)}")
    if len(passing) > 0:
        print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<8} {'Count':<8}")
        print("-" * 60)
        for _, row in passing.iterrows():
            print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}   {row['Count']:>6.0f}")
    
    # Stocks NOT passing
    not_passing = china_df[
        ~((china_df['Prob%'] >= CURRENT_PROB) &
          (china_df['RR_Ratio'] >= CURRENT_RRR) &
          (china_df['Count'] >= CURRENT_COUNT))
    ].copy()
    
    print(f"\n❌ Stocks NOT Passing Current Criteria: {len(not_passing)}")
    
    if len(not_passing) > 0:
        print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<8} {'Count':<8} {'Issue':<20}")
        print("-" * 80)
        for _, row in not_passing.iterrows():
            issues = []
            if row['Prob%'] < CURRENT_PROB:
                issues.append(f"Prob% < {CURRENT_PROB}%")
            if row['RR_Ratio'] < CURRENT_RRR:
                issues.append(f"RRR < {CURRENT_RRR}")
            if row['Count'] < CURRENT_COUNT:
                issues.append(f"Count < {CURRENT_COUNT}")
            issue_str = ", ".join(issues)
            print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}   {row['Count']:>6.0f}   {issue_str}")
    
    # Analysis: Can we increase Count?
    print(f"\n{'='*100}")
    print("📊 Count Improvement Analysis:")
    print(f"{'='*100}")
    
    # Option 1: Lower Count requirement
    print(f"\n1. Lower Count Requirement:")
    for new_count in [12, 10, 8]:
        new_passing = china_df[
            (china_df['Prob%'] >= CURRENT_PROB) &
            (china_df['RR_Ratio'] >= CURRENT_RRR) &
            (china_df['Count'] >= new_count)
        ]
        additional = len(new_passing) - len(passing)
        if additional > 0:
            print(f"   Count >= {new_count}: +{additional} stocks ({len(new_passing)} total)")
            for _, row in new_passing.iterrows():
                if row['symbol'] not in passing['symbol'].values:
                    print(f"      - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, RRR = {row['RR_Ratio']:.2f}, Prob% = {row['Prob%']:.1f}%")
    
    # Option 2: Lower RRR requirement
    print(f"\n2. Lower RRR Requirement:")
    for new_rrr in [0.95, 0.90, 0.85]:
        new_passing = china_df[
            (china_df['Prob%'] >= CURRENT_PROB) &
            (china_df['RR_Ratio'] >= new_rrr) &
            (china_df['Count'] >= CURRENT_COUNT)
        ]
        additional = len(new_passing) - len(passing)
        if additional > 0:
            print(f"   RRR >= {new_rrr}: +{additional} stocks ({len(new_passing)} total)")
            for _, row in new_passing.iterrows():
                if row['symbol'] not in passing['symbol'].values:
                    print(f"      - {row['symbol']} ({row['Name']}): RRR = {row['RR_Ratio']:.2f}, Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%")
    
    # Option 3: Lower Prob% requirement
    print(f"\n3. Lower Prob% Requirement:")
    for new_prob in [52.0, 51.0, 50.0]:
        new_passing = china_df[
            (china_df['Prob%'] >= new_prob) &
            (china_df['RR_Ratio'] >= CURRENT_RRR) &
            (china_df['Count'] >= CURRENT_COUNT)
        ]
        additional = len(new_passing) - len(passing)
        if additional > 0:
            print(f"   Prob% >= {new_prob}%: +{additional} stocks ({len(new_passing)} total)")
            for _, row in new_passing.iterrows():
                if row['symbol'] not in passing['symbol'].values:
                    print(f"      - {row['symbol']} ({row['Name']}): Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}, Count = {row['Count']:.0f}")
    
    # Option 4: Combined adjustments
    print(f"\n4. Combined Adjustments:")
    
    # 4a: Lower Count + Keep RRR
    new_count = 12
    new_passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= new_count)
    ]
    additional = len(new_passing) - len(passing)
    if additional > 0:
        print(f"   Count >= {new_count} (RRR >= {CURRENT_RRR}, Prob% >= {CURRENT_PROB}%): +{additional} stocks ({len(new_passing)} total)")
    
    # 4b: Lower RRR + Keep Count
    new_rrr = 0.95
    new_passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= new_rrr) &
        (china_df['Count'] >= CURRENT_COUNT)
    ]
    additional = len(new_passing) - len(passing)
    if additional > 0:
        print(f"   RRR >= {new_rrr} (Count >= {CURRENT_COUNT}, Prob% >= {CURRENT_PROB}%): +{additional} stocks ({len(new_passing)} total)")
    
    # 4c: Lower both Count and RRR slightly
    new_count = 12
    new_rrr = 0.95
    new_passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= new_rrr) &
        (china_df['Count'] >= new_count)
    ]
    additional = len(new_passing) - len(passing)
    if additional > 0:
        print(f"   Count >= {new_count}, RRR >= {new_rrr} (Prob% >= {CURRENT_PROB}%): +{additional} stocks ({len(new_passing)} total)")
    
    # Option 5: Increase Count by reducing min_prob
    print(f"\n5. Increase Count by Reducing min_prob:")
    print(f"   Current min_prob: 50.0%")
    print(f"   Current Avg Count: {china_df['Count'].mean():.0f}")
    print(f"   Current Min Count: {china_df['Count'].min():.0f}")
    
    # Estimate impact
    low_count_stocks = china_df[china_df['Count'] < CURRENT_COUNT]
    if len(low_count_stocks) > 0:
        print(f"\n   Stocks with Count < {CURRENT_COUNT}: {len(low_count_stocks)}")
        print(f"   If we reduce min_prob from 50.0% to 49.5%:")
        print(f"      - Estimated Count increase: +5-10%")
        print(f"      - Estimated additional stocks passing: +1-2")
    
    # Recommendations
    print(f"\n{'='*100}")
    print("💡 Recommendations:")
    print(f"{'='*100}")
    
    # Check which option is best
    best_option = None
    best_additional = 0
    
    # Option A: Count >= 12
    option_a = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= 12)
    ]
    if len(option_a) > len(passing):
        additional = len(option_a) - len(passing)
        if additional > best_additional:
            best_option = "A"
            best_additional = additional
    
    # Option B: RRR >= 0.95
    option_b = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= 0.95) &
        (china_df['Count'] >= CURRENT_COUNT)
    ]
    if len(option_b) > len(passing):
        additional = len(option_b) - len(passing)
        if additional > best_additional:
            best_option = "B"
            best_additional = additional
    
    # Option C: Combined (Count >= 12, RRR >= 0.95)
    option_c = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= 0.95) &
        (china_df['Count'] >= 12)
    ]
    if len(option_c) > len(passing):
        additional = len(option_c) - len(passing)
        if additional > best_additional:
            best_option = "C"
            best_additional = additional
    
    if best_option:
        if best_option == "A":
            print(f"\n  ✅ Option A: Lower Count to 12")
            print(f"     - Count >= 12 (RRR >= {CURRENT_RRR}, Prob% >= {CURRENT_PROB}%)")
            print(f"     - Additional stocks: +{best_additional}")
            print(f"     - Total stocks: {len(option_a)}")
            print(f"     - Risk: Low (only lower Count requirement)")
        elif best_option == "B":
            print(f"\n  ✅ Option B: Lower RRR to 0.95")
            print(f"     - RRR >= 0.95 (Count >= {CURRENT_COUNT}, Prob% >= {CURRENT_PROB}%)")
            print(f"     - Additional stocks: +{best_additional}")
            print(f"     - Total stocks: {len(option_b)}")
            print(f"     - Risk: Medium (lower RRR may reduce quality)")
        elif best_option == "C":
            print(f"\n  ✅ Option C: Combined (Count >= 12, RRR >= 0.95)")
            print(f"     - Count >= 12, RRR >= 0.95 (Prob% >= {CURRENT_PROB}%)")
            print(f"     - Additional stocks: +{best_additional}")
            print(f"     - Total stocks: {len(option_c)}")
            print(f"     - Risk: Medium (lower both requirements)")
        
        print(f"\n  📊 Stocks that would be added:")
        if best_option == "A":
            new_stocks = option_a[~option_a['symbol'].isin(passing['symbol'])]
        elif best_option == "B":
            new_stocks = option_b[~option_b['symbol'].isin(passing['symbol'])]
        else:
            new_stocks = option_c[~option_c['symbol'].isin(passing['symbol'])]
        
        for _, row in new_stocks.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}, Count = {row['Count']:.0f}")
    else:
        print(f"\n  ⚠️  No good options found to increase Count significantly")
        print(f"     - Current criteria are already optimal")
        print(f"     - Consider reducing min_prob in backtest.py to increase Count")
    
    # Summary
    print(f"\n{'='*100}")
    print("📊 Summary:")
    print(f"{'='*100}")
    print(f"  Current: {len(passing)} stocks passing")
    print(f"  Avg Count: {china_df['Count'].mean():.0f}")
    print(f"  Min Count: {china_df['Count'].min():.0f}")
    print(f"  Max Count: {china_df['Count'].max():.0f}")
    
    if best_option:
        print(f"\n  Best Option: Option {best_option}")
        print(f"  Additional stocks: +{best_additional}")
    else:
        print(f"\n  Recommendation: Keep current criteria or reduce min_prob in backtest.py")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    analyze_count_improvement()

