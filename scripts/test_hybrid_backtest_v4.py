"""
test_hybrid_backtest_v4.py - Reliable Hybrid Filter Test (5000 Bars)
======================================================================
Optimization: v3 logic + yfinance Data Fetching (Reliable).
Goal: Compare Baseline vs Hybrid Filter with guaranteed execution.
"""

import sys
import os
import pandas as pd
import numpy as np
import time
import yfinance as yf

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

def fetch_data_yf(symbol, period="5y"): # 5 years approx 1250 bars. Need more? 
    # yfinance max period is 'max' or specific dates. 
    # 5000 bars is approx 20 years. Let's try 'max'.
    try:
        # print(f"   Fetching {symbol} via yfinance...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="max")
        
        if df is None or df.empty:
            return None
            
        # Standardize columns to lowercase
        df.columns = [c.lower() for c in df.columns]
        # Ensure 'close' exists
        if 'close' not in df.columns and 'Close' in df.columns:
            df['close'] = df['Close']
            
        return df
    except Exception as e:
        print(f"❌ Failed to fetch {symbol}: {e}")
        return None

def fetch_all_data(symbols):
    """Fetch all required data upfront using yfinance."""
    data = {}
    print(f"📊 Fetching data for {len(symbols)} symbols using yfinance...")
    
    for i, sym in enumerate(symbols):
        print(f"   [{i+1}/{len(symbols)}] Fetching {sym}...", end="\r")
        df = fetch_data_yf(sym)
        if df is not None:
            # We want roughly 5000 bars if available
            if len(df) > 5000:
                df = df.iloc[-5000:]
            data[sym] = df
        time.sleep(0.2) # Gentle pace
            
    print("\n✅ Data fetching complete.")
    return data

def simulate_fast_backtest(df, spy_df, sector_data, symbol):
    """
    Optimized backtest simulation (Same logic as v2/v3).
    """
    if df is None or len(df) < 500: return 0, 0, 0.0, 0.0
    
    # Pre-calculate indicators
    df = df.copy() # Avoid SettingWithCopy
    df['rsi'] = momentum.calculate_rsi(df)
    df['ret_1d'] = df['close'].pct_change().shift(-1)
    
    # Identify Signals (RSI Reversal Proxy)
    # Using slightly more relaxed conditions to get enough trades
    buy_signals = (df['rsi'] < 35) 
    sell_signals = (df['rsi'] > 65)
    
    # Market Regime Pre-calculation
    spy_sma50 = market_regime.calculate_sma(spy_df, 50)
    is_spy_bull = spy_df['close'] > spy_sma50
    # Reindex to match stock dates
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
        try:
            market_bull = market_filter_pass.loc[idx]
            if direction == 'UP' and not market_bull: continue
            if direction == 'DOWN' and market_bull: continue
        except KeyError: continue # Date mismatch
        
        # 2. Stock Specific
        passed_layer2 = True
        
        if stock_type == 'tech':
            try:
                # RSI Slope Logic
                rsi_val = df['rsi'].loc[idx]
                rsi_prev = df['rsi'].shift(3).loc[idx]
                rsi_slope = rsi_val - rsi_prev
                
                if direction == 'UP' and rsi_slope < 0: passed_layer2 = False
                if direction == 'DOWN' and rsi_slope > 0: passed_layer2 = False
            except: pass
            
        elif stock_type == 'defensive':
            sector = sector_rotation.get_sector_for_symbol(symbol)
            if sector and sector in sector_data:
                try:
                    # Sector Relative Strength
                    sdf = sector_data[sector]
                    spy = spy_df
                    
                    # Need to align dates carefully
                    # Check return over last 60 days
                    # Using simplified check: Is Sector > SPY over last 60 bars?
                    
                    # We pre-calculate 'rel_strength' for speed? No, do on fly with lookup
                    # Just calculate pct_change(60) for both at this index
                    
                    # Get integer location
                    iloc = df.index.get_loc(idx)
                    if iloc < 60: continue
                    
                    date_60_ago = df.index[iloc-60]
                    
                    # Find closest date in Sector/SPY
                    sec_idx = sdf.index.asof(idx)
                    sec_old_idx = sdf.index.asof(date_60_ago)
                    
                    spy_idx = spy.index.asof(idx)
                    spy_old_idx = spy.index.asof(date_60_ago)
                    
                    sec_ret = (sdf.loc[sec_idx, 'close'] - sdf.loc[sec_old_idx, 'close']) / sdf.loc[sec_old_idx, 'close']
                    spy_ret = (spy.loc[spy_idx, 'close'] - spy.loc[spy_old_idx, 'close']) / spy.loc[spy_old_idx, 'close']
                    
                    if sec_ret < spy_ret: passed_layer2 = False
                    
                except Exception as e: 
                    # print(e)
                    pass
        
        if passed_layer2:
            filtered_trades += 1
            if is_win: filtered_wins += 1
            
    base_wr = (baseline_wins / baseline_trades * 100) if baseline_trades > 0 else 0
    filt_wr = (filtered_wins / filtered_trades * 100) if filtered_trades > 0 else 0
    
    return baseline_trades, filtered_trades, base_wr, filt_wr

def run_test():
    print("=" * 60)
    print("🚀 RELIABLE HYBRID BACKTEST (yfinance)")
    print("=" * 60)
    
    # Fetch Data
    stock_data = fetch_all_data(ALL_STOCKS)
    spy_data = fetch_all_data(['SPY'])['SPY']
    
    sector_syms = ['XLK', 'XLV', 'XLF', 'XLY', 'XLP']
    sector_data_raw = fetch_all_data(sector_syms)
             
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
            'base_wr': b_wr, 'filt_wr': f_wr, 'diff': diff,
            'b_cnt': b_cnt, 'f_cnt': f_cnt
        })
        
    df = pd.DataFrame(results)
    
    if df.empty:
        print("❌ No results.")
        return

    print("-" * 75)
    print(f"AVERAGE    ALL        {df['base_wr'].mean():.1f}       {df['filt_wr'].mean():.1f}       {df['diff'].mean():+.1f}")
    
    tech = df[df['type']=='tech']
    if not tech.empty:
        print(f"AVERAGE    TECH       {tech['base_wr'].mean():.1f}       {tech['filt_wr'].mean():.1f}       {tech['diff'].mean():+.1f}")
        
    defensive = df[df['type']=='defensive']
    if not defensive.empty:
        print(f"AVERAGE    DEFENSIVE  {defensive['base_wr'].mean():.1f}       {defensive['filt_wr'].mean():.1f}       {defensive['diff'].mean():+.1f}")
        
    # Formatting Improvement
    print("\n💡 CONCLUSION:")
    avg_imp = df['diff'].mean()
    if avg_imp > 0:
        print(f"✅ Hybrid Filter IMPROVED Win Rate by +{avg_imp:.1f}% on average.")
    else:
        print(f"⚠️ Hybrid Filter did NOT improve Win Rate significantly ({avg_imp:.1f}%).")
        
    reduced_trades = (1 - df['f_cnt'].sum() / df['b_cnt'].sum()) * 100
    print(f"📉 Trade Count Reduced by {reduced_trades:.1f}% (Quality Filtering)")


if __name__ == "__main__":
    run_test()
