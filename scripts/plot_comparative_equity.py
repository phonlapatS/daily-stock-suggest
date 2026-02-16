
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Global Symbol Map from config
SYMBOL_MAP = {}
for group in config.ASSET_GROUPS.values():
    for asset in group.get('assets', []):
        if 'name' in asset:
            SYMBOL_MAP[str(asset['symbol'])] = asset['name']

# User Directed Elite Selection (Cleanest View)
ELITE_TARGETS = {
    'TH': ['TPIPP', 'BYD', 'CPF', 'BGRIM'],
    'US': ['MDLZ', 'ODFL', 'ZM', 'ENPH'],
    'TW': ['2395'] # Map to ADVANTECH
}

def get_pnl_col(df):
    if 'trader_return' in df.columns:
        return df['trader_return']
    return df.apply(lambda row: row['actual_return'] if row['forecast'] == 'UP' else -row['actual_return'], axis=1)

def plot_consolidated_elite_comparison(metrics_df, output_file='data/elite_stocks_comparison.png'):
    """
    Creates a professional consolidated view of Elite stocks for Thai, US, and Taiwan markets.
    """
    market_configs = [
        ('Thai Market (SET)', 'logs/trade_history_THAI.csv', 'TH'),
        ('US Market (NASDAQ)', 'logs/trade_history_US.csv', 'US'),
        ('Taiwan Market (TWSE)', 'logs/trade_history_TAIWAN.csv', 'TW')
    ]
    
    plot_markets = [m for m in market_configs if os.path.exists(m[1])]
    if not plot_markets:
        print("⚠️ No suitable market log files found.")
        return

    n_plots = len(plot_markets)
    # Increase height per plot for clarity
    fig, axes = plt.subplots(n_plots, 1, figsize=(16, 7 * n_plots), dpi=100, sharex=False)
    if n_plots == 1: axes = [axes]

    for idx, (market_name, log_path, country_code) in enumerate(plot_markets):
        ax = axes[idx]
        
        # Priority 1: User specified list
        pass_list = ELITE_TARGETS.get(country_code, [])
        
        # Priority 2: Fallback to metrics if list is empty (not used here based on request)
        if not pass_list:
            pass_list = metrics_df[metrics_df['Country'] == country_code]['symbol'].unique().tolist()
            # Limit fallback to top 5 to avoid overcrowding
            pass_list = pass_list[:5]

        if not pass_list:
            ax.text(0.5, 0.5, f'No Elite stocks found for {market_name}', ha='center', va='center', fontsize=12)
            continue

        try:
            df = pd.read_csv(log_path)
            # Ensure symbol is string for lookup
            df['symbol'] = df['symbol'].astype(str)
            df['date'] = pd.to_datetime(df['date'])
            df['pnl'] = get_pnl_col(df)
            
            all_equity_values = []
            plot_count = 0

            for symbol in pass_list:
                s_df = df[df['symbol'] == str(symbol)].sort_values('date')
                if s_df.empty:
                    print(f"   > Stock {symbol} not found in {log_path}")
                    continue
                
                s_df['equity'] = s_df['pnl'].cumsum()
                
                display_name = SYMBOL_MAP.get(str(symbol), str(symbol))
                ax.plot(s_df['date'], s_df['equity'], label=f"{display_name} (N={len(s_df)})", linewidth=3, alpha=0.9)
                all_equity_values.extend(s_df['equity'].tolist())
                plot_count += 1

            ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
            ax.set_title(f'Elite Stocks Performance: {market_name}', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Individual Cumulative Return (%)', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.4)
            
            if plot_count > 0:
                ax.legend(loc='upper left', ncol=max(1, min(4, plot_count)), fontsize=11, frameon=True, framealpha=0.9, shadow=True)
            else:
                ax.text(0.5, 0.5, f'No data matched target list for {market_name}', ha='center', va='center')

            # Professional Scaling
            if all_equity_values:
                y_min, y_max = min(all_equity_values), max(all_equity_values)
                margin_factor = 0.5 if country_code == 'US' else 0.3
                range_val = y_max - y_min if y_max != y_min else 100.0
                ax.set_ylim(min(-20, y_min - range_val * margin_factor), max(100, y_max + range_val * margin_factor))

        except Exception as e:
            print(f"❌ Error plotting {market_name}: {e}")

    plt.tight_layout(pad=6.0)
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Refined Elite Comparison saved to: {output_file}")

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    metrics_path = 'data/symbol_performance.csv'
    if not os.path.exists(metrics_path):
        print("❌ symbol_performance.csv missing. Run calculate_metrics.py first.")
        exit()
        
    metrics_df = pd.read_csv(metrics_path)
    plot_consolidated_elite_comparison(metrics_df)
