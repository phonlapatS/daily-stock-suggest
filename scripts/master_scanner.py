#!/usr/bin/env python
"""
master_scanner.py - Universal Multi-Asset Scanner (V2 Logic)
=============================================================

Purpose: Central analysis engine for multi-asset trading system
Logic: V2 (Percentile-based, Volatility Classification, Mixed Streaks)

Supports:
- Thai Stocks (1D): PTT_SET_1D.parquet
- US Stocks (1D): TSLA_NASDAQ_1D.parquet  
- Gold Intraday (15M): XAUUSD_FOREX_15M.parquet
- Silver Intraday (30M): XAGUSD_FOREX_30M.parquet

Features:
- Smart file categorization by timeframe
- Universal V2 logic (timeframe agnostic)
- Dynamic floor adjustment (1D: 1.0%, Intraday: 0.2%)
- Volatility classification (Low/Med/High)
- Separate dashboards per timeframe

Author: Stock Analysis System
Date: 2026-01-15
Version: 2.0 (V2 Logic Integrated)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from tabulate import tabulate
from collections import defaultdict


# ================================
# Configuration - V2 Logic
# ================================

DATA_DIR = "data/stocks"

# V2 Logic Parameters
LOOKBACK_DAILY = 126  # 6 months for daily (V2 standard)
LOOKBACK_INTRADAY = 3000  # Full history for intraday
PERCENTILE = 0.90  # 90th percentile (V2 method)

# Dynamic floors (V2 adaptive)
FLOOR_DAILY = 1.0  # 1% for daily timeframes
FLOOR_INTRADAY = 0.2  # 0.2% for intraday (tighter for smaller moves)

# Timeframe categorization
INTRADAY_TIMEFRAMES = ['15M', '30M', '5M', '1H']  # Intraday patterns
DAILY_TIMEFRAMES = ['1D', 'D1', 'DAILY']  # Daily patterns

# Asset-specific notes
# Gold (XAUUSD): Typically 15M or 30M for intraday
# Silver (XAGUSD): Typically 15M or 30M for intraday
# Thai Stocks: 1D (daily)
# US Stocks: 1D (daily)


# ================================
# File Parser
# ================================

def parse_filename(filename):
    """
    Parse filename to extract metadata
    
    Supported formats:
    - SYMBOL_EXCHANGE_TIMEFRAME.parquet (Full format)
      Examples: PTT_SET_1D.parquet, XAUUSD_FOREX_15M.parquet
    - SYMBOL_EXCHANGE.parquet (Assume 1D)
      Examples: PTT_SET.parquet
    - SYMBOL.parquet (Minimal)
      Examples: PTT.parquet
    
    Args:
        filename: Parquet filename (Path object or string)
    
    Returns:
        dict: {symbol, exchange, timeframe, asset_type}
    """
    if isinstance(filename, Path):
        stem = filename.stem
    else:
        stem = Path(filename).stem
    
    parts = stem.split('_')
    
    # Default values
    symbol = parts[0]
    exchange = 'UNKNOWN'
    timeframe = '1D'
    
    if len(parts) >= 3:
        # Full format: SYMBOL_EXCHANGE_TIMEFRAME
        exchange = parts[1]
        timeframe = parts[2]
    elif len(parts) == 2:
        # SYMBOL_EXCHANGE (no timeframe = assume 1D)
        exchange = parts[1]
        timeframe = '1D'
    
    # Determine asset type
    if symbol in ['XAUUSD', 'XAGUSD', 'GOLD', 'SILVER']:
        asset_type = 'Precious Metals'
    elif exchange == 'FOREX' or 'USD' in symbol:
        asset_type = 'Forex'
    elif exchange in ['NASDAQ', 'NYSE', 'AMEX']:
        asset_type = 'US Stocks'
    elif exchange == 'SET':
        asset_type = 'Thai Stocks'
    else:
        asset_type = 'Other'
    
    return {
        'symbol': symbol,
        'exchange': exchange,
        'timeframe': timeframe,
        'asset_type': asset_type
    }


def categorize_files(data_dir):
    """
    Scan and categorize all parquet files by timeframe
    
    Args:
        data_dir: Data directory
    
    Returns:
        dict: {timeframe: [file_list]}
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    # Find all parquet files
    parquet_files = list(data_path.glob("*.parquet"))
    
    if not parquet_files:
        raise ValueError(f"No parquet files found in {data_dir}")
    
    # Group by timeframe
    categorized = defaultdict(list)
    
    for filepath in parquet_files:
        metadata = parse_filename(filepath)
        timeframe = metadata['timeframe']
        
        categorized[timeframe].append({
            'filepath': filepath,
            'symbol': metadata['symbol'],
            'exchange': metadata['exchange'],
            'timeframe': timeframe
        })
    
    return dict(categorized)


# ================================
# Universal Analysis Logic
# ================================

def calculate_dynamic_threshold(df, lookback, floor):
    """
    Calculate dynamic threshold using percentile method
    
    Args:
        df: DataFrame with pct_change
        lookback: Lookback period
        floor: Minimum floor
    
    Returns:
        float: Threshold value
    """
    if len(df) < 30:
        return floor
    
    # Use all data or lookback, whichever is smaller
    periods = min(len(df), lookback)
    
    # Calculate 90th percentile of absolute changes
    threshold = df['pct_change'].abs().tail(periods).quantile(PERCENTILE)
    
    # Apply floor
    return max(threshold, floor)


def calculate_volatility(df):
    """
    Calculate annualized volatility
    
    Args:
        df: DataFrame
    
    Returns:
        float: Annual volatility
    """
    # Intraday: use 252 × periods per day
    # Daily: use 252
    # For simplicity, always use sqrt(252)
    return df['pct_change'].std() * np.sqrt(252)


def classify_volatility(vol):
    """
    Classify volatility
    
    Args:
        vol: Volatility value
    
    Returns:
        str: Classification
    """
    if vol < 20:
        return 'Low'
    elif vol <= 60:
        return 'Med'
    else:
        return 'High'


def detect_volatility_streak(df, threshold):
    """
    Detect volatility streak (direction-agnostic)
    
    Args:
        df: DataFrame
        threshold: Threshold value
    
    Returns:
        int: Current streak
    """
    if df.empty or len(df) < 2:
        return 0
    
    streak = 0
    
    # Walk backwards from latest
    for i in range(len(df) - 1, -1, -1):
        change = df.iloc[i]['pct_change']
        
        if abs(change) > threshold:
            streak += 1
        else:
            break  # Stop at first quiet bar
    
    return streak


def calculate_historical_probability(df, current_streak, threshold):
    """
    Calculate historical probability for volatility streaks
    
    Args:
        df: DataFrame
        current_streak: Current streak count
        threshold: Threshold
    
    Returns:
        dict: Statistics
    """
    if current_streak == 0 or len(df) < 10:
        return {
            'win_rate': 0,
            'avg_return': 0,
            'max_risk': 0,
            'events': 0
        }
    
    # Add streak column
    df = df.copy()
    df['streak'] = 0
    
    # Calculate streak for each bar
    for i in range(len(df)):
        streak = 0
        for j in range(i, -1, -1):
            if abs(df.iloc[j]['pct_change']) > threshold:
                streak += 1
            else:
                break
        df.iloc[i, df.columns.get_loc('streak')] = streak
    
    # Add next return
    df['next_return'] = df['pct_change'].shift(-1)
    
    # Find matches (exclude last bar)
    history = df.iloc[:-1].copy()
    matches = history[history['streak'] == current_streak]
    matches = matches.dropna(subset=['next_return'])
    
    if len(matches) == 0:
        return {
            'win_rate': 0,
            'avg_return': 0,
            'max_risk': 0,
            'events': 0
        }
    
    # Calculate stats
    wins = len(matches[matches['next_return'] > 0])
    win_rate = (wins / len(matches)) * 100
    avg_return = matches['next_return'].mean()
    max_risk = matches['next_return'].min()
    
    return {
        'win_rate': win_rate,
        'avg_return': avg_return,
        'max_risk': max_risk,
        'events': len(matches)
    }


def analyze_asset(filepath, symbol, exchange, timeframe):
    """
    Analyze one asset
    
    Args:
        filepath: Path to parquet file
        symbol: Symbol
        exchange: Exchange
        timeframe: Timeframe
    
    Returns:
        dict: Analysis results
    """
    try:
        # Load data
        df = pd.read_parquet(filepath)
        df.index = pd.to_datetime(df.index)
        
        # Drop duplicates
        df = df[~df.index.duplicated(keep='last')]
        df = df.dropna()
        
        # Calculate pct_change if not exists
        if 'pct_change' not in df.columns:
            df['pct_change'] = df['close'].pct_change() * 100
            df = df.dropna()
        
        if len(df) < 30:
            return None
        
        # Determine lookback and floor based on timeframe
        if timeframe == '1D':
            lookback = LOOKBACK_DAILY
            floor = FLOOR_DAILY
        else:
            lookback = LOOKBACK_INTRADAY
            floor = FLOOR_INTRADAY
        
        # Calculate threshold
        threshold = calculate_dynamic_threshold(df, lookback, floor)
        
        # Volatility
        vol = calculate_volatility(df)
        vol_class = classify_volatility(vol)
        
        # Current state
        latest = df.iloc[-1]
        latest_change = latest['pct_change']
        
        # Streak
        streak = detect_volatility_streak(df, threshold)
        
        # Status
        if streak > 0:
            if latest_change > 0:
                status = f"🟢 Up Vol {streak}"
            else:
                status = f"🔴 Down Vol {streak}"
        else:
            status = "⚪ Quiet"
        
        # Historical probability
        prob = calculate_historical_probability(df, streak, threshold)
        
        return {
            'Symbol': symbol,
            'Exchange': exchange,
            'Price': latest['close'],
            'Change%': latest_change,
            'Status': status,
            'Threshold': threshold,
            'Vol_Class': vol_class,
            'WinRate': prob['win_rate'],
            'AvgRet': prob['avg_return'],
            'MaxRisk': prob['max_risk'],
            'Events': prob['events'],
            'Streak': streak
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None


# ================================
# Dashboard Display
# ================================

def format_dashboard(results, timeframe):
    """
    Format and display dashboard for one timeframe
    
    Args:
        results: List of analysis results
        timeframe: Timeframe name
    """
    if not results:
        print(f"\n⚪ No active signals for {timeframe}")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Filter active only (skip quiet)
    df_active = df[df['Streak'] > 0].copy()
    
    if df_active.empty:
        print(f"\n⚪ No active streaks for {timeframe}")
        return
    
    # Sort by Events (most data first)
    df_active = df_active.sort_values('Events', ascending=False)
    
    # Format for display
    df_display = df_active.copy()
    df_display['Price'] = df_display['Price'].apply(lambda x: f"{x:.2f}")
    df_display['Change%'] = df_display['Change%'].apply(lambda x: f"{x:+.2f}%")
    df_display['Threshold'] = df_display['Threshold'].apply(lambda x: f"{x:.2f}%")
    df_display['WinRate'] = df_display['WinRate'].apply(lambda x: f"{x:.1f}%")
    df_display['AvgRet'] = df_display['AvgRet'].apply(lambda x: f"{x:+.2f}%")
    df_display['MaxRisk'] = df_display['MaxRisk'].apply(lambda x: f"{x:+.2f}%")
    
    # Select columns
    cols = ['Symbol', 'Exchange', 'Price', 'Change%', 'Status', 
            'Threshold', 'Vol_Class', 'WinRate', 'AvgRet', 'MaxRisk', 'Events']
    
    # Print
    print(f"\n{'='*100}")
    print(f"📊 REPORT: {timeframe.upper()}")
    print(f"{'='*100}")
    print(tabulate(df_display[cols], headers='keys', tablefmt='plain', showindex=False))
    print(f"{'='*100}")
    print(f"Active Signals: {len(df_active)}")
    print(f"{'='*100}")


# ================================
# Main Scanner
# ================================

def main():
    """
    Main execution
    """
    print("\n" + "="*100)
    print("🚀 UNIVERSAL MASTER SCANNER - Multi-Asset Analysis")
    print("="*100)
    print(f"📁 Data Directory: {DATA_DIR}")
    print(f"🎯 Logic: V2 (Percentile-based, Timeframe Agnostic)")
    print("="*100)
    
    # Categorize files
    print("\n📂 Scanning files...")
    categorized = categorize_files(DATA_DIR)
    
    print(f"✅ Found {sum(len(files) for files in categorized.values())} files")
    print(f"📊 Timeframes: {list(categorized.keys())}")
    
    # Process each timeframe group
    for timeframe, files in sorted(categorized.items()):
        print(f"\n🔄 Processing {timeframe}: {len(files)} assets...")
        
        results = []
        
        for file_info in files:
            result = analyze_asset(
                filepath=file_info['filepath'],
                symbol=file_info['symbol'],
                exchange=file_info['exchange'],
                timeframe=timeframe
            )
            
            if result:
                results.append(result)
        
        # Display dashboard
        format_dashboard(results, timeframe)
    
    print(f"\n✅ Master Scan Complete!\n")


if __name__ == "__main__":
    main()
