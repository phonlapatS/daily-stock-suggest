#!/usr/bin/env python
"""
view_accuracy.py - Performance Accuracy Report
===============================================
แสดงสรุปความแม่นยำของ forecast

Usage:
    python scripts/view_accuracy.py
    python scripts/view_accuracy.py --days 7
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance import get_accuracy, LOG_FILE
import pandas as pd
from datetime import datetime


def main():
    # Parse arguments
    days = 30
    if len(sys.argv) > 1:
        if sys.argv[1] == '--days' and len(sys.argv) > 2:
            days = int(sys.argv[2])
        elif sys.argv[1].isdigit():
            days = int(sys.argv[1])
    
    print("\n" + "=" * 60)
    print(f"📊 PERFORMANCE REPORT (Last {days} Days)")
    print("=" * 60)
    
    # Get accuracy stats
    stats = get_accuracy(days)
    
    if stats['total'] == 0:
        print("\n⚠️ No verified forecasts found")
        print(f"   Log file: {LOG_FILE}")
        return
    
    # Overall accuracy
    print(f"\n🎯 Overall Accuracy: {stats['accuracy']}%")
    print(f"   Correct: {stats['correct']} / {stats['total']}")
    
    # By symbol (if available)
    if stats.get('by_symbol'):
        print("\n📈 By Symbol:")
        print("-" * 40)
        print(f"{'Symbol':<12} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
        print("-" * 40)
        
        for s in sorted(stats['by_symbol'], key=lambda x: -x['accuracy']):
            print(f"{s['symbol']:<12} {s['correct']:<10} {s['total']:<10} {s['accuracy']:.1f}%")
    
    # Recent forecasts
    print("\n📋 Recent Forecasts:")
    print("-" * 60)
    
    try:
        df = pd.read_csv(LOG_FILE)
        df = df.sort_values('scan_date', ascending=False).head(10)
        
        if not df.empty:
            for _, row in df.iterrows():
                status = "✅" if row['correct'] == 1 else "❌" if row['correct'] == 0 else "⏳"
                print(f"{status} {row['scan_date']} | {row['symbol']:<8} | {row['forecast']:<5} → {row['actual']:<8}")
    except Exception as e:
        print(f"⚠️ Error reading log: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
