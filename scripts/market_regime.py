
"""
market_regime.py - Market Trend Analysis
========================================
Goal: Determine if the overall market is BULLISH or BEARISH.
Logic:
    - Fetech SPY (S&P 500 ETF) and QQQ (Nasdaq ETF).
    - Calculate SMA 50 and SMA 200.
    - Check if Price > SMA 50/200.
    - Returns: 'BULL' or 'BEAR' status.
"""

import sys
import os
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_market_regime(tv, verbose=True):
    """
    Analyzes Market Regime (SPY, QQQ).
    Returns:
        dict: {
            'status': 'BULL' | 'BEAR' | 'NEUTRAL',
            'spy_trend': 'UP' | 'DOWN',
            'qqq_trend': 'UP' | 'DOWN',
            'details': {...}
        }
    """
    if verbose:
        print("\n🔍 Analyzing Market Regime (S&P 500 & Nasdaq)...")
        
    indices = [
        {'symbol': 'SPY', 'exchange': 'AMEX', 'name': 'S&P 500'},
        {'symbol': 'QQQ', 'exchange': 'NASDAQ', 'name': 'Nasdaq 100'}
    ]
    
    regime_score = 0
    details = {}
    
    for idx in indices:
        try:
            df = tv.get_hist(symbol=idx['symbol'], exchange=idx['exchange'], interval=Interval.in_daily, n_bars=300)
            
            if df is None or df.empty:
                print(f"⚠️ Failed to fetch {idx['symbol']}")
                continue
                
            # Calculate Indicators
            close = df['close']
            sma50 = close.rolling(50).mean()
            sma200 = close.rolling(200).mean()
            
            current_price = close.iloc[-1]
            current_sma50 = sma50.iloc[-1]
            current_sma200 = sma200.iloc[-1]
            
            # Trend Logic
            # Bullish: Price > SMA50 (Short-term strength) AND Price > SMA200 (Long-term strength)
            # Bearish: Price < SMA50
            
            trend = "SIDEWAYS"
            score = 0
            
            if current_price > current_sma50:
                trend = "UP"
                score = 1
                if current_price > current_sma200:
                    score = 2 # Strong Bull
            elif current_price < current_sma50:
                trend = "DOWN"
                score = -1
                if current_price < current_sma200:
                    score = -2 # Strong Bear
            
            regime_score += score
            
            details[idx['symbol']] = {
                'price': current_price,
                'sma50': current_sma50,
                'sma200': current_sma200,
                'trend': trend,
                'score': score
            }
            
            if verbose:
                icon = "🟢" if trend == "UP" else "🔴" if trend == "DOWN" else "⚪"
                print(f"   {icon} {idx['name']} ({idx['symbol']}): Price {current_price:.2f} vs SMA50 {current_sma50:.2f}")
                
        except Exception as e:
            print(f"❌ Error analyzing {idx['symbol']}: {e}")
            
    # Final Decision
    # If Score > 0 -> BULL
    # If Score <= 0 -> BEAR
    
    if regime_score > 0:
        overall_status = "BULL"
    elif regime_score < 0:
        overall_status = "BEAR"
    else:
        overall_status = "NEUTRAL"
        
    if verbose:
        print(f"👉 Market Regime: {overall_status} (Score: {regime_score})")
        
    return {
        'status': overall_status,
        'score': regime_score,
        'details': details
    }

if __name__ == "__main__":
    tv = TvDatafeed()
    get_market_regime(tv)
