#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
forward_testing_report_v2.py - Forward Testing Report (Detailed)
=================================================
รายงานผลการทายใน forward testing แบบละเอียด
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_forward_testing_report():
    """สร้างรายงานผลการทายแบบละเอียด"""
    
    print("📊 Forward Testing Report (Detailed)")
    print("=" * 60)
    
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
    
    print(f"📈 สรุปโดยรวม:")
    total_forecasts = len(verified_df)
    correct_forecasts = len(verified_df[verified_df['correct'] == 1])
    accuracy = (correct_forecasts / total_forecasts) * 100 if total_forecasts > 0 else 0
    
    print(f"   - จำนวน forecasts ที่ตรวจสอบ: {total_forecasts}")
    print(f"   - จำนวนที่ทายถูก: {correct_forecasts}")
    print(f"   - จำนวนที่ทายผิด: {total_forecasts - correct_forecasts}")
    print(f"   - ความแม่นทั้วหมด: {accuracy:.2f}%")
    print()
    
    # แบ่งตาม exchange
    print("📊 รายงานตาม Exchange:")
    print("-" * 60)
    
    exchange_performance = []
    
    for exchange in ['SET', 'NASDAQ', 'TWSE', 'HKEX']:
        exchange_data = verified_df[verified_df['exchange'] == exchange]
        
        if len(exchange_data) > 0:
            exchange_total = len(exchange_data)
            exchange_correct = len(exchange_data[exchange_data['correct'] == 1])
            exchange_accuracy = (exchange_correct / exchange_total) * 100
            
            # คำนวณ RRR
            wins = exchange_data[exchange_data['correct'] == 1]
            losses = exchange_data[exchange_data['correct'] == 0]
            
            avg_win = wins['price_actual'].mean() if len(wins) > 0 else 0
            avg_loss = abs(losses['price_actual'].mean()) if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else float('inf')
            
            exchange_names = {
                'SET': '🇹🇭 ตลาดหุ้นไทย',
                'NASDAQ': '🇺🇸 ตลาดหุ้นอเมริกา',
                'TWSE': '🇹🇼 ตลาดหุ้นไต้หวัน',
                'HKEX': '🇭🇰 ตลาดหุ้นฮ่องกง'
            }
            
            exchange_performance.append({
                'exchange': exchange_names[exchange],
                'total': exchange_total,
                'correct': exchange_correct,
                'accuracy': exchange_accuracy,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'rrr': rrr
            })
    
    # แสดงตาราง
    print(f"{'Exchange':<15} {'Total':>6} {'Correct':>8} {'Accuracy':>9} {'Avg Win':>10} {'Avg Loss':>10} {'RRR':>8}")
    print("-" * 60)
    
    for perf in exchange_performance:
        print(f"{perf['exchange']:<15} {perf['total']:>6} {perf['correct']:>8} {perf['accuracy']:>9.1f}% {perf['avg_win']:>10.2f}% {perf['avg_loss']:>10.2f}% {perf['rrr']:>8.2f}")
    
    print()
    
    # แบ่งตาม pattern
    print("📊 รายงานตาม Pattern:")
    print("-" * 60)
    
    pattern_performance = verified_df.groupby('pattern').agg({
        'total': ('correct', 'count'),
        'correct': ('correct', 'sum'),
        'accuracy': ('correct', lambda x: (x.sum() / x.count() * 100) if x.count() > 0 else 0)
    }).reset_index()
    
    print(f"{'Pattern':<12} {'Total':>6} {'Correct':>8} {'Accuracy':>9}")
    print("-" * 60)
    
    for _, row in pattern_performance.sort_values('accuracy', ascending=False).iterrows():
        pattern = row['pattern']
        total = row['total']
        correct = row['correct']
        accuracy = row['accuracy']
        
        print(f"{pattern:<12} {total:>6} {correct:>8} {accuracy:>9.1f}%")
    
    print()
    
    # แบ่งตามวันที่ตรวจสอบ (30 วันล่าสุด)
    print("📅 สถิติการทาย 30 วันล่าสุด:")
    print("-" * 60)
    
    verified_df['scan_date'] = pd.to_datetime(verified_df['scan_date'])
    recent_days = verified_df['scan_date'].max() - timedelta(days=30)
    recent_data = verified_df[verified_df['scan_date'] >= recent_days]
    
    if len(recent_data) > 0:
        daily_stats = recent_data.groupby('scan_date').agg({
            'total': ('correct', 'count'),
            'correct': ('correct', 'sum')
        }).reset_index()
        
        daily_stats['accuracy'] = (daily_stats['correct'] / daily_stats['total'] * 100).round(2)
        
        # คำนวณค่าเฉลี่ยของ 30 วัน
        avg_accuracy_30d = daily_stats['accuracy'].mean()
        max_accuracy = daily_stats['accuracy'].max()
        min_accuracy = daily_stats['accuracy'].min()
        
        print(f"   - ความแม่นเฉลี่ย 30 วัน: {avg_accuracy_30d:.2f}%")
        print(f"   - ความแม่นสูงสุด: {max_accuracy:.2f}%")
        print(f"   - ความแม่นต่ำสุด: {min_accuracy:.2f}%")
        print()
        
        # 10 วันล่าสุด
        print("   10 วันล่าสุด:")
        recent_10d = daily_stats.sort_values('scan_date', ascending=False).head(10)
        
        print(f"   {'วันที่':<12} {'จำนวน':>6} {'ทายถูก':>8} {'ความแม่น':>9}")
        print("   " + "-" * 50)
        
        for _, row in recent_10d.iterrows():
            date_str = row['scan_date'].strftime('%Y-%m-%d')
            print(f"   {date_str:<12} {row['total']:>6} {row['correct']:>8} {row['accuracy']:>9}%")
    
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
    generate_forward_testing_report()
