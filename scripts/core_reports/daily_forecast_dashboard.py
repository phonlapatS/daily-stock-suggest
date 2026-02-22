#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
daily_forecast_dashboard.py - Predict N+1 Executive Dashboard (V4.4.7)
=====================================================================
Unified Dashboard Entry Point.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_tomorrow_forecasts():
    """ดึงข้อมูล forecasts สำหรับพรุ่งนี้"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow_forecasts = df[df['target_date'] == tomorrow].copy()
    return tomorrow_forecasts

def get_accuracy_report():
    """ดึงข้อมูล accuracy report (Trading Performance Logic)"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    # Filter only verified
    verified_df = df[df['actual'] != 'PENDING'].copy()
    
    if len(verified_df) == 0:
        return pd.DataFrame()
    
    # Logic: Calculate P/L
    # If Forecast UP   -> P/L = change_pct
    # If Forecast DOWN -> P/L = -change_pct
    def calc_pnl(row):
        f = str(row['forecast']).upper()
        # Use realized_change (Target Price - Scan Price) instead of signal change
        c = float(row.get('realized_change', 0.0)) if pd.notna(row.get('realized_change')) else 0.0
        if f == 'UP': return c
        if f == 'DOWN': return -c
        return 0.0

    verified_df['P/L'] = verified_df.apply(calc_pnl, axis=1)
    
    accuracy_data = []
    # Calculate per exchange for cleaner display
    for exchange in verified_df['exchange'].unique():
        ex_df = verified_df[verified_df['exchange'] == exchange]
        for symbol in ex_df['symbol'].unique():
            symbol_data = ex_df[ex_df['symbol'] == symbol]
            total = len(symbol_data)
            
            # Profitable trades (Winrate) - Matching calculate_performance.py logic
            winning_trades = symbol_data[symbol_data['P/L'] > 0]
            losing_trades = symbol_data[symbol_data['P/L'] <= 0]
            
            wins = len(winning_trades)
            winrate = (wins / total) * 100 if total > 0 else 0
            
            avg_win = winning_trades['P/L'].mean() if len(winning_trades) > 0 else 0
            avg_loss = losing_trades['P/L'].mean() if len(losing_trades) > 0 else 0
            rrr = abs(avg_win / avg_loss) if avg_loss != 0 else (99.0 if avg_win > 0 else 0)
            
            accuracy_data.append({
                'symbol': symbol,
                'exchange': exchange,
                'correct': wins, # Use 'correct' label for backward compatibility with display logic, but it's 'wins'
                'total': total,
                'accuracy': winrate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'rrr': rrr
            })
            
    return pd.DataFrame(accuracy_data)

def display_executive_dashboard():
    """แสดง Executive Dashboard"""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("=" * 100)
    print("📊 PREDICT N+1 DASHBOARD (V4.4.7)")
    print(f"📅 Date: {today} | 🎯 Predict For: {tomorrow}")
    print("=" * 100)
    
    log_file = "logs/performance_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        print(f"📈 MARKET OVERVIEW: {df['symbol'].nunique()} Unique Stocks ({len(df)} Records)")
        print("-" * 50)
        for exchange in df['exchange'].unique():
            count = len(df[df['exchange'] == exchange])
            print(f"   {exchange}: {count} records")
        print()
    
    # Section 1: PREDICT TOMORROW
    print("1. PREDICT TOMORROW (" + tomorrow + ")")
    print("-" * 100)
    tomorrow_data = get_tomorrow_forecasts()
    
    if tomorrow_data.empty:
        print("📋 No forecasts available for tomorrow")
    else:
        for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
            ex_df = tomorrow_data[tomorrow_data['exchange'] == exchange]
            if not ex_df.empty:
                print(f"--- {exchange} ---")
                print("Symbol     Change%  Threshold  Predict    Prob%        Consensus (P/N)")
                print("-" * 75)
                ex_df = ex_df.sort_values('prob', ascending=False)
                for _, row in ex_df.iterrows():
                    sym = row['symbol']
                    chg = f"{row.get('change_pct', 0.0):>6.2f}%"
                    thresh = f"±{row.get('threshold', 0.0):.2f}%"
                    dir_sym = "🟢 UP" if row['forecast'] == "UP" else "🔴 DOWN"
                    p_w = int(row.get('total_p', 0))
                    n_w = int(row.get('total_n', 0))
                    consensus_str = f"{p_w} vs {n_w}"
                    print(f"{sym:<10} {chg:>8} {thresh:>10} {dir_sym:^10} {row['prob']:>6.1f}% {consensus_str:>18}")
                print()

    # Section 2: ACCURACY REPORT
    print("2. ACCURACY REPORT (Historical Performance)")
    print("-" * 100)
    acc_df = get_accuracy_report()
    if acc_df.empty:
        print("📋 No accuracy data available")
    else:
        # 2a. Market Summary Table
        print("📊 MARKET-LEVEL SUMMARY:")
        print(f"{'Market':<12} {'Trades':<8} {'Wins':<8} {'Winrate':<10} {'Avg Win':<10} {'Avg Loss':<10}")
        print("-" * 75)
        
        for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                m_total = ex_acc_df['total'].sum()
                m_wins = ex_acc_df['correct'].sum()
                m_winrate = (m_wins / m_total * 100) if m_total > 0 else 0
                m_avg_win = ex_acc_df['avg_win'].mean()
                m_avg_loss = ex_acc_df['avg_loss'].mean()
                print(f"{exchange:<12} {m_total:<8.0f} {m_wins:<8.0f} {m_winrate:>7.1f}% {m_avg_win:>9.2f}% {m_avg_loss:>9.2f}%")
        
        # Calculate Global
        g_total = acc_df['total'].sum()
        g_wins = acc_df['correct'].sum()
        g_winrate = (g_wins / g_total * 100) if g_total > 0 else 0
        print("-" * 75)
        print(f"{'GLOBAL':<12} {g_total:<8.0f} {g_wins:<8.0f} {g_winrate:>7.1f}%")
        print("\n")

        # 2b. Per-Stock Details
        print("🎯 PER-STOCK PRECISION VIEW:")
        for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                print(f"--- {exchange} ---")
                print(f"{'Symbol':<12} {'Wins':>8} {'Total':>8} {'Win%':>9} {'Avg.Win%':>12} {'Avg.Loss%':>12} {'RRR':>8}")
                print("-" * 80)
                ex_acc_df = ex_acc_df.sort_values('accuracy', ascending=False)
                for _, row in ex_acc_df.iterrows():
                    print(f"{row['symbol']:12} {row['correct']:>8.0f} {row['total']:>8} {row['accuracy']:>8.1f}% {row['avg_win']:>11.2f}% {row['avg_loss']:>12.2f}% {row['rrr']:>8.2f}")
                print()
    
    print("\n" + "=" * 100)
    print("🎯 Dashboard Complete")
    print("=" * 100)

if __name__ == "__main__":
    display_executive_dashboard()
