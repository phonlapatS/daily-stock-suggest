#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_rrr_calculation.py - วิเคราะห์การคำนวณ RRR และหาสาเหตุที่ RRR ต่ำ
================================================================================
"""

import sys
import os
import pandas as pd
import numpy as np

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache

def analyze_rrr_calculation(symbol, exchange, strategy='HYBRID_VOL', n_bars=2000):
    """วิเคราะห์การคำนวณ RRR อย่างละเอียด"""
    
    print(f"\n{'='*100}")
    print(f"🔍 วิเคราะห์ RRR Calculation: {symbol} ({exchange})")
    print(f"   Strategy: {strategy}")
    print(f"{'='*100}")
    
    try:
        tv = TvDatafeed()
        df = get_data_with_cache(
            tv=tv,
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            full_bars=5000,
            delta_bars=50
        )
        
        if df is None or len(df) < 500:
            print(f"❌ Not enough data")
            return None
        
        total_bars = len(df)
        train_end = total_bars - n_bars
        
        close = df['close']
        pct_change = close.pct_change()
        
        # Calculate threshold
        short_std = pct_change.rolling(window=20).std()
        long_std = pct_change.rolling(window=252).std()
        effective_std = np.maximum(short_std, long_std.fillna(0))
        
        if exchange.upper() in ['NASDAQ', 'NYSE', 'US']:
            floor = 0.006
        elif exchange.upper() in ['TWSE', 'TW']:
            floor = 0.005
        else:
            floor = 0.005
        
        effective_std = np.maximum(effective_std, floor)
        threshold = effective_std * 1.25
        
        # Extract patterns
        raw_patterns = []
        for i in range(len(pct_change)):
            if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
                raw_patterns.append(None)
            elif pct_change.iloc[i] > threshold.iloc[i]:
                raw_patterns.append('+')
            elif pct_change.iloc[i] < -threshold.iloc[i]:
                raw_patterns.append('-')
            else:
                raw_patterns.append(None)
        
        # Simulate trades
        predictions = []
        MAX_LEN = 8
        
        for i in range(train_end, len(df) - 1):
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            # Get last pattern
            window_slice = raw_patterns[i-MAX_LEN+1 : i+1] if i-MAX_LEN+1 >= 0 else raw_patterns[:i+1]
            last_pats = [p for p in window_slice if p is not None]
            
            if not last_pats:
                continue
            
            last_directional = last_pats[-1]
            actual_dir = 1 if next_ret > 0 else -1
            
            # Determine strategy
            if strategy == 'HYBRID_VOL':
                avg_vol = effective_std.iloc[max(0, i-20):i+1].mean()
                current_vol = effective_std.iloc[i]
                vol_regime = 'HIGH_VOL' if current_vol > avg_vol * 1.2 else 'LOW_VOL'
                
                if vol_regime == 'HIGH_VOL':
                    intended_dir = -1 if last_directional == '+' else 1 if last_directional == '-' else 0
                else:
                    intended_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
            else:
                intended_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
            
            if intended_dir == 0:
                continue
            
            # Simple filter (skip pattern matching for now)
            is_correct = 1 if intended_dir == actual_dir else 0
            
            # Calculate trader return
            # IMPORTANT: trader_return = actual_return * direction
            trader_return_pct = next_ret * 100 * intended_dir
            
            predictions.append({
                'date': df.index[i],
                'intended_dir': intended_dir,
                'actual_dir': actual_dir,
                'actual_return_pct': next_ret * 100,
                'trader_return_pct': trader_return_pct,
                'correct': is_correct
            })
        
        if len(predictions) == 0:
            print("❌ No predictions")
            return None
        
        # Detailed analysis
        df_pred = pd.DataFrame(predictions)
        
        print(f"\n📊 สรุปโดยรวม:")
        total_trades = len(df_pred)
        correct_trades = df_pred['correct'].sum()
        accuracy = (correct_trades / total_trades * 100)
        
        print(f"   Total Trades: {total_trades}")
        print(f"   Correct: {correct_trades}")
        print(f"   Accuracy: {accuracy:.2f}%")
        
        # Analyze wins and losses
        wins = df_pred[df_pred['correct'] == 1]
        losses = df_pred[df_pred['correct'] == 0]
        
        print(f"\n📈 วิเคราะห์ Wins:")
        print(f"   Count: {len(wins)}")
        if len(wins) > 0:
            win_returns = wins['trader_return_pct'].abs()
            print(f"   Avg Win%: {win_returns.mean():.4f}%")
            print(f"   Min Win%: {win_returns.min():.4f}%")
            print(f"   Max Win%: {win_returns.max():.4f}%")
            print(f"   Median Win%: {win_returns.median():.4f}%")
            print(f"\n   Win Distribution:")
            print(f"     0-0.5%: {len(win_returns[win_returns <= 0.5])}")
            print(f"     0.5-1%: {len(win_returns[(win_returns > 0.5) & (win_returns <= 1.0)])}")
            print(f"     1-2%: {len(win_returns[(win_returns > 1.0) & (win_returns <= 2.0)])}")
            print(f"     2-5%: {len(win_returns[(win_returns > 2.0) & (win_returns <= 5.0)])}")
            print(f"     5%+: {len(win_returns[win_returns > 5.0])}")
        
        print(f"\n📉 วิเคราะห์ Losses:")
        print(f"   Count: {len(losses)}")
        if len(losses) > 0:
            loss_returns = losses['trader_return_pct'].abs()
            print(f"   Avg Loss%: {loss_returns.mean():.4f}%")
            print(f"   Min Loss%: {loss_returns.min():.4f}%")
            print(f"   Max Loss%: {loss_returns.max():.4f}%")
            print(f"   Median Loss%: {loss_returns.median():.4f}%")
            print(f"\n   Loss Distribution:")
            print(f"     0-0.5%: {len(loss_returns[loss_returns <= 0.5])}")
            print(f"     0.5-1%: {len(loss_returns[(loss_returns > 0.5) & (loss_returns <= 1.0)])}")
            print(f"     1-2%: {len(loss_returns[(loss_returns > 1.0) & (loss_returns <= 2.0)])}")
            print(f"     2-5%: {len(loss_returns[(loss_returns > 2.0) & (loss_returns <= 5.0)])}")
            print(f"     5%+: {len(loss_returns[loss_returns > 5.0])}")
        
        # Calculate RRR
        avg_win = win_returns.mean() if len(wins) > 0 else 0
        avg_loss = loss_returns.mean() if len(losses) > 0 else 0
        realized_rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        print(f"\n💰 RRR Calculation:")
        print(f"   Avg Win%: {avg_win:.4f}%")
        print(f"   Avg Loss%: {avg_loss:.4f}%")
        print(f"   RRR = AvgWin / AvgLoss = {avg_win:.4f} / {avg_loss:.4f} = {realized_rrr:.4f}")
        
        # Expected value
        win_rate = accuracy / 100
        expected_value = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        print(f"\n📊 Expected Value:")
        print(f"   Win Rate: {win_rate:.4f} ({accuracy:.2f}%)")
        print(f"   Expected Value = ({win_rate:.4f} × {avg_win:.4f}%) - ({1-win_rate:.4f} × {avg_loss:.4f}%)")
        print(f"   Expected Value = {expected_value:.4f}% per trade")
        
        # Problem analysis
        print(f"\n🔍 วิเคราะห์ปัญหา:")
        
        if realized_rrr < 1.5:
            print(f"   ⚠️  RRR ต่ำ ({realized_rrr:.2f}) แม้ Accuracy สูง ({accuracy:.2f}%)")
            print(f"   → สาเหตุ: AvgWin ({avg_win:.4f}%) ใกล้เคียง AvgLoss ({avg_loss:.4f}%)")
            
            if avg_win < avg_loss:
                print(f"   ❌ ปัญหา: AvgWin ต่ำกว่า AvgLoss!")
                print(f"   → อาจเกิดจาก:")
                print(f"      1. Direction logic ผิด (ทายผิด direction)")
                print(f"      2. ไม่มี stop loss/take profit")
                print(f"      3. Market noise ทำให้กำไรเล็กแต่ขาดทุนใหญ่")
            else:
                print(f"   ⚠️  AvgWin มากกว่า AvgLoss แต่ไม่มากพอ")
                print(f"   → ควรปรับปรุง:")
                print(f"      1. เพิ่ม Take Profit target")
                print(f"      2. ลด Stop Loss")
                print(f"      3. ใช้ Trailing Stop")
        
        # Analyze by direction
        print(f"\n📊 วิเคราะห์ตาม Direction:")
        print("-"*100)
        print(f"{'Direction':<15} {'Trades':<10} {'Wins':<10} {'Losses':<10} {'Avg Win%':<12} {'Avg Loss%':<12} {'RRR':<10}")
        print("-"*100)
        
        for direction in [1, -1]:
            dir_df = df_pred[df_pred['intended_dir'] == direction]
            if len(dir_df) > 0:
                dir_wins = dir_df[dir_df['correct'] == 1]
                dir_losses = dir_df[dir_df['correct'] == 0]
                
                dir_avg_win = dir_wins['trader_return_pct'].abs().mean() if len(dir_wins) > 0 else 0
                dir_avg_loss = dir_losses['trader_return_pct'].abs().mean() if len(dir_losses) > 0 else 0
                dir_rrr = dir_avg_win / dir_avg_loss if dir_avg_loss > 0 else 0
                
                dir_label = "LONG" if direction == 1 else "SHORT"
                print(f"{dir_label:<15} {len(dir_df):<10} {len(dir_wins):<10} {len(dir_losses):<10} {dir_avg_win:<12.4f} {dir_avg_loss:<12.4f} {dir_rrr:<10.2f}")
        
        print("-"*100)
        
        # Show sample trades
        print(f"\n📝 Sample Trades (10 ล่าสุด):")
        print("-"*100)
        print(f"{'Date':<12} {'Intended':<10} {'Actual':<10} {'Actual Ret%':<12} {'Trader Ret%':<12} {'Result':<10}")
        print("-"*100)
        
        for idx, row in df_pred.tail(10).iterrows():
            date_str = str(row['date'])[:10]
            intended = "LONG" if row['intended_dir'] == 1 else "SHORT"
            actual = "UP" if row['actual_dir'] == 1 else "DOWN"
            result = "✅ WIN" if row['correct'] == 1 else "❌ LOSS"
            print(f"{date_str:<12} {intended:<10} {actual:<10} {row['actual_return_pct']:<12.4f} {row['trader_return_pct']:<12.4f} {result:<10}")
        
        print("-"*100)
        
        return df_pred
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("\n" + "="*100)
    print("🔍 RRR Calculation Analysis")
    print("="*100)
    
    # Test US Market
    print("\n🇺🇸 US Market (NVDA) - Hybrid Volatility:")
    analyze_rrr_calculation('NVDA', 'NASDAQ', strategy='HYBRID_VOL', n_bars=2000)
    
    print("\n🇹🇼 Taiwan Market (TSMC) - Hybrid Volatility:")
    analyze_rrr_calculation('2330', 'TWSE', strategy='HYBRID_VOL', n_bars=2000)
    
    print("\n" + "="*100)

if __name__ == "__main__":
    main()

