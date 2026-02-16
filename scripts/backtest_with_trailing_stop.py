#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backtest_with_trailing_stop.py - Backtest ด้วย Trailing Stop Loss เพื่อให้ RRR > 2.0
================================================================================

ปรับปรุงจาก backtest.py:
- เปลี่ยนจาก 1-day exit เป็น Trailing Stop Loss
- ให้กำไรเดินทาง (let profit run)
- Lock profit เมื่อ price pullback

Author: Stock Analysis System
Date: 2026-01-XX
"""

import pandas as pd
import numpy as np
import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.indicators import calculate_adx, calculate_volume_adv
from core.engines.base_engine import BasePatternEngine
from core.data_cache import get_data_with_cache
from tvDatafeed import TvDatafeed, Interval
import config


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
    
    Returns:
        dict with exit_idx, exit_price, return_pct, exit_reason
    """
    if entry_idx >= len(df) - 1:
        return None
    
    entry_price = df['close'].iloc[entry_idx]
    atr_series = calculate_atr(df['high'], df['low'], df['close'])
    current_atr = atr_series.iloc[entry_idx]
    
    # Fallback if ATR is NaN
    if pd.isna(current_atr) or current_atr == 0:
        current_atr = entry_price * 0.02  # 2% fallback
    
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
        current_atr_val = atr_series.iloc[i] if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else current_atr
        
        if direction == 1:  # LONG
            # Update highest price
            if current_high > highest_price:
                highest_price = current_high
                # Update trailing stop (never goes down)
                new_stop = highest_price - (current_atr_val * atr_multiplier)
                trailing_stop = max(trailing_stop, new_stop)
            
            # Check if stop hit
            if current_low <= trailing_stop:
                exit_price = trailing_stop
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': 'TRAILING_STOP',
                    'hold_days': i - entry_idx
                }
            
            # Check if max hold days reached
            if i == entry_idx + max_hold_days:
                exit_price = current_close
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': 'MAX_HOLD',
                    'hold_days': max_hold_days
                }
        else:  # SHORT
            # Update lowest price
            if current_low < lowest_price:
                lowest_price = current_low
                # Update trailing stop (never goes up)
                new_stop = lowest_price + (current_atr_val * atr_multiplier)
                trailing_stop = min(trailing_stop, new_stop)
            
            # Check if stop hit
            if current_high >= trailing_stop:
                exit_price = trailing_stop
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': 'TRAILING_STOP',
                    'hold_days': i - entry_idx
                }
            
            # Check if max hold days reached
            if i == entry_idx + max_hold_days:
                exit_price = current_close
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': 'MAX_HOLD',
                    'hold_days': max_hold_days
                }
    
    # End of data
    exit_price = df['close'].iloc[-1]
    return {
        'exit_idx': len(df) - 1,
        'exit_price': exit_price,
        'return_pct': ((exit_price - entry_price) / entry_price) * 100 * direction,
        'exit_reason': 'END_OF_DATA',
        'hold_days': len(df) - 1 - entry_idx
    }


def backtest_with_trailing_stop(symbol, exchange, n_bars=500, atr_multiplier=2.0, max_hold_days=10, 
                                 threshold_multiplier=1.25, min_stats=30, verbose=True):
    """
    Backtest with Trailing Stop Loss instead of 1-day exit
    """
    # Load data
    df = get_data_with_cache(symbol, exchange, Interval.in_daily, n_bars=n_bars)
    if df is None or len(df) < 100:
        if verbose:
            print(f"❌ {symbol}: Not enough data")
        return None
    
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    pct_change = close.pct_change()
    
    # Determine market type
    is_us = any(ex in exchange.upper() for ex in ['NASDAQ', 'NYSE', 'US'])
    is_thai = any(ex in exchange.upper() for ex in ['SET', 'MAI', 'TH'])
    
    # Calculate threshold
    min_floor = 0.006 if is_us else 0.01 if is_thai else 0.005
    engine = BasePatternEngine()
    effective_std = engine.calculate_dynamic_threshold(pct_change, min_floor)
    
    # Pattern detection (simplified - same as backtest.py)
    MIN_LEN = 3
    MAX_LEN = 8
    
    pattern_stats = {}
    scan_start = 50
    
    # Build pattern stats
    for i in range(scan_start, len(pct_change) - 1):
        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0:
                continue
            
            window = pct_change.iloc[i-length+1 : i+1]
            thresh_win = effective_std.iloc[i-length+1 : i+1] * threshold_multiplier
            
            pat_str = engine.extract_pattern(window, thresh_win)
            if not pat_str or len(pat_str) < MIN_LEN:
                continue
            
            next_ret = (close.iloc[i+1] - close.iloc[i]) / close.iloc[i]
            
            if pat_str not in pattern_stats:
                pattern_stats[pat_str] = []
            pattern_stats[pat_str].append(next_ret)
    
    # Simulate trades with trailing stop
    trades = []
    test_start = scan_start + 50  # Start testing after enough history
    
    for i in range(test_start, len(df) - max_hold_days):
        # Determine direction (simplified - use last pattern)
        intended_dir = 0
        window_slice = pct_change.iloc[max(0, i-3):i+1]
        thresh_slice = effective_std.iloc[max(0, i-3):i+1] * threshold_multiplier
        last_pats = engine.extract_pattern(window_slice, thresh_slice)
        
        if last_pats:
            last_char = last_pats[-1] if last_pats else None
            if last_char == '+':
                intended_dir = -1 if is_thai else 1  # Mean Reversion vs Trend
            elif last_char == '-':
                intended_dir = 1 if is_thai else -1
        
        if intended_dir == 0:
            continue
        
        # Find matching pattern
        best_match = None
        best_prob = 0
        
        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0:
                continue
            
            window_slice = pct_change.iloc[i-length+1 : i+1]
            thresh_win = effective_std.iloc[i-length+1 : i+1] * threshold_multiplier
            pat_str = engine.extract_pattern(window_slice, thresh_win)
            
            if not pat_str or pat_str not in pattern_stats:
                continue
            
            hist_returns = pattern_stats[pat_str]
            if len(hist_returns) < min_stats:
                continue
            
            # Calculate stats for direction
            if intended_dir == 1:
                wins = [abs(r) for r in hist_returns if r > 0]
                losses = [abs(r) for r in hist_returns if r <= 0]
            else:
                wins = [abs(r) for r in hist_returns if r < 0]
                losses = [abs(r) for r in hist_returns if r >= 0]
            
            win_count = len(wins)
            prob = (win_count / len(hist_returns)) * 100
            
            if prob > best_prob and prob >= 55.0:  # Minimum threshold
                best_match = {
                    'pattern': pat_str,
                    'prob': prob,
                    'length': length
                }
                best_prob = prob
        
        if not best_match:
            continue
        
        # Simulate trailing stop exit
        exit_result = simulate_trailing_stop_exit(df, i, intended_dir, atr_multiplier, max_hold_days)
        
        if exit_result:
            trades.append({
                'symbol': symbol,
                'entry_idx': i,
                'entry_price': df['close'].iloc[i],
                'direction': intended_dir,
                'exit_idx': exit_result['exit_idx'],
                'exit_price': exit_result['exit_price'],
                'return_pct': exit_result['return_pct'],
                'exit_reason': exit_result['exit_reason'],
                'hold_days': exit_result['hold_days'],
                'prob': best_prob
            })
    
    if not trades:
        return None
    
    trades_df = pd.DataFrame(trades)
    wins = trades_df[trades_df['return_pct'] > 0]
    losses = trades_df[trades_df['return_pct'] <= 0]
    
    win_rate = len(wins) / len(trades_df) * 100 if len(trades_df) > 0 else 0
    avg_win = wins['return_pct'].mean() if not wins.empty else 0
    avg_loss = abs(losses['return_pct'].mean()) if not losses.empty else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    return {
        'symbol': symbol,
        'exchange': exchange,
        'count': len(trades_df),
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rrr': rrr,
        'trades': trades_df
    }


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[BACKTEST TRAILING STOP] ทดสอบ Trailing Stop Loss เพื่อให้ RRR > 2.0")
    print("="*100)
    
    # Test with sample symbols
    test_symbols = [
        {'symbol': 'PTTEP', 'exchange': 'SET', 'country': 'TH'},
        {'symbol': 'DOHOME', 'exchange': 'SET', 'country': 'TH'},
        {'symbol': 'VRTX', 'exchange': 'NASDAQ', 'country': 'US'},
        {'symbol': 'MDLZ', 'exchange': 'NASDAQ', 'country': 'US'},
    ]
    
    print(f"\n🎯 ทดสอบ {len(test_symbols)} symbols")
    
    # Test different ATR multipliers
    atr_multipliers = [1.5, 2.0, 2.5]
    results_summary = []
    
    for item in test_symbols:
        symbol = item['symbol']
        exchange = item['exchange']
        country = item['country']
        
        print(f"\n[{symbol}] ({country})")
        print("-" * 80)
        
        for atr_mult in atr_multipliers:
            result = backtest_with_trailing_stop(
                symbol, exchange,
                n_bars=500,
                atr_multiplier=atr_mult,
                max_hold_days=10,
                verbose=False
            )
            
            if result:
                print(f"   ATR × {atr_mult}: Count={result['count']}, "
                      f"WinRate={result['win_rate']:.1f}%, "
                      f"AvgWin={result['avg_win']:.2f}%, "
                      f"AvgLoss={result['avg_loss']:.2f}%, "
                      f"RRR={result['rrr']:.2f}")
                
                results_summary.append({
                    'symbol': symbol,
                    'country': country,
                    'atr_multiplier': atr_mult,
                    **{k: v for k, v in result.items() if k != 'trades'}
                })
    
    # Summary
    if results_summary:
        print("\n" + "="*100)
        print("[SUMMARY] สรุปผลการทดสอบ")
        print("="*100)
        
        summary_df = pd.DataFrame(results_summary)
        
        print("\n[1] เปรียบเทียบ ATR Multipliers")
        print("-" * 80)
        for atr_mult in atr_multipliers:
            mult_df = summary_df[summary_df['atr_multiplier'] == atr_mult]
            if not mult_df.empty:
                print(f"\n   ATR × {atr_mult}:")
                print(f"      Mean RRR: {mult_df['rrr'].mean():.2f}")
                print(f"      Mean WinRate: {mult_df['win_rate'].mean():.1f}%")
                print(f"      Mean AvgWin: {mult_df['avg_win'].mean():.2f}%")
                print(f"      Mean AvgLoss: {mult_df['avg_loss'].mean():.2f}%")
                print(f"      Symbols with RRR > 2.0: {len(mult_df[mult_df['rrr'] > 2.0])}/{len(mult_df)}")
        
        print("\n[2] Best Configuration")
        print("-" * 80)
        best = summary_df.nlargest(1, 'rrr')
        if not best.empty:
            best_row = best.iloc[0]
            print(f"   Symbol: {best_row['symbol']}")
            print(f"   ATR Multiplier: {best_row['atr_multiplier']}")
            print(f"   RRR: {best_row['rrr']:.2f}")
            print(f"   WinRate: {best_row['win_rate']:.1f}%")
            print(f"   AvgWin: {best_row['avg_win']:.2f}%")
            print(f"   AvgLoss: {best_row['avg_loss']:.2f}%")
            
            if best_row['rrr'] > 2.0:
                print(f"\n   ✅ RRR > 2.0 ได้แล้ว!")
            else:
                print(f"\n   ⚠️ RRR ยังต่ำกว่า 2.0")


if __name__ == "__main__":
    main()

