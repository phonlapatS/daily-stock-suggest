#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_backtest_results.py - วิเคราะห์ผลลัพธ์ Backtest และแนะนำการปรับปรุง
================================================================================
"""

import pandas as pd
import numpy as np
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_trade_logs(log_file='logs/trade_history.csv'):
    """วิเคราะห์ trade logs และสรุปผลลัพธ์"""
    
    if not os.path.exists(log_file):
        print(f"❌ ไม่พบไฟล์: {log_file}")
        return None
    
    try:
        df = pd.read_csv(log_file)
        # กรองเฉพาะ QUICK_TEST หรือ SINGLE_TEST (ล่าสุด)
        if 'group' in df.columns:
            df = df[df['group'].isin(['QUICK_TEST', 'SINGLE_TEST'])].copy()
    except Exception as e:
        print(f"❌ ไม่สามารถอ่านไฟล์ได้: {e}")
        return None
    
    if df.empty:
        print("❌ ไม่มีข้อมูลในไฟล์")
        return None
    
    print("\n" + "=" * 80)
    print("📊 วิเคราะห์ผลลัพธ์ Backtest")
    print("=" * 80)
    
    # 1. สรุปโดยรวม
    total_trades = len(df)
    if 'correct' in df.columns:
        df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
        correct_trades = int(df['correct'].sum())
    else:
        correct_trades = 0
    accuracy = (correct_trades / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n📈 สรุปโดยรวม:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Correct: {correct_trades}")
    print(f"   Accuracy: {accuracy:.2f}%")
    
    # 2. วิเคราะห์ตาม Symbol
    if 'symbol' in df.columns:
        print(f"\n📊 วิเคราะห์ตาม Symbol:")
        print("-" * 80)
        print(f"{'Symbol':<12} {'Trades':<8} {'Correct':<8} {'Accuracy':<10} {'Avg Win%':<12} {'Avg Loss%':<12} {'RRR':<8}")
        print("-" * 80)
        
        symbol_stats = []
        for symbol in df['symbol'].unique():
            s_df = df[df['symbol'] == symbol].copy()
            s_trades = len(s_df)
            
            if 'correct' in s_df.columns:
                s_df['correct'] = pd.to_numeric(s_df['correct'], errors='coerce').fillna(0)
                s_correct = int(s_df['correct'].sum())
            else:
                s_correct = 0
            s_acc = (s_correct / s_trades * 100) if s_trades > 0 else 0
            
            # คำนวณ Avg Win%, Avg Loss%, RRR
            if 'trader_return' in s_df.columns:
                s_df['trader_return'] = pd.to_numeric(s_df['trader_return'], errors='coerce').fillna(0)
                wins = s_df[s_df['correct'] == 1]['trader_return'].abs()
                losses = s_df[s_df['correct'] == 0]['trader_return'].abs()
            else:
                wins = pd.Series()
                losses = pd.Series()
            
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = losses.mean() if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
            
            symbol_stats.append({
                'symbol': symbol,
                'trades': s_trades,
                'correct': s_correct,
                'accuracy': s_acc,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'rrr': rrr
            })
            
            print(f"{symbol:<12} {s_trades:<8} {s_correct:<8} {s_acc:<10.2f} {avg_win:<12.2f} {avg_loss:<12.2f} {rrr:<8.2f}")
        
        print("-" * 80)
    
    # 3. วิเคราะห์ตาม Pattern
    if 'pattern' in df.columns:
        print(f"\n🔍 วิเคราะห์ตาม Pattern (Top 10):")
        if 'trader_return' in df.columns:
            df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce').fillna(0)
        if 'correct' in df.columns:
            df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
        
        pattern_summary = df.groupby('pattern').agg({
            'correct': ['count', lambda x: int(x.sum())],
        }).round(2)
        pattern_summary.columns = ['Count', 'Correct']
        pattern_summary['Accuracy'] = (pattern_summary['Correct'] / pattern_summary['Count'] * 100).round(2)
        pattern_summary = pattern_summary.sort_values('Count', ascending=False)
        
        if not pattern_summary.empty:
            print(pattern_summary.head(10))
    
    # 4. วิเคราะห์ตาม Prob
    if 'prob' in df.columns:
        print(f"\n📊 วิเคราะห์ตาม Prob:")
        prob_ranges = [
            (0, 55, "0-55%"),
            (55, 60, "55-60%"),
            (60, 65, "60-65%"),
            (65, 70, "65-70%"),
            (70, 100, "70%+")
        ]
        
        print(f"{'Prob Range':<15} {'Trades':<10} {'Accuracy':<12} {'Avg RRR':<12}")
        print("-" * 50)
        
        if 'prob' in df.columns:
            df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
        
        for min_prob, max_prob, label in prob_ranges:
            range_df = df[(df['prob'] >= min_prob) & (df['prob'] < max_prob)].copy()
            if len(range_df) > 0:
                range_trades = len(range_df)
                if 'correct' in range_df.columns:
                    range_df['correct'] = pd.to_numeric(range_df['correct'], errors='coerce').fillna(0)
                    range_correct = int(range_df['correct'].sum())
                else:
                    range_correct = 0
                range_acc = (range_correct / range_trades * 100) if range_trades > 0 else 0
                
                # คำนวณ RRR
                if 'trader_return' in range_df.columns:
                    range_df['trader_return'] = pd.to_numeric(range_df['trader_return'], errors='coerce').fillna(0)
                    wins = range_df[range_df['correct'] == 1]['trader_return'].abs()
                    losses = range_df[range_df['correct'] == 0]['trader_return'].abs()
                else:
                    wins = pd.Series()
                    losses = pd.Series()
                avg_win = wins.mean() if len(wins) > 0 else 0
                avg_loss = losses.mean() if len(losses) > 0 else 0
                rrr = avg_win / avg_loss if avg_loss > 0 else 0
                
                print(f"{label:<15} {range_trades:<10} {range_acc:<12.2f} {rrr:<12.2f}")
    
    return symbol_stats


def suggest_improvements(symbol_stats):
    """แนะนำการปรับปรุงตามผลลัพธ์"""
    
    print("\n" + "=" * 80)
    print("💡 คำแนะนำการปรับปรุง")
    print("=" * 80)
    
    if not symbol_stats:
        print("❌ ไม่มีข้อมูลสำหรับวิเคราะห์")
        return
    
    # วิเคราะห์ปัญหา
    total_trades = sum(s['trades'] for s in symbol_stats)
    avg_accuracy = np.mean([s['accuracy'] for s in symbol_stats])
    avg_rrr = np.mean([s['rrr'] for s in symbol_stats if s['rrr'] > 0])
    
    print(f"\n📊 สถิติปัจจุบัน:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Average Accuracy: {avg_accuracy:.2f}%")
    print(f"   Average RRR: {avg_rrr:.2f}")
    
    # ปัญหาที่พบ
    print(f"\n⚠️  ปัญหาที่พบ:")
    
    if total_trades < 30:
        print(f"   ❌ จำนวน Trades น้อยเกินไป ({total_trades} trades)")
        print(f"      → Filter เข้มเกินไป (Prob >= 60%, RR >= 1.2)")
        print(f"      → แนะนำ: ลด Prob threshold เป็น 55-58% และ RR threshold เป็น 1.0-1.1")
    
    if avg_accuracy < 50:
        print(f"   ❌ Accuracy ต่ำเกินไป ({avg_accuracy:.2f}%)")
        print(f"      → Pattern matching อาจไม่เหมาะสมกับตลาด")
        print(f"      → แนะนำ: ตรวจสอบ threshold และ market floor")
    
    if avg_rrr < 1.0:
        print(f"   ❌ RRR ต่ำเกินไป ({avg_rrr:.2f})")
        print(f"      → Avg Loss สูงกว่า Avg Win")
        print(f"      → แนะนำ: ปรับ stop loss หรือใช้ trailing stop")
    
    # คำแนะนำเฉพาะ
    print(f"\n🎯 คำแนะนำการปรับปรุง:")
    
    print(f"\n1. ปรับ Filter Criteria:")
    print(f"   ปัจจุบัน: Prob >= 60% AND RR >= 1.2 AND Expectancy > 0")
    print(f"   แนะนำ:")
    print(f"   - THAI: Prob >= 58% AND RR >= 1.0 AND AvgWin > 1.0% AND AvgLoss < 2.0%")
    print(f"   - US: Prob >= 52% AND RR >= 1.0 AND AvgWin > 1.0% AND AvgLoss < 3.0%")
    print(f"   - CHINA: Prob >= 55% AND RR >= 1.0 AND AvgWin > 1.0%")
    print(f"   - TAIWAN: Prob >= 52% AND RR >= 1.0 AND AvgWin > 1.0%")
    
    print(f"\n2. ปรับ Threshold:")
    print(f"   - ตรวจสอบ Market Floor: THAI=1.0%, US=0.6%, CHINA=0.5%, TAIWAN=0.5%")
    print(f"   - ลองลด multiplier จาก 1.25 เป็น 1.15-1.20 เพื่อให้ได้ signals มากขึ้น")
    
    print(f"\n3. ปรับ Min Stats:")
    print(f"   ปัจจุบัน: min_stats = 30")
    print(f"   แนะนำ: ลดเป็น 15-20 สำหรับ US/CHINA/TAIWAN")
    
    print(f"\n4. ใช้ Mentor Score:")
    print(f"   Mentor_Score = (Prob% × 0.4) + (RRR × 15) + (AvgWin% × 2) - (AvgLoss% × 2)")
    print(f"   เรียงลำดับตาม Mentor Score แทนการใช้ filter เข้ม")
    
    print(f"\n5. เพิ่มจำนวน Test Bars:")
    print(f"   ปัจจุบัน: 500 bars")
    print(f"   แนะนำ: เพิ่มเป็น 1000 bars เพื่อให้เห็นผลลัพธ์ชัดเจนขึ้น")


def main():
    """Main function"""
    log_file = 'logs/trade_history.csv'
    
    symbol_stats = analyze_trade_logs(log_file)
    suggest_improvements(symbol_stats)
    
    print("\n" + "=" * 80)
    print("✅ การวิเคราะห์เสร็จสิ้น")
    print("=" * 80)


if __name__ == "__main__":
    main()

