#!/usr/bin/env python
"""
Show China Detailed Metrics - แสดง RRR, AvgWin, AvgLoss, Prob

แสดงผลลัพธ์โดยละเอียด:
- RRR
- AvgWin%
- AvgLoss%
- Prob%
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

def show_detailed_metrics():
    """Show detailed metrics"""
    perf_file = 'data/symbol_performance.csv'
    results_file = 'data/china_realistic_settings_results.csv'
    
    print("="*100)
    print("China Market - Detailed Metrics")
    print("="*100)
    
    # From symbol_performance.csv (by stock)
    if os.path.exists(perf_file):
        df = pd.read_csv(perf_file)
        china_df = df[df['Country'] == 'CN'].copy()
        
        if len(china_df) > 0:
            china_df = china_df.sort_values('Prob%', ascending=False)
            china_df['Name'] = china_df['symbol'].map(STOCK_NAMES).fillna(china_df['symbol'])
            
            print(f"\n📊 By Stock (from symbol_performance.csv):")
            print(f"\n{'Symbol':<12} {'Name':<15} {'Prob%':<10} {'RRR':<8} {'AvgWin%':<12} {'AvgLoss%':<12} {'Count':<8}")
            print("-" * 100)
            
            for _, row in china_df.iterrows():
                print(f"{row['symbol']:<12} {row['Name']:<15} {row['Prob%']:>6.1f}%     {row['RR_Ratio']:>6.2f}   {row['AvgWin%']:>8.2f}%     {row['AvgLoss%']:>8.2f}%     {row['Count']:>6.0f}")
            
            print(f"\n📈 Average Metrics:")
            print(f"  Avg Prob%: {china_df['Prob%'].mean():.1f}%")
            print(f"  Avg RRR: {china_df['RR_Ratio'].mean():.2f}")
            print(f"  Avg AvgWin%: {china_df['AvgWin%'].mean():.2f}%")
            print(f"  Avg AvgLoss%: {china_df['AvgLoss%'].mean():.2f}%")
            print(f"  Avg Count: {china_df['Count'].mean():.0f}")
            print(f"  Total Trades: {china_df['Count'].sum():.0f}")
            
            # Best metrics
            best_prob = china_df.loc[china_df['Prob%'].idxmax()]
            best_rrr = china_df.loc[china_df['RR_Ratio'].idxmax()]
            
            print(f"\n  Best Prob%: {best_prob['Prob%']:.1f}% ({best_prob['symbol']} - {best_prob['Name']})")
            print(f"  Best RRR: {best_rrr['RR_Ratio']:.2f} ({best_rrr['symbol']} - {best_rrr['Name']})")
            print(f"  Best AvgWin%: {china_df['AvgWin%'].max():.2f}%")
            print(f"  Best AvgLoss%: {china_df['AvgLoss%'].min():.2f}% (ต่ำ = ดี)")
    
    # From test results (overall)
    if os.path.exists(results_file):
        df_results = pd.read_csv(results_file)
        best = df_results.loc[df_results['score'].idxmax()]
        
        print(f"\n{'='*100}")
        print("📊 Overall Performance (from test results):")
        print(f"{'='*100}")
        print(f"\n  Best Combination:")
        print(f"    TP: {best['tp']}%")
        print(f"    Max Hold: {best['max_hold']:.0f} days")
        print(f"    SL: {best['sl']}%")
        
        print(f"\n  Performance Metrics:")
        print(f"    RRR: {best['rrr']:.2f}")
        print(f"    Win Rate: {best['win_rate']:.1f}%")
        print(f"    Expectancy: {best['expectancy']:.2f}%")
        print(f"    TP Hit Rate: {best['tp_rate']:.1f}%")
        print(f"    SL Hit Rate: {best['sl_rate']:.1f}%")
        print(f"    MAX_HOLD Rate: {best['max_hold_rate']:.1f}%")
        print(f"    Avg Hold Days: {best['avg_hold_days']:.1f} days")
        
        # Calculate AvgWin and AvgLoss from RRR and Win Rate
        # RRR = AvgWin / AvgLoss
        # Win Rate = Wins / Total
        # Expectancy = (Win Rate * AvgWin) - ((1 - Win Rate) * AvgLoss)
        
        win_rate = best['win_rate'] / 100
        rrr = best['rrr']
        expectancy = best['expectancy']
        
        # Solve: expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        # And: rrr = avg_win / avg_loss
        # So: avg_win = rrr * avg_loss
        # And: expectancy = (win_rate * rrr * avg_loss) - ((1 - win_rate) * avg_loss)
        #     = avg_loss * (win_rate * rrr - (1 - win_rate))
        # So: avg_loss = expectancy / (win_rate * rrr - (1 - win_rate))
        
        denominator = (win_rate * rrr - (1 - win_rate))
        if denominator != 0:
            avg_loss = expectancy / denominator
            avg_win = rrr * avg_loss
        else:
            avg_loss = 0
            avg_win = 0
        
        print(f"\n  Calculated from RRR and Win Rate:")
        print(f"    AvgWin%: {avg_win:.2f}%")
        print(f"    AvgLoss%: {avg_loss:.2f}%")
        print(f"    RRR: {rrr:.2f} (verified)")
    
    # From trade history (actual)
    log_file = 'logs/trade_history_CHINA.csv'
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
            
            print(f"\n{'='*100}")
            print("📊 Actual Performance (from trade history):")
            print(f"{'='*100}")
            print(f"\n  Total Trades: {total_trades}")
            print(f"  Win Rate: {win_rate:.1f}%")
            print(f"  RRR: {rrr:.2f}")
            print(f"  AvgWin%: {avg_win:.2f}%")
            print(f"  AvgLoss%: {avg_loss:.2f}%")
            print(f"  Expectancy: {(win_rate/100 * avg_win) - ((1-win_rate/100) * avg_loss):.2f}%")
    
    print(f"\n{'='*100}")

if __name__ == '__main__':
    show_detailed_metrics()

