"""
test_hybrid_backtest_v2.py - Optimized Hybrid Filter Test (5000 Bars)
======================================================================
Optimization: Removed time.sleep() and optimized data slicing for speed.
Goal: Compare Baseline vs Hybrid Filter (Market Regime + Stock Specific).
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

# Stock classification
TECH_STOCKS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'META', 'AVGO', 'ADBE', 
               'CRM', 'AMD', 'QCOM', 'INTC', 'TXN', 'MU', 'AMAT', 'LRCX', 'TSLA']
DEFENSIVE_STOCKS = ['PEP', 'KO', 'PG', 'JNJ', 'WMT', 'COST', 'MCD', 'PFE', 
                    'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'AMGN', 'MDLZ']

def get_stock_type(symbol):
    if symbol in TECH_STOCKS: return 'tech'
    if symbol in DEFENSIVE_STOCKS: return 'defensive'
    return 'other'

def fetch_all_data(tv, symbols, n_bars=5000):
    """Fetch all required data upfront."""
    data = {}
    print(f"📊 Fetching {n_bars} bars for {len(symbols)} symbols...")
    
    for sym in symbols:
        try:
            df = tv.get_hist(symbol=sym, exchange='NASDAQ', interval=Interval.in_daily, n_bars=n_bars) # Try NASDAQ first
            if df is None:
                df = tv.get_hist(symbol=sym, exchange='NYSE', interval=Interval.in_daily, n_bars=n_bars) # Fallback
            if df is None:
                df = tv.get_hist(symbol=sym, exchange='AMEX', interval=Interval.in_daily, n_bars=n_bars) # Fallback
                
            if df is not None:
                data[sym] = df
            time.sleep(0.1) # Minimum delay to avoid ban
        except:
            print(f"❌ Failed to fetch {sym}")
            
    return data

def simulate_fast_backtest(df, spy_df, sector_data, symbol):
    """
    Optimized backtest simulation.
    Uses vector operations or simplified loop.
    """
    if df is None or len(df) < 200: return 0, 0, 0.0, 0.0
    
    # Pre-calculate indicators for speed
    # 1. Pattern Direction (Simplified as 5-day return for speed in this test)
    #    Real fractal matching is too slow for 5000 bars * 20 stocks in a quick test.
    #    We assume the Fractal Logic identifies trend reversals.
    #    Here we simulate "Potential Signals" using RSI reversals as a proxy for Fractal.
    
    df['rsi'] = momentum.calculate_rsi(df)
    df['ret_1d'] = df['close'].pct_change().shift(-1) # Next day return (Outcome)
    
    # Identify "Signals" (Proxy for Fractal N+1)
    # Buy Signal: RSI < 30 (Oversold) -> Reversal Up
    # Sell Signal: RSI > 70 (Overbought) -> Reversal Down
    # This simulates "Mean Reversion" logic of the main system.
    
    buy_signals = (df['rsi'] < 30)
    sell_signals = (df['rsi'] > 70)
    
    results = []
    
    # Market Regime Pre-calculation
    spy_sma50 = market_regime.calculate_sma(spy_df, 50)
    is_spy_bull = spy_df['close'] > spy_sma50
    
    # Align SPY data to Stock data
    # Creates a Series with same index as df, evaluating to True/False
    market_filter_pass = is_spy_bull.reindex(df.index, method='ffill').fillna(False)
    
    # Iterate only on signals
    signal_indices = df[buy_signals | sell_signals].index
    
    baseline_wins = 0
    baseline_trades = 0
    filtered_wins = 0
    filtered_trades = 0
    
    stock_type = get_stock_type(symbol)
    
    for idx in signal_indices:
        if idx not in df.index[:-1]: continue # Skip last bar
        
        # Determine Signal Type
        is_buy = buy_signals[idx]
        direction = 'UP' if is_buy else 'DOWN'
        outcome = df.loc[idx, 'ret_1d']
        
        # Baseline Result
        is_win = (direction == 'UP' and outcome > 0) or (direction == 'DOWN' and outcome < 0)
        baseline_trades += 1
        if is_win: baseline_wins += 1
        
        # --- Apply Hybrid Filter ---
        
        # 1. Market Regime (Layer 1)
        # Block LONG if Bear, Block SHORT if Bull
        market_bull = market_filter_pass.loc[idx]
        
        if direction == 'UP' and not market_bull: continue
        if direction == 'DOWN' and market_bull: continue
        
        # 2. Stock Specific (Layer 2)
        passed_layer2 = True
        
        if stock_type == 'tech':
            # Momentum Filter Logic:
            # Require MACD to be rising for Buy
            # We calculate this on the fly or pre-calc? On fly is ok for subset.
            # Simplified: Check if RSI is rising (3-bar slope)
            # This is a proxy for "Momentum Confirmation"
            try:
                rsi_slope = df['rsi'].loc[idx] - df['rsi'].shift(3).loc[idx]
                if direction == 'UP' and rsi_slope < 0: passed_layer2 = False
                if direction == 'DOWN' and rsi_slope > 0: passed_layer2 = False
            except: pass
            
        elif stock_type == 'defensive':
            # Sector Filter
            # Check if Sector is outperforming SPY
            sector = sector_rotation.get_sector_for_symbol(symbol)
            if sector and sector in sector_data:
                # Check relative strength
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
    print("🚀 FAST HYBRID BACKTEST (5000 Bars)")
    print("=" * 60)
    
    tv = TvDatafeed()
    stocks = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA', 'AMD', 'META', 
              'PEP', 'KO', 'COST', 'WMT', 'JNJ', 'PG', 'MCD']
    
    # Fetch Data
    stock_data = fetch_all_data(tv, stocks, n_bars=5000)
    spy_data = fetch_all_data(tv, ['SPY'], n_bars=5000)['SPY']
    
    sector_syms = ['XLK', 'XLV', 'XLF', 'XLY', 'XLP']
    sector_data_raw = fetch_all_data(tv, sector_syms, n_bars=5000)
             
    print("\n⚔️  Running Comparison...")
    print(f"{'Symbol':<10} {'Type':<10} {'Base WR':<10} {'Hybrid WR':<10} {'Diff':<10} {'Trades (Base->Filt)'}")
    print("-" * 75)
    
    results = []
    
    for sym in stocks:
        if sym not in stock_data: continue
        
        b_cnt, f_cnt, b_wr, f_wr = simulate_fast_backtest(stock_data[sym], spy_data, sector_data_raw, sym)
        
        diff = f_wr - b_wr
        stock_type = get_stock_type(sym)
        
        print(f"{sym:<10} {stock_type:<10} {b_wr:<10.1f} {f_wr:<10.1f} {diff:<+10.1f} {b_cnt}->{f_cnt}")
        
        results.append({
            'symbol': sym, 'type': stock_type,
            'base_wr': b_wr, 'filt_wr': f_wr, 'diff': diff
        })
        
    # Summary
    df = pd.DataFrame(results)
    print("-" * 75)
    print(f"AVERAGE    ALL        {df['base_wr'].mean():.1f}       {df['filt_wr'].mean():.1f}       {df['diff'].mean():+.1f}")
    
    tech = df[df['type']=='tech']
    print(f"AVERAGE    TECH       {tech['base_wr'].mean():.1f}       {tech['filt_wr'].mean():.1f}       {tech['diff'].mean():+.1f}")

if __name__ == "__main__":
    run_test()
