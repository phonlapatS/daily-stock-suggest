#!/usr/bin/env python
"""
fact_check.py - Generate Fact Check Log for Mentor Audit
=========================================================
Exports row-by-row verification data to prove that:
- Direction is correctly classified based on Threshold
- Only significant days are counted as UP/DOWN

Output: logs/fact_check_log.csv
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import config


def classify_direction(change_pct, threshold):
    """
    Strict Mode: Classify daily change into Direction.
    
    Returns:
        1  = UP (Significant Positive)
        -1 = DOWN (Significant Negative)
        0  = NOISE (Not Significant)
    """
    if change_pct > threshold:
        return 1
    elif change_pct < -threshold:
        return -1
    else:
        return 0


def generate_fact_check_log(symbol='PTT', exchange='SET', n_bars=100, output_path=None):
    """
    Generate Fact Check Log for a single stock.
    
    Columns:
    - Date
    - Symbol
    - Close
    - Change_Pct
    - Dynamic_Threshold
    - Direction
    - Direction_Label
    - Is_Pass_Threshold
    """
    print(f"\n📋 Generating Fact Check Log for {symbol}...")
    
    # Fetch data
    tv = TvDatafeed()
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
    
    if df is None or len(df) < 20:
        print(f"❌ Failed to fetch data for {symbol}")
        return None
    
    # Calculate metrics
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]
    
    # Change %
    df['change_pct'] = df['close'].pct_change() * 100
    
    # Dynamic Threshold (SD * 1.25)
    short_std = df['change_pct'].rolling(window=config.VOLATILITY_WINDOW).std()
    long_std = df['change_pct'].rolling(window=252).std()
    long_term_floor = long_std * 0.50
    effective_std = np.maximum(short_std, long_term_floor.fillna(0))
    effective_std = effective_std.fillna(short_std)
    df['dynamic_threshold'] = effective_std * 1.25
    
    # Fill NaN
    df['change_pct'] = df['change_pct'].fillna(0)
    df['dynamic_threshold'] = df['dynamic_threshold'].fillna(df['dynamic_threshold'].mean())
    
    # Direction
    df['direction'] = df.apply(
        lambda row: classify_direction(row['change_pct'], row['dynamic_threshold']),
        axis=1
    )
    
    # Human-readable labels
    df['direction_label'] = df['direction'].map({
        1: 'UP',
        -1: 'DOWN',
        0: 'NOISE'
    })
    
    df['is_pass_threshold'] = df['direction'] != 0
    df['symbol'] = symbol
    
    # Select columns for output
    log_df = df[['datetime', 'symbol', 'close', 'change_pct', 'dynamic_threshold', 
                  'direction', 'direction_label', 'is_pass_threshold']].copy()
    
    log_df.columns = ['Date', 'Symbol', 'Close', 'Change_Pct', 'Dynamic_Threshold',
                      'Direction', 'Direction_Label', 'Is_Pass_Threshold']
    
    # Round for readability
    log_df['Close'] = log_df['Close'].round(2)
    log_df['Change_Pct'] = log_df['Change_Pct'].round(2)
    log_df['Dynamic_Threshold'] = log_df['Dynamic_Threshold'].round(2)
    
    # Save
    if output_path is None:
        output_path = 'logs/fact_check_log.csv'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    log_df.to_csv(output_path, index=False)
    
    print(f"✅ Saved: {output_path} ({len(log_df)} rows)")
    
    # Print summary
    up_count = (log_df['Direction'] == 1).sum()
    down_count = (log_df['Direction'] == -1).sum()
    noise_count = (log_df['Direction'] == 0).sum()
    
    print(f"\n📊 Summary:")
    print(f"   🟢 UP Days:     {up_count} ({up_count/len(log_df)*100:.1f}%)")
    print(f"   🔴 DOWN Days:   {down_count} ({down_count/len(log_df)*100:.1f}%)")
    print(f"   ⚪ NOISE Days:  {noise_count} ({noise_count/len(log_df)*100:.1f}%)")
    print(f"   📏 Avg Threshold: {log_df['Dynamic_Threshold'].mean():.2f}%")
    
    return log_df


def generate_multi_stock_log(symbols_info, output_path='logs/fact_check_log.csv'):
    """
    Generate Fact Check Log for multiple stocks.
    """
    all_logs = []
    
    for sym_info in symbols_info:
        symbol = sym_info['symbol']
        exchange = sym_info['exchange']
        
        log_df = generate_fact_check_log(symbol, exchange, n_bars=100, output_path=None)
        
        if log_df is not None:
            all_logs.append(log_df)
    
    if all_logs:
        combined = pd.concat(all_logs, ignore_index=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined.to_csv(output_path, index=False)
        print(f"\n✅ Combined Fact Check Log: {output_path} ({len(combined)} rows)")
        return combined
    
    return None


def main():
    print("\n" + "=" * 60)
    print("🔍 FACT CHECK LOG GENERATOR")
    print("=" * 60)
    print("Purpose: Verify that Direction logic works correctly")
    print("=" * 60)
    
    # Get sample stocks from config
    sample_stocks = []
    for group_name, group_config in config.ASSET_GROUPS.items():
        if 'METALS' in group_name:  # Skip intraday
            continue
        assets = group_config['assets'][:2]  # First 2 per group
        for asset in assets:
            sample_stocks.append({
                'symbol': asset['symbol'],
                'exchange': asset['exchange']
            })
    
    # Limit to 5 stocks for quick generation
    sample_stocks = sample_stocks[:5]
    
    print(f"\n📊 Generating logs for {len(sample_stocks)} stocks...")
    
    generate_multi_stock_log(sample_stocks, 'logs/fact_check_log.csv')
    
    print("\n" + "=" * 60)
    print("✅ FACT CHECK LOG COMPLETE")
    print("=" * 60)
    print("Open logs/fact_check_log.csv to verify row-by-row:")
    print("  - Each row shows Change_Pct vs Dynamic_Threshold")
    print("  - Direction should be UP if Change_Pct > Threshold")
    print("  - Direction should be DOWN if Change_Pct < -Threshold")
    print("  - Direction should be NOISE otherwise")
    print("=" * 60)


if __name__ == "__main__":
    main()
