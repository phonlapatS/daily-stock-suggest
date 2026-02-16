#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_metrics_by_country.py - วิเคราะห์หุ้นแต่ละประเทศว่าทำไมแสดงหรือไม่แสดง
================================================================================
ตรวจสอบว่า:
1. หุ้นแต่ละประเทศมีเกณฑ์การแสดงผลอย่างไร
2. หุ้นไหนแสดงเพราะอะไร (ผ่านเกณฑ์)
3. หุ้นไหนไม่แสดงเพราะอะไร (ไม่ผ่านเกณฑ์)
"""

import pandas as pd
import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
METRICS_FILE = os.path.join(DATA_DIR, "symbol_performance.csv")

# เกณฑ์การแสดงผลตามประเทศ (จาก calculate_metrics.py)
CRITERIA = {
    'TH': {
        'name': 'THAI MARKET',
        'prob_min': 60.0,
        'rrr_min': 1.2,
        'count_min': 30,
        'reason': 'หุ้นไทยใช้ Mean Reversion - ต้องการความถี่สูงและความแม่นยำสูง'
    },
    'US': {
        'name': 'US STOCK',
        'prob_min': 55.0,
        'rrr_min': 1.2,
        'count_min': 15,
        'reason': 'หุ้น US ใช้ Trend Momentum - ความถี่ต่ำแต่ผลตอบแทนสูง'
    },
    'CN': {
        'name': 'CHINA & HK MARKET',
        'prob_min': 55.0,
        'rrr_min': 1.2,
        'count_min': 15,
        'reason': 'หุ้นจีน/ฮ่องกง ใช้ Trend Momentum'
    },
    'TW': {
        'name': 'TAIWAN MARKET',
        'prob_min': 55.0,
        'rrr_min': 1.2,
        'count_min': 15,
        'reason': 'หุ้นไต้หวัน ใช้ Trend Momentum'
    },
    'GL': {
        'name': 'METALS',
        'prob_min': 50.0,
        'rrr_min': 0.0,  # ไม่มีเกณฑ์ RRR
        'count_min': 0,  # ไม่มีเกณฑ์ Count
        'reason': 'ทอง/โลหะ ใช้ Mean Reversion - เกณฑ์ต่ำกว่า'
    },
    'HK': {
        'name': 'HONG KONG',
        'prob_min': 55.0,
        'rrr_min': 1.2,
        'count_min': 15,
        'reason': 'หุ้นฮ่องกง ใช้ Trend Momentum'
    }
}

def analyze_symbol(symbol_row, criteria):
    """
    วิเคราะห์ว่าหุ้นผ่านเกณฑ์หรือไม่
    """
    symbol = symbol_row.get('symbol', '?')
    country = symbol_row.get('Country', 'GL')
    prob = symbol_row.get('Prob%', 0.0)
    rrr = symbol_row.get('RR_Ratio', 0.0)
    count = symbol_row.get('Count', 0)
    
    crit = criteria.get(country, CRITERIA['GL'])
    
    passed = True
    reasons = []
    failed_reasons = []
    
    # ตรวจสอบ Prob%
    if prob < crit['prob_min']:
        passed = False
        failed_reasons.append(f"Prob% {prob:.1f}% < {crit['prob_min']:.1f}% (ต่ำกว่าเกณฑ์)")
    else:
        reasons.append(f"Prob% {prob:.1f}% >= {crit['prob_min']:.1f}% ✓")
    
    # ตรวจสอบ RRR
    if crit['rrr_min'] > 0:
        if rrr < crit['rrr_min']:
            passed = False
            failed_reasons.append(f"RRR {rrr:.2f} < {crit['rrr_min']:.2f} (ต่ำกว่าเกณฑ์)")
        else:
            reasons.append(f"RRR {rrr:.2f} >= {crit['rrr_min']:.2f} ✓")
    
    # ตรวจสอบ Count
    if crit['count_min'] > 0:
        if count < crit['count_min']:
            passed = False
            failed_reasons.append(f"Count {count} < {crit['count_min']} (ข้อมูลไม่เพียงพอ)")
        else:
            reasons.append(f"Count {count} >= {crit['count_min']} ✓")
    
    return {
        'symbol': symbol,
        'country': country,
        'passed': passed,
        'prob': prob,
        'rrr': rrr,
        'count': count,
        'reasons': reasons,
        'failed_reasons': failed_reasons,
        'criteria': crit
    }

def main():
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์หุ้นแต่ละประเทศว่าทำไมแสดงหรือไม่แสดง")
    print("="*100)
    
    # Load data
    if not os.path.exists(METRICS_FILE):
        print(f"\n❌ ไม่พบไฟล์: {METRICS_FILE}")
        print("   กรุณารัน calculate_metrics.py ก่อน")
        return
    
    df = pd.read_csv(METRICS_FILE)
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    print(f"\n📊 โหลดข้อมูล: {len(df)} symbols ทั้งหมด")
    
    # แสดงเกณฑ์แต่ละประเทศ
    print("\n" + "="*100)
    print("[เกณฑ์การแสดงผลแต่ละประเทศ]")
    print("="*100)
    for country_code, crit in CRITERIA.items():
        print(f"\n{crit['name']} ({country_code}):")
        print(f"  - Prob% >= {crit['prob_min']:.1f}%")
        if crit['rrr_min'] > 0:
            print(f"  - RRR >= {crit['rrr_min']:.2f}")
        if crit['count_min'] > 0:
            print(f"  - Count >= {crit['count_min']}")
        print(f"  - เหตุผล: {crit['reason']}")
    
    # วิเคราะห์แต่ละประเทศ
    print("\n" + "="*100)
    print("[ผลการวิเคราะห์แต่ละประเทศ]")
    print("="*100)
    
    for country_code, crit in CRITERIA.items():
        country_data = df[df['Country'] == country_code].copy()
        
        if country_data.empty:
            print(f"\n{crit['name']} ({country_code}):")
            print("  ❌ ไม่มีข้อมูลหุ้นในประเทศนี้")
            continue
        
        print(f"\n{crit['name']} ({country_code}):")
        print(f"  📊 จำนวนหุ้นทั้งหมด: {len(country_data)} symbols")
        
        # วิเคราะห์แต่ละหุ้น
        passed_symbols = []
        failed_symbols = []
        
        for _, row in country_data.iterrows():
            analysis = analyze_symbol(row, CRITERIA)
            if analysis['passed']:
                passed_symbols.append(analysis)
            else:
                failed_symbols.append(analysis)
        
        # แสดงหุ้นที่ผ่านเกณฑ์
        print(f"\n  ✅ หุ้นที่แสดงผล ({len(passed_symbols)} symbols):")
        if passed_symbols:
            # เรียงตาม Prob% และ RRR
            passed_symbols.sort(key=lambda x: (x['prob'], x['rrr']), reverse=True)
            for sym in passed_symbols[:10]:  # แสดงแค่ 10 ตัวแรก
                print(f"     • {sym['symbol']:<10} Prob%: {sym['prob']:>5.1f}%  RRR: {sym['rrr']:>5.2f}  Count: {sym['count']:>4}")
                print(f"       เหตุผล: {', '.join(sym['reasons'])}")
            if len(passed_symbols) > 10:
                print(f"     ... และอีก {len(passed_symbols) - 10} symbols")
        else:
            print("     (ไม่มีหุ้นที่ผ่านเกณฑ์)")
        
        # แสดงหุ้นที่ไม่ผ่านเกณฑ์ (ตัวอย่าง)
        print(f"\n  ❌ หุ้นที่ไม่แสดงผล (ตัวอย่าง 5 ตัวแรก):")
        if failed_symbols:
            # เรียงตาม Prob% (สูงสุดก่อน)
            failed_symbols.sort(key=lambda x: x['prob'], reverse=True)
            for sym in failed_symbols[:5]:
                print(f"     • {sym['symbol']:<10} Prob%: {sym['prob']:>5.1f}%  RRR: {sym['rrr']:>5.2f}  Count: {sym['count']:>4}")
                print(f"       สาเหตุที่ไม่แสดง: {', '.join(sym['failed_reasons'])}")
            if len(failed_symbols) > 5:
                print(f"     ... และอีก {len(failed_symbols) - 5} symbols")
        else:
            print("     (ไม่มีหุ้นที่ไม่ผ่านเกณฑ์)")
        
        # สรุปสถิติ
        if country_data.shape[0] > 0:
            avg_prob = country_data['Prob%'].mean()
            avg_rrr = country_data['RR_Ratio'].mean()
            avg_count = country_data['Count'].mean()
            print(f"\n  📈 สถิติเฉลี่ย:")
            print(f"     - Prob% เฉลี่ย: {avg_prob:.1f}%")
            print(f"     - RRR เฉลี่ย: {avg_rrr:.2f}")
            print(f"     - Count เฉลี่ย: {avg_count:.1f}")
            print(f"     - ผ่านเกณฑ์: {len(passed_symbols)}/{len(country_data)} ({len(passed_symbols)/len(country_data)*100:.1f}%)")
    
    # สรุปภาพรวม
    print("\n" + "="*100)
    print("[สรุปภาพรวม]")
    print("="*100)
    
    total_symbols = len(df)
    total_passed = 0
    
    for country_code in CRITERIA.keys():
        country_data = df[df['Country'] == country_code]
        if country_data.empty:
            continue
        
        passed = 0
        for _, row in country_data.iterrows():
            analysis = analyze_symbol(row, CRITERIA)
            if analysis['passed']:
                passed += 1
        
        total_passed += passed
        crit = CRITERIA[country_code]
        print(f"{crit['name']:<25} {passed:>3}/{len(country_data):<3} ผ่านเกณฑ์ ({passed/len(country_data)*100 if len(country_data) > 0 else 0:.1f}%)")
    
    print(f"\nรวมทั้งหมด: {total_passed}/{total_symbols} symbols ผ่านเกณฑ์ ({total_passed/total_symbols*100:.1f}%)")
    print("="*100)

if __name__ == "__main__":
    main()

