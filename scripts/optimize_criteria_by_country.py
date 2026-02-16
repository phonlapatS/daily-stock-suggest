#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
วิเคราะห์และแนะนำเกณฑ์ RRR ที่เหมาะสมสำหรับแต่ละประเทศ
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

def calculate_expected_value(prob, rrr):
    """คำนวณ Expected Value"""
    win_rate = prob / 100.0
    loss_rate = 1.0 - win_rate
    ev = (win_rate * rrr) - (loss_rate * 1.0)
    return ev

def optimize_criteria_by_country():
    """วิเคราะห์และแนะนำเกณฑ์ที่เหมาะสม"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 160)
    print("วิเคราะห์และแนะนำเกณฑ์ RRR ที่เหมาะสมสำหรับแต่ละประเทศ")
    print("=" * 160)
    
    recommendations = {}
    
    for country in ['TH', 'US', 'CN', 'TW', 'GL']:
        country_df = df[df['Country'] == country]
        if country_df.empty:
            continue
        
        country_name = {
            'TH': 'THAI',
            'US': 'US',
            'CN': 'CHINA/HK',
            'TW': 'TAIWAN',
            'GL': 'METALS'
        }.get(country, country)
        
        print(f"\n{'=' * 160}")
        print(f"{country_name}")
        print("=" * 160)
        
        # กรองหุ้นที่มี Prob >= 60%
        prob_60 = country_df[country_df['Prob%'] >= 60.0].copy()
        if prob_60.empty:
            print(f"  ❌ ไม่มีหุ้นที่ Prob >= 60%")
            continue
        
        # คำนวณ EV
        prob_60['EV'] = prob_60.apply(lambda row: calculate_expected_value(row['Prob%'], row['RR_Ratio']), axis=1)
        
        # ทดสอบเกณฑ์ RRR ต่างๆ
        rrr_levels = [1.5, 1.4, 1.3, 1.25, 1.2]
        
        print(f"\n  หุ้นที่มี Prob >= 60%: {len(prob_60)} หุ้น")
        print(f"\n  📊 ทดสอบเกณฑ์ RRR ต่างๆ:")
        print(f"    {'RRR':>8} {'จำนวนหุ้น':>12} {'EV เฉลี่ย':>12} {'EV ต่ำสุด':>12} {'EV สูงสุด':>12} {'คำแนะนำ':<30}")
        print(f"    {'-' * 100}")
        
        best_rrr = None
        best_score = -1
        
        for rrr_level in rrr_levels:
            filtered = prob_60[prob_60['RR_Ratio'] >= rrr_level]
            
            if len(filtered) == 0:
                print(f"    {rrr_level:>7.2f} {'0':>12} {'N/A':>12} {'N/A':>12} {'N/A':>12} {'ไม่มีหุ้น':<30}")
                continue
            
            avg_ev = filtered['EV'].mean()
            min_ev = filtered['EV'].min()
            max_ev = filtered['EV'].max()
            
            # คะแนน = จำนวนหุ้น * EV เฉลี่ย (ถ้า EV >= 0.4)
            if avg_ev >= 0.4:
                score = len(filtered) * avg_ev
            else:
                score = 0
            
            if score > best_score:
                best_score = score
                best_rrr = rrr_level
            
            # คำแนะนำ
            if avg_ev >= 0.5:
                recommendation = "✅ ดีมาก - คุ้มค่าเสี่ยง"
            elif avg_ev >= 0.4:
                recommendation = "✅ ดี - คุ้มค่าเสี่ยง"
            elif avg_ev >= 0.3:
                recommendation = "⚠️  พอใช้ - คุ้มค่าเสี่ยงเล็กน้อย"
            else:
                recommendation = "❌ ไม่แนะนำ - EV ต่ำ"
            
            print(f"    {rrr_level:>7.2f} {len(filtered):>12} {avg_ev:>11.3f} {min_ev:>11.3f} {max_ev:>11.3f} {recommendation}")
        
        # แนะนำเกณฑ์ที่เหมาะสม
        if best_rrr:
            recommended = prob_60[prob_60['RR_Ratio'] >= best_rrr]
            avg_ev = recommended['EV'].mean()
            
            print(f"\n  💡 แนะนำเกณฑ์: RRR >= {best_rrr}")
            print(f"     - จำนวนหุ้น: {len(recommended)} หุ้น")
            print(f"     - EV เฉลี่ย: {avg_ev:.3f}")
            print(f"     - EV ต่ำสุด: {recommended['EV'].min():.3f}")
            print(f"     - EV สูงสุด: {recommended['EV'].max():.3f}")
            
            recommendations[country] = {
                'name': country_name,
                'rrr': best_rrr,
                'count': len(recommended),
                'avg_ev': avg_ev,
                'stocks': recommended[['symbol', 'Prob%', 'RR_Ratio', 'Count', 'EV']].to_dict('records')
            }
            
            # แสดงหุ้นที่ผ่านเกณฑ์
            print(f"\n     หุ้นที่ผ่านเกณฑ์:")
            print(f"       {'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'EV':>8}")
            print(f"       {'-' * 60}")
            for _, row in recommended.sort_values('EV', ascending=False).iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                count = int(row['Count'])
                ev = row['EV']
                print(f"       {symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {ev:>7.3f}")
        else:
            print(f"\n  ⚠️  ไม่มีเกณฑ์ที่เหมาะสม (EV < 0.4)")
            recommendations[country] = {
                'name': country_name,
                'rrr': None,
                'count': 0,
                'avg_ev': 0,
                'stocks': []
            }
    
    # สรุปคำแนะนำ
    print(f"\n{'=' * 160}")
    print("สรุปคำแนะนำเกณฑ์สำหรับแต่ละประเทศ")
    print("=" * 160)
    print(f"\n{'Country':<15} {'RRR >=':>10} {'จำนวนหุ้น':>12} {'EV เฉลี่ย':>12} {'สถานะ':<20}")
    print("-" * 160)
    
    for country, rec in recommendations.items():
        if rec['rrr']:
            status = "✅ แนะนำ" if rec['avg_ev'] >= 0.4 else "⚠️  พิจารณา"
            print(f"{rec['name']:<15} {rec['rrr']:>9.2f} {rec['count']:>12} {rec['avg_ev']:>11.3f} {status}")
        else:
            print(f"{rec['name']:<15} {'N/A':>10} {'0':>12} {'N/A':>12} {'❌ ไม่แนะนำ'}")
    
    print("\n" + "=" * 160)
    print("โค้ดสำหรับ calculate_metrics.py:")
    print("=" * 160)
    print("""
# THAI MARKET
thai_trend = summary_df[
    (summary_df['Country'] == 'TH') & 
    (summary_df['Prob%'] >= 60.0) & 
    (summary_df['RR_Ratio'] >= {thai_rrr}) &
    (summary_df['Count'] >= 30)
].sort_values(by='Prob%', ascending=False)
print_market_section(thai_trend, "[THAI MARKET]", "Prob >= 60% | RRR >= {thai_rrr} | Count >= 30")

# US STOCK
us_trend = summary_df[
    (summary_df['Country'] == 'US') & 
    (summary_df['Prob%'] >= 60.0) & 
    (summary_df['RR_Ratio'] >= {us_rrr}) &
    (summary_df['Count'] >= 15)
].sort_values(by='Prob%', ascending=False)
print_market_section(us_trend, "[US STOCK]", "Prob >= 60% | RRR >= {us_rrr} | Count >= 15")

# CHINA & HK MARKET
china_trend = summary_df[
    ((summary_df['Country'] == 'CN') | (summary_df['Country'] == 'HK')) & 
    (summary_df['Prob%'] >= 60.0) & 
    (summary_df['RR_Ratio'] >= {china_rrr}) &
    (summary_df['Count'] >= 20)
].sort_values(by='Prob%', ascending=False)
print_market_section(china_trend, "[CHINA & HK MARKET]", "Prob >= 60% | RRR >= {china_rrr} | Count >= 20")

# TAIWAN MARKET
tw_trend = summary_df[
    (summary_df['Country'] == 'TW') & 
    (summary_df['Prob%'] >= 60.0) & 
    (summary_df['RR_Ratio'] >= {tw_rrr}) &
    (summary_df['Count'] >= 25) &
    (summary_df['Count'] <= 150)
].sort_values(by='Prob%', ascending=False)
print_market_section(tw_trend, "[TAIWAN MARKET]", "Prob >= 60% | RRR >= {tw_rrr} | Count 25-150")

# METALS
metals = summary_df[
    (summary_df['Country'] == 'GL') & 
    (summary_df['Prob%'] >= 60.0) &
    (summary_df['RR_Ratio'] >= {metals_rrr})
].sort_values(by='Prob%', ascending=False)
print_market_section(metals, "[METALS]", "Prob >= 60% | RRR >= {metals_rrr}")
    """.format(
        thai_rrr=recommendations.get('TH', {}).get('rrr', 1.5),
        us_rrr=recommendations.get('US', {}).get('rrr', 1.5),
        china_rrr=recommendations.get('CN', {}).get('rrr', 1.5),
        tw_rrr=recommendations.get('TW', {}).get('rrr', 1.3),
        metals_rrr=recommendations.get('GL', {}).get('rrr', 1.5)
    ))
    print("=" * 160)

if __name__ == "__main__":
    optimize_criteria_by_country()

