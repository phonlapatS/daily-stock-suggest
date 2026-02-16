#!/usr/bin/env python
"""
Analyze China Market TP Reality - วิเคราะห์ว่าหุ้นถึง TP ได้จริงหรือไม่

วิเคราะห์:
1. TP Hit Rate - มีกี่ % ที่ถึง TP
2. Exit Reasons Distribution
3. Hold Days for TP hits
4. Average return for MAX_HOLD exits
5. Comparison with Taiwan
"""

import sys
import os
import pandas as pd
import numpy as np
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_tp_reality():
    """Analyze TP hit rate and reality"""
    log_file = 'logs/trade_history_CHINA.csv'
    
    if not os.path.exists(log_file):
        print("❌ File not found: trade_history_CHINA.csv")
        print("   Please run backtest first:")
        print("   python scripts/backtest.py --full --bars 2000 --group CHINA --fast")
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        print("❌ No trades found")
        return None
    
    # Convert to numeric
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df = df.dropna(subset=['actual_return'])
    
    print("="*100)
    print("China Market - TP Reality Analysis")
    print("="*100)
    print(f"\n📊 Total Trades: {len(df)}")
    
    # ========================================================================
    # 1. Exit Reasons Distribution
    # ========================================================================
    print(f"\n{'='*100}")
    print("1. Exit Reasons Distribution")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        exit_counts = df['exit_reason'].value_counts()
        exit_pct = df['exit_reason'].value_counts(normalize=True) * 100
        
        for reason in exit_counts.index:
            count = exit_counts[reason]
            pct = exit_pct[reason]
            reason_df = df[df['exit_reason'] == reason]
            avg_ret = reason_df['actual_return'].mean() if len(reason_df) > 0 else 0
            avg_hold = reason_df['hold_days'].mean() if len(reason_df) > 0 and 'hold_days' in reason_df.columns else 0
            
            print(f"  {reason:<20}: {count:>5} ({pct:>5.1f}%) - Avg Return: {avg_ret:>6.2f}%, Avg Hold: {avg_hold:>5.1f} days")
    else:
        print("  ⚠️  No exit_reason column found")
    
    # ========================================================================
    # 2. TP Hit Rate Analysis
    # ========================================================================
    print(f"\n{'='*100}")
    print("2. TP Hit Rate Analysis")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        tp_hits = df[df['exit_reason'] == 'TAKE_PROFIT']
        total_trades = len(df)
        tp_count = len(tp_hits)
        tp_rate = (tp_count / total_trades) * 100 if total_trades > 0 else 0
        
        print(f"\n  TP Hits: {tp_count} / {total_trades} = {tp_rate:.1f}%")
        
        if tp_rate < 10:
            print(f"  ❌ TP Hit Rate ต่ำมาก (< 10%)")
            print(f"  ⚠️  หุ้นไม่ค่อยถึง TP - อาจเป็นเพราะ:")
            print(f"     - TP สูงเกินไป (5.5%)")
            print(f"     - Max Hold สั้นเกินไป (8 days)")
            print(f"     - Market conditions")
        elif tp_rate < 20:
            print(f"  ⚠️  TP Hit Rate ต่ำ (10-20%)")
            print(f"  💡 ควรปรับ TP หรือ Max Hold")
        elif tp_rate < 30:
            print(f"  ✅ TP Hit Rate ปานกลาง (20-30%)")
        else:
            print(f"  ✅ ✅ TP Hit Rate ดี (>= 30%)")
        
        if len(tp_hits) > 0:
            avg_hold_tp = tp_hits['hold_days'].mean() if 'hold_days' in tp_hits.columns else 0
            avg_return_tp = tp_hits['actual_return'].mean()
            print(f"\n  TP Hits Details:")
            print(f"    Avg Hold Days: {avg_hold_tp:.1f} days")
            print(f"    Avg Return: {avg_return_tp:.2f}%")
            
            # TP hits by hold days
            if 'hold_days' in tp_hits.columns:
                print(f"\n  TP Hits by Hold Days:")
                tp_by_days = tp_hits.groupby('hold_days').size()
                for days, count in tp_by_days.items():
                    pct = (count / len(tp_hits)) * 100
                    print(f"    {days} days: {count} hits ({pct:.1f}%)")
    
    # ========================================================================
    # 3. MAX_HOLD Exits Analysis
    # ========================================================================
    print(f"\n{'='*100}")
    print("3. MAX_HOLD Exits Analysis (หุ้นที่ถือครบ 8 วัน)")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        max_hold_exits = df[df['exit_reason'] == 'MAX_HOLD']
        max_hold_count = len(max_hold_exits)
        max_hold_rate = (max_hold_count / len(df)) * 100 if len(df) > 0 else 0
        
        print(f"\n  MAX_HOLD Exits: {max_hold_count} / {len(df)} = {max_hold_rate:.1f}%")
        
        if len(max_hold_exits) > 0:
            avg_return_max_hold = max_hold_exits['actual_return'].mean()
            wins_max_hold = max_hold_exits[max_hold_exits['actual_return'] > 0]
            win_rate_max_hold = (len(wins_max_hold) / len(max_hold_exits)) * 100
            
            print(f"  Avg Return: {avg_return_max_hold:.2f}%")
            print(f"  Win Rate: {win_rate_max_hold:.1f}%")
            
            if avg_return_max_hold < 0:
                print(f"\n  ❌ MAX_HOLD exits มี return ติดลบ!")
                print(f"  ⚠️  แสดงว่าถือ 8 วันแล้วไม่ได้กำไร - Max Hold อาจยาวเกินไป")
            elif avg_return_max_hold < 1.0:
                print(f"\n  ⚠️  MAX_HOLD exits มี return ต่ำ (< 1%)")
                print(f"  💡 ได้กำไรแต่ไม่ถึง TP - อาจต้องเพิ่ม Max Hold หรือลด TP")
            else:
                print(f"\n  ✅ MAX_HOLD exits มี return บวก")
                print(f"  💡 ได้กำไรแต่ไม่ถึง TP - อาจต้องเพิ่ม Max Hold")
            
            # Distribution
            print(f"\n  Return Distribution:")
            print(f"    Positive: {len(wins_max_hold)} ({win_rate_max_hold:.1f}%)")
            print(f"    Negative: {len(max_hold_exits) - len(wins_max_hold)} ({100-win_rate_max_hold:.1f}%)")
    
    # ========================================================================
    # 4. SL Hit Rate
    # ========================================================================
    print(f"\n{'='*100}")
    print("4. SL Hit Rate Analysis")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        sl_hits = df[df['exit_reason'] == 'STOP_LOSS']
        sl_count = len(sl_hits)
        sl_rate = (sl_count / len(df)) * 100 if len(df) > 0 else 0
        
        print(f"\n  SL Hits: {sl_count} / {len(df)} = {sl_rate:.1f}%")
        
        if sl_rate > 30:
            print(f"  ❌ SL Hit Rate สูงมาก (> 30%)")
            print(f"  ⚠️  ชน SL บ่อย - อาจเป็นเพราะ:")
            print(f"     - SL ต่ำเกินไป (1.2%)")
            print(f"     - Market volatility สูง")
        elif sl_rate > 20:
            print(f"  ⚠️  SL Hit Rate สูง (20-30%)")
        else:
            print(f"  ✅ SL Hit Rate ต่ำ (< 20%)")
        
        if len(sl_hits) > 0:
            avg_hold_sl = sl_hits['hold_days'].mean() if 'hold_days' in sl_hits.columns else 0
            print(f"  Avg Hold Days (SL): {avg_hold_sl:.1f} days")
    
    # ========================================================================
    # 5. Return Distribution by Exit Reason
    # ========================================================================
    print(f"\n{'='*100}")
    print("5. Return Distribution by Exit Reason")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        for reason in df['exit_reason'].unique():
            reason_df = df[df['exit_reason'] == reason]
            if len(reason_df) == 0:
                continue
            
            wins = reason_df[reason_df['actual_return'] > 0]
            losses = reason_df[reason_df['actual_return'] <= 0]
            
            print(f"\n  {reason}:")
            print(f"    Total: {len(reason_df)} trades")
            print(f"    Wins: {len(wins)} ({len(wins)/len(reason_df)*100:.1f}%)")
            print(f"    Losses: {len(losses)} ({len(losses)/len(reason_df)*100:.1f}%)")
            print(f"    Avg Return: {reason_df['actual_return'].mean():.2f}%")
            
            if len(wins) > 0:
                print(f"    Avg Win: {wins['actual_return'].mean():.2f}%")
            if len(losses) > 0:
                print(f"    Avg Loss: {losses['actual_return'].abs().mean():.2f}%")
    
    # ========================================================================
    # 6. Assessment: จะได้ TP ง่ายขนาดนั้นเลยหรอ?
    # ========================================================================
    print(f"\n{'='*100}")
    print("6. Assessment: จะได้ TP ง่ายขนาดนั้นเลยหรอ?")
    print(f"{'='*100}")
    
    if 'exit_reason' in df.columns:
        tp_rate = (len(df[df['exit_reason'] == 'TAKE_PROFIT']) / len(df)) * 100
        max_hold_rate = (len(df[df['exit_reason'] == 'MAX_HOLD']) / len(df)) * 100
        sl_rate = (len(df[df['exit_reason'] == 'STOP_LOSS']) / len(df)) * 100
        
        print(f"\n  TP Hit Rate: {tp_rate:.1f}%")
        print(f"  MAX_HOLD Rate: {max_hold_rate:.1f}%")
        print(f"  SL Hit Rate: {sl_rate:.1f}%")
        
        if tp_rate < 10:
            print(f"\n  ❌ ไม่! หุ้นไม่ค่อยถึง TP ({tp_rate:.1f}%)")
            print(f"  ⚠️  TP 5.5% สูงเกินไปสำหรับหุ้นรายวัน")
            print(f"  💡 แนะนำ:")
            print(f"     - ลด TP (5.5% → 4.0-4.5%)")
            print(f"     - หรือเพิ่ม Max Hold (8 → 10-12 days)")
        elif tp_rate < 20:
            print(f"\n  ⚠️  หุ้นถึง TP น้อย ({tp_rate:.1f}%)")
            print(f"  💡 แนะนำ:")
            print(f"     - ลด TP เล็กน้อย (5.5% → 5.0%)")
            print(f"     - หรือเพิ่ม Max Hold (8 → 10 days)")
        elif tp_rate < 30:
            print(f"\n  ✅ หุ้นถึง TP ได้พอสมควร ({tp_rate:.1f}%)")
            print(f"  💡 อาจปรับเพิ่มเล็กน้อยเพื่อให้ดีขึ้น")
        else:
            print(f"\n  ✅ ✅ หุ้นถึง TP ได้ดี ({tp_rate:.1f}%)")
        
        if max_hold_rate > 50:
            print(f"\n  ⚠️  MAX_HOLD Rate สูงมาก ({max_hold_rate:.1f}%)")
            print(f"  ⚠️  แสดงว่าหุ้นส่วนใหญ่ถือครบ 8 วันแล้วออก")
            print(f"  💡 แนะนำ:")
            print(f"     - เพิ่ม Max Hold (8 → 10-12 days) เพื่อให้มีเวลาไปถึง TP")
            print(f"     - หรือลด TP (5.5% → 4.5-5.0%) เพื่อให้ถึง TP ง่ายขึ้น")
        
        # Check MAX_HOLD return
        max_hold_exits = df[df['exit_reason'] == 'MAX_HOLD']
        if len(max_hold_exits) > 0:
            avg_return_max_hold = max_hold_exits['actual_return'].mean()
            if avg_return_max_hold < 0:
                print(f"\n  ❌ MAX_HOLD exits มี return ติดลบ ({avg_return_max_hold:.2f}%)")
                print(f"  ❌ แสดงว่าถือ 8 วันแล้วไม่ได้กำไร - Max Hold ยาวเกินไป")
            elif avg_return_max_hold < 1.0:
                print(f"\n  ⚠️  MAX_HOLD exits มี return ต่ำ ({avg_return_max_hold:.2f}%)")
                print(f"  ⚠️  ได้กำไรแต่ไม่ถึง TP - ควรเพิ่ม Max Hold หรือลด TP")
    
    return df

if __name__ == '__main__':
    df = analyze_tp_reality()
    
    if df is not None:
        print(f"\n{'='*100}")
        print("Analysis Complete!")
        print(f"{'='*100}")

