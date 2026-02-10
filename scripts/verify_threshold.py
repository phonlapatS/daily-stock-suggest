#!/usr/bin/env python
"""
verify_threshold.py - Verify Threshold Configuration for Each Group
====================================================================
ทดสอบว่า Threshold ที่ตั้งไว้ทำงานได้ดีจริงหรือไม่

Usage:
    python scripts/verify_threshold.py GROUP_C1_GOLD_30M
    python scripts/verify_threshold.py GROUP_B_US
    python scripts/verify_threshold.py all  # ทดสอบทั้งหมด (นาน)
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from tvDatafeed import TvDatafeed, Interval

# Results file
RESULTS_FILE = "logs/threshold_verification_results.json"


def backtest_asset(df, threshold_pct, n_test_bars=5000):
    """Backtest single asset with given threshold (Fixed or Dynamic)"""
    if df is None or len(df) < 1000:
        return None
    
    total_bars = len(df)
    # Remove 20% limit to allow full backtest if requested
    test_bars = n_test_bars if n_test_bars < total_bars else total_bars - 100
    train_end = total_bars - test_bars
    if train_end < 50: train_end = 50 # Ensure minimum history
    
    close = df['close']
    pct_change = close.pct_change()
    
    # Threshold Logic
    if threshold_pct == 'Dynamic':
        # Replicate processor.py Dynamic Logic
        short_term_std = pct_change.rolling(window=20).std()
        long_term_std = pct_change.rolling(window=252).std()
        long_term_floor = long_term_std * 0.50
        effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
        effective_std = effective_std.fillna(short_term_std)
        threshold_series = effective_std * 1.25
        is_dynamic = True
    else:
        # Fixed Threshold
        fixed_val = float(threshold_pct) / 100.0
        threshold_series = pd.Series(fixed_val, index=pct_change.index)
        is_dynamic = False
    
    correct, total = 0, 0
    wins, losses = [], []
    
    # Progress tracking for large N
    start_time = time.time()
    
    for i in range(train_end, total_bars - 1):
        if (i - train_end) % 500 == 0 and (i - train_end) > 0:
            elapsed = time.time() - start_time
            print(f"    ... processed {i - train_end}/{test_bars} bars ({elapsed:.1f}s)")
            
        # Determine threshold for current bar (and history)
        # Note: In real-time, threshold changes every bar. 
        # For simplicity in fixed mode, it's constant.
        # In dynamic mode, we use the threshold at time j.
        
        # Build Pattern
        pattern = ''
        for j in range(i-2, i+1):
            thresh = threshold_series.iloc[j]
            change = pct_change.iloc[j]
            if change > thresh: pattern += '+'
            elif change < -thresh: pattern += '-'
            else: pattern += '.'
            
        if '.' in pattern:
            continue
        
        # Find matches in Expanding Window (Walk-Forward)
        # Search from start of data up to current bar 'i'
        matches = []
        
        # Optimization: Scan only necessary range?
        # For comprehensive test, scan 50 to i-1
        for k in range(50, i - 1):
            hist_pattern = ''
            for m in range(k-2, k+1):
                thresh = threshold_series.iloc[m] # Use historical threshold
                change = pct_change.iloc[m]
                if change > thresh: hist_pattern += '+'
                elif change < -thresh: hist_pattern += '-'
                else: hist_pattern += '.'
            
            if hist_pattern == pattern:
                matches.append((close.iloc[k+1] - close.iloc[k]) / close.iloc[k])
        
        if len(matches) < 10:
            continue
        
        # Probability
        if pattern[-1] == '+':
            prob = sum(1 for r in matches if r > 0) / len(matches) * 100
            forecast = 'UP'
        else:
            prob = sum(1 for r in matches if r < 0) / len(matches) * 100
            forecast = 'DOWN'
        
        if prob < 55:
            continue
        
        # Actual
        actual_ret = (close.iloc[i+1] - close.iloc[i]) / close.iloc[i]
        actual_dir = 'UP' if actual_ret > 0 else 'DOWN'
        
        total += 1
        if forecast == actual_dir:
            correct += 1
            wins.append(abs(actual_ret))
        else:
            losses.append(abs(actual_ret))
    
    if total == 0:
        return None
    
    accuracy = correct / total * 100
    avg_win = np.mean(wins) * 100 if wins else 0
    avg_loss = np.mean(losses) * 100 if losses else 0
    rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    expectancy = (accuracy/100 * avg_win) - ((1 - accuracy/100) * avg_loss)
    
    return {
        'trades': total,
        'test_bars': test_bars,
        'accuracy': round(accuracy, 1),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'rr_ratio': round(rr_ratio, 2),
        'expectancy': round(expectancy, 3)
    }


def verify_group(group_name, tv=None, threshold_override=None):
    """Verify threshold for a specific group"""
    if group_name not in config.ASSET_GROUPS:
        print(f"❌ Group '{group_name}' not found")
        return None
    
    settings = config.ASSET_GROUPS[group_name]
    
    if threshold_override:
        threshold = threshold_override
    else:
        threshold = settings.get('fixed_threshold')
    
    assets = settings.get('assets', [])
    interval = settings.get('interval', Interval.in_daily)
    
    if threshold is None:
        threshold = 'Dynamic'
    
    print(f"\n{'='*60}")
    print(f"VERIFYING: {group_name}")
    print(f"Threshold: {threshold}{'%' if threshold != 'Dynamic' else ''} | Assets: {len(assets)}")
    print(f"{'='*60}")
    
    if tv is None:
        tv = TvDatafeed()
    
    all_results = []
    
    for asset in assets[:5]:  # Limit to first 5 for speed
        symbol = asset.get('symbol') if isinstance(asset, dict) else asset
        exchange = asset.get('exchange', 'SET') if isinstance(asset, dict) else 'SET'
        name = asset.get('name', symbol) if isinstance(asset, dict) else symbol
        
        try:
            # Load from cache first
            cache_path = f"data/cache/{exchange}_{symbol}.csv"
            if os.path.exists(cache_path):
                df = pd.read_csv(cache_path, parse_dates=['datetime'])
                df.set_index('datetime', inplace=True)
            else:
                df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=5000)
            
            result = backtest_asset(df, threshold, n_test_bars=5000)
            
            if result:
                result['symbol'] = name
                all_results.append(result)
                status = "✅" if result['expectancy'] > 0 else "❌"
                print(f"  {status} {name:<12} | Trades: {result['trades']:>4} | "
                      f"Acc: {result['accuracy']:>5.1f}% | RR: {result['rr_ratio']:>5.2f} | "
                      f"Exp: {result['expectancy']:>6.3f}% | Bars: {result['test_bars']}")
            else:
                print(f"  ⚠️  {name:<12} | No trades generated")
                
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ {name:<12} | Error: {str(e)[:30]}")
    
    # Summary
    if all_results:
        avg_trades = np.mean([r['trades'] for r in all_results])
        avg_accuracy = np.mean([r['accuracy'] for r in all_results])
        avg_rr = np.mean([r['rr_ratio'] for r in all_results])
        avg_exp = np.mean([r['expectancy'] for r in all_results])
        avg_bars = np.mean([r.get('test_bars', 0) for r in all_results])
        
        print(f"\n📊 GROUP SUMMARY:")
        print(f"   Avg Trades: {avg_trades:.0f}")
        print(f"   Avg Accuracy: {avg_accuracy:.1f}%")
        print(f"   Avg RR: {avg_rr:.2f}")
        print(f"   Avg Expectancy: {avg_exp:.3f}%")
        print(f"   Avg Bars: {avg_bars:.0f}")
        
        verdict = "PASS ✅" if avg_exp > 0 else "FAIL ❌"
        print(f"   VERDICT: {verdict}")
        
        return {
            'group': group_name,
            'threshold': threshold,
            'assets_tested': len(all_results),
            'avg_trades': round(avg_trades, 0),
            'avg_accuracy': round(avg_accuracy, 1),
            'avg_rr': round(avg_rr, 2),
            'avg_expectancy': round(avg_exp, 3),
            'avg_bars': int(avg_bars),
            'verdict': 'PASS' if avg_exp > 0 else 'FAIL',
            'tested_at': datetime.now().isoformat()
        }
    
    return None


def load_results():
    """Load existing results"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_results(results):
    """Save results to file"""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)


def print_summary_table(results):
    """Print summary table of all results"""
    print("\n" + "="*90)
    print("THRESHOLD VERIFICATION SUMMARY TABLE")
    print("="*90)
    print(f"{'Group':<25} {'Threshold':<12} {'Bars':<8} {'Assets':<8} {'Acc':<8} {'RR':<8} {'Exp':<10} {'Verdict'}")
    print("-"*90)
    
    for group, data in sorted(results.items()):
        if data.get('status') == 'SKIPPED':
            print(f"{group:<25} {'Dynamic':<12} {'-':<8} {'-':<8} {'-':<8} {'-':<8} {'-':<10} {'SKIP'}")
        else:
            print(f"{group:<25} {str(data.get('threshold','?'))+'%':<12} "
                  f"{str(data.get('avg_bars','?')):<8} "
                  f"{data.get('assets_tested',0):<8} "
                  f"{str(data.get('avg_accuracy','?'))+'%':<8} "
                  f"{data.get('avg_rr','?'):<8} "
                  f"{str(data.get('avg_expectancy','?'))+'%':<10} "
                  f"{data.get('verdict','?')}")
    
    print("="*90)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_threshold.py <GROUP_NAME or 'all'> [THRESHOLD_OVERRIDE]")
        print("\nAvailable groups:")
        for name in config.ASSET_GROUPS.keys():
            print(f"  - {name}")
        return
    
    target = sys.argv[1]
    threshold_override = sys.argv[2] if len(sys.argv) >= 3 else None
    
    results = load_results()
    tv = TvDatafeed()
    
    if target.lower() == 'all':
        for group_name in config.ASSET_GROUPS.keys():
            result = verify_group(group_name, tv, threshold_override)
            if result:
                results[group_name] = result
                save_results(results)
    else:
        result = verify_group(target, tv, threshold_override)
        if result:
            results[target] = result
            save_results(results)
    
    print_summary_table(results)
    print(f"\n💾 Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
