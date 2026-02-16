#!/usr/bin/env python
"""
analyze_main_system_results.py - วิเคราะห์ผลลัพธ์ของ Main System แต่ละประเทศ
"""

import sys
import os
import pandas as pd
import numpy as np

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def analyze_by_country():
    """วิเคราะห์ผลลัพธ์ของ Main System แต่ละประเทศ"""
    
    print("\n" + "="*80)
    print("📊 MAIN SYSTEM RESULTS BY COUNTRY")
    print("="*80)
    
    # 1. อ่าน full_backtest_results.csv (symbol-level summary)
    full_results_path = 'data/full_backtest_results.csv'
    if os.path.exists(full_results_path):
        df_full = pd.read_csv(full_results_path, on_bad_lines='skip', engine='python')
        print(f"\n✅ Loaded {len(df_full)} symbols from full_backtest_results.csv")
    else:
        print(f"\n❌ File not found: {full_results_path}")
        df_full = pd.DataFrame()
    
    # 2. อ่าน symbol_performance.csv (detailed metrics)
    perf_path = 'data/symbol_performance.csv'
    if os.path.exists(perf_path):
        df_perf = pd.read_csv(perf_path, on_bad_lines='skip', engine='python')
        print(f"✅ Loaded {len(df_perf)} symbols from symbol_performance.csv")
    else:
        print(f"❌ File not found: {perf_path}")
        df_perf = pd.DataFrame()
    
    # 3. อ่าน trade history files
    logs_dir = 'logs'
    trade_files = []
    if os.path.exists(logs_dir):
        for f in os.listdir(logs_dir):
            if f.startswith('trade_history_') and f.endswith('.csv'):
                trade_files.append(os.path.join(logs_dir, f))
    
    print(f"✅ Found {len(trade_files)} trade history file(s)")
    
    # 4. รวมข้อมูล trade history
    all_trades = []
    for tf in trade_files:
        try:
            df_trades = pd.read_csv(tf, on_bad_lines='skip', engine='python')
            all_trades.append(df_trades)
            print(f"   - {os.path.basename(tf)}: {len(df_trades)} trades")
        except Exception as e:
            print(f"   - {os.path.basename(tf)}: Error - {e}")
    
    if all_trades:
        df_all_trades = pd.concat(all_trades, ignore_index=True)
        print(f"\n✅ Total trades: {len(df_all_trades)}")
    else:
        df_all_trades = pd.DataFrame()
        print(f"\n⚠️  No trade history files found")
    
    # 5. วิเคราะห์ตามประเทศ
    countries = {}
    
    # จาก full_backtest_results.csv
    if not df_full.empty:
        for idx, row in df_full.iterrows():
            group = str(row.get('group', ''))
            
            # ระบุประเทศ
            if 'THAI' in group:
                country = 'THAI'
            elif 'US' in group:
                country = 'US'
            elif 'CHINA' in group or 'HK' in group:
                country = 'CHINA/HK'
            elif 'TAIWAN' in group:
                country = 'TAIWAN'
            else:
                country = 'OTHER'
            
            if country not in countries:
                countries[country] = {
                    'symbols': 0,
                    'total_trades': 0,
                    'correct_trades': 0,
                    'avg_wins': [],
                    'avg_losses': [],
                    'risk_rewards': []
                }
            
            countries[country]['symbols'] += 1
            countries[country]['total_trades'] += int(row.get('total', 0))
            countries[country]['correct_trades'] += int(row.get('correct', 0))
            
            avg_win = pd.to_numeric(row.get('avg_win', 0), errors='coerce')
            avg_loss = pd.to_numeric(row.get('avg_loss', 0), errors='coerce')
            risk_reward = pd.to_numeric(row.get('risk_reward', 0), errors='coerce')
            
            if pd.notna(avg_win) and avg_win > 0:
                countries[country]['avg_wins'].append(float(avg_win))
            if pd.notna(avg_loss) and avg_loss < 0:
                countries[country]['avg_losses'].append(abs(float(avg_loss)))
            if pd.notna(risk_reward) and risk_reward > 0:
                countries[country]['risk_rewards'].append(float(risk_reward))
    
    # จาก trade history (ถ้ามี) - คำนวณจาก trader_return โดยตรง
    if not df_all_trades.empty:
        # แปลง trader_return เป็น numeric
        df_all_trades['trader_return'] = pd.to_numeric(df_all_trades.get('trader_return', 0), errors='coerce')
        df_all_trades['correct'] = pd.to_numeric(df_all_trades.get('correct', 0), errors='coerce').fillna(0)
        
        for idx, row in df_all_trades.iterrows():
            exchange = str(row.get('exchange', '')).upper()
            group = str(row.get('group', ''))
            
            # ระบุประเทศ
            if 'SET' in exchange or 'THAI' in group:
                country = 'THAI'
            elif 'NASDAQ' in exchange or 'NYSE' in exchange or 'US' in group:
                country = 'US'
            elif 'HKEX' in exchange or 'SHANGHAI' in exchange or 'SHENZHEN' in exchange or 'CHINA' in group or 'HK' in group:
                country = 'CHINA/HK'
            elif 'TWSE' in exchange or 'TAIWAN' in group:
                country = 'TAIWAN'
            else:
                country = 'OTHER'
            
            if country not in countries:
                countries[country] = {
                    'symbols': 0,
                    'total_trades': 0,
                    'correct_trades': 0,
                    'avg_wins': [],
                    'avg_losses': [],
                    'risk_rewards': []
                }
            
            countries[country]['total_trades'] += 1
            if row.get('correct', 0) == 1:
                countries[country]['correct_trades'] += 1
            
            # คำนวณ win/loss จาก trader_return
            trader_return = row.get('trader_return', 0)
            if pd.notna(trader_return):
                if trader_return > 0:
                    countries[country]['avg_wins'].append(float(trader_return))
                elif trader_return < 0:
                    countries[country]['avg_losses'].append(abs(float(trader_return)))
    
    # 6. แสดงผลลัพธ์
    print("\n" + "="*80)
    print(f"{'Country':<15} {'Symbols':>10} {'Count':>12} {'Prob%':>10} {'AvgWin%':>12} {'AvgLoss%':>12} {'RRR':>8}")
    print("="*80)
    
    for country in ['THAI', 'US', 'CHINA/HK', 'TAIWAN']:
        if country not in countries:
            print(f"{country:<15} {'-':>10} {'-':>12} {'-':>10} {'-':>12} {'-':>12} {'-':>8}")
            continue
        
        data = countries[country]
        symbols = data['symbols']
        total = data['total_trades']
        correct = data['correct_trades']
        
        # Prob%
        prob = (correct / total * 100) if total > 0 else 0
        
        # AvgWin% (คำนวณจาก wins ทั้งหมด)
        avg_win = np.mean(data['avg_wins']) if data['avg_wins'] else 0
        
        # AvgLoss% (คำนวณจาก losses ทั้งหมด)
        avg_loss = np.mean(data['avg_losses']) if data['avg_losses'] else 0
        
        # RRR (คำนวณจาก avg_win / avg_loss)
        if avg_loss > 0:
            rrr = avg_win / avg_loss
        elif data['risk_rewards']:
            # Fallback: ใช้ risk_reward จาก full_backtest_results
            rrr = np.mean(data['risk_rewards'])
        else:
            rrr = 0
        
        print(f"{country:<15} {symbols:>10,} {total:>12,} {prob:>9.1f}% {avg_win:>11.2f}% {avg_loss:>11.2f}% {rrr:>7.2f}")
    
    print("="*80)
    
    # 7. แสดงรายละเอียดเพิ่มเติม (ถ้ามี)
    if not df_perf.empty:
        print("\n" + "="*80)
        print("📈 TOP PERFORMERS BY COUNTRY")
        print("="*80)
        
        for country in ['THAI', 'US', 'CHINA/HK', 'TAIWAN']:
            # กรองตามประเทศ
            if country == 'THAI':
                country_df = df_perf[df_perf['Country'] == 'TH']
            elif country == 'US':
                country_df = df_perf[df_perf['Country'] == 'US']
            elif country == 'CHINA/HK':
                country_df = df_perf[df_perf['Country'].isin(['CN', 'HK'])]
            elif country == 'TAIWAN':
                country_df = df_perf[df_perf['Country'] == 'TW']
            else:
                continue
            
            if country_df.empty:
                print(f"\n{country}: No data")
                continue
            
            # เรียงตาม Prob% และ Count
            top_df = country_df.nlargest(5, 'Prob%')
            
            print(f"\n{country} (Top 5 by Prob%):")
            print(f"{'Symbol':<10} {'Count':>8} {'Prob%':>8} {'RRR':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
            print("-" * 60)
            
            for idx, row in top_df.iterrows():
                symbol = row.get('symbol', 'N/A')
                count = int(row.get('Count', 0))
                prob = row.get('Prob%', 0)
                rrr = row.get('RR_Ratio', 0)
                avg_win = row.get('AvgWin%', 0)
                avg_loss = row.get('AvgLoss%', 0)
                
                print(f"{symbol:<10} {count:>8,} {prob:>7.1f}% {rrr:>7.2f} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    
    print("\n" + "="*80)
    print("✅ Analysis Complete")
    print("="*80 + "\n")

if __name__ == '__main__':
    analyze_by_country()

