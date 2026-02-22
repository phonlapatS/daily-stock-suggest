#!/usr/bin/env python
"""
scripts/cleanup_duplicate_forecasts.py
======================================
ลบข้อมูลซ้ำใน performance_log.csv

Usage:
    python scripts/cleanup_duplicate_forecasts.py
    python scripts/cleanup_duplicate_forecasts.py --dry-run  # แสดงว่าจะลบอะไรบ้าง แต่ไม่ลบจริง
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.performance import LOG_FILE

def cleanup_duplicates(dry_run=False):
    """ลบข้อมูลซ้ำใน performance_log.csv"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ Log file not found: {LOG_FILE}")
        return
    
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        print("📊 Log file is empty")
        return
    
    original_count = len(df)
    print(f"📊 Original records: {original_count}")
    
    # Deduplicate: เก็บแค่ record ล่าสุดของแต่ละ unique combination
    dedup_cols = ['scan_date', 'symbol', 'pattern', 'forecast', 'target_date']
    
    # Sort by last_update descending to keep the latest record
    df_sorted = df.sort_values('last_update', ascending=False)
    
    # Find duplicates
    duplicates = df_sorted[df_sorted.duplicated(subset=dedup_cols, keep='first')]
    duplicate_count = len(duplicates)
    
    if duplicate_count == 0:
        print("✅ No duplicates found")
        return
    
    print(f"🔍 Found {duplicate_count} duplicate record(s)")
    
    if dry_run:
        print("\n📋 Duplicates to be removed (sample of first 10):")
        print(duplicates[['scan_date', 'symbol', 'pattern', 'forecast', 'target_date', 'last_update']].head(10).to_string())
        print(f"\n⚠️ DRY RUN: Would remove {duplicate_count} duplicate(s), keeping {original_count - duplicate_count} unique record(s)")
        return
    
    # Remove duplicates (keep first = latest due to sorting)
    df_cleaned = df_sorted.drop_duplicates(subset=dedup_cols, keep='first')
    df_cleaned = df_cleaned.sort_index()  # Restore original order if needed
    
    # Save cleaned data
    df_cleaned.to_csv(LOG_FILE, index=False)
    
    final_count = len(df_cleaned)
    removed_count = original_count - final_count
    
    print(f"✅ Removed {removed_count} duplicate record(s)")
    print(f"📊 Final records: {final_count} (was {original_count})")
    print(f"💾 Saved cleaned data to {LOG_FILE}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup duplicate forecasts in performance log')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without actually removing')
    args = parser.parse_args()
    
    print("=" * 80)
    print("🧹 CLEANUP DUPLICATE FORECASTS")
    print("=" * 80)
    
    cleanup_duplicates(dry_run=args.dry_run)
    
    print("\n✅ Cleanup completed.")

if __name__ == "__main__":
    main()

