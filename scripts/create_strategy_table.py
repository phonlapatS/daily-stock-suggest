#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
สร้าง table ระบุกลยุทธ์, การบริหารความเสี่ยง, และเกณฑ์ threshold ของแต่ละประเทศ
"""
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_strategy_table():
    """สร้าง table ระบุกลยุทธ์ของแต่ละประเทศ"""
    
    print("\n" + "=" * 200)
    print("กลยุทธ์, การบริหารความเสี่ยง, และเกณฑ์ Threshold ของแต่ละประเทศ")
    print("=" * 200)
    
    # ข้อมูลแต่ละประเทศ
    markets = [
        {
            'country': 'THAI',
            'strategy': 'Mean Reversion',
            'description': 'Fade the move - ซื้อเมื่อราคาตก, ขายเมื่อราคาขึ้น',
            'threshold_multiplier': '1.0',
            'threshold_floor': '0.7%',
            'min_stats': '25',
            'gatekeeper_prob': '53%',
            'gatekeeper_notes': 'Prob >= 53% + Expectancy > 0',
            'sl_type': 'Fixed',
            'sl_value': '1.5%',
            'tp_type': 'Fixed',
            'tp_value': '3.5%',
            'rrr_theoretical': '2.33',
            'max_hold': '5 days',
            'trailing': 'Activate 1.5%, Distance 50%',
            'position_sizing': 'Risk 2% per trade',
            'slippage': '0.1%',
            'commission': '0.1%',
            'notes': 'เหมาะกับตลาดไทย - Mean Reversion ทำงานได้ดี'
        },
        {
            'country': 'US',
            'strategy': 'Trend Following',
            'description': 'Follow the momentum - ซื้อเมื่อราคาขึ้น, ขายเมื่อราคาตก',
            'threshold_multiplier': '0.9',
            'threshold_floor': '0.6%',
            'min_stats': '20',
            'gatekeeper_prob': '52%',
            'gatekeeper_notes': 'Prob >= 52% + Expectancy > 0 + AvgWin > AvgLoss',
            'sl_type': 'ATR-based',
            'sl_value': '1.0x ATR',
            'tp_type': 'ATR-based',
            'tp_value': '3.5x ATR',
            'rrr_theoretical': '3.5',
            'max_hold': '7 days',
            'trailing': 'Activate 2.0%, Distance 40%',
            'position_sizing': 'Risk 2% per trade',
            'slippage': '0.1%',
            'commission': '0.1%',
            'notes': 'ATR-based TP 3.5x (ปรับจาก 5.0x) + Trailing 2.0% (ปรับจาก 1.5%) - based on actual data'
        },
        {
            'country': 'CHINA/HK',
            'strategy': 'Mean Reversion',
            'description': 'Fade the move - ซื้อเมื่อราคาตก, ขายเมื่อราคาขึ้น',
            'threshold_multiplier': '0.9',
            'threshold_floor': '0.5%',
            'min_stats': '30',
            'gatekeeper_prob': '54%',
            'gatekeeper_notes': 'Prob >= 54% + Expectancy > 0',
            'sl_type': 'ATR-based',
            'sl_value': '1.0x ATR',
            'tp_type': 'ATR-based',
            'tp_value': '3.5x ATR',
            'rrr_theoretical': '3.5',
            'max_hold': '8 days',
            'trailing': 'Activate 2.0%, Distance 40%',
            'position_sizing': 'Risk 2% per trade',
            'slippage': '0.1%',
            'commission': '0.1%',
            'notes': 'ATR-based TP 3.5x (ปรับจาก 5.0x) + Trailing 2.0% (ปรับจาก 1.0%) - based on actual data'
        },
        {
            'country': 'TAIWAN',
            'strategy': 'Trend Following',
            'description': 'Follow the momentum - ซื้อเมื่อราคาขึ้น, ขายเมื่อราคาตก',
            'threshold_multiplier': '0.9',
            'threshold_floor': '0.5%',
            'min_stats': '25',
            'gatekeeper_prob': '51%',
            'gatekeeper_notes': 'Prob >= 51% + Expectancy > 0',
            'sl_type': 'ATR-based',
            'sl_value': '1.0x ATR',
            'tp_type': 'ATR-based',
            'tp_value': '3.5x ATR',
            'rrr_theoretical': '3.5',
            'max_hold': '10 days',
            'trailing': 'Activate 2.0%, Distance 40%',
            'position_sizing': 'Risk 2% per trade',
            'slippage': '0.1%',
            'commission': '0.44%',
            'notes': 'ATR-based TP 3.5x (ปรับจาก 6.5x) + Trailing 2.0% (ปรับจาก 1.0%) - based on actual data'
        },
        {
            'country': 'METALS',
            'strategy': 'Mean Reversion',
            'description': 'Fade the move - ซื้อเมื่อราคาตก, ขายเมื่อราคาขึ้น',
            'threshold_multiplier': '0.9',
            'threshold_floor': '0.3%',
            'min_stats': '25',
            'gatekeeper_prob': '50%',
            'gatekeeper_notes': 'Prob >= 50% + Expectancy > 0',
            'sl_type': 'Fixed',
            'sl_value': '1.5%',
            'tp_type': 'Fixed',
            'tp_value': '3.5%',
            'rrr_theoretical': '2.33',
            'max_hold': '5 days',
            'trailing': 'Activate 1.5%, Distance 50%',
            'position_sizing': 'Risk 2% per trade',
            'slippage': '0.1%',
            'commission': '0.1%',
            'notes': 'Similar to Thai market'
        }
    ]
    
    # Table 1: Strategy & Threshold
    print("\n" + "=" * 200)
    print("1. กลยุทธ์ (Strategy) และ Threshold")
    print("=" * 200)
    print(f"{'Country':<12} {'Strategy':<20} {'Description':<50} {'Threshold':<15} {'Floor':<10} {'Min Stats':<12} {'Gatekeeper':<20}")
    print("-" * 200)
    
    for m in markets:
        threshold_str = f"{m['threshold_multiplier']}x SD"
        print(f"{m['country']:<12} {m['strategy']:<20} {m['description']:<50} {threshold_str:<15} {m['threshold_floor']:<10} {m['min_stats']:<12} {m['gatekeeper_prob']:<20}")
    
    # Table 2: Risk Management
    print("\n" + "=" * 200)
    print("2. การบริหารความเสี่ยง (Risk Management)")
    print("=" * 200)
    print(f"{'Country':<12} {'SL Type':<15} {'SL Value':<15} {'TP Type':<15} {'TP Value':<15} {'RRR':<10} {'Max Hold':<12} {'Trailing':<30}")
    print("-" * 200)
    
    for m in markets:
        print(f"{m['country']:<12} {m['sl_type']:<15} {m['sl_value']:<15} {m['tp_type']:<15} {m['tp_value']:<15} {m['rrr_theoretical']:<10} {m['max_hold']:<12} {m['trailing']:<30}")
    
    # Table 3: Production Settings
    print("\n" + "=" * 200)
    print("3. Production Settings (สำหรับการเทรดจริง)")
    print("=" * 200)
    print(f"{'Country':<12} {'Position Size':<20} {'Slippage':<12} {'Commission':<15} {'Notes':<80}")
    print("-" * 200)
    
    for m in markets:
        print(f"{m['country']:<12} {m['position_sizing']:<20} {m['slippage']:<12} {m['commission']:<15} {m['notes']:<80}")
    
    # Table 4: Summary
    print("\n" + "=" * 200)
    print("4. สรุปเปรียบเทียบ")
    print("=" * 200)
    
    print("\n📊 กลยุทธ์:")
    print("  - Mean Reversion: THAI, CHINA/HK, METALS")
    print("  - Trend Following: US, TAIWAN")
    
    print("\n📊 Risk Management:")
    print("  - Fixed SL/TP: THAI, METALS")
    print("  - ATR-based SL/TP: US, CHINA/HK, TAIWAN (ยืดหยุ่นตาม volatility)")
    
    print("\n📊 Gatekeeper:")
    print("  - THAI: Prob >= 53% (ต่ำสุด - เพิ่มสัญญาณ)")
    print("  - TAIWAN: Prob >= 51% (ต่ำสุด - เพิ่มสัญญาณ)")
    print("  - US: Prob >= 52% + Quality Filter (AvgWin > AvgLoss)")
    print("  - CHINA/HK: Prob >= 54% (สูงสุด - คุณภาพสูง)")
    print("  - METALS: Prob >= 50% (ต่ำสุด)")
    
    print("\n📊 RRR Theoretical (ปรับตามความเป็นจริง):")
    print("  - US/CHINA/TAIWAN: 3.5 (ปรับจาก 5.0-6.5 → 3.5 - ให้ถึง TP ได้มากขึ้น)")
    print("  - THAI/METALS: 2.33 (ปานกลาง)")
    
    print("\n" + "=" * 200)
    print("หมายเหตุ:")
    print("=" * 200)
    print("""
1. ATR-based SL/TP:
   - ยืดหยุ่นตาม volatility ของแต่ละหุ้น
   - หุ้นผันผวนมาก → SL/TP กว้าง
   - หุ้นผันผวนน้อย → SL/TP แคบ
   - เหมาะกับการเทรดจริง (auto system)

2. Fixed SL/TP:
   - Lock ไว้ที่ค่าเดียว
   - ง่ายต่อการเข้าใจ
   - แต่ไม่ยืดหยุ่นตาม volatility

3. Gatekeeper:
   - กรอง trades ก่อนบันทึก
   - Prob% = Historical Probability (ความน่าจะเป็นที่ pattern จะชนะ)
   - Expectancy > 0 = ต้องเป็น +EV (Expected Value บวก)

4. Trailing Stop:
   - Lock กำไรเมื่อราคาเคลื่อนไหวในทิศทางที่ถูกต้อง
   - Activate = เริ่ม trailing เมื่อกำไรถึง X%
   - Distance = Trail ที่ X% ของ peak profit
    """)
    print("=" * 200)

if __name__ == "__main__":
    create_strategy_table()

