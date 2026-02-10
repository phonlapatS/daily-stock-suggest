#!/usr/bin/env python
"""
analyze_rrr_potential.py
========================
Analysis script to find the "Optimal Holding Period" and "Natural RRR" 
for each market group using the V3.4 Verified Thresholds.

It avoids complex trading logic (TP/SL) and instead measures:
"If we entered at the signal and held for N bars, what would be the Best & Worst case?"

Outputs tables similar to the "Thai Strict/Balanced" examples for the Mentor.
"""

import sys
import os
import time
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from tvDatafeed import TvDatafeed, Interval

# Configuration
HOLDING_PERIODS = [1, 3, 5, 10]  # Bars to look forward
# Min samples to be statistically significant
MIN_SAMPLES = 30

def get_market_behavior(percent_change):
    """Categorize behavior based on volatility"""
    std = np.std(percent_change)
    if std > 0.02: return "Volatile"
    if std < 0.01: return "Stable"
    return "Normal"

def analyze_holding_period(df, threshold_pct, periods=[1, 3, 5, 10]):
    """
    Analyze potential returns over multiple holding periods.
    Returns a dictionary of stats for each period.
    """
    if df is None or len(df) < 200:
        return None

    close = df['close']
    pct_change = close.pct_change()
    
    # Determine Threshold Series
    if threshold_pct == 'Dynamic':
        short_term_std = pct_change.rolling(window=20).std()
        long_term_std = pct_change.rolling(window=252).std()
        long_term_floor = long_term_std * 0.50
        effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
        effective_std = effective_std.fillna(short_term_std)
        threshold_series = effective_std * 1.25
        threshold_val_str = "Dynamic"
    else:
        fixed_val = float(threshold_pct) / 100.0
        threshold_series = pd.Series(fixed_val, index=pct_change.index)
        threshold_val_str = f"{threshold_pct}%"

    signals = []
    
    # Identify Signals (Same logic as verify_threshold.py)
    # Scan from bar 50 to end - max_period
    max_period = max(periods)
    
    for i in range(50, len(df) - max_period):
        # 3-bar pattern check
        pattern = ''
        for j in range(i-2, i+1):
            thresh = threshold_series.iloc[j]
            change = pct_change.iloc[j]
            if change > thresh: pattern += '+'
            elif change < -thresh: pattern += '-'
            else: pattern += '.'
            
        if '.' in pattern: continue

        # We only care about the direction of the pattern
        # End with + is BULLISH, End with - is BEARISH
        signal_dir = 1 if pattern[-1] == '+' else -1
        
        entry_price = close.iloc[i]
        
        # Analyze outcome for each period
        period_stats = {}
        for p in periods:
            exit_price = close.iloc[i+p]
            
            # Simple Return at end of period
            ret = (exit_price - entry_price) / entry_price * signal_dir
            
            # Max Favorable Excursion (MFE) - Best price during hold
            window_prices = close.iloc[i+1 : i+p+1]
            if signal_dir == 1:
                max_price = window_prices.max()
                mfe = (max_price - entry_price) / entry_price
                
                min_price = window_prices.min()
                mae = (min_price - entry_price) / entry_price # Negative value
            else:
                min_price = window_prices.min()
                mfe = (entry_price - min_price) / entry_price
                
                max_price = window_prices.max()
                mae = (entry_price - max_price) / entry_price # Negative value

            period_stats[p] = {
                'return': ret,
                'mfe': mfe,
                'mae': mae
            }
            
        signals.append(period_stats)
        
    if len(signals) < MIN_SAMPLES:
        return None
        
    # Aggregate Stats
    results = {}
    for p in periods:
        rets = [s[p]['return'] for s in signals]
        mfes = [s[p]['mfe'] for s in signals]
        maes = [s[p]['mae'] for s in signals]
        
        # Win Rate (End of Period)
        wins = [r for r in rets if r > 0]
        losses = [r for r in rets if r <= 0]
        
        win_rate = len(wins) / len(rets) * 100
        avg_win = np.mean(wins) * 100 if wins else 0
        avg_loss = abs(np.mean(losses)) * 100 if losses else 0
        
        # RRR based on End Return
        rrr_end = avg_win / avg_loss if avg_loss > 0 else 0
        
        # RRR based on Potential (Avg MFE / Avg MAE) - "Natural Potential"
        # Use abs(MAE)
        avg_mfe = np.mean(mfes) * 100
        avg_mae = abs(np.mean(maes)) * 100
        rrr_potential = avg_mfe / avg_mae if avg_mae > 0 else 0
        
        results[p] = {
            'win_rate': win_rate,
            'avg_return': np.mean(rets) * 100,
            'rrr_end': rrr_end,
            'rrr_potential': rrr_potential,
            'avg_mfe': avg_mfe,
            'avg_mae': avg_mae
        }
        
    return {
        'count': len(signals),
        'periods': results
    }

def process_group(group_name, tv):
    if group_name not in config.ASSET_GROUPS:
        print(f"Skipping {group_name}...")
        return
        
    settings = config.ASSET_GROUPS[group_name]
    threshold = settings.get('fixed_threshold', 'Dynamic')
    assets = settings.get('assets', [])
    interval = settings.get('interval')
    
    print(f"\nAnalyzing {group_name} (Thresh: {threshold})...")
    
    group_stats = {p: {'win_rate': [], 'rrr': [], 'exp': []} for p in HOLDING_PERIODS}
    
    table_data = []

    for asset in assets[:5]: # Limit to 5 for speed
        symbol = asset.get('symbol') if isinstance(asset, dict) else asset
        exchange = asset.get('exchange', 'SET') if isinstance(asset, dict) else 'SET'
        
        # Load Data (Cache preferred)
        cache_path = f"data/cache/{exchange}_{symbol}.csv"
        if os.path.exists(cache_path):
            df = pd.read_csv(cache_path, parse_dates=['datetime']).set_index('datetime')
        else:
            try:
                df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=3000)
            except:
                continue
                
        res = analyze_holding_period(df, threshold, HOLDING_PERIODS)
        
        if res:
            # Pick the "Best" Period for this asset (Max Expectancy)
            best_p = 1
            max_exp = -999
            
            for p in HOLDING_PERIODS:
                data = res['periods'][p]
                # Expectancy = (Win% x AvgWin) - (Loss% x AvgLoss) -- approximates to Avg Return
                # Let's use avg_return as proxy for net profitability
                exp = data['avg_return']
                
                # Collect group stats
                group_stats[p]['win_rate'].append(data['win_rate'])
                group_stats[p]['rrr'].append(data['rrr_end'])
                group_stats[p]['exp'].append(exp)
                
                if exp > max_exp:
                    max_exp = exp
                    best_p = p
            
            best_data = res['periods'][best_p]
            
            # Add to table row
            table_data.append({
                'symbol': symbol,
                'count': res['count'],
                'best_period': best_p,
                'win_rate': best_data['win_rate'],
                'avg_win': best_data['avg_mfe'], # Potential upside
                'avg_loss': best_data['avg_mae'], # Potential downside
                'rrr': best_data['rrr_potential'] # Potential RRR
            })

    # Sort table by RRR descending
    table_data.sort(key=lambda x: x['rrr'], reverse=True)
    
    # Print Table similar to user request
    print(f"\n💎 TABLE: {group_name} OPTIMIZED POTENTIAL (Prob > 50%)")
    print("=" * 85)
    print(f"{'Symbol':<10} {'Count':<6} {'BestHold':<9} {'WinRate%':<9} {'AvgUpside%':<11} {'AvgRisk%':<10} {'RRR':<6}")
    print("-" * 85)
    
    for row in table_data:
        print(f"{row['symbol']:<10} {row['count']:<6} {str(row['best_period'])+' bars':<9} "
              f"{row['win_rate']:>6.1f}%   {row['avg_win']:>8.2f}%   {row['avg_loss']:>8.2f}%   {row['rrr']:>5.2f}")
              
    print("=" * 85)
    print(f"* BestHold: Optimal holding duration. AvgUpside/Risk based on Max Excursion.")

    # Group Recommendations
    print("\n💡 GROUP INSIGHTS:")
    best_group_p = 1
    max_group_rrr = 0
    
    for p in HOLDING_PERIODS:
        avg_rrr = np.mean(group_stats[p]['rrr']) if group_stats[p]['rrr'] else 0
        avg_wr = np.mean(group_stats[p]['win_rate']) if group_stats[p]['win_rate'] else 0
        print(f"  - Hold {p:<2} Bars: Win {avg_wr:>5.1f}% | RRR {avg_rrr:.2f}")
        
        if avg_rrr > max_group_rrr:
            max_group_rrr = avg_rrr
            best_group_p = p
            
    print(f"✅ RECOMMENDATION: Hold for {best_group_p} bars for maximum efficiency.")

def main():
    tv = TvDatafeed()
    
    targets = [
        "GROUP_B_US",       # 0.6%
        "GROUP_C1_GOLD_30M", # 0.1%
        "GROUP_E_CHINA_ADR"  # 1.2%
    ]
    
    print("🚀 ANALYZING RRR POTENTIAL ACROSS MARKETS...")
    for group in targets:
        process_group(group, tv)

if __name__ == "__main__":
    main()
