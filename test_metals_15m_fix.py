#!/usr/bin/env python
"""Test and fix Metals 15min - Check why values don't change"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
import config

print("=" * 80)
print("CHECKING CURRENT STATE")
print("=" * 80)

# Check config
gold_conf = config.ASSET_GROUPS.get('GROUP_C2_GOLD_15M', {})
silver_conf = config.ASSET_GROUPS.get('GROUP_D2_SILVER_15M', {})
print(f"\nGold 15min config:")
print(f"  threshold: {gold_conf.get('fixed_threshold')}%")
print(f"  engine: {gold_conf.get('engine')}")
print(f"\nSilver 15min config:")
print(f"  threshold: {silver_conf.get('fixed_threshold')}%")
print(f"  engine: {silver_conf.get('engine')}")

# Check trade history
file_path = 'logs/trade_history_METALS_15M.csv'
if os.path.exists(file_path):
    mtime = os.path.getmtime(file_path)
    print(f"\nTrade history file exists")
    print(f"  Last modified: {datetime.fromtimestamp(mtime)}")
    
    df = pd.read_csv(file_path)
    print(f"  Total trades: {len(df)}")
    print(f"\n  By symbol:")
    print(df['symbol'].value_counts())
    
    xauusd = df[df['symbol'] == 'XAUUSD']
    xagusd = df[df['symbol'] == 'XAGUSD']
    
    print(f"\n  === XAUUSD ===")
    print(f"  Trades: {len(xauusd)}")
    if len(xauusd) > 0:
        correct = xauusd['correct'].sum() if 'correct' in xauusd.columns else 0
        prob = (correct / len(xauusd) * 100) if len(xauusd) > 0 else 0
        wins = xauusd[xauusd['actual_return'] > 0] if 'actual_return' in xauusd.columns else pd.DataFrame()
        losses = xauusd[xauusd['actual_return'] <= 0] if 'actual_return' in xauusd.columns else pd.DataFrame()
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['actual_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"  Prob%: {prob:.1f}%")
        print(f"  RRR: {rrr:.2f}")
        print(f"  AvgWin%: {avg_win*100:.2f}%")
        print(f"  AvgLoss%: {avg_loss*100:.2f}%")
    
    print(f"\n  === XAGUSD ===")
    print(f"  Trades: {len(xagusd)}")
    if len(xagusd) > 0:
        correct = xagusd['correct'].sum() if 'correct' in xagusd.columns else 0
        prob = (correct / len(xagusd) * 100) if len(xagusd) > 0 else 0
        wins = xagusd[xagusd['actual_return'] > 0] if 'actual_return' in xagusd.columns else pd.DataFrame()
        losses = xagusd[xagusd['actual_return'] <= 0] if 'actual_return' in xagusd.columns else pd.DataFrame()
        avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['actual_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"  Prob%: {prob:.1f}%")
        print(f"  RRR: {rrr:.2f}")
        print(f"  AvgWin%: {avg_win*100:.2f}%")
        print(f"  AvgLoss%: {avg_loss*100:.2f}%")
else:
    print("\n❌ Trade history file does not exist")

print("\n" + "=" * 80)
print("CLEARING CACHE AND TRADE HISTORY")
print("=" * 80)

# Clear cache
cache_files = [
    'data/cache/OANDA_XAUUSD.csv',
    'data/cache/OANDA_XAGUSD.csv'
]
for f in cache_files:
    if os.path.exists(f):
        os.remove(f)
        print(f"✅ Deleted {f}")

# Clear trade history
if os.path.exists(file_path):
    os.remove(file_path)
    print(f"✅ Deleted {file_path}")

print("\n" + "=" * 80)
print("RUNNING BACKTEST")
print("=" * 80)

from scripts.backtest_metals_15m import backtest_metals_15m
backtest_metals_15m(n_bars=500, verbose=True)

print("\n" + "=" * 80)
print("CHECKING RESULTS")
print("=" * 80)

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    print(f"Total trades: {len(df)}")
    print(f"\nBy symbol:")
    print(df['symbol'].value_counts())
    
    xauusd = df[df['symbol'] == 'XAUUSD']
    xagusd = df[df['symbol'] == 'XAGUSD']
    
    print(f"\n=== XAUUSD ===")
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
    
    print(f"\n=== XAGUSD ===")
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
else:
    print("❌ No trade history file found after backtest")

print("\n" + "=" * 80)

