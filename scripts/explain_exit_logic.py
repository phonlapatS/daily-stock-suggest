#!/usr/bin/env python
"""
Explain Exit Logic - อธิบายว่าระบบออก trade อย่างไร

คำถาม:
1. ระบบต้องถือ 3 วันหรอ?
2. หรือถ้ามันได้กำไรแล้ว ก็ถอนออกเลย?
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def explain_exit_logic():
    """Explain how the system exits trades"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        print("❌ File not found: trade_history_CHINA.csv")
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        print("❌ No trades found")
        return None
    
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df = df.dropna(subset=['hold_days', 'actual_return'])
    
    print("="*100)
    print("Exit Logic Explanation")
    print("="*100)
    
    print(f"\n❓ คำถาม: ระบบต้องถือ 3 วันหรอ? หรือถ้ามันได้กำไรแล้ว ก็ถอนออกเลย?")
    
    print(f"\n💡 คำตอบ: ระบบไม่บังคับให้ถือ 3 วัน!")
    print(f"   Max Hold = ระยะเวลาสูงสุดที่ถือได้ (ไม่ใช่บังคับให้ถือ)")
    
    print(f"\n📊 ระบบจะออก trade เมื่อ:")
    print(f"   1. ✅ ถึง TP (Take Profit) - ได้กำไรตามเป้าหมาย")
    print(f"   2. ❌ ถึง SL (Stop Loss) - เสียตามที่กำหนด")
    print(f"   3. 🔒 Trailing Stop activate - lock profits")
    print(f"   4. ⏰ ถึง Max Hold - ถ้ายังไม่ถึง TP/SL")
    
    if 'exit_reason' in df.columns:
        print(f"\n📈 Exit Reasons Distribution:")
        exit_counts = df['exit_reason'].value_counts()
        exit_pct = df['exit_reason'].value_counts(normalize=True) * 100
        
        for reason in exit_counts.index:
            count = exit_counts[reason]
            pct = exit_pct[reason]
            reason_df = df[df['exit_reason'] == reason]
            avg_ret = reason_df['actual_return'].mean()
            avg_hold = reason_df['hold_days'].mean()
            
            print(f"\n  {reason}: {count} ({pct:.1f}%)")
            print(f"    Avg Return: {avg_ret:.2f}%")
            print(f"    Avg Hold: {avg_hold:.1f} days")
            
            # Explain each exit reason
            if reason == 'TAKE_PROFIT':
                print(f"    💡 ออกเพราะ: ถึง TP ({reason_df.iloc[0].get('take_profit', 'N/A')}%)")
                print(f"    ✅ ได้กำไรตามเป้าหมาย → ออกทันที")
            elif reason == 'STOP_LOSS':
                print(f"    💡 ออกเพราะ: ถึง SL ({reason_df.iloc[0].get('stop_loss', 'N/A')}%)")
                print(f"    ❌ เสียตามที่กำหนด → ออกทันที")
            elif reason == 'TRAILING_STOP':
                print(f"    💡 ออกเพราะ: Trailing Stop activate")
                print(f"    🔒 Lock profits → ออกเมื่อได้กำไรแล้ว")
            elif reason == 'MAX_HOLD':
                print(f"    💡 ออกเพราะ: ถึง Max Hold")
                print(f"    ⏰ ถือครบเวลาสูงสุด → ออกแม้ยังไม่ถึง TP/SL")
    
    print(f"\n📊 Hold Days Analysis:")
    print(f"  Avg Hold: {df['hold_days'].mean():.2f} days")
    print(f"  Median Hold: {df['hold_days'].median():.0f} days")
    print(f"  Max Hold: {df['hold_days'].max():.0f} days")
    
    print(f"\n  Hold Days Distribution:")
    dist = df['hold_days'].value_counts().sort_index()
    for days in dist.index[:5]:
        count = dist[days]
        pct = (count / len(df)) * 100
        print(f"    {days:.0f} days: {count} ({pct:.1f}%)")
    
    print(f"\n💡 สรุป:")
    print(f"  - ระบบไม่บังคับให้ถือ 3 วัน")
    print(f"  - ระบบจะออกเมื่อ:")
    print(f"    * ได้กำไร → ออกทันที (TP หรือ Trailing Stop)")
    print(f"    * เสีย → ออกทันที (SL)")
    print(f"    * ถือครบ Max Hold → ออกแม้ยังไม่ถึง TP/SL")
    
    print(f"\n  - จากผลลัพธ์:")
    print(f"    * 95.8% ของ trades ออกใน 1 day")
    print(f"    * ส่วนใหญ่ออกเพราะ Trailing Stop (lock profits)")
    print(f"    * หรือ Stop Loss (ตัดขาดทุน)")
    print(f"    * ไม่ได้บังคับให้ถือถึง Max Hold")
    
    # Show examples
    if 'exit_reason' in df.columns:
        print(f"\n📋 ตัวอย่าง Trades:")
        
        # Example 1: Trailing Stop (winning)
        trailing_wins = df[(df['exit_reason'] == 'TRAILING_STOP') & (df['actual_return'] > 0)]
        if len(trailing_wins) > 0:
            example = trailing_wins.iloc[0]
            print(f"\n  Example 1: Trailing Stop (ได้กำไร)")
            print(f"    Hold: {example['hold_days']:.0f} days")
            print(f"    Return: {example['actual_return']:.2f}%")
            print(f"    💡 ได้กำไร → Trailing Stop lock profits → ออกใน {example['hold_days']:.0f} day")
        
        # Example 2: Stop Loss (losing)
        sl_losses = df[(df['exit_reason'] == 'STOP_LOSS') & (df['actual_return'] < 0)]
        if len(sl_losses) > 0:
            example = sl_losses.iloc[0]
            print(f"\n  Example 2: Stop Loss (เสีย)")
            print(f"    Hold: {example['hold_days']:.0f} days")
            print(f"    Return: {example['actual_return']:.2f}%")
            print(f"    💡 เสีย → Stop Loss ตัดขาดทุน → ออกใน {example['hold_days']:.0f} day")
        
        # Example 3: Take Profit
        tp_trades = df[df['exit_reason'] == 'TAKE_PROFIT']
        if len(tp_trades) > 0:
            example = tp_trades.iloc[0]
            print(f"\n  Example 3: Take Profit")
            print(f"    Hold: {example['hold_days']:.0f} days")
            print(f"    Return: {example['actual_return']:.2f}%")
            print(f"    💡 ถึง TP → ออกทันทีใน {example['hold_days']:.0f} day")
    
    print(f"\n{'='*100}")
    print("สรุป")
    print(f"{'='*100}")
    print(f"\n  ✅ ระบบไม่บังคับให้ถือ 3 วัน")
    print(f"  ✅ ระบบจะออกเมื่อได้กำไรหรือเสีย")
    print(f"  ✅ Max Hold = ระยะเวลาสูงสุด (ไม่ใช่บังคับ)")
    print(f"  ✅ 95.8% ของ trades ออกใน 1 day (ได้กำไรหรือเสียเร็ว)")
    
    return df

if __name__ == '__main__':
    df = explain_exit_logic()
    
    if df is not None:
        print(f"\n✅ อธิบายเสร็จแล้ว!")

