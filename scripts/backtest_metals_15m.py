#!/usr/bin/env python
"""
backtest_metals_15m.py - Backtest Gold/Silver Intraday 15min
=============================================================
Backtest Metals (Gold/Silver) สำหรับ intraday 15min timeframe

Usage:
    python scripts/backtest_metals_15m.py
    python scripts/backtest_metals_15m.py --group GROUP_C2_GOLD_15M
    python scripts/backtest_metals_15m.py --group GROUP_D2_SILVER_15M
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import argparse
from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache
import config

# Import backtest functions
backtest_path = os.path.join(os.path.dirname(__file__), "backtest.py")
if os.path.exists(backtest_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("backtest_module", backtest_path)
    backtest_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backtest_module)
    backtest_single = backtest_module.backtest_single
    save_trade_logs = backtest_module.save_trade_logs
else:
    raise ImportError(f"Cannot find backtest.py at {backtest_path}")

def backtest_metals_15m(group_key=None, n_bars=500, verbose=True):
    """
    Backtest Metals (Gold/Silver) สำหรับ intraday 15min
    
    Args:
        group_key: Group key จาก config (เช่น 'GROUP_C2_GOLD_15M', 'GROUP_D2_SILVER_15M')
                  ถ้า None จะ backtest ทั้ง Gold และ Silver 15min
        n_bars: จำนวน bars สำหรับ testing
        verbose: แสดง output หรือไม่
    """
    tv = TvDatafeed()
    
    # Target groups สำหรับ Metals 15min
    if group_key:
        target_groups = [group_key] if group_key in config.ASSET_GROUPS else []
    else:
        target_groups = [
            "GROUP_C2_GOLD_15M",      # Gold 15min
            "GROUP_D2_SILVER_15M"     # Silver 15min
        ]
    
    if not target_groups:
        print(f"❌ Group '{group_key}' not found in config")
        return
    
    print(f"\n{'='*80}")
    print(f"🔬 METALS INTRADAY 15MIN BACKTEST")
    print(f"{'='*80}")
    print(f"Target Groups: {', '.join(target_groups)}")
    print(f"Test Bars: {n_bars}")
    print(f"{'='*80}\n")
    
    all_trades = []
    
    for group_key in target_groups:
        if group_key not in config.ASSET_GROUPS:
            print(f"⚠️ Group '{group_key}' not found, skipping...")
            continue
            
        group_conf = config.ASSET_GROUPS[group_key]
        interval = group_conf.get('interval', Interval.in_15_minute)
        fixed_threshold = group_conf.get('fixed_threshold', None)
        engine = group_conf.get('engine', 'MEAN_REVERSION')  # Get engine from config
        
        print(f"\n📂 {group_conf.get('description', group_key)}")
        print("-" * 80)
        
        for asset in group_conf.get('assets', []):
            symbol = asset.get('symbol')
            exchange = asset.get('exchange', 'OANDA')
            
            if verbose:
                print(f"\n🔬 Processing {symbol} ({exchange})...")
                print(f"   📊 Config: threshold={fixed_threshold}%, engine={engine}, interval={interval}")
                # Debug: Show expected min_prob and min_stats
                is_silver = 'XAGUSD' in symbol.upper() or 'SILVER' in symbol.upper()
                if is_silver:
                    print(f"   📊 Expected: min_prob=58.0%, min_stats=35 (Silver 15min)")
                else:
                    print(f"   📊 Expected: min_prob=53.0%, min_stats=32 (Gold 15min)")
            
            try:
                # Fetch data with intraday interval
                df = get_data_with_cache(
                    tv=tv,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    full_bars=5000,
                    delta_bars=50
                )
                
                if df is None or len(df) < 500:
                    print(f"   ⚠️ Not enough data: {len(df) if df is not None else 0} bars")
                    continue
                
                if verbose:
                    print(f"   ✅ Loaded {len(df)} bars")
                    print(f"   📅 Date Range: {df.index[0]} → {df.index[-1]}")
                
                # Run backtest with intraday interval
                result = backtest_single(
                    tv=tv,
                    symbol=symbol,
                    exchange=exchange,
                    n_bars=n_bars,
                    verbose=verbose,
                    interval=interval,  # Pass interval to backtest
                    engine=engine,  # Pass engine to backtest (TREND_FOLLOWING for Gold, MEAN_REVERSION for Silver)
                    fixed_threshold=fixed_threshold,  # Pass fixed_threshold in kwargs
                    group=group_key
                )
                
                if result and 'detailed_predictions' in result:
                    trades = result['detailed_predictions']
                    # Add group, symbol, exchange info to trades
                    for trade in trades:
                        trade['group'] = group_key
                        trade['symbol'] = symbol
                        trade['exchange'] = exchange
                    all_trades.extend(trades)
                    
                    if verbose:
                        print(f"   ✅ Generated {len(trades)} trades")
                        if result.get('accuracy'):
                            print(f"   📊 Accuracy: {result['accuracy']:.1f}%")
                            print(f"   📊 RRR: {result.get('risk_reward', 0):.2f}")
                elif result and result.get('total', 0) == 0:
                    if verbose:
                        print(f"   ⚠️ No trades generated (no signals passed filters)")
                
                time.sleep(1)  # Rate limit
                
            except Exception as e:
                print(f"   ❌ Error processing {symbol}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("-" * 80)
    
    # Save all trades
    if all_trades:
        save_trade_logs(all_trades, 'trade_history_METALS_15M.csv')
        print(f"\n💾 Saved Trade Logs: {os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'trade_history_METALS_15M.csv')} ({len(all_trades)} trades)")
    else:
        print("\n⚠️ No trades generated")
    
    print(f"\n✅ Backtest Complete!")
    print(f"   Total Trades: {len(all_trades)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backtest Metals Intraday 15min')
    parser.add_argument('--group', type=str, default=None, help='Specific group to backtest (e.g., GROUP_C2_GOLD_15M)')
    parser.add_argument('--bars', type=int, default=2500, help='Number of bars for testing (default: 2500)')
    parser.add_argument('--verbose', action='store_true', default=True, help='Show verbose output')
    
    args = parser.parse_args()
    
    backtest_metals_15m(group_key=args.group, n_bars=args.bars, verbose=args.verbose)

