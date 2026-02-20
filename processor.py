
"""
processor.py - Core Logic for Fractal N+1 Prediction (Pattern-Based Edition)
==============================================================================
Implements:
1. Pattern Detection (Find all unique patterns in history)
2. Pattern-Specific Statistics (Each pattern gets its own Prob/Stats)
3. Volatility-Based Threshold
"""

import pandas as pd
import numpy as np
import config
import time
from core.engines.reversion_engine import MeanReversionEngine
from core.engines.trend_engine import TrendMomentumEngine

# Initialize Engines
engines = {
    'MEAN_REVERSION': MeanReversionEngine(),
    'TREND_MOMENTUM': TrendMomentumEngine()
}

def analyze_asset(df, symbol=None, exchange=None, fixed_threshold=None, engine_type=None):
    """
    Router function that delegates analysis to the appropriate specialized engine.
    """
    try:
        if df is None:
            return []
            
        # V4.9.5: Ensure only clean (filtered) bars are counted and analyzed
        df = df.dropna()
        
        if len(df) < 50:
            return []
            
        # Determine Engine to use
        # Priority: 1. passed engine_type, 2. config based on symbol, 3. Default (MEAN_REVERSION)
        selected_engine_type = engine_type
        settings = {'fixed_threshold': fixed_threshold, 'exchange': exchange or ''}
        
        if not selected_engine_type and symbol:
            # Look up engine in config ASSET_GROUPS
            for group_name, group_config in config.ASSET_GROUPS.items():
                asset_symbols = [a['symbol'] for a in group_config['assets']]
                if symbol in asset_symbols:
                    selected_engine_type = group_config.get('engine')
                    # Inherit settings from group if not explicitly passed
                    if settings.get('fixed_threshold') is None:
                        settings['fixed_threshold'] = group_config.get('fixed_threshold')
                    
                    # V4.2: Explicitly pass the market floor (min_threshold)
                    settings['min_threshold'] = group_config.get('min_threshold')
                    
                    # Inherit exchange from config if not explicitly passed
                    if not exchange:
                        for a in group_config['assets']:
                            if a['symbol'] == symbol:
                                settings['exchange'] = a.get('exchange', '')
                                break
                    break
        
        selected_engine_type = selected_engine_type or 'MEAN_REVERSION'
        engine = engines.get(selected_engine_type, engines['MEAN_REVERSION'])
        
        # Delegate to specialized engine
        engine_results = engine.analyze(df, symbol, settings)
        
        # Post-process results for reporting consistency
        formatted_results = []
        for res in engine_results:
            # Derive avg_return direction from forecast
            # If UP forecast: avg_return positive, bull_prob = prob, bear_prob = 100-prob
            # If DOWN forecast: avg_return negative, bear_prob = prob, bull_prob = 100-prob
            is_up = (res['forecast'] == 'UP')
            prob_val = res['prob']
            
            formatted_results.append({
                'status': 'MATCH_FOUND',
                'symbol': symbol or 'Unknown',
                'price': df['close'].iloc[-1],
                'is_tradeable': res['is_tradeable'],
                'acc_score': prob_val,
                'rr_score': res['rr'],
                'change_pct': ((df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1]) * 100,
                'pattern_display': res['pattern'],
                'pattern': res['pattern'], # Compatibility key for main.py
                'matches': res['matches'],
                'forecast_dir': 1 if is_up else -1,
                'forecast_label': res['forecast'],
                'strategy_name': f"{res['engine']} ({'REVERSAL' if res.get('is_reversal') else 'TREND' if res.get('is_trend_follow') else 'DATA'})",
                'confidence': (prob_val - 50) * 2,
                # Compatibility keys for generate_report
                'avg_return': res['rr'] if is_up else -res['rr'],
                'bull_prob': prob_val if is_up else (100 - prob_val),
                'bear_prob': (100 - prob_val) if is_up else prob_val,
                'threshold': res.get('threshold', 0),
                'avg_win': res.get('avg_win', 0),
                'avg_loss': res.get('avg_loss', 0),
                'total_bars': len(df)
            })
            
        # ---------------------------------------------------------
        # V8.0: ANTI-OVERLAPPING (Best Fit Selection)
        # ---------------------------------------------------------
        # User Req: Select ONLY ONE pattern per symbol (The most confident one)
        # Logic: 
        # 1. Sort by Probability (Confidence) DESC
        # 2. Sort by Pattern Length DESC (Tie-breaker)
        # 3. Return top 1
        
        if not formatted_results:
            return []
            
        # Sort: Acc Score (Prob) DESC, Pattern Length DESC
        formatted_results.sort(key=lambda x: (-x['acc_score'], -len(x['pattern'])))
        
        # Select Top 1
        best_fit = [formatted_results[0]]
        
        return best_fit

    except Exception as e:
        print(f"❌ Error in modular analysis for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return []
