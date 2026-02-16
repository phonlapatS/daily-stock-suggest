#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
deep_analysis_international.py - วิเคราะห์ลึกเพื่อหาสาเหตุที่ Accuracy ต่ำ
================================================================================
วิเคราะห์ว่าทำไม Win/Loss เท่าๆกัน (50%) และหาทางปรับปรุง
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

def deep_analyze_market(symbol, exchange, strategy='TREND', n_bars=2000):
    """วิเคราะห์ลึกเพื่อหาสาเหตุที่ Accuracy ต่ำ"""
    
    print(f"\n{'='*100}")
    print(f"🔬 Deep Analysis: {symbol} ({exchange}) - Strategy: {strategy}")
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
        high = df['high']
        low = df['low']
        volume = df['volume']
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
        
        # 1. วิเคราะห์ Market Regime (BULL vs BEAR)
        sma50 = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()
        
        regime_stats = {
            'BULL': {'total': 0, 'up': 0, 'down': 0, 'correct': 0},
            'BEAR': {'total': 0, 'up': 0, 'down': 0, 'correct': 0},
            'SIDEWAYS': {'total': 0, 'up': 0, 'down': 0, 'correct': 0}
        }
        
        # 2. วิเคราะห์ Volatility Regime
        volatility_stats = {
            'HIGH_VOL': {'total': 0, 'up': 0, 'down': 0, 'correct': 0},
            'LOW_VOL': {'total': 0, 'up': 0, 'down': 0, 'correct': 0}
        }
        
        # 3. วิเคราะห์ Pattern Strength
        pattern_strength_stats = {}
        
        # 4. วิเคราะห์ Consecutive Patterns
        consecutive_analysis = []
        
        for i in range(train_end, len(df) - 1):
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            # Determine regime
            current_price = close.iloc[i]
            current_sma50 = sma50.iloc[i]
            current_sma200 = sma200.iloc[i] if not pd.isna(sma200.iloc[i]) else current_price
            
            if pd.isna(current_sma50):
                regime = 'SIDEWAYS'
            elif current_price > current_sma50 and current_sma50 > current_sma200:
                regime = 'BULL'
            elif current_price < current_sma50 and current_sma50 < current_sma200:
                regime = 'BEAR'
            else:
                regime = 'SIDEWAYS'
            
            # Determine volatility
            current_vol = effective_std.iloc[i]
            avg_vol = effective_std.iloc[max(0, i-20):i+1].mean()
            vol_regime = 'HIGH_VOL' if current_vol > avg_vol * 1.2 else 'LOW_VOL'
            
            # Get pattern
            MAX_LEN = 8
            window_slice = raw_patterns[i-MAX_LEN+1 : i+1] if i-MAX_LEN+1 >= 0 else raw_patterns[:i+1]
            last_pats = [p for p in window_slice if p is not None]
            
            if not last_pats:
                continue
            
            last_directional = last_pats[-1]
            actual_dir = 1 if next_ret > 0 else -1
            
            # Determine predicted direction
            if strategy == 'TREND':
                predicted_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
            else:  # REVERSION
                predicted_dir = -1 if last_directional == '+' else 1 if last_directional == '-' else 0
            
            if predicted_dir == 0:
                continue
            
            is_correct = 1 if predicted_dir == actual_dir else 0
            
            # Count consecutive patterns
            consecutive_count = 1
            for j in range(i-1, max(0, i-10), -1):
                if raw_patterns[j] == last_directional:
                    consecutive_count += 1
                else:
                    break
            
            # Track statistics
            regime_stats[regime]['total'] += 1
            regime_stats[regime]['up'] += 1 if actual_dir == 1 else 0
            regime_stats[regime]['down'] += 1 if actual_dir == -1 else 0
            regime_stats[regime]['correct'] += is_correct
            
            volatility_stats[vol_regime]['total'] += 1
            volatility_stats[vol_regime]['up'] += 1 if actual_dir == 1 else 0
            volatility_stats[vol_regime]['down'] += 1 if actual_dir == -1 else 0
            volatility_stats[vol_regime]['correct'] += is_correct
            
            # Pattern strength
            pattern_key = f"{last_directional}x{consecutive_count}"
            if pattern_key not in pattern_strength_stats:
                pattern_strength_stats[pattern_key] = {'total': 0, 'correct': 0}
            pattern_strength_stats[pattern_key]['total'] += 1
            pattern_strength_stats[pattern_key]['correct'] += is_correct
            
            consecutive_analysis.append({
                'consecutive': consecutive_count,
                'predicted': predicted_dir,
                'actual': actual_dir,
                'correct': is_correct,
                'regime': regime,
                'vol_regime': vol_regime
            })
        
        # Display results
        print(f"\n📊 1. Market Regime Analysis:")
        print("-"*100)
        print(f"{'Regime':<15} {'Total':<10} {'Up':<10} {'Down':<10} {'Correct':<10} {'Accuracy':<12}")
        print("-"*100)
        
        for regime, stats in regime_stats.items():
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total'] * 100)
                print(f"{regime:<15} {stats['total']:<10} {stats['up']:<10} {stats['down']:<10} {stats['correct']:<10} {acc:<12.2f}%")
        
        print(f"\n📊 2. Volatility Regime Analysis:")
        print("-"*100)
        print(f"{'Volatility':<15} {'Total':<10} {'Up':<10} {'Down':<10} {'Correct':<10} {'Accuracy':<12}")
        print("-"*100)
        
        for vol_regime, stats in volatility_stats.items():
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total'] * 100)
                print(f"{vol_regime:<15} {stats['total']:<10} {stats['up']:<10} {stats['down']:<10} {stats['correct']:<10} {acc:<12.2f}%")
        
        print(f"\n📊 3. Pattern Strength Analysis:")
        print("-"*100)
        print(f"{'Pattern':<15} {'Total':<10} {'Correct':<10} {'Accuracy':<12}")
        print("-"*100)
        
        pattern_list = []
        for pattern, stats in pattern_strength_stats.items():
            if stats['total'] >= 5:  # Only show patterns with enough samples
                acc = (stats['correct'] / stats['total'] * 100)
                pattern_list.append({
                    'pattern': pattern,
                    'total': stats['total'],
                    'accuracy': acc
                })
        
        pattern_list.sort(key=lambda x: x['accuracy'], reverse=True)
        for p in pattern_list[:10]:
            print(f"{p['pattern']:<15} {p['total']:<10} {pattern_strength_stats[p['pattern']]['correct']:<10} {p['accuracy']:<12.2f}%")
        
        # Analyze consecutive patterns
        df_consec = pd.DataFrame(consecutive_analysis)
        if not df_consec.empty:
            print(f"\n📊 4. Consecutive Pattern Analysis:")
            print("-"*100)
            consec_stats = df_consec.groupby('consecutive').agg({
                'correct': ['count', 'sum']
            })
            consec_stats.columns = ['Total', 'Correct']
            consec_stats['Accuracy'] = (consec_stats['Correct'] / consec_stats['Total'] * 100).round(2)
            
            print(f"{'Consecutive':<15} {'Total':<10} {'Correct':<10} {'Accuracy':<12}")
            print("-"*100)
            for consec, row in consec_stats.iterrows():
                print(f"{consec:<15} {int(row['Total']):<10} {int(row['Correct']):<10} {row['Accuracy']:<12.2f}%")
        
        # Recommendations
        print(f"\n💡 สาเหตุที่ Accuracy ต่ำ (50%):")
        
        # Check if accuracy is around 50% (random)
        total_trades = sum(s['total'] for s in regime_stats.values())
        total_correct = sum(s['correct'] for s in regime_stats.values())
        overall_acc = (total_correct / total_trades * 100) if total_trades > 0 else 0
        
        if 45 <= overall_acc <= 55:
            print(f"   ⚠️  Accuracy = {overall_acc:.2f}% (ใกล้เคียง Random 50%)")
            print(f"   → Direction Logic อาจไม่เหมาะสมกับตลาด")
            print(f"   → Pattern matching อาจไม่แม่นยำพอ")
        
        # Check regime differences
        bull_acc = (regime_stats['BULL']['correct'] / regime_stats['BULL']['total'] * 100) if regime_stats['BULL']['total'] > 0 else 0
        bear_acc = (regime_stats['BEAR']['correct'] / regime_stats['BEAR']['total'] * 100) if regime_stats['BEAR']['total'] > 0 else 0
        
        if abs(bull_acc - bear_acc) > 10:
            print(f"   ✅ พบความแตกต่างระหว่าง BULL ({bull_acc:.2f}%) และ BEAR ({bear_acc:.2f}%)")
            print(f"   → ควรใช้ Regime-Aware Logic")
        
        print(f"\n🎯 คำแนะนำการปรับปรุง:")
        print(f"   1. ใช้ Regime-Aware Logic:")
        print(f"      - BULL Market: ใช้ Trend Following")
        print(f"      - BEAR Market: ใช้ Mean Reversion หรือไม่เทรด")
        print(f"      - SIDEWAYS: ใช้ Mean Reversion")
        
        print(f"\n   2. เพิ่ม Volatility Filter:")
        print(f"      - HIGH_VOL: อาจต้องใช้ threshold สูงขึ้น")
        print(f"      - LOW_VOL: อาจใช้ threshold ต่ำลง")
        
        print(f"\n   3. ใช้ Consecutive Pattern Strength:")
        print(f"      - Pattern ที่มี consecutive สูงอาจมีความน่าเชื่อถือมากกว่า")
        print(f"      - แต่ต้องระวัง overfitting")
        
        print(f"\n   4. เพิ่ม Multi-timeframe Confirmation:")
        print(f"      - ใช้ Weekly/Daily timeframe ร่วมกัน")
        print(f"      - ยืนยัน signal จากหลาย timeframe")
        
        print(f"\n   5. ใช้ Volume/ADX Filter:")
        print(f"      - Volume spike อาจยืนยัน trend")
        print(f"      - ADX >= 20 สำหรับ Trend Following")
        
        return {
            'overall_accuracy': overall_acc,
            'regime_stats': regime_stats,
            'volatility_stats': volatility_stats,
            'pattern_strength_stats': pattern_strength_stats
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("\n" + "="*100)
    print("🔬 Deep Analysis - International Markets")
    print("="*100)
    print("วิเคราะห์ลึกเพื่อหาสาเหตุที่ Accuracy ต่ำและหาทางปรับปรุง")
    print("="*100)
    
    # Test US Market
    print("\n🇺🇸 US Market (NVDA):")
    deep_analyze_market('NVDA', 'NASDAQ', strategy='TREND', n_bars=2000)
    deep_analyze_market('NVDA', 'NASDAQ', strategy='REVERSION', n_bars=2000)
    
    # Test Taiwan Market
    print("\n🇹🇼 Taiwan Market (TSMC):")
    deep_analyze_market('2330', 'TWSE', strategy='TREND', n_bars=2000)
    deep_analyze_market('2330', 'TWSE', strategy='REVERSION', n_bars=2000)
    
    print("\n" + "="*100)

if __name__ == "__main__":
    main()

