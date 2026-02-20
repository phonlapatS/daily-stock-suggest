#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
calculate_performance_v2.py - Calculate Performance Summary
====================================
คำนวณสถิติ performance โดยรวม
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_performance():
    """คำนวณสถิติ performance โดยรวม"""
    
    print("📊 Performance Summary")
    print("=" * 50)
    
    # อ่านข้อมูลจาก performance_log.csv
    log_file = "logs/performance_log.csv"
    
    if not pd.io.file.file_exists(log_file):
        print("❌ ไม่พบไฟล์ performance_log.csv")
        return
    
    df = pd.read_csv(log_file)
    
    # กรองเฉพาะเฉพาะ verified แล้ว
    verified_df = df[df['actual'] != 'PENDING'].copy()
    
    if len(verified_df) == 0:
        print("📋 ยังไม่มีข้อมูลที่ตรวจสอบ")
        return
    
    # คำนวณสถิติโดยรวม
    total_forecasts = len(verified_df)
    correct_forecasts = len(verified_df[verified_df['correct'] == 1])
    accuracy = (correct_forecasts / total_forecasts) * 100 if total_forecasts > 0 else 0
    
    print(f"📈 สถิติการทายโดยรวม:")
    print(f"   - จำนวน forecasts ที่ตรวจสอบ: {total_forecasts}")
    print(f"   - จำนวนที่ทายถูก: {correct_forecasts}")
    print(f"   - จำนวนที่ทายผิด: {total_forecasts - correct_forecasts}")
    print(f"   - ความแม่น: {accuracy:.2f}%")
    print()
    
    # คำนวณ Win Rate โดยรวม
    win_rate = accuracy
    
    # คำนวณ Average Win และ Loss
    wins = verified_df[verified_df['correct'] == 1]
    losses = verified_df[verified_df['correct'] == 0]
    
    if len(wins) > 0:
        avg_win = wins['price_actual'].mean()
    else:
        avg_win = 0
    
    if len(losses) > 0:
        avg_loss = abs(losses['price_actual'].mean())
    else:
        avg_loss = 0
    
    # คำนวณ Risk-Reward Ratio
    rrr = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    print(f"📊 สถิติการทายโดยละเอียด:")
    print(f"   - Win Rate: {win_rate:.2f}%")
    print(f"   - Average Win: {avg_win:.2f}%")
    print(f"   - Average Loss: {avg_loss:.2f}%")
    print(f"   - Risk-Reward Ratio: {rrr:.2f}")
    print()
    
    # คำนวณสถิติการทายตามระยะง
    print("📊 สถิติการทายตามระยะง:")
    print("-" * 50)
    
    # แบ่งตาม exchange
    for exchange in ['SET', 'NASDAQ', 'TWSE', 'HKEX']:
        exchange_data = verified_df[verified_df['exchange'] == exchange]
        
        if len(exchange_data) > 0:
            exchange_total = len(exchange_data)
            exchange_correct = len(exchange_data[exchange_data['correct'] == 1])
            exchange_accuracy = (exchange_correct / exchange_total) * 100
            
            exchange_names = {
                'SET': '🇹🇭 ตลาดหุ้นไทย',
                'NASDAQ': '🇺🇸 ตลาดหุ้นอเมริกา',
                'TWSE': '🇹🇼 ตลาดหุ้นไต้หวัน',
                'HKEX': '🇭🇰 ตลาดหุ้นฮ่องกง'
            }
            
            print(f"   {exchange_names[exchange]}:")
            print(f"     - จำนวน forecasts: {exchange_total}")
            print(f"     - จำนวนที่ทายถูก: {exchange_correct}")
            print(f"     - ความแม่น: {exchange_accuracy:.2f}%")
            
            # คำนวณ RRR ตาม exchange
            exchange_wins = exchange_data[exchange_data['correct'] == 1]
            exchange_losses = exchange_data[exchange_data['correct'] == 0]
            
            if len(exchange_wins) > 0:
                exchange_avg_win = exchange_wins['price_actual'].mean()
            else:
                exchange_avg_win = 0
            
            if len(exchange_losses) > 0:
                exchange_avg_loss = abs(exchange_losses['price_actual'].mean())
            else:
                exchange_avg_loss = 0
            
            exchange_rrr = exchange_avg_win / exchange_avg_loss if exchange_avg_loss > 0 else float('inf')
            
            print(f"     - Average Win: {exchange_avg_win:.2f}%")
            print(f"     - Average Loss: {exchange_avg_loss:.2f}%")
            print(f"     - Risk-Reward Ratio: {exchange_rrr:.2f}")
            print()
    
    # คำนวณสถิติการทายตาม pattern
    print("📊 สถิติการทายตาม Pattern:")
    print("-" * 50)
    
    pattern_performance = verified_df.groupby('pattern').agg({
        'total': ('correct', 'count'),
        'correct': ('correct', 'sum'),
        'accuracy': ('correct', lambda x: (x.sum() / x.count() * 100) if x.count() > 0 else 0)
    }).reset_index()
    
    print(f"{'Pattern':<12} {'Total':>6} {'Correct':>8} {'Accuracy':>9}")
    print("-" * 50)
    
    for _, row in pattern_performance.sort_values('accuracy', ascending=False).iterrows():
        pattern = row['pattern']
        total = row['total']
        correct = row['correct']
        accuracy = row['accuracy']
        
        print(f"{pattern:<12} {total:>6} {correct:>8} {accuracy:>9.1f}%")
    
    print()
    
    # คำนวณสถิติการทายตามช่วงเวลา
    print("📊 สถิติการทายตามช่วงเวลา:")
    print("-" * 50)
    
    # แบ่งตามช่วงเวลา (30 วัน, 7 วัน, 1 วัน)
    verified_df['scan_date'] = pd.to_datetime(verified_df['scan_date'])
    current_date = verified_df['scan_date'].max()
    
    # 30 วัน
    start_30d = current_date - timedelta(days=30)
    data_30d = verified_df[verified_df['scan_date'] >= start_30d]
    
    if len(data_30d) > 0:
        accuracy_30d = (len(data_30d[data_30d['correct'] == 1]) / len(data_30d) * 100)
        print(f"   - 30 วันล่าสุด: {accuracy_30d:.2f}%")
    else:
        print("   - 30 วันล่าสุด: ไม่มีข้อมูล")
    
    # 7 วัน
    start_7d = current_date - timedelta(days=7)
    data_7d = verified_df[verified_df['scan_date'] >= start_7d]
    
    if len(data_7d) > 0:
        accuracy_7d = (len(data_7d[data_7d['correct'] == 1]) / len(data_7d) * 100)
        print(f"   - 7 วันล่าสุด: {accuracy_7d:.2f}%")
    else:
        print("   - 7 วันล่าสุด: ไม่มีข้อมูล")
    
    # 1 วัน
    start_1d = current_date - timedelta(days=1)
    data_1d = verified_df[verified_df['scan_date'] >= start_1d]
    
    if len(data_1d) > 0:
        accuracy_1d = (len(data_1d[data_1d['correct'] == 1]) / len(data_1d) * 100)
        print(f"   - 1 วันล่าสุด: {accuracy_1d:.2f}%")
    else:
        print("   - 1 วันล่าสุด: ไม่มีข้อมูล")
    
    print()
    print("🎯 สรุปการทาย:")
    if accuracy >= 60:
        print("   ✅ ความแม่นดี (≥60%) - มีประสิทธ์ที่ดี")
    elif accuracy >= 50:
        print("   ⚠️ ความแม่นปานกลาง (50-59%) - อาจต้องปรับปรับ")
    else:
        print("   ❌ ความแม่นต่ำ (<50%) - ควรจะต้องตรวจสอบ logic")
    
    print()
    print("💡 ข้อเสนอง:")
    print("   - ควรจะต้องมีความแม่น ≥60% ถึงจะถือว่ามีประสิทธ์ที่ดี")
    print("   - ความแม่น <50% ควรจะต้องตรวจสอบ logic ใหม่")
    print("   - ควรจะต้องพิจารณาการเปลี่ยน threshold หรือเพิ่ม logic")

if __name__ == "__main__":
    calculate_performance()
