#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบหุ้นที่หายไป (ไต้หวัน และหุ้นไทย)
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

def check_missing_stocks():
    """ตรวจสอบหุ้นที่หายไป"""
    if not os.path.exists(METRICS_FILE):
        print(f"❌ ไม่พบไฟล์: {METRICS_FILE}")
        return
    
    df = pd.read_csv(METRICS_FILE)
    
    print("\n" + "=" * 140)
    print("ตรวจสอบหุ้นที่หายไป")
    print("=" * 140)
    
    # ========================================
    # ตรวจสอบหุ้นไต้หวัน
    # ========================================
    print("\n" + "=" * 140)
    print("TAIWAN MARKET - หุ้นทั้งหมดที่มีข้อมูล")
    print("=" * 140)
    
    tw_all = df[df['Country'] == 'TW'].sort_values('Prob%', ascending=False)
    
    if tw_all.empty:
        print("❌ ไม่มีข้อมูลหุ้นไต้หวัน")
    else:
        print(f"\nพบ {len(tw_all)} หุ้น:")
        print(f"{'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'ผ่านเกณฑ์':<15}")
        print("-" * 140)
        
        for _, row in tw_all.iterrows():
            symbol = str(row['symbol'])
            prob = row['Prob%']
            rrr = row['RR_Ratio']
            count = int(row['Count'])
            avg_win = row['AvgWin%']
            avg_loss = row['AvgLoss%']
            
            # ตรวจสอบว่าผ่านเกณฑ์หรือไม่ (Prob >= 60%, RRR >= 1.5, Count >= 25)
            passes = (prob >= 60.0) and (rrr >= 1.5) and (count >= 25) and (count <= 150)
            status = "✅ ผ่าน" if passes else "❌ ไม่ผ่าน"
            
            print(f"{symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}% {status}")
        
        # สรุป
        print("\n" + "-" * 140)
        print("สรุป:")
        passes_prob = tw_all[tw_all['Prob%'] >= 60.0]
        passes_rrr = tw_all[tw_all['RR_Ratio'] >= 1.5]
        passes_count = tw_all[(tw_all['Count'] >= 25) & (tw_all['Count'] <= 150)]
        passes_all = tw_all[
            (tw_all['Prob%'] >= 60.0) & 
            (tw_all['RR_Ratio'] >= 1.5) & 
            (tw_all['Count'] >= 25) & 
            (tw_all['Count'] <= 150)
        ]
        
        print(f"  Prob >= 60%: {len(passes_prob)} หุ้น")
        print(f"  RRR >= 1.5: {len(passes_rrr)} หุ้น")
        print(f"  Count 25-150: {len(passes_count)} หุ้น")
        print(f"  ผ่านเกณฑ์ทั้งหมด: {len(passes_all)} หุ้น")
        
        if len(passes_all) == 0:
            print("\n  ⚠️  ไม่มีหุ้นที่ผ่านเกณฑ์ทั้งหมด")
            print("  หุ้นที่ใกล้เกณฑ์ที่สุด:")
            # หาหุ้นที่ Prob >= 60% แต่ RRR < 1.5
            prob_60 = tw_all[tw_all['Prob%'] >= 60.0].sort_values('RR_Ratio', ascending=False)
            if not prob_60.empty:
                print(f"    - Prob >= 60% แต่ RRR < 1.5:")
                for _, row in prob_60.iterrows():
                    print(f"      {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
            
            # หาหุ้นที่ RRR >= 1.5 แต่ Prob < 60%
            rrr_15 = tw_all[tw_all['RR_Ratio'] >= 1.5].sort_values('Prob%', ascending=False)
            if not rrr_15.empty:
                print(f"    - RRR >= 1.5 แต่ Prob < 60%:")
                for _, row in rrr_15.iterrows():
                    print(f"      {row['symbol']}: Prob {row['Prob%']:.1f}%, RRR {row['RR_Ratio']:.2f}, Count {int(row['Count'])}")
    
    # ========================================
    # ตรวจสอบหุ้นไทยที่หายไป
    # ========================================
    print("\n" + "=" * 140)
    print("THAI MARKET - เปรียบเทียบเกณฑ์เดิม vs เกณฑ์ใหม่")
    print("=" * 140)
    
    th_all = df[df['Country'] == 'TH'].sort_values('Prob%', ascending=False)
    
    if th_all.empty:
        print("❌ ไม่มีข้อมูลหุ้นไทย")
    else:
        # เกณฑ์เดิม: Prob >= 60%, RRR >= 1.2, Count >= 30
        old_criteria = th_all[
            (th_all['Prob%'] >= 60.0) & 
            (th_all['RR_Ratio'] >= 1.2) & 
            (th_all['Count'] >= 30)
        ]
        
        # เกณฑ์ใหม่: Prob >= 60%, RRR >= 1.5, Count >= 30
        new_criteria = th_all[
            (th_all['Prob%'] >= 60.0) & 
            (th_all['RR_Ratio'] >= 1.5) & 
            (th_all['Count'] >= 30)
        ]
        
        print(f"\nเกณฑ์เดิม (Prob >= 60%, RRR >= 1.2, Count >= 30): {len(old_criteria)} หุ้น")
        print(f"เกณฑ์ใหม่ (Prob >= 60%, RRR >= 1.5, Count >= 30): {len(new_criteria)} หุ้น")
        print(f"ลดลง: {len(old_criteria) - len(new_criteria)} หุ้น")
        
        # หุ้นที่หายไป (ผ่านเกณฑ์เดิม แต่ไม่ผ่านเกณฑ์ใหม่)
        missing = old_criteria[~old_criteria.index.isin(new_criteria.index)]
        
        if not missing.empty:
            print(f"\nหุ้นที่หายไป ({len(missing)} หุ้น):")
            print(f"{'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'เหตุผล':<20}")
            print("-" * 140)
            for _, row in missing.iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                count = int(row['Count'])
                avg_win = row['AvgWin%']
                avg_loss = row['AvgLoss%']
                reason = "RRR < 1.5" if rrr < 1.5 else "อื่นๆ"
                print(f"{symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}% {reason}")
        
        # หุ้นที่ยังผ่านเกณฑ์ใหม่
        print(f"\nหุ้นที่ยังผ่านเกณฑ์ใหม่ ({len(new_criteria)} หุ้น):")
        if not new_criteria.empty:
            print(f"{'Symbol':<12} {'Prob%':>8} {'RRR':>8} {'Count':>8} {'AvgWin%':>10} {'AvgLoss%':>10}")
            print("-" * 140)
            for _, row in new_criteria.iterrows():
                symbol = str(row['symbol'])
                prob = row['Prob%']
                rrr = row['RR_Ratio']
                count = int(row['Count'])
                avg_win = row['AvgWin%']
                avg_loss = row['AvgLoss%']
                print(f"{symbol:<12} {prob:>7.1f}% {rrr:>7.2f} {count:>8} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
    
    print("\n" + "=" * 140)

if __name__ == "__main__":
    check_missing_stocks()

