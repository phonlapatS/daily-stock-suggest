#!/usr/bin/env python
"""
backtest_metals.py - Backtest Gold/Silver with Fixed Threshold (Sensitivity Test)
==================================================================================
ทดสอบ accuracy ของ pattern matching สำหรับทองคำ/เงิน (Intraday 15m/30m)
ใช้ Fixed Threshold 0.12% ตามที่ปรับปรุงใหม่

Usage:
    python3 scripts/backtest_metals.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval
from core.data_cache import save_cache, load_cache, has_cache
import config

# Fixed Threshold for Metals (Intraday)
FIXED_THRESHOLD = 0.12  # 0.12% per Volatility Scaling Law

def backtest_metal(tv, symbol, exchange, interval, n_test_bars=500, verbose=True):
    """
    Backtest สินทรัพย์เดียว (Gold/Silver) ด้วย Fixed Threshold
    
    Args:
        tv: TvDatafeed instance
        symbol: Symbol name (e.g. XAUUSD)
        exchange: Exchange (e.g. OANDA)
        interval: Interval (15m or 30m)
        n_test_bars: จำนวน test bars
        verbose: แสดง output หรือไม่
    
    Returns:
        dict: ผล backtest
    """
    interval_str = "30m" if interval == Interval.in_30_minute else "15m"
    
    if verbose:
        print(f"\n🔬 BACKTEST: {symbol} ({interval_str})")
        print("=" * 60)
    
    try:
        # Fetch 5000 bars and save to cache
        df = tv.get_hist(symbol=symbol, exchange=exchange, 
                         interval=interval, n_bars=5000)
        
        if df is None or len(df) < 500:
            if verbose:
                print(f"❌ Not enough data for {symbol}")
            return None
        
        # Save to cache for future use
        cache_filename = f"cache/{symbol}_{interval_str}.parquet"
        os.makedirs("cache", exist_ok=True)
        df.to_parquet(cache_filename)
        if verbose:
            print(f"💾 Cached {len(df)} bars to {cache_filename}")
        
        total_bars = len(df)
        
        # Split: 80% Train, 20% Test (or use n_test_bars)
        test_bars = min(n_test_bars, int(total_bars * 0.2))
        train_end = total_bars - test_bars
        
        test_date_from = df.index[train_end].strftime('%Y-%m-%d %H:%M')
        test_date_to = df.index[-1].strftime('%Y-%m-%d %H:%M')
        train_date_from = df.index[0].strftime('%Y-%m-%d %H:%M')
        train_date_to = df.index[train_end-1].strftime('%Y-%m-%d %H:%M')
        
        if verbose:
            print(f"📊 Total: {total_bars} bars")
            print(f"   Train: {train_date_from} → {train_date_to} ({train_end} bars)")
            print(f"   Test:  {test_date_from} → {test_date_to} ({test_bars} bars)")
            print(f"   Fixed Threshold: {FIXED_THRESHOLD}%")
        
        # Calculate returns
        close = df['close']
        pct_change = close.pct_change()
        
        # Fixed Threshold (NOT Dynamic)
        threshold = FIXED_THRESHOLD / 100.0  # Convert to decimal
        
        # Build pattern and test
        correct = 0
        total = 0
        wins = []
        losses = []
        trades = []
        
        for i in range(train_end, total_bars - 1):
            # Build current pattern (last 3-8 bars ending at i)
            pattern_3 = ""
            for j in range(i-2, i+1):
                ret = pct_change.iloc[j]
                if ret > threshold:
                    pattern_3 += "+"
                elif ret < -threshold:
                    pattern_3 += "-"
                else:
                    pattern_3 += "."  # Flat
            
            # Skip if pattern has flat days (less confident)
            if "." in pattern_3:
                continue
            
            # Find pattern in training data
            matches = []
            for k in range(50, train_end - 1):
                hist_pattern = ""
                for m in range(k-2, k+1):
                    ret = pct_change.iloc[m]
                    if ret > threshold:
                        hist_pattern += "+"
                    elif ret < -threshold:
                        hist_pattern += "-"
                    else:
                        hist_pattern += "."
                
                if hist_pattern == pattern_3:
                    # Record next day return
                    next_ret = (close.iloc[k+1] - close.iloc[k]) / close.iloc[k]
                    matches.append(next_ret)
            
            # Need minimum matches
            if len(matches) < 10:
                continue
            
            # Calculate probability
            if pattern_3[-1] == "+":
                # Predicted UP
                up_count = sum(1 for r in matches if r > 0)
                prob = (up_count / len(matches)) * 100
                forecast = "UP"
            else:
                # Predicted DOWN
                down_count = sum(1 for r in matches if r < 0)
                prob = (down_count / len(matches)) * 100
                forecast = "DOWN"
            
            # Only trade high-probability signals
            if prob < 55:
                continue
            
            # Actual result
            actual_ret = (close.iloc[i+1] - close.iloc[i]) / close.iloc[i]
            actual_dir = "UP" if actual_ret > 0 else "DOWN"
            
            is_correct = (forecast == actual_dir)
            total += 1
            if is_correct:
                correct += 1
                wins.append(abs(actual_ret))
            else:
                losses.append(abs(actual_ret))
            
            trades.append({
                'date': df.index[i],
                'symbol': symbol,
                'interval': interval_str,
                'pattern': pattern_3,
                'forecast': forecast,
                'prob': prob,
                'matches': len(matches),
                'actual': actual_dir,
                'pnl': actual_ret * 100,
                'correct': is_correct
            })
        
        # Calculate stats
        if total == 0:
            if verbose:
                print("⚠️ No trades generated (patterns too weak)")
            return None
        
        accuracy = (correct / total) * 100
        avg_win = np.mean(wins) * 100 if wins else 0
        avg_loss = np.mean(losses) * 100 if losses else 0
        rr_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        if verbose:
            print(f"\n📈 RESULTS:")
            print(f"   Total Trades: {total}")
            print(f"   Accuracy:     {accuracy:.1f}%")
            print(f"   Avg Win:      {avg_win:.2f}%")
            print(f"   Avg Loss:     {avg_loss:.2f}%")
            print(f"   RR Ratio:     {rr_ratio:.2f}")
        
        return {
            'symbol': symbol,
            'interval': interval_str,
            'total_trades': total,
            'accuracy': accuracy,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'rr_ratio': rr_ratio,
            'trades': trades
        }
        
    except Exception as e:
        if verbose:
            print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 70)
    print("🔬 METALS BACKTEST (Fixed Threshold 0.12%)")
    print("=" * 70)
    
    # Connect to TradingView
    tv = TvDatafeed()
    
    all_results = []
    all_trades = []
    
    # Test configurations
    assets = [
        {'symbol': 'XAUUSD', 'exchange': 'OANDA', 'name': 'GOLD'},
        {'symbol': 'XAGUSD', 'exchange': 'OANDA', 'name': 'SILVER'},
    ]
    
    intervals = [
        (Interval.in_30_minute, "30m"),
        (Interval.in_15_minute, "15m"),
    ]
    
    for asset in assets:
        for interval, interval_name in intervals:
            print(f"\n{'='*70}")
            result = backtest_metal(
                tv=tv,
                symbol=asset['symbol'],
                exchange=asset['exchange'],
                interval=interval,
                n_test_bars=500,
                verbose=True
            )
            
            if result:
                all_results.append(result)
                all_trades.extend(result['trades'])
            
            time.sleep(1)  # Rate limit
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"{'Asset':<15} {'TF':<8} {'Trades':>8} {'Accuracy':>10} {'Avg Win':>10} {'Avg Loss':>10} {'RR':>8}")
    print("-" * 70)
    
    for r in all_results:
        print(f"{r['symbol']:<15} {r['interval']:<8} {r['total_trades']:>8} {r['accuracy']:>9.1f}% {r['avg_win']:>9.2f}% {r['avg_loss']:>9.2f}% {r['rr_ratio']:>8.2f}")
    
    # Save trades
    if all_trades:
        df_trades = pd.DataFrame(all_trades)
        df_trades.to_csv('logs/metals_backtest.csv', index=False)
        print(f"\n💾 Saved {len(all_trades)} trades to logs/metals_backtest.csv")
    
    print("\n✅ Backtest Complete!")


if __name__ == "__main__":
    main()
