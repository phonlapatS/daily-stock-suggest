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
import argparse

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
    
    # User Request: ตัดอันที่นับไม่ถึง 30 ออก (Require minimum 30 stats)
    # And filter out illogical probabilities (Prob < 50%) where engine forces a guess against historical odds
    if 'stats' in tomorrow_forecasts.columns:
        # Fill missing with 0 and convert
        tomorrow_forecasts['stats'] = pd.to_numeric(tomorrow_forecasts['stats'], errors='coerce').fillna(0)
        
        # Only keep forecasts with >= 30 stats AND >= 50.0% prob
        target_mask = (tomorrow_forecasts['stats'] >= 30)
        if 'prob' in tomorrow_forecasts.columns:
            tomorrow_forecasts['prob'] = pd.to_numeric(tomorrow_forecasts['prob'], errors='coerce').fillna(0)
            target_mask = target_mask & (tomorrow_forecasts['prob'] >= 50.0)
            
        tomorrow_forecasts = tomorrow_forecasts[target_mask]
        
    return tomorrow_forecasts

def get_accuracy_report():
    """ดึงข้อมูล accuracy report (Aggregated Strategy Insights V4.5)"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    # Standardize names
    df.columns = df.columns.str.strip()
    
    # Filter only verified
    verified_df = df[df['actual'] != 'PENDING'].copy()
    
    if len(verified_df) == 0:
        return pd.DataFrame()
    
    # Ensure realized_change exists
    if 'realized_change' not in verified_df.columns:
        verified_df['realized_change'] = (verified_df['price_actual'] - verified_df['price_at_scan']) / verified_df['price_at_scan'] * 100.0

    accuracy_data = []
    # Group by Pattern + Forecast level for deep insights
    groups = verified_df.groupby(['exchange', 'symbol', 'pattern', 'forecast'])
    
    for (ex, sym, pat, fcast), g_df in groups:
        total = len(g_df)
        wins = int(g_df['correct'].sum())
        winrate = (wins / total) * 100 if total > 0 else 0
        
        # Pull means for descriptive stats
        avg_prob = g_df['prob'].mean() if 'prob' in g_df.columns else 0
        avg_stats = g_df['stats'].mean() if 'stats' in g_df.columns else 0
        latest_thresh = g_df.sort_values('scan_date')['threshold'].iloc[-1] if 'threshold' in g_df.columns else 0
        
        # Profit/Loss Stats
        winning_trades = g_df[g_df['correct'] == 1]
        losing_trades = g_df[g_df['correct'] == 0]
        
        avg_win = winning_trades['realized_change'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['realized_change'].mean() if len(losing_trades) > 0 else 0
        
        rrr = abs(avg_win / avg_loss) if avg_loss != 0 else (99.0 if avg_win != 0 else 0)
        
        accuracy_data.append({
            'exchange': ex,
            'symbol': sym,
            'pattern': pat,
            'forecast': fcast,
            'prob': avg_prob,
            'stats': avg_stats,
            'threshold': latest_thresh,
            'correct': wins, # Number of Wins
            'total': total,
            'accuracy': winrate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'rrr': rrr
        })
            
    res_df = pd.DataFrame(accuracy_data)
    
    # User Request: ตัดอันที่นับไม่ถึง 30 ออก (Require minimum 30 stats per symbol/pattern)
    # And filter out illogical probabilities (Prob < 50%)
    if not res_df.empty and 'stats' in res_df.columns:
        target_mask = (res_df['stats'] >= 30)
        if 'prob' in res_df.columns:
            target_mask = target_mask & (res_df['prob'] >= 50.0)
            
        res_df = res_df[target_mask]
        
    return res_df

def display_executive_dashboard(target_market=None):
    """
    แสดง Executive Dashboard
    :param target_market: ถ้าระบุจะแสดงเฉพาะตลาดนั้น (เช่น 'SET', 'NASDAQ')
    """
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    market_list = ['TWSE', 'SET', 'NASDAQ', 'HKEX']
    if target_market:
        target_market = target_market.upper()
        if target_market in market_list:
            market_list = [target_market]
        else:
            print(f"⚠️ Warning: Market '{target_market}' not in standard list {market_list}. Showing all.")
    
    print("=" * 100)
    print("📊 PREDICT N+1 DASHBOARD (V4.5 FINAL)")
    print(f"📅 Date: {today} | 🎯 Predict For: {tomorrow}")
    print("=" * 100)
    
    log_file = "logs/performance_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        # Use verified rows for the range
        df_ver = df[df['actual'] != 'PENDING'].copy()
        
        print(f"📈 MARKET OVERVIEW: {df['symbol'].nunique()} Unique Stocks ({len(df)} Records)")
        if not df_ver.empty:
            min_date = df_ver['scan_date'].min()
            max_date = df_ver['scan_date'].max()
            total_verified = len(df_ver)
            print(f"   Data Range     : {min_date} to {max_date}")
            print(f"   Total Sample   : {total_verified} Verified Forecasts")
        print("-" * 50)
        for exchange in df['exchange'].unique():
            count = len(df[df['exchange'] == exchange])
            print(f"   {exchange}: {count} records")
        print()
    
    # Section 1: PREDICT TOMORROW
    # Display explicit data range and total sample to confirm statistical strength
    print("\n" + "═"*90)
    print("  STRATEGY INSIGHTS: PREDICT TOMORROW (V4.5)")
    print("═"*90)
    print(f"  Last Update : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Data Range  : {min_date} to {max_date}")
    print(f"  Total Sample: {total_verified} Verified Forecasts (Historical)")
    print("─" * 90)
    
    tmr_df = get_tomorrow_forecasts()
    
    if tmr_df.empty:
        print("📋 No forecasts available for tomorrow")
    else:
        for exchange in market_list:
            ex_df = tmr_df[tmr_df['exchange'] == exchange]
            if not ex_df.empty:
                print(f"--- {exchange} ---")
                header = f"  {'Symbol':<10} {'Thresh':>7}   {'Pattern':<10} {'Predict':<8} {'Prob (Stats)':<15}"
                print(header)
                print("─" * 60)
                
                last_symbol = ""
                for idx, row in ex_df.iterrows():
                    symbol = row['symbol']
                    if last_symbol != "" and symbol != last_symbol:
                        print("  " + "-" * 55)
                        
                    s_display = f"{symbol:<10}" if symbol != last_symbol else f"{'':<10}"
                    t_display = f"{row.get('threshold', 0.0):>6.2f}%" if symbol != last_symbol else f"{'':>7}"
                    pat = row.get('pattern', '+')
                    p_icon = "🟢" if row['forecast'] == "UP" else "🔴"
                    predict_display = f"{p_icon} {row['forecast']:<5}"
                    
                    prob_val = min(row['prob'], 100.0)
                    stats = int(row.get('stats', 0))
                    prob_stats_str = f"{prob_val:>5.1f}% ({stats})"
                    
                    print(f"  {s_display:<10} {t_display:<7}   {pat:<10} {predict_display:<8} {prob_stats_str:<15}")
                    last_symbol = symbol
                    
                print("─" * 60)
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
        
        for exchange in market_list:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                m_total = ex_acc_df['total'].sum()
                m_wins = ex_acc_df['correct'].sum()
                m_winrate = (m_wins / m_total * 100) if m_total > 0 else 0
                
                # Format for display: Win (+) Loss (-)
                m_avg_win = abs(ex_acc_df['avg_win'].mean())
                m_avg_loss = -abs(ex_acc_df['avg_loss'].mean())
                print(f"{exchange:<12} {m_total:<8.0f} {m_wins:<8.0f} {m_winrate:>7.1f}% {m_avg_win:>9.2f}% {m_avg_loss:>9.2f}%")
        
        # Calculate Global
        g_total = acc_df['total'].sum()
        g_wins = acc_df['correct'].sum()
        g_winrate = (g_wins / g_total * 100) if g_total > 0 else 0
        print("-" * 75)
        print(f"{'GLOBAL':<12} {g_total:<8.0f} {g_wins:<8.0f} {g_winrate:>7.1f}%")
        print("\n")

        # 2b. Per-Stock Details (V4.5 Standard Format)
        print("🎯 PER-STOCK PRECISION VIEW (STRATEGY INSIGHTS):")
        for exchange in market_list:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                print(f"--- {exchange} ---")
                header = f"  {'Symbol':<10} {'Thresh':>7}   {'Pattern':<10} {'Predict':<8} {'Prob (Stats)':<15} | {'Wins/Total':>11} {'Win%':>7} {'Avg.Win%':>9} {'Avg.Loss%':>9} {'RRR':>6}"
                print(header)
                print("─" * 120)
                
                # Sort for display
                ex_acc_df = ex_acc_df.sort_values(['symbol', 'accuracy'], ascending=[True, False])
                
                last_symbol = ""
                for idx, row in ex_acc_df.iterrows():
                    symbol = row['symbol']
                    
                    # Draw dotted line between DIFFERENT symbols
                    if last_symbol != "" and symbol != last_symbol:
                        print("  " + "-" * 115)
                        
                    s_display = f"{symbol:<10}" if symbol != last_symbol else f"{'':<10}"
                    t_display = f"{row['threshold']:>6.2f}%" if symbol != last_symbol else f"{'':>7}"
                    p_icon = "🟢" if row['forecast'] == 'UP' else "🔴"
                    predict_display = f"{p_icon} {row['forecast']:<5}"
                    
                    # Prob (Stats)
                    prob_val = min(row['prob'], 100.0)
                    prob_stats_str = f"{prob_val:>5.1f}% ({int(row['stats'])})"
                    
                    # Trade Stats
                    wins_total = f"{int(row['correct']):>3}/{int(row['total']):<7}"
                    win_rate_str = f"{row['accuracy']:>6.1f}%"
                    
                    # Avg Win/Loss Formatting
                    disp_win = abs(row['avg_win'])
                    disp_loss = -abs(row['avg_loss'])
                    avg_win_str = f"{disp_win:>8.2f}%" if disp_win != 0 else f"{' - ':>9}"
                    avg_loss_str = f"{disp_loss:>8.2f}%" if disp_loss != 0 else f"{' - ':>9}"
                    
                    rrr_str = f"{row['rrr']:>6.2f}" if row['rrr'] > 0 else f"{' - ':>6}"
                    
                    print(f"  {s_display:<10} {t_display:<7}   {row['pattern']:<10} {predict_display:<8} {prob_stats_str:<15} | {wins_total:>11} {win_rate_str:>7} {avg_win_str} {avg_loss_str} {rrr_str}")
                    last_symbol = symbol
                print("─" * 120)
                print()
    
    print("\n" + "=" * 100)
    print("🎯 Dashboard Complete (V4.5 Standard)")
    print("=" * 100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict N+1 Executive Dashboard")
    parser.add_argument("--market", type=str, help="Filter by market (SET, NASDAQ, TWSE, HKEX)")
    args = parser.parse_args()
    
    display_executive_dashboard(target_market=args.market)
