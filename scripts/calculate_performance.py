import os
import pandas as pd
import numpy as np

def calculate_global_stats(log_dir="data/logs"):
    """
    Scans all market subdirectories and generates a summary 'Stats' table 
    for each, matching the user's Google Sheets format.
    """
    if not os.path.exists(log_dir):
        print(f"❌ Log directory {log_dir} not found.")
        return

    # Find all market subdirectories
    markets = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
    
    if not markets:
        # Check if logs exist directly in log_dir (legacy)
        markets = ["."] 

    for market in markets:
        market_path = os.path.join(log_dir, market)
        all_trades = []
        
        # Collect all closed trades from all files in this market
        for file in os.listdir(market_path):
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(market_path, file))
                if 'Status' in df.columns:
                    closed_trades = df[df['Status'] == 'CLOSED'].copy()
                    if not closed_trades.empty:
                        all_trades.append(closed_trades)

        if not all_trades:
            if market != ".":
                print(f"ℹ️ No closed trades found for market: {market.upper()}")
            continue

        full_df = pd.concat(all_trades, ignore_index=True)
        
        # 1. PER-STOCK DEEP DIVE (The Precision View)
        # ==========================================
        stock_stats = []
        for symbol, s_df in full_df.groupby('Stock'):
            s_df['P/L'] = pd.to_numeric(s_df['P/L'], errors='coerce')
            s_profits = s_df[s_df['P/L'] > 0]
            s_losses = s_df[s_df['P/L'] <= 0]
            
            n_trades = len(s_df)
            n_wins = len(s_profits)
            n_losses = n_trades - n_wins
            wr = (n_wins / n_trades * 100) if n_trades > 0 else 0
            
            a_win = s_profits['%P/L'].mean() if n_wins > 0 else 0
            a_loss = s_losses['%P/L'].mean() if n_losses > 0 else 0
            
            # Ratio (Profit Factor)
            total_p = s_profits['P/L'].sum()
            total_l = abs(s_losses['P/L'].sum())
            s_ratio = (total_p / total_l) if total_l != 0 else (99.0 if total_p > 0 else 0)
            
            net_pnl = s_df['%P/L'].sum()
            
            stock_stats.append({
                "Stock": symbol,
                "Trades": n_trades,
                "W/L": f"{n_wins}W-{n_losses}L",
                "Winrate": f"{wr:.0f}%",
                "Avg Win": f"{a_win:+.1f}%",
                "Avg Loss": f"{a_loss:+.1f}%",
                "Ratio": round(s_ratio, 2),
                "Net P/L": f"{net_pnl:+.1f}%"
            })
            
        stock_summary_df = pd.DataFrame(stock_stats).sort_values(by="Net P/L", ascending=False)

        # 2. MARKET SUMMARY (The Big Picture)
        # ==========================================
        full_df['P/L'] = pd.to_numeric(full_df['P/L'], errors='coerce')
        profits = full_df[full_df['P/L'] > 0]
        losses = full_df[full_df['P/L'] <= 0]

        n_profits = len(profits)
        n_losses = len(losses)
        total_trades = n_profits + n_losses
        
        avg_profit = profits['P/L'].mean() if n_profits > 0 else 0
        avg_loss = losses['P/L'].mean() if n_losses > 0 else 0 
        
        total_profit = profits['P/L'].sum()
        total_loss = losses['P/L'].sum()
        
        winrate = (n_profits / total_trades * 100) if total_trades > 0 else 0
        ratio = (total_profit / abs(total_loss)) if total_loss != 0 else 0

        summary_data = [
            {"Type": "Profit", "#": n_profits, "Avg Profit": round(avg_profit, 2), "Total P/L": round(total_profit, 2), "Ratio": round(ratio, 2), "Winrate": f"{winrate:.2f}%"},
            {"Type": "Loss", "#": n_losses, "Avg Loss": round(avg_loss, 2), "Total P/L": round(total_loss, 2), "Ratio": "", "Winrate": ""}
        ]
        summary_df = pd.DataFrame(summary_data)
        
        market_display = market.upper() if market != "." else "UNGROUPED"
        
        # DISPLAY LOGIC (High Clarity Wide Layout)
        # ==========================================
        line_w = 115
        print("\n" + "=" * line_w)
        print(f"🌍 MARKET: {market_display}")
        print("=" * line_w)
        
        print("\n📊 LEVEL A: MARKET SUMMARY")
        print("-" * line_w)
        header_a = f"{'Type':<12} {'#':<8} {'Avg Profit/Loss':<20} {'Total P/L':<20} {'Ratio':<12} {'Winrate':<15}"
        print(header_a)
        print("-" * line_w)
        for _, row in summary_df.iterrows():
            is_profit = row['Type'] == 'Profit'
            val_col = 'Avg Profit' if is_profit else 'Avg Loss'
            val = row[val_col] if not pd.isna(row[val_col]) else 0.0
            
            print(f"{row['Type']:<12} {row['#']:<8} {val:<20.2f} {row['Total P/L']:<20.2f} {str(row['Ratio']):<12} {str(row['Winrate']):<15}")
        
        print("\n🎯 LEVEL B: PER-STOCK PRECISION VIEW")
        print("-" * line_w)
        header_b = f"{'Stock':<15} {'Trades':<10} {'W/L':<15} {'Winrate':<12} {'Avg Win':<12} {'Avg Loss':<12} {'Ratio':<12} {'Net P/L':<15}"
        print(header_b)
        print("-" * line_w)
        for _, row in stock_summary_df.iterrows():
            print(f"{str(row['Stock']):<15} {str(row['Trades']):<10} {str(row['W/L']):<15} {str(row['Winrate']):<12} {str(row['Avg Win']):<12} {str(row['Avg Loss']):<12} {str(row['Ratio']):<12} {str(row['Net P/L']):<15}")
        print("=" * line_w)
        
        # Save to market-specific summary file
        summary_filename = f"data/performance_summary_{market.lower()}.csv" if market != "." else "data/performance_summary_global.csv"
        stock_summary_df.to_csv(f"data/stock_stats_{market.lower()}.csv", index=False)
        summary_df.to_csv(summary_filename, index=False)
        print(f"✅ Saved detailed stats to data/stock_stats_{market.lower()}.csv")
        print(f"✅ Summary saved to {summary_filename}")

if __name__ == "__main__":
    calculate_global_stats()
