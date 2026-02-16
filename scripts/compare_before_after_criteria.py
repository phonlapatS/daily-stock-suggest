#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
เปรียบเทียบ Before (เกณฑ์เดิม) vs After (Prob >= 60%, RRR >= 2.0)
"""
import pandas as pd
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(BASE_DIR, "data", "symbol_performance.csv")

def compare_before_after():
    """เปรียบเทียบ Before vs After"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("เปรียบเทียบ BEFORE vs AFTER (Prob >= 60%, RRR >= 2.0)")
    print("=" * 160)
    
    # กำหนดเกณฑ์ Before (เดิม) และ After (ใหม่)
    criteria = {
        'TH': {
            'name': 'THAI MARKET',
            'before': {'prob': 60.0, 'rrr': 1.2, 'count': 30},
            'after': {'prob': 60.0, 'rrr': 2.0, 'count': 30}
        },
        'US': {
            'name': 'US STOCK',
            'before': {'prob': 55.0, 'rrr': 1.2, 'count': 15},
            'after': {'prob': 60.0, 'rrr': 2.0, 'count': 15}
        },
        'CN': {
            'name': 'CHINA & HK MARKET',
            'before': {'prob': 60.0, 'rrr': 1.0, 'count': 20},
            'after': {'prob': 60.0, 'rrr': 2.0, 'count': 20}
        },
        'TW': {
            'name': 'TAIWAN MARKET',
            'before': {'prob': 53.0, 'rrr': 1.25, 'count': 25},
            'after': {'prob': 60.0, 'rrr': 2.0, 'count': 25}
        },
        'GL': {
            'name': 'METALS',
            'before': {'prob': 50.0, 'rrr': 0.0, 'count': 0},
            'after': {'prob': 60.0, 'rrr': 2.0, 'count': 0}
        }
    }
    
    for country_code, country_criteria in criteria.items():
        country_df = df[df['Country'] == country_code]
        if country_df.empty:
            continue
        
        before_crit = country_criteria['before']
        after_crit = country_criteria['after']
        country_name = country_criteria['name']
        
        # Before: เกณฑ์เดิม
        if before_crit['rrr'] > 0:
            before_filter = (
                (country_df['Prob%'] >= before_crit['prob']) &
                (country_df['RR_Ratio'] >= before_crit['rrr']) &
                (country_df['Count'] >= before_crit['count'])
            )
        else:
            before_filter = (country_df['Prob%'] >= before_crit['prob'])
        
        before_stocks = country_df[before_filter].sort_values('Prob%', ascending=False)
        
        # After: เกณฑ์ใหม่ (Prob >= 60%, RRR >= 2.0)
        after_filter = (
            (country_df['Prob%'] >= after_crit['prob']) &
            (country_df['RR_Ratio'] >= after_crit['rrr']) &
            (country_df['Count'] >= after_crit['count'])
        )
        after_stocks = country_df[after_filter].sort_values('Prob%', ascending=False)
        
        print(f"\n{'=' * 160}")
        print(f"{country_name}")
        print("=" * 160)
        
        print(f"\n📊 BEFORE (เกณฑ์เดิม):")
        print(f"   เกณฑ์: Prob >= {before_crit['prob']}%, RRR >= {before_crit['rrr']}, Count >= {before_crit['count']}")
        print(f"   จำนวนหุ้นที่ผ่าน: {len(before_stocks)} หุ้น")
        
        if not before_stocks.empty:
            print(f"\n   หุ้นที่ผ่านเกณฑ์:")
            print(f"   {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
            print(f"   {'-' * 70}")
            for _, row in before_stocks.iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                count = int(row['Count'])
                avg_win = row['AvgWin%']
                avg_loss = row['AvgLoss%']
                print(f"   {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
        else:
            print("   ไม่มีหุ้นที่ผ่านเกณฑ์")
        
        print(f"\n📊 AFTER (เกณฑ์ใหม่ - Prob >= 60%, RRR >= 2.0):")
        print(f"   เกณฑ์: Prob >= {after_crit['prob']}%, RRR >= {after_crit['rrr']}, Count >= {after_crit['count']}")
        print(f"   จำนวนหุ้นที่ผ่าน: {len(after_stocks)} หุ้น")
        
        if not after_stocks.empty:
            print(f"\n   หุ้นที่ผ่านเกณฑ์:")
            print(f"   {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
            print(f"   {'-' * 70}")
            for _, row in after_stocks.iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                count = int(row['Count'])
                avg_win = row['AvgWin%']
                avg_loss = row['AvgLoss%']
                print(f"   {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
        else:
            print("   ❌ ไม่มีหุ้นที่ผ่านเกณฑ์")
            
            # แสดงหุ้นที่ใกล้เกณฑ์ที่สุด
            print(f"\n   หุ้นที่ใกล้เกณฑ์ที่สุด (Prob >= 60%, RRR ใกล้ 2.0):")
            prob_60_plus = country_df[country_df['Prob%'] >= 60.0].sort_values('RR_Ratio', ascending=False)
            if not prob_60_plus.empty:
                print(f"   {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'Distance':>10}")
                print(f"   {'-' * 70}")
                for _, row in prob_60_plus.head(5).iterrows():
                    symbol = str(row['symbol'])
                    prob = row['Prob%']
                    rrr = row['RR_Ratio']
                    count = int(row['Count'])
                    distance = abs(rrr - 2.0)
                    print(f"   {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {distance:>9.2f}")
            else:
                print("   ไม่มีหุ้นที่ Prob >= 60%")
        
        # สรุปการเปลี่ยนแปลง
        print(f"\n📈 สรุปการเปลี่ยนแปลง:")
        print(f"   Before: {len(before_stocks)} หุ้น")
        print(f"   After: {len(after_stocks)} หุ้น")
        if len(before_stocks) > 0:
            reduction = len(before_stocks) - len(after_stocks)
            reduction_pct = (reduction / len(before_stocks)) * 100
            print(f"   ลดลง: {reduction} หุ้น ({reduction_pct:.1f}%)")
        else:
            print(f"   ไม่มีการเปลี่ยนแปลง (ไม่มีหุ้นผ่านเกณฑ์เดิม)")
    
    # สรุปภาพรวม
    print(f"\n{'=' * 160}")
    print("สรุปภาพรวม")
    print("=" * 160)
    
    total_before = 0
    total_after = 0
    
    for country_code, country_criteria in criteria.items():
        country_df = df[df['Country'] == country_code]
        if country_df.empty:
            continue
        
        before_crit = country_criteria['before']
        after_crit = country_criteria['after']
        
        # Before
        if before_crit['rrr'] > 0:
            before_filter = (
                (country_df['Prob%'] >= before_crit['prob']) &
                (country_df['RR_Ratio'] >= before_crit['rrr']) &
                (country_df['Count'] >= before_crit['count'])
            )
        else:
            before_filter = (country_df['Prob%'] >= before_crit['prob'])
        before_count = len(country_df[before_filter])
        
        # After
        after_filter = (
            (country_df['Prob%'] >= after_crit['prob']) &
            (country_df['RR_Ratio'] >= after_crit['rrr']) &
            (country_df['Count'] >= after_crit['count'])
        )
        after_count = len(country_df[after_filter])
        
        total_before += before_count
        total_after += after_count
        
        country_name = country_criteria['name']
        print(f"   {country_name:<25} Before: {before_count:>3} หุ้น → After: {after_count:>3} หุ้น")
    
    print(f"\n   {'รวมทั้งหมด':<25} Before: {total_before:>3} หุ้น → After: {total_after:>3} หุ้น")
    if total_before > 0:
        reduction = total_before - total_after
        reduction_pct = (reduction / total_before) * 100
        print(f"   {'ลดลง':<25} {reduction:>3} หุ้น ({reduction_pct:.1f}%)")
    
    print("=" * 160)

if __name__ == "__main__":
    compare_before_after()

