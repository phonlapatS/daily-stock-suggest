#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimize_trailing_stop_parameters.py - หาค่า ATR Multiplier และ Max Hold Days ที่เหมาะสม
================================================================================

เป้าหมาย:
- RRR > 2.0
- ลด AvgLoss ให้ต่ำลง
- ปรับตามตลาด (US, CN, TW ยากมาก)

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


def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range (ATR)"""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def simulate_trailing_stop_exit(df, entry_idx, direction, atr_multiplier=2.0, max_hold_days=10, take_profit_pct=None):
    """
    Simulate Trailing Stop Exit with optional Take Profit
    """
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
        take_profit_price = entry_price * (1 + take_profit_pct / 100) if take_profit_pct else None
    else:  # SHORT
        initial_stop = entry_price + (current_atr * atr_multiplier)
        trailing_stop = initial_stop
        lowest_price = entry_price
        take_profit_price = entry_price * (1 - take_profit_pct / 100) if take_profit_pct else None
    
    for i in range(entry_idx + 1, min(entry_idx + max_hold_days + 1, len(df))):
        current_high = df['high'].iloc[i]
        current_low = df['low'].iloc[i]
        current_close = df['close'].iloc[i]
        current_atr_val = atr_series.iloc[i] if i < len(atr_series) and not pd.isna(atr_series.iloc[i]) else current_atr
        
        if direction == 1:  # LONG
            # Check Take Profit first
            if take_profit_price and current_high >= take_profit_price:
                exit_price = take_profit_price
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((exit_price - entry_price) / entry_price) * 100,
                    'exit_reason': 'TAKE_PROFIT',
                    'hold_days': i - entry_idx
                }
            
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
            if take_profit_price and current_low <= take_profit_price:
                exit_price = take_profit_price
                return {
                    'exit_idx': i,
                    'exit_price': exit_price,
                    'return_pct': ((entry_price - exit_price) / entry_price) * 100,
                    'exit_reason': 'TAKE_PROFIT',
                    'hold_days': i - entry_idx
                }
            
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


def test_parameters(symbol, exchange, country, atr_multiplier, max_hold_days, take_profit_pct=None):
    """Test specific parameters"""
    try:
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
        
        if 'date' in trades_df.columns:
            trades_df['date'] = pd.to_datetime(trades_df['date'], errors='coerce')
            trades_df = trades_df.dropna(subset=['date'])
        
        if trades_df.empty:
            return None
        
        df['date'] = pd.to_datetime(df.index) if not isinstance(df.index[0], pd.Timestamp) else df.index
        df = df.reset_index()
        
        results = []
        for _, trade in trades_df.head(30).iterrows():  # Limit for speed
            try:
                entry_date = trade['date']
                entry_idx = df[df['date'] == entry_date].index[0] if 'date' in df.columns else None
                
                if entry_idx is None or entry_idx >= len(df) - 1:
                    continue
                
                forecast = str(trade.get('forecast', '')).upper()
                direction = 1 if forecast == 'UP' else -1
                
                exit_result = simulate_trailing_stop_exit(df, entry_idx, direction, atr_multiplier, max_hold_days, take_profit_pct)
                if exit_result:
                    results.append(exit_result['return_pct'])
            except:
                continue
        
        if not results:
            return None
        
        returns = np.array(results)
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
    
    except Exception as e:
        return None


def optimize_parameters():
    """หาค่าที่เหมาะสม"""
    print("\n" + "="*100)
    print("[OPTIMIZE] หาค่า ATR Multiplier และ Max Hold Days ที่เหมาะสม")
    print("="*100)
    
    # Load metrics
    metrics_file = os.path.join(DATA_DIR, "symbol_performance.csv")
    if not os.path.exists(metrics_file):
        print("❌ ไม่พบไฟล์ metrics")
        return
    
    df_metrics = pd.read_csv(metrics_file)
    
    # Test different parameters - Focus on tighter stops and take profit
    test_configs = [
        # (country, atr_mult, max_hold, take_profit, description)
        # THAI Market - Mean Reversion (Tight stops, Quick exits)
        ('TH', 1.0, 3, 2.0, 'TH: Very Tight Stop, Very Short Hold, TP 2%'),
        ('TH', 1.0, 3, 3.0, 'TH: Very Tight Stop, Very Short Hold, TP 3%'),
        ('TH', 1.2, 5, 4.0, 'TH: Tight Stop, Short Hold, TP 4%'),
        ('TH', 1.5, 7, 5.0, 'TH: Medium Stop, Medium Hold, TP 5%'),
        
        # US Market - Trend Following (Need very tight stops for foreign stocks - difficult!)
        ('US', 1.0, 3, 2.0, 'US: Very Tight Stop, Very Short Hold, TP 2%'),
        ('US', 1.0, 3, 3.0, 'US: Very Tight Stop, Very Short Hold, TP 3%'),
        ('US', 1.2, 3, 2.0, 'US: Tight Stop, Very Short Hold, TP 2%'),
        ('US', 1.2, 5, 3.0, 'US: Tight Stop, Short Hold, TP 3%'),
        ('US', 1.5, 5, 4.0, 'US: Medium Stop, Short Hold, TP 4%'),
        
        # CHINA Market - Mean Reversion (Tight stops)
        ('CN', 1.0, 3, 3.0, 'CN: Very Tight Stop, Very Short Hold, TP 3%'),
        ('CN', 1.2, 5, 4.0, 'CN: Tight Stop, Short Hold, TP 4%'),
        ('CN', 1.5, 7, 5.0, 'CN: Medium Stop, Medium Hold, TP 5%'),
        
        # TAIWAN Market - Mean Reversion (Tight stops)
        ('TW', 1.0, 3, 3.0, 'TW: Very Tight Stop, Very Short Hold, TP 3%'),
        ('TW', 1.2, 5, 4.0, 'TW: Tight Stop, Short Hold, TP 4%'),
        ('TW', 1.5, 7, 5.0, 'TW: Medium Stop, Medium Hold, TP 5%'),
    ]
    
    # Get test symbols
    test_symbols = {}
    for country in ['TH', 'US', 'CN', 'TW']:
        country_df = df_metrics[df_metrics['Country'] == country].nlargest(2, 'Count')
        symbols = []
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
            
            symbols.append({'symbol': row['symbol'], 'exchange': exchange})
        test_symbols[country] = symbols
    
    print(f"\n🎯 ทดสอบ {len(test_configs)} configurations")
    
    # Test each configuration
    results = []
    for country, atr_mult, max_hold, tp, desc in test_configs:
        print(f"\n   Testing: {desc}")
        print(f"   ATR Mult: {atr_mult}, Max Hold: {max_hold}, Take Profit: {tp}%")
        
        all_results = []
        for item in test_symbols.get(country, []):
            result = test_parameters(item['symbol'], item['exchange'], country, atr_mult, max_hold, tp)
            if result:
                all_results.append(result)
        
        if all_results:
            # Aggregate
            total_count = sum(r['count'] for r in all_results)
            weighted_wr = sum(r['win_rate'] * r['count'] for r in all_results) / total_count if total_count > 0 else 0
            avg_win = np.mean([r['avg_win'] for r in all_results])
            avg_loss = np.mean([r['avg_loss'] for r in all_results])
            avg_rrr = np.mean([r['rrr'] for r in all_results])
            avg_exp = np.mean([r['expectancy'] for r in all_results])
            
            results.append({
                'country': country,
                'atr_multiplier': atr_mult,
                'max_hold_days': max_hold,
                'take_profit_pct': tp,
                'description': desc,
                'count': total_count,
                'win_rate': weighted_wr,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'rrr': avg_rrr,
                'expectancy': avg_exp
            })
    
    # Find best configuration for each country
    print("\n" + "="*100)
    print("[RESULTS] ผลการทดสอบ")
    print("="*100)
    
    for country in ['TH', 'US', 'CN', 'TW']:
        country_results = [r for r in results if r['country'] == country]
        if not country_results:
            continue
        
        print(f"\n[{country}] Market")
        print("-" * 100)
        print(f"{'ATR':<6} {'MaxHold':<8} {'TP%':<6} {'Count':<8} {'WinRate':<8} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6} {'Exp%':<8}")
        print("-" * 100)
        
        for r in country_results:
            tp_str = f"{r['take_profit_pct']:.0f}%" if r['take_profit_pct'] else "None"
            print(f"{r['atr_multiplier']:<6} {r['max_hold_days']:<8} {tp_str:<6} {r['count']:<8} {r['win_rate']:<7.1f}% {r['avg_win']:<9.2f}% {r['avg_loss']:<9.2f}% {r['rrr']:<5.2f} {r['expectancy']:<7.2f}%")
        
        # Find best (RRR > 2.0 and highest expectancy)
        best = None
        for r in country_results:
            if r['rrr'] > 2.0:
                if best is None or r['expectancy'] > best['expectancy']:
                    best = r
        
        if best:
            print(f"\n   ✅ Best: ATR={best['atr_multiplier']}, MaxHold={best['max_hold_days']}, TP={best['take_profit_pct']}%")
            print(f"      RRR={best['rrr']:.2f}, Expectancy={best['expectancy']:.2f}%")
        else:
            # Find best RRR even if < 2.0
            best = max(country_results, key=lambda x: x['rrr'])
            print(f"\n   ⚠️ Best (RRR < 2.0): ATR={best['atr_multiplier']}, MaxHold={best['max_hold_days']}, TP={best['take_profit_pct']}%")
            print(f"      RRR={best['rrr']:.2f}, Expectancy={best['expectancy']:.2f}%")
    
    # Recommended settings
    print("\n" + "="*100)
    print("[RECOMMENDED] ค่าที่แนะนำ")
    print("="*100)
    
    recommendations = {}
    for country in ['TH', 'US', 'CN', 'TW']:
        country_results = [r for r in results if r['country'] == country]
        if not country_results:
            continue
        
        # Find best RRR > 2.0, or best overall
        best = None
        for r in country_results:
            if r['rrr'] > 2.0:
                if best is None or r['expectancy'] > best['expectancy']:
                    best = r
        
        if not best:
            best = max(country_results, key=lambda x: x['rrr'])
        
        recommendations[country] = best
    
    print("\nRecommended Settings:")
    print("-" * 100)
    for country, rec in recommendations.items():
        print(f"\n{country}:")
        print(f"  ATR Multiplier: {rec['atr_multiplier']}")
        print(f"  Max Hold Days: {rec['max_hold_days']}")
        print(f"  Take Profit: {rec['take_profit_pct']}%" if rec['take_profit_pct'] else "  Take Profit: None")
        print(f"  Expected RRR: {rec['rrr']:.2f}")
        print(f"  Expected Expectancy: {rec['expectancy']:.2f}%")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    optimize_parameters()

