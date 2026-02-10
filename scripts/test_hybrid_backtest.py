"""
test_hybrid_backtest.py - Hybrid Filter Test with Real Backtest Data
=====================================================================
Purpose: Test the Hybrid Filter approach using real backtest logic (5000 bars).
Logic:
    Layer 1: Market Regime Filter (SPY > SMA50)
    Layer 2: Stock-Specific Filter (Momentum for Tech, Sector for Defensive)
"""

import sys
import os
import pandas as pd
import time
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import filters
from scripts.filters import market_regime, momentum, sector_rotation

# Import processor for actual pattern matching
from processor import analyze_asset

# Stock classification
TECH_STOCKS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'META', 'AVGO', 'ADBE', 
               'CRM', 'AMD', 'QCOM', 'INTC', 'TXN', 'MU', 'AMAT', 'LRCX']
DEFENSIVE_STOCKS = ['PEP', 'KO', 'PG', 'JNJ', 'WMT', 'COST', 'MCD', 'PFE', 
                    'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'AMGN', 'MDLZ']

def get_stock_type(symbol):
    """Classify stock as Tech, Defensive, or Other."""
    if symbol in TECH_STOCKS:
        return 'tech'
    elif symbol in DEFENSIVE_STOCKS:
        return 'defensive'
    return 'other'

def apply_hybrid_filter(signal_direction, df, spy_df, sector_data, symbol):
    """
    Apply Hybrid Filter (2 Layers).
    Returns: True if trade should be taken, False otherwise.
    """
    # Layer 1: Market Regime
    if len(spy_df) >= 50:
        is_bull = market_regime.is_market_bullish(spy_df)
        if signal_direction == 'UP' and not is_bull:
            return False  # Block LONG in BEAR market
        if signal_direction == 'DOWN' and is_bull:
            return False  # Block SHORT in BULL market
    
    # Layer 2: Stock-Specific Filter
    stock_type = get_stock_type(symbol)
    
    if stock_type == 'tech':
        # Use Momentum Filter for Tech
        if len(df) >= 30:
            return momentum.is_signal_confirmed(df, signal_direction)
    elif stock_type == 'defensive':
        # Use Sector Filter for Defensive
        sector = sector_rotation.get_sector_for_symbol(symbol)
        if sector and sector in sector_data and len(spy_df) >= 60:
            sector_df = sector_data[sector]
            return sector_rotation.is_sector_strong(symbol, sector_df, spy_df, lookback=60)
    
    # For 'other' stocks, just pass through (Market Regime already applied)
    return True

def simulate_backtest_with_filter(df, spy_df, sector_data, symbol, threshold_pct=0.6):
    """
    Simulate backtest and apply Hybrid Filter.
    Returns: (baseline_trades, filtered_trades, baseline_wr, filtered_wr)
    """
    if df is None or len(df) < 300:
        return 0, 0, 0.0, 0.0
    
    baseline_trades = []
    filtered_trades = []
    
    # Simulate trades using N+1 logic
    for i in range(200, len(df) - 1):
        window = df.iloc[i-200:i]
        
        # Get SPY data up to this point
        current_date = df.index[i]
        spy_up_to_date = spy_df[spy_df.index <= current_date] if spy_df is not None else pd.DataFrame()
        
        # Get sector data up to this point
        sector_up_to_date = {}
        for sector, sdf in sector_data.items():
            sector_up_to_date[sector] = sdf[sdf.index <= current_date]
        
        # Use simple pattern detection (simplified N+1 logic)
        try:
            results = analyze_asset(window, fixed_threshold=threshold_pct)
            if not results:
                continue
            
            best_pattern = results[0]
            direction = 'UP' if best_pattern.get('avg_return', 0) > 0 else 'DOWN'
            prob = best_pattern.get('bull_prob', 50) if direction == 'UP' else best_pattern.get('bear_prob', 50)
            
            # Skip low confidence signals
            if prob < 50:
                continue
            
            entry_price = df['close'].iloc[i]
            exit_price = df['close'].iloc[i + 1]
            
            # Determine result
            if direction == 'UP':
                result = 1 if exit_price > entry_price else 0
            else:
                result = 1 if exit_price < entry_price else 0
            
            # Baseline trade
            baseline_trades.append({'direction': direction, 'result': result})
            
            # Apply Hybrid Filter
            df_slice = df.iloc[:i+1]
            if apply_hybrid_filter(direction, df_slice, spy_up_to_date, sector_up_to_date, symbol):
                filtered_trades.append({'direction': direction, 'result': result})
                
        except Exception as e:
            continue
    
    # Calculate win rates
    baseline_wr = sum(t['result'] for t in baseline_trades) / len(baseline_trades) * 100 if baseline_trades else 0
    filtered_wr = sum(t['result'] for t in filtered_trades) / len(filtered_trades) * 100 if filtered_trades else 0
    
    return len(baseline_trades), len(filtered_trades), baseline_wr, filtered_wr

def run_hybrid_test():
    """Main test runner."""
    print("=" * 70)
    print("🔬 HYBRID FILTER BACKTEST (5000 Bars)")
    print("=" * 70)
    
    tv = TvDatafeed()
    
    # Test stocks (mix of Tech and Defensive)
    test_stocks = [
        {'symbol': 'AAPL', 'exchange': 'NASDAQ'},
        {'symbol': 'MSFT', 'exchange': 'NASDAQ'},
        {'symbol': 'NVDA', 'exchange': 'NASDAQ'},
        {'symbol': 'GOOGL', 'exchange': 'NASDAQ'},
        {'symbol': 'AMD', 'exchange': 'NASDAQ'},
        {'symbol': 'TXN', 'exchange': 'NASDAQ'},
        {'symbol': 'PEP', 'exchange': 'NASDAQ'},
        {'symbol': 'KO', 'exchange': 'NYSE'},
        {'symbol': 'JNJ', 'exchange': 'NYSE'},
        {'symbol': 'AMGN', 'exchange': 'NASDAQ'},
    ]
    
    # Fetch SPY
    print("\n📊 Fetching SPY (5000 bars)...")
    spy_df = tv.get_hist(symbol='SPY', exchange='AMEX', interval=Interval.in_daily, n_bars=5000)
    time.sleep(0.5)
    
    # Fetch sector ETFs
    print("📊 Fetching Sector ETFs (5000 bars)...")
    sector_data = {}
    for sector in ['XLK', 'XLV', 'XLF', 'XLY', 'XLP']:
        df = tv.get_hist(symbol=sector, exchange='AMEX', interval=Interval.in_daily, n_bars=5000)
        if df is not None:
            sector_data[sector] = df
        time.sleep(0.3)
    
    # Results
    results = []
    
    print(f"\n🚀 Running backtest on {len(test_stocks)} stocks...")
    print("-" * 70)
    
    for i, stock in enumerate(test_stocks):
        symbol = stock['symbol']
        exchange = stock['exchange']
        stock_type = get_stock_type(symbol)
        
        print(f"   [{i+1}/{len(test_stocks)}] {symbol} ({stock_type})...", end=" ")
        
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=5000)
        
        if df is None or len(df) < 500:
            print("❌ Skip (No Data)")
            continue
        
        baseline_count, filtered_count, baseline_wr, filtered_wr = simulate_backtest_with_filter(
            df, spy_df, sector_data, symbol
        )
        
        improvement = filtered_wr - baseline_wr
        
        results.append({
            'symbol': symbol,
            'type': stock_type,
            'baseline_trades': baseline_count,
            'baseline_wr': baseline_wr,
            'filtered_trades': filtered_count,
            'filtered_wr': filtered_wr,
            'improvement': improvement
        })
        
        icon = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
        print(f"Base: {baseline_wr:.1f}% → Hybrid: {filtered_wr:.1f}% {icon} ({improvement:+.1f}%)")
        
        time.sleep(0.5)
    
    # Summary
    df_results = pd.DataFrame(results)
    
    print("\n" + "=" * 70)
    print("📈 SUMMARY RESULTS")
    print("=" * 70)
    
    avg_baseline = df_results['baseline_wr'].mean()
    avg_filtered = df_results['filtered_wr'].mean()
    avg_improvement = df_results['improvement'].mean()
    
    print(f"\n{'Metric':<30} {'Baseline':<15} {'Hybrid Filter':<15} {'Change':<10}")
    print("-" * 70)
    print(f"{'Average Win Rate':<30} {avg_baseline:<15.1f}% {avg_filtered:<15.1f}% {avg_improvement:+.1f}%")
    print(f"{'Avg Trade Count':<30} {df_results['baseline_trades'].mean():<15.0f} {df_results['filtered_trades'].mean():<15.0f}")
    
    # By stock type
    print("\n📊 By Stock Type:")
    for stock_type in ['tech', 'defensive']:
        subset = df_results[df_results['type'] == stock_type]
        if not subset.empty:
            print(f"   {stock_type.upper()}: {subset['baseline_wr'].mean():.1f}% → {subset['filtered_wr'].mean():.1f}% ({subset['improvement'].mean():+.1f}%)")
    
    # Save results
    output_path = 'data/hybrid_backtest_results.csv'
    df_results.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to {output_path}")
    
    return df_results

if __name__ == "__main__":
    run_hybrid_test()
