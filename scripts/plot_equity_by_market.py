#!/usr/bin/env python
"""
plot_equity_by_market.py - Equity Curve Charts by Market (V3)
==============================================================
Generates charts with GROSS and NET (after commission + slippage) equity curves.

Two chart types:
  1. Individual equity curves per market (TH, US, CN/HK, TW) — Gross vs Net
  2. Combined overlay of all markets — NET only

Commission & Slippage are deducted PER TRADE (round-trip).
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==========================================
# Configuration
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "equity_charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MARKET_FILES = {
    "THAI": "trade_history_THAI.csv",
    "US (NASDAQ)": "trade_history_US.csv",
    "CHINA/HK": "trade_history_CHINA.csv",
    "TAIWAN": "trade_history_TAIWAN.csv",
}

MARKET_COLORS = {
    "THAI": "#E65100",
    "US (NASDAQ)": "#00897B",
    "CHINA/HK": "#C62828",
    "TAIWAN": "#5C6BC0",
}

# Commission + Slippage per TRADE (round-trip %)
# คิดรวม ค่าคอมซื้อ+ขาย + Slippage ต่อ 1 ไม้
MARKET_COSTS = {
    "THAI": 0.20,          # 0.15% commission (round-trip) + 0.05% slippage
    "US (NASDAQ)": 0.10,   # ~$0 commission + 0.10% slippage/spread
    "CHINA/HK": 0.25,      # 0.10% stamp duty + 0.05% commission + 0.10% slippage
    "TAIWAN": 0.20,        # 0.14% commission (round-trip) + 0.06% slippage
}

# ==========================================
# Data Loading
# ==========================================
def load_market_data(market_name, filename):
    """Load trade history and build gross & net equity curves."""
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        print(f"   [SKIP] {market_name}: File not found ({filename})")
        return None

    df = pd.read_csv(filepath, on_bad_lines='skip')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    return_col = 'trader_return' if 'trader_return' in df.columns else 'actual_return'
    df[return_col] = pd.to_numeric(df[return_col], errors='coerce').fillna(0)

    cost = MARKET_COSTS.get(market_name, 0.15)
    df['net_return'] = df[return_col] - cost  # Deduct cost per trade

    # --- GROSS: Average return per date, then compound ---
    daily_gross = df.groupby(df['date'].dt.date)[return_col].mean().reset_index()
    daily_gross.columns = ['date', 'avg_return']
    daily_gross['date'] = pd.to_datetime(daily_gross['date'])
    daily_gross = daily_gross.sort_values('date').reset_index(drop=True)
    daily_gross['equity'] = (1 + daily_gross['avg_return'] / 100).cumprod() * 100

    # --- NET: Average NET return per date, then compound ---
    daily_net = df.groupby(df['date'].dt.date)['net_return'].mean().reset_index()
    daily_net.columns = ['date', 'avg_return']
    daily_net['date'] = pd.to_datetime(daily_net['date'])
    daily_net = daily_net.sort_values('date').reset_index(drop=True)
    daily_net['equity'] = (1 + daily_net['avg_return'] / 100).cumprod() * 100

    total_trades = len(df)
    gross_ret = daily_gross['equity'].iloc[-1] - 100
    net_ret = daily_net['equity'].iloc[-1] - 100
    total_cost = cost * total_trades

    print(f"   [OK] {market_name:12s}: {total_trades:>6,} trades | "
          f"Gross: {'+' if gross_ret >= 0 else ''}{gross_ret:.1f}% | "
          f"Net: {'+' if net_ret >= 0 else ''}{net_ret:.1f}% | "
          f"Cost/trade: {cost:.2f}%")

    return {
        'gross': daily_gross,
        'net': daily_net,
        'trades': total_trades,
        'cost': cost,
    }

# ==========================================
# Chart 1: Individual Market Charts (Gross vs Net)
# ==========================================
def plot_individual_markets(market_data):
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle("Equity Curves by Market — Gross vs Net (after Comm. + Slippage)",
                 fontsize=16, fontweight='bold', color='#222222', y=0.98)
    fig.patch.set_facecolor('white')

    for idx, (market_name, data) in enumerate(market_data.items()):
        ax = axes[idx // 2][idx % 2]
        ax.set_facecolor('white')

        if data is None:
            ax.text(0.5, 0.5, f"{market_name}\nNo Data", transform=ax.transAxes,
                    ha='center', va='center', fontsize=14, color='gray')
            continue

        color = MARKET_COLORS.get(market_name, '#333333')
        gross = data['gross']
        net = data['net']
        cost = data['cost']

        # Plot GROSS (dashed, lighter)
        ax.plot(gross['date'], gross['equity'], color=color, linewidth=1.2,
                alpha=0.4, linestyle='--', label='Gross')

        # Plot NET (solid, bold)
        ax.plot(net['date'], net['equity'], color=color, linewidth=2.0,
                alpha=0.9, label=f'Net (-{cost:.2f}%/trade)')

        # Fill net profit/loss
        ax.fill_between(net['date'], 100, net['equity'],
                        where=(net['equity'] >= 100), alpha=0.08, color='#4CAF50')
        ax.fill_between(net['date'], 100, net['equity'],
                        where=(net['equity'] < 100), alpha=0.08, color='#F44336')

        # Baseline
        ax.axhline(y=100, color='#999999', linestyle='--', alpha=0.5, linewidth=0.8)

        # Annotations
        gross_pct = gross['equity'].iloc[-1] - 100
        net_pct = net['equity'].iloc[-1] - 100

        gross_color = '#888888'
        net_color = '#2E7D32' if net_pct >= 0 else '#C62828'

        ax.annotate(f"Gross: {'+' if gross_pct >= 0 else ''}{gross_pct:.0f}%",
                    xy=(gross['date'].iloc[-1], gross['equity'].iloc[-1]),
                    fontsize=9, color=gross_color, fontweight='bold',
                    xytext=(5, 15), textcoords='offset points')

        ax.annotate(f"Net: {'+' if net_pct >= 0 else ''}{net_pct:.0f}%",
                    xy=(net['date'].iloc[-1], net['equity'].iloc[-1]),
                    fontsize=12, color=net_color, fontweight='bold',
                    xytext=(5, -5), textcoords='offset points')

        # Max drawdown on NET
        peak = net['equity'].expanding().max()
        dd = (net['equity'] - peak) / peak * 100
        max_dd = dd.min()
        max_dd_date = net['date'].iloc[dd.idxmin()]
        ax.annotate(f"Max DD: {max_dd:.1f}%", xy=(max_dd_date, net['equity'].iloc[dd.idxmin()]),
                    fontsize=8, color='#C62828', xytext=(-50, -20), textcoords='offset points')

        # Styling
        ax.set_title(f"{market_name} (Cost: {cost:.2f}%/trade)",
                     fontsize=13, fontweight='bold', color=color, pad=10)
        ax.set_ylabel("Equity (%)", color='#333333', fontsize=10)
        ax.tick_params(colors='#333333', labelsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.grid(True, alpha=0.15, color='#cccccc')
        ax.legend(loc='upper left', fontsize=9, framealpha=0.8,
                  facecolor='white', edgecolor='#cccccc')
        for spine in ax.spines.values():
            spine.set_color('#cccccc')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "equity_individual_gross_vs_net.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n   [SAVED] {out_path}")
    return out_path

# ==========================================
# Chart 2: Combined All Markets (Gross)
# ==========================================
def plot_combined_markets(market_data):
    fig, ax = plt.subplots(figsize=(18, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Sort by final equity descending for label offset
    end_values = []
    for market_name, data in market_data.items():
        if data is None:
            continue
        gross = data['gross']
        end_values.append((market_name, data, gross['equity'].iloc[-1]))
    end_values.sort(key=lambda x: x[2], reverse=True)

    for market_name, data, _ in end_values:
        color = MARKET_COLORS.get(market_name, '#333333')
        gross = data['gross']

        ax.plot(gross['date'], gross['equity'], color=color, linewidth=2.2, alpha=0.85,
                label=market_name)

    # Baseline
    ax.axhline(y=100, color='#999999', linestyle='--', alpha=0.5, linewidth=1)

    # End labels — stagger offsets to avoid overlap
    offsets = [12, -12, 24, -24]
    for i, (market_name, data, final_eq) in enumerate(end_values):
        color = MARKET_COLORS.get(market_name, '#333333')
        gross = data['gross']
        pct = final_eq - 100
        sign = "+" if pct >= 0 else ""
        text_color = '#2E7D32' if pct >= 0 else '#C62828'
        y_off = offsets[i % len(offsets)]
        ax.annotate(f"{market_name}: {sign}{pct:.0f}%",
                    xy=(gross['date'].iloc[-1], final_eq),
                    fontsize=11, fontweight='bold', color=text_color,
                    xytext=(15, y_off), textcoords='offset points', va='center')

    # Styling
    ax.set_title("Equity Curves — All Markets Combined",
                 fontsize=16, fontweight='bold', color='#222222', pad=15)
    ax.set_ylabel("Cumulative Equity (Start = 100)", color='#333333', fontsize=12)
    ax.set_xlabel("Date", color='#333333', fontsize=12)
    ax.tick_params(colors='#333333', labelsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.grid(True, alpha=0.15, color='#cccccc')
    for spine in ax.spines.values():
        spine.set_color('#cccccc')

    ax.legend(loc='upper left', fontsize=11, framealpha=0.9,
              facecolor='white', edgecolor='#cccccc', labelcolor='#333333')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "equity_all_markets_combined.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   [SAVED] {out_path}")
    return out_path

# ==========================================
# Main
# ==========================================
def main():
    print("\n" + "=" * 70)
    print("EQUITY CURVE GENERATOR - Gross vs Net (V3)")
    print("=" * 70)
    print("Cost assumptions (round-trip per trade):")
    for m, c in MARKET_COSTS.items():
        print(f"   {m:12s}: {c:.2f}% (commission + slippage)")
    print()

    market_data = {}
    for market_name, filename in MARKET_FILES.items():
        data = load_market_data(market_name, filename)
        market_data[market_name] = data

    print("\n[Generating Charts...]")
    path1 = plot_individual_markets(market_data)
    path2 = plot_combined_markets(market_data)

    print("\n" + "=" * 70)
    print("ALL CHARTS GENERATED")
    print(f"   Output: {OUTPUT_DIR}")
    print("=" * 70)

    return path1, path2

if __name__ == "__main__":
    main()
