
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

def analyze_asset(df, symbol=None, fixed_threshold=None, engine_type=None):
    """
    Router function that delegates analysis to the appropriate specialized engine.
    """
    try:
        if df is None or len(df) < 50:
            return []
            
        # Determine Engine to use
        # Priority: 1. passed engine_type, 2. config based on symbol, 3. Default (MEAN_REVERSION)
        selected_engine_type = engine_type
        settings = {'fixed_threshold': fixed_threshold}
        
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
                    break
        
        selected_engine_type = selected_engine_type or 'MEAN_REVERSION'
        engine = engines.get(selected_engine_type, engines['MEAN_REVERSION'])
        
        # Delegate to specialized engine
        engine_results = engine.analyze(df, symbol, settings)
        
        # Post-process results for reporting consistency
        formatted_results = []
        for res in engine_results:
            formatted_results.append({
                'status': 'MATCH_FOUND',
                'symbol': symbol or 'Unknown',
                'price': df['close'].iloc[-1],
                'is_tradeable': res['is_tradeable'],
                'acc_score': res['prob'],
                'rr_score': res['rr'],
                'change_pct': df['close'].pct_change().iloc[-1] * 100,
                'pattern_display': res['pattern'],
                'matches': res['matches'],
                'forecast_dir': 1 if res['forecast'] == 'UP' else -1,
                'forecast_label': res['forecast'],
                'strategy_name': f"{res['engine']} ({'REVERSAL' if res.get('is_reversal') else 'TREND' if res.get('is_trend_follow') else 'DATA'})",
                'confidence': (res['prob'] - 50) * 2
            })
            
        return formatted_results

    except Exception as e:
        print(f"❌ Error in modular analysis for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return []

    except Exception as e:
        return []
