#!/usr/bin/env python
"""
Analyze China Market Stability - วิเคราะห์ความเสถียรของตลาดจีน

ตรวจสอบ:
1. Consistency ของ metrics
2. Distribution ของผลลัพธ์
3. Risk factors
4. Overall stability assessment
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

def analyze_stability():
    """Analyze China market stability"""
    perf_file = 'data/symbol_performance.csv'
    log_file = 'logs/trade_history_CHINA.csv'
    
    print("="*100)
    print("China Market - Stability Analysis")
    print("="*100)
    
    if not os.path.exists(perf_file):
        print("❌ File not found: symbol_performance.csv")
        return
    
    df = pd.read_csv(perf_file)
    china_df = df[df['Country'] == 'CN'].copy()
    
    if len(china_df) == 0:
        print("❌ No China stocks found")
        return
    
    print(f"\n📊 Current Status (V13.2):")
    print(f"  Total Stocks Passing: {len(china_df)}")
    
    # Basic Metrics
    print(f"\n📈 Basic Metrics:")
    print(f"  Avg Prob%: {china_df['Prob%'].mean():.1f}% (Min: {china_df['Prob%'].min():.1f}%, Max: {china_df['Prob%'].max():.1f}%)")
    print(f"  Avg RRR: {china_df['RR_Ratio'].mean():.2f} (Min: {china_df['RR_Ratio'].min():.2f}, Max: {china_df['RR_Ratio'].max():.2f})")
    print(f"  Avg AvgWin%: {china_df['AvgWin%'].mean():.2f}%")
    print(f"  Avg AvgLoss%: {china_df['AvgLoss%'].mean():.2f}%")
    print(f"  Avg Count: {china_df['Count'].mean():.0f} (Min: {china_df['Count'].min():.0f}, Max: {china_df['Count'].max():.0f})")
    
    # Stability Indicators
    print(f"\n🔍 Stability Indicators:")
    
    # 1. Consistency of Prob%
    prob_std = china_df['Prob%'].std()
    prob_cv = (prob_std / china_df['Prob%'].mean()) * 100 if china_df['Prob%'].mean() > 0 else 0
    print(f"\n  1. Prob% Consistency:")
    print(f"     Std Dev: {prob_std:.1f}%")
    print(f"     Coefficient of Variation: {prob_cv:.1f}%")
    if prob_cv < 15:
        print(f"     ✅ Stable (CV < 15%)")
    elif prob_cv < 25:
        print(f"     ⚠️  Moderate (CV 15-25%)")
    else:
        print(f"     ❌ Unstable (CV > 25%)")
    
    # 2. RRR Distribution
    rrr_std = china_df['RR_Ratio'].std()
    rrr_cv = (rrr_std / china_df['RR_Ratio'].mean()) * 100 if china_df['RR_Ratio'].mean() > 0 else 0
    print(f"\n  2. RRR Distribution:")
    print(f"     Std Dev: {rrr_std:.2f}")
    print(f"     Coefficient of Variation: {rrr_cv:.1f}%")
    low_rrr_count = len(china_df[china_df['RR_Ratio'] < 1.0])
    print(f"     Stocks with RRR < 1.0: {low_rrr_count}/{len(china_df)} ({low_rrr_count/len(china_df)*100:.1f}%)")
    if low_rrr_count == 0:
        print(f"     ✅ All stocks have RRR >= 1.0")
    elif low_rrr_count <= len(china_df) * 0.3:
        print(f"     ⚠️  Some stocks have low RRR")
    else:
        print(f"     ❌ Many stocks have low RRR")
    
    # 3. Count Distribution
    count_std = china_df['Count'].std()
    count_cv = (count_std / china_df['Count'].mean()) * 100 if china_df['Count'].mean() > 0 else 0
    print(f"\n  3. Count Distribution:")
    print(f"     Std Dev: {count_std:.0f}")
    print(f"     Coefficient of Variation: {count_cv:.1f}%")
    low_count_count = len(china_df[china_df['Count'] < 25])
    print(f"     Stocks with Count < 25: {low_count_count}/{len(china_df)} ({low_count_count/len(china_df)*100:.1f}%)")
    if low_count_count == 0:
        print(f"     ✅ All stocks have Count >= 25")
    elif low_count_count <= len(china_df) * 0.3:
        print(f"     ⚠️  Some stocks have low Count")
    else:
        print(f"     ❌ Many stocks have low Count")
    
    # 4. AvgWin% vs AvgLoss% Balance
    win_loss_ratio = china_df['AvgWin%'].mean() / china_df['AvgLoss%'].mean() if china_df['AvgLoss%'].mean() > 0 else 0
    bad_ratio_count = len(china_df[china_df['AvgLoss%'] > china_df['AvgWin%']])
    print(f"\n  4. Win/Loss Balance:")
    print(f"     AvgWin% / AvgLoss% Ratio: {win_loss_ratio:.2f}")
    print(f"     Stocks where AvgLoss% > AvgWin%: {bad_ratio_count}/{len(china_df)} ({bad_ratio_count/len(china_df)*100:.1f}%)")
    if win_loss_ratio > 1.0 and bad_ratio_count == 0:
        print(f"     ✅ Good balance (AvgWin% > AvgLoss%)")
    elif win_loss_ratio > 0.9 and bad_ratio_count <= len(china_df) * 0.3:
        print(f"     ⚠️  Moderate balance")
    else:
        print(f"     ❌ Poor balance (AvgLoss% > AvgWin%)")
    
    # 5. Trade History Analysis (if available)
    if os.path.exists(log_file):
        df_trades = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
        
        if len(df_trades) > 0:
            df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
            df_trades = df_trades.dropna(subset=['actual_return'])
            
            print(f"\n  5. Trade History Analysis:")
            print(f"     Total Trades: {len(df_trades)}")
            
            # Win Rate Consistency
            if 'symbol' in df_trades.columns:
                win_rates = []
                for symbol in df_trades['symbol'].unique():
                    symbol_trades = df_trades[df_trades['symbol'] == symbol]
                    wins = len(symbol_trades[symbol_trades['actual_return'] > 0])
                    total = len(symbol_trades)
                    if total > 0:
                        win_rates.append((wins / total) * 100)
                
                if win_rates:
                    win_rate_std = np.std(win_rates)
                    win_rate_mean = np.mean(win_rates)
                    print(f"     Avg Win Rate: {win_rate_mean:.1f}%")
                    print(f"     Win Rate Std Dev: {win_rate_std:.1f}%")
                    if win_rate_std < 10:
                        print(f"     ✅ Consistent win rates across stocks")
                    elif win_rate_std < 15:
                        print(f"     ⚠️  Moderate win rate variation")
                    else:
                        print(f"     ❌ High win rate variation")
            
            # Return Distribution
            returns_std = df_trades['actual_return'].std()
            returns_mean = df_trades['actual_return'].mean()
            returns_skew = df_trades['actual_return'].skew()
            print(f"     Return Std Dev: {returns_std:.2f}%")
            print(f"     Return Skewness: {returns_skew:.2f}")
            if abs(returns_skew) < 0.5:
                print(f"     ✅ Normal return distribution")
            elif abs(returns_skew) < 1.0:
                print(f"     ⚠️  Slightly skewed returns")
            else:
                print(f"     ❌ Highly skewed returns")
    
    # Overall Stability Assessment
    print(f"\n{'='*100}")
    print("📊 Overall Stability Assessment:")
    print(f"{'='*100}")
    
    issues = []
    strengths = []
    
    # Check each indicator
    if prob_cv < 15:
        strengths.append("Prob% is consistent")
    elif prob_cv > 25:
        issues.append("Prob% has high variation")
    
    if low_rrr_count == 0:
        strengths.append("All stocks have RRR >= 1.0")
    elif low_rrr_count > len(china_df) * 0.5:
        issues.append(f"{low_rrr_count} stocks have RRR < 1.0")
    
    if low_count_count == 0:
        strengths.append("All stocks have Count >= 25")
    elif low_count_count > len(china_df) * 0.5:
        issues.append(f"{low_count_count} stocks have Count < 25")
    
    if win_loss_ratio > 1.0 and bad_ratio_count == 0:
        strengths.append("AvgWin% > AvgLoss% for all stocks")
    elif win_loss_ratio < 0.9 or bad_ratio_count > len(china_df) * 0.5:
        issues.append("AvgLoss% > AvgWin% for many stocks")
    
    # Stability Score
    stability_score = 100
    if prob_cv > 25:
        stability_score -= 20
    if low_rrr_count > len(china_df) * 0.3:
        stability_score -= 25
    if low_count_count > len(china_df) * 0.3:
        stability_score -= 20
    if win_loss_ratio < 0.9:
        stability_score -= 25
    if china_df['RR_Ratio'].mean() < 1.0:
        stability_score -= 10
    
    print(f"\n  Stability Score: {stability_score}/100")
    
    if stability_score >= 80:
        stability_level = "✅ Very Stable"
    elif stability_score >= 60:
        stability_level = "⚠️  Moderately Stable"
    elif stability_score >= 40:
        stability_level = "⚠️  Somewhat Unstable"
    else:
        stability_level = "❌ Unstable"
    
    print(f"  Stability Level: {stability_level}")
    
    if strengths:
        print(f"\n  ✅ Strengths:")
        for strength in strengths:
            print(f"     - {strength}")
    
    if issues:
        print(f"\n  ⚠️  Issues:")
        for issue in issues:
            print(f"     - {issue}")
    
    # Recommendations
    print(f"\n  💡 Recommendations:")
    
    if china_df['RR_Ratio'].mean() < 1.0:
        print(f"     - Adjust Risk Management to improve RRR (SL/TP)")
    
    if low_count_count > len(china_df) * 0.3:
        print(f"     - Reduce min_prob or increase n_bars to increase Count")
    
    if win_loss_ratio < 0.9:
        print(f"     - Adjust Risk Management to improve Win/Loss ratio")
    
    if prob_cv > 25:
        print(f"     - Review stock selection criteria for more consistent Prob%")
    
    if stability_score >= 80:
        print(f"     - ✅ Market is stable - ready for production")
    elif stability_score >= 60:
        print(f"     - ⚠️  Market needs minor adjustments before production")
    else:
        print(f"     - ❌ Market needs significant improvements before production")
    
    print(f"\n{'='*100}")
    
    return stability_score, issues, strengths

if __name__ == '__main__':
    score, issues, strengths = analyze_stability()
    
    if score is not None:
        print(f"\n✅ Analysis complete!")
        print(f"   Stability Score: {score}/100")

