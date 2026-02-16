#!/usr/bin/env python
"""
Test Threshold Multiplier Effect - ทดสอบว่า threshold_multiplier มีผลต่อ Prob% และจำนวน trades อย่างไร
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_threshold_multiplier_effect():
    """วิเคราะห์ว่า threshold_multiplier มีผลต่อ Prob% และจำนวน trades อย่างไร"""
    
    print("="*100)
    print("Test Threshold Multiplier Effect - ทดสอบว่า threshold_multiplier มีผลต่อ Prob% และจำนวน trades อย่างไร")
    print("="*100)
    print()
    
    # Load trade history
    trade_file = 'logs/trade_history_CHINA.csv'
    if not os.path.exists(trade_file):
        print(f"❌ File not found: {trade_file}")
        print("   Please run backtest first to generate trade history")
        return
    
    df = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    print(f"✅ Loaded {len(df)} trades from {trade_file}")
    print()
    
    # Convert to numeric
    df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce').fillna(0)
    
    print("="*100)
    print("What is threshold_multiplier? - threshold_multiplier คืออะไร?")
    print("="*100)
    print()
    print("threshold_multiplier ใช้ในการคำนวณ threshold สำหรับ pattern detection:")
    print()
    print("  threshold = effective_std × threshold_multiplier")
    print()
    print("โดยที่:")
    print("  - effective_std = max(SD_20d, SD_252d, Market_Floor)")
    print("  - threshold_multiplier = ค่าคงที่ (เช่น 0.9, 1.0, 1.25)")
    print()
    print("ผลกระทบ:")
    print("  - threshold_multiplier ต่ำ (เช่น 0.9) → threshold ต่ำ → จับ pattern ได้ง่ายขึ้น → มี trades มากขึ้น")
    print("  - threshold_multiplier สูง (เช่น 1.25) → threshold สูง → จับ pattern ได้ยากขึ้น → มี trades น้อยลง แต่ Prob% อาจสูงขึ้น")
    print()
    
    print("="*100)
    print("Current Settings (V13.9)")
    print("="*100)
    print("  - threshold_multiplier: 0.9 (ต่ำ - จับ pattern ได้ง่าย)")
    print("  - min_stats: 30")
    print("  - min_prob (gatekeeper): 54.0%")
    print()
    
    print("="*100)
    print("Analysis: How threshold_multiplier Affects Pattern Detection")
    print("="*100)
    print()
    
    # Analyze historical prob distribution
    print("Historical Prob% Distribution (Pattern Match Prob%):")
    print("(Prob% นี้มาจาก pattern matching - ถ้า threshold_multiplier สูงขึ้น Prob% อาจสูงขึ้น)")
    print()
    print(f"{'Prob Range':<20} {'Trades':<15} {'Wins':<15} {'Win Rate':<15} {'% of Total':<15}")
    print("-" * 100)
    
    total_trades = len(df)
    prob_ranges = [
        (54, 56, "54-56%"),
        (56, 60, "56-60%"),
        (60, 70, "60-70%"),
        (70, 100, "70-100%")
    ]
    
    for min_p, max_p, label in prob_ranges:
        if max_p == 100:
            filtered = df[(df['prob'] >= min_p) & (df['prob'] <= max_p)]
        else:
            filtered = df[(df['prob'] >= min_p) & (df['prob'] < max_p)]
        
        if len(filtered) > 0:
            wins = int(filtered['correct'].sum())
            win_rate = (wins / len(filtered) * 100) if len(filtered) > 0 else 0
            pct_total = (len(filtered) / total_trades * 100) if total_trades > 0 else 0
            print(f"{label:<20} {len(filtered):<15} {wins:<15} {win_rate:<15.1f} {pct_total:<15.1f}")
    
    print()
    
    # Analyze by symbol
    print("="*100)
    print("By Symbol - Historical Prob% vs Actual Win Rate")
    print("="*100)
    print()
    print("(ถ้า Historical Prob% สูง → threshold_multiplier อาจช่วยกรอง pattern ที่ดี)")
    print()
    
    symbols = df['symbol'].unique()
    symbol_stats = []
    
    for symbol in symbols:
        sym_df = df[df['symbol'] == symbol].copy()
        
        avg_hist_prob = sym_df['prob'].mean()
        min_hist_prob = sym_df['prob'].min()
        max_hist_prob = sym_df['prob'].max()
        
        actual_wins = int(sym_df['correct'].sum())
        actual_prob = (actual_wins / len(sym_df) * 100) if len(sym_df) > 0 else 0
        
        symbol_stats.append({
            'symbol': symbol,
            'trades': len(sym_df),
            'avg_hist_prob': avg_hist_prob,
            'min_hist_prob': min_hist_prob,
            'max_hist_prob': max_hist_prob,
            'actual_prob': actual_prob,
            'diff': actual_prob - avg_hist_prob
        })
    
    # Sort by avg_hist_prob
    symbol_stats.sort(key=lambda x: x['avg_hist_prob'], reverse=True)
    
    print(f"{'Symbol':<12} {'Trades':<15} {'Avg Hist Prob%':<20} {'Min-Max':<20} {'Actual Prob%':<20} {'Diff':<15}")
    print("-" * 100)
    
    for stat in symbol_stats:
        if stat['trades'] >= 20:
            print(f"{stat['symbol']:<12} {stat['trades']:<15} {stat['avg_hist_prob']:<20.1f} {stat['min_hist_prob']:.1f}-{stat['max_hist_prob']:.1f} {'':<10} {stat['actual_prob']:<20.1f} {stat['diff']:<15.1f}")
    
    print()
    
    # Conclusion
    print("="*100)
    print("💡 How threshold_multiplier Helps - threshold_multiplier ช่วยอะไร?")
    print("="*100)
    print()
    
    print("1. ✅ Pattern Detection (จับ Pattern):")
    print("   - threshold_multiplier ต่ำ (0.9) → threshold ต่ำ → จับ pattern ได้ง่ายขึ้น")
    print("   - threshold_multiplier สูง (1.25) → threshold สูง → จับ pattern ได้ยากขึ้น")
    print("   - ผลลัพธ์: threshold_multiplier ต่ำ = มี trades มากขึ้น")
    print()
    
    print("2. ✅ Pattern Quality (คุณภาพ Pattern):")
    print("   - threshold_multiplier สูง → จับเฉพาะ pattern ที่มี price move ใหญ่")
    print("   - threshold_multiplier ต่ำ → จับ pattern ที่มี price move เล็กได้ด้วย")
    print("   - ผลลัพธ์: threshold_multiplier สูง = Prob% อาจสูงขึ้น (แต่ trades น้อยลง)")
    print()
    
    print("3. ✅ Current Situation (สถานการณ์ปัจจุบัน):")
    avg_hist_prob = df['prob'].mean()
    min_hist_prob = df['prob'].min()
    print(f"   - threshold_multiplier = 0.9 (ต่ำ)")
    print(f"   - Historical Prob% Range: {min_hist_prob:.1f}% - {df['prob'].max():.1f}%")
    print(f"   - Avg Historical Prob%: {avg_hist_prob:.1f}%")
    print(f"   - Actual Prob%: {df['correct'].sum() / len(df) * 100:.1f}%")
    print()
    
    if min_hist_prob >= 54.0:
        print("   ⚠️  สังเกต: Historical Prob% ทั้งหมด >= 54%")
        print("   → threshold_multiplier 0.9 จับ pattern ที่มี historical prob สูงอยู่แล้ว")
        print("   → ถ้าเพิ่ม threshold_multiplier เป็น 1.0-1.1 อาจจับ pattern ที่มี historical prob สูงขึ้น")
        print("   → แต่จะทำให้จำนวน trades ลดลง")
    print()
    
    print("4. ✅ Effect on Prob% (ผลกระทบต่อ Prob%):")
    print("   - threshold_multiplier ไม่ได้เปลี่ยน Prob% โดยตรง")
    print("   - แต่เปลี่ยน pattern ที่จับได้ → เปลี่ยน historical prob ของ pattern")
    print("   - ถ้า threshold_multiplier สูงขึ้น → จับ pattern ที่มี historical prob สูงขึ้น → Prob% อาจสูงขึ้น")
    print("   - แต่จะทำให้จำนวน trades ลดลง")
    print()
    
    print("="*100)
    print("🎯 CONCLUSION - สรุป")
    print("="*100)
    print()
    
    print("threshold_multiplier ช่วย:")
    print()
    print("1. ✅ ควบคุมความยากง่ายในการจับ pattern:")
    print("   - ต่ำ (0.9) = จับ pattern ได้ง่าย → trades มากขึ้น")
    print("   - สูง (1.25) = จับ pattern ได้ยาก → trades น้อยลง แต่ Prob% อาจสูงขึ้น")
    print()
    print("2. ✅ กรอง pattern ที่มี price move ใหญ่:")
    print("   - threshold_multiplier สูง = จับเฉพาะ pattern ที่มี price move ใหญ่")
    print("   - อาจทำให้ Prob% สูงขึ้น (เพราะ pattern ที่มี price move ใหญ่อาจมี historical prob สูง)")
    print()
    print("3. ✅ ปัจจุบัน (threshold_multiplier = 0.9):")
    print("   - จับ pattern ได้ง่าย → มี trades มาก (2257 trades)")
    print("   - แต่ historical prob ทั้งหมด >= 54% อยู่แล้ว")
    print("   - ถ้าเพิ่ม threshold_multiplier เป็น 1.0-1.1 อาจจับ pattern ที่มี historical prob สูงขึ้น")
    print("   - แต่จะทำให้จำนวน trades ลดลง")
    print()
    print("💡 ถ้าต้องการลด Prob%:")
    print("   - เพิ่ม threshold_multiplier เป็น 1.0-1.1 (จับ pattern ยากขึ้น)")
    print("   - หรือเพิ่ม min_stats เป็น 35-40 (ต้องมี pattern มากขึ้น)")
    print("   - หรือเพิ่ม min_prob เป็น 55-56% (กรองมากขึ้น)")
    print("   - แต่จะทำให้จำนวนหุ้นลดลง")

if __name__ == "__main__":
    analyze_threshold_multiplier_effect()

