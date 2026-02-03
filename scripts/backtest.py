#!/usr/bin/env python
"""
backtest.py - Backtest Pattern Accuracy
========================================
ทดสอบ accuracy ของ pattern matching ด้วย historical data
ไม่ต้องรอผลจริง - ใช้ข้อมูลในอดีตมาทดสอบทันที

Usage:
    python scripts/backtest.py                    # ทุกหุ้น (จาก config.py)
    python scripts/backtest.py PTT SET            # หุ้นเดียว
    python scripts/backtest.py NVDA NASDAQ 300    # ระบุ test bars
    python scripts/backtest.py --quick            # ทดสอบ 4 หุ้นหลัก
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import config


def backtest_single(tv, symbol, exchange, n_bars=200, threshold_multiplier=1.25, min_stats=30, verbose=True):
    """
    Backtest หุ้นเดียว พร้อมแสดงช่วงวันที่
    
    Returns:
        dict: ผล backtest รวมถึง date_from, date_to
    """
    if verbose:
        print(f"\n🔬 BACKTEST: {symbol} ({exchange})")
        print("=" * 50)
    
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, 
                         interval=Interval.in_daily, n_bars=5000)
        
        if df is None or len(df) < 1000:
            if verbose:
                print(f"❌ Not enough data for {symbol}")
            return None
        
        # Get date range
        total_bars = len(df)
        
        # Adjust n_bars if total history is small
        # We need at least some data for training "Pattern Stats"
        # Let's say we want at least 50% for training if history is short
        if n_bars >= total_bars * 0.8:
            n_bars = int(total_bars * 0.3) # Fallback to 30% test set
            if verbose:
                print(f"⚠️ Adjusted test bars to {n_bars} (limited history)")
        
        train_end = total_bars - n_bars
        
        if train_end < 100:
            if verbose:
                print(f"❌ Not enough training data (Train: {train_end} bars)")
            return None
        
        test_date_from = df.index[train_end].strftime('%Y-%m-%d')
        test_date_to = df.index[-1].strftime('%Y-%m-%d')
        train_date_from = df.index[0].strftime('%Y-%m-%d')
        train_date_to = df.index[train_end-1].strftime('%Y-%m-%d')
        
        if verbose:
            print(f"📊 Total: {len(df)} bars")
            print(f"   Train: {train_date_from} → {train_date_to} ({train_end} bars)")
            print(f"   Test:  {test_date_from} → {test_date_to} ({n_bars} bars)")
        
        # Calculate returns and threshold
        close = df['close']
        pct_change = close.pct_change()
        
        # Rolling volatility
        short_std = pct_change.rolling(20).std()
        long_std = pct_change.rolling(252).std()
        effective_std = np.maximum(short_std, long_std.fillna(0) * 0.5)
        threshold = effective_std * threshold_multiplier
        
        # Convert to +/- pattern
        patterns = []
        for i in range(len(pct_change)):
            if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
                patterns.append('')
            elif pct_change.iloc[i] > threshold.iloc[i]:
                patterns.append('+')
            elif pct_change.iloc[i] < -threshold.iloc[i]:
                patterns.append('-')
            else:
                patterns.append('')
        
        # Build pattern stats from Training data
        pattern_stats = {}
        
        for i in range(10, train_end - 1):
            pat = ''.join(patterns[i-3:i+1])
            if len(pat) < 2:
                continue
            
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            if pat not in pattern_stats:
                pattern_stats[pat] = {'up': 0, 'down': 0}
            
            if next_ret > 0:
                pattern_stats[pat]['up'] += 1
            else:
                pattern_stats[pat]['down'] += 1
        
        if verbose:
            print(f"   Patterns found: {len(pattern_stats)}")
        
        # Test on Test data
        total_predictions = 0
        correct_predictions = 0
        predictions = []
        
        for i in range(train_end, len(df) - 1):
            pat = ''.join(patterns[i-3:i+1])
            if len(pat) < 2 or pat not in pattern_stats:
                continue
            
            stats = pattern_stats[pat]
            total = stats['up'] + stats['down']
            
            if total < min_stats:
                continue
            
            if stats['up'] > stats['down']:
                forecast = 'UP'
                prob = stats['up'] / total * 100
            else:
                forecast = 'DOWN'
                prob = stats['down'] / total * 100
            
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            actual = 'UP' if next_ret > 0 else 'DOWN'
            is_correct = 1 if forecast == actual else 0
            
            # Calculate actual return percentage (needed for RR analysis)
            # next_ret is a float (e.g., 0.015 for 1.5%), convert to percentage
            actual = 'UP' if next_ret > 0 else 'DOWN'
            is_correct = 1 if forecast == actual else 0
            
            # Calculate actual return percentage (needed for RR analysis)
            # next_ret is a float (e.g., 0.015 for 1.5%), convert to percentage
            actual_return_pct = next_ret * 100 

            total_predictions += 1
            correct_predictions += is_correct
            
            predictions.append({
                'date': df.index[i],
                'pattern': pat,
                'forecast': forecast,
                'prob': prob,
                'actual': actual,
                'actual_return': actual_return_pct, # Added for metrics analysis
                'correct': is_correct
            })
        
        if total_predictions == 0:
            if verbose:
                print("❌ No forecasts (no patterns met min_stats threshold)")
            return None
        
        accuracy = correct_predictions / total_predictions * 100
        
        if verbose:
            print(f"\n📊 RESULTS")
            print("-" * 50)
            print(f"   Forecasts: {total_predictions}")
            print(f"   Correct:   {correct_predictions}")
            print(f"   Accuracy:  {accuracy:.1f}%")
            
            # Detailed breakdown by pattern
            df_pred = pd.DataFrame(predictions)
            print(f"\n📈 Forecast Breakdown:")
            print(f"   {'Pattern':<8} {'Forecast':<10} {'Count':<8} {'Correct':<8} {'Acc%':<8}")
            print("   " + "-" * 45)
            
            by_pattern = df_pred.groupby(['pattern', 'forecast']).agg({
                'correct': ['sum', 'count']
            }).reset_index()
            by_pattern.columns = ['pattern', 'forecast', 'correct', 'count']
            by_pattern['acc'] = (by_pattern['correct'] / by_pattern['count'] * 100).round(1)
            by_pattern = by_pattern.sort_values('count', ascending=False)
            
            for _, row in by_pattern.head(10).iterrows():
                icon = "🟢" if row['forecast'] == 'UP' else "🔴"
                print(f"   {row['pattern']:<8} {icon} {row['forecast']:<7} {int(row['count']):<8} {int(row['correct']):<8} {row['acc']:.1f}%")
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'total': total_predictions,
            'correct': correct_predictions,
            'accuracy': round(accuracy, 1),
            'test_date_from': test_date_from,
            'test_date_to': test_date_to,
            'test_bars': n_bars,
            'patterns_tested': len(pattern_stats),
            'detailed_predictions': predictions  # Added for export
        }
        
    except Exception as e:
        if verbose:
            print(f"❌ Error: {e}")
        return None


def backtest_all(n_bars=200, skip_intraday=True, full_scan=False):
    """
    Backtest ทุกหุ้นจาก config.py
    
    Args:
        n_bars: จำนวน test bars
        skip_intraday: ข้าม intraday (Gold/Silver) ไหม
        full_scan: If True, test ALL assets (no limit)
    """
    print("\n" + "=" * 70)
    print("🔬 BACKTEST ALL STOCKS")
    print("=" * 70)
    print(f"Test Period: {n_bars} bars ล่าสุด")
    print(f"Mode: {'FULL SCAN (200+ Assets)' if full_scan else 'SAMPLE SCAN (10 per group)'}")
    print("=" * 70)
    
    tv = TvDatafeed()
    
    all_results = []
    all_trades = [] # Initialize logs list
    
    for group_name, group_config in config.ASSET_GROUPS.items():
        # Skip intraday
        if skip_intraday and 'METALS' in group_name:
            print(f"\n⏭️ Skipping {group_name} (intraday)")
            continue
        
        print(f"\n📂 {group_config['description']}")
        print("-" * 50)
        
        assets = group_config['assets']
        
        # Limit to 10 unless full_scan is True
        target_assets = assets if full_scan else assets[:10]
        
        for i, asset in enumerate(target_assets):  
            symbol = asset['symbol']
            exchange = asset['exchange']
            
            print(f"   [{i+1}/{len(target_assets)}] {symbol}...", end=" ")
            
            result = backtest_single(tv, symbol, exchange, n_bars=n_bars, verbose=True)
            
            if result:
                result['group'] = group_name
                all_results.append(result)
                print(f"✅ {result['accuracy']:.1f}%")
                
                # Collect detailed trades for metrics analysis
                if 'detailed_predictions' in result:
                    for trade in result['detailed_predictions']:
                        trade['symbol'] = symbol
                        trade['exchange'] = exchange
                        trade['group'] = group_name
                        all_trades.append(trade)
            else:
                print("❌")
            
            time.sleep(0.3)  # Rate limit
            
    # Save Trade Logs to CSV (Phase 1.6: Advanced Filtering)
    if all_trades:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'trade_history.csv')
        
        df_trades = pd.DataFrame(all_trades)
        # Reorder columns for readability
        cols = ['date', 'symbol', 'group', 'pattern', 'forecast', 'prob', 'actual', 'actual_return', 'correct']
        df_trades = df_trades[cols]
        
        df_trades.to_csv(log_path, index=False)
        print(f"\n💾 Saved Trade Logs: {log_path} ({len(df_trades)} trades)")
        log_path = os.path.join(log_dir, 'trade_history.csv')
        
        df_trades = pd.DataFrame(all_trades)
        # Reorder columns for readability
        cols = ['date', 'symbol', 'group', 'pattern', 'forecast', 'prob', 'actual', 'actual_return', 'correct']
        df_trades = df_trades[cols]
        
        df_trades.to_csv(log_path, index=False)
        print(f"\n💾 Saved Trade Logs: {log_path} ({len(df_trades)} trades)")
    
    # Summary
    if all_results:
        print("\n" + "=" * 70)
        print("📊 BACKTEST SUMMARY")
        print("=" * 70)
        
        df = pd.DataFrame(all_results)
        
        # Date range
        print(f"\n📅 Test Period: {df['test_date_from'].min()} → {df['test_date_to'].max()}")
        print(f"   ({n_bars} bars per stock)")
        
        # Overall
        total_preds = df['total'].sum()
        total_correct = df['correct'].sum()
        avg_accuracy = total_correct / total_preds * 100 if total_preds > 0 else 0
        
        print(f"\n🎯 Overall Accuracy: {avg_accuracy:.1f}%")
        print(f"   Total Predictions: {total_preds}")
        print(f"   Correct: {total_correct}")
        
        # Best & Worst
        print(f"\n📈 Top 5 Best:")
        top5 = df.nlargest(5, 'accuracy')
        for _, r in top5.iterrows():
            print(f"   {r['symbol']:<10} {r['accuracy']:.1f}% ({r['total']} predictions)")
        
        print(f"\n📉 Bottom 5:")
        bottom5 = df.nsmallest(5, 'accuracy')
        for _, r in bottom5.iterrows():
            print(f"   {r['symbol']:<10} {r['accuracy']:.1f}% ({r['total']} predictions)")
        
        # By group
        print(f"\n📊 By Group:")
        by_group = df.groupby('group').agg({
            'total': 'sum',
            'correct': 'sum',
            'accuracy': 'mean'
        }).reset_index()
        by_group['calc_accuracy'] = (by_group['correct'] / by_group['total'] * 100).round(1)
        
        for _, row in by_group.iterrows():
            print(f"   {row['group']:<20} {row['calc_accuracy']:.1f}%")
        
        return df
    
    return None


def main():
    print("\n" + "=" * 70)
    print("🔬 PATTERN MATCHING BACKTEST")
    print("=" * 70)
    print("ทดสอบ accuracy ด้วย historical data (ไม่ต้องรอผลจริง)")
    print("=" * 70)
    
    n_bars = 200  # Default
    
    # Parse arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--full':
            # NEW: Full Scan Mode
            if len(sys.argv) >= 3:
                n_bars = int(sys.argv[2])
            backtest_all(n_bars=n_bars, full_scan=True)
            
        elif sys.argv[1] == '--all':
            # Backtest all stocks (Sample 10)
            if len(sys.argv) >= 3:
                n_bars = int(sys.argv[2])
            backtest_all(n_bars=n_bars, full_scan=False)
            
        elif sys.argv[1] == '--quick':
            # Quick test with 4 stocks
            default_stocks = [
                ('PTT', 'SET'),
                ('ADVANC', 'SET'),
                ('NVDA', 'NASDAQ'),
                ('AAPL', 'NASDAQ'),
            ]
            if len(sys.argv) >= 3:
                n_bars = int(sys.argv[2])
            
            print(f"\nQuick test: {len(default_stocks)} stocks, {n_bars} test bars each")
            
            tv = TvDatafeed()
            results = []
            all_trades = [] # Initialize here
            
            for symbol, exchange in default_stocks:
                result = backtest_single(tv, symbol, exchange, n_bars=n_bars)
                if result:
                    results.append(result)
                    if 'detailed_predictions' in result:
                        for trade in result['detailed_predictions']:
                            trade['symbol'] = symbol
                            trade['exchange'] = exchange
                            trade['group'] = 'QUICK_TEST'
                            all_trades.append(trade)
            
            # Save Trade Logs to CSV (Quick Mode)
            if all_trades:
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, 'trade_history.csv')
                
                df_trades = pd.DataFrame(all_trades)
                cols = ['date', 'symbol', 'group', 'pattern', 'forecast', 'prob', 'actual', 'actual_return', 'correct']
                df_trades = df_trades[cols]
                
                df_trades.to_csv(log_path, index=False)
                print(f"\n💾 Saved Trade Logs: {log_path} ({len(df_trades)} trades)")
                
            if results:
                print("\n" + "=" * 60)
                print("📊 SUMMARY")
                print("=" * 60)
                
                print(f"\n📅 Test Period: {results[0]['test_date_from']} → {results[0]['test_date_to']}")
                
                total_preds = sum(r['total'] for r in results)
                total_correct = sum(r['correct'] for r in results)
                avg_accuracy = total_correct / total_preds * 100 if total_preds > 0 else 0
                
                print(f"\n{'Symbol':<12} {'Exchange':<10} {'Total':<10} {'Correct':<10} {'Accuracy':<10}")
                print("-" * 60)
                for r in results:
                    print(f"{r['symbol']:<12} {r['exchange']:<10} {r['total']:<10} {r['correct']:<10} {r['accuracy']:.1f}%")
                print("-" * 60)
                print(f"{'TOTAL':<12} {'':<10} {total_preds:<10} {total_correct:<10} {avg_accuracy:.1f}%")
                
        else:
            # Single stock
            symbol = sys.argv[1]
            exchange = sys.argv[2] if len(sys.argv) >= 3 else 'SET'
            if len(sys.argv) >= 4:
                n_bars = int(sys.argv[3])
            
            tv = TvDatafeed()
            backtest_single(tv, symbol, exchange, n_bars=n_bars)
    
    else:
        # Default: show help
        print("\nUsage:")
        print("  python scripts/backtest.py PTT SET           # หุ้นเดียว")
        print("  python scripts/backtest.py NVDA NASDAQ 300   # ระบุ test bars")
        print("  python scripts/backtest.py --quick           # 4 หุ้นหลัก")
        print("  python scripts/backtest.py --all             # ทุกหุ้น (ช้า)")
        print("  python scripts/backtest.py --all 100         # ทุกหุ้น, 100 bars")
    
    print("\n" + "=" * 70)
    print("✅ Backtest Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
