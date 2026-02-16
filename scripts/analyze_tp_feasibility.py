#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
วิเคราะห์ว่า TP เป็นไปได้จริงหรือไม่ - ตรวจสอบจาก trade_history
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

def analyze_tp_feasibility():
    """วิเคราะห์ว่า TP เป็นไปได้จริงหรือไม่"""
    
    print("\n" + "=" * 160)
    print("วิเคราะห์: TP เป็นไปได้จริงหรือไม่? (จาก trade_history)")
    print("=" * 160)
    
    # หา trade_history files
    trade_history_files = glob.glob(os.path.join(LOGS_DIR, "trade_history_*.csv"))
    
    markets = {
        'US': [f for f in trade_history_files if 'US' in f.upper()],
        'CHINA': [f for f in trade_history_files if 'CHINA' in f.upper() or 'CN' in f.upper()],
        'TAIWAN': [f for f in trade_history_files if 'TAIWAN' in f.upper() or 'TW' in f.upper()],
        'THAI': [f for f in trade_history_files if 'THAI' in f.upper() or 'TH' in f.upper()]
    }
    
    results = []
    
    for market_name, files in markets.items():
        if not files:
            continue
        
        file_path = files[0]
        print(f"\n{'=' * 160}")
        print(f"{market_name} - วิเคราะห์จาก {os.path.basename(file_path)}")
        print("=" * 160)
        
        try:
            df = pd.read_csv(file_path)
            
            total_trades = len(df)
            print(f"\nTotal Trades: {total_trades:,}")
            
            # ตรวจสอบ exit_reason
            if 'exit_reason' in df.columns:
                exit_reasons = df['exit_reason'].value_counts()
                print(f"\nExit Reasons:")
                for reason, count in exit_reasons.items():
                    pct = (count / total_trades * 100) if total_trades > 0 else 0
                    print(f"  - {reason}: {count:,} ({pct:.1f}%)")
                
                # หา TP exits
                tp_exits = df[df['exit_reason'].str.contains('TP|TAKE_PROFIT', case=False, na=False)]
                tp_count = len(tp_exits)
                tp_pct = (tp_count / total_trades * 100) if total_trades > 0 else 0
                
                print(f"\n📊 TP Exits:")
                print(f"  - จำนวน: {tp_count:,} trades")
                print(f"  - เปอร์เซ็นต์: {tp_pct:.1f}%")
                
                # ตรวจสอบ actual_return ของ TP exits
                if not tp_exits.empty and 'actual_return' in tp_exits.columns:
                    tp_exits['actual_return'] = pd.to_numeric(tp_exits['actual_return'], errors='coerce').fillna(0)
                    avg_tp_return = tp_exits['actual_return'].mean()
                    min_tp_return = tp_exits['actual_return'].min()
                    max_tp_return = tp_exits['actual_return'].max()
                    
                    print(f"  - Avg Return: {avg_tp_return:.2f}%")
                    print(f"  - Min Return: {min_tp_return:.2f}%")
                    print(f"  - Max Return: {max_tp_return:.2f}%")
                
                # ตรวจสอบ RRR
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
                    rrr = avg_win / avg_loss if avg_loss > 0 else 0
                    
                    print(f"\n📊 RRR (Actual):")
                    print(f"  - AvgWin%: {avg_win:.2f}%")
                    print(f"  - AvgLoss%: {avg_loss:.2f}%")
                    print(f"  - RRR: {rrr:.2f}")
                    
                    # Theoretical RRR
                    if market_name == 'US':
                        theoretical_rrr = 5.0
                    elif market_name == 'CHINA':
                        theoretical_rrr = 5.0
                    elif market_name == 'TAIWAN':
                        theoretical_rrr = 6.5
                    elif market_name == 'THAI':
                        theoretical_rrr = 2.33
                    else:
                        theoretical_rrr = 0
                    
                    if theoretical_rrr > 0:
                        print(f"  - Theoretical RRR: {theoretical_rrr:.2f}")
                        print(f"  - Actual vs Theoretical: {rrr:.2f} vs {theoretical_rrr:.2f} ({rrr/theoretical_rrr*100:.1f}%)")
                
                # ตรวจสอบ hold_days
                if 'hold_days' in df.columns:
                    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce').fillna(0)
                    avg_hold = df['hold_days'].mean()
                    max_hold = df['hold_days'].max()
                    
                    print(f"\n📊 Hold Days:")
                    print(f"  - Average: {avg_hold:.1f} days")
                    print(f"  - Maximum: {max_hold:.0f} days")
                    
                    if not tp_exits.empty and 'hold_days' in tp_exits.columns:
                        tp_exits['hold_days'] = pd.to_numeric(tp_exits['hold_days'], errors='coerce').fillna(0)
                        avg_tp_hold = tp_exits['hold_days'].mean()
                        print(f"  - TP Exits Average: {avg_tp_hold:.1f} days")
                
                results.append({
                    'market': market_name,
                    'total_trades': total_trades,
                    'tp_count': tp_count,
                    'tp_pct': tp_pct,
                    'rrr_actual': rrr,
                    'rrr_theoretical': theoretical_rrr if 'theoretical_rrr' in locals() else 0,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss
                })
            else:
                print("  ⚠️  ไม่มี exit_reason column")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # สรุปเปรียบเทียบ
    print("\n" + "=" * 160)
    print("สรุปเปรียบเทียบ")
    print("=" * 160)
    print(f"{'Market':<12} {'Total Trades':>15} {'TP Exits':>12} {'TP %':>8} {'RRR Actual':>12} {'RRR Theoretical':>18} {'Ratio':>10}")
    print("-" * 160)
    
    for r in results:
        ratio = (r['rrr_actual'] / r['rrr_theoretical'] * 100) if r['rrr_theoretical'] > 0 else 0
        print(f"{r['market']:<12} {r['total_trades']:>15,} {r['tp_count']:>12,} {r['tp_pct']:>7.1f}% {r['rrr_actual']:>11.2f} {r['rrr_theoretical']:>17.2f} {ratio:>9.1f}%")
    
    print("\n" + "=" * 160)
    print("สรุปและคำแนะนำ:")
    print("=" * 160)
    print("""
1. TP เป็นไปได้จริงหรือไม่?
   - ขึ้นอยู่กับ % TP Exits
   - ถ้า TP Exits < 10% → TP ยากมาก (ถึง TP น้อย)
   - ถ้า TP Exits 10-30% → TP เป็นไปได้ (แต่ไม่บ่อย)
   - ถ้า TP Exits > 30% → TP เป็นไปได้บ่อย

2. RRR Actual vs Theoretical:
   - RRR Actual < 50% ของ Theoretical → TP ยากมาก
   - RRR Actual 50-70% ของ Theoretical → TP เป็นไปได้
   - RRR Actual > 70% ของ Theoretical → TP เป็นไปได้บ่อย

3. สาเหตุที่ RRR Actual ต่ำกว่า Theoretical:
   - Trailing Stop exit ก่อนถึง TP
   - Max Hold exit ก่อนถึง TP
   - SL hit ก่อนถึง TP
   - Slippage และ Commission ลด RRR

4. คำแนะนำ:
   - ถ้า TP Exits < 10% → พิจารณาลด TP หรือเพิ่ม Max Hold
   - ถ้า RRR Actual < 50% ของ Theoretical → TP อาจสูงเกินไป
   - ใช้ Trailing Stop เพื่อ lock กำไร (แม้ไม่ถึง TP)
    """)
    print("=" * 160)

if __name__ == "__main__":
    analyze_tp_feasibility()

