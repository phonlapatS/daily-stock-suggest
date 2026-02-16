#!/usr/bin/env python
"""Test Metals 15min backtest and check results"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from scripts.backtest_metals_15m import backtest_metals_15m
import config

# Clear cache and trade history
print("=" * 80)
print("CLEARING CACHE AND TRADE HISTORY")
print("=" * 80)

cache_dir = "data/cache"
log_file = "logs/trade_history_METALS_15M.csv"

if os.path.exists(f"{cache_dir}/OANDA_XAUUSD.csv"):
    os.remove(f"{cache_dir}/OANDA_XAUUSD.csv")
    print("✅ Deleted Gold cache")
if os.path.exists(f"{cache_dir}/OANDA_XAGUSD.csv"):
    os.remove(f"{cache_dir}/OANDA_XAGUSD.csv")
    print("✅ Deleted Silver cache")
if os.path.exists(log_file):
    os.remove(log_file)
    print("✅ Deleted trade history")

# Check config
print("\n" + "=" * 80)
print("CURRENT CONFIG")
print("=" * 80)
gold_conf = config.ASSET_GROUPS.get('GROUP_C2_GOLD_15M', {})
silver_conf = config.ASSET_GROUPS.get('GROUP_D2_SILVER_15M', {})
print(f"Gold 15min: threshold={gold_conf.get('fixed_threshold')}%, engine={gold_conf.get('engine')}")
print(f"Silver 15min: threshold={silver_conf.get('fixed_threshold')}%, engine={silver_conf.get('engine')}")

# Run backtest
print("\n" + "=" * 80)
print("RUNNING BACKTEST")
print("=" * 80)
backtest_metals_15m(n_bars=500, verbose=True)

# Check results
print("\n" + "=" * 80)
print("CHECKING RESULTS")
print("=" * 80)

if os.path.exists(log_file):
    df = pd.read_csv(log_file)
    print(f"Total trades: {len(df)}")
    print(f"\nBy symbol:")
    print(df['symbol'].value_counts())
    
    xauusd = df[df['symbol'] == 'XAUUSD']
    xagusd = df[df['symbol'] == 'XAGUSD']
    
    print(f"\n=== XAUUSD (Gold) ===")
    print(f"Trades: {len(xauusd)}")
    if len(xauusd) > 0:
        correct = xauusd['correct'].sum() if 'correct' in xauusd.columns else 0
        prob = (correct / len(xauusd) * 100) if len(xauusd) > 0 else 0
        wins = xauusd[xauusd['actual_return'] > 0] if 'actual_return' in xauusd.columns else pd.DataFrame()
        losses = xauusd[xauusd['actual_return'] <= 0] if 'actual_return' in xauusd.columns else pd.DataFrame()
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['actual_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"Prob%: {prob:.1f}%")
        print(f"RRR: {rrr:.2f}")
        print(f"AvgWin%: {avg_win*100:.2f}%")
        print(f"AvgLoss%: {avg_loss*100:.2f}%")
        print(f"\nCriteria check:")
        print(f"  Count >= 20: {len(xauusd) >= 20} ({len(xauusd)})")
        print(f"  Prob >= 28%: {prob >= 28.0} ({prob:.1f}%)")
        print(f"  RRR >= 0.75: {rrr >= 0.75} ({rrr:.2f})")
        if len(xauusd) >= 20 and prob >= 28.0 and rrr >= 0.75:
            print("  ✅ PASSES ALL CRITERIA")
        else:
            print("  ❌ DOES NOT PASS CRITERIA")
    else:
        print("  ❌ No trades found")
    
    print(f"\n=== XAGUSD (Silver) ===")
    print(f"Trades: {len(xagusd)}")
    if len(xagusd) > 0:
        correct = xagusd['correct'].sum() if 'correct' in xagusd.columns else 0
        prob = (correct / len(xagusd) * 100) if len(xagusd) > 0 else 0
        wins = xagusd[xagusd['actual_return'] > 0] if 'actual_return' in xagusd.columns else pd.DataFrame()
        losses = xagusd[xagusd['actual_return'] <= 0] if 'actual_return' in xagusd.columns else pd.DataFrame()
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['actual_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"Prob%: {prob:.1f}%")
        print(f"RRR: {rrr:.2f}")
        print(f"AvgWin%: {avg_win*100:.2f}%")
        print(f"AvgLoss%: {avg_loss*100:.2f}%")
        print(f"\nCriteria check:")
        print(f"  Count >= 20: {len(xagusd) >= 20} ({len(xagusd)})")
        print(f"  Prob >= 28%: {prob >= 28.0} ({prob:.1f}%)")
        print(f"  RRR >= 0.75: {rrr >= 0.75} ({rrr:.2f})")
        if len(xagusd) >= 20 and prob >= 28.0 and rrr >= 0.75:
            print("  ✅ PASSES ALL CRITERIA")
        else:
            print("  ❌ DOES NOT PASS CRITERIA")
    else:
        print("  ❌ No trades found")
else:
    print("❌ No trade history file found")

print("\n" + "=" * 80)

