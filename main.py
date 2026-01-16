#!/usr/bin/env python
"""
main.py - Fractal N+1 Prediction Runner (Categorized Edition)
=============================================================
Orchestrates the entire pipeline: 
Fetch -> Process -> Categorize -> Report -> Forget.
"""
import sys
import time
import pandas as pd
from tvDatafeed import TvDatafeed
import config
import processor

def fetch_and_analyze(tv, asset_info, history_bars, interval):
    symbol = asset_info['symbol']
    exchange = asset_info['exchange']
    
    # Retry Logic for Fetch
    for attempt in range(3):
        try:
            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=history_bars
            )
            if df is not None and not df.empty:
                results_list = processor.analyze_asset(df)  # Returns list now
                # Add symbol to each result
                for res in results_list:
                    res['symbol'] = symbol
                return results_list  # Return all patterns
        except Exception as e:
            time.sleep(1)
            
    return []  # Return empty list on failure


from tabulate import tabulate


from tabulate import tabulate



def generate_report(results):
    print("\n" + "="*95)
    print("📊 FRACTAL PREDICTION REPORT (High Confidence Only)")
    print("="*95)
    
    groups = {
        "GROUP_A_THAI": "🇹🇭 THAI MARKET (SET100+)",
        "GROUP_B_US": "🇺🇸 US MARKET (NASDAQ)",
        "GROUP_C_METALS": "⚡ INTRADAY METALS (Gold/Silver)"
    }
    
    for group_key, title in groups.items():
        # -------------------------------------------------------------
        # 1. Quality Filtering (The Guardrails)
        # -------------------------------------------------------------
        # Rule 1: Minimum Matches >= 10
        # Rule 2: Significance Threshold >= 60% (Prob)
        
        filtered_data = []
        for r in results:
            if r['group'] != group_key: continue
            
            # Identify dominant prob
            avg_ret = r['avg_return']
            if avg_ret > 0: prob = r['bull_prob']
            elif avg_ret < 0: prob = r['bear_prob']
            else: prob = 50.0
            
            # Trust processor.py's adaptive filtering
            # We display EVERYTHING that processor found (Matched logic)
            # No prob threshold (User wants to see raw data)
            
            # Add prob to dict for sorting
            r['_sort_prob'] = prob
            filtered_data.append(r)
        
        if not filtered_data:
            print(f"\n{title}")
            print("   (No high-confidence signals found)")
            continue
            
        print(f"\n{title}")
        
        # -------------------------------------------------------------
        # 2. Sorting (Group by Symbol, then Prob% within symbol)
        # -------------------------------------------------------------
        filtered_data.sort(key=lambda x: (x['symbol'], -x['_sort_prob'], -x['matches']))
        
        
        # 3. Table Layout
        # Columns (Left-to-Right): Symbol, Price, Threshold, Chg%, Pattern, Prob, Stats, Exp.Move
        header = f"{'Symbol':<10} {'Price':>10} {'Threshold':>12} {'Chg%':>10} {'Pattern':^12} {'Prob.':>8} {'Stats':>12} {'Exp. Move':>12}"
        
        print("-" * 95)
        print(header)
        print("-" * 95)

        for r in filtered_data:
            # Logic: Predict & Prob
            avg_ret = r['avg_return']
            if avg_ret > 0:
                # guess = "🟢 UP"  # Hidden
                prob_val = r['bull_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            elif avg_ret < 0:
                # guess = "🔴 DOWN"  # Hidden
                prob_val = r['bear_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            else:
                # guess = "⚪ NEUTRAL"  # Hidden
                prob_val = 50.0
                win_count = 0
            
            # Get hybrid pattern (context + current)
            pattern = r.get('pattern_display', '.')
            
             # Formatting
            price_str = f"{r['price']:,.2f}"
            thresh_str = f"±{r['threshold']:.2f}%"
            chg_str   = f"{r['change_pct']:+.2f}%"
            prob_str  = f"{int(prob_val)}%"
            stats_str = f"{win_count}/{r['matches']}"
            exp_str   = f"{avg_ret:+.2f}%"
            
            # Print Row (Hybrid pattern display)
            print(f"{r['symbol']:<10} {price_str:>10} {thresh_str:>12} {chg_str:>10} {pattern:^12} {prob_str:>8} {stats_str:>12} {exp_str:>12}")

        print("-" * 95)

    print("\n✅ Report Generated.")

def main():
    print("🚀 Starting Fractal N+1 Prediction System...")
    
    # Connect TV
    try:
        tv = TvDatafeed()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    all_results = []
    
    # Iterate through Asset Groups
    for group_name, settings in config.ASSET_GROUPS.items():
        print(f"\n📂 Processing {settings['description']}...")
        
        assets = settings['assets']
        interval = settings['interval']
        history = settings['history_bars']
        
        for i, asset in enumerate(assets):
            sys.stdout.write(f"\r   [{i+1}/{len(assets)}] Scanning {asset['symbol']}...")
            sys.stdout.flush()
            
            pattern_results = fetch_and_analyze(tv, asset, history, interval)
            
            # pattern_results is now a list (can be empty or have multiple items)
            for res in pattern_results:
                res['group'] = group_name
                all_results.append(res)
            
            time.sleep(0.5) # Rate Limit

    # Final Report
    if all_results:
        generate_report(all_results)
    else:
        print("\n❌ No matching patterns found in any asset.")

if __name__ == "__main__":
    main()
