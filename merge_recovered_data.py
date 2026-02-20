#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_recovered_data.py - Merge recovered forecasts into main system
=============================================================
Merges recovered forecast data into main performance log and forecast files
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def merge_performance_logs():
    """Merge recovered performance logs into main performance log"""
    print("🔄 Merging performance logs...")
    
    # Main performance log
    main_log_file = "logs/performance_log.csv"
    recovered_dir = "data/recovered_forecasts"
    
    # Read main log
    if os.path.exists(main_log_file):
        main_df = pd.read_csv(main_log_file)
        print(f"📋 Main log has {len(main_df)} entries")
    else:
        main_df = pd.DataFrame()
        print("📋 Main log not found, creating new one")
    
    # Recovered log files
    recovered_files = [
        f"{recovered_dir}/performance_log_2026-02-12.csv",
        f"{recovered_dir}/performance_log_2026-02-13.csv", 
        f"{recovered_dir}/performance_log_2026-02-16.csv",
        f"{recovered_dir}/performance_log_2026-02-17.csv"
    ]
    
    all_recovered = []
    for file_path in recovered_files:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            all_recovered.append(df)
            print(f"📥 Loaded {len(df)} entries from {os.path.basename(file_path)}")
    
    if all_recovered:
        recovered_df = pd.concat(all_recovered, ignore_index=True)
        print(f"📊 Total recovered entries: {len(recovered_df)}")
        
        # Combine with main log
        combined_df = pd.concat([main_df, recovered_df], ignore_index=True)
        
        # Remove duplicates (same symbol, pattern, target_date)
        combined_df = combined_df.drop_duplicates(
            subset=['symbol', 'pattern', 'target_date'], 
            keep='first'
        )
        
        # Sort by date
        combined_df['scan_date'] = pd.to_datetime(combined_df['scan_date'])
        combined_df = combined_df.sort_values('scan_date')
        
        # Save back to main log
        combined_df.to_csv(main_log_file, index=False)
        print(f"💾 Saved {len(combined_df)} total entries to {main_log_file}")
        
        return len(recovered_df)
    
    return 0

def merge_forecast_files():
    """Merge recovered forecast data into main forecast file"""
    print("\n🔄 Merging forecast files...")
    
    # Main forecast file
    main_forecast_file = "data/forecast_tomorrow.csv"
    recovered_dir = "data/recovered_forecasts"
    
    # Read main forecast
    if os.path.exists(main_forecast_file):
        main_df = pd.read_csv(main_forecast_file)
        print(f"📋 Main forecast has {len(main_df)} entries")
    else:
        main_df = pd.DataFrame()
        print("📋 Main forecast not found, creating new one")
    
    # Recovered forecast files
    recovered_files = [
        f"{recovered_dir}/forecast_2026-02-12.csv",
        f"{recovered_dir}/forecast_2026-02-13.csv",
        f"{recovered_dir}/forecast_2026-02-16.csv", 
        f"{recovered_dir}/forecast_2026-02-17.csv"
    ]
    
    all_recovered = []
    for file_path in recovered_files:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            all_recovered.append(df)
            print(f"📥 Loaded {len(df)} forecasts from {os.path.basename(file_path)}")
    
    if all_recovered:
        recovered_df = pd.concat(all_recovered, ignore_index=True)
        print(f"📊 Total recovered forecasts: {len(recovered_df)}")
        
        # Add scan_date to match main format
        if 'scan_date' in recovered_df.columns:
            recovered_df['scan_date'] = pd.to_datetime(recovered_df['scan_date'])
        
        # Combine with main forecast
        combined_df = pd.concat([main_df, recovered_df], ignore_index=True)
        
        # Remove duplicates
        if 'symbol' in combined_df.columns and 'pattern' in combined_df.columns:
            combined_df = combined_df.drop_duplicates(
                subset=['symbol', 'pattern'], 
                keep='first'
            )
        
        # Save back to main forecast file
        combined_df.to_csv(main_forecast_file, index=False)
        print(f"💾 Saved {len(combined_df)} total forecasts to {main_forecast_file}")
        
        return len(recovered_df)
    
    return 0

def update_stock_stats():
    """Update stock stats files with recovered data"""
    print("\n🔄 Updating stock stats...")
    
    # This would require running the performance calculation again
    print("📊 Running performance calculation to update stats...")
    
    try:
        # Run the performance calculation script
        import subprocess
        result = subprocess.run([sys.executable, "scripts/calculate_performance.py"], 
                           capture_output=True, text=True, cwd=".")
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Warning: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running performance calculation: {e}")

def create_backup():
    """Create backup of current files before merging"""
    print("\n💾 Creating backups...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "logs/performance_log.csv",
        "data/forecast_tomorrow.csv",
        "data/stock_stats_set.csv",
        "data/performance_summary_set.csv"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            backup_path = f"{backup_dir}/{filename}"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"📋 Backed up {file_path} -> {backup_path}")
    
    print(f"✅ Backup created in {backup_dir}")

def main():
    print("🔄 Starting Merge of Recovered Data...")
    print("=" * 50)
    
    # Create backup first
    create_backup()
    
    # Merge performance logs
    performance_count = merge_performance_logs()
    
    # Merge forecast files  
    forecast_count = merge_forecast_files()
    
    # Update stats
    update_stock_stats()
    
    print("\n" + "=" * 50)
    print("✅ Merge Complete!")
    print(f"📊 Merged {performance_count} performance log entries")
    print(f"📊 Merged {forecast_count} forecast entries")
    print("\n🔍 You can now run:")
    print("   python scripts/check_forward_testing.py")
    print("   python scripts/forward_testing_report.py") 
    print("   python scripts/calculate_performance.py")
    print("   to see the updated results")

if __name__ == "__main__":
    main()
