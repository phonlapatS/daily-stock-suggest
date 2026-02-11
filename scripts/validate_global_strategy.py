
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
# Add parent dir to path to import scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from scripts.backtest import backtest_single

# Suppression helper
class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def run_validation():
    print("\n🌍 GLOBAL STRATEGY VALIDATION (Inverse Logic) 🌍")
    print("=" * 70)
    print(f"{'Group':<15} | {'Asset':<10} | {'Mode':<10} | {'Acc %':<10} | {'Trades':<8}")
    print("-" * 70)
    
    tv = TvDatafeed()
    bars = 500
    
    summary_stats = []

    # 1. US Markets (Compare Fixed 0.6 vs Dynamic)
    # Correct Key: GROUP_B_US
    us_assets = config.ASSET_GROUPS['GROUP_B_US']['assets']
    
    # Remove duplicates
    seen = set()
    unique_us = []
    for a in us_assets:
        if a['symbol'] not in seen:
            unique_us.append(a)
            seen.add(a['symbol'])
            
    print(f"👉 TESTING US MARKETS ({len(unique_us)} Symbols) - Comparing Fixed vs Dynamic")
    
    us_fixed_results = []
    us_dynamic_results = []
    
    for asset in unique_us:
        symbol = asset['symbol']
        exchange = asset['exchange']
        
        # Test Fixed 0.6
        try:
            with SuppressPrint():
                res_f = backtest_single(tv, symbol, exchange, n_bars=bars, fixed_threshold=0.6, inverse_logic=True, verbose=False)
            if res_f: 
                us_fixed_results.append(res_f['accuracy'])
        except: pass
        
        # Test Dynamic
        try:
            with SuppressPrint():
                res_d = backtest_single(tv, symbol, exchange, n_bars=bars, fixed_threshold=None, inverse_logic=True, verbose=False)
            if res_d:
                us_dynamic_results.append(res_d['accuracy'])
                print(f"{'US (Dynamic)':<15} | {symbol:<10} | {'Dynamic':<10} | {res_d['accuracy']:.1f}% | {res_d['total']}")
        except: pass

    # 2. China/Asian Markets (Test Configured Fixed)
    other_groups = ['GROUP_E_CHINA_ADR', 'GROUP_F_CHINA_A', 'GROUP_G_HK_TECH', 'GROUP_H_TAIWAN']
    
    for group_key in other_groups:
        if group_key not in config.ASSET_GROUPS: continue
        
        group = config.ASSET_GROUPS[group_key]
        desc = group['description']
        fixed_th = group.get('fixed_threshold')
        
        print(f"👉 TESTING {desc} (Fixed {fixed_th}%)")
        
        grp_results = []
        for asset in group['assets']:
            symbol = asset['symbol']
            exchange = asset['exchange']
            
            try:
                with SuppressPrint():
                    # Use Configured Threshold (Fixed)
                    res = backtest_single(tv, symbol, exchange, n_bars=bars, fixed_threshold=fixed_th, inverse_logic=True, verbose=False)
                if res:
                    grp_results.append(res['accuracy'])
                    print(f"{group_key:<15} | {symbol:<10} | {f'Fixed {fixed_th}':<10} | {res['accuracy']:.1f}% | {res['total']}")
            except: pass
            
        if grp_results:
            summary_stats.append({
                'group': group_key,
                'avg_acc': np.mean(grp_results),
                'mode': f"Fixed {fixed_th}%"
            })

    # Summary Output
    print("\n" + "=" * 70)
    print("📊 AGGREGATE SUMMARY")
    print("=" * 70)
    
    # US Comparison
    avg_us_fixed = np.mean(us_fixed_results) if us_fixed_results else 0
    avg_us_dynamic = np.mean(us_dynamic_results) if us_dynamic_results else 0
    
    print(f"🇺🇸 US MARKET (Inverse Strategy):")
    print(f"   - Fixed 0.6% Acc:    {avg_us_fixed:.1f}%")
    print(f"   - Dynamic 1.25SD Acc: {avg_us_dynamic:.1f}%  <-- WINNER? {'✅' if avg_us_dynamic > avg_us_fixed else '❌'}")
    
    # Others
    print(f"\n🌏 ASIAN MARKETS (Inverse Strategy):")
    for stat in summary_stats:
        print(f"   - {stat['group']:<15}: {stat['avg_acc']:.1f}% ({stat['mode']})")
        
    print("=" * 70)

if __name__ == "__main__":
    run_validation()
