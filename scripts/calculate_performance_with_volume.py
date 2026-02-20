#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
calculate_performance_with_volume.py - Calculate Performance with Volume Filter
=================================================================
คำนวณสถิติ performance โดยรวมพร้อม volume filter
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_performance_with_volume():
    """คำนวณสถิติ performance พร้อม volume filter"""
    
    print("📊 Performance Summary with Volume Filter")
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
    
    # คำนวณ volume ratio (ถ้ามีข้อมูล volume)
    if 'volume' in verified_df.columns:
        # คำนวณ average volume ตาม symbol
        symbol_avg_volume = verified_df.groupby('symbol')['volume'].mean()
        
        # คำนวณ volume ratio
        def calculate_volume_ratio(row):
            symbol = row['symbol']
            current_volume = row['volume']
            avg_volume = symbol_avg_volume.get(symbol, 0)
            
            if avg_volume == 0:
                return 0
            
            return current_volume / avg_volume
        
        verified_df['volume_ratio'] = verified_df.apply(calculate_volume_ratio, axis=1)
        
        # กรองเฉพาะที่มี volume สูง
        high_volume_df = verified_df[verified_df['volume_ratio'] >= 1.2].copy()
        
        print(f"📈 สถิติการทายโดยรวม:")
        print(f"   - จำนวน forecasts ทั้วหมด: {len(verified_df)}")
        print(f"   - จำนวนที่มี volume สูง (≥1.2x): {len(high_volume_df)}")
        print(f"   - สัดส่วนที่มี volume สูง: {len(high_volume_df)/len(verified_df)*100:.1f}%")
        print()
        
        # คำนวณสถิติเฉพาะ high volume
        if len(high_volume_df) > 0:
            total_forecasts = len(high_volume_df)
            correct_forecasts = len(high_volume_df[high_volume_df['correct'] == 1])
            accuracy = (correct_forecasts / total_forecasts) * 100
            
            print(f"📊 สถิติเฉพาะ High Volume (≥1.2x):")
            print(f"   - จำนวน forecasts: {total_forecasts}")
            print(f"   - จำนวนที่ทายถูก: {correct_forecasts}")
            print(f"   - ความแม่น: {accuracy:.2f}%")
            print()
            
            # คำนวณ Win Rate โดยรวม
            win_rate = accuracy
            
            # คำนวณ Average Win และ Loss
            wins = high_volume_df[high_volume_df['correct'] == 1]
            losses = high_volume_df[high_volume_df['correct'] == 0]
            
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
            
            print(f"📊 สถิติการทายโดยละเอียด (High Volume):")
            print(f"   - Win Rate: {win_rate:.2f}%")
            print(f"   - Average Win: {avg_win:.2f}%")
            print(f"   - Average Loss: {avg_loss:.2f}%")
            print(f"   - Risk-Reward Ratio: {rrr:.2f}")
            print()
            
            # แบ่งตาม exchange (High Volume)
            print("📊 สถิติการทายตาม Exchange (High Volume):")
            print("-" * 60)
            
            for exchange in ['SET', 'NASDAQ', 'TWSE', 'HKEX']:
                exchange_data = high_volume_df[high_volume_df['exchange'] == exchange]
                
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
            
            # แบ่งตาม volume ratio
            print("📊 สถิติการทายตาม Volume Ratio:")
            print("-" * 60)
            
            volume_ranges = [
                (1.2, 1.5, "1.2x - 1.5x"),
                (1.5, 2.0, "1.5x - 2.0x"),
                (2.0, float('inf'), "≥2.0x")
            ]
            
            for min_ratio, max_ratio, label in volume_ranges:
                volume_data = high_volume_df[
                    (high_volume_df['volume_ratio'] >= min_ratio) &
                    (high_volume_df['volume_ratio'] < max_ratio)
                ]
                
                if len(volume_data) > 0:
                    volume_total = len(volume_data)
                    volume_correct = len(volume_data[volume_data['correct'] == 1])
                    volume_accuracy = (volume_correct / volume_total) * 100
                    
                    print(f"   Volume Ratio {label}:")
                    print(f"     - จำนวน forecasts: {volume_total}")
                    print(f"     - จำนวนที่ทายถูก: {volume_correct}")
                    print(f"     - ความแม่น: {volume_accuracy:.2f}%")
                    print()
    
    # สรุปการทายโดยรวม
    total_forecasts = len(verified_df)
    correct_forecasts = len(verified_df[verified_df['correct'] == 1])
    accuracy = (correct_forecasts / total_forecasts) * 100 if total_forecasts > 0 else 0
    
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
    print("   - Volume Filter (≥1.2x) ช่วยกรองหุ้นที่มีความสนใจสูง")
    print("   - หุ้นที่มี volume สูงมักมีความน่าเชื่อถือมั่นมากกว่า")
    print("   - ควรจะต้องพิจารณาการเปลี่ยน threshold หรือเพิ่ม logic")

if __name__ == "__main__":
    calculate_performance_with_volume()
