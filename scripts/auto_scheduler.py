#!/usr/bin/env python
"""
scripts/auto_scheduler.py
=========================
Auto-scheduler สำหรับรันระบบทำนายอัตโนมัติตามเวลาตลาดปิด

Schedule:
- 17:00 ICT: ตลาดเอเชีย (ไทย, จีน, ฮ่องกง, ไต้หวัน)
- 05:00 ICT: ตลาด US

Usage:
    python scripts/auto_scheduler.py
"""

import schedule
import time
import os
import sys
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_asia_markets():
    """รันตลาดเอเชียหลังปิด (17:00 ICT)"""
    print("\n" + "="*80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌏 Running Asia Markets")
    print("="*80)
    print("Markets: Thailand (SET), China, Hong Kong, Taiwan")
    print("-"*80)
    
    os.chdir(PROJECT_ROOT)
    
    # รันตลาดเอเชียทั้งหมด (รันแยกกัน 3 ครั้ง)
    # GROUP_A_THAI = ไทย
    print("\n🇹🇭 Running Thailand (SET)...")
    os.system("python scripts/run_market_groups.py GROUP_A_THAI")
    
    # GROUP_C_CHINA_HK = จีน + ฮ่องกง
    print("\n🇨🇳🇭🇰 Running China & Hong Kong...")
    os.system("python scripts/run_market_groups.py GROUP_C_CHINA_HK")
    
    # GROUP_D_TAIWAN = ไต้หวัน
    print("\n🇹🇼 Running Taiwan...")
    os.system("python scripts/run_market_groups.py GROUP_D_TAIWAN")
    
    print("\n" + "="*80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Asia Markets Scan Complete")
    print("="*80 + "\n")

def run_us_market():
    """รัน US market หลังปิด (05:00 ICT)"""
    print("\n" + "="*80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🇺🇸 Running US Market")
    print("="*80)
    print("Market: NASDAQ/NYSE")
    print("-"*80)
    
    os.chdir(PROJECT_ROOT)
    os.system("python scripts/run_market_groups.py GROUP_B_US")
    
    print("\n" + "="*80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ US Market Scan Complete")
    print("="*80 + "\n")

def main():
    print("="*80)
    print("🕐 AUTO-SCHEDULER STARTED")
    print("="*80)
    print("\nSchedule:")
    print("  📅 17:00 ICT - Asia Markets (Thailand, China, Hong Kong, Taiwan)")
    print("  📅 05:00 ICT - US Market (NASDAQ/NYSE)")
    print("\nWaiting for scheduled times...")
    print("(Press Ctrl+C to stop)")
    print("="*80 + "\n")
    
    # Schedule tasks
    schedule.every().day.at("17:00").do(run_asia_markets)  # เอเชีย
    schedule.every().day.at("05:00").do(run_us_market)     # US
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Auto-scheduler stopped by user")
        print("="*80)

if __name__ == "__main__":
    main()

