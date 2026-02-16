#!/usr/bin/env python
"""
Analyze China Market V13.4 Stability - วิเคราะห์ความเสถียรของ V13.4

เปรียบเทียบกับ V13.2 และประเมินความเสถียร
"""

import sys
import os
import pandas as pd
import io
import numpy as np

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

def analyze_v13_4_stability():
    """Analyze V13.4 stability"""
    perf_file = 'data/symbol_performance.csv'
    log_file = 'logs/trade_history_CHINA.csv'
    
    print("="*100)
    print("China Market V13.4 - Stability Assessment")
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
    
    # Current criteria (V13.4)
    CURRENT_RRR = 1.0
    CURRENT_COUNT = 15
    CURRENT_PROB = 53.0
    
    # Stocks passing criteria
    passing = china_df[
        (china_df['Prob%'] >= CURRENT_PROB) &
        (china_df['RR_Ratio'] >= CURRENT_RRR) &
        (china_df['Count'] >= CURRENT_COUNT)
    ].copy()
    
    print(f"\n📊 V13.4 Results:")
    print(f"  Stocks Passing Criteria: {len(passing)}")
    print(f"  Criteria: Prob% >= {CURRENT_PROB}%, RRR >= {CURRENT_RRR}, Count >= {CURRENT_COUNT}")
    print("")
    
    if len(passing) > 0:
        print(f"{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<8} {'AvgWin%':<12} {'AvgLoss%':<12} {'Count':<10} {'Reliability':<20}")
        print("-" * 110)
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
            
            print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}   {row['AvgWin%']:>8.2f}%     {row['AvgLoss%']:>8.2f}%     {row['Count']:>6.0f}      {reliability}")
    
    # Stability Indicators
    print(f"\n{'='*100}")
    print("🔍 Stability Indicators:")
    print(f"{'='*100}")
    
    if len(passing) == 0:
        print("❌ No stocks passing criteria - Market is unstable")
        return
    
    # 1. Count Reliability
    low_count = len(passing[passing['Count'] < 30])
    print(f"\n1. Count Reliability:")
    print(f"   Avg Count: {passing['Count'].mean():.0f}")
    print(f"   Min Count: {passing['Count'].min():.0f}")
    print(f"   Max Count: {passing['Count'].max():.0f}")
    print(f"   Stocks with Count < 30: {low_count}/{len(passing)} ({low_count/len(passing)*100:.1f}%)")
    if low_count == 0:
        print(f"   ✅ All stocks have Count >= 30 (น่าเชื่อถือ)")
    elif low_count <= len(passing) * 0.3:
        print(f"   ⚠️  Some stocks have Count < 30 (พอใช้)")
    else:
        print(f"   ❌ Many stocks have Count < 30 (ไม่น่าเชื่อถือ)")
    
    # 2. RRR Quality
    low_rrr = len(passing[passing['RR_Ratio'] < 1.2])
    print(f"\n2. RRR Quality:")
    print(f"   Avg RRR: {passing['RR_Ratio'].mean():.2f}")
    print(f"   Min RRR: {passing['RR_Ratio'].min():.2f}")
    print(f"   Max RRR: {passing['RR_Ratio'].max():.2f}")
    print(f"   Stocks with RRR < 1.2: {low_rrr}/{len(passing)} ({low_rrr/len(passing)*100:.1f}%)")
    if passing['RR_Ratio'].min() >= 1.2:
        print(f"   ✅ All stocks have RRR >= 1.2 (ดีมาก)")
    elif passing['RR_Ratio'].min() >= 1.0:
        print(f"   ✅ All stocks have RRR >= 1.0 (ดี)")
    else:
        print(f"   ⚠️  Some stocks have RRR < 1.0 (ไม่ดี)")
    
    # 3. Win/Loss Balance
    bad_ratio = len(passing[passing['AvgLoss%'] > passing['AvgWin%']])
    win_loss_ratio = passing['AvgWin%'].mean() / passing['AvgLoss%'].mean() if passing['AvgLoss%'].mean() > 0 else 0
    print(f"\n3. Win/Loss Balance:")
    print(f"   AvgWin%: {passing['AvgWin%'].mean():.2f}%")
    print(f"   AvgLoss%: {passing['AvgLoss%'].mean():.2f}%")
    print(f"   Win/Loss Ratio: {win_loss_ratio:.2f}")
    print(f"   Stocks where AvgLoss% > AvgWin%: {bad_ratio}/{len(passing)} ({bad_ratio/len(passing)*100:.1f}%)")
    if win_loss_ratio > 1.2 and bad_ratio == 0:
        print(f"   ✅ Excellent balance (AvgWin% > AvgLoss% by 20%+)")
    elif win_loss_ratio > 1.0 and bad_ratio == 0:
        print(f"   ✅ Good balance (AvgWin% > AvgLoss%)")
    elif win_loss_ratio > 0.9:
        print(f"   ⚠️  Moderate balance")
    else:
        print(f"   ❌ Poor balance (AvgLoss% > AvgWin%)")
    
    # 4. Prob% Consistency
    prob_std = passing['Prob%'].std()
    prob_cv = (prob_std / passing['Prob%'].mean()) * 100 if passing['Prob%'].mean() > 0 else 0
    print(f"\n4. Prob% Consistency:")
    print(f"   Avg Prob%: {passing['Prob%'].mean():.1f}%")
    print(f"   Std Dev: {prob_std:.1f}%")
    print(f"   Coefficient of Variation: {prob_cv:.1f}%")
    if prob_cv < 15:
        print(f"   ✅ Very consistent (CV < 15%)")
    elif prob_cv < 25:
        print(f"   ⚠️  Moderate consistency (CV 15-25%)")
    else:
        print(f"   ❌ High variation (CV > 25%)")
    
    # 5. Trade History Analysis
    if os.path.exists(log_file):
        df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
        
        if len(df_trades) > 0:
            df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
            df_trades = df_trades.dropna(subset=['actual_return'])
            
            wins = df_trades[df_trades['actual_return'] > 0]
            losses = df_trades[df_trades['actual_return'] <= 0]
            
            total_trades = len(df_trades)
            win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
            avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
            avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
            
            print(f"\n5. Trade History Analysis:")
            print(f"   Total Trades: {total_trades:,}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   RRR: {rrr:.2f}")
            print(f"   AvgWin%: {avg_win:.2f}%")
            print(f"   AvgLoss%: {avg_loss:.2f}%")
            print(f"   Expectancy: {(win_rate/100 * avg_win) - ((1-win_rate/100) * avg_loss):.2f}%")
            
            if win_rate >= 60 and rrr >= 1.5:
                print(f"   ✅ Excellent performance")
            elif win_rate >= 55 and rrr >= 1.2:
                print(f"   ✅ Good performance")
            elif win_rate >= 50 and rrr >= 1.0:
                print(f"   ⚠️  Acceptable performance")
            else:
                print(f"   ❌ Poor performance")
    
    # Overall Stability Score
    print(f"\n{'='*100}")
    print("📊 Overall Stability Score:")
    print(f"{'='*100}")
    
    score = 100
    
    # Count Reliability (30 points)
    if passing['Count'].min() >= 50:
        count_score = 30
    elif passing['Count'].min() >= 30:
        count_score = 25
    elif passing['Count'].min() >= 25:
        count_score = 20
    elif passing['Count'].min() >= 20:
        count_score = 15
    else:
        count_score = 5
    
    if low_count > len(passing) * 0.5:
        count_score -= 10
    
    score -= (30 - count_score)
    
    # RRR Quality (25 points)
    if passing['RR_Ratio'].min() >= 1.5:
        rrr_score = 25
    elif passing['RR_Ratio'].min() >= 1.2:
        rrr_score = 20
    elif passing['RR_Ratio'].min() >= 1.0:
        rrr_score = 15
    else:
        rrr_score = 5
    
    if passing['RR_Ratio'].mean() < 1.0:
        rrr_score -= 10
    
    score -= (25 - rrr_score)
    
    # Win/Loss Balance (25 points)
    if win_loss_ratio > 1.2 and bad_ratio == 0:
        balance_score = 25
    elif win_loss_ratio > 1.0 and bad_ratio == 0:
        balance_score = 20
    elif win_loss_ratio > 0.9:
        balance_score = 15
    else:
        balance_score = 5
    
    score -= (25 - balance_score)
    
    # Prob% Consistency (20 points)
    if prob_cv < 15:
        prob_score = 20
    elif prob_cv < 25:
        prob_score = 15
    else:
        prob_score = 5
    
    score -= (20 - prob_score)
    
    print(f"\n  Stability Score: {score}/100")
    
    if score >= 80:
        stability_level = "✅ Very Stable"
        status = "พร้อมใช้งานจริง"
    elif score >= 60:
        stability_level = "✅ Stable"
        status = "พร้อมใช้งานจริง (แต่ควร monitor)"
    elif score >= 40:
        stability_level = "⚠️  Moderately Stable"
        status = "ยังไม่พร้อม - ต้องปรับปรุง"
    else:
        stability_level = "❌ Unstable"
        status = "ไม่พร้อมใช้งาน"
    
    print(f"  Stability Level: {stability_level}")
    print(f"  Status: {status}")
    
    # Breakdown
    print(f"\n  Score Breakdown:")
    print(f"    Count Reliability: {count_score}/30")
    print(f"    RRR Quality: {rrr_score}/25")
    print(f"    Win/Loss Balance: {balance_score}/25")
    print(f"    Prob% Consistency: {prob_score}/20")
    
    # Strengths and Issues
    strengths = []
    issues = []
    
    if passing['Count'].min() >= 30:
        strengths.append("All stocks have Count >= 30 (น่าเชื่อถือ)")
    elif passing['Count'].min() < 20:
        issues.append(f"Min Count = {passing['Count'].min():.0f} (ไม่น่าเชื่อถือ)")
    
    if passing['RR_Ratio'].min() >= 1.2:
        strengths.append("All stocks have RRR >= 1.2 (ดีมาก)")
    elif passing['RR_Ratio'].min() < 1.0:
        issues.append(f"Min RRR = {passing['RR_Ratio'].min():.2f} (ไม่ดี)")
    
    if win_loss_ratio > 1.0 and bad_ratio == 0:
        strengths.append("AvgWin% > AvgLoss% for all stocks")
    elif win_loss_ratio < 0.9:
        issues.append("AvgLoss% > AvgWin% (เสียมากกว่าได้)")
    
    if prob_cv < 15:
        strengths.append("Prob% is very consistent")
    elif prob_cv > 25:
        issues.append("Prob% has high variation")
    
    if strengths:
        print(f"\n  ✅ Strengths:")
        for strength in strengths:
            print(f"     - {strength}")
    
    if issues:
        print(f"\n  ⚠️  Issues:")
        for issue in issues:
            print(f"     - {issue}")
    
    # Final Assessment
    print(f"\n{'='*100}")
    print("📊 Final Assessment:")
    print(f"{'='*100}")
    
    if score >= 80:
        print(f"\n  ✅ Market is VERY STABLE")
        print(f"     - Ready for production use")
        print(f"     - All metrics are good")
        print(f"     - Count is reliable (>= 30)")
        print(f"     - RRR is good (>= 1.0)")
        print(f"     - Win/Loss balance is good")
    elif score >= 60:
        print(f"\n  ✅ Market is STABLE")
        print(f"     - Ready for production use (with monitoring)")
        print(f"     - Most metrics are good")
        if low_count > 0:
            print(f"     - Some stocks have Count < 30 (ควร monitor)")
    else:
        print(f"\n  ⚠️  Market needs improvement")
        print(f"     - Not ready for production")
        if issues:
            print(f"     - Issues to fix:")
            for issue in issues:
                print(f"       * {issue}")
    
    print(f"\n{'='*100}")
    
    return score

if __name__ == '__main__':
    score = analyze_v13_4_stability()
    
    if score is not None:
        print(f"\n✅ Analysis complete!")
        print(f"   Stability Score: {score}/100")

