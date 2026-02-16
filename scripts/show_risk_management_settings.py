#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
แสดง Risk Management Settings ปัจจุบันของแต่ละประเทศ
"""
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def show_risk_management_settings():
    """แสดง risk management settings สำหรับแต่ละประเทศ"""
    
    print("\n" + "=" * 100)
    print("RISK MANAGEMENT SETTINGS - ปัจจุบัน")
    print("=" * 100)
    
    settings = [
        {
            "country": "[TW] TAIWAN",
            "type": "ATR-based",
            "atr_sl": "1.0x",
            "atr_tp": "6.5x",
            "trail_activate": "1.0%",
            "trail_distance": "40.0%",
            "max_hold": "10 days",
            "note": "ค่าเดิม"
        },
        {
            "country": "[CN] CHINA/HK",
            "type": "ATR-based",
            "atr_sl": "1.0x",
            "atr_tp": "5.0x",
            "trail_activate": "1.0%",
            "trail_distance": "40.0%",
            "max_hold": "3 days",
            "note": "ค่าเดิม"
        },
        {
            "country": "[US] US",
            "type": "ATR-based",
            "atr_sl": "1.0x",
            "atr_tp": "5.0x",
            "trail_activate": "1.5%",
            "trail_distance": "50.0%",
            "max_hold": "5 days",
            "note": "ค่าเดิม"
        },
        {
            "country": "[TH] THAI",
            "type": "Fixed %",
            "stop_loss": "1.5%",
            "take_profit": "3.5%",
            "trail_activate": "1.5%",
            "trail_distance": "50.0%",
            "max_hold": "5 days",
            "note": "ค่าเดิม"
        }
    ]
    
    print(f"\n{'Country':<15} {'Type':<12} {'SL':<10} {'TP':<10} {'Trail Act':<12} {'Trail Dist':<12} {'Max Hold':<12} {'Note':<15}")
    print("-" * 100)
    
    for s in settings:
        if s['type'] == 'ATR-based':
            sl = s['atr_sl']
            tp = s['atr_tp']
        else:
            sl = s['stop_loss']
            tp = s['take_profit']
        
        print(f"{s['country']:<15} {s['type']:<12} {sl:<10} {tp:<10} {s['trail_activate']:<12} {s['trail_distance']:<12} {s['max_hold']:<12} {s['note']:<15}")
    
    print("\n" + "=" * 100)
    print("📝 หมายเหตุ:")
    print("  - ATR-based: SL/TP จะปรับตาม volatility ของแต่ละหุ้น")
    print("  - Fixed %: SL/TP เป็นเปอร์เซ็นต์คงที่")
    print("  - Trail Activate: กำไรต้องถึง % นี้ก่อน trailing stop จะทำงาน")
    print("  - Trail Distance: trailing stop จะอยู่ห่างจาก peak profit % นี้")
    print("  - Max Hold: จำนวนวันสูงสุดที่ถือหุ้น")
    print("=" * 100)
    
    print("\n📋 คำสั่ง Backtest:")
    print("-" * 100)
    print("🇹🇼 TAIWAN:")
    print("  python scripts/backtest.py --full --bars 2500 --group TAIWAN")
    print("\n🇨🇳 CHINA/HK:")
    print("  python scripts/backtest.py --full --bars 2500 --group CHINA")
    print("\n🇺🇸 US:")
    print("  python scripts/backtest.py --full --bars 2500 --group US")
    print("\n🇹🇭 THAI:")
    print("  python scripts/backtest.py --full --bars 2500 --group THAI")
    print("\n🚀 รันทั้งหมด:")
    print("  python scripts/run_backtest_all_markets.py")
    print("=" * 100)

if __name__ == "__main__":
    show_risk_management_settings()

