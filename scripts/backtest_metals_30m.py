#!/usr/bin/env python
"""
backtest_metals_30m.py - Backtest Gold/Silver Intraday 30min
=============================================================
Backtest Metals (Gold/Silver) สำหรับ intraday 30min timeframe

Usage:
    python scripts/backtest_metals_30m.py
    python scripts/backtest_metals_30m.py --group GROUP_C1_GOLD_30M
    python scripts/backtest_metals_30m.py --group GROUP_D1_SILVER_30M
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
# Import from backtest.py in the same directory
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

def backtest_metals_30m(group_key=None, n_bars=500, verbose=True):
    """
    Backtest Metals (Gold/Silver) สำหรับ intraday 30min
    
    Args:
        group_key: Group key จาก config (เช่น 'GROUP_C1_GOLD_30M', 'GROUP_D1_SILVER_30M')
                  ถ้า None จะ backtest ทั้ง Gold และ Silver 30min
        n_bars: จำนวน bars สำหรับ testing
        verbose: แสดง output หรือไม่
    """
    tv = TvDatafeed()
    
    # Target groups สำหรับ Metals 30min
    if group_key:
        target_groups = [group_key] if group_key in config.ASSET_GROUPS else []
    else:
        target_groups = [
            "GROUP_C1_GOLD_30M",      # Gold 30min
            "GROUP_D1_SILVER_30M"     # Silver 30min
        ]
    
    if not target_groups:
        print(f"❌ Group '{group_key}' not found in config")
        return
    
    print(f"\n{'='*80}")
    print(f"🔬 METALS INTRADAY 30MIN BACKTEST")
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
        interval = group_conf.get('interval', Interval.in_30_minute)
        fixed_threshold = group_conf.get('fixed_threshold', None)
        engine = group_conf.get('engine', 'MEAN_REVERSION')  # Get engine from config
        
        print(f"\n📂 {group_conf.get('description', group_key)}")
        print("-" * 80)
        
        for asset in group_conf.get('assets', []):
            symbol = asset.get('symbol')
            exchange = asset.get('exchange', 'OANDA')
            
            if verbose:
                print(f"\n🔬 Processing {symbol} ({exchange})...")
            
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
        save_trade_logs(all_trades, 'trade_history_METALS.csv')
        print(f"\n✅ Backtest Complete!")
        print(f"   Total Trades: {len(all_trades)}")
    else:
        print(f"\n⚠️ No trades generated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backtest Metals Intraday 30min')
    parser.add_argument('--group', type=str, default=None,
                       help='Group key to backtest (e.g., GROUP_C1_GOLD_30M, GROUP_D1_SILVER_30M)')
    parser.add_argument('--bars', type=int, default=500,
                       help='Number of test bars (default: 500)')
    parser.add_argument('--quiet', action='store_true',
                       help='Quiet mode (less output)')
    
    args = parser.parse_args()
    
    backtest_metals_30m(
        group_key=args.group,
        n_bars=args.bars,
        verbose=not args.quiet
    )

