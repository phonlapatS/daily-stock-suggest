import os
import pandas as pd
import numpy as np

def calculate_stats_from_log(log_file="logs/performance_log.csv"):
    """
    V4.3 Performance Calculator
    Reads single 'performance_log.csv' and generates reports per Market (Exchange).
    """
    if not os.path.exists(log_file):
        print(f"❌ Log file {log_file} not found.")
        return

    # Load Data
    try:
        df = pd.read_csv(log_file)
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return

    if df.empty:
        print("ℹ️ Log file is empty.")
        return
        
    # Standardize Column Names (strip spaces)
    df.columns = df.columns.str.strip()
    
    # Check required columns
    required_cols = ['exchange', 'symbol', 'forecast', 'change_pct', 'actual', 'correct']
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ Missing required column: {col}")
            return

    # Filter Completed Trades (Exclude Pending)
    # 'actual' should not be 'PENDING'
    completed_df = df[df['actual'] != 'PENDING'].copy()
    
    if completed_df.empty:
        print("ℹ️ No completed trades found in log (all pending?).")
        return

    # =========================================================
    # 1. Calculate P/L logic
    # =========================================================
    # Logic:
    # If Forecast UP   -> P/L = change_pct
    # If Forecast DOWN -> P/L = -change_pct (Short selling logic)
    # If Forecast SIDE -> P/L = 0 (No trade)
    #
    # Note: 'change_pct' in log is (Close - Open) / Open * 100
    #
    def calc_pnl(row):
        forecast = str(row['forecast']).upper()
        change = float(row['change_pct']) if pd.notna(row['change_pct']) else 0.0
        
        if forecast == 'UP':
            return change
        elif forecast == 'DOWN':
            return -change
        return 0.0

    completed_df['P/L'] = completed_df.apply(calc_pnl, axis=1)

    # Get Unique Markets
    markets = completed_df['exchange'].unique()
    
    print(f"\n📊 PERFORMANCE ANALYSIS (Based on {len(completed_df)} completed trades)")
    print(f"   Source: {log_file}")

    for market in markets:
        market_df = completed_df[completed_df['exchange'] == market].copy()
        
        if market_df.empty:
            continue
            
        print("\n" + "=" * 115)
        print(f"🌍 MARKET: {market}")
        print("=" * 115)

        # ---------------------------------------------------------
        # LEVEL A: MARKET SUMMARY
        # ---------------------------------------------------------
        profits = market_df[market_df['P/L'] > 0]
        losses = market_df[market_df['P/L'] <= 0]
        
        n_prof = len(profits)
        n_loss = len(losses)
        n_total = len(market_df)
        
        avg_prof = profits['P/L'].mean() if n_prof > 0 else 0
        avg_loss = losses['P/L'].mean() if n_loss > 0 else 0
        
        total_prof = profits['P/L'].sum()
        total_loss = losses['P/L'].sum()
        net_pnl = total_prof + total_loss
        
        winrate = (n_prof / n_total * 100) if n_total > 0 else 0
        if total_prof > 0 or total_loss < 0:
            ratio = abs(total_prof / total_loss) if total_loss != 0 else (99.0 if total_prof > 0 else 0)
        else:
            ratio = 0.0
            
        print("\n📊 LEVEL A: MARKET SUMMARY")
        print("-" * 115)
        print(f"{'Type':<12} {'#':<8} {'Avg P/L %':<15} {'Total P/L %':<15} {'Winrate':<15}")
        print("-" * 115)
        print(f"{'Profit':<12} {n_prof:<8} {avg_prof:<15.2f} {total_prof:<15.2f} {winrate:<15.1f}")
        print(f"{'Loss':<12} {n_loss:<8} {avg_loss:<15.2f} {total_loss:<15.2f} {'':<15}")
        print("-" * 115)
        # print(f"{'NET':<12} {n_total:<8} {'':<15} {net_pnl:<15.2f} {'':<15}") # Hidden by request

        # ---------------------------------------------------------
        # LEVEL B: PER-STOCK PRECISION VIEW
        # ---------------------------------------------------------
        stock_stats = []
        for symbol, s_df in market_df.groupby('symbol'):
            s_profits = s_df[s_df['P/L'] > 0]
            s_losses = s_df[s_df['P/L'] <= 0]
            
            n_s = len(s_df)
            n_w = len(s_profits)
            n_l = len(s_losses)
            wr = (n_w / n_s * 100) if n_s > 0 else 0
            
            avg_w = s_profits['P/L'].mean() if n_w > 0 else 0
            avg_l = s_losses['P/L'].mean() if n_l > 0 else 0
            
            tot_p = s_profits['P/L'].sum()
            tot_l = s_losses['P/L'].sum()
            net = tot_p + tot_l
            
            stock_stats.append({
                'Stock': symbol,
                'Trades': n_s,
                'W/L': f"{n_w}W-{n_l}L",
                'Winrate': wr,
                'Avg Win': avg_w,
                'Avg Loss': avg_l,
                'Net P/L': net # Kept for sorting, but hidden in display
            })
            
        stock_df = pd.DataFrame(stock_stats).sort_values(by='Net P/L', ascending=False)
        
        print("\n🎯 LEVEL B: PER-STOCK PRECISION VIEW")
        print("-" * 115)
        header = f"{'Stock':<12} {'Trades':<8} {'W/L':<12} {'Winrate':<10} {'Avg Win':<10} {'Avg Loss':<10}"
        print(header)
        print("-" * 115)
        
        for _, r in stock_df.iterrows():
            print(f"{r['Stock']:<12} {r['Trades']:<8} {r['W/L']:<12} {r['Winrate']:<9.0f}% {r['Avg Win']:<+9.1f}% {r['Avg Loss']:<+9.1f}%")
        
        print("=" * 115)

        # Save to CSV
        stock_df.to_csv(f"data/stats_{market.lower()}.csv", index=False)

    print(f"\n✅ Stats updated for {len(markets)} markets.")

if __name__ == "__main__":
    calculate_stats_from_log()
