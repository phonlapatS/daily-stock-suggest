#!/usr/bin/env python
"""
filter_signals.py - Smart Signal Filter
=======================================

Purpose: คัดกรองหุ้นจาก Master Scanner เพื่อหา "High Probability Setups"
Filters:
1. Active Streak (Status != Quiet)
2. WinRate > 55% (ชนะมากกว่าแพ้)
3. Events > 10 (มีข้อมูลในอดีตมากพอ)
4. AvgRet > 0.5% (ผลตอบแทนคุ้มค่า)

Author: Stock Analysis System
Date: 2026-01-16
"""

import pandas as pd
import sys
import os

# Add script directory to path to import master_scanner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from master_scanner import categorize_files, analyze_asset
except ImportError:
    print("❌ Error: Cannot import master_scanner.py")
    sys.exit(1)

DATA_DIR = "data/stocks"

def main():
    print("\n" + "="*80)
    print("🔍 SMART SIGNAL FILTER - High Probability Setups")
    print("="*80)
    print("🎯 Filter Criteria:")
    print("   • Active Streak Only")
    print("   • Win Rate > 55%")
    print("   • Events > 10")
    print("   • Avg Return > 0.5%")
    print("="*80)

    # 1. Get all files
    categorized = categorize_files(DATA_DIR)
    
    all_results = []
    
    # 2. Run analysis
    total_files = sum(len(f) for f in categorized.values())
    print(f"\n🔄 Scanning {total_files} stocks...", end="", flush=True)
    
    for timeframe, files in categorized.items():
        for file_info in files:
            result = analyze_asset(
                file_info['filepath'], 
                file_info['symbol'], 
                file_info['exchange'], 
                file_info['timeframe']
            )
            if result:
                all_results.append(result)
                
    print(" Done!")
    
    df = pd.DataFrame(all_results)
    
    if df.empty:
        print("❌ No data found.")
        return

    # 3. Apply Filters
    # Filter 1: Active Streak
    filtered = df[df['Streak'] > 0].copy()
    
    # Filter 2: WinRate > 55%
    filtered = filtered[filtered['WinRate'] > 55]
    
    # Filter 3: Events > 10
    filtered = filtered[filtered['Events'] > 10]
    
    # Filter 4: AvgRet > 0.5%
    filtered = filtered[filtered['AvgRet'] > 0.5]
    
    # Sort by WinRate
    filtered = filtered.sort_values('WinRate', ascending=False)
    
    # 4. Display Results
    if filtered.empty:
        print("\n❌ No stocks matched STRICT criteria today.")
        print("   (WinRate > 55%, Events > 10)")
        
        # ---------------------------------------------------------
        # Show Near Misses (Relaxed Criteria)
        # ---------------------------------------------------------
        relaxed = df[df['Streak'] > 0].copy()
        
        # Criteria: WinRate > 50% OR (WinRate > 45% AND AvgRet > 1.0%)
        # And Events > 5 (less strict sample size)
        mask = ((relaxed['WinRate'] > 50) | ((relaxed['WinRate'] > 45) & (relaxed['AvgRet'] > 1.0)))
        mask = mask & (relaxed['Events'] > 5)
        
        near_misses = relaxed[mask].sort_values('WinRate', ascending=False)
        
        if not near_misses.empty:
            print("\n👀 BUT... Here are some INTERESTING CANDIDATES (Relaxed Criteria):")
            print("   (WinRate > 50% or High Reward, Events > 5)\n")
            
            display = near_misses[['Symbol', 'Price', 'Change%', 'Status', 'WinRate', 'AvgRet', 'Events']].copy()
            display['Price'] = display['Price'].apply(lambda x: f"{x:.2f}")
            display['Change%'] = display['Change%'].apply(lambda x: f"{x:+.2f}%")
            display['WinRate'] = display['WinRate'].apply(lambda x: f"{x:.1f}%")
            display['AvgRet'] = display['AvgRet'].apply(lambda x: f"{x:+.2f}%")
            
            print(display.to_string(index=False))
        else:
            print("\n   No interesting candidates found either.")
            
    else:
        print(f"\n✅ Found {len(filtered)} High Quality Signals!\n")
        
        # Format for display
        display = filtered[['Symbol', 'Price', 'Change%', 'Status', 'WinRate', 'AvgRet', 'Events']].copy()
        display['Price'] = display['Price'].apply(lambda x: f"{x:.2f}")
        display['Change%'] = display['Change%'].apply(lambda x: f"{x:+.2f}%")
        display['WinRate'] = display['WinRate'].apply(lambda x: f"{x:.1f}%")
        display['AvgRet'] = display['AvgRet'].apply(lambda x: f"{x:+.2f}%")
        
        print(display.to_string(index=False))
        
        # Recommendation
        top_pick = filtered.iloc[0]
        print("\n" + "="*80)
        print(f"🏆 TOP PICK: {top_pick['Symbol']}")
        print(f"   WinRate: {top_pick['WinRate']:.1f}% | AvgRet: {top_pick['AvgRet']:+.2f}% | Events: {top_pick['Events']}")
        print("="*80)

if __name__ == "__main__":
    main()
