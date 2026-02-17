#!/usr/bin/env python
"""
plot_equity_curves.py
=====================

Generate equity curves for each market (TH, US, CN, TW, GL) and combined equity curves.
Saves separate PNG files for each market.

IMPORTANT: Filters trades by the same criteria as calculate_metrics.py to show accurate performance.

Usage:
    python scripts/plot_equity_curves.py
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import glob

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set style (use default, override per-chart)
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# QUALIFYING SYMBOLS — from calculate_metrics.py output
# Only these symbols passed the quality criteria per market.
# Update this list when re-running calculate_metrics.
# ============================================================================
QUALIFYING_SYMBOLS = {
    'TH': [
        # Updated: RRR >= 1.5 (เพิ่มจาก 1.3 → 1.5) - Prob >= 60%, Count >= 30
        # ตัดออก: QH (RRR 1.44), BANPU (RRR 1.38), BCPG (RRR 1.35), TPIPL (RRR 1.48)
        'BAM', 'JTS', 'ICHI', 'HANA', 'EPG', 'PTTGC', 'RCL', 'CHG', 'DELTA',
        'THANI', 'ERW', 'ONEE', 'SNNP', 'SUPER', 'SSP', 'NEX', 'FORTH',
        'PTG', 'STA', 'PSL', 'MAJOR', 'OR', 'BCH', 'RATCH',
        'TTB', 'TASCO',
    ],
    'US': [
        'WBD', 'ENPH', 'ROKU', 'DXCM', 'DDOG', 'MRNA', 'BKR',
    ],
    'CN': [
        '9868', '9618', '9888',  # XPeng, JD.com, Baidu (HKEX codes)
    ],
    'TW': [
        '3711', '2330', '2303', '2382',  # ASE, TSMC, UMC, Quanta (TWSE codes)
    ],
    'GL': None,  # Metals — include all (Gold/Silver)
}

def load_all_trade_logs():
    """Load and merge all trade_history_*.csv files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("❌ No trade history files found.")
        return pd.DataFrame()
    
    dfs = []
    print(f"📂 Loading trade logs from {len(files)} files...")
    for f in files:
        try:
            df = pd.read_csv(f, on_bad_lines='skip', engine='python')
            # Add country info based on filename
            filename = os.path.basename(f).upper()
            if 'THAI' in filename: 
                df['Country'] = 'TH'
            elif 'US' in filename: 
                df['Country'] = 'US'
            elif 'CHINA' in filename: 
                df['Country'] = 'CN'
            elif 'TAIWAN' in filename: 
                df['Country'] = 'TW'
            elif 'METALS' in filename: 
                df['Country'] = 'GL'
            else: 
                df['Country'] = 'GL'
            
            print(f"   ✅ Loaded {len(df)} trades from {os.path.basename(f)}")
            dfs.append(df)
        except Exception as e:
            print(f"   ⚠️ Error reading {os.path.basename(f)}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    all_trades = pd.concat(dfs, ignore_index=True)
    print(f"✅ Total: {len(all_trades)} trades loaded")
    return all_trades

def filter_trades_by_criteria(trades, country_code):
    """
    Filter trades by the same criteria as calculate_metrics.py for each market.
    This ensures equity curve shows only trades that pass the display criteria.
    
    Args:
        trades: DataFrame with trades for a specific country
        country_code: Country code ('TH', 'US', 'CN', 'TW', 'GL')
    
    Returns:
        Filtered DataFrame with only trades from symbols that pass criteria
    """
    if trades.empty:
        return pd.DataFrame()
    
    # Calculate pnl (same as calculate_metrics.py)
    trades = trades.copy()
    trades['actual_return'] = pd.to_numeric(trades['actual_return'], errors='coerce')
    trades['pnl'] = trades.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
    
    # Calculate metrics per symbol (same as calculate_metrics.py)
    symbol_metrics = []
    for symbol in trades['symbol'].unique():
        symbol_trades = trades[trades['symbol'] == symbol]
        
        wins = symbol_trades[symbol_trades['pnl'] > 0]
        losses = symbol_trades[symbol_trades['pnl'] <= 0]
        
        count = len(symbol_trades)
        prob = len(wins) / count * 100 if count > 0 else 0
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        symbol_metrics.append({
            'symbol': symbol,
            'count': count,
            'prob': prob,
            'rrr': rrr
        })
    
    metrics_df = pd.DataFrame(symbol_metrics)
    
    # Apply filters based on country (same as calculate_metrics.py)
    # V14.2: ใช้เกณฑ์เข้มงวด Prob > 60% และ RRR > 2.0 เท่านั้น
    if country_code == 'TH':
        # THAI: Prob > 60%, RRR > 2.0, Count >= 5
        filtered_symbols = metrics_df[
            (metrics_df['prob'] > 60.0) &  # V14.2: เปลี่ยนจาก >= เป็น >
            (metrics_df['rrr'] > 2.0) &  # V14.2: เปลี่ยนจาก >= 1.3 เป็น > 2.0
            (metrics_df['count'] >= 5)  # V14.2: ลดจาก 30 เป็น 5
        ]['symbol'].tolist()
    elif country_code == 'US':
        # US: Prob >= 60%, RRR >= 1.5, Count >= 15 (คงเดิม)
        filtered_symbols = metrics_df[
            (metrics_df['prob'] >= 60.0) & 
            (metrics_df['rrr'] >= 1.5) &
            (metrics_df['count'] >= 15)
        ]['symbol'].tolist()
    elif country_code in ['CN', 'HK']:
        # CHINA/HK: Prob > 60%, RRR > 2.0, Count >= 5
        filtered_symbols = metrics_df[
            (metrics_df['prob'] > 60.0) &  # V14.2: เปลี่ยนจาก >= เป็น >
            (metrics_df['rrr'] > 2.0) &  # V14.2: เปลี่ยนจาก >= 1.2 เป็น > 2.0
            (metrics_df['count'] >= 5)  # V14.2: ลดจาก 15 เป็น 5
        ]['symbol'].tolist()
    elif country_code == 'TW':
        # TAIWAN: Prob >= 50%, RRR >= 1.0, Count >= 15
        filtered_symbols = metrics_df[
            (metrics_df['prob'] >= 50.0) & 
            (metrics_df['rrr'] >= 1.0) &
            (metrics_df['count'] >= 15)
        ]['symbol'].tolist()
    elif country_code == 'GL':
        # METALS: Use all trades (no filter for now, or apply 30min/15min filters separately)
        # For now, return all trades
        return trades
    else:
        # Default: return all trades
        return trades
    
    # Filter trades to only include symbols that pass criteria
    filtered_trades = trades[trades['symbol'].isin(filtered_symbols)]
    
    return filtered_trades

def calculate_equity_curve(trades, initial_capital=1000):
    """
    Calculate equity curve from trades - using same logic as calculate_metrics.py.
    Shows actual win/loss performance from trades (not exponential compound).
    
    Uses the same pnl calculation as calculate_metrics.py:
    - pnl = actual_return * (1 if forecast == 'UP' else -1)
    - This matches the Prob%, RRR, AvgWin%, AvgLoss% shown in calculate_metrics.py
    
    Args:
        trades: DataFrame with columns: date, actual_return, forecast, correct
        initial_capital: Starting capital (default 1000)
    
    Returns:
        DataFrame with columns: date, equity, cumulative_return, drawdown, return
    """
    if trades.empty:
        return pd.DataFrame()
    
    # Sort by date
    trades = trades.copy()
    trades['date'] = pd.to_datetime(trades['date'])
    trades = trades.sort_values('date').reset_index(drop=True)
    
    # Use same logic as calculate_metrics.py
    if 'actual_return' not in trades.columns:
        print("⚠️ No actual_return column found")
        return pd.DataFrame()
    
    # Calculate pnl using same method as calculate_metrics.py
    # pnl = actual_return * direction (UP = 1, DOWN = -1)
    trades['actual_return'] = pd.to_numeric(trades['actual_return'], errors='coerce').fillna(0)
    
    # Apply direction multiplier (same as calculate_metrics.py line 303)
    if 'forecast' in trades.columns:
        trades['pnl'] = trades.apply(
            lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
            axis=1
        )
    else:
        # Fallback: use actual_return directly if no forecast
        trades['pnl'] = trades['actual_return']
    
    # Calculate equity using SIMPLE CUMULATIVE SUM (no compounding, no position sizing)
    # This matches calculate_metrics.py which shows AvgWin% and AvgLoss% as simple averages
    # actual_return is already the return % of the trade (price-based), not capital-based
    # So we just sum up the pnl% to get cumulative return, then apply to initial capital
    
    equity = [initial_capital]
    cumulative_return_pct = 0  # Cumulative return in % (simple sum, not compound)
    
    for pnl_pct in trades['pnl'].values:
        # pnl_pct is in % (e.g., 2.5% = 2.5, -1.5% = -1.5)
        # Simple cumulative: just add pnl% to cumulative return
        # This matches how calculate_metrics.py calculates AvgWin% and AvgLoss%
        # Equity = Initial Capital * (1 + cumulative_return_pct / 100)
        cumulative_return_pct += pnl_pct
        new_equity = initial_capital * (1 + cumulative_return_pct / 100.0)
        equity.append(new_equity)
    
    # Remove first element (initial capital) to match dates length
    equity = equity[1:]
    
    # Calculate cumulative return %
    equity_array = np.array(equity)
    cumulative_return = ((equity_array / initial_capital) - 1) * 100
    
    # Calculate drawdown
    running_max = np.maximum.accumulate(equity_array)
    drawdown = ((equity_array - running_max) / running_max) * 100
    
    result = pd.DataFrame({
        'date': trades['date'].values,
        'equity': equity,
        'cumulative_return': cumulative_return,
        'drawdown': drawdown,
        'return': trades['pnl'].values  # Use pnl (with direction) as return
    })
    
    return result

def plot_single_market_equity(equity_df, market_name, country_code, output_dir='data/plots'):
    """
    Plot simple equity curve for a single market (line chart with white background).
    
    Args:
        equity_df: DataFrame from calculate_equity_curve()
        market_name: Market name (e.g., 'US', 'THAI', 'CHINA', 'TAIWAN', 'METALS')
        country_code: Country code (e.g., 'US', 'TH', 'CN', 'TW', 'GL')
        output_dir: Output directory for PNG files
    """
    if equity_df.empty:
        print(f"⚠️ No data for {market_name}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    dates = equity_df['date']
    equity = equity_df['equity']
    initial_capital = equity.iloc[0]
    
    # Plot equity curve
    ax.plot(dates, equity, linewidth=2.5, color='#0066ff', label=f'{market_name} Equity', alpha=0.9)
    
    # Add horizontal line at initial capital
    ax.axhline(y=initial_capital, color='gray', linestyle='--', linewidth=1.5, alpha=0.6, label='Initial Capital')
    
    # Formatting
    ax.set_xlabel('Date', fontsize=13, fontweight='bold', color='black')
    ax.set_ylabel('Equity ($)', fontsize=13, fontweight='bold', color='black')
    ax.set_title(f'{market_name} Market - Equity Curve', 
                fontsize=16, fontweight='bold', pad=25, color='black')
    
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray', which='both')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95, facecolor='white', edgecolor='gray', frameon=True)
    
    # Format axes
    ax.tick_params(colors='black', labelsize=10)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Calculate and display statistics
    final_equity = equity.iloc[-1]
    total_return = equity_df['cumulative_return'].iloc[-1]
    max_drawdown = equity_df['drawdown'].min()
    total_trades = len(equity_df)
    winning_trades = (equity_df['return'] > 0).sum()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    stats_text = (
        f'Final Equity: ${final_equity:,.2f}\n'
        f'Total Return: {total_return:.2f}%\n'
        f'Max Drawdown: {max_drawdown:.2f}%\n'
        f'Total Trades: {total_trades}\n'
        f'Win Rate: {win_rate:.1f}%'
    )
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, color='black', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    
    plt.tight_layout()
    
    # Save PNG
    output_path = os.path.join(output_dir, f'equity_{market_name.upper()}.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    plt.close()

def filter_by_qualifying_symbols(trades, country_code):
    """
    Filter trades to only include qualifying symbols for a given market.
    V14.3: ใช้ qualifying symbols จาก calculate_metrics.py output แทน hardcoded list
    """
    # Try to load from symbol_performance.csv (created by calculate_metrics.py)
    perf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'symbol_performance.csv')
    if os.path.exists(perf_file):
        try:
            perf_df = pd.read_csv(perf_file)
            # Map country codes
            country_map = {'TH': 'TH', 'US': 'US', 'CN': 'CN', 'HK': 'HK', 'TW': 'TW', 'GL': 'GL'}
            target_country = country_map.get(country_code, country_code)
            
            # Get qualifying symbols based on criteria (same as calculate_metrics.py)
            if country_code == 'TH':
                # THAI: Prob > 60%, RRR > 2.0, Count >= 5
                qualifying = perf_df[
                    (perf_df['Country'] == target_country) &
                    (perf_df['Prob%'] > 60.0) &
                    (perf_df['RR_Ratio'] > 2.0) &
                    (perf_df['Count'] >= 5)
                ]
            elif country_code == 'US':
                # US: Prob >= 60%, RRR >= 1.5, Count >= 15
                qualifying = perf_df[
                    (perf_df['Country'] == target_country) &
                    (perf_df['Prob%'] >= 60.0) &
                    (perf_df['RR_Ratio'] >= 1.5) &
                    (perf_df['Count'] >= 15)
                ]
            elif country_code in ['CN', 'HK']:
                # CHINA/HK: Prob > 60%, RRR > 2.0, Count >= 5
                qualifying = perf_df[
                    ((perf_df['Country'] == 'CN') | (perf_df['Country'] == 'HK')) &
                    (perf_df['Prob%'] > 60.0) &
                    (perf_df['RR_Ratio'] > 2.0) &
                    (perf_df['Count'] >= 5)
                ]
            elif country_code == 'TW':
                # TAIWAN: Prob >= 50%, RRR >= 1.0, Count >= 15
                qualifying = perf_df[
                    (perf_df['Country'] == target_country) &
                    (perf_df['Prob%'] >= 50.0) &
                    (perf_df['RR_Ratio'] >= 1.0) &
                    (perf_df['Count'] >= 15)
                ]
            else:
                # METALS or other: return all trades
                return trades
            
            if not qualifying.empty:
                qualifying_symbols = qualifying['symbol'].astype(str).str.upper().str.strip().tolist()
                # Normalize symbol names for matching
                trades_copy = trades.copy()
                trades_copy['_sym_upper'] = trades_copy['symbol'].astype(str).str.upper().str.strip()
                filtered = trades_copy[trades_copy['_sym_upper'].isin(qualifying_symbols)].copy()
                filtered.drop(columns=['_sym_upper'], inplace=True)
                return filtered
        except Exception as e:
            print(f"   ⚠️ Error loading symbol_performance.csv: {e}")
    
    # Fallback: Use hardcoded QUALIFYING_SYMBOLS
    symbols = QUALIFYING_SYMBOLS.get(country_code)
    if symbols is None:
        return trades  # No filter (e.g. Metals — include all)
    
    # Normalize symbol names for matching (handle mixed types)
    trades_copy = trades.copy()
    trades_copy['_sym_upper'] = trades_copy['symbol'].astype(str).str.upper().str.strip()
    qualifying_upper = [s.upper().strip() for s in symbols]
    
    filtered = trades_copy[trades_copy['_sym_upper'].isin(qualifying_upper)].copy()
    filtered.drop(columns=['_sym_upper'], inplace=True)
    return filtered


def plot_all_markets_combined(all_trades, output_dir='data/plots'):
    """
    Plot all markets in a single chart — filtered by qualifying symbols.
    Clean style matching equity_per_market_clean.png.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Market configuration
    # V14.3: เอา Metals market ออก (ยังไม่ได้ทำ)
    markets_config = {
        'US': {'name': 'US (NASDAQ)',      'color': '#0077CC', 'label': 'US Market'},
        'TW': {'name': 'Taiwan (TWSE)',    'color': '#FF8800', 'label': 'Taiwan Market'},
        'CN': {'name': 'China/HK (HKEX)', 'color': '#CC2222', 'label': 'China/HK Market'},
        'TH': {'name': 'Thai (SET)',       'color': '#22AA44', 'label': 'Thai Market'},
        # 'GL': {'name': 'Metals',           'color': '#7733CC', 'label': 'Metals Market'},  # V14.3: เอาออก (ยังไม่ได้ทำ)
    }

    # Calculate equity curves for each market (filtered by qualifying symbols)
    equity_curves = {}
    all_filtered_dfs = []

    for country_code, cfg in markets_config.items():
        market_trades = all_trades[all_trades['Country'] == country_code].copy()
        if market_trades.empty:
            continue

        # Filter to qualifying symbols only (use same criteria as calculate_metrics.py)
        # V14.3: ใช้ filter_by_qualifying_symbols ที่อ่านจาก symbol_performance.csv
        filtered = filter_by_qualifying_symbols(market_trades, country_code)
        if filtered.empty:
            print(f"   ⚠️ No qualifying trades for {cfg['label']}")
            continue

        n_symbols = filtered['symbol'].nunique()
        print(f"   ✅ {cfg['label']}: {len(filtered)} trades from {n_symbols} qualifying symbols (from {len(market_trades)} total)")

        equity_df = calculate_equity_curve(filtered)
        if equity_df.empty:
            continue

        wins = (equity_df['return'] > 0).sum()
        wr = (wins / len(equity_df)) * 100 if len(equity_df) > 0 else 0
        ret = equity_df['cumulative_return'].iloc[-1]

        equity_curves[country_code] = {
            'data': equity_df,
            'config': cfg,
            'trades_count': len(filtered),
            'symbols_count': n_symbols,
            'win_rate': wr,
            'total_return': ret,
        }
        all_filtered_dfs.append(filtered)

    # Combined TOTAL PORTFOLIO from filtered trades
    equity_df_combined = pd.DataFrame()
    combined_return = 0
    combined_wr = 0
    total_filtered_trades = 0
    if all_filtered_dfs:
        all_filtered = pd.concat(all_filtered_dfs, ignore_index=True)
        total_filtered_trades = len(all_filtered)
        equity_df_combined = calculate_equity_curve(all_filtered)
        if not equity_df_combined.empty:
            wins_c = (equity_df_combined['return'] > 0).sum()
            combined_wr = (wins_c / len(equity_df_combined)) * 100 if len(equity_df_combined) > 0 else 0
            combined_return = equity_df_combined['cumulative_return'].iloc[-1]

    # --- Create the plot ---
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Sort by final equity descending
    sorted_curves = sorted(equity_curves.items(),
                           key=lambda x: x[1]['data']['equity'].iloc[-1], reverse=True)

    # Plot each market
    for country_code, curve in sorted_curves:
        cfg = curve['config']
        eq = curve['data']
        n = curve['trades_count']
        ns = curve['symbols_count']
        wr = curve['win_rate']
        ret = curve['total_return']
        sign = "+" if ret >= 0 else ""

        ax.plot(eq['date'], eq['equity'], linewidth=2.2, color=cfg['color'], alpha=0.85,
                label=f"{cfg['name']} | {ns} stocks | {n} trades | WR {wr:.0f}% | {sign}{ret:.0f}%")

    # Plot TOTAL PORTFOLIO (black dashed)
    if not equity_df_combined.empty:
        sign_c = "+" if combined_return >= 0 else ""
        ax.plot(equity_df_combined['date'], equity_df_combined['equity'],
                linewidth=2.8, color='black', linestyle='--', alpha=0.7,
                label=f"TOTAL PORTFOLIO | {total_filtered_trades} trades | WR {combined_wr:.0f}% | {sign_c}{combined_return:.0f}%")

    # Baseline at initial capital
    if equity_curves:
        first_eq = list(equity_curves.values())[0]['data']['equity'].iloc[0]
        ax.axhline(y=first_eq, color='#999999', linestyle='--', linewidth=1, alpha=0.4)

    # End labels — smart y-positioning to prevent overlap
    all_endpoints = []
    for country_code, curve in sorted_curves:
        cfg = curve['config']
        eq = curve['data']
        all_endpoints.append((cfg['label'], eq['date'].iloc[-1], eq['equity'].iloc[-1], cfg['color']))
    if not equity_df_combined.empty:
        all_endpoints.append(('TOTAL PORTFOLIO',
                              equity_df_combined['date'].iloc[-1],
                              equity_df_combined['equity'].iloc[-1],
                              'black'))

    # Sort descending by y and enforce min gap
    all_endpoints.sort(key=lambda x: x[2], reverse=True)
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0] if equity_curves else 1
    min_gap = y_range * 0.035
    adjusted_y = []
    for i, (_, _, eq_val, _) in enumerate(all_endpoints):
        y = eq_val
        if adjusted_y and adjusted_y[-1] - y < min_gap:
            y = adjusted_y[-1] - min_gap
        adjusted_y.append(y)

    for i, (lbl, dt, eq_val, clr) in enumerate(all_endpoints):
        y_offset = adjusted_y[i] - eq_val  # data-space offset
        ax.annotate(f" {lbl}", xy=(dt, eq_val),
                    xytext=(12, y_offset * 0.8 if abs(y_offset) > 5 else 0),
                    textcoords='offset points',
                    fontsize=10, fontweight='bold', color=clr, va='center')

    # Styling
    total_symbols = sum(c['symbols_count'] for c in equity_curves.values())
    ax.set_title(f"PredictPlus1 — Equity Curve (Qualifying Stocks Only, {total_symbols} stocks)",
                 fontsize=15, fontweight='bold', color='#222222', pad=15)
    ax.set_ylabel("Equity ($)", fontsize=13, color='#333333')
    ax.set_xlabel("Date", fontsize=13, color='#333333')
    ax.tick_params(colors='#333333', labelsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.grid(True, alpha=0.15, color='#cccccc')
    for spine in ax.spines.values():
        spine.set_color('#cccccc')

    ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
              facecolor='white', edgecolor='#cccccc', labelcolor='#333333')

    plt.tight_layout()

    # Save PNG
    output_path = os.path.join(output_dir, 'equity_all_markets.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    plt.close()

def main():
    print("\n" + "="*80)
    print("📊 GENERATING EQUITY CURVES (Qualifying Stocks Only)")
    print("="*80)

    # Load all trades
    all_trades = load_all_trade_logs()

    if all_trades.empty:
        print("❌ No trades loaded. Exiting.")
        return

    print(f"\n📊 Total trades loaded: {len(all_trades)}")
    print(f"   Countries: {all_trades['Country'].value_counts().to_dict()}")

    # Show qualifying symbols summary
    print(f"\n📋 Qualifying symbols:")
    for cc, syms in QUALIFYING_SYMBOLS.items():
        if syms is None:
            print(f"   {cc}: ALL (no filter)")
        else:
            print(f"   {cc}: {len(syms)} stocks — {', '.join(syms[:5])}{'...' if len(syms) > 5 else ''}")

    # Markets to process
    markets = {
        'US': 'US',
        'TH': 'THAI',
        'CN': 'CHINA',
        'TW': 'TAIWAN',
        'GL': 'METALS'
    }

    # Create separate equity chart for each market (filtered)
    for country_code, market_name in markets.items():
        print(f"\n📈 Processing {market_name} Market ({country_code})...")

        market_trades = all_trades[all_trades['Country'] == country_code].copy()
        if market_trades.empty:
            print(f"   ⚠️ No trades found for {market_name}")
            continue

        # V14.3: ใช้ filter_by_qualifying_symbols ที่อ่านจาก symbol_performance.csv
        filtered = filter_by_qualifying_symbols(market_trades, country_code)
        if filtered.empty:
            print(f"   ⚠️ No qualifying trades for {market_name}")
            continue

        equity_df = calculate_equity_curve(filtered)
        if equity_df.empty:
            print(f"   ⚠️ Could not calculate equity curve for {market_name}")
            continue

        plot_single_market_equity(equity_df, market_name, country_code)
        print(f"   ✅ {market_name}: {len(filtered)} trades ({filtered['symbol'].nunique()} stocks), Final Equity: ${equity_df['equity'].iloc[-1]:,.2f}")

    # Combined chart
    print(f"\n📈 Creating combined equity curve (qualifying stocks only)...")
    plot_all_markets_combined(all_trades)

    print("\n" + "="*80)
    print("✅ All equity curves generated!")
    print("="*80)

if __name__ == "__main__":
    main()
