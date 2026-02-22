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
    """ดึงข้อมูล accuracy report จาก forward testing"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    verified_df = df[df['actual'] != 'PENDING'].copy()
    
    if len(verified_df) == 0:
        return pd.DataFrame()
    
    accuracy_data = []
    for symbol in verified_df['symbol'].unique():
        symbol_data = verified_df[verified_df['symbol'] == symbol]
        total = len(symbol_data)
        correct = symbol_data['correct'].sum()
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        correct_trades = symbol_data[symbol_data['correct'] == 1]
        wrong_trades = symbol_data[symbol_data['correct'] == 0]
        avg_win = correct_trades['change_pct'].mean() if len(correct_trades) > 0 else 0
        avg_loss = wrong_trades['change_pct'].mean() if len(wrong_trades) > 0 else 0
        rrr = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        exchange = symbol_data.iloc[0]['exchange']
        
        accuracy_data.append({
            'symbol': symbol,
            'exchange': exchange,
            'correct': correct,
            'total': total,
            'accuracy': accuracy,
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
    print("2. ACCURACY REPORT")
    print("-" * 100)
    acc_df = get_accuracy_report()
    if acc_df.empty:
        print("📋 No accuracy data available")
    else:
        for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                print(f"--- {exchange} ---")
                print("Symbol      Correct   Total    Acc%     Avg.Win%   Avg.Lose%    RRR")
                print("-" * 75)
                ex_acc_df = ex_acc_df.sort_values('accuracy', ascending=False)
                for _, row in ex_acc_df.iterrows():
                    print(f"{row['symbol']:12} {row['correct']:>8.0f} {row['total']:>8} {row['accuracy']:>7.1f}%        {row['avg_win']:>8.2f}%      {row['avg_loss']:>8.2f}%      {row['rrr']:>8.2f}")
                print()
    
    print("\n" + "=" * 100)
    print("🎯 Dashboard Complete")
    print("=" * 100)

if __name__ == "__main__":
    display_executive_dashboard()
