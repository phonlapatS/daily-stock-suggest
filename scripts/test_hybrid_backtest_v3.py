"""
test_hybrid_backtest_v3.py - Robust Hybrid Filter Test (5000 Bars)
======================================================================
Optimization: v2 logic + Robust Data Fetching (Retries/Fallbacks).
Goal: Compare Baseline vs Hybrid Filter with guaranteed execution.
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.filters import market_regime, momentum, sector_rotation

# Reduced List for Stability (Top 5 Tech, Top 5 Defensive)
TECH_STOCKS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMD']
DEFENSIVE_STOCKS = ['PEP', 'KO', 'JNJ', 'PG', 'MCD']
ALL_STOCKS = TECH_STOCKS + DEFENSIVE_STOCKS

def get_stock_type(symbol):
    if symbol in TECH_STOCKS: return 'tech'
    if symbol in DEFENSIVE_STOCKS: return 'defensive'
    return 'other'

def fetch_data_robust(tv, symbol, n_bars=5000, retries=3):
    """Robust data fetching with retries and exchange fallback."""
    exchanges = ['NASDAQ', 'NYSE', 'AMEX']
    
    for attempt in range(retries):
        for ex in exchanges:
            try:
                # print(f"   Trying {symbol} on {ex} (Attempt {attempt+1})...")
                df = tv.get_hist(symbol=symbol, exchange=ex, interval=Interval.in_daily, n_bars=n_bars)
                if df is not None and not df.empty:
                    return df
            except:
                pass
        time.sleep(1) # Wait before retry
        
    print(f"❌ Failed to fetch {symbol} after {retries} attempts.")
    return None

def fetch_all_data(tv, symbols, n_bars=5000):
    """Fetch all required data upfront."""
    data = {}
    print(f"📊 Fetching {n_bars} bars for {len(symbols)} symbols...")
    
    for i, sym in enumerate(symbols):
        print(f"   [{i+1}/{len(symbols)}] Fetching {sym}...", end="\r")
        df = fetch_data_robust(tv, sym, n_bars=n_bars)
        if df is not None:
            data[sym] = df
        time.sleep(0.5) # Pace requests
            
    print("\n✅ Data fetching complete.")
    return data

def simulate_fast_backtest(df, spy_df, sector_data, symbol):
    """
    Optimized backtest simulation (Same logic as v2).
    """
    if df is None or len(df) < 200: return 0, 0, 0.0, 0.0
    
    # Pre-calculate indicators
    df['rsi'] = momentum.calculate_rsi(df)
    df['ret_1d'] = df['close'].pct_change().shift(-1)
    
    # Identify Signals (RSI Reversal Proxy)
    buy_signals = (df['rsi'] < 30)
    sell_signals = (df['rsi'] > 70)
    
    # Market Regime Pre-calculation
    spy_sma50 = market_regime.calculate_sma(spy_df, 50)
    is_spy_bull = spy_df['close'] > spy_sma50
    market_filter_pass = is_spy_bull.reindex(df.index, method='ffill').fillna(False)
    
    baseline_wins = 0
    baseline_trades = 0
    filtered_wins = 0
    filtered_trades = 0
    
    stock_type = get_stock_type(symbol)
    signal_indices = df[buy_signals | sell_signals].index
    
    for idx in signal_indices:
        if idx not in df.index[:-1]: continue
        
        is_buy = buy_signals[idx]
        direction = 'UP' if is_buy else 'DOWN'
        outcome = df.loc[idx, 'ret_1d']
        
        # Baseline Result
        is_win = (direction == 'UP' and outcome > 0) or (direction == 'DOWN' and outcome < 0)
        baseline_trades += 1
        if is_win: baseline_wins += 1
        
        # --- Apply Hybrid Filter ---
        
        # 1. Market Regime
        market_bull = market_filter_pass.loc[idx]
        if direction == 'UP' and not market_bull: continue
        if direction == 'DOWN' and market_bull: continue
        
        # 2. Stock Specific
        passed_layer2 = True
        
        if stock_type == 'tech':
            try:
                rsi_slope = df['rsi'].loc[idx] - df['rsi'].shift(3).loc[idx]
                if direction == 'UP' and rsi_slope < 0: passed_layer2 = False
                if direction == 'DOWN' and rsi_slope > 0: passed_layer2 = False
            except: pass
            
        elif stock_type == 'defensive':
            sector = sector_rotation.get_sector_for_symbol(symbol)
            if sector and sector in sector_data:
                try:
                    sec_ret = sector_data[sector]['close'].pct_change(60).reindex(df.index, method='ffill').loc[idx]
                    spy_ret = spy_df['close'].pct_change(60).reindex(df.index, method='ffill').loc[idx]
                    if sec_ret < spy_ret: passed_layer2 = False
                except: pass
        
        if passed_layer2:
            filtered_trades += 1
            if is_win: filtered_wins += 1
            
    base_wr = (baseline_wins / baseline_trades * 100) if baseline_trades > 0 else 0
    filt_wr = (filtered_wins / filtered_trades * 100) if filtered_trades > 0 else 0
    
    return baseline_trades, filtered_trades, base_wr, filt_wr

def run_test():
    print("=" * 60)
    print("🚀 ROBUST HYBRID BACKTEST (5000 Bars)")
    print("=" * 60)
    
    tv = TvDatafeed()
    
    # Fetch Data
    stock_data = fetch_all_data(tv, ALL_STOCKS, n_bars=5000)
    spy_data = fetch_all_data(tv, ['SPY'], n_bars=5000)['SPY']
    
    sector_syms = ['XLK', 'XLV', 'XLF', 'XLY', 'XLP']
    sector_data_raw = fetch_all_data(tv, sector_syms, n_bars=5000)
             
    print("\n⚔️  Running Comparison...")
    print(f"{'Symbol':<10} {'Type':<10} {'Base WR':<10} {'Hybrid WR':<10} {'Diff':<10} {'Trades (Base->Filt)'}")
    print("-" * 75)
    
    results = []
    
    for sym in ALL_STOCKS:
        if sym not in stock_data: continue
        
        b_cnt, f_cnt, b_wr, f_wr = simulate_fast_backtest(stock_data[sym], spy_data, sector_data_raw, sym)
        
        diff = f_wr - b_wr
        stock_type = get_stock_type(sym)
        
        print(f"{sym:<10} {stock_type:<10} {b_wr:<10.1f} {f_wr:<10.1f} {diff:<+10.1f} {b_cnt}->{f_cnt}")
        
        results.append({
            'symbol': sym, 'type': stock_type,
            'base_wr': b_wr, 'filt_wr': f_wr, 'diff': diff
        })
        
    # Summary with Safety Check
    if not results:
        print("\n❌ No results generated. Check connection or symbol list.")
        return

    df = pd.DataFrame(results)
    print("-" * 75)
    print(f"AVERAGE    ALL        {df['base_wr'].mean():.1f}       {df['filt_wr'].mean():.1f}       {df['diff'].mean():+.1f}")
    
    tech = df[df['type']=='tech']
    if not tech.empty:
        print(f"AVERAGE    TECH       {tech['base_wr'].mean():.1f}       {tech['filt_wr'].mean():.1f}       {tech['diff'].mean():+.1f}")
        
    defensive = df[df['type']=='defensive']
    if not defensive.empty:
        print(f"AVERAGE    DEFENSIVE  {defensive['base_wr'].mean():.1f}       {defensive['filt_wr'].mean():.1f}       {defensive['diff'].mean():+.1f}")

if __name__ == "__main__":
    run_test()
