#!/usr/bin/env python
"""
Analyze Elite Prob% Reliability for China Stocks
ตรวจสอบว่า Elite Prob% (91.7%, 82.7%) น่าเชื่อถือหรือไม่
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_elite_reliability():
    """วิเคราะห์ความน่าเชื่อถือของ Elite Prob%"""
    
    print("="*100)
    print("Elite Prob% Reliability Analysis - China Market")
    print("="*100)
    print()
    
    # Load trade history
    trade_file = 'logs/trade_history_CHINA.csv'
    if not os.path.exists(trade_file):
        print(f"❌ File not found: {trade_file}")
        return
    
    df = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    print(f"✅ Loaded {len(df)} trades from {trade_file}")
    print()
    
    # Focus on XIAOMI (1810) and MEITUAN (3690)
    # Note: Check actual symbols in the file
    print(f"Available symbols: {df['symbol'].unique()[:20]}")
    print()
    
    symbols_to_check = ['1810', '3690']
    
    for symbol in symbols_to_check:
        # Handle both string and numeric symbol types
        symbol_trades = df[df['symbol'].astype(str) == str(symbol)].copy()
        
        if symbol_trades.empty:
            print(f"⚠️ No trades found for {symbol}")
            continue
        
        print("="*100)
        print(f"Analysis: {symbol}")
        print("="*100)
        
        # Convert to numeric
        symbol_trades['prob'] = pd.to_numeric(symbol_trades['prob'], errors='coerce').fillna(0)
        symbol_trades['correct'] = pd.to_numeric(symbol_trades['correct'], errors='coerce').fillna(0)
        
        # Raw metrics
        raw_count = len(symbol_trades)
        raw_correct = int(symbol_trades['correct'].sum())
        raw_prob = (raw_correct / raw_count * 100) if raw_count > 0 else 0
        
        # Elite metrics (Prob >= 60%)
        elite_trades = symbol_trades[symbol_trades['prob'] >= 60.0].copy()
        elite_count = len(elite_trades)
        
        if elite_count > 0:
            elite_correct = int(elite_trades['correct'].sum())
            elite_prob = (elite_correct / elite_count * 100) if elite_count > 0 else 0
            elite_avg_prob = elite_trades['prob'].mean()
        else:
            elite_correct = 0
            elite_prob = 0
            elite_avg_prob = 0
        
        print(f"\n📊 Raw Metrics:")
        print(f"   Total Trades: {raw_count}")
        print(f"   Wins: {raw_correct}")
        print(f"   Raw Prob%: {raw_prob:.1f}%")
        print(f"   Avg Historical Prob%: {symbol_trades['prob'].mean():.1f}%")
        
        print(f"\n⭐ Elite Metrics (Historical Prob >= 60%):")
        print(f"   Elite Count: {elite_count} ({elite_count/raw_count*100:.1f}% of total)")
        print(f"   Elite Wins: {elite_correct}")
        print(f"   Elite Prob% (Win Rate): {elite_prob:.1f}%")
        print(f"   Avg Historical Prob% (Elite): {elite_avg_prob:.1f}%")
        
        # Reliability Assessment
        print(f"\n🔍 Reliability Assessment:")
        
        # 1. Count Check
        if elite_count < 30:
            print(f"   ⚠️ Elite Count = {elite_count} (< 30) - Low statistical reliability")
        elif elite_count < 50:
            print(f"   ⚠️ Elite Count = {elite_count} (30-50) - Moderate reliability")
        else:
            print(f"   ✅ Elite Count = {elite_count} (>= 50) - Good reliability")
        
        # 2. Consistency Check
        diff = abs(elite_prob - raw_prob)
        if diff > 20:
            print(f"   ⚠️ Elite Prob% ({elite_prob:.1f}%) vs Raw Prob% ({raw_prob:.1f}%) = {diff:.1f}% difference")
            print(f"      → Elite Prob% อาจสูงเกินจริง (overfitting risk)")
        elif diff > 10:
            print(f"   ⚠️ Elite Prob% ({elite_prob:.1f}%) vs Raw Prob% ({raw_prob:.1f}%) = {diff:.1f}% difference")
            print(f"      → Elite Prob% สูงกว่า Raw Prob% ค่อนข้างมาก")
        else:
            print(f"   ✅ Elite Prob% ({elite_prob:.1f}%) vs Raw Prob% ({raw_prob:.1f}%) = {diff:.1f}% difference")
            print(f"      → Elite Prob% สอดคล้องกับ Raw Prob%")
        
        # 3. Historical Prob vs Actual Win Rate (Elite)
        if elite_count > 0:
            hist_vs_actual_diff = abs(elite_avg_prob - elite_prob)
            if hist_vs_actual_diff > 15:
                print(f"   ⚠️ Historical Prob% ({elite_avg_prob:.1f}%) vs Actual Win Rate ({elite_prob:.1f}%) = {hist_vs_actual_diff:.1f}% difference")
                print(f"      → Pattern matching อาจไม่แม่นสำหรับ Elite Trades")
            elif hist_vs_actual_diff > 10:
                print(f"   ⚠️ Historical Prob% ({elite_avg_prob:.1f}%) vs Actual Win Rate ({elite_prob:.1f}%) = {hist_vs_actual_diff:.1f}% difference")
                print(f"      → Pattern matching ค่อนข้างแม่น")
            else:
                print(f"   ✅ Historical Prob% ({elite_avg_prob:.1f}%) vs Actual Win Rate ({elite_prob:.1f}%) = {hist_vs_actual_diff:.1f}% difference")
                print(f"      → Pattern matching แม่นมาก")
        
        # 4. Sample Size Check
        if elite_count < 30:
            print(f"\n⚠️ Warning: Elite Count = {elite_count} (< 30)")
            print(f"   → Prob% {elite_prob:.1f}% อาจไม่น่าเชื่อถือ (sample size น้อย)")
            print(f"   → ควรใช้ Raw Prob% ({raw_prob:.1f}%) แทน")
        elif elite_count < 50:
            print(f"\n⚠️ Caution: Elite Count = {elite_count} (30-50)")
            print(f"   → Prob% {elite_prob:.1f}% มีความน่าเชื่อถือปานกลาง")
            print(f"   → ควรระวัง overfitting")
        else:
            print(f"\n✅ Good: Elite Count = {elite_count} (>= 50)")
            print(f"   → Prob% {elite_prob:.1f}% น่าเชื่อถือ")
        
        # 5. Distribution Check
        if elite_count > 0:
            prob_distribution = elite_trades['prob'].describe()
            print(f"\n📈 Elite Historical Prob% Distribution:")
            print(f"   Min: {prob_distribution['min']:.1f}%")
            print(f"   Max: {prob_distribution['max']:.1f}%")
            print(f"   Mean: {prob_distribution['mean']:.1f}%")
            print(f"   Median: {prob_distribution['50%']:.1f}%")
            
            # Check if most trades are at the high end
            high_prob_trades = elite_trades[elite_trades['prob'] >= 80.0]
            if len(high_prob_trades) / elite_count > 0.5:
                print(f"   ⚠️ {len(high_prob_trades)}/{elite_count} ({len(high_prob_trades)/elite_count*100:.1f}%) มี Prob >= 80%")
                print(f"      → Elite Prob% อาจสูงเกินจริง (overfitting)")
        
        print()
    
    print("="*100)
    print("Summary:")
    print("="*100)
    print("""
Elite Prob% คือ Win Rate ของ Elite Trades (trades ที่มี Historical Prob >= 60%)

⚠️ ข้อควรระวัง:
1. Elite Count น้อย (< 30) → Prob% อาจไม่น่าเชื่อถือ
2. Elite Prob% สูงกว่า Raw Prob% มาก (> 20%) → อาจ overfitting
3. Historical Prob% ไม่สอดคล้องกับ Actual Win Rate → Pattern matching อาจไม่แม่น

✅ ข้อดี:
- Elite Prob% สะท้อน Win Rate ของ trades ที่มี Historical Prob สูง
- ถ้า Elite Count >= 50 และสอดคล้องกับ Raw Prob% → น่าเชื่อถือ
    """)

if __name__ == "__main__":
    analyze_elite_reliability()

