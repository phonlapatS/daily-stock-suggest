
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')

# Thresholds from Analysis Phase
THRESHOLDS = {
    'XAUUSD_15m': 0.0018,  # 0.18%
    'XAUUSD_30m': 0.0023,  # 0.23%
    'XAGUSD_15m': 0.0049,  # 0.49%
    'XAGUSD_30m': 0.0051   # 0.51%
}

def load_data(filename):
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    df = pd.read_csv(filepath, parse_dates=['datetime'], index_col='datetime')
    return df

def backtest_strategy(df, threshold, strategy_type='TREND', holding_period=1):
    """
    Backtest specific strategy on dataframe
    strategy_type: 'TREND' (Follow) or 'REVERSION' (Fade)
    holding_period: Number of bars to hold
    """
    close = df['close']
    pct_change = close.pct_change()
    
    signals = pd.Series(0, index=df.index)
    
    # 1. Generate Signals based on Threshold
    # +1 = Bullish Signal, -1 = Bearish Signal
    
    if strategy_type == 'TREND':
        # Breakout: If > Threshold => BUY
        signals[pct_change > threshold] = 1
        signals[pct_change < -threshold] = -1
    else: # REVERSION
        # Fade: If > Threshold => SELL
        signals[pct_change > threshold] = -1
        signals[pct_change < -threshold] = 1
        
    # 2. Calculate Returns
    # We enter on the Close of the signal bar (assuming we reacted to the move)
    # OR we enter on Open of next bar. Let's use Open of next bar for realism.
    # Future return = (Close[i+holding] - Open[i+1]) / Open[i+1]
    
    # Actually, simpler logic for "Pattern Engine" equivalent:
    # We see a big move at Close[i]. We bet on direction for next N bars.
    # Return = (Close[i+N] - Close[i]) / Close[i] * Direction
    
    future_returns = close.shift(-holding_period) / close - 1
    strategy_returns = signals * future_returns
    
    # Filter for trades only
    trades = strategy_returns[signals != 0].dropna()
    
    if len(trades) == 0:
        return {
            'N': 0, 'Win%': 0, 'AvgWin': 0, 'AvgLoss': 0, 'RRR': 0, 'Total': 0
        }
    
    wins = trades[trades > 0]
    losses = trades[trades <= 0]
    
    win_rate = len(wins) / len(trades) * 100
    avg_win = wins.mean() * 100 if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) * 100 if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    total_return = trades.sum() * 100
    
    return {
        'N': len(trades),
        'Win%': win_rate,
        'AvgWin': avg_win,
        'AvgLoss': avg_loss,
        'RRR': rrr,
        'Total': total_return
    }

def main():
    print("⚔️  METALS BATTLE: Trend vs Mean Reversion")
    print("=" * 65)
    print(f"{'Asset':<12} {'TF':<5} {'Strategy':<12} {'N':<5} {'Win%':<8} {'RRR':<6} {'Total%':<8}")
    print("-" * 65)
    
    best_configs = []
    
    files = [f for f in os.listdir(CACHE_DIR) if 'OANDA' in f and 'csv' in f]
    
    for filename in files:
        key = filename.replace('OANDA_', '').replace('.csv', '')
        if key not in THRESHOLDS: continue
        
        df = load_data(filename)
        threshold = THRESHOLDS[key]
        
        # Test Trend Following
        res_trend = backtest_strategy(df, threshold, strategy_type='TREND', holding_period=1)
        print(f"{key:<12} {key.split('_')[1]:<5} {'TREND':<12} {res_trend['N']:<5} {res_trend['Win%']:<6.1f}   {res_trend['RRR']:<6.2f} {res_trend['Total']:<8.1f}")
        
        # Test Mean Reversion
        res_rev = backtest_strategy(df, threshold, strategy_type='REVERSION', holding_period=1)
        print(f"{key:<12} {key.split('_')[1]:<5} {'REVERSION':<12} {res_rev['N']:<5} {res_rev['Win%']:<6.1f}   {res_rev['RRR']:<6.2f} {res_rev['Total']:<8.1f}")
        
        # Pick Winner
        if res_trend['Total'] > res_rev['Total']:
            best_configs.append((key, 'TREND', res_trend))
        else:
            best_configs.append((key, 'REVERSION', res_rev))
            
    print("=" * 65)
    print("\n🏆 WINNERS CIRCLE (Optimization Results):")
    for asset, strategy, stats in best_configs:
         print(f"✅ {asset}: Best is {strategy} (Win: {stats['Win%']:.1f}%, Return: {stats['Total']:.1f}%)")

if __name__ == "__main__":
    main()
