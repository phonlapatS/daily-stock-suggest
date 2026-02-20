#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
executive_dashboard.py - Predict N+1 Executive Dashboard
=============================================================
แสดงข้อมูลจาก logs/performance_log.csv และ forecast_tomorrow.csv
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Fix encoding for Windows console
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
    
    # ดึง forecasts ที่ target_date = พรุ่งนี้
    tomorrow_forecasts = df[df['target_date'] == tomorrow].copy()
    
    if len(tomorrow_forecasts) == 0:
        return pd.DataFrame()
    
    # คำนวณข้อมูลเพิ่มเติม
    tomorrow_forecasts['change_pct_abs'] = abs(tomorrow_forecasts['change_pct'])
    tomorrow_forecasts['threshold_display'] = tomorrow_forecasts['threshold'].apply(lambda x: f"±{x:.2f}%")
    
    return tomorrow_forecasts

def get_accuracy_report():
    """ดึงข้อมูล accuracy report จาก forward testing"""
    log_file = "logs/performance_log.csv"
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    df = pd.read_csv(log_file)
    
    # กรองเฉพาะที่ verified แล้ว
    verified_df = df[df['actual'] != 'PENDING'].copy()
    
    if len(verified_df) == 0:
        return pd.DataFrame()
    
    # คำนวณ accuracy สำหรับแต่ละ symbol
    accuracy_data = []
    
    for symbol in verified_df['symbol'].unique():
        symbol_data = verified_df[verified_df['symbol'] == symbol]
        
        total = len(symbol_data)
        correct = symbol_data['correct'].sum()
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        # คำนวณ avg win/loss
        correct_trades = symbol_data[symbol_data['correct'] == 1]
        wrong_trades = symbol_data[symbol_data['correct'] == 0]
        
        avg_win = correct_trades['change_pct'].mean() if len(correct_trades) > 0 else 0
        avg_loss = wrong_trades['change_pct'].mean() if len(wrong_trades) > 0 else 0
        
        # คำนวณ RRR
        rrr = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        # ดึง exchange จาก record แรกกแรกก
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

def format_number(num):
    """จัดรูปแบบตัวเลของ"""
    if pd.isna(num) or num == 0:
        return "0.00%"
    return f"{num:+.2f}%"

def get_symbol_name(symbol, exchange):
    """แปลงรหัสเป็นชื่อหุ้นจริง"""
    # Mapping สำหรับหุ้นไต้หวัน TWSE
    twse_names = {
        '3711': 'LITE-ON',
        '2454': 'KCE',
        '2395': 'WHA',
        '2330': 'TSMC',
        '2308': 'WHAUP',
        '2303': 'DELTA'
    }
    
    # Mapping สำหรับหุ้นจีน/ฮ่องกง HKEX
    hkex_names = {
        '3690': 'MEITU',
        '9866': 'KINGSTONE'
    }
    
    if exchange == 'TWSE':
        return twse_names.get(symbol, symbol)
    elif exchange == 'HKEX':
        return hkex_names.get(symbol, symbol)
    else:
        return symbol

def format_chance_direction(forecast):
    """จัดรูปแบบ emoji สำหรับ forecast direction"""
    if forecast == "UP":
        return "🟢 UP"
    elif forecast == "DOWN":
        return "🔴 DOWN"
    else:
        return "⚪ WAIT"

def display_executive_dashboard():
    """แสดง Executive Dashboard"""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("=" * 100)
    print("📊 PREDICT N+1 DASHBOARD")
    print(f"📅 Date: {today} | 🎯 Predict For: {tomorrow}")
    print("=" * 100)
    
    # แสดงสรุปจำนวนหุ้นทั้งหมด
    log_file = "logs/performance_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        exchange_counts = df['exchange'].value_counts()
        unique_symbols = df['symbol'].nunique()
        total_records = len(df)
        
        print(f"📈 MARKET OVERVIEW: {unique_symbols} Unique Stocks")
        print(f"📊 Total Records: {total_records}")
        print("-" * 50)
        for exchange, count in exchange_counts.items():
            exchange_names = {
                'SET': '🇹🇭 THAILAND',
                'NASDAQ': '🇺🇸 USA', 
                'TWSE': '🇹🇼 TAIWAN',
                'HKEX': '🇭🇰 HONG KONG'
            }
            # นับจำนวนหุ้นจริงตาม exchange
            exchange_symbols = df[df['exchange'] == exchange]['symbol'].nunique()
            print(f"   {exchange_names.get(exchange, exchange)}: {exchange_symbols} stocks ({count} records)")
        print()
    
    # Section 1: PREDICT TOMORROW
    print("1. PREDICT TOMORROW (" + tomorrow + ")")
    print("-" * 100)
    
    tomorrow_data = get_tomorrow_forecasts()
    
    if len(tomorrow_data) == 0:
        print("📋 No forecasts available for tomorrow")
    else:
        # Group by exchange
        exchange_names = {
            'TWSE': '🇹🇼 TAIWAN (TWSE)',
            'SET': '🇹🇭 THAILAND (SET)', 
            'NASDAQ': '🇺🇸 USA (NASDAQ)',
            'HKEX': '🇭🇰 HONG KONG (HKEX)'
        }
        
        for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
            exchange_data = tomorrow_data[tomorrow_data['exchange'] == exchange]
            
            if len(exchange_data) > 0:
                print(exchange_names.get(exchange, exchange))
                print("Symbol      Price     Chg%    Threshold   Pattern    Chance     Prob.       Stats     Exp.Move")
                print("-" * 96)
                
                # Sort by probability
                exchange_data = exchange_data.sort_values('prob', ascending=False)
                
                for _, row in exchange_data.iterrows():
                    symbol = row['symbol']
                    price = row['price_at_scan']
                    change_pct = row['change_pct']
                    threshold = row.get('threshold', change_pct * 1.5)  # Fallback to 1.5x change_pct
                    threshold_display = f"±{threshold:.2f}%"
                    pattern = row['pattern']
                    chance = format_chance_direction(row['forecast'])
                    prob = f"{row['prob']:.0f}%"
                    
                    # Parse stats from stats column - แยกจำนวน wins และ total bars
                    stats = row['stats']
                    if '/' in stats and '(' in stats and ')' in stats:
                        # Extract wins and total from "100/100 (5000)"
                        wins_part = stats.split('/')[0].strip()
                        total_part = stats.split('(')[1].replace(')', '').strip()
                        stats_display = f"{wins_part} ({total_part})"
                    elif stats.isdigit():
                        # Case where stats is just wins number like "54"
                        stats_display = f"{stats} (5000)"  # Default total bars
                    else:
                        stats_display = stats
                    
                    # Expected move (placeholder - ควรคำนวณจากข้อมูลจริง)
                    exp_move = format_number(row['change_pct'] * 0.8)  # Simple estimate
                    
                    print(f"{symbol:12} {price:8.1f}   {change_pct:+6.2f}%   {threshold:10}   {pattern:8}    {chance:9}     {prob:5}       {stats_display:10}   {exp_move:>9}")
                
                print()
    
    # Section 1.5: TODAY'S FORECASTS (Generated Today)
    print("2. TODAY'S FORECASTS (" + today + ")")
    print("-" * 100)
    
    # Get today's forecasts (scan_date = today)
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        today_forecasts = df[df['scan_date'] == today].copy()
        
        if len(today_forecasts) > 0:
            # Group by exchange
            for exchange in ['TWSE', 'SET', 'NASDAQ', 'HKEX']:
                exchange_data = today_forecasts[today_forecasts['exchange'] == exchange]
                
                if len(exchange_data) > 0:
                    print(exchange_names.get(exchange, exchange))
                    print("Symbol      Price     Chg%    Threshold   Pattern    Chance     Prob.       Stats     Exp.Move   Status")
                    print("-" * 105)
                    
                    # Sort by probability
                    exchange_data = exchange_data.sort_values('prob', ascending=False)
                    
                    # Show top 10 only
                    top_data = exchange_data.head(10)
                    for _, row in top_data.iterrows():
                        symbol = row['symbol']
                        price = row['price_at_scan']
                        change_pct = row['change_pct']
                        threshold = row.get('threshold_display', row.get('threshold', change_pct * 1.5))  # Fallback to 1.5x change_pct
                        threshold_display = f"±{threshold:.2f}%"
                        pattern = row['pattern']
                        chance = format_chance_direction(row['forecast'])
                        prob = f"{row['prob']:.0f}%"
                        
                        # Parse stats from stats column
                        stats = row['stats']
                        if '/' in stats and '(' in stats and ')' in stats:
                            wins_part = stats.split('/')[0].strip()
                            total_part = stats.split('(')[1].replace(')', '').strip()
                            stats_display = f"{wins_part} ({total_part})"
                        elif stats.isdigit():
                            stats_display = f"{stats} (5000)"
                        else:
                            stats_display = stats
                        
                        exp_move = format_number(row['change_pct'] * 0.8)
                        
                        # Check verification status
                        if row['actual'] != 'PENDING':
                            status = "Verified"
                        else:
                            status = "Pending"
                        
                        print(f"{symbol:12} {price:8.1f}   {change_pct:+6.2f}%   {threshold:10}   {pattern:8}    {chance:9}     {prob:5}       {stats_display:10}   {exp_move:>9}   {status}")
                    
                    if len(exchange_data) > 10:
                        print(f"   ... and {len(exchange_data) - 10} more")
                    print()
        else:
            print("📋 No forecasts generated today")
    else:
        print("📋 No forecast data available")
    
    # Section 2: ACCURACY REPORT
    print("3. ACCURACY REPORT (Forward Test Since Feb 12)")
    print("-" * 100)
    
    accuracy_data = get_accuracy_report()
    
    if len(accuracy_data) == 0:
        print("📋 No accuracy data available")
    else:
        # Group by exchange
        for exchange in ['SET', 'NASDAQ', 'TWSE', 'HKEX']:
            exchange_data = accuracy_data[accuracy_data['exchange'] == exchange]
            
            if len(exchange_data) > 0:
                exchange_names = {
                    'SET': '🇹🇭 THAILAND (SET Market)',
                    'NASDAQ': '🇺🇸 USA (NASDAQ Market)',
                    'TWSE': '🇹🇼 TAIWAN (TWSE Market)',
                    'HKEX': '🇭🇰 HONG KONG (HKEX Market)'
                }
                
                print(exchange_names.get(exchange, exchange))
                print("Symbol      Correct   Total    Acc%     Avg.Win%   Avg.Lose%    RRR")
                print("-" * 70)
                
                # Sort by accuracy
                exchange_data = exchange_data.sort_values('accuracy', ascending=False)
                
                for _, row in exchange_data.iterrows():
                    symbol = get_symbol_name(row['symbol'], exchange)
                    correct = row['correct']
                    total = row['total']
                    accuracy = row['accuracy']
                    avg_win = row['avg_win']
                    avg_loss = row['avg_loss']
                    rrr = row['rrr']
                    
                    print(f"{symbol:12} {correct:>8.0f} {total:>8} {accuracy:>7.1f}%        {avg_win:>8.2f}%      {avg_loss:>8.2f}%      {rrr:>8.2f}")
                
                print()
    
    # Section 3: MARKET OVERVIEW
    print("4. MARKET OVERVIEW")
    print("-" * 50)
    
    log_file = "logs/performance_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        exchange_counts = df['exchange'].value_counts()
        
        for exchange, count in exchange_counts.items():
            exchange_names = {
                'SET': '🇹🇭 THAILAND',
                'NASDAQ': '🇺🇸 USA', 
                'TWSE': '🇹🇼 TAIWAN',
                'HKEX': '🇭🇰 HONG KONG'
            }
            print(f"   📈 {exchange_names.get(exchange, exchange)}: {count} records")
        
        print(f"\n📊 Total Records: {len(df)}")
        
        # Count by status
        pending_count = len(df[df['actual'] == 'PENDING'])
        verified_count = len(df[df['actual'] != 'PENDING'])
        
        print(f"   ⏳ Pending: {pending_count}")
        print(f"   ✅ Verified: {verified_count}")
    else:
        print("📋 No market data available")
    
    print("\n" + "=" * 100)
    print("🎯 Predict N+1 Dashboard Complete")
    print("=" * 100)

def main():
    display_executive_dashboard()

if __name__ == "__main__":
    main()
