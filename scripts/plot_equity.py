#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_equity.py - Plot Equity Curves เปรียบเทียบแต่ละตลาด
========================================================
V9.0 BALANCED: Position Sizing + Trailing Stop + ATR Cap
แสดง:
1. Equity Curve รวมทุกตลาด (US, Taiwan, China/HK)
2. Equity Curve แยกแต่ละตลาด (per stock)
3. Drawdown + Return Distribution
4. Summary Table + Cumulative Return
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a clean style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = '#FAFAFA'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['font.size'] = 10


def load_trade_data():
    """Load trade data from all market log files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, 'logs')
    
    files = {
        'US': os.path.join(log_dir, 'trade_history_US.csv'),
        'Taiwan': os.path.join(log_dir, 'trade_history_TAIWAN.csv'),
        'China/HK': os.path.join(log_dir, 'trade_history_CHINA.csv'),
        'Thai': os.path.join(log_dir, 'trade_history_THAI.csv'),
    }
    
    all_data = {}
    
    for market, filepath in files.items():
        if not os.path.exists(filepath):
            print(f"  Skip {market}: file not found")
            continue
        
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce')
        df['correct'] = pd.to_numeric(df['correct'], errors='coerce')
        if 'actual_return' in df.columns:
            df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
        if 'position_pct' in df.columns:
            df['position_pct'] = pd.to_numeric(df['position_pct'], errors='coerce')
        
        # Use all available data (no date filter - test period varies per market)
        df = df.sort_values('date').reset_index(drop=True)
        
        if len(df) > 0:
            all_data[market] = df
            n_symbols = df['symbol'].nunique()
            print(f"  {market}: {len(df)} trades, {n_symbols} symbols, "
                  f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    return all_data


def calc_equity_curve(df, initial_capital=10000):
    """
    Calculate equity curve from trades.
    Aggregates returns by date (avg across stocks on same day),
    then compounds daily to avoid unrealistic multi-stock multiplication.
    """
    df = df.sort_values('date').reset_index(drop=True)
    
    # Aggregate by date: average return per day (portfolio approach)
    daily = df.groupby('date')['trader_return'].mean().reset_index()
    daily = daily.sort_values('date').reset_index(drop=True)
    
    equity = [initial_capital]
    dates = [daily['date'].iloc[0] - pd.Timedelta(days=1)]
    
    for _, row in daily.iterrows():
        ret_pct = row['trader_return']
        if pd.isna(ret_pct):
            ret_pct = 0
        new_equity = equity[-1] * (1 + ret_pct / 100)
        equity.append(new_equity)
        dates.append(row['date'])
    
    return dates, equity


def calc_drawdown(equity):
    """Calculate drawdown from equity curve"""
    peak = np.maximum.accumulate(equity)
    drawdown = (np.array(equity) - peak) / peak * 100
    return drawdown


def calc_sharpe(returns, risk_free_rate=0.04):
    """Calculate annualized Sharpe Ratio"""
    if len(returns) < 2:
        return 0
    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf
    if excess.std() == 0:
        return 0
    return (excess.mean() / excess.std()) * np.sqrt(252)


def calc_calmar(total_return_pct, max_dd_pct, n_days=500):
    """Calculate Calmar Ratio (Annual Return / Max DD)"""
    annual_return = total_return_pct * (252 / max(n_days, 1))
    if max_dd_pct == 0:
        return 0
    return annual_return / abs(max_dd_pct)


def plot_all(all_data, output_dir):
    """Create comprehensive equity comparison plots"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Colors for each market
    colors = {
        'US': '#2196F3',        # Blue
        'Taiwan': '#4CAF50',    # Green
        'China/HK': '#FF5722',  # Red-Orange
        'Thai': '#9C27B0',      # Purple
    }
    
    markets_to_show = [m for m in all_data.keys()]
    
    # Pre-compute all stats
    stats = []
    for market in markets_to_show:
        df = all_data[market]
        n_trades = len(df)
        n_wins = (df['correct'] == 1).sum()
        accuracy = n_wins / n_trades * 100 if n_trades > 0 else 0
        
        wins_ret = df[df['correct'] == 1]['trader_return'].abs()
        losses_ret = df[df['correct'] == 0]['trader_return'].abs()
        avg_win = wins_ret.mean() if len(wins_ret) > 0 else 0
        avg_loss = losses_ret.mean() if len(losses_ret) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        total_return = df['trader_return'].sum()
        
        # Calculate max consecutive losses
        max_consec_loss = 0
        streak = 0
        for _, r in df.iterrows():
            if r['correct'] == 0:
                streak += 1
                max_consec_loss = max(max_consec_loss, streak)
            else:
                streak = 0
        
        # Sharpe Ratio
        sharpe = calc_sharpe(df['trader_return'] / 100)
        
        # Equity and DD
        dates, equity = calc_equity_curve(df)
        dd = calc_drawdown(equity)
        max_dd = min(dd)
        
        # Number of days
        n_days = (df['date'].max() - df['date'].min()).days
        
        # Calmar Ratio
        calmar = calc_calmar(total_return, max_dd, n_days)
        
        # Expectancy per trade
        expectancy = total_return / n_trades if n_trades > 0 else 0
        
        # Exit reasons
        exit_reasons = df['exit_reason'].value_counts().to_dict() if 'exit_reason' in df.columns else {}
        
        stats.append({
            'market': market, 'trades': n_trades, 'accuracy': accuracy,
            'avg_win': avg_win, 'avg_loss': avg_loss, 'rrr': rrr,
            'total_return': total_return, 'max_dd': max_dd,
            'max_consec_loss': max_consec_loss, 'sharpe': sharpe,
            'calmar': calmar, 'expectancy': expectancy,
            'n_days': n_days, 'exit_reasons': exit_reasons,
            'dates': dates, 'equity': equity, 'drawdown': dd
        })
    
    # ===================================================================
    # PLOT 1: Equity Curves Only (Clean View)
    # ===================================================================
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle('V10.0 Equity Curve Comparison\n'
                 'Prob 52-55% | RRR > 1.0 | Trailing Stop + Position Sizing', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # --- Panel 1: Combined Equity Curves ---
    ax1 = axes[0]
    for s in stats:
        market = s['market']
        color = colors.get(market, '#666')
        final_return = (s['equity'][-1] / s['equity'][0] - 1) * 100
        n_t = s['trades']
        ax1.plot(s['dates'], s['equity'], 
                 label=f"{market}  |  +{final_return:,.0f}%  |  {n_t:,} trades  |  Acc {s['accuracy']:.1f}%  |  RRR {s['rrr']:.2f}  |  Sharpe {s['sharpe']:.2f}", 
                 color=color, linewidth=2, alpha=0.9)
    
    ax1.axhline(y=10000, color='gray', linestyle='--', alpha=0.4, label='$10,000 Start')
    ax1.set_title('Equity Curves - All International Markets (Portfolio: avg daily return)', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Equity ($)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.grid(True, alpha=0.3)
    
    # Fill profit/loss zones
    for s in stats:
        color = colors.get(s['market'], '#666')
        ax1.fill_between(s['dates'], 10000, s['equity'],
                         where=[e >= 10000 for e in s['equity']], alpha=0.05, color=color)
    
    # --- Panel 2: Drawdown (Underwater Chart) ---
    ax2 = axes[1]
    for s in stats:
        market = s['market']
        color = colors.get(market, '#666')
        max_dd = min(s['drawdown'])
        ax2.fill_between(s['dates'], s['drawdown'], 0, alpha=0.25, color=color)
        ax2.plot(s['dates'], s['drawdown'], color=color, linewidth=1, alpha=0.8,
                label=f"{market}  |  Max DD: {max_dd:.1f}%")
    
    ax2.set_title('Drawdown (Underwater Chart)', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Drawdown (%)', fontsize=11)
    ax2.legend(loc='lower left', fontsize=9, framealpha=0.9)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    path1 = os.path.join(output_dir, 'equity_comparison_v10.png')
    fig.savefig(path1, dpi=150, bbox_inches='tight')
    print(f"\n  Saved: {path1}")
    plt.close(fig)
    
    # ===================================================================
    # PLOT 2: Best Stock Per Market (Top 1 each)
    # ===================================================================
    n_markets = len(markets_to_show)
    fig2, ax2 = plt.subplots(1, 1, figsize=(16, 8))
    fig2.suptitle('V10.1 Best Stock Per Market - Head-to-Head Comparison\n'
                  'Top 1 stock from each market by Sharpe Ratio', 
                  fontsize=13, fontweight='bold', y=0.98)
    
    best_stocks = []
    for market in markets_to_show:
        df = all_data[market]
        symbols = df['symbol'].unique()
        
        best_sym = None
        best_sharpe = -999
        
        for sym in symbols:
            sym_df = df[df['symbol'] == sym].copy()
            if len(sym_df) < 20:
                continue
            rets = sym_df['trader_return']
            if rets.std() > 0:
                sharpe = (rets.mean() / rets.std()) * np.sqrt(252)
            else:
                sharpe = 0
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_sym = sym
        
        if best_sym:
            best_stocks.append((market, best_sym, best_sharpe))
    
    market_line_styles = {'US': '-', 'Taiwan': '-', 'China/HK': '-', 'Thai': '-'}
    
    for market, sym, sharpe_val in best_stocks:
        color = colors.get(market, '#666')
        sym_df = all_data[market][all_data[market]['symbol'] == sym].copy()
        dates, equity = calc_equity_curve(sym_df)
        final_ret = (equity[-1] / equity[0] - 1) * 100
        n_trades = len(sym_df)
        acc = (sym_df['correct'] == 1).sum() / n_trades * 100
        
        wins_ret = sym_df[sym_df['correct'] == 1]['trader_return']
        losses_ret = sym_df[sym_df['correct'] == 0]['trader_return']
        avg_win = wins_ret.mean() if len(wins_ret) > 0 else 0
        avg_loss = losses_ret.abs().mean() if len(losses_ret) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        ax2.plot(dates, equity, 
                label=f'{sym} ({market})  |  +{final_ret:,.0f}%  |  {n_trades} trades  |  Acc {acc:.1f}%  |  RRR {rrr:.2f}  |  Sharpe {sharpe_val:.2f}',
                color=color, linewidth=2.5, alpha=0.9,
                linestyle=market_line_styles.get(market, '-'))
    
    ax2.axhline(y=10000, color='gray', linestyle='--', alpha=0.4, label='$10,000 Start')
    ax2.set_ylabel('Equity ($)', fontsize=11)
    ax2.set_xlabel('Date', fontsize=11)
    ax2.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    
    path2 = os.path.join(output_dir, 'equity_per_stock_v10.png')
    fig2.savefig(path2, dpi=150, bbox_inches='tight')
    print(f"  Saved: {path2}")
    plt.close(fig2)
    
    # ===================================================================
    # PLOT 3: Total Portfolio View (All Markets Combined)
    # ===================================================================
    fig3, axes3 = plt.subplots(2, 1, figsize=(16, 12))
    fig3.suptitle('V10.0 Total Portfolio - All Markets Combined\n'
                  'Equal weight allocation across markets',
                  fontsize=14, fontweight='bold', y=0.99)
    
    # --- Build combined portfolio using REAL equity curves ---
    n_mkts = len(markets_to_show)
    initial = 10000
    alloc_per_market = initial / n_mkts  # Equal weight per market
    
    # Step 1: Calc each market's equity curve (same as calc_equity_curve)
    mkt_curves = {}
    for market in markets_to_show:
        df = all_data[market]
        dates, equity = calc_equity_curve(df, initial_capital=alloc_per_market)
        mkt_curves[market] = (dates, equity)
    
    # Step 2: Align all equity curves to a common date index by interpolation
    # Collect all dates
    all_dates_set = set()
    for market in markets_to_show:
        all_dates_set.update(mkt_curves[market][0])
    all_dates_sorted = sorted(all_dates_set)
    
    # Build a DataFrame of equity per market aligned by date
    eq_df = pd.DataFrame(index=all_dates_sorted)
    for market in markets_to_show:
        dt, eq = mkt_curves[market]
        s = pd.Series(eq, index=dt)
        # Remove duplicates (keep last)
        s = s[~s.index.duplicated(keep='last')]
        eq_df[market] = s
    
    # Forward-fill: before first date of a market, use its initial allocation
    for market in markets_to_show:
        first_date = mkt_curves[market][0][0]
        eq_df.loc[eq_df.index < first_date, market] = alloc_per_market
    eq_df = eq_df.ffill()
    eq_df = eq_df.fillna(alloc_per_market)
    
    # Step 3: Portfolio = sum of all market equities
    eq_df['portfolio'] = eq_df[markets_to_show].sum(axis=1)
    
    port_dates = eq_df.index.tolist()
    port_equity = eq_df['portfolio'].values
    
    port_equity_arr = np.array(port_equity)
    port_peak = np.maximum.accumulate(port_equity_arr)
    port_dd = (port_equity_arr - port_peak) / port_peak * 100
    
    # --- Panel A: Equity Curves ---
    ax_eq = axes3[0]
    
    # Plot individual markets (thin, faded)
    for market in markets_to_show:
        color = colors.get(market, '#666')
        dt, eq = mkt_curves[market]
        final_ret = (eq[-1] / eq[0] - 1) * 100
        ax_eq.plot(dt, eq, color=color, linewidth=1.5, alpha=0.5,
                  label=f'{market} (+{final_ret:,.0f}%)')
    
    # Plot portfolio (bold)
    port_final_ret = (port_equity[-1] / initial - 1) * 100
    total_trades = sum(s['trades'] for s in stats)
    
    # Portfolio stats: calc daily % changes
    port_pct_changes = pd.Series(port_equity).pct_change().dropna() * 100
    port_sharpe = (port_pct_changes.mean() / port_pct_changes.std()) * np.sqrt(252) if port_pct_changes.std() > 0 else 0
    port_max_dd = min(port_dd)
    ax_eq.plot(port_dates, port_equity, color='black', linewidth=3, alpha=0.9,
              label=f'TOTAL PORTFOLIO  |  +{port_final_ret:,.0f}%  |  {total_trades:,} trades  |  Sharpe {port_sharpe:.2f}')
    
    ax_eq.axhline(y=initial, color='gray', linestyle='--', alpha=0.4, label=f'${initial:,} Start')
    ax_eq.fill_between(port_dates, initial, port_equity,
                      where=[e >= initial for e in port_equity], alpha=0.08, color='green')
    
    ax_eq.set_title('Equity Curves: Individual Markets vs Total Portfolio', fontweight='bold', fontsize=12)
    ax_eq.set_ylabel('Equity ($)', fontsize=11)
    ax_eq.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax_eq.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_eq.xaxis.set_major_locator(mdates.YearLocator())
    ax_eq.grid(True, alpha=0.3)
    
    # --- Panel B: Portfolio Drawdown vs Individual Market DDs ---
    ax_dd = axes3[1]
    
    # Individual market DDs (thin, faded)
    for market in markets_to_show:
        color = colors.get(market, '#666')
        mkt_eq_series = eq_df[market].values
        mkt_dates_series = eq_df.index.tolist()
        pk = np.maximum.accumulate(mkt_eq_series)
        dd = (mkt_eq_series - pk) / pk * 100
        mkt_max_dd = min(dd)
        ax_dd.fill_between(mkt_dates_series, dd, 0, alpha=0.1, color=color)
        ax_dd.plot(mkt_dates_series, dd, color=color, linewidth=0.8, alpha=0.5,
                  label=f'{market} (Max DD: {mkt_max_dd:.1f}%)')
    
    # Portfolio DD (bold)
    ax_dd.fill_between(port_dates, port_dd, 0, alpha=0.25, color='black')
    ax_dd.plot(port_dates, port_dd, color='black', linewidth=2, alpha=0.9,
              label=f'PORTFOLIO (Max DD: {port_max_dd:.1f}%)')
    
    ax_dd.set_title('Drawdown: Portfolio vs Individual Markets', fontweight='bold', fontsize=12)
    ax_dd.set_ylabel('Drawdown (%)', fontsize=11)
    ax_dd.legend(loc='lower left', fontsize=9, framealpha=0.9)
    ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_dd.xaxis.set_major_locator(mdates.YearLocator())
    ax_dd.grid(True, alpha=0.3)
    
    # Add annotation box with portfolio summary
    summary_text = (f'Portfolio Summary\n'
                    f'{"─" * 25}\n'
                    f'Total Return: +{port_final_ret:,.0f}%\n'
                    f'Max Drawdown: {port_max_dd:.1f}%\n'
                    f'Sharpe Ratio: {port_sharpe:.2f}\n'
                    f'Total Trades: {total_trades:,}\n'
                    f'Markets: {len(markets_to_show)}')
    ax_dd.text(0.98, 0.02, summary_text, transform=ax_dd.transAxes,
              fontsize=9, fontfamily='monospace', verticalalignment='bottom',
              horizontalalignment='right',
              bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    path3 = os.path.join(output_dir, 'portfolio_total_v10.png')
    fig3.savefig(path3, dpi=150, bbox_inches='tight')
    print(f"  Saved: {path3}")
    plt.close(fig3)
    
    return [path1, path2, path3]


def main():
    print("\n" + "=" * 70)
    print("  EQUITY CURVE COMPARISON - V9.0 Balanced RM")
    print("=" * 70)
    
    print("\n Loading trade data...")
    all_data = load_trade_data()
    
    if not all_data:
        print("\n No trade data found! Run backtest first.")
        return
    
    print("\n Generating plots...")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'plots')
    
    paths = plot_all(all_data, output_dir)
    
    print("\n" + "=" * 70)
    print("  DONE! Generated plots:")
    for p in paths:
        print(f"    {p}")
    print("=" * 70)


if __name__ == "__main__":
    main()
