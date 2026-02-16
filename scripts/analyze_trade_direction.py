#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_trade_direction.py - วิเคราะห์ Direction Logic และ Win/Loss Pattern
================================================================================
วิเคราะห์ว่าทำไม accuracy ต่ำ (50%) และหาทางปรับปรุง
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

def analyze_direction_logic(symbol, exchange, strategy='TREND', n_bars=2000):
    """วิเคราะห์ Direction Logic และ Win/Loss Pattern"""
    
    print(f"\n{'='*80}")
    print(f"🔍 วิเคราะห์ Direction Logic: {symbol} ({exchange})")
    print(f"   Strategy: {strategy}")
    print(f"{'='*80}")
    
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
        
        # Analyze direction logic
        print(f"\n📊 วิเคราะห์ Direction Logic:")
        print(f"   Test Period: {train_end} → {total_bars} ({n_bars} bars)")
        
        direction_stats = {
            'trend_long': {'total': 0, 'correct': 0, 'up': 0, 'down': 0},
            'trend_short': {'total': 0, 'correct': 0, 'up': 0, 'down': 0},
            'reversion_long': {'total': 0, 'correct': 0, 'up': 0, 'down': 0},
            'reversion_short': {'total': 0, 'correct': 0, 'up': 0, 'down': 0}
        }
        
        pattern_direction_map = []
        
        for i in range(train_end, len(df) - 1):
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            # Get last pattern
            MAX_LEN = 8
            window_slice = raw_patterns[i-MAX_LEN+1 : i+1] if i-MAX_LEN+1 >= 0 else raw_patterns[:i+1]
            last_pats = [p for p in window_slice if p is not None]
            
            if not last_pats:
                continue
            
            last_directional = last_pats[-1]
            actual_dir = 1 if next_ret > 0 else -1
            
            # Trend Following Logic
            if last_directional == '+':
                trend_dir = 1  # LONG
                reversion_dir = -1  # SHORT
            elif last_directional == '-':
                trend_dir = -1  # SHORT
                reversion_dir = 1  # LONG
            else:
                continue
            
            # Track statistics
            if strategy == 'TREND':
                if trend_dir == 1:
                    direction_stats['trend_long']['total'] += 1
                    direction_stats['trend_long']['up'] += 1 if actual_dir == 1 else 0
                    direction_stats['trend_long']['down'] += 1 if actual_dir == -1 else 0
                    direction_stats['trend_long']['correct'] += 1 if trend_dir == actual_dir else 0
                else:
                    direction_stats['trend_short']['total'] += 1
                    direction_stats['trend_short']['up'] += 1 if actual_dir == 1 else 0
                    direction_stats['trend_short']['down'] += 1 if actual_dir == -1 else 0
                    direction_stats['trend_short']['correct'] += 1 if trend_dir == actual_dir else 0
            else:  # REVERSION
                if reversion_dir == 1:
                    direction_stats['reversion_long']['total'] += 1
                    direction_stats['reversion_long']['up'] += 1 if actual_dir == 1 else 0
                    direction_stats['reversion_long']['down'] += 1 if actual_dir == -1 else 0
                    direction_stats['reversion_long']['correct'] += 1 if reversion_dir == actual_dir else 0
                else:
                    direction_stats['reversion_short']['total'] += 1
                    direction_stats['reversion_short']['up'] += 1 if actual_dir == 1 else 0
                    direction_stats['reversion_short']['down'] += 1 if actual_dir == -1 else 0
                    direction_stats['reversion_short']['correct'] += 1 if reversion_dir == actual_dir else 0
            
            pattern_direction_map.append({
                'date': df.index[i],
                'pattern': last_directional,
                'trend_dir': trend_dir,
                'reversion_dir': reversion_dir,
                'actual_dir': actual_dir,
                'next_return': next_ret * 100
            })
        
        # Display statistics
        print(f"\n📈 Direction Statistics ({strategy}):")
        print("-"*80)
        
        if strategy == 'TREND':
            print(f"{'Direction':<20} {'Total':<10} {'Up':<10} {'Down':<10} {'Correct':<10} {'Accuracy':<12}")
            print("-"*80)
            
            for key, label in [('trend_long', 'LONG (+++ -> LONG)'), ('trend_short', 'SHORT (--- -> SHORT)')]:
                stats = direction_stats[key]
                total = stats['total']
                if total > 0:
                    acc = (stats['correct'] / total * 100)
                    print(f"{label:<20} {total:<10} {stats['up']:<10} {stats['down']:<10} {stats['correct']:<10} {acc:<12.2f}%")
        else:  # REVERSION
            print(f"{'Direction':<20} {'Total':<10} {'Up':<10} {'Down':<10} {'Correct':<10} {'Accuracy':<12}")
            print("-"*80)
            
            for key, label in [('reversion_long', 'LONG (--- -> LONG)'), ('reversion_short', 'SHORT (+++ -> SHORT)')]:
                stats = direction_stats[key]
                total = stats['total']
                if total > 0:
                    acc = (stats['correct'] / total * 100)
                    print(f"{label:<20} {total:<10} {stats['up']:<10} {stats['down']:<10} {stats['correct']:<10} {acc:<12.2f}%")
        
        print("-"*80)
        
        # Analyze pattern sequences
        print(f"\n🔍 วิเคราะห์ Pattern Sequences:")
        df_map = pd.DataFrame(pattern_direction_map)
        
        if not df_map.empty:
            # Analyze consecutive patterns
            print(f"\n📊 Consecutive Pattern Analysis:")
            consecutive_stats = []
            
            for length in [2, 3, 4]:
                for i in range(len(df_map) - length + 1):
                    patterns = ''.join([str(p) for p in df_map['pattern'].iloc[i:i+length]])
                    actual_dir = df_map['actual_dir'].iloc[i+length-1]
                    
                    if strategy == 'TREND':
                        # Trend: last pattern determines direction
                        last_pat = patterns[-1]
                        predicted_dir = 1 if last_pat == '+' else -1 if last_pat == '-' else 0
                    else:  # REVERSION
                        # Reversion: inverse of last pattern
                        last_pat = patterns[-1]
                        predicted_dir = -1 if last_pat == '+' else 1 if last_pat == '-' else 0
                    
                    if predicted_dir != 0:
                        consecutive_stats.append({
                            'pattern': patterns,
                            'predicted': predicted_dir,
                            'actual': actual_dir,
                            'correct': 1 if predicted_dir == actual_dir else 0
                        })
            
            if consecutive_stats:
                df_consec = pd.DataFrame(consecutive_stats)
                pattern_acc = df_consec.groupby('pattern').agg({
                    'correct': ['count', 'sum']
                })
                pattern_acc.columns = ['Total', 'Correct']
                pattern_acc['Accuracy'] = (pattern_acc['Correct'] / pattern_acc['Total'] * 100).round(2)
                pattern_acc = pattern_acc.sort_values('Accuracy', ascending=False)
                
                print(f"\n{'Pattern':<15} {'Total':<10} {'Correct':<10} {'Accuracy':<12}")
                print("-"*50)
                for pattern, row in pattern_acc.head(10).iterrows():
                    print(f"{pattern:<15} {int(row['Total']):<10} {int(row['Correct']):<10} {row['Accuracy']:<12.2f}%")
        
        # Recommendations
        print(f"\n💡 สาเหตุที่ Accuracy ต่ำ (50%):")
        print(f"   1. Direction Logic อาจไม่เหมาะสมกับตลาด")
        print(f"   2. Pattern matching อาจไม่แม่นยำพอ")
        print(f"   3. Threshold อาจไม่เหมาะสม")
        print(f"   4. Market regime อาจเปลี่ยนไป")
        
        print(f"\n🎯 คำแนะนำการปรับปรุง:")
        print(f"   1. ใช้ Regime-Aware Logic (BULL/BEAR market)")
        print(f"   2. เพิ่มเงื่อนไข Volume/Volatility")
        print(f"   3. ใช้ Multi-timeframe confirmation")
        print(f"   4. ปรับ Threshold ตาม Market Volatility")
        print(f"   5. ใช้ ADX/RSI เพื่อยืนยัน Trend")
        
        return df_map
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("\n" + "="*80)
    print("🔍 Direction Logic Analysis")
    print("="*80)
    
    # Test US Market
    print("\n🇺🇸 US Market (NVDA):")
    analyze_direction_logic('NVDA', 'NASDAQ', strategy='TREND', n_bars=2000)
    analyze_direction_logic('NVDA', 'NASDAQ', strategy='REVERSION', n_bars=2000)
    
    # Test Taiwan Market
    print("\n🇹🇼 Taiwan Market (TSMC):")
    analyze_direction_logic('2330', 'TWSE', strategy='TREND', n_bars=2000)
    analyze_direction_logic('2330', 'TWSE', strategy='REVERSION', n_bars=2000)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

