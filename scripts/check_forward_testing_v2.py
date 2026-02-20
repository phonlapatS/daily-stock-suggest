#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_forward_testing_v2.py - Check Forward Testing Results
=================================================
ตรวจสอบผลการทายใน forward testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def check_forward_testing():
    """ตรวจสอบผลการทายใน forward testing"""
    
    print("🔍 ตรวจสอบผล Forward Testing")
    print("=" * 50)
    
    # อ่านข้อมูลจาก performance_log.csv
    log_file = "logs/performance_log.csv"
    
    if not pd.io.file.file_exists(log_file):
        print("❌ ไม่พบไฟล์ performance_log.csv")
        return
    
    df = pd.read_csv(log_file)
    
    # กรองเฉพาะเฉพาะ verified แล้ว
    verified_df = df[df['actual'] != 'PENDING'].copy()
    pending_df = df[df['actual'] == 'PENDING'].copy()
    
    print(f"📊 ข้อมูลทั้วหมด:")
    print(f"   - จำนวน forecasts ทั้วหมด: {len(df)}")
    print(f"   - จำนวนที่ตรวจสอบแล้ว: {len(verified_df)}")
    print(f"   - จำนวนที่รอตรวจสอบ: {len(pending_df)}")
    print()
    
    if len(verified_df) == 0:
        print("📋 ยังไม่มีข้อมูลที่ตรวจสอบ")
        return
    
    # คำนวณสถิติโดยรวม
    total_forecasts = len(verified_df)
    correct_forecasts = len(verified_df[verified_df['correct'] == 1])
    accuracy = (correct_forecasts / total_forecasts) * 100 if total_forecasts > 0 else 0
    
    print(f"📈 สถิติการทายโดยรวม:")
    print(f"   - จำนวนที่ตรวจสอบ: {total_forecasts}")
    print(f"   - ทายถูก: {correct_forecasts}")
    print(f"   - ทายผิด: {total_forecasts - correct_forecasts}")
    print(f"   - ความแม่น: {accuracy:.2f}%")
    print()
    
    # แบ่งตาม exchange
    print("📊 สถิติการทายตาม Exchange:")
    print("-" * 50)
    
    for exchange in ['SET', 'NASDAQ', 'TWSE', 'HKEX']:
        exchange_data = verified_df[verified_df['exchange'] == exchange]
        
        if len(exchange_data) > 0:
            exchange_total = len(exchange_data)
            exchange_correct = len(exchange_data[exchange_data['correct'] == 1])
            exchange_accuracy = (exchange_correct / exchange_total) * 100
            
            exchange_names = {
                'SET': '🇹🇭 ไทย',
                'NASDAQ': '🇺🇸 อเมริกา',
                'TWSE': '🇹🇼 ไต้หวัน',
                'HKEX': '🇭🇰 ฮ่องกง'
            }
            
            print(f"   {exchange_names[exchange]}:")
            print(f"     - จำนวนที่ตรวจสอบ: {exchange_total}")
            print(f"     - ทายถูก: {exchange_correct}")
            print(f"     - ความแม่น: {exchange_accuracy:.2f}%")
            print()
    
    # แบ่งตามวันที่ตรวจสอบ
    print("📅 สถิติการทายตามวันที่ตรวจสอบ (7 วันล่าสุด):")
    print("-" * 50)
    
    verified_df['scan_date'] = pd.to_datetime(verified_df['scan_date'])
    recent_days = verified_df['scan_date'].max() - timedelta(days=7)
    recent_data = verified_df[verified_df['scan_date'] >= recent_days]
    
    if len(recent_data) > 0:
        daily_stats = recent_data.groupby('scan_date').agg({
            'total': ('correct', 'count'),
            'correct': ('correct', 'sum')
        }).reset_index()
        
        daily_stats['accuracy'] = (daily_stats['correct'] / daily_stats['total'] * 100).round(2)
        
        print("   วันที่ตรวจสอบ    จำนวน  ทายถูก  ความแม่น")
        print("   " + "-" * 50)
        
        for _, row in daily_stats.sort_values('scan_date', ascending=False).iterrows():
            date_str = row['scan_date'].strftime('%Y-%m-%d')
            print(f"   {date_str}        {row['total']:>6}     {row['correct']:>6}     {row['accuracy']:>7}%")
    else:
        print("   ไม่มีข้อมูลใน 7 วันที่ผ่านมา")
    
    print()
    print("🎯 สรุป:")
    if accuracy >= 60:
        print("   ✅ ความแม่นดี (≥60%)")
    elif accuracy >= 50:
        print("   ⚠️ ความแม่นปานกลาง (50-59%)")
    else:
        print("   ❌ ความแม่นต่ำ (<50%)")
    
    print()
    print("💡 คำแนะนำ:")
    print("   - ความแม่น ≥60% ถือว่ามีประสิทธ์ที่ดี")
    print("   - ความแม่น 50-59% ควรจะต้องปรับปรับปรับ")
    print("   - ความแม่น <50% ควรจะต้องตรวจสอบ logic ใหม่")

if __name__ == "__main__":
    check_forward_testing()
