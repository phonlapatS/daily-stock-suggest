#!/usr/bin/env python
"""
backtest_basic.py - Back to Basic: สถิติเพียวๆ
==============================================
Backtest แบบเรียบง่าย ไม่ใช้ risk management, multi-day hold, หรือ trade simulation
เน้นสถิติเพียวๆ: Prob%, RRR, match_count

Usage:
    python scripts/backtest_basic.py --symbol PTT --exchange SET
    python scripts/backtest_basic.py --group THAI
    python scripts/backtest_basic.py --full
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import config
from core.data_cache import get_data_with_cache
from core.pattern_matcher_basic import BasicPatternMatcher
from core.gatekeeper_basic import BasicGatekeeper


def backtest_basic_single(tv, symbol, exchange, n_bars=200, prob_threshold=55.0, min_stats=25, verbose=True):
    """
    Backtest แบบเรียบง่าย - สถิติเพียวๆ
    
    Args:
        tv: TvDatafeed instance
        symbol: Symbol name
        exchange: Exchange name
        n_bars: จำนวน bars สำหรับ testing
        prob_threshold: Prob% ขั้นต่ำ (default: 55.0)
        min_stats: จำนวน match ขั้นต่ำ (default: 25)
        verbose: แสดงผลละเอียดหรือไม่
    
    Returns:
        dict: Results
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"🔬 BASIC BACKTEST: {symbol} ({exchange})")
        print(f"{'='*80}")
    
    # Fetch data
    df = get_data_with_cache(tv, symbol, exchange, Interval.in_daily, full_bars=5000)
    
    if df is None or len(df) < 250:
        if verbose:
            print(f"❌ Not enough data: {len(df) if df is not None else 0} bars")
        return None
    
    # Split train/test
    train_end = len(df) - n_bars
    if train_end < 50:
        if verbose:
            print(f"❌ Not enough training data: {train_end} bars")
        return None
    
    df_train = df.iloc[:train_end].copy()
    df_test = df.iloc[train_end:].copy()
    
    if verbose:
        print(f"📊 Data: {len(df)} bars (Train: {len(df_train)}, Test: {len(df_test)})")
    
    # Initialize Pattern Matcher
    matcher = BasicPatternMatcher(lookback=5000)
    
    # Initialize Gatekeeper (ปรับ criteria ตามประเทศ)
    # China/HK: Prob >= 50%, Min Stats >= 20 (ผ่อนปรนกว่า)
    # อื่นๆ: Prob >= 55%, Min Stats >= 25
    is_china_hk = any(x in exchange.upper() for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN'])
    
    if is_china_hk:
        # China/HK: ใช้ criteria ที่สมดุล (Prob 48%, Min Stats 25)
        # - Prob 48%: เพื่อให้ได้หุ้นมากขึ้น (700: 51.4%, 1211: 49.7%)
        # - Min Stats 25: เพื่อให้ count น่าเชื่อถือขึ้น
        gatekeeper = BasicGatekeeper(
            prob_threshold=48.0,  # ลดจาก 50% เพื่อให้ได้หุ้นมากขึ้น
            min_stats=25  # เพิ่มจาก 20 เพื่อให้ count น่าเชื่อถือขึ้น
        )
    else:
        # อื่นๆ: ใช้ criteria ปกติ (Prob 55%, Min Stats 25)
        gatekeeper = BasicGatekeeper(
            prob_threshold=prob_threshold,
            min_stats=min_stats
        )
    
    # ตรวจสอบว่าเป็นจีน/ฮ่องกงหรือไม่ (ใช้ Volume Ratio filter)
    is_china_hk = any(x in exchange.upper() for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN'])
    
    # Volume Ratio (VR) Filter สำหรับจีน/ฮ่องกง
    if is_china_hk and 'volume' in df_train.columns:
        volume = df_train['volume']
        vol_avg_20 = volume.rolling(20).mean()
        if len(vol_avg_20) > 0 and vol_avg_20.iloc[-1] > 0:
            vr = volume.iloc[-1] / vol_avg_20.iloc[-1]
            
            # Skip dead liquidity zones (VR < 0.5)
            if vr < 0.5:
                if verbose:
                    print(f"❌ Volume Ratio {vr:.2f} < 0.5 (Dead Zone - no liquidity)")
                return None
            
            if verbose:
                print(f"📊 Volume Ratio: {vr:.2f} {'(FOMO_REVERSION)' if vr > 3.0 else ''}")
    
    # Get best pattern from training data (ส่ง exchange เพื่อใช้ threshold ตามประเทศ)
    best_pattern_info = matcher.get_best_pattern(df_train, min_len=3, max_len=8, min_stats=min_stats, exchange=exchange)
    
    if best_pattern_info is None:
        if verbose:
            print(f"❌ No valid pattern found")
        return None
    
    pattern = best_pattern_info['pattern']
    direction = best_pattern_info['direction']
    stats = best_pattern_info['stats']
    
    if verbose:
        print(f"\n📈 Pattern: {pattern} ({direction})")
        print(f"   Prob%: {stats['prob']:.1f}%")
        print(f"   AvgWin%: {stats['avg_win']:.2f}%")
        print(f"   AvgLoss%: {stats['avg_loss']:.2f}%")
        print(f"   RRR: {stats['rrr']:.2f}")
        print(f"   Match Count: {stats['match_count']}")
    
    # Check gatekeeper
    signal = gatekeeper.decide_signal(
        prob=stats['prob'],
        match_count=stats['match_count'],
        direction=direction,
        rrr=stats['rrr']
    )
    
    if verbose:
        print(f"\n🎯 Gatekeeper: {signal['signal']}")
        print(f"   Reason: {signal['reason']}")
    
    # Test on test data (ส่ง exchange เพื่อใช้ threshold ตามประเทศ)
    test_matches = matcher.find_pattern_matches(df_test, pattern, min_len=len(pattern), max_len=len(pattern), exchange=exchange)
    test_stats = matcher.calculate_stats(df_test, test_matches, direction)
    
    if verbose:
        print(f"\n📊 Test Results:")
        print(f"   Test Matches: {len(test_matches)}")
        if test_stats['match_count'] > 0:
            print(f"   Test Prob%: {test_stats['prob']:.1f}%")
            print(f"   Test AvgWin%: {test_stats['avg_win']:.2f}%")
            print(f"   Test AvgLoss%: {test_stats['avg_loss']:.2f}%")
            print(f"   Test RRR: {test_stats['rrr']:.2f}")
    
    # Prepare result
    result = {
        'symbol': symbol,
        'exchange': exchange,
        'pattern': pattern,
        'direction': direction,
        'prob': stats['prob'],
        'avg_win': stats['avg_win'],
        'avg_loss': stats['avg_loss'],
        'rrr': stats['rrr'],
        'match_count': stats['match_count'],
        'signal': signal['signal'],
        'reason': signal['reason'],
        'passed': signal['passed'],
        'test_matches': len(test_matches),
        'test_prob': test_stats['prob'] if test_stats['match_count'] > 0 else 0.0,
        'test_rrr': test_stats['rrr'] if test_stats['match_count'] > 0 else 0.0
    }
    
    return result


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Basic Backtest - สถิติเพียวๆ')
    parser.add_argument('--symbol', type=str, help='Symbol name')
    parser.add_argument('--exchange', type=str, help='Exchange name')
    parser.add_argument('--group', type=str, help='Asset group (THAI, US, CHINA, TAIWAN)')
    parser.add_argument('--full', action='store_true', help='Full scan all groups')
    parser.add_argument('--bars', type=int, default=200, help='Test bars (default: 200, total data: 5000 bars)')
    parser.add_argument('--prob', type=float, default=55.0, help='Prob threshold (default: 55.0)')
    parser.add_argument('--min_stats', type=int, default=25, help='Min stats (default: 25)')
    parser.add_argument('--verbose', action='store_true', default=True, help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize TvDatafeed
    tv = TvDatafeed()
    
    results = []
    
    if args.symbol and args.exchange:
        # Single symbol
        result = backtest_basic_single(
            tv, args.symbol, args.exchange,
            n_bars=args.bars,
            prob_threshold=args.prob,
            min_stats=args.min_stats,
            verbose=args.verbose
        )
        if result:
            results.append(result)
    elif args.group:
        # Group
        group_name = f"GROUP_{args.group[0]}_{args.group[1:]}"
        if group_name in config.ASSET_GROUPS:
            group_config = config.ASSET_GROUPS[group_name]
            assets = group_config['assets']
            
            print(f"\n{'='*80}")
            print(f"🔬 BASIC BACKTEST: {group_config['description']}")
            print(f"{'='*80}")
            
            for asset in assets:
                symbol = asset['symbol']
                exchange = asset['exchange']
                
                result = backtest_basic_single(
                    tv, symbol, exchange,
                    n_bars=args.bars,
                    prob_threshold=args.prob,
                    min_stats=args.min_stats,
                    verbose=args.verbose
                )
                if result:
                    results.append(result)
        else:
            print(f"❌ Group not found: {group_name}")
    elif args.full:
        # Full scan
        print(f"\n{'='*80}")
        print(f"🔬 BASIC BACKTEST: FULL SCAN")
        print(f"{'='*80}")
        print(f"📊 Test Bars: {args.bars} (Total: 5000 bars)")
        print(f"🎯 Prob Threshold: {args.prob}%")
        print(f"📈 Min Stats: {args.min_stats}")
        print(f"{'='*80}")
        
        for group_name, group_config in config.ASSET_GROUPS.items():
            # รันเฉพาะหุ้นรายวัน (THAI, US, CHINA/HK, TAIWAN)
            # ข้าม METALS (GOLD, SILVER) เพราะเป็น intraday
            if ('THAI' in group_name or 'US' in group_name or 'CHINA' in group_name or 'TAIWAN' in group_name) and \
               'GOLD' not in group_name and 'SILVER' not in group_name:
                assets = group_config['assets']
                
                print(f"\n📂 {group_config['description']} ({len(assets)} symbols)")
                print("-" * 80)
                
                # รันทุกหุ้น (ไม่จำกัด)
                for idx, asset in enumerate(assets, 1):
                    symbol = asset['symbol']
                    exchange = asset['exchange']
                    
                    result = backtest_basic_single(
                        tv, symbol, exchange,
                        n_bars=args.bars,
                        prob_threshold=args.prob,
                        min_stats=args.min_stats,
                        verbose=False
                    )
                    if result:
                        results.append(result)
                        status = "✅" if result['passed'] else "❌"
                        print(f"{status} [{idx}/{len(assets)}] {symbol}: {result['signal']} (Prob: {result['prob']:.1f}%, RRR: {result['rrr']:.2f}, Matches: {result['match_count']})")
                    else:
                        print(f"⏭️  [{idx}/{len(assets)}] {symbol}: No pattern found")
    else:
        parser.print_help()
        return
    
    # Summary
    if results:
        print(f"\n{'='*80}")
        print(f"📊 SUMMARY")
        print(f"{'='*80}")
        
        df_results = pd.DataFrame(results)
        
        passed = df_results[df_results['passed'] == True]
        no_trade = df_results[df_results['passed'] == False]
        
        print(f"\n✅ Passed: {len(passed)}")
        print(f"❌ No-Trade: {len(no_trade)}")
        
        if len(passed) > 0:
            print(f"\n📈 Passed Stats:")
            print(f"   Avg Prob%: {passed['prob'].mean():.1f}%")
            print(f"   Avg RRR: {passed['rrr'].mean():.2f}")
            print(f"   Avg Match Count: {passed['match_count'].mean():.0f}")
        
        # Save to CSV
        output_file = 'data/basic_backtest_results.csv'
        df_results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 Saved to: {output_file}")


if __name__ == '__main__':
    main()

