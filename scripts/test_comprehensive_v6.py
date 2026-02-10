"""
test_comprehensive_v6.py - Isolated Filter Test (TvDatafeed)
=============================================================
Purpose: Test 3 strategies IN ISOLATION to find the true winner.
1. Market Regime Only (SPY Trend)
2. Momentum Only (RSI/Trend)
3. Sector Rotation Only (Sector Strength)
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from tvDatafeed import TvDatafeed, Interval

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.filters import market_regime, momentum, sector_rotation

# Test Symbols (Liquid only)
STOCKS = [
    ('AAPL', 'NASDAQ', 'tech'), ('NVDA', 'NASDAQ', 'tech'), 
    ('GOOGL', 'NASDAQ', 'tech'), ('MSFT', 'NASDAQ', 'tech'),
    ('PEP', 'NASDAQ', 'defensive'), ('KO', 'NYSE', 'defensive')
]

SECTOR_MAP = {'tech': 'XLK', 'defensive': 'XLP'}

def fetch_with_fallback(tv, symbol, exchange, target_bars=5000):
    for n in [target_bars, 2000, 1000]:
        try:
            df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n)
            if df is not None and not df.empty: return df
        except: pass
        time.sleep(0.5)
    return None

def fetch_all_data(tv):
    data = {}
    print("📊 Fetching Data...")
    for sym, ex, _ in STOCKS:
        print(f"   {sym}...", end="\r")
        df = fetch_with_fallback(tv, sym, ex)
        if df is not None: data[sym] = df
        time.sleep(0.5)
    
    print("   SPY...     ", end="\r")
    data['SPY'] = fetch_with_fallback(tv, 'SPY', 'AMEX')
    
    print("   Sectors... ", end="\r")
    for s in ['XLK', 'XLP']:
        df = fetch_with_fallback(tv, s, 'AMEX')
        if df is not None: data[s] = df
        
    print("\n✅ Done.")
    return data

def run_strategy_test(data):
    results = []
    spy = data.get('SPY')
    
    for sym, _, stype in STOCKS:
        if sym not in data: continue
        df = data[sym]
        if len(df) < 200: continue
        
        # Pre-calc
        df['rsi'] = momentum.calculate_rsi(df)
        df['ret'] = df['close'].pct_change().shift(-1)
        
        # Base Signals (N+1 Proxy)
        buy_sigs = (df['rsi'] < 30)
        sell_sigs = (df['rsi'] > 70)
        indices = df[buy_sigs | sell_sigs].index
        
        # Counters
        base_t, base_w = 0, 0
        regime_t, regime_w = 0, 0
        mom_t, mom_w = 0, 0
        sec_t, sec_w = 0, 0
        
        # Logic Pre-calc
        if spy is not None:
            spy_sma = spy['close'].rolling(50).mean()
            spy_bull = (spy['close'] > spy_sma).reindex(df.index, method='ffill').fillna(False)
        
        sec_name = SECTOR_MAP.get(stype)
        sec_df = data.get(sec_name)
        
        for idx in indices:
            if idx not in df.index[:-1]: continue
            
            is_buy = buy_sigs[idx]
            direction = 'UP' if is_buy else 'DOWN'
            outcome = df.loc[idx, 'ret']
            is_win = (direction=='UP' and outcome>0) or (direction=='DOWN' and outcome<0)
            
            # 1. Baseline
            base_t += 1
            if is_win: base_w += 1
            
            # 2. Regime Filter (SPY Trend)
            if spy is not None:
                is_mkt_bull = spy_bull.loc[idx]
                if (direction=='UP' and is_mkt_bull) or (direction=='DOWN' and not is_mkt_bull):
                    regime_t += 1
                    if is_win: regime_w += 1
            
            # 3. Momentum Filter (RSI Slope)
            try:
                rsi_slope = df['rsi'].loc[idx] - df['rsi'].shift(3).loc[idx]
                if (direction=='UP' and rsi_slope>0) or (direction=='DOWN' and rsi_slope<0):
                    mom_t += 1
                    if is_win: mom_w += 1
            except: pass
            
            # 4. Sector Filter (Sector Trend)
            if sec_df is not None:
                try:
                    sec_sma = sec_df['close'].rolling(50).mean()
                    sec_bull = sec_df['close'].loc[idx] > sec_sma.reindex(df.index, method='ffill').loc[idx]
                    if (direction=='UP' and sec_bull) or (direction=='DOWN' and not sec_bull):
                        sec_t += 1
                        if is_win: sec_w += 1
                except: pass

        # Calc Win Rates
        def wr(w, t): return (w/t*100) if t>0 else 0
        
        results.append({
            'Symbol': sym,
            'Base': wr(base_w, base_t),
            'Regime': wr(regime_w, regime_t),
            'Mom': wr(mom_w, mom_t),
            'Sector': wr(sec_w, sec_t)
        })

    # Summary
    res_df = pd.DataFrame(results)
    print("\n🏆 RESULTS (Win Rates %)")
    print(res_df.to_string(index=False, float_format="%.1f"))
    print("-" * 50)
    print(f"AVG BASE:   {res_df['Base'].mean():.1f}%")
    print(f"AVG REGIME: {res_df['Regime'].mean():.1f}%  (Diff: {res_df['Regime'].mean()-res_df['Base'].mean():+.1f}%)")
    print(f"AVG MOM:    {res_df['Mom'].mean():.1f}%     (Diff: {res_df['Mom'].mean()-res_df['Base'].mean():+.1f}%)")
    print(f"AVG SECTOR: {res_df['Sector'].mean():.1f}%  (Diff: {res_df['Sector'].mean()-res_df['Base'].mean():+.1f}%)")

if __name__ == "__main__":
    tv = TvDatafeed()
    data = fetch_all_data(tv)
    run_strategy_test(data)
