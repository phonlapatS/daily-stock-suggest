#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compare_trailing_stop_results.py - เปรียบเทียบผลลัพธ์ก่อนและหลังใช้ Trailing Stop
================================================================================

เปรียบเทียบ:
1. 1-day exit (เดิม) vs Trailing Stop (ใหม่)
2. RRR, Win Rate, AvgWin, AvgLoss
3. จำนวนหุ้นที่ RRR > 2.0

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

sys.path.append(BASE_DIR)
from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache
from core.engines.base_engine import BasePatternEngine
import config


def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range (ATR)"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def simulate_1day_exit(df, entry_idx, direction):
    """Simulate 1-day exit (เดิม)"""
    if entry_idx >= len(df) - 1:
        return None
    
    entry_price = df['close'].iloc[entry_idx]
    exit_price = df['close'].iloc[entry_idx + 1]
    
    if direction == 1:  # LONG
        return_pct = ((exit_price - entry_price) / entry_price) * 100
    else:  # SHORT
        return_pct = ((entry_price - exit_price) / entry_price) * 100
    
    return {
        'exit_idx': entry_idx + 1,
        'exit_price': exit_price,
        'return_pct': return_pct,
        'exit_reason': '1DAY_EXIT',
        'hold_days': 1
    }


def simulate_trailing_stop_exit(df, entry_idx, direction, atr_multiplier=2.0, max_hold_days=10):
    """Simulate Trailing Stop Exit (ใหม่)"""
    if entry_idx >= len(df) - 1:
        return None
    
    entry_price = df['close'].iloc[entry_idx]
    atr_series = calculate_atr(df['high'], df['low'], df['close'])
    current_atr = atr_series.iloc[entry_idx]
    
    if pd.isna(current_atr) or current_atr == 0:
        current_atr = entry_price * 0.02
    
    if direction == 1:  # LONG
        initial_stop = entry_price - (current_atr * atr_multiplier)
        trailing_stop = initial_stop
        highest_price = entry_price
    else:  # SHORT
        initial_stop = entry_price + (current_atr * atr_multiplier)
        trailing_stop = initial_stop
        lowest_price = entry_price
    
    for i in range(entry_idx + 1, min(entry_idx + max_hold_days + 1, len(df))):
        current_high = df['high'].iloc[i]
        current_low = df['low'].iloc[i]
        current_close = df['close'].iloc[i]
        current_atr_val = atr_series.iloc[i] if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else current_atr
        
        if direction == 1:  # LONG
            if current_high > highest_price:
                highest_price = current_high
                new_stop = highest_price - (current_atr_val * atr_multiplier)
                trailing_stop = max(trailing_stop, new_stop)
            
            if current_low <= trailing_stop:
                exit_price = trailing_stop
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': 'TRAILING_STOP',
                    'hold_days': i - entry_idx
                }
            
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
            if current_low < lowest_price:
                lowest_price = current_low
                new_stop = lowest_price + (current_atr_val * atr_multiplier)
                trailing_stop = min(trailing_stop, new_stop)
            
            if current_high >= trailing_stop:
                exit_price = trailing_stop
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': 'TRAILING_STOP',
                    'hold_days': i - entry_idx
                }
            
            if i == entry_idx + max_hold_days:
                exit_price = current_close
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': 'MAX_HOLD',
                    'hold_days': max_hold_days
                }
    
    exit_price = df['close'].iloc[-1]
    return {
        'exit_idx': len(df) - 1,
        'exit_price': exit_price,
        'return_pct': ((exit_price - entry_price) / entry_price) * 100 * direction,
        'exit_reason': 'END_OF_DATA',
        'hold_days': len(df) - 1 - entry_idx
    }


def compare_strategies(symbol, exchange, country):
    """เปรียบเทียบ 1-day exit vs Trailing Stop"""
    try:
        from tvDatafeed import TvDatafeed
        tv = TvDatafeed()
        df = get_data_with_cache(tv=tv, symbol=symbol, exchange=exchange, interval=Interval.in_daily, full_bars=1000)
        if df is None or len(df) < 100:
            return None
        
        # Load trade history
        trade_files = glob.glob(os.path.join(LOG_DIR, "trade_history_*.csv"))
        if not trade_files:
            trade_files = [os.path.join(LOG_DIR, "trade_history.csv")]
        
        all_trades = []
        for f in trade_files:
            try:
                trades_df = pd.read_csv(f, engine='python', on_bad_lines='skip')
                if not trades_df.empty and 'symbol' in trades_df.columns:
                    symbol_trades = trades_df[trades_df['symbol'] == symbol]
                    if not symbol_trades.empty:
                        all_trades.append(symbol_trades)
            except:
                continue
        
        if not all_trades:
            return None
        
        trades_df = pd.concat(all_trades, ignore_index=True)
        
        # Convert date
        if 'date' in trades_df.columns:
            trades_df['date'] = pd.to_datetime(trades_df['date'], errors='coerce')
            trades_df = trades_df.dropna(subset=['date'])
        
        if trades_df.empty:
            return None
        
        # Match with price data
        df['date'] = pd.to_datetime(df.index) if not isinstance(df.index[0], pd.Timestamp) else df.index
        df = df.reset_index()
        
        # Determine ATR multiplier
        if country == 'US':
            atr_multiplier = 2.5
        else:
            atr_multiplier = 1.5
        
        # Test both strategies
        results_1day = []
        results_trailing = []
        
        for _, trade in trades_df.head(50).iterrows():  # Limit to 50 trades for speed
            try:
                entry_date = trade['date']
                entry_idx = df[df['date'] == entry_date].index[0] if 'date' in df.columns else None
                
                if entry_idx is None or entry_idx >= len(df) - 1:
                    continue
                
                forecast = str(trade.get('forecast', '')).upper()
                direction = 1 if forecast == 'UP' else -1
                
                # 1-day exit
                exit_1day = simulate_1day_exit(df, entry_idx, direction)
                if exit_1day:
                    results_1day.append(exit_1day['return_pct'])
                
                # Trailing stop
                exit_trailing = simulate_trailing_stop_exit(df, entry_idx, direction, atr_multiplier, 10)
                if exit_trailing:
                    results_trailing.append(exit_trailing['return_pct'])
            except:
                continue
        
        if not results_1day or not results_trailing:
            return None
        
        # Calculate stats
        def calc_stats(returns):
            returns = np.array(returns)
            wins = returns[returns > 0]
            losses = returns[returns <= 0]
            
            win_rate = len(wins) / len(returns) * 100 if len(returns) > 0 else 0
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
            
            return {
                'count': len(returns),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'rrr': rrr,
                'expectancy': (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
            }
        
        stats_1day = calc_stats(results_1day)
        stats_trailing = calc_stats(results_trailing)
        
        return {
            'symbol': symbol,
            'country': country,
            '1day': stats_1day,
            'trailing': stats_trailing
        }
    
    except Exception as e:
        print(f"   Error: {e}")
        return None


def main():
    """Main function"""
    print("\n" + "="*100)
    print("[COMPARE RESULTS] เปรียบเทียบผลลัพธ์ก่อนและหลังใช้ Trailing Stop")
    print("="*100)
    
    # Load metrics to get symbols
    metrics_file = os.path.join(DATA_DIR, "symbol_performance.csv")
    if not os.path.exists(metrics_file):
        print("❌ ไม่พบไฟล์ metrics")
        return
    
    df_metrics = pd.read_csv(metrics_file)
    if df_metrics.empty:
        print("❌ ไม่มีข้อมูล metrics")
        return
    
    print(f"\n📊 โหลด metrics: {len(df_metrics)} symbols")
    
    # Select top symbols from each country
    test_symbols = []
    
    for country in ['TH', 'US', 'CN', 'TW']:
        country_df = df_metrics[df_metrics['Country'] == country].nlargest(3, 'Count')
        for _, row in country_df.iterrows():
            if country == 'TH':
                exchange = 'SET'
            elif country == 'US':
                exchange = 'NASDAQ'
            elif country == 'CN':
                exchange = 'HKEX'
            elif country == 'TW':
                exchange = 'TWSE'
            else:
                exchange = 'SET'
            
            test_symbols.append({
                'symbol': row['symbol'],
                'exchange': exchange,
                'country': country
            })
    
    print(f"\n🎯 ทดสอบ {len(test_symbols)} symbols")
    
    # Compare strategies
    results = []
    for item in test_symbols:
        print(f"\n   Testing {item['symbol']} ({item['country']})...")
        result = compare_strategies(item['symbol'], item['exchange'], item['country'])
        if result:
            results.append(result)
    
    if not results:
        print("\n❌ ไม่มีผลลัพธ์")
        return
    
    # Summary
    print("\n" + "="*100)
    print("[RESULTS] สรุปผลการเปรียบเทียบ")
    print("="*100)
    
    print("\n[1] เปรียบเทียบโดยรวม")
    print("-" * 100)
    
    # Aggregate stats
    all_1day = {'count': 0, 'wins': [], 'losses': []}
    all_trailing = {'count': 0, 'wins': [], 'losses': []}
    
    for r in results:
        all_1day['count'] += r['1day']['count']
        all_trailing['count'] += r['trailing']['count']
        
        # Estimate wins/losses from win rate
        wins_1day = r['1day']['count'] * (r['1day']['win_rate'] / 100)
        losses_1day = r['1day']['count'] - wins_1day
        all_1day['wins'].extend([r['1day']['avg_win']] * int(wins_1day))
        all_1day['losses'].extend([-r['1day']['avg_loss']] * int(losses_1day))
        
        wins_trailing = r['trailing']['count'] * (r['trailing']['win_rate'] / 100)
        losses_trailing = r['trailing']['count'] - wins_trailing
        all_trailing['wins'].extend([r['trailing']['avg_win']] * int(wins_trailing))
        all_trailing['losses'].extend([-r['trailing']['avg_loss']] * int(losses_trailing))
    
    def calc_agg_stats(data):
        wins = np.array(data['wins'])
        losses = np.array(data['losses'])
        all_returns = np.concatenate([wins, losses])
        
        win_rate = len(wins) / len(all_returns) * 100 if len(all_returns) > 0 else 0
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        return {
            'count': data['count'],
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'rrr': rrr
        }
    
    agg_1day = calc_agg_stats(all_1day)
    agg_trailing = calc_agg_stats(all_trailing)
    
    print(f"\n{'Metric':<20} {'1-Day Exit':>20} {'Trailing Stop':>20} {'Change':>20}")
    print("-" * 100)
    print(f"{'Count':<20} {agg_1day['count']:>20} {agg_trailing['count']:>20} {agg_trailing['count'] - agg_1day['count']:>+20}")
    print(f"{'Win Rate':<20} {agg_1day['win_rate']:>19.1f}% {agg_trailing['win_rate']:>19.1f}% {agg_trailing['win_rate'] - agg_1day['win_rate']:>+19.1f}%")
    print(f"{'AvgWin%':<20} {agg_1day['avg_win']:>19.2f}% {agg_trailing['avg_win']:>19.2f}% {agg_trailing['avg_win'] - agg_1day['avg_win']:>+19.2f}%")
    print(f"{'AvgLoss%':<20} {agg_1day['avg_loss']:>19.2f}% {agg_trailing['avg_loss']:>19.2f}% {agg_trailing['avg_loss'] - agg_1day['avg_loss']:>+19.2f}%")
    print(f"{'RRR':<20} {agg_1day['rrr']:>20.2f} {agg_trailing['rrr']:>20.2f} {agg_trailing['rrr'] - agg_1day['rrr']:>+20.2f}")
    
    print("\n[2] วิเคราะห์ผลลัพธ์")
    print("-" * 100)
    
    rrr_improved = agg_trailing['rrr'] > agg_1day['rrr']
    rrr_above_2 = agg_trailing['rrr'] > 2.0
    
    print(f"\n   RRR:")
    print(f"   - เดิม (1-day exit): {agg_1day['rrr']:.2f}")
    print(f"   - ใหม่ (Trailing Stop): {agg_trailing['rrr']:.2f}")
    print(f"   - เปลี่ยนแปลง: {agg_trailing['rrr'] - agg_1day['rrr']:+.2f}")
    
    if rrr_improved:
        print(f"   ✅ RRR ดีขึ้น!")
    else:
        print(f"   ⚠️ RRR แย่ลง")
    
    if rrr_above_2:
        print(f"   ✅ RRR > 2.0 ได้แล้ว!")
    else:
        print(f"   ⚠️ RRR ยังต่ำกว่า 2.0")
    
    print(f"\n   Win Rate:")
    print(f"   - เดิม: {agg_1day['win_rate']:.1f}%")
    print(f"   - ใหม่: {agg_trailing['win_rate']:.1f}%")
    print(f"   - เปลี่ยนแปลง: {agg_trailing['win_rate'] - agg_1day['win_rate']:+.1f}%")
    
    print(f"\n   AvgWin:")
    print(f"   - เดิม: {agg_1day['avg_win']:.2f}%")
    print(f"   - ใหม่: {agg_trailing['avg_win']:.2f}%")
    print(f"   - เปลี่ยนแปลง: {agg_trailing['avg_win'] - agg_1day['avg_win']:+.2f}%")
    
    print("\n[3] สรุปผลลัพธ์")
    print("-" * 100)
    
    if rrr_improved and rrr_above_2:
        print("   ✅ Trailing Stop ดีขึ้นและ RRR > 2.0 แล้ว!")
    elif rrr_improved:
        print("   ✅ Trailing Stop ดีขึ้น แต่ RRR ยังต่ำกว่า 2.0")
    else:
        print("   ⚠️ Trailing Stop ยังไม่ดีขึ้น อาจต้องปรับ ATR Multiplier")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    main()

