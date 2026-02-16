#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
เปรียบเทียบผลลัพธ์ก่อนและหลังการปรับ TP/Trailing Stop
"""
import pandas as pd
import glob
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def analyze_market_tp_feasibility(file_path, market_name):
    """วิเคราะห์ TP feasibility สำหรับแต่ละ market"""
    try:
        df = pd.read_csv(file_path)
        
        total_trades = len(df)
        if total_trades == 0:
            return None
        
        # ตรวจสอบ exit_reason
        if 'exit_reason' not in df.columns:
            return None
        
        exit_reasons = df['exit_reason'].value_counts()
        
        # หา TP exits
        tp_exits = df[df['exit_reason'].str.contains('TP|TAKE_PROFIT', case=False, na=False)]
        tp_count = len(tp_exits)
        tp_pct = (tp_count / total_trades * 100) if total_trades > 0 else 0
        
        # หา Trailing Stop exits
        trailing_exits = df[df['exit_reason'].str.contains('TRAILING', case=False, na=False)]
        trailing_count = len(trailing_exits)
        trailing_pct = (trailing_count / total_trades * 100) if total_trades > 0 else 0
        
        # หา SL exits
        sl_exits = df[df['exit_reason'].str.contains('STOP_LOSS|SL', case=False, na=False)]
        sl_count = len(sl_exits)
        sl_pct = (sl_count / total_trades * 100) if total_trades > 0 else 0
        
        # คำนวณ RRR
        rrr_actual = 0
        avg_win = 0
        avg_loss = 0
        
        if 'actual_return' in df.columns and 'forecast' in df.columns:
            df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce').fillna(0)
            df['pnl'] = df.apply(
                lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1),
                axis=1
            )
            
            wins = df[df['pnl'] > 0]
            losses = df[df['pnl'] <= 0]
            
            avg_win = wins['pnl'].mean() if not wins.empty else 0
            avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
            rrr_actual = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Theoretical RRR
        if market_name == 'US':
            theoretical_rrr = 5.0  # ค่าเดิม
        elif market_name == 'CHINA':
            theoretical_rrr = 5.0  # ค่าเดิม
        elif market_name == 'TAIWAN':
            theoretical_rrr = 6.5  # ค่าเดิม
        elif market_name == 'THAI':
            theoretical_rrr = 2.33  # ค่าเดิม
        else:
            theoretical_rrr = 0
        
        return {
            'market': market_name,
            'total_trades': total_trades,
            'tp_count': tp_count,
            'tp_pct': tp_pct,
            'trailing_count': trailing_count,
            'trailing_pct': trailing_pct,
            'sl_count': sl_count,
            'sl_pct': sl_pct,
            'rrr_actual': rrr_actual,
            'rrr_theoretical': theoretical_rrr,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'rrr_ratio': (rrr_actual / theoretical_rrr * 100) if theoretical_rrr > 0 else 0
        }
    except Exception as e:
        print(f"  Error analyzing {market_name}: {e}")
        return None

def compare_before_after():
    """เปรียบเทียบผลลัพธ์ก่อนและหลังการปรับ"""
    
    print("\n" + "=" * 160)
    print("เปรียบเทียบผลลัพธ์: ก่อนและหลังการปรับ TP/Trailing Stop")
    print("=" * 160)
    
    # หา trade_history files
    trade_history_files = glob.glob(os.path.join(LOGS_DIR, "trade_history_*.csv"))
    
    markets_config = {
        'US': {'file_key': 'US', 'old_tp': 5.0, 'new_tp': 3.5, 'old_trail': 1.5, 'new_trail': 2.0, 'old_hold': 5, 'new_hold': 7},
        'CHINA': {'file_key': 'CHINA', 'old_tp': 5.0, 'new_tp': 3.5, 'old_trail': 1.0, 'new_trail': 2.0, 'old_hold': 3, 'new_hold': 8},
        'TAIWAN': {'file_key': 'TAIWAN', 'old_tp': 6.5, 'new_tp': 3.5, 'old_trail': 1.0, 'new_trail': 2.0, 'old_hold': 10, 'new_hold': 10},
        'THAI': {'file_key': 'THAI', 'old_tp': 3.5, 'new_tp': 3.5, 'old_trail': 1.5, 'new_trail': 1.5, 'old_hold': 5, 'new_hold': 5}
    }
    
    results = []
    
    for market_name, config in markets_config.items():
        # หาไฟล์ (ใช้ exact match เพื่อป้องกัน match ผิด)
        file_path = None
        expected_filename = f"trade_history_{config['file_key']}.csv"
        for f in trade_history_files:
            if os.path.basename(f).upper() == expected_filename.upper():
                file_path = f
                break
        
        if not file_path:
            print(f"⚠️  ไม่พบไฟล์: {expected_filename}")
            continue
        
        print(f"\n{'=' * 160}")
        print(f"{market_name} - วิเคราะห์จาก {os.path.basename(file_path)}")
        print("=" * 160)
        
        result = analyze_market_tp_feasibility(file_path, market_name)
        if result:
            result.update(config)
            results.append(result)
            
            print(f"Total Trades: {result['total_trades']:,}")
            print(f"TP Exits: {result['tp_count']:,} ({result['tp_pct']:.1f}%)")
            print(f"Trailing Stop Exits: {result['trailing_count']:,} ({result['trailing_pct']:.1f}%)")
            print(f"Stop Loss Exits: {result['sl_count']:,} ({result['sl_pct']:.1f}%)")
            print(f"RRR Actual: {result['rrr_actual']:.2f}")
            print(f"RRR Theoretical: {result['rrr_theoretical']:.2f}")
            print(f"RRR Ratio: {result['rrr_ratio']:.1f}%")
    
    # สร้างตารางเปรียบเทียบ
    print("\n" + "=" * 160)
    print("ตารางเปรียบเทียบ: ก่อนและหลังการปรับ")
    print("=" * 160)
    
    print("\n1. การตั้งค่า (Settings):")
    print("-" * 160)
    print(f"{'Market':<12} {'TP (Old)':>12} {'TP (New)':>12} {'Trail Act (Old)':>18} {'Trail Act (New)':>18} {'Max Hold (Old)':>18} {'Max Hold (New)':>18}")
    print("-" * 160)
    
    for r in results:
        print(f"{r['market']:<12} {r['old_tp']:>11.1f}x {r['new_tp']:>11.1f}x {r['old_trail']:>17.1f}% {r['new_trail']:>17.1f}% {r['old_hold']:>17.0f} days {r['new_hold']:>17.0f} days")
    
    print("\n2. ผลลัพธ์ (Results - ข้อมูลปัจจุบัน):")
    print("-" * 160)
    print(f"{'Market':<12} {'Total Trades':>15} {'TP Exits':>12} {'TP %':>8} {'Trailing %':>12} {'SL %':>8} {'RRR Actual':>12} {'RRR Theo':>12} {'Ratio':>10}")
    print("-" * 160)
    
    for r in results:
        print(f"{r['market']:<12} {r['total_trades']:>15,} {r['tp_count']:>12,} {r['tp_pct']:>7.1f}% {r['trailing_pct']:>11.1f}% {r['sl_pct']:>7.1f}% {r['rrr_actual']:>11.2f} {r['rrr_theoretical']:>11.2f} {r['rrr_ratio']:>9.1f}%")
    
    print("\n3. สรุปและคำแนะนำ:")
    print("-" * 160)
    print("""
⚠️  หมายเหตุ: ข้อมูลปัจจุบันยังเป็นผลลัพธ์จากค่าเดิม (TP 5.0-6.5x)
   ต้อง backtest ใหม่ด้วยค่าใหม่ (TP 3.5x) เพื่อดูผลลัพธ์จริง

📊 ผลลัพธ์ปัจจุบัน (ค่าเดิม):
   - TP Exits: 0.0-0.5% (น้อยมาก)
   - Trailing Stop: 57-72% (ส่วนใหญ่)
   - RRR Actual: 16-45% ของ Theoretical (ต่ำมาก)

🎯 ผลลัพธ์ที่คาดหวัง (หลังปรับ):
   - TP Exits: 5-15% (เพิ่มขึ้น)
   - Trailing Stop: 50-60% (ลดลงเล็กน้อย)
   - RRR Actual: 50-70% ของ Theoretical (เพิ่มขึ้น)

💡 คำแนะนำ:
   1. Backtest ใหม่ด้วยค่าใหม่ (TP 3.5x, Trailing 2.0%)
   2. เปรียบเทียบผลลัพธ์ก่อนและหลัง
   3. ปรับเพิ่มเติมถ้าจำเป็น
    """)
    print("=" * 160)
    
    return results

if __name__ == "__main__":
    compare_before_after()

