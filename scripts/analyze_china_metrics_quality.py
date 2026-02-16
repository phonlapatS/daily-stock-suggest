#!/usr/bin/env python
"""
Analyze China Metrics Quality - วิเคราะห์ว่าค่าเหล่านี้โอเคหรือยัง และ Count น้อยไหม

เปรียบเทียบกับ:
- Taiwan (V12.4) - มาตรฐานที่ยอมรับได้
- Display Criteria (เกณฑ์ที่ตั้งไว้)
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

def analyze_quality():
    """Analyze if metrics are acceptable"""
    perf_file = 'data/symbol_performance.csv'
    
    print("="*100)
    print("China Market - Quality Analysis")
    print("="*100)
    
    if not os.path.exists(perf_file):
        print("❌ File not found: symbol_performance.csv")
        return
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        return
    
    # Taiwan for comparison
    taiwan_df = df[df['Country'] == 'TW'].copy()
    
    print(f"\n📊 China Market Analysis:")
    print(f"  Total Stocks Passing: {len(china_df)}")
    
    # Display Criteria (from calculate_metrics.py)
    CHINA_CRITERIA = {
        'Prob%': 53.0,
        'RRR': 0.95,
        'Count': 10
    }
    
    print(f"\n📋 Display Criteria (เกณฑ์ที่ตั้งไว้):")
    print(f"  Prob% >= {CHINA_CRITERIA['Prob%']}%")
    print(f"  RRR >= {CHINA_CRITERIA['RRR']}")
    print(f"  Count >= {CHINA_CRITERIA['Count']}")
    
    # Count Analysis
    print(f"\n📊 Count Analysis:")
    print(f"  Min Count: {china_df['Count'].min():.0f}")
    print(f"  Max Count: {china_df['Count'].max():.0f}")
    print(f"  Avg Count: {china_df['Count'].mean():.0f}")
    print(f"  Median Count: {china_df['Count'].median():.0f}")
    print(f"  Total Trades: {china_df['Count'].sum():.0f}")
    
    # Count Distribution
    print(f"\n  Count Distribution:")
    count_ranges = [
        (0, 10, "Very Low (< 10)"),
        (10, 25, "Low (10-25)"),
        (25, 50, "Medium (25-50)"),
        (50, 100, "Good (50-100)"),
        (100, float('inf'), "Excellent (100+)")
    ]
    
    for min_c, max_c, label in count_ranges:
        if max_c == float('inf'):
            count = len(china_df[china_df['Count'] >= min_c])
        else:
            count = len(china_df[(china_df['Count'] >= min_c) & (china_df['Count'] < max_c)])
        pct = (count / len(china_df)) * 100 if len(china_df) > 0 else 0
        print(f"    {label}: {count} stocks ({pct:.1f}%)")
    
    # Stocks with low count
    low_count = china_df[china_df['Count'] < 25]
    if len(low_count) > 0:
        print(f"\n  ⚠️ Stocks with Low Count (< 25):")
        for _, row in low_count.iterrows():
            name = STOCK_NAMES.get(row['symbol'], row['symbol'])
            print(f"    {row['symbol']} ({name}): Count = {row['Count']:.0f}, Prob% = {row['Prob%']:.1f}%, RRR = {row['RR_Ratio']:.2f}")
    
    # Metrics Analysis
    print(f"\n📈 Metrics Analysis:")
    
    # Prob%
    print(f"\n  Prob%:")
    print(f"    Min: {china_df['Prob%'].min():.1f}%")
    print(f"    Max: {china_df['Prob%'].max():.1f}%")
    print(f"    Avg: {china_df['Prob%'].mean():.1f}%")
    print(f"    Median: {china_df['Prob%'].median():.1f}%")
    passing_prob = len(china_df[china_df['Prob%'] >= CHINA_CRITERIA['Prob%']])
    print(f"    Passing (>= {CHINA_CRITERIA['Prob%']}%): {passing_prob}/{len(china_df)} ({passing_prob/len(china_df)*100:.1f}%)")
    
    # RRR
    print(f"\n  RRR:")
    print(f"    Min: {china_df['RR_Ratio'].min():.2f}")
    print(f"    Max: {china_df['RR_Ratio'].max():.2f}")
    print(f"    Avg: {china_df['RR_Ratio'].mean():.2f}")
    print(f"    Median: {china_df['RR_Ratio'].median():.2f}")
    passing_rrr = len(china_df[china_df['RR_Ratio'] >= CHINA_CRITERIA['RRR']])
    print(f"    Passing (>= {CHINA_CRITERIA['RRR']}): {passing_rrr}/{len(china_df)} ({passing_rrr/len(china_df)*100:.1f}%)")
    
    # Stocks with RRR < 1.0
    low_rrr = china_df[china_df['RR_Ratio'] < 1.0]
    if len(low_rrr) > 0:
        print(f"\n    ⚠️ Stocks with RRR < 1.0 (ไม่คุ้มค่า):")
        for _, row in low_rrr.iterrows():
            name = STOCK_NAMES.get(row['symbol'], row['symbol'])
            print(f"      {row['symbol']} ({name}): RRR = {row['RR_Ratio']:.2f}, Prob% = {row['Prob%']:.1f}%, Count = {row['Count']:.0f}")
    
    # AvgWin% vs AvgLoss%
    print(f"\n  AvgWin% vs AvgLoss%:")
    print(f"    AvgWin%: Min={china_df['AvgWin%'].min():.2f}%, Max={china_df['AvgWin%'].max():.2f}%, Avg={china_df['AvgWin%'].mean():.2f}%")
    print(f"    AvgLoss%: Min={china_df['AvgLoss%'].min():.2f}%, Max={china_df['AvgLoss%'].max():.2f}%, Avg={china_df['AvgLoss%'].mean():.2f}%")
    
    # Stocks where AvgLoss > AvgWin
    bad_ratio = china_df[china_df['AvgLoss%'] > china_df['AvgWin%']]
    if len(bad_ratio) > 0:
        print(f"\n    ⚠️ Stocks where AvgLoss% > AvgWin% (เสียมากกว่าได้):")
        for _, row in bad_ratio.iterrows():
            name = STOCK_NAMES.get(row['symbol'], row['symbol'])
            print(f"      {row['symbol']} ({name}): AvgWin% = {row['AvgWin%']:.2f}%, AvgLoss% = {row['AvgLoss%']:.2f}%, RRR = {row['RR_Ratio']:.2f}")
    
    # Comparison with Taiwan
    if len(taiwan_df) > 0:
        print(f"\n{'='*100}")
        print("📊 Comparison with Taiwan (V12.4):")
        print(f"{'='*100}")
        
        print(f"\n  Taiwan Metrics:")
        print(f"    Stocks Passing: {len(taiwan_df)}")
        print(f"    Avg Prob%: {taiwan_df['Prob%'].mean():.1f}%")
        print(f"    Avg RRR: {taiwan_df['RR_Ratio'].mean():.2f}")
        print(f"    Avg AvgWin%: {taiwan_df['AvgWin%'].mean():.2f}%")
        print(f"    Avg AvgLoss%: {taiwan_df['AvgLoss%'].mean():.2f}%")
        print(f"    Avg Count: {taiwan_df['Count'].mean():.0f}")
        print(f"    Total Trades: {taiwan_df['Count'].sum():.0f}")
        
        print(f"\n  China vs Taiwan:")
        print(f"    Prob%: {china_df['Prob%'].mean():.1f}% vs {taiwan_df['Prob%'].mean():.1f}% ({'+' if china_df['Prob%'].mean() > taiwan_df['Prob%'].mean() else '-'}{abs(china_df['Prob%'].mean() - taiwan_df['Prob%'].mean()):.1f}%)")
        print(f"    RRR: {china_df['RR_Ratio'].mean():.2f} vs {taiwan_df['RR_Ratio'].mean():.2f} ({'+' if china_df['RR_Ratio'].mean() > taiwan_df['RR_Ratio'].mean() else '-'}{abs(china_df['RR_Ratio'].mean() - taiwan_df['RR_Ratio'].mean()):.2f})")
        print(f"    AvgWin%: {china_df['AvgWin%'].mean():.2f}% vs {taiwan_df['AvgWin%'].mean():.2f}% ({'+' if china_df['AvgWin%'].mean() > taiwan_df['AvgWin%'].mean() else '-'}{abs(china_df['AvgWin%'].mean() - taiwan_df['AvgWin%'].mean()):.2f}%)")
        print(f"    AvgLoss%: {china_df['AvgLoss%'].mean():.2f}% vs {taiwan_df['AvgLoss%'].mean():.2f}% ({'+' if china_df['AvgLoss%'].mean() < taiwan_df['AvgLoss%'].mean() else '-'}{abs(china_df['AvgLoss%'].mean() - taiwan_df['AvgLoss%'].mean()):.2f}%)")
        print(f"    Avg Count: {china_df['Count'].mean():.0f} vs {taiwan_df['Count'].mean():.0f} ({'+' if china_df['Count'].mean() > taiwan_df['Count'].mean() else '-'}{abs(china_df['Count'].mean() - taiwan_df['Count'].mean()):.0f})")
    
    # Overall Assessment
    print(f"\n{'='*100}")
    print("📊 Overall Assessment:")
    print(f"{'='*100}")
    
    # Check each metric
    issues = []
    recommendations = []
    
    # Prob% Assessment
    avg_prob = china_df['Prob%'].mean()
    if avg_prob >= 60:
        prob_status = "✅ ดีมาก"
    elif avg_prob >= 55:
        prob_status = "✅ ดี"
    elif avg_prob >= 50:
        prob_status = "⚠️ พอใช้"
    else:
        prob_status = "❌ ไม่ดี"
        issues.append("Prob% ต่ำเกินไป")
    
    print(f"\n  Prob%: {avg_prob:.1f}% - {prob_status}")
    
    # RRR Assessment
    avg_rrr = china_df['RR_Ratio'].mean()
    if avg_rrr >= 1.5:
        rrr_status = "✅ ดีมาก"
    elif avg_rrr >= 1.2:
        rrr_status = "✅ ดี"
    elif avg_rrr >= 1.0:
        rrr_status = "⚠️ พอใช้"
    else:
        rrr_status = "❌ ไม่ดี"
        issues.append("RRR ต่ำกว่า 1.0 (ไม่คุ้มค่า)")
    
    print(f"  RRR: {avg_rrr:.2f} - {rrr_status}")
    
    # AvgWin% vs AvgLoss% Assessment
    avg_win = china_df['AvgWin%'].mean()
    avg_loss = china_df['AvgLoss%'].mean()
    if avg_win > avg_loss * 1.5:
        win_loss_status = "✅ ดีมาก"
    elif avg_win > avg_loss:
        win_loss_status = "✅ ดี"
    elif avg_win > avg_loss * 0.9:
        win_loss_status = "⚠️ พอใช้"
    else:
        win_loss_status = "❌ ไม่ดี"
        issues.append("AvgWin% ต่ำกว่า AvgLoss% (เสียมากกว่าได้)")
    
    print(f"  AvgWin% vs AvgLoss%: {avg_win:.2f}% vs {avg_loss:.2f}% - {win_loss_status}")
    
    # Count Assessment
    avg_count = china_df['Count'].mean()
    min_count = china_df['Count'].min()
    low_count_stocks = len(china_df[china_df['Count'] < 25])
    
    if avg_count >= 50 and min_count >= 25:
        count_status = "✅ ดีมาก"
    elif avg_count >= 30 and min_count >= 15:
        count_status = "✅ ดี"
    elif avg_count >= 20 and min_count >= 10:
        count_status = "⚠️ พอใช้"
    else:
        count_status = "❌ ไม่ดี"
        issues.append(f"Count น้อยเกินไป (เฉลี่ย {avg_count:.0f}, ต่ำสุด {min_count:.0f})")
    
    print(f"  Count: Avg={avg_count:.0f}, Min={min_count:.0f}, Low Count Stocks={low_count_stocks} - {count_status}")
    
    if low_count_stocks > 0:
        recommendations.append(f"มี {low_count_stocks} หุ้นที่มี Count < 25 - ควรเพิ่ม Count")
    
    # Overall Conclusion
    print(f"\n  Overall Conclusion:")
    if len(issues) == 0:
        print(f"    ✅ ค่าทั้งหมดโอเค - พร้อมใช้งาน")
    else:
        print(f"    ⚠️ มีปัญหา:")
        for issue in issues:
            print(f"      - {issue}")
    
    if len(recommendations) > 0:
        print(f"\n  Recommendations:")
        for rec in recommendations:
            print(f"    - {rec}")
    
    # Specific recommendations
    print(f"\n  Specific Recommendations:")
    
    if avg_rrr < 1.0:
        print(f"    - RRR ต่ำเกินไป ({avg_rrr:.2f}) - ควรปรับ Risk Management (ลด SL หรือเพิ่ม TP)")
    
    if avg_win < avg_loss:
        print(f"    - AvgWin% ต่ำกว่า AvgLoss% - ควรปรับ Risk Management")
    
    if min_count < 15:
        print(f"    - Count ต่ำสุด ({min_count:.0f}) น้อยเกินไป - ควรลด min_prob หรือเพิ่ม n_bars")
    
    if low_count_stocks > len(china_df) * 0.3:
        print(f"    - มีหุ้นจำนวนมากที่มี Count ต่ำ - ควรปรับ display criteria หรือเพิ่ม Count")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    analyze_quality()

