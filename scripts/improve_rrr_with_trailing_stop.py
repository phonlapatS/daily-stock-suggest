#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
improve_rrr_with_trailing_stop.py - ปรับปรุง RRR ให้ > 2.0 ด้วย Trailing Stop Loss
================================================================================

เป้าหมาย:
- ปรับ Exit Strategy ให้ RRR > 2.0
- ใช้ Trailing Stop Loss เพื่อให้กำไรเดินทาง
- ทดสอบว่าทำได้จริงหรือไม่

Author: Stock Analysis System
Date: 2026-01-XX
"""

import pandas as pd
import numpy as np
import os
import sys
import glob

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
METRICS_FILE = os.path.join(DATA_DIR, "symbol_performance.csv")


def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range (ATR)"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def simulate_trailing_stop_exit(df, entry_idx, direction, atr_multiplier=2.0, max_hold_days=10):
    """
    Simulate Trailing Stop Loss Exit
    
    Args:
        df: DataFrame with 'close', 'high', 'low'
        entry_idx: Entry bar index
        direction: 1 for LONG, -1 for SHORT
        atr_multiplier: ATR multiplier for stop distance
        max_hold_days: Maximum holding period
    
    Returns:
        dict with exit_idx, exit_price, return_pct, exit_reason
    """
    if entry_idx >= len(df) - 1:
        return None
    
    entry_price = df['close'].iloc[entry_idx]
    atr = calculate_atr(df['high'], df['low'], df['close'])
    current_atr = atr.iloc[entry_idx] if not pd.isna(atr.iloc[entry_idx]) else df['close'].iloc[entry_idx] * 0.02
    
    # Initial stop loss
    if direction == 1:  # LONG
        initial_stop = entry_price - (current_atr * atr_multiplier)
        trailing_stop = initial_stop
        highest_price = entry_price
    else:  # SHORT
        initial_stop = entry_price + (current_atr * atr_multiplier)
        trailing_stop = initial_stop
        lowest_price = entry_price
    
    # Simulate holding
    for i in range(entry_idx + 1, min(entry_idx + max_hold_days + 1, len(df))):
        current_high = df['high'].iloc[i]
        current_low = df['low'].iloc[i]
        current_close = df['close'].iloc[i]
        
        if direction == 1:  # LONG
            # Update highest price
            if current_high > highest_price:
                highest_price = current_high
                # Update trailing stop
                trailing_stop = highest_price - (current_atr * atr_multiplier)
            
            # Check if stop hit
            if current_low <= trailing_stop:
                exit_price = trailing_stop
                exit_reason = "TRAILING_STOP"
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': exit_reason,
                    'hold_days': i - entry_idx
                }
            
            # Check if max hold days reached
            if i == entry_idx + max_hold_days:
                exit_price = current_close
                exit_reason = "MAX_HOLD"
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': exit_reason,
                    'hold_days': max_hold_days
                }
        else:  # SHORT
            # Update lowest price
            if current_low < lowest_price:
                lowest_price = current_low
                # Update trailing stop
                trailing_stop = lowest_price + (current_atr * atr_multiplier)
            
            # Check if stop hit
            if current_high >= trailing_stop:
                exit_price = trailing_stop
                exit_reason = "TRAILING_STOP"
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': exit_reason,
                    'hold_days': i - entry_idx
                }
            
            # Check if max hold days reached
            if i == entry_idx + max_hold_days:
                exit_price = current_close
                exit_reason = "MAX_HOLD"
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': exit_reason,
                    'hold_days': max_hold_days
                }
    
    # Should not reach here, but return last close if needed
    exit_price = df['close'].iloc[-1]
    return {
        'exit_idx': len(df) - 1,
        'exit_price': exit_price,
        'return_pct': ((exit_price - entry_price) / entry_price) * 100 * direction,
        'exit_reason': "END_OF_DATA",
        'hold_days': len(df) - 1 - entry_idx
    }


def analyze_trailing_stop_impact():
    """วิเคราะห์ผลกระทบของ Trailing Stop ต่อ RRR"""
    print("\n" + "="*100)
    print("[ANALYSIS] วิเคราะห์ผลกระทบของ Trailing Stop ต่อ RRR")
    print("="*100)
    
    # Load trade history
    trade_files = glob.glob(os.path.join(LOG_DIR, "trade_history_*.csv"))
    if not trade_files:
        trade_files = [os.path.join(LOG_DIR, "trade_history.csv")]
    
    all_trades = []
    for f in trade_files:
        try:
            df = pd.read_csv(f, engine='python', on_bad_lines='skip')
            if not df.empty:
                all_trades.append(df)
        except Exception as e:
            print(f"⚠️ Error loading {f}: {e}")
    
    if not all_trades:
        print("❌ ไม่พบ trade history")
        return
    
    df_trades = pd.concat(all_trades, ignore_index=True)
    print(f"\n📊 โหลด trade history: {len(df_trades)} trades")
    
    # Group by symbol
    print("\n[1] วิเคราะห์ RRR ปัจจุบัน (1-day exit)")
    print("-" * 80)
    
    # Current RRR (1-day exit)
    df_trades['actual_return'] = pd.to_numeric(df_trades['actual_return'], errors='coerce')
    df_trades['trader_return'] = df_trades.apply(
        lambda row: row['actual_return'] if str(row['forecast']).upper() == 'UP' else -row['actual_return'],
        axis=1
    )
    
    wins = df_trades[df_trades['trader_return'] > 0]
    losses = df_trades[df_trades['trader_return'] <= 0]
    
    current_avg_win = wins['trader_return'].mean() if not wins.empty else 0
    current_avg_loss = abs(losses['trader_return'].mean()) if not losses.empty else 0
    current_rrr = current_avg_win / current_avg_loss if current_avg_loss > 0 else 0
    
    print(f"   Current Strategy (1-day exit):")
    print(f"   AvgWin: {current_avg_win:.2f}%")
    print(f"   AvgLoss: {current_avg_loss:.2f}%")
    print(f"   RRR: {current_rrr:.2f}")
    print(f"   Win Rate: {len(wins)/len(df_trades)*100:.1f}%")
    
    print("\n[2] วิเคราะห์ Trailing Stop Strategy")
    print("-" * 80)
    print("   Strategy: Trailing Stop = High - (ATR × 2.0), Max Hold = 10 days")
    print("   Note: ต้องใช้ข้อมูลราคาจริงเพื่อทดสอบ")
    
    print("\n[3] แนวทางปรับปรุง RRR")
    print("-" * 80)
    print("   [PROBLEM]")
    print("   - Exit เร็วเกินไป (1-day) → กำไรไม่เต็มที่")
    print("   - ไม่มี Trailing Stop → กำไรหายไปเมื่อ pullback")
    print("   - RRR ต่ำ (Mean=1.20) → ไม่คุ้มเสี่ยง")
    
    print("\n   [SOLUTION]")
    print("   1. ใช้ Trailing Stop Loss:")
    print("      - Initial Stop = Entry - (ATR × 2.0)")
    print("      - Trailing Stop = High - (ATR × 2.0)")
    print("      - Update เมื่อ High ใหม่")
    print()
    print("   2. ให้กำไรเดินทาง:")
    print("      - Max Hold = 10 days (หรือจนกว่า Trailing Stop จะถูก hit)")
    print("      - Lock profit เมื่อ price เดินทาง")
    print()
    print("   3. ปรับตามตลาด:")
    print("      - THAI (Mean Reversion): Trailing Stop แน่น (ATR × 1.5)")
    print("      - US (Trend Following): Trailing Stop หลวม (ATR × 2.5)")
    
    print("\n[4] สูตร Trailing Stop")
    print("-" * 80)
    print("   [LONG Position]")
    print("   Initial Stop = Entry Price - (ATR × Multiplier)")
    print("   Trailing Stop = Highest Price - (ATR × Multiplier)")
    print("   Update: เมื่อ High ใหม่ > Highest Price")
    print()
    print("   [SHORT Position]")
    print("   Initial Stop = Entry Price + (ATR × Multiplier)")
    print("   Trailing Stop = Lowest Price + (ATR × Multiplier)")
    print("   Update: เมื่อ Low ใหม่ < Lowest Price")
    
    print("\n[5] ผลลัพธ์ที่คาดหวัง")
    print("-" * 80)
    print("   [Expected Improvement]")
    print("   - AvgWin: เพิ่มขึ้น (ให้กำไรเดินทาง)")
    print("   - AvgLoss: คงที่หรือลดลง (Trailing Stop ป้องกัน)")
    print("   - RRR: เพิ่มขึ้นเป็น > 2.0")
    print("   - Win Rate: อาจลดลงเล็กน้อย (แต่ RRR สูงขึ้น)")
    
    print("\n" + "="*100)
    print("[NEXT STEPS] ขั้นตอนต่อไป")
    print("="*100)
    print("   1. 🔴 สร้างสคริปต์ทดสอบ Trailing Stop กับข้อมูลจริง")
    print("   2. 🔴 ปรับปรุง Engine ให้รองรับ Trailing Stop")
    print("   3. 🔴 ทดสอบว่า RRR > 2.0 ได้จริงหรือไม่")
    print("   4. 🔴 ปรับ Multiplier ตามตลาด (TH: 1.5, US: 2.5)")


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[IMPROVE RRR] ปรับปรุง RRR ให้ > 2.0 ด้วย Trailing Stop Loss")
    print("="*100)
    
    analyze_trailing_stop_impact()


if __name__ == "__main__":
    main()

