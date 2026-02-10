"""
test_hybrid_backtest_v5.py - Compliant Hybrid Filter Test (TvDatafeed Only)
============================================================================
Constraint: NO yfinance allowed. Use TvDatafeed only.
Strategy:
1. Try fetching 5000 bars.
2. If timeout, fallback to 2500, then 1000.
3. Test on specific liquid stocks to ensure data availability.
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

# Symbols to test (Reduced list for higher success rate)
STOCKS = [
    # Tech
    ('AAPL', 'NASDAQ', 'tech'),
    ('MSFT', 'NASDAQ', 'tech'),
    ('NVDA', 'NASDAQ', 'tech'),
    ('GOOGL', 'NASDAQ', 'tech'),
    # Defensive
    ('PEP', 'NASDAQ', 'defensive'),
    ('KO', 'NYSE', 'defensive'),
    ('JNJ', 'NYSE', 'defensive'),
]

SECTOR_MAP = {
    'tech': 'XLK',
    'defensive': 'XLP' # Simplified: Mapping both PEP/KO/JNJ to Cons. Staples for test
}

def fetch_with_fallback(tv, symbol, exchange, target_bars=5000):
    """Fetch data with bar-count fallback to avoid timeouts."""
    for n in [target_bars, 2500, 1000, 500]:
        try:
            # print(f"   Trying {n} bars for {symbol}...")
            df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n)
            if df is not None and not df.empty:
                if n < target_bars:
                    print(f"   ⚠️  Fetched only {n} bars for {symbol} (Timeout protection)")
                return df
        except:
            pass
        time.sleep(1)
    
    print(f"❌ Failed to fetch {symbol} completely.")
    return None

def fetch_all_data(tv):
    data = {}
    print("📊 Fetching market data (TV Datafeed)...")
    
    # 1. Fetch Stocks
    for sym, ex, _ in STOCKS:
        print(f"   Fetching {sym}...", end="\r")
        df = fetch_with_fallback(tv, sym, ex)
        if df is not None:
            data[sym] = df
        time.sleep(1)
            
    # 2. Fetch SPY
    print("   Fetching SPY...     ", end="\r")
    spy = fetch_with_fallback(tv, 'SPY', 'AMEX')
    if spy is not None:
        data['SPY'] = spy
        
    # 3. Fetch Sectors
    print("   Fetching Sectors... ", end="\r")
    for sec in ['XLK', 'XLP']:
        df = fetch_with_fallback(tv, sec, 'AMEX')
        if df is not None:
            data[sec] = df
            
    print("\n✅ Data fetching complete.")
    return data

def simulate_backtest(df, spy_df, sector_data, stock_type, symbol):
    if df is None or len(df) < 200: return 0, 0, 0.0, 0.0
    
    # Pre-calc indicators
    df['rsi'] = momentum.calculate_rsi(df)
    df['ret_1d'] = df['close'].pct_change().shift(-1)
    
    # Signals (Proxy)
    buy_signals = (df['rsi'] < 30)
    sell_signals = (df['rsi'] > 70)
    
    # Market Regime
    if spy_df is not None:
        spy_sma50 = market_regime.calculate_sma(spy_df, 50)
        is_spy_bull = spy_df['close'] > spy_sma50
        market_filter_pass = is_spy_bull.reindex(df.index, method='ffill').fillna(False)
    else:
        market_filter_pass = pd.Series(True, index=df.index) # Analysis impossible without SPY, pass all
    
    baseline_wins = 0
    baseline_trades = 0
    filtered_wins = 0
    filtered_trades = 0
    
    signal_indices = df[buy_signals | sell_signals].index
    
    for idx in signal_indices:
        if idx not in df.index[:-1]: continue
        
        is_buy = buy_signals[idx]
        direction = 'UP' if is_buy else 'DOWN'
        outcome = df.loc[idx, 'ret_1d']
        
        # Baseline
        is_win = (direction == 'UP' and outcome > 0) or (direction == 'DOWN' and outcome < 0)
        baseline_trades += 1
        if is_win: baseline_wins += 1
        
        # --- Hybrid Filter ---
        
        # 1. Market Regime
        if spy_df is not None:
            try:
                market_bull = market_filter_pass.loc[idx]
                if direction == 'UP' and not market_bull: continue
                if direction == 'DOWN' and market_bull: continue
            except: continue
            
        # 2. Stock Specific
        passed_layer2 = True
        
        if stock_type == 'tech':
            try:
                rsi_val = df['rsi'].loc[idx]
                rsi_prev = df['rsi'].shift(3).loc[idx]
                # Filter: Momentum must be in direction of trade
                if direction == 'UP' and (rsi_val < rsi_prev): passed_layer2 = False
                if direction == 'DOWN' and (rsi_val > rsi_prev): passed_layer2 = False
            except: pass
            
        elif stock_type == 'defensive':
            sec_sym = SECTOR_MAP.get(stock_type)
            if sec_sym and sec_sym in sector_data:
                try:
                    # Check if Sector > SPY (Relative Strength)
                    # Simplified: Sector Price > Sector SMA50 (Trend check) for robustness
                    # (Relative strength calculation across mismatched time series is error prone in fast script)
                    # Let's use: Sector Trend Confirmation
                    sec_df = sector_data[sec_sym]
                    sec_sma = sec_df['close'].rolling(50).mean()
                    sec_trend_bull = sec_df['close'].loc[idx] > sec_sma.reindex(df.index, method='ffill').loc[idx]
                    
                    if direction == 'UP' and not sec_trend_bull: passed_layer2 = False
                    if direction == 'DOWN' and sec_trend_bull: passed_layer2 = False
                except: pass
        
        if passed_layer2:
            filtered_trades += 1
            if is_win: filtered_wins += 1
            
    base_wr = (baseline_wins / baseline_trades * 100) if baseline_trades > 0 else 0
    filt_wr = (filtered_wins / filtered_trades * 100) if filtered_trades > 0 else 0
    
    return baseline_trades, filtered_trades, base_wr, filt_wr

def run():
    print("=" * 60)
    print("🚀 HYBRID BACKTEST v5 (TvDatafeed Compliant)")
    print("=" * 60)
    
    tv = TvDatafeed()
    data = fetch_all_data(tv)
    
    if 'SPY' not in data:
        print("❌ Critical: SPY data failed. Cannot run Market Regime filter.")
        return

    print("\n⚔️  Running Analysis...")
    print(f"{'Symbol':<10} {'Type':<10} {'Base WR':<10} {'Hybrid WR':<10} {'Diff':<10} {'Trades'}")
    print("-" * 75)
    
    results = []
    
    for sym, _, stype in STOCKS:
        if sym not in data: continue
        
        b_cnt, f_cnt, b_wr, f_wr = simulate_backtest(data[sym], data.get('SPY'), data, stype, sym)
        
        diff = f_wr - b_wr
        print(f"{sym:<10} {stype:<10} {b_wr:<10.1f} {f_wr:<10.1f} {diff:<+10.1f} {b_cnt}->{f_cnt}")
        
        results.append({'diff': diff, 'base': b_wr, 'filt': f_wr, 'type': stype})
        
    if results:
        df = pd.DataFrame(results)
        print("-" * 75)
        print(f"AVG IMPROVEMENT: {df['diff'].mean():+.1f}%")
        print(f"TECH AVG:        {df[df['type']=='tech']['diff'].mean():+.1f}%")
        print(f"DEFENSIVE AVG:   {df[df['type']=='defensive']['diff'].mean():+.1f}%")

if __name__ == "__main__":
    run()
