
import pandas as pd
import os

def diagnose(file_path, market_name):
    if not os.path.exists(file_path):
        print(f"❌ {market_name} file missing: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    # Use strategy-adjusted return from the backtest
    df['pnl'] = df['trader_return']
    
    print(f"\n--- DIAGNOSIS: {market_name} ---")
    print(f"Total Trades: {len(df)}")
    print(f"Overall Avg Return: {df['pnl'].mean():.4f}%")
    
    # Analyze by Prob tiers
    tiers = [
        ('Low Quality (Prob < 55%)', df[df['prob'] < 55]),
        ('Medium Quality (55% <= Prob < 60%)', df[(df['prob'] >= 55) & (df['prob'] < 60)]),
        ('Elite (Prob >= 60%)', df[df['prob'] >= 60])
    ]
    
    for label, subset in tiers:
        if not subset.empty:
            avg_ret = subset['pnl'].mean()
            win_rate = (subset['pnl'] > 0).mean() * 100
            print(f"{label:<40} | Trades: {len(subset):<6} | WinRate: {win_rate:.1f}% | AvgPnl: {avg_ret:.4f}%")
        else:
            print(f"{label:<40} | (No Data)")

if __name__ == "__main__":
    diagnose('logs/trade_history_THAI.csv', 'THAI SET')
    diagnose('logs/trade_history_TAIWAN.csv', 'TAIWAN TWSE')
    diagnose('logs/trade_history_US.csv', 'US NASDAQ')
    diagnose('logs/trade_history_CHINA.csv', 'CHINA/HK')
