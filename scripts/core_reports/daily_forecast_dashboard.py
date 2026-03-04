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

    if tomorrow_forecasts.empty:
        return tomorrow_forecasts

    # V4.6.2: Add Confidence Ranking (Merge historical metrics for sorting/display)
    acc_df = get_accuracy_report()
    if not acc_df.empty:
        # Pull performance metrics for the Predict table
        perf_lookup = acc_df[['exchange', 'symbol', 'pattern', 'forecast', 'accuracy', 'rrr', 'net_pnl', 'scan_date']]
        tomorrow_forecasts = tomorrow_forecasts.merge(
            perf_lookup, 
            on=['exchange', 'symbol', 'pattern', 'forecast'], 
            how='left'
        )
        # Fill NaN with 0
        tomorrow_forecasts['net_pnl'] = tomorrow_forecasts['net_pnl'].fillna(0)
        tomorrow_forecasts['accuracy'] = tomorrow_forecasts['accuracy'].fillna(0)
        tomorrow_forecasts['rrr'] = tomorrow_forecasts['rrr'].fillna(0)
        # Ensure the symbols with the highest probability patterns are at the top,
        # but keep all rows for the same symbol grouped together.
        tomorrow_forecasts['max_prob'] = tomorrow_forecasts.groupby('symbol')['prob'].transform('max')
        # Sort by Max Prob (Desc), Symbol (Asc), Prob (Desc), Net PnL (Desc)
        tomorrow_forecasts = tomorrow_forecasts.sort_values(
            by=['exchange', 'max_prob', 'symbol', 'prob', 'net_pnl'], 
            ascending=[True, False, True, False, False]
        )
        
    return tomorrow_forecasts

def get_accuracy_report():
    """ดึงข้อมูล accuracy report (Aggregated Strategy Insights V5.1)"""
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
    
    # Calculate Realized Profit/Loss based on direction
    if 'realized_change' not in verified_df.columns:
        verified_df['realized_change'] = (verified_df['price_actual'] - verified_df['price_at_scan']) / verified_df['price_at_scan'] * 100.0
    
    # Calculate Profit: If DOWN and price goes down, profit is positive.
    verified_df['profit'] = np.where(verified_df['forecast'] == 'UP', 
                                     verified_df['realized_change'], 
                                     -verified_df['realized_change'])

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
        
        avg_win = winning_trades['profit'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['profit'].mean() if len(losing_trades) > 0 else 0
        
        rrr = abs(avg_win / avg_loss) if avg_loss != 0 else (99.0 if avg_win != 0 else 0)
        
        net_pnl = g_df['profit'].mean()
        
        earliest_scan = g_df['scan_date'].min() if 'scan_date' in g_df.columns else "N/A"
        
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
            'rrr': rrr,
            'net_pnl': net_pnl,
            'scan_date': earliest_scan # Store for UI labeling
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

def get_recent_activity(market=None, limit=20):
    """ดึงข้อมูลการทำนายล่าสุดที่บรรลุผลแล้ว (Traceability)"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    df.columns = df.columns.str.strip()
    
    # Filter only verified
    verified_df = df[df['actual'] != 'PENDING'].copy()
    if market:
        verified_df = verified_df[verified_df['exchange'] == market]
        
    if verified_df.empty:
        return pd.DataFrame()
        
    # Sort by date (newest first)
    verified_df = verified_df.sort_values(['scan_date', 'symbol'], ascending=[False, True])
    
    # Calculate profit like accuracy report
    if 'realized_change' not in verified_df.columns:
        verified_df['realized_change'] = (verified_df['price_actual'] - verified_df['price_at_scan']) / verified_df['price_at_scan'] * 100.0
    
    verified_df['profit'] = np.where(verified_df['forecast'] == 'UP', 
                                     verified_df['realized_change'], 
                                     -verified_df['realized_change'])
    
    # V4.6.8: Filter to show ONLY the latest verified session (one date only)
    if not verified_df.empty:
        latest_date = verified_df['scan_date'].max()
        verified_df = verified_df[verified_df['scan_date'] == latest_date]
        
    # User Request: Sort by probability (prob) descending if available, and group by symbol
    if 'prob' in verified_df.columns:
        verified_df['max_prob'] = verified_df.groupby('symbol')['prob'].transform('max')
        verified_df = verified_df.sort_values(by=['max_prob', 'symbol', 'prob'], ascending=[False, True, False])
    else:
        verified_df = verified_df.sort_values('symbol')
        
    return verified_df

def get_pattern_distribution(market=None, limit=15):
    """คำนวณและดึงข้อมูล Distribution Analysis แบบรวบรัด"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    df.columns = df.columns.str.strip()
    
    verified_df = df[df['actual'] != 'PENDING'].copy()
    if market:
        verified_df = verified_df[verified_df['exchange'] == market.upper()]
        
    if verified_df.empty:
        return pd.DataFrame()
        
    verified_df['prob'] = pd.to_numeric(verified_df['prob'], errors='coerce').fillna(0)
    verified_df = verified_df[verified_df['prob'] > 0]
    
    if verified_df.empty:
        return pd.DataFrame()
        
    grouped = verified_df.groupby('pattern').agg(
        avg_prob=('prob', 'mean'),
        count=('prob', 'count')
    ).reset_index()
    
    grouped = grouped[grouped['count'] >= 10]
    sorted_df = grouped.sort_values('avg_prob', ascending=False).head(limit)
    return sorted_df

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
    print("📊 PREDICT N+1 DASHBOARD (V5.1)")
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
    print("  STRATEGY INSIGHTS: PREDICT TOMORROW (V5.1)")
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
                
                # V4.6.9: Add Forward Test Period Label above header (Right aligned)
                test_start = ex_df['scan_date'].min() if 'scan_date' in ex_df.columns else "2026-02-02"
                test_label = f"[ Forward Test Data: {test_start} - Present ]"
                print(f"{'':>105}{test_label}")
                
                header = f"  {'Symbol':<10} {'Thresh':>7}   {'Pattern':<10} {'Predict':<8} {'Prob (Stats)':<15} | {'Win%':>7} {'RRR':>6} {'Net PnL':>8}"
                print(header)
                print("─" * 90)
                
                last_symbol = ""
                for idx, row in ex_df.iterrows():
                    symbol = row['symbol']
                    if last_symbol != "" and symbol != last_symbol:
                        print("  " + "-" * 85)
                        
                    s_display = f"{symbol:<10}" if symbol != last_symbol else f"{'':<10}"
                    t_display = f"{row.get('threshold', 0.0):>6.2f}%" if symbol != last_symbol else f"{'':>7}"
                    pat = row.get('pattern', '+')
                    p_icon = "🟢" if row['forecast'] == "UP" else "🔴"
                    predict_display = f"{p_icon} {row['forecast']:<5}"
                    
                    prob_val = min(row['prob'], 100.0)
                    stats = int(row.get('stats', 0))
                    prob_stats_str = f"{prob_val:>5.1f}% ({stats})"
                    
                    # Performance Metrics (Alpha Columns)
                    win_pct = row.get('accuracy', 0.0)
                    rrr_val = row.get('rrr', 0.0)
                    pnl_val = row.get('net_pnl', 0.0)
                    
                    print(f"  {s_display:<10} {t_display:<7}   {pat:<10} {predict_display:<8} {prob_stats_str:<15} | {win_pct:>6.1f}% {rrr_val:>6.2f} {pnl_val:>7.2f}%")
                    last_symbol = symbol
                    
                print("─" * 90)
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
        print(f"{'Market':<12} {'Trades':<8} {'Wins':<8} {'Winrate':<10} {'Avg Win':<10} {'Avg Loss':<10} {'Net PnL'}")
        print("-" * 88)
        
        for exchange in market_list:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange]
            if not ex_acc_df.empty:
                m_total = ex_acc_df['total'].sum()
                m_wins = ex_acc_df['correct'].sum()
                m_winrate = (m_wins / m_total * 100) if m_total > 0 else 0
                
                # Format for display: Win (+) Loss (-)
                m_avg_win = abs(ex_acc_df['avg_win'].mean())
                m_avg_loss = -abs(ex_acc_df['avg_loss'].mean())
                m_net_pnl = ex_acc_df['net_pnl'].mean()
                print(f"{exchange:<12} {m_total:<8.0f} {m_wins:<8.0f} {m_winrate:>7.1f}% {m_avg_win:>9.2f}% {m_avg_loss:>9.2f}% {m_net_pnl:>9.2f}%")
        
        # Calculate Global
        g_total = acc_df['total'].sum()
        g_wins = acc_df['correct'].sum()
        g_winrate = (g_wins / g_total * 100) if g_total > 0 else 0
        g_net_pnl = acc_df['net_pnl'].mean()
        print("-" * 88)
        print(f"{'GLOBAL':<12} {g_total:<8.0f} {g_wins:<8.0f} {g_winrate:>7.1f}% {'':>23} {g_net_pnl:>9.2f}%")
        print("\n")

        # 2b. Per-Stock Details (V4.5 Standard Format)
        print("🎯 PER-STOCK PRECISION VIEW (STRATEGY INSIGHTS):")
        for exchange in market_list:
            ex_acc_df = acc_df[acc_df['exchange'] == exchange].copy()
            if not ex_acc_df.empty:
                print(f"--- {exchange} ---")
                # V4.6.9: Add Forward Test Period Label above header (Right aligned)
                test_start = ex_acc_df['scan_date'].min() if 'scan_date' in ex_acc_df.columns else "2026-02-02"
                test_label = f"[ Forward Test Data: {test_start} - Present ]"
                print(f"{'':>105}{test_label}")
                
                header = f"  {'Symbol':<10} {'Thresh':>7}   {'Pattern':<10} {'Predict':<8} {'Prob (Stats)':<15} | {'Wins/Total':>11} {'Win%':>7} {'Avg.Win%':>9} {'Avg.Loss%':>9} {'RRR':>6} {'Net PnL':>8}"
                print(header)
                print("─" * 130)
                
                # Sort for display: Group by symbol, order by max prob% globally, then internal prob% and net_pnl
                ex_acc_df['max_prob'] = ex_acc_df.groupby('symbol')['prob'].transform('max')
                ex_acc_df = ex_acc_df.sort_values(by=['max_prob', 'symbol', 'prob', 'net_pnl'], ascending=[False, True, False, False])
                
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
                    net_pnl_str = f"{row['net_pnl']:>8.2f}%"
                    
                    print(f"  {s_display:<10} {t_display:<7}   {row['pattern']:<10} {predict_display:<8} {prob_stats_str:<15} | {wins_total:>11} {win_rate_str:>7} {avg_win_str} {avg_loss_str} {rrr_str} {net_pnl_str}")
                    last_symbol = symbol
                print("─" * 130)
                print()
    
    # Section 3: RECENT ACTIVITY (Traceability)
    print("\n" + "═"*90)
    print("3. RECENT ACTIVITY LOG (Latest Session Traceability)")
    print("═"*90)
    # V4.6.8: Just get the latest session (no limit needed, function handles filter)
    recent_df = get_recent_activity(market=target_market)
    if recent_df.empty:
        print("📋 No recent activity recorded")
    else:
        # V4.6.8: Show the date in the session title if applicable
        latest_date = recent_df['scan_date'].iloc[0] if not recent_df.empty else "N/A"
        print(f"📊 Results for Scan Date: {latest_date}")
        
        # V4.6.9: Separate by country/market
        for market in market_list:
            market_df = recent_df[recent_df['exchange'] == market]
            if market_df.empty:
                continue
            
            print(f"\n--- {market} ---")
            header = f"  {'Symbol':<15} {'Pattern':<12} {'Predict':<10} {'Actual':<10} {'Result':<12} {'Target':<12} {'PnL%':>8}"
            print(header)
            print("─" * 90)
            for _, row in market_df.iterrows():
                p_icon = "🟢" if row['forecast'] == 'UP' else "🔴"
                res_icon = "✅ WIN" if row['correct'] == 1 else "❌ LOSS"
                actual_move = row['actual']
                # V4.6.1: Show 'NEUTRAL' explicitly per user request
                if actual_move == 'NEUTRAL': actual_move = 'NEUTRAL'
                
                # Format target date
                target_date = row.get('target_date', 'N/A')
                
                print(f"  {row['symbol']:<15} {row['pattern']:<12} {p_icon} {row['forecast']:<7} {actual_move:<10} {res_icon:<12} {target_date:<12} {row['profit']:>7.2f}%")
            print("─" * 90)

    # Section 4: PATTERN PROBABILITY DISTRIBUTION (Summary)
    print("\n" + "═"*90)
    print("4. PATTERN PROBABILITY DISTRIBUTION (Top Performing Patterns - Min 10 Occurrences)")
    print("═"*90)
    dist_df = get_pattern_distribution(market=target_market, limit=15)
    if dist_df.empty:
        print("📋 No distribution data available")
    else:
        header = f"  {'Pattern (Top 15)':<20} | {'Avg Prob%':>12} | {'Historical Occurrences':>25}"
        print(header)
        print("─" * 90)
        for _, row in dist_df.iterrows():
            print(f"  {row['pattern']:<20} | {row['avg_prob']:>11.2f}% | {int(row['count']):>25}")
        print("─" * 90)

    print("\n" + "=" * 100)
    print("🎯 Dashboard Complete (V5.1 compliant)")
    print("=" * 100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict N+1 Executive Dashboard")
    parser.add_argument("--market", type=str, help="Filter by market (SET, NASDAQ, TWSE, HKEX)")
    args = parser.parse_args()
    
    display_executive_dashboard(target_market=args.market)
