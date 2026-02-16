#!/usr/bin/env python
"""
Analyze China Current Results - วิเคราะห์ผลลัพธ์ปัจจุบัน
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_current_results():
    """วิเคราะห์ผลลัพธ์ปัจจุบัน"""
    
    print("="*100)
    print("Analyze China Current Results - วิเคราะห์ผลลัพธ์ปัจจุบัน")
    print("="*100)
    print()
    
    # Load symbol performance
    perf_file = 'data/symbol_performance.csv'
    if not os.path.exists(perf_file):
        print(f"❌ File not found: {perf_file}")
        return
    
    perf_df = pd.read_csv(perf_file)
    china_perf = perf_df[((perf_df['Country'] == 'CN') | (perf_df['Country'] == 'HK')) & 
                         (perf_df['Prob%'] >= 60.0) & 
                         (perf_df['RR_Ratio'] >= 1.0) & 
                         (perf_df['Count'] >= 20)]
    
    if china_perf.empty:
        print("❌ No China/HK stocks found")
        return
    
    print("="*100)
    print("Current China/HK Stocks (Prob% >= 60%, RRR >= 1.0, Count >= 20)")
    print("="*100)
    print(f"{'Symbol':<12} {'Prob%':<10} {'RRR':<10} {'AvgWin%':<12} {'AvgLoss%':<12} {'Count':<10} {'Status':<20}")
    print("-" * 100)
    
    results = []
    for _, row in china_perf.iterrows():
        symbol = str(row['symbol'])
        prob = row['Prob%']
        rrr = row['RR_Ratio']
        avgwin = row['AvgWin%']
        avgloss = row['AvgLoss%']
        count = row['Count']
        
        # Status
        status = []
        if rrr >= 1.40:
            status.append("✅ RRR OK")
        else:
            status.append("⚠️ RRR Low")
        
        if prob >= 60.0:
            status.append("✅ Prob OK")
        else:
            status.append("⚠️ Prob Low")
        
        if count >= 20:
            status.append("✅ Count OK")
        else:
            status.append("⚠️ Count Low")
        
        status_str = ", ".join(status)
        results.append({
            'symbol': symbol,
            'prob': prob,
            'rrr': rrr,
            'avgwin': avgwin,
            'avgloss': avgloss,
            'count': count,
            'status': status_str
        })
        
        print(f"{symbol:<12} {prob:<10.1f} {rrr:<10.2f} {avgwin:<12.2f} {avgloss:<12.2f} {count:<10.0f} {status_str:<20}")
    
    print()
    print("="*100)
    print("Summary Statistics")
    print("="*100)
    
    if results:
        avg_prob = sum(r['prob'] for r in results) / len(results)
        avg_rrr = sum(r['rrr'] for r in results) / len(results)
        avg_win = sum(r['avgwin'] for r in results) / len(results)
        avg_loss = sum(r['avgloss'] for r in results) / len(results)
        avg_count = sum(r['count'] for r in results) / len(results)
        min_rrr = min(r['rrr'] for r in results)
        max_rrr = max(r['rrr'] for r in results)
        
        print(f"Number of Stocks: {len(results)}")
        print(f"Avg Prob%: {avg_prob:.1f}%")
        print(f"Avg RRR: {avg_rrr:.2f}")
        print(f"Min RRR: {min_rrr:.2f}")
        print(f"Max RRR: {max_rrr:.2f}")
        print(f"Avg Win%: {avg_win:.2f}%")
        print(f"Avg Loss%: {avg_loss:.2f}%")
        print(f"Avg Count: {avg_count:.0f}")
        print()
        
        # Check targets
        print("="*100)
        print("Target Achievement")
        print("="*100)
        
        rrr_ok = sum(1 for r in results if r['rrr'] >= 1.40)
        prob_ok = sum(1 for r in results if r['prob'] >= 60.0)
        count_ok = sum(1 for r in results if r['count'] >= 20)
        
        print(f"✅ RRR >= 1.40: {rrr_ok}/{len(results)} stocks ({rrr_ok/len(results)*100:.1f}%)")
        print(f"✅ Prob% >= 60%: {prob_ok}/{len(results)} stocks ({prob_ok/len(results)*100:.1f}%)")
        print(f"✅ Count >= 20: {count_ok}/{len(results)} stocks ({count_ok/len(results)*100:.1f}%)")
        print()
        
        # Overall assessment
        print("="*100)
        print("Overall Assessment")
        print("="*100)
        
        if avg_rrr >= 1.40 and avg_prob >= 60.0 and len(results) >= 4:
            print("✅ EXCELLENT: All targets achieved!")
            print(f"   - Avg RRR: {avg_rrr:.2f} >= 1.40 ✅")
            print(f"   - Avg Prob%: {avg_prob:.1f}% >= 60% ✅")
            print(f"   - Stocks: {len(results)} >= 4 ✅")
        elif avg_rrr >= 1.30 and avg_prob >= 60.0 and len(results) >= 4:
            print("⚠️ GOOD: Most targets achieved, but RRR could be higher")
            print(f"   - Avg RRR: {avg_rrr:.2f} (target: >= 1.40)")
            print(f"   - Avg Prob%: {avg_prob:.1f}% >= 60% ✅")
            print(f"   - Stocks: {len(results)} >= 4 ✅")
            print()
            print("💡 Recommendation:")
            print("   → ผลลัพธ์นี้มาจาก V13.7/V13.8 (ก่อน V13.9)")
            print("   → ควรรัน backtest ใหม่ด้วย V13.9 settings (min_prob 54.0%, ATR TP 5.0x)")
            print("   → เพื่อให้ RRR >= 1.40 สำหรับทุกหุ้น")
        elif avg_rrr >= 1.20 and avg_prob >= 60.0 and len(results) >= 4:
            print("⚠️ ACCEPTABLE: Basic targets met, but RRR needs improvement")
            print(f"   - Avg RRR: {avg_rrr:.2f} (target: >= 1.40)")
            print(f"   - Avg Prob%: {avg_prob:.1f}% >= 60% ✅")
            print(f"   - Stocks: {len(results)} >= 4 ✅")
            print()
            print("💡 Recommendation:")
            print("   → ผลลัพธ์นี้มาจาก V13.7/V13.8 (ก่อน V13.9)")
            print("   → ควรรัน backtest ใหม่ด้วย V13.9 settings (min_prob 54.0%, ATR TP 5.0x)")
            print("   → เพื่อให้ RRR >= 1.40 สำหรับทุกหุ้น")
        else:
            print("❌ NEEDS IMPROVEMENT: Some targets not met")
            print(f"   - Avg RRR: {avg_rrr:.2f} (target: >= 1.40)")
            print(f"   - Avg Prob%: {avg_prob:.1f}% (target: >= 60%)")
            print(f"   - Stocks: {len(results)} (target: >= 4)")
        
        print()
        print("="*100)
        print("💡 Next Steps")
        print("="*100)
        print()
        print("1. รัน backtest ใหม่ด้วย V13.9 settings:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA")
        print("   python scripts/calculate_metrics.py")
        print()
        print("2. ตรวจสอบผลลัพธ์:")
        print("   - RRR >= 1.40?")
        print("   - Prob% >= 60%?")
        print("   - Count >= 20?")
        print("   - Stocks >= 4?")
        print()
        print("3. ถ้าผลลัพธ์ยังไม่ถึงเป้าหมาย:")
        print("   - เพิ่ม ATR TP เป็น 5.5x (ถ้า RRR ยังไม่ถึง 1.40)")
        print("   - หรือลด min_prob เป็น 53.0% (ถ้าจำนวนหุ้นน้อยเกินไป)")

if __name__ == "__main__":
    analyze_current_results()

