#!/usr/bin/env python
"""
Analyze China Market RRR Value - วิเคราะห์ว่า RRR คุ้มค่าหรือไม่

เปรียบเทียบ:
1. RRR 1.14 vs Taiwan 1.68
2. Real-world costs (commission, slippage)
3. Expected return after costs
4. Risk assessment
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_rrr_value():
    """Analyze if RRR is worth it"""
    print("="*100)
    print("China Market - RRR Value Analysis")
    print("="*100)
    
    # Data from V13.0
    china_data = {
        'MEITUAN': {'Prob%': 76.9, 'RRR': 1.22, 'Count': 39},
        'BYD': {'Prob%': 59.1, 'RRR': 1.00, 'Count': 159},
        'JD-COM': {'Prob%': 54.2, 'RRR': 1.20, 'Count': 24},
    }
    
    taiwan_data = {
        'DELTA': {'Prob%': 71.4, 'RRR': 1.95, 'Count': 35},
        'QUANTA': {'Prob%': 62.5, 'RRR': 1.41, 'Count': 96},
    }
    
    # Calculate averages
    china_avg_rrr = sum(s['RRR'] for s in china_data.values()) / len(china_data)
    china_avg_prob = sum(s['Prob%'] for s in china_data.values()) / len(china_data)
    
    taiwan_avg_rrr = sum(s['RRR'] for s in taiwan_data.values()) / len(taiwan_data)
    taiwan_avg_prob = sum(s['Prob%'] for s in taiwan_data.values()) / len(taiwan_data)
    
    print(f"\n{'='*100}")
    print("1. RRR Comparison")
    print(f"{'='*100}")
    print(f"\n  China V13.0:")
    print(f"    Avg RRR: {china_avg_rrr:.2f}")
    print(f"    Avg Prob%: {china_avg_prob:.1f}%")
    print(f"    Best RRR: {max(s['RRR'] for s in china_data.values()):.2f} (MEITUAN)")
    print(f"    Worst RRR: {min(s['RRR'] for s in china_data.values()):.2f} (BYD)")
    
    print(f"\n  Taiwan V12.4:")
    print(f"    Avg RRR: {taiwan_avg_rrr:.2f}")
    print(f"    Avg Prob%: {taiwan_avg_prob:.1f}%")
    print(f"    Best RRR: {max(s['RRR'] for s in taiwan_data.values()):.2f} (DELTA)")
    print(f"    Worst RRR: {min(s['RRR'] for s in taiwan_data.values()):.2f} (QUANTA)")
    
    print(f"\n  Difference:")
    print(f"    RRR Gap: {taiwan_avg_rrr - china_avg_rrr:.2f} ({((taiwan_avg_rrr / china_avg_rrr - 1) * 100):.1f}% higher)")
    print(f"    Prob% Gap: {taiwan_avg_prob - china_avg_prob:.1f}%")
    
    # ========================================================================
    # 2. Expected Return Analysis
    # ========================================================================
    print(f"\n{'='*100}")
    print("2. Expected Return Analysis")
    print(f"{'='*100}")
    
    # Assume AvgWin% = RRR × AvgLoss%
    # For China: AvgWin% ≈ 1.8%, AvgLoss% ≈ 1.5% (estimated)
    # For Taiwan: AvgWin% ≈ 2.0%, AvgLoss% ≈ 1.2% (estimated)
    
    china_win_rate = china_avg_prob / 100
    china_avg_win = 1.8  # Estimated
    china_avg_loss = 1.5  # Estimated
    
    taiwan_win_rate = taiwan_avg_prob / 100
    taiwan_avg_win = 2.0  # Estimated
    taiwan_avg_loss = 1.2  # Estimated
    
    # Expected return per trade (before costs)
    china_expectancy = (china_win_rate * china_avg_win) - ((1 - china_win_rate) * china_avg_loss)
    taiwan_expectancy = (taiwan_win_rate * taiwan_avg_win) - ((1 - taiwan_win_rate) * taiwan_avg_loss)
    
    print(f"\n  China V13.0:")
    print(f"    Win Rate: {china_win_rate*100:.1f}%")
    print(f"    Avg Win: ~{china_avg_win:.2f}%")
    print(f"    Avg Loss: ~{china_avg_loss:.2f}%")
    print(f"    Expected Return: {china_expectancy:.2f}% per trade")
    
    print(f"\n  Taiwan V12.4:")
    print(f"    Win Rate: {taiwan_win_rate*100:.1f}%")
    print(f"    Avg Win: ~{taiwan_avg_win:.2f}%")
    print(f"    Avg Loss: ~{taiwan_avg_loss:.2f}%")
    print(f"    Expected Return: {taiwan_expectancy:.2f}% per trade")
    
    print(f"\n  Difference:")
    print(f"    Expectancy Gap: {taiwan_expectancy - china_expectancy:.2f}% per trade")
    
    # ========================================================================
    # 3. Real-World Costs Analysis
    # ========================================================================
    print(f"\n{'='*100}")
    print("3. Real-World Costs Analysis")
    print(f"{'='*100}")
    
    # China/HK commission (estimated)
    china_commission = 0.15  # 0.15% per trade (round trip)
    china_slippage = 0.10   # 0.10% per trade (round trip)
    china_total_cost = china_commission + china_slippage
    
    # Taiwan commission
    taiwan_commission = 0.285  # 0.285% per trade (round trip)
    taiwan_slippage = 0.10     # 0.10% per trade (round trip)
    taiwan_total_cost = taiwan_commission + taiwan_slippage
    
    # Expected return after costs
    china_expectancy_after = china_expectancy - china_total_cost
    taiwan_expectancy_after = taiwan_expectancy - taiwan_total_cost
    
    print(f"\n  China V13.0:")
    print(f"    Commission: {china_commission:.3f}% per trade")
    print(f"    Slippage: {china_slippage:.3f}% per trade")
    print(f"    Total Cost: {china_total_cost:.3f}% per trade")
    print(f"    Expected Return (Before): {china_expectancy:.2f}%")
    print(f"    Expected Return (After): {china_expectancy_after:.2f}%")
    
    print(f"\n  Taiwan V12.4:")
    print(f"    Commission: {taiwan_commission:.3f}% per trade")
    print(f"    Slippage: {taiwan_slippage:.3f}% per trade")
    print(f"    Total Cost: {taiwan_total_cost:.3f}% per trade")
    print(f"    Expected Return (Before): {taiwan_expectancy:.2f}%")
    print(f"    Expected Return (After): {taiwan_expectancy_after:.2f}%")
    
    # ========================================================================
    # 4. Annual Return Analysis
    # ========================================================================
    print(f"\n{'='*100}")
    print("4. Annual Return Analysis")
    print(f"{'='*100}")
    
    china_total_trades = 222
    taiwan_total_trades = 131
    
    china_annual_return = china_expectancy_after * china_total_trades
    taiwan_annual_return = taiwan_expectancy_after * taiwan_total_trades
    
    print(f"\n  China V13.0:")
    print(f"    Total Trades/Year: {china_total_trades}")
    print(f"    Expected Return/Trade: {china_expectancy_after:.2f}%")
    print(f"    Annual Expected Return: {china_annual_return:.2f}%")
    
    print(f"\n  Taiwan V12.4:")
    print(f"    Total Trades/Year: {taiwan_total_trades}")
    print(f"    Expected Return/Trade: {taiwan_expectancy_after:.2f}%")
    print(f"    Annual Expected Return: {taiwan_annual_return:.2f}%")
    
    # ========================================================================
    # 5. Risk Assessment
    # ========================================================================
    print(f"\n{'='*100}")
    print("5. Risk Assessment")
    print(f"{'='*100}")
    
    # Minimum RRR for profitability
    # If Win Rate = 50%, need RRR > 1.0 to break even
    # If Win Rate = 60%, need RRR > 0.67 to break even
    # But with costs, need higher RRR
    
    min_rrr_50 = 1.0 + (china_total_cost / china_avg_loss)
    min_rrr_60 = 0.67 + (china_total_cost / china_avg_loss)
    
    print(f"\n  Minimum RRR Required (with costs):")
    print(f"    Win Rate 50%: RRR >= {min_rrr_50:.2f}")
    print(f"    Win Rate 60%: RRR >= {min_rrr_60:.2f}")
    print(f"    Win Rate {china_win_rate*100:.0f}%: RRR >= {min_rrr_50:.2f} (estimated)")
    
    print(f"\n  Current RRR:")
    print(f"    China Avg RRR: {china_avg_rrr:.2f}")
    print(f"    Status: {'✅ Above minimum' if china_avg_rrr >= min_rrr_50 else '❌ Below minimum'}")
    
    # ========================================================================
    # 6. Assessment
    # ========================================================================
    print(f"\n{'='*100}")
    print("6. Assessment: RRR คุ้มค่าหรือไม่?")
    print(f"{'='*100}")
    
    print(f"\n  China V13.0 RRR = {china_avg_rrr:.2f}:")
    
    if china_avg_rrr < 1.2:
        print(f"    ❌ RRR ต่ำเกินไป (< 1.2)")
        print(f"    ⚠️  ไม่คุ้มค่าสำหรับ real trading")
        print(f"    ⚠️  ต้องปรับ RM parameters เพื่อเพิ่ม RRR")
    elif china_avg_rrr < 1.3:
        print(f"    ⚠️  RRR ต่ำ (1.2-1.3)")
        print(f"    ⚠️  คุ้มค่าแต่ไม่ดีมาก")
        print(f"    💡 ควรปรับ RM parameters เพื่อเพิ่ม RRR")
    elif china_avg_rrr < 1.5:
        print(f"    ✅ RRR ดี (1.3-1.5)")
        print(f"    ✅ คุ้มค่าสำหรับ real trading")
    else:
        print(f"    ✅ ✅ RRR ดีมาก (>= 1.5)")
        print(f"    ✅ ✅ คุ้มค่ามากสำหรับ real trading")
    
    print(f"\n  Comparison with Taiwan:")
    if china_avg_rrr < taiwan_avg_rrr * 0.8:
        print(f"    ❌ RRR ต่ำกว่า Taiwan มาก ({china_avg_rrr:.2f} vs {taiwan_avg_rrr:.2f})")
        print(f"    ❌ ต้องปรับปรุงมาก")
    elif china_avg_rrr < taiwan_avg_rrr:
        print(f"    ⚠️  RRR ต่ำกว่า Taiwan ({china_avg_rrr:.2f} vs {taiwan_avg_rrr:.2f})")
        print(f"    💡 ควรปรับปรุง")
    else:
        print(f"    ✅ RRR ดีกว่า Taiwan ({china_avg_rrr:.2f} vs {taiwan_avg_rrr:.2f})")
    
    print(f"\n  Recommendations:")
    if china_avg_rrr < 1.2:
        print(f"    1. ⚠️  URGENT: ปรับ RM parameters เพื่อเพิ่ม RRR")
        print(f"       - เพิ่ม TP (5.5% → 6.0-6.5%)")
        print(f"       - ลด SL (1.2% → 1.0%)")
        print(f"       - เพิ่ม Max Hold (8 → 10 days)")
        print(f"    2. ทดสอบหลายค่าเพื่อหาค่าที่เหมาะสมที่สุด")
        print(f"    3. เป้าหมาย: RRR >= 1.3-1.5")
    elif china_avg_rrr < 1.3:
        print(f"    1. 💡 ปรับ RM parameters เพื่อเพิ่ม RRR")
        print(f"       - เพิ่ม TP (5.5% → 6.0%)")
        print(f"       - ลด SL (1.2% → 1.0%)")
        print(f"    2. เป้าหมาย: RRR >= 1.3")
    else:
        print(f"    1. ✅ RRR ดีแล้ว")
        print(f"    2. 💡 อาจปรับเพิ่มเล็กน้อยเพื่อให้ดีขึ้น")
    
    return {
        'china_avg_rrr': china_avg_rrr,
        'taiwan_avg_rrr': taiwan_avg_rrr,
        'china_expectancy_after': china_expectancy_after,
        'taiwan_expectancy_after': taiwan_expectancy_after,
        'min_rrr_required': min_rrr_50
    }

if __name__ == '__main__':
    result = analyze_rrr_value()
    
    if result:
        print(f"\n{'='*100}")
        print("Conclusion:")
        print(f"{'='*100}")
        if result['china_avg_rrr'] < 1.2:
            print("  ❌ RRR ไม่คุ้มค่า - ต้องปรับปรุงด่วน")
        elif result['china_avg_rrr'] < 1.3:
            print("  ⚠️  RRR คุ้มค่าแต่ไม่ดีมาก - ควรปรับปรุง")
        else:
            print("  ✅ RRR คุ้มค่า - ดีพอสำหรับ real trading")

