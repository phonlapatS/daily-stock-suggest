#!/usr/bin/env python
"""
view_scanner.py - Quick CSV Viewer
==================================

ดูข้อมูล market scanner แบบง่ายๆ ใน terminal
"""

import pandas as pd
import sys

def view_latest():
    """ดูไฟล์ล่าสุด"""
    df = pd.read_csv('results/market_scanner.csv')
    
    print("\n" + "="*70)
    print("📊 MARKET SCANNER - Latest Data")
    print("="*70 + "\n")
    
    # แสดงทั้งหมด
    print(df.to_string(index=False))
    
    print(f"\n{'='*70}")
    print(f"Total: {len(df)} stocks")
    print("="*70 + "\n")

def view_top_movers(n=10):
    """ดู top movers"""
    df = pd.read_csv('results/market_scanner.csv')
    
    print("\n" + "="*70)
    print(f"📈 TOP {n} MOVERS (Absolute Change)")
    print("="*70 + "\n")
    
    # คำนวณ absolute change
    df['Abs_Chg'] = df['Chg%'].abs()
    top = df.nlargest(n, 'Abs_Chg')
    
    # แสดง
    cols = ['Symbol', 'Price', 'Chg%', 'Streak_Status']
    print(top[cols].to_string(index=False))
    print()

def view_streaks():
    """ดูเฉพาะ active streaks"""
    df = pd.read_csv('results/market_scanner.csv')
    
    # กรองเฉพาะ streak
    streaks = df[df['Streak'] != 0]
    
    print("\n" + "="*70)
    print(f"🔥 ACTIVE STREAKS ({len(streaks)} stocks)")
    print("="*70 + "\n")
    
    if streaks.empty:
        print("⚪ No active streaks\n")
        return
    
    cols = ['Symbol', 'Price', 'Chg%', 'Streak_Status', 'Win_Rate', 'Events']
    print(streaks[cols].to_string(index=False))
    print()

def compare_history():
    """เปรียบเทียบกับไฟล์เก่า"""
    from pathlib import Path
    
    # หาไฟล์ล่าสุด 2 ไฟล์
    history_dir = Path('results/scanner_history')
    files = sorted(history_dir.glob('scanner_*.csv'))
    
    if len(files) < 2:
        print("\n⚠️ Need at least 2 archive files to compare\n")
        return
    
    # โหลด 2 ไฟล์ล่าสุด
    old = pd.read_csv(files[-2])
    new = pd.read_csv(files[-1])
    
    print("\n" + "="*70)
    print("📊 COMPARISON")
    print("="*70)
    print(f"Old: {files[-2].name}")
    print(f"New: {files[-1].name}\n")
    
    # Merge
    merged = old.merge(new, on='Symbol', suffixes=('_old', '_new'))
    merged['Price_Change'] = merged['Price_new'] - merged['Price_old']
    merged['Pct_Change'] = (merged['Price_Change'] / merged['Price_old']) * 100
    
    # แสดง top gainers
    top_gainers = merged.nlargest(5, 'Pct_Change')
    print("🟢 Top Gainers:")
    for _, row in top_gainers.iterrows():
        print(f"   {row['Symbol']:6s}: {row['Price_old']:.2f} → {row['Price_new']:.2f} ({row['Pct_Change']:+.2f}%)")
    
    # แสดง top losers
    top_losers = merged.nsmallest(5, 'Pct_Change')
    print("\n🔴 Top Losers:")
    for _, row in top_losers.iterrows():
        print(f"   {row['Symbol']:6s}: {row['Price_old']:.2f} → {row['Price_new']:.2f} ({row['Pct_Change']:+.2f}%)")
    
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'top':
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            view_top_movers(n)
        elif cmd == 'streaks':
            view_streaks()
        elif cmd == 'compare':
            compare_history()
        else:
            print("Usage:")
            print("  python scripts/view_scanner.py           # ดูทั้งหมด")
            print("  python scripts/view_scanner.py top [N]   # ดู top N movers")
            print("  python scripts/view_scanner.py streaks   # ดูเฉพาะ streaks")
            print("  python scripts/view_scanner.py compare   # เปรียบเทียบ")
    else:
        view_latest()
