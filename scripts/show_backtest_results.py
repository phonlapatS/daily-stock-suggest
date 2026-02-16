#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
show_backtest_results.py - แสดงผลลัพธ์ Backtest แบบละเอียด
================================================================================
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_detailed_results(log_file='logs/trade_history.csv'):
    """แสดงผลลัพธ์ Backtest แบบละเอียด"""
    
    if not os.path.exists(log_file):
        print(f"❌ ไม่พบไฟล์: {log_file}")
        return
    
    try:
        df = pd.read_csv(log_file)
        # กรองเฉพาะ QUICK_TEST หรือ SINGLE_TEST (ล่าสุด)
        if 'group' in df.columns:
            df = df[df['group'].isin(['QUICK_TEST', 'SINGLE_TEST'])].copy()
    except Exception as e:
        print(f"❌ ไม่สามารถอ่านไฟล์ได้: {e}")
        return
    
    if df.empty:
        print("❌ ไม่มีข้อมูลในไฟล์")
        return
    
    # Convert columns
    if 'correct' in df.columns:
        df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
    if 'trader_return' in df.columns:
        df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce').fillna(0)
    if 'prob' in df.columns:
        df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
    
    print("\n" + "=" * 100)
    print("📊 ผลลัพธ์ Backtest แบบละเอียด (Filter: Prob > 60%, RRR >= 2.0)")
    print("=" * 100)
    
    # 1. สรุปโดยรวม
    total_trades = len(df)
    correct_trades = int(df['correct'].sum()) if 'correct' in df.columns else 0
    accuracy = (correct_trades / total_trades * 100) if total_trades > 0 else 0
    
    wins = df[df['correct'] == 1]['trader_return'].abs() if 'trader_return' in df.columns else pd.Series()
    losses = df[df['correct'] == 0]['trader_return'].abs() if 'trader_return' in df.columns else pd.Series()
    
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    realized_rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    total_return = df['trader_return'].sum() if 'trader_return' in df.columns else 0
    
    print(f"\n📈 สรุปโดยรวม:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Correct: {correct_trades}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print(f"   Avg Win%: {avg_win:.2f}%")
    print(f"   Avg Loss%: {avg_loss:.2f}%")
    print(f"   Realized RRR: {realized_rrr:.2f}")
    print(f"   Total Return%: {total_return:.2f}%")
    
    # 2. วิเคราะห์ตาม Symbol
    if 'symbol' in df.columns:
        print(f"\n📊 ผลลัพธ์ตาม Symbol:")
        print("=" * 100)
        print(f"{'Symbol':<12} {'Trades':<8} {'Correct':<8} {'Accuracy':<12} {'Avg Win%':<12} {'Avg Loss%':<12} {'RRR':<10} {'Total Return%':<15}")
        print("-" * 100)
        
        for symbol in df['symbol'].unique():
            s_df = df[df['symbol'] == symbol].copy()
            s_trades = len(s_df)
            s_correct = int(s_df['correct'].sum())
            s_acc = (s_correct / s_trades * 100) if s_trades > 0 else 0
            
            s_wins = s_df[s_df['correct'] == 1]['trader_return'].abs()
            s_losses = s_df[s_df['correct'] == 0]['trader_return'].abs()
            
            s_avg_win = s_wins.mean() if len(s_wins) > 0 else 0
            s_avg_loss = s_losses.mean() if len(s_losses) > 0 else 0
            s_rrr = s_avg_win / s_avg_loss if s_avg_loss > 0 else 0
            s_total_return = s_df['trader_return'].sum()
            
            print(f"{symbol:<12} {s_trades:<8} {s_correct:<8} {s_acc:<12.2f} {s_avg_win:<12.2f} {s_avg_loss:<12.2f} {s_rrr:<10.2f} {s_total_return:<15.2f}")
        
        print("-" * 100)
    
    # 3. แสดง Trade Logs ล่าสุด
    if 'date' in df.columns:
        print(f"\n📝 Trade Logs ล่าสุด (10 รายการ):")
        print("=" * 100)
        df_sorted = df.sort_values('date', ascending=False) if 'date' in df.columns else df
        
        cols = ['date', 'symbol', 'pattern', 'forecast', 'prob', 'actual', 'trader_return', 'correct']
        available_cols = [c for c in cols if c in df_sorted.columns]
        
        print(f"{'Date':<12} {'Symbol':<10} {'Pattern':<10} {'Forecast':<10} {'Prob%':<8} {'Actual':<8} {'Return%':<10} {'Result':<8}")
        print("-" * 100)
        
        for idx, row in df_sorted.head(10).iterrows():
            date_str = str(row['date'])[:10] if 'date' in row else 'N/A'
            symbol = row.get('symbol', 'N/A')
            pattern = row.get('pattern', 'N/A')
            forecast = row.get('forecast', 'N/A')
            prob = f"{row.get('prob', 0):.1f}" if 'prob' in row else 'N/A'
            actual = row.get('actual', 'N/A')
            ret = f"{row.get('trader_return', 0):.2f}" if 'trader_return' in row else 'N/A'
            result = "✅ WIN" if row.get('correct', 0) == 1 else "❌ LOSS"
            
            print(f"{date_str:<12} {symbol:<10} {pattern:<10} {forecast:<10} {prob:<8} {actual:<8} {ret:<10} {result:<8}")
        
        print("-" * 100)
    
    # 4. วิเคราะห์ตาม Prob Range
    if 'prob' in df.columns:
        print(f"\n📊 วิเคราะห์ตาม Prob Range:")
        print("=" * 100)
        print(f"{'Prob Range':<15} {'Trades':<10} {'Correct':<10} {'Accuracy':<12} {'Avg Win%':<12} {'Avg Loss%':<12} {'RRR':<10}")
        print("-" * 100)
        
        prob_ranges = [
            (60, 65, "60-65%"),
            (65, 70, "65-70%"),
            (70, 75, "70-75%"),
            (75, 100, "75%+")
        ]
        
        for min_prob, max_prob, label in prob_ranges:
            range_df = df[(df['prob'] > min_prob) & (df['prob'] <= max_prob)].copy()
            if len(range_df) > 0:
                range_trades = len(range_df)
                range_correct = int(range_df['correct'].sum())
                range_acc = (range_correct / range_trades * 100) if range_trades > 0 else 0
                
                range_wins = range_df[range_df['correct'] == 1]['trader_return'].abs()
                range_losses = range_df[range_df['correct'] == 0]['trader_return'].abs()
                
                range_avg_win = range_wins.mean() if len(range_wins) > 0 else 0
                range_avg_loss = range_losses.mean() if len(range_losses) > 0 else 0
                range_rrr = range_avg_win / range_avg_loss if range_avg_loss > 0 else 0
                
                print(f"{label:<15} {range_trades:<10} {range_correct:<10} {range_acc:<12.2f} {range_avg_win:<12.2f} {range_avg_loss:<12.2f} {range_rrr:<10.2f}")
        
        print("-" * 100)
    
    # 5. Pattern ที่ดีที่สุด
    if 'pattern' in df.columns:
        print(f"\n🏆 Pattern ที่ดีที่สุด (Top 10):")
        print("=" * 100)
        
        pattern_stats = []
        for pattern in df['pattern'].unique():
            p_df = df[df['pattern'] == pattern].copy()
            p_trades = len(p_df)
            p_correct = int(p_df['correct'].sum())
            p_acc = (p_correct / p_trades * 100) if p_trades > 0 else 0
            
            p_wins = p_df[p_df['correct'] == 1]['trader_return'].abs()
            p_losses = p_df[p_df['correct'] == 0]['trader_return'].abs()
            
            p_avg_win = p_wins.mean() if len(p_wins) > 0 else 0
            p_avg_loss = p_losses.mean() if len(p_losses) > 0 else 0
            p_rrr = p_avg_win / p_avg_loss if p_avg_loss > 0 else 0
            
            pattern_stats.append({
                'pattern': pattern,
                'trades': p_trades,
                'accuracy': p_acc,
                'rrr': p_rrr
            })
        
        pattern_stats.sort(key=lambda x: (x['accuracy'], x['rrr']), reverse=True)
        
        print(f"{'Pattern':<15} {'Trades':<10} {'Accuracy':<12} {'RRR':<10}")
        print("-" * 100)
        
        for stat in pattern_stats[:10]:
            print(f"{stat['pattern']:<15} {stat['trades']:<10} {stat['accuracy']:<12.2f} {stat['rrr']:<10.2f}")
        
        print("-" * 100)
    
    # 6. สรุปและคำแนะนำ
    print(f"\n💡 สรุป:")
    print("=" * 100)
    print(f"✅ Filter Criteria: Prob > 60%, RRR >= 2.0 (ตาม Mentor)")
    print(f"✅ Total Trades: {total_trades} trades")
    print(f"✅ Overall Accuracy: {accuracy:.2f}%")
    print(f"✅ Realized RRR: {realized_rrr:.2f}")
    
    if accuracy >= 60:
        print(f"✅ Accuracy ดีมาก! ({accuracy:.2f}% >= 60%)")
    elif accuracy >= 50:
        print(f"⚠️  Accuracy พอใช้ ({accuracy:.2f}%) - อาจต้องปรับปรุง")
    else:
        print(f"❌ Accuracy ต่ำ ({accuracy:.2f}%) - ต้องปรับปรุง")
    
    if realized_rrr >= 2.0:
        print(f"✅ Realized RRR ดีมาก! ({realized_rrr:.2f} >= 2.0)")
    elif realized_rrr >= 1.5:
        print(f"⚠️  Realized RRR พอใช้ ({realized_rrr:.2f})")
    else:
        print(f"❌ Realized RRR ต่ำ ({realized_rrr:.2f}) - Historical RRR >= 2.0 แต่ Realized RRR ต่ำกว่า")
    
    print("=" * 100)


def main():
    """Main function"""
    log_file = 'logs/trade_history.csv'
    show_detailed_results(log_file)


if __name__ == "__main__":
    main()

