#!/usr/bin/env python
"""
scripts/check_forward_testing.py
================================
Forward Testing Checker - ตรวจการบ้าน

Usage:
    python scripts/check_forward_testing.py
    python scripts/check_forward_testing.py --verify
    python scripts/check_forward_testing.py --days 30
"""

import sys
import os
from datetime import datetime, timedelta

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from core.performance import verify_forecast, get_accuracy, LOG_FILE
from tvDatafeed import TvDatafeed

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def show_pending_forecasts():
    """แสดง forecasts ที่ยัง PENDING (ทุกตัว ไม่ว่าจะ target_date อะไร)"""
    if not os.path.exists(LOG_FILE):
        print("❌ No performance log found. Run main.py first to generate forecasts.")
        return
    
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        print("📊 No forecasts in log file.")
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # แสดงทุกตัวที่ PENDING (ไม่ว่าจะ target_date อะไร)
    pending_all = df[df['actual'] == 'PENDING']
    
    if pending_all.empty:
        print("✅ No pending forecasts (all are already verified)")
        return
    
    # แยกเป็น 2 กลุ่ม: ที่ควร verify วันนี้ vs ที่ยังไม่ถึงวัน
    pending_today = pending_all[pending_all['target_date'] <= today]
    pending_future = pending_all[pending_all['target_date'] > today]
    
    print_header(f"📋 ALL PENDING FORECASTS ({len(pending_all)} total)")
    
    # กลุ่มที่ควร verify วันนี้
    if not pending_today.empty:
        print(f"\n🔄 READY TO VERIFY ({len(pending_today)} forecasts) - target_date <= {today}")
        print(f"{'Symbol':<12} {'Exchange':<10} {'Pattern':^10} {'Forecast':<10} {'Prob%':>8} {'Target Date':<12} {'Scan Date':<12} {'Price':>10}")
        print("-" * 90)
        for _, row in pending_today.iterrows():
            print(f"{row['symbol']:<12} {row['exchange']:<10} {row['pattern']:^10} {row['forecast']:<10} {row['prob']:>7.1f}% {row['target_date']:<12} {row['scan_date']:<12} {row['price_at_scan']:>10.2f}")
        print("-" * 90)
    
    # กลุ่มที่ยังไม่ถึงวัน
    if not pending_future.empty:
        print(f"\n⏳ WAITING ({len(pending_future)} forecasts) - target_date > {today}")
        print(f"{'Symbol':<12} {'Exchange':<10} {'Pattern':^10} {'Forecast':<10} {'Prob%':>8} {'Target Date':<12} {'Scan Date':<12} {'Price':>10}")
        print("-" * 90)
        for _, row in pending_future.iterrows():
            print(f"{row['symbol']:<12} {row['exchange']:<10} {row['pattern']:^10} {row['forecast']:<10} {row['prob']:>7.1f}% {row['target_date']:<12} {row['scan_date']:<12} {row['price_at_scan']:>10.2f}")
        print("-" * 90)
    
    if pending_today.empty and pending_future.empty:
        print("✅ No pending forecasts")

def show_verified_summary(days=30):
    """แสดงสรุปผลการ verify"""
    if not os.path.exists(LOG_FILE):
        return
    
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        return
    
    # Filter verified forecasts
    verified = df[df['actual'] != 'PENDING']
    
    if verified.empty:
        print("📊 No verified forecasts yet.")
        return
    
    # Filter by date range
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent = verified[verified['scan_date'] >= cutoff]
    
    if recent.empty:
        print(f"📊 No verified forecasts in the last {days} days.")
        return
    
    total = len(recent)
    correct = recent['correct'].sum()
    incorrect = total - correct
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print_header(f"📊 VERIFICATION SUMMARY (Last {days} days)")
    print(f"Total Verified: {total}")
    print(f"✅ Correct: {correct}")
    print(f"❌ Incorrect: {incorrect}")
    print(f"📈 Accuracy: {accuracy:.1f}%")
    
    # By symbol
    by_symbol = recent.groupby('symbol').agg({
        'correct': ['sum', 'count']
    }).reset_index()
    by_symbol.columns = ['symbol', 'correct', 'total']
    by_symbol['accuracy'] = (by_symbol['correct'] / by_symbol['total'] * 100).round(1)
    by_symbol = by_symbol.sort_values('total', ascending=False).head(10)
    
    if len(by_symbol) > 0:
        print("\n📈 Top 10 Symbols by Forecast Count:")
        print(f"{'Symbol':<12} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
        print("-" * 40)
        for _, row in by_symbol.iterrows():
            print(f"{row['symbol']:<12} {int(row['correct']):>8} {int(row['total']):>8} {row['accuracy']:>9.1f}%")
    
    # By pattern
    by_pattern = recent.groupby('pattern').agg({
        'correct': ['sum', 'count']
    }).reset_index()
    by_pattern.columns = ['pattern', 'correct', 'total']
    by_pattern['accuracy'] = (by_pattern['correct'] / by_pattern['total'] * 100).round(1)
    by_pattern = by_pattern[by_pattern['total'] >= 3].sort_values('accuracy', ascending=False).head(10)
    
    if len(by_pattern) > 0:
        print("\n📊 Top 10 Patterns by Accuracy (min 3 forecasts):")
        print(f"{'Pattern':<12} {'Correct':>8} {'Total':>8} {'Accuracy':>10}")
        print("-" * 40)
        for _, row in by_pattern.iterrows():
            print(f"{row['pattern']:<12} {int(row['correct']):>8} {int(row['total']):>8} {row['accuracy']:>9.1f}%")

def show_all_forecasts_in_log(show_all_verified=False):
    """แสดงทุก forecast ใน log (ทั้ง PENDING และ Verified)"""
    if not os.path.exists(LOG_FILE):
        return
    
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        return
    
    print_header(f"📊 ALL FORECASTS IN LOG ({len(df)} total)")
    
    # Group by status
    pending = df[df['actual'] == 'PENDING']
    verified = df[df['actual'] != 'PENDING']
    
    print(f"\n📋 Summary:")
    print(f"   PENDING: {len(pending)} forecasts")
    print(f"   VERIFIED: {len(verified)} forecasts")
    
    # Show all pending (deduplicated)
    if not pending.empty:
        # Deduplicate pending forecasts
        dedup_cols = ['scan_date', 'symbol', 'pattern', 'forecast', 'target_date']
        pending_dedup = pending.sort_values('last_update', ascending=False).drop_duplicates(
            subset=dedup_cols,
            keep='first'
        )
        
        print(f"\n⏳ PENDING FORECASTS ({len(pending_dedup)} unique, {len(pending)} total):")
        print(f"{'Symbol':<12} {'Exchange':<10} {'Pattern':^10} {'Forecast':<10} {'Prob%':>8} {'Target Date':<12} {'Status':<15}")
        print("-" * 85)
        for _, row in pending_dedup.iterrows():
            today = datetime.now().strftime('%Y-%m-%d')
            status = "🔄 Ready" if row['target_date'] <= today else "⏳ Waiting"
            print(f"{row['symbol']:<12} {row['exchange']:<10} {row['pattern']:^10} {row['forecast']:<10} {row['prob']:>7.1f}% {row['target_date']:<12} {status:<15}")
        print("-" * 85)
        
        # Show duplicate count if any
        duplicate_count = len(pending) - len(pending_dedup)
        if duplicate_count > 0:
            print(f"⚠️ Note: {duplicate_count} duplicate record(s) were filtered out")
    
    # Show recent verified (deduplicated by scan_date, symbol, pattern, forecast, target_date)
    if not verified.empty:
        # Deduplicate: เก็บแค่ record ล่าสุดของแต่ละ unique combination
        dedup_cols = ['scan_date', 'symbol', 'pattern', 'forecast', 'target_date']
        verified_dedup = verified.sort_values('last_update', ascending=False).drop_duplicates(
            subset=dedup_cols, 
            keep='first'
        )
        
        if show_all_verified:
            verified_to_show = verified_dedup.sort_values('last_update', ascending=False)
            title = f"✅ ALL VERIFIED ({len(verified_to_show)} unique forecasts, {len(verified)} total records)"
        else:
            verified_to_show = verified_dedup.sort_values('last_update', ascending=False).head(10)
            title = f"✅ RECENTLY VERIFIED (Last 10 unique of {len(verified_dedup)} unique, {len(verified)} total records)"
        
        print(f"\n{title}:")
        print(f"{'Symbol':<12} {'Exchange':<10} {'Pattern':^10} {'Forecast':<10} {'Actual':<10} {'Correct':<8} {'Target Date':<12} {'Scan Date':<12}")
        print("-" * 95)
        for _, row in verified_to_show.iterrows():
            correct_str = "✅ YES" if row['correct'] == 1 else "❌ NO"
            scan_date = str(row.get('scan_date', ''))[:10]  # First 10 chars (date only)
            print(f"{row['symbol']:<12} {row['exchange']:<10} {row['pattern']:^10} {row['forecast']:<10} {row['actual']:<10} {correct_str:<8} {row['target_date']:<12} {scan_date:<12}")
        print("-" * 95)
        
        # Show duplicate count if any
        duplicate_count = len(verified) - len(verified_dedup)
        if duplicate_count > 0:
            print(f"⚠️ Note: {duplicate_count} duplicate record(s) were filtered out")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Forward Testing Checker')
    parser.add_argument('--verify', action='store_true', help='Verify pending forecasts')
    parser.add_argument('--days', type=int, default=30, help='Days to look back for summary (default: 30)')
    parser.add_argument('--all', action='store_true', help='Show all forecasts in log (both pending and verified)')
    args = parser.parse_args()
    
    print_header("🔍 FORWARD TESTING CHECKER")
    
    # Show all forecasts summary (always show)
    show_all_forecasts_in_log(show_all_verified=args.all)
    
    # Show pending forecasts (detailed)
    show_pending_forecasts()
    
    # Verify if requested
    if args.verify:
        print_header("🔄 VERIFYING PENDING FORECASTS")
        try:
            tv = TvDatafeed()
            result = verify_forecast(tv=tv)
            if result:
                verified = result.get('verified', 0)
                correct = result.get('correct', 0)
                incorrect = result.get('incorrect', 0)
                if verified > 0:
                    accuracy = (correct / verified * 100) if verified > 0 else 0
                    print(f"\n✅ Verified: {verified} forecasts")
                    print(f"✅ Correct: {correct}")
                    print(f"❌ Incorrect: {incorrect}")
                    print(f"📈 Accuracy: {accuracy:.1f}%")
                else:
                    print("ℹ️ No pending forecasts to verify")
        except Exception as e:
            print(f"⚠️ Verification failed: {e}")
    
    # Show summary
    show_verified_summary(days=args.days)
    
    print("\n✅ Forward testing check completed.")

if __name__ == "__main__":
    main()

