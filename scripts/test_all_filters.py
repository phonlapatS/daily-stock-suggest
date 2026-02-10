"""
test_all_filters.py - Compare All Filter Strategies
====================================================
Purpose: Apply each filter to the same backtest data and compare win rates.
Output: A comparison table showing win rate before/after each filter.
"""

import sys
import os
import pandas as pd
import time
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import filters
from scripts.filters import market_regime, multi_timeframe, momentum, sector_rotation

# Import existing backtest logic
from config import ASSET_GROUPS

def fetch_data(tv, symbol, exchange, n_bars=500):
    """Fetch historical data for a symbol."""
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def simulate_trades(df, threshold_pct=0.6):
    """
    Simulate simple pattern-based trades.
    Returns list of trades: [{date, direction, entry, exit, result}, ...]
    """
    if df is None or len(df) < 50:
        return []
    
    trades = []
    
    # Simple logic: Use last N bars' avg return as direction
    for i in range(50, len(df) - 1):
        window = df.iloc[i-50:i]
        
        # Calculate pattern direction (simplified)
        avg_change = window['close'].pct_change().mean() * 100
        
        if abs(avg_change) < threshold_pct / 100:
            continue  # No signal
        
        direction = 'UP' if avg_change > 0 else 'DOWN'
        entry_price = df['close'].iloc[i]
        exit_price = df['close'].iloc[i + 1]
        
        if direction == 'UP':
            result = 1 if exit_price > entry_price else 0
        else:
            result = 1 if exit_price < entry_price else 0
        
        trades.append({
            'date': df.index[i],
            'direction': direction,
            'entry': entry_price,
            'exit': exit_price,
            'result': result,
            'df_slice': df.iloc[:i+1].copy()  # Data up to entry point
        })
    
    return trades

def calculate_win_rate(trades):
    """Calculate win rate from trades list."""
    if not trades:
        return 0.0
    wins = sum(t['result'] for t in trades)
    return wins / len(trades) * 100

def apply_market_regime_filter(trades, spy_df):
    """Apply market regime filter to trades."""
    filtered = []
    for t in trades:
        # Get SPY data up to trade date
        spy_up_to_date = spy_df[spy_df.index <= t['date']]
        if len(spy_up_to_date) < 50:
            continue
        
        if market_regime.is_market_bullish(spy_up_to_date):
            # Only allow LONG in bull market
            if t['direction'] == 'UP':
                filtered.append(t)
        else:
            # Bear market: allow SHORT only
            if t['direction'] == 'DOWN':
                filtered.append(t)
    return filtered

def apply_multi_timeframe_filter(trades):
    """Apply multi-timeframe filter to trades."""
    filtered = []
    for t in trades:
        df = t['df_slice']
        if multi_timeframe.is_signal_confirmed(df, t['direction']):
            filtered.append(t)
    return filtered

def apply_momentum_filter(trades):
    """Apply momentum filter to trades."""
    filtered = []
    for t in trades:
        df = t['df_slice']
        if len(df) < 30:
            continue
        if momentum.is_signal_confirmed(df, t['direction']):
            filtered.append(t)
    return filtered

def apply_sector_filter(trades, symbol, sector_data, spy_df):
    """Apply sector rotation filter to trades."""
    sector = sector_rotation.get_sector_for_symbol(symbol)
    if sector is None or sector not in sector_data:
        return trades  # No sector mapping, allow all
    
    sector_df = sector_data[sector]
    
    filtered = []
    for t in trades:
        spy_up_to_date = spy_df[spy_df.index <= t['date']]
        sector_up_to_date = sector_df[sector_df.index <= t['date']]
        
        if len(spy_up_to_date) < 60 or len(sector_up_to_date) < 60:
            continue
        
        if sector_rotation.is_sector_strong(symbol, sector_up_to_date, spy_up_to_date):
            filtered.append(t)
    return filtered

def run_comparison():
    """Main function to run comparison of all filters."""
    print("=" * 70)
    print("🔬 FILTER COMPARISON TEST")
    print("=" * 70)
    
    tv = TvDatafeed()
    
    # Get US stocks from config
    us_group = ASSET_GROUPS.get('GROUP_B_US', {})
    us_assets = us_group.get('assets', [])[:20]  # Limit to 20 for speed
    
    # Fetch SPY for market regime filter
    print("\n📊 Fetching SPY (Market Index)...")
    spy_df = fetch_data(tv, 'SPY', 'AMEX', n_bars=500)
    time.sleep(0.5)
    
    # Fetch sector ETFs
    print("📊 Fetching Sector ETFs...")
    sector_data = {}
    for sector in ['XLK', 'XLV', 'XLF', 'XLY', 'XLP']:  # Limit for speed
        df = fetch_data(tv, sector, 'AMEX', n_bars=500)
        if df is not None:
            sector_data[sector] = df
        time.sleep(0.3)
    
    # Results storage
    results = {
        'symbol': [],
        'baseline_trades': [],
        'baseline_wr': [],
        'regime_trades': [],
        'regime_wr': [],
        'mtf_trades': [],
        'mtf_wr': [],
        'momentum_trades': [],
        'momentum_wr': [],
        'sector_trades': [],
        'sector_wr': [],
    }
    
    print(f"\n🚀 Analyzing {len(us_assets)} US stocks...")
    
    for i, asset in enumerate(us_assets):
        symbol = asset['symbol']
        exchange = asset['exchange']
        
        print(f"   [{i+1}/{len(us_assets)}] {symbol}...", end=" ")
        
        df = fetch_data(tv, symbol, exchange, n_bars=500)
        if df is None or len(df) < 100:
            print("❌ Skip (No Data)")
            continue
        
        # Generate baseline trades
        trades = simulate_trades(df)
        baseline_wr = calculate_win_rate(trades)
        
        # Apply each filter
        regime_trades = apply_market_regime_filter(trades, spy_df) if spy_df is not None else trades
        mtf_trades = apply_multi_timeframe_filter(trades)
        momentum_trades = apply_momentum_filter(trades)
        sector_trades = apply_sector_filter(trades, symbol, sector_data, spy_df) if spy_df is not None else trades
        
        # Store results
        results['symbol'].append(symbol)
        results['baseline_trades'].append(len(trades))
        results['baseline_wr'].append(baseline_wr)
        results['regime_trades'].append(len(regime_trades))
        results['regime_wr'].append(calculate_win_rate(regime_trades))
        results['mtf_trades'].append(len(mtf_trades))
        results['mtf_wr'].append(calculate_win_rate(mtf_trades))
        results['momentum_trades'].append(len(momentum_trades))
        results['momentum_wr'].append(calculate_win_rate(momentum_trades))
        results['sector_trades'].append(len(sector_trades))
        results['sector_wr'].append(calculate_win_rate(sector_trades))
        
        print(f"✅ Base: {baseline_wr:.1f}%")
        
        time.sleep(0.3)
    
    # Create summary DataFrame
    df_results = pd.DataFrame(results)
    
    # Calculate averages
    print("\n" + "=" * 70)
    print("📈 SUMMARY RESULTS")
    print("=" * 70)
    
    print(f"\n{'Filter':<25} {'Avg Trades':<15} {'Avg Win Rate':<15}")
    print("-" * 55)
    print(f"{'Baseline (No Filter)':<25} {df_results['baseline_trades'].mean():<15.1f} {df_results['baseline_wr'].mean():<15.1f}%")
    print(f"{'Market Regime':<25} {df_results['regime_trades'].mean():<15.1f} {df_results['regime_wr'].mean():<15.1f}%")
    print(f"{'Multi-Timeframe':<25} {df_results['mtf_trades'].mean():<15.1f} {df_results['mtf_wr'].mean():<15.1f}%")
    print(f"{'Momentum (RSI/MACD/ADX)':<25} {df_results['momentum_trades'].mean():<15.1f} {df_results['momentum_wr'].mean():<15.1f}%")
    print(f"{'Sector Rotation':<25} {df_results['sector_trades'].mean():<15.1f} {df_results['sector_wr'].mean():<15.1f}%")
    
    # Save results
    output_path = 'data/filter_comparison.csv'
    df_results.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to {output_path}")
    
    return df_results

if __name__ == "__main__":
    run_comparison()
