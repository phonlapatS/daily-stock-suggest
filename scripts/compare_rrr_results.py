#!/usr/bin/env python
"""
compare_rrr_results.py
======================

Compare Original vs Optimized (V14.5) results for all markets.
Uses simulation logic to project V14.5 performance on historical data.

Metrics Compared:
- Win Rate (%)
- Avg Win (%)
- Avg Loss (%)
- RRR (Risk-Reward Ratio)
- Total Return (%)
- Expectancy (% per trade)
"""

import os
import sys
import pandas as pd
import numpy as np
import glob

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import qualifying symbols from plot_equity_curves (to match logic)
# Copying valid symbols directly to avoid import issues
QUALIFYING_SYMBOLS = {
    'TH': [
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
    'GL': None, 
}

def load_all_trade_logs():
    """Load and merge all trade_history_*.csv files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        return pd.DataFrame()
    
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, on_bad_lines='skip', engine='python')
            filename = os.path.basename(f).upper()
            if 'THAI' in filename: df['Country'] = 'TH'
            elif 'US' in filename: df['Country'] = 'US'
            elif 'CHINA' in filename: df['Country'] = 'CN'
            elif 'TAIWAN' in filename: df['Country'] = 'TW'
            elif 'METALS' in filename: df['Country'] = 'GL'
            else: df['Country'] = 'GL'
            dfs.append(df)
        except Exception:
            pass
    
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

def filter_trades(trades, country_code):
    """Filter trades by qualifying symbols"""
    if trades.empty: return pd.DataFrame()
    
    symbols = QUALIFYING_SYMBOLS.get(country_code)
    if symbols is None: return trades
    
    trades_copy = trades.copy()
    trades_copy['_sym_upper'] = trades_copy['symbol'].astype(str).str.upper().str.strip()
    qualifying_upper = [s.upper().strip() for s in symbols]
    
    filtered = trades_copy[trades_copy['_sym_upper'].isin(qualifying_upper)].copy()
    filtered.drop(columns=['_sym_upper'], inplace=True)
    return filtered

def calculate_metrics(trades):
    """Calculate key performance metrics"""
    if trades.empty:
        return {
            'count': 0, 'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 
            'rrr': 0, 'return': 0, 'expectancy': 0
        }
    
    df = trades.copy()
    
    # Ensure PnL exists
    if 'pnl' not in df.columns:
        df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce').fillna(0)
        if 'forecast' in df.columns:
            df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        else:
            df['pnl'] = df['actual_return']
            
    # Calculate stats
    wins = df[df['pnl'] > 0]
    losses = df[df['pnl'] <= 0]
    
    count = len(df)
    win_rate = (len(wins) / count * 100) if count > 0 else 0
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    avg_loss = abs(losses['pnl'].mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Total cumulative return (simple sum for comparison)
    total_return = df['pnl'].sum()
    
    # Expectancy = (Win% * AvgWin) - (Loss% * AvgLoss)
    win_pct = win_rate / 100
    loss_pct = 1 - win_pct
    expectancy = (win_pct * avg_win) - (loss_pct * avg_loss)
    
    return {
        'count': count,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rrr': rrr,
        'return': total_return,
        'expectancy': expectancy
    }

def simulate_optimization(trades, sl_cap, tp_cap):
    """Simulate improved RRR by capping losses/wins"""
    df = trades.copy()
    
    # Ensure PnL
    if 'pnl' not in df.columns:
        df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce').fillna(0)
        if 'forecast' in df.columns:
            df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        else:
            df['pnl'] = df['actual_return']
    
    # Cap losses
    df.loc[df['pnl'] < -sl_cap, 'pnl'] = -sl_cap
    # Cap wins
    df.loc[df['pnl'] > tp_cap, 'pnl'] = tp_cap
    
    return df

def main():
    print("="*100)
    print("  RRR OPTIMIZATION ANALYSIS: ORIGINAL vs NEW (V14.5)")
    print("="*100)
    
    all_trades = load_all_trade_logs()
    
    markets = [
        {'code': 'TH', 'name': 'THAI MARKET', 'optimized': True, 'sl_cap': 1.3, 'tp_cap': 3.2},
        {'code': 'CN', 'name': 'CHINA MARKET', 'optimized': True, 'sl_cap': 1.2, 'tp_cap': 4.0},
        {'code': 'TW', 'name': 'TAIWAN MARKET', 'optimized': True, 'sl_cap': 1.2, 'tp_cap': 4.0}, # V14.5 Proposed
        {'code': 'US', 'name': 'US MARKET', 'optimized': True, 'sl_cap': 1.2, 'tp_cap': 4.0},     # V14.5 Proposed
    ]
    
    for m in markets:
        print(f"\n🔵 {m['name']}")
        print("-" * 100)
        print(f"{'METRIC':<20} | {'ORIGINAL':<15} | {'NEW (OPTIMIZED)':<15} | {'CHANGE':<15}")
        print("-" * 100)
        
        # Get trades
        market_trades = all_trades[all_trades['Country'] == m['code']].copy()
        market_trades = filter_trades(market_trades, m['code'])
        
        if market_trades.empty:
            print("  (No data found)")
            continue
            
        # Original Metrics
        orig_stats = calculate_metrics(market_trades)
        
        # New Metrics
        if m['optimized']:
            opt_trades = simulate_optimization(market_trades, sl_cap=m['sl_cap'], tp_cap=m['tp_cap'])
            new_stats = calculate_metrics(opt_trades)
        else:
            new_stats = orig_stats # No change
            
        # Display Row by Row
        metrics_list = [
            ('Win Rate', 'win_rate', '%', 1),
            ('Avg Win', 'avg_win', '%', 2),
            ('Avg Loss', 'avg_loss', '%', 2),
            ('RRR', 'rrr', 'x', 2),
            ('Expectancy per Trade', 'expectancy', '%', 3),
            ('Total Return (Simple)', 'return', '%', 1)
        ]
        
        for name, key, unit, decimals in metrics_list:
            orig_val = orig_stats[key]
            new_val = new_stats[key]
            diff = new_val - orig_val
            
            # Format
            orig_str = f"{orig_val:.{decimals}f}{unit}"
            new_str = f"{new_val:.{decimals}f}{unit}"
            
            # Change Format
            if key == 'avg_loss': 
                # For loss, smaller is better (negative diff is good)
                diff_str = f"{diff:+.{decimals}f}{unit}"
                good = diff < 0
            elif key == 'win_rate' and diff < 0:
                # Win rate drop is expected, show neutral/bad
                diff_str = f"{diff:+.{decimals}f}{unit}"
                good = False
            else:
                # Higher is better
                diff_str = f"{diff:+.{decimals}f}{unit}"
                good = diff > 0
                
            # Add star for huge improvement
            if good and abs(diff) > 0.1:
                diff_str += " ⭐"
                
            if not m['optimized']:
                diff_str = "-"
            
            print(f"{name:<20} | {orig_str:<15} | {new_str:<15} | {diff_str:<15}")
            
    print("\n" + "="*100)

if __name__ == "__main__":
    main()
