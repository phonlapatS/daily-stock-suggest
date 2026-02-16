#!/usr/bin/env python
"""
Verify China Raw Prob% - ตรวจสอบว่า Prob% ที่แสดงเป็น Raw Prob% จริงหรือไม่
และวิเคราะห์ว่าทำไม Prob% ถึงสูงขนาดนี้
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def verify_raw_prob():
    """ตรวจสอบ Raw Prob% ของ China stocks"""
    
    print("="*100)
    print("Verify China Raw Prob% - ตรวจสอบว่า Prob% ที่แสดงเป็น Raw Prob% จริงหรือไม่")
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
    
    # Load symbol performance
    perf_file = 'data/symbol_performance.csv'
    if not os.path.exists(perf_file):
        print(f"❌ File not found: {perf_file}")
        return
    
    perf_df = pd.read_csv(perf_file)
    china_perf = perf_df[((perf_df['Country'] == 'CN') | (perf_df['Country'] == 'HK')) & 
                         (perf_df['Prob%'] >= 50.0) & 
                         (perf_df['RR_Ratio'] >= 1.0) & 
                         (perf_df['Count'] >= 20)]
    
    if china_perf.empty:
        print("❌ No China/HK stocks found in symbol_performance.csv")
        return
    
    print("="*100)
    print("Comparison: Displayed Prob% vs Actual Raw Prob%")
    print("="*100)
    print(f"{'Symbol':<12} {'Displayed Prob%':<18} {'Raw Prob%':<15} {'Elite Prob%':<15} {'Raw Count':<12} {'Elite Count':<12} {'Difference':<12}")
    print("-" * 100)
    
    for _, row in china_perf.iterrows():
        symbol = str(row['symbol'])
        
        # Get trades for this symbol
        symbol_trades = df[df['symbol'].astype(str) == symbol].copy()
        
        if symbol_trades.empty:
            continue
        
        # Convert to numeric
        symbol_trades['correct'] = pd.to_numeric(symbol_trades['correct'], errors='coerce').fillna(0)
        symbol_trades['prob'] = pd.to_numeric(symbol_trades['prob'], errors='coerce').fillna(0)
        
        # Calculate Raw Prob%
        raw_count = len(symbol_trades)
        raw_wins = int(symbol_trades['correct'].sum())
        raw_prob = (raw_wins / raw_count * 100) if raw_count > 0 else 0
        
        # Calculate Elite Prob%
        elite_trades = symbol_trades[symbol_trades['prob'] >= 60.0].copy()
        elite_count = len(elite_trades)
        if elite_count > 0:
            elite_wins = int(elite_trades['correct'].sum())
            elite_prob = (elite_wins / elite_count * 100) if elite_count > 0 else 0
        else:
            elite_prob = 0
        
        # Displayed Prob% (from calculate_metrics)
        displayed_prob = row['Prob%']
        
        # Check if displayed Prob% matches Raw Prob%
        diff = abs(displayed_prob - raw_prob)
        match = "✅" if diff < 1.0 else "❌"
        
        print(f"{symbol:<12} {displayed_prob:<18.1f} {raw_prob:<15.1f} {elite_prob:<15.1f} {raw_count:<12} {elite_count:<12} {diff:<12.1f} {match}")
    
    print()
    print("="*100)
    print("Analysis: ทำไม Prob% ถึงสูงขนาดนี้?")
    print("="*100)
    print()
    
    # Analyze overall market
    df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
    
    total_trades = len(df)
    total_wins = int(df['correct'].sum())
    overall_raw_prob = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"📊 Overall Market Stats:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Total Wins: {total_wins}")
    print(f"   Overall Raw Prob%: {overall_raw_prob:.1f}%")
    print()
    
    # Check if gatekeeper is working
    print(f"🔍 Gatekeeper Analysis:")
    print(f"   Min Prob (Gatekeeper): 51.0% (V13.7)")
    print(f"   Trades with Historical Prob >= 51.0%: {len(df[df['prob'] >= 51.0])}")
    print(f"   Percentage: {len(df[df['prob'] >= 51.0]) / total_trades * 100:.1f}%")
    print()
    
    # Check if there's still selection bias
    elite_trades_all = df[df['prob'] >= 60.0].copy()
    if len(elite_trades_all) > 0:
        elite_wins_all = int(elite_trades_all['correct'].sum())
        elite_prob_all = (elite_wins_all / len(elite_trades_all) * 100) if len(elite_trades_all) > 0 else 0
        print(f"   Elite Trades (Prob >= 60%): {len(elite_trades_all)} ({len(elite_trades_all)/total_trades*100:.1f}%)")
        print(f"   Elite Win Rate: {elite_prob_all:.1f}%")
        print(f"   ⚠️  ถ้า Elite Win Rate สูงกว่า Raw Prob% มาก → ยังมี selection bias")
    print()
    
    # Recommendation
    print("="*100)
    print("💡 Recommendation:")
    print("="*100)
    print()
    
    if overall_raw_prob > 70:
        print(f"⚠️  Overall Raw Prob% ({overall_raw_prob:.1f}%) ยังสูงเกินไป")
        print(f"   → อาจจะต้อง:")
        print(f"      1. เพิ่ม min_prob ใน gatekeeper (51.0% → 52.0% หรือ 53.0%)")
        print(f"      2. เพิ่ม Prob% threshold ใน display criteria (50% → 55% หรือ 60%)")
        print(f"      3. ตรวจสอบว่า gatekeeper ทำงานถูกต้องหรือไม่")
    else:
        print(f"✅ Overall Raw Prob% ({overall_raw_prob:.1f}%) อยู่ในระดับที่เหมาะสม")
        print(f"   → แต่ Prob% ของแต่ละหุ้นอาจจะสูงเพราะ:")
        print(f"      1. หุ้นที่ผ่านเกณฑ์แล้ว (Prob% >= 50%, RRR >= 1.0, Count >= 20)")
        print(f"      2. Selection bias จาก gatekeeper (min_prob 51.0%)")
        print(f"      3. อาจจะต้องเพิ่ม Prob% threshold ใน display criteria")

if __name__ == "__main__":
    verify_raw_prob()

