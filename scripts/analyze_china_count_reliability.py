#!/usr/bin/env python
"""
Analyze China Count Reliability - วิเคราะห์ความน่าเชื่อถือทางสถิติของ Count

ความสำคัญ:
- Count น้อย = ไม่น่าเชื่อถือทางสถิติ
- ควรมี Count >= 25-30 เพื่อความน่าเชื่อถือ
- ไม่ควรลด Count requirement เพื่อให้ได้หุ้นเพิ่ม
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

def analyze_reliability():
    """Analyze statistical reliability of Count"""
    perf_file = 'data/symbol_performance.csv'
    
    print("="*100)
    print("China Market - Count Reliability Analysis")
    print("="*100)
    print("\n⚠️  ความสำคัญ: Count น้อย = ไม่น่าเชื่อถือทางสถิติ")
    print("   - Count < 20: ไม่น่าเชื่อถือ (sample size เล็กเกินไป)")
    print("   - Count 20-30: พอใช้ (minimal statistical significance)")
    print("   - Count >= 30: น่าเชื่อถือ (good statistical significance)")
    print("   - Count >= 50: น่าเชื่อถือมาก (strong statistical significance)")
    print("")
    
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
    
    print(f"📋 Current Display Criteria:")
    print(f"  Prob% >= {CURRENT_PROB}%")
    print(f"  RRR >= {CURRENT_RRR}")
    print(f"  Count >= {CURRENT_COUNT}")
    print("")
    
    # Categorize by Count reliability
    print("📊 Count Reliability Categories:")
    print("")
    
    very_low = china_df[china_df['Count'] < 20]
    low = china_df[(china_df['Count'] >= 20) & (china_df['Count'] < 30)]
    moderate = china_df[(china_df['Count'] >= 30) & (china_df['Count'] < 50)]
    good = china_df[(china_df['Count'] >= 50) & (china_df['Count'] < 100)]
    excellent = china_df[china_df['Count'] >= 100]
    
    print(f"  ❌ Very Low (< 20): {len(very_low)} stocks - ไม่น่าเชื่อถือ")
    if len(very_low) > 0:
        for _, row in very_low.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    print(f"\n  ⚠️  Low (20-29): {len(low)} stocks - พอใช้ (minimal)")
    if len(low) > 0:
        for _, row in low.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    print(f"\n  ✅ Moderate (30-49): {len(moderate)} stocks - น่าเชื่อถือ")
    if len(moderate) > 0:
        for _, row in moderate.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    print(f"\n  ✅ Good (50-99): {len(good)} stocks - น่าเชื่อถือมาก")
    if len(good) > 0:
        for _, row in good.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    print(f"\n  ✅ Excellent (100+): {len(excellent)} stocks - น่าเชื่อถือมากที่สุด")
    if len(excellent) > 0:
        for _, row in excellent.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    # Stocks passing current criteria
    passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= CURRENT_COUNT)
    ].copy()
    
    print(f"\n{'='*100}")
    print("✅ Stocks Passing Current Criteria:")
    print(f"{'='*100}")
    print(f"  Total: {len(passing)} stocks")
    print("")
    
    if len(passing) > 0:
        print(f"{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<8} {'Count':<10} {'Reliability':<20}")
        print("-" * 85)
        for _, row in passing.iterrows():
            if row['Count'] < 20:
                reliability = "❌ Very Low"
            elif row['Count'] < 30:
                reliability = "⚠️  Low"
            elif row['Count'] < 50:
                reliability = "✅ Moderate"
            elif row['Count'] < 100:
                reliability = "✅ Good"
            else:
                reliability = "✅ Excellent"
            
            print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}   {row['Count']:>6.0f}      {reliability}")
    
    # Analysis: Should we increase Count requirement?
    print(f"\n{'='*100}")
    print("📊 Analysis: Should we INCREASE Count requirement?")
    print(f"{'='*100}")
    
    # Option 1: Count >= 20 (minimal statistical significance)
    option_20 = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= 20)
    ]
    print(f"\n  Option 1: Count >= 20 (minimal statistical significance)")
    print(f"     Stocks passing: {len(option_20)}")
    if len(option_20) < len(passing):
        print(f"     ⚠️  จะลดหุ้นลง {len(passing) - len(option_20)} ตัว")
        removed = passing[~passing['symbol'].isin(option_20['symbol'])]
        for _, row in removed.iterrows():
            print(f"        - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f} (จะถูกกรองออก)")
    else:
        print(f"     ✅ ไม่กระทบหุ้นที่มีอยู่")
    
    # Option 2: Count >= 25 (better statistical significance)
    option_25 = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= 25)
    ]
    print(f"\n  Option 2: Count >= 25 (better statistical significance)")
    print(f"     Stocks passing: {len(option_25)}")
    if len(option_25) < len(passing):
        print(f"     ⚠️  จะลดหุ้นลง {len(passing) - len(option_25)} ตัว")
        removed = passing[~passing['symbol'].isin(option_25['symbol'])]
        for _, row in removed.iterrows():
            print(f"        - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f} (จะถูกกรองออก)")
    else:
        print(f"     ✅ ไม่กระทบหุ้นที่มีอยู่")
    
    # Option 3: Count >= 30 (good statistical significance)
    option_30 = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= 30)
    ]
    print(f"\n  Option 3: Count >= 30 (good statistical significance)")
    print(f"     Stocks passing: {len(option_30)}")
    if len(option_30) < len(passing):
        print(f"     ⚠️  จะลดหุ้นลง {len(passing) - len(option_30)} ตัว")
        removed = passing[~passing['symbol'].isin(option_30['symbol'])]
        for _, row in removed.iterrows():
            print(f"        - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f} (จะถูกกรองออก)")
    else:
        print(f"     ✅ ไม่กระทบหุ้นที่มีอยู่")
    
    # How to increase Count without lowering requirement
    print(f"\n{'='*100}")
    print("💡 How to Increase Count (without lowering requirement):")
    print(f"{'='*100}")
    
    print(f"\n  1. Reduce min_prob in backtest.py:")
    print(f"     Current: min_prob = 50.0%")
    print(f"     Option: min_prob = 49.5% or 49.0%")
    print(f"     Impact: +5-15% Count increase for existing stocks")
    print(f"     Risk: Low (only 0.5-1.0% reduction)")
    
    print(f"\n  2. Increase n_bars in backtest:")
    print(f"     Current: n_bars = 2000")
    print(f"     Option: n_bars = 2500 or 3000")
    print(f"     Impact: +10-25% Count increase (more historical data)")
    print(f"     Risk: Low (more data = better)")
    
    print(f"\n  3. Reduce threshold_multiplier:")
    print(f"     Current: threshold_multiplier = 0.9")
    print(f"     Option: threshold_multiplier = 0.85")
    print(f"     Impact: +10-20% Count increase (more patterns)")
    print(f"     Risk: Medium (may reduce quality)")
    
    # Recommendations
    print(f"\n{'='*100}")
    print("💡 Recommendations:")
    print(f"{'='*100}")
    
    # Check current Count distribution
    low_count_passing = passing[passing['Count'] < 30]
    
    if len(low_count_passing) > 0:
        print(f"\n  ⚠️  มี {len(low_count_passing)} หุ้นที่มี Count < 30 (พอใช้แต่ไม่ดีที่สุด):")
        for _, row in low_count_passing.iterrows():
            print(f"     - {row['symbol']} ({row['Name']}): Count = {row['Count']:.0f}")
        print(f"\n  💡 แนะนำ:")
        print(f"     1. ลด min_prob จาก 50.0% → 49.5% เพื่อเพิ่ม Count")
        print(f"     2. หรือเพิ่ม n_bars จาก 2000 → 2500 เพื่อเพิ่ม Count")
        print(f"     3. ไม่ควรลด Count requirement เพราะจะได้หุ้นที่ไม่น่าเชื่อถือ")
    else:
        print(f"\n  ✅ หุ้นทั้งหมดมี Count >= 30 (น่าเชื่อถือ)")
        print(f"     - ไม่ต้องปรับเพิ่ม")
    
    # Final recommendation
    print(f"\n  📊 Final Recommendation:")
    if len(passing) > 0:
        avg_count = passing['Count'].mean()
        min_count = passing['Count'].min()
        
        if min_count < 25:
            print(f"     - มีหุ้นที่มี Count < 25: ควรเพิ่ม Count โดยลด min_prob หรือเพิ่ม n_bars")
            print(f"     - ไม่ควรลด Count requirement (จะได้หุ้นที่ไม่น่าเชื่อถือ)")
        elif min_count < 30:
            print(f"     - Count ต่ำสุด = {min_count:.0f} (พอใช้)")
            print(f"     - แนะนำ: เพิ่ม Count โดยลด min_prob จาก 50.0% → 49.5%")
        else:
            print(f"     - Count ต่ำสุด = {min_count:.0f} (ดี)")
            print(f"     - ไม่ต้องปรับเพิ่ม")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    analyze_reliability()

