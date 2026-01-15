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
                res = processor.analyze_asset(df)
                if res and res['status'] == 'MATCH_FOUND':
                    res['symbol'] = symbol
                    return res
                return None
        except Exception as e:
            time.sleep(1)
            
    return None


from tabulate import tabulate


from tabulate import tabulate

def generate_report(results):
    print("\n" + "="*80)
    print("📊 FRACTAL PREDICTION REPORT")
    print("="*80)
    
    # Define Columns
    headers = ["Symbol", "Price", "Streak", "Predict", "Exp. %Chg", "Prob.", "Max Risk", "Events"]
    
    groups = {
        "GROUP_A_THAI": "🇹🇭 THAI MARKET (SET100+)",
        "GROUP_B_US": "🇺🇸 US MARKET (NASDAQ)",
        "GROUP_C_METALS": "⚡ INTRADAY METALS (Gold/Silver)"
    }
    
    for group_key, title in groups.items():
        # 1. Filter Logic: Events >= 5
        group_data = [r for r in results if r['group'] == group_key and r['matches'] >= 5]
        
        if not group_data:
            continue
            
        print(f"\n{title}")
        table_rows = []
        
        # Sort by: 1. Probability (Dominant) DESC, 2. Events DESC
        def get_sort_key(x):
            avg_ret = x['avg_return']
            if avg_ret > 0: prob = x['bull_prob']
            elif avg_ret < 0: prob = x['bear_prob']
            else: prob = 50.0
            return (prob, x['matches'])

        group_data.sort(key=get_sort_key, reverse=True)
        
        for r in group_data:
            # Logic: Predict based on Mean Return
            avg_ret = r['avg_return']
            if avg_ret > 0:
                predict = "🟢 UP"
                prob_val = r['bull_prob']
            elif avg_ret < 0:
                predict = "🔴 DOWN"
                prob_val = r['bear_prob']
            else:
                predict = "⚪ NEUTRAL"
                prob_val = 50.0
                
            # Logic: Streak Icon
            s_val = r['streak']
            if s_val > 0: s_str = f"🟢 Up {s_val}"
            elif s_val < 0: s_str = f"🔴 Down {abs(s_val)}"
            else: s_str = "⚪ Quiet"
            
            # Format row
            row = [
                r['symbol'],
                f"{r['price']:.2f}",
                s_str,
                predict,
                f"{avg_ret:+.2f}%",     # Signed Exp. %Chg
                f"{prob_val:.0f}%",     # Dominant Prob
                f"{r['max_risk']:.2f}%",
                r['matches']
            ]
            table_rows.append(row)
            
        print(tabulate(table_rows, headers=headers, tablefmt="simple", stralign="right"))
        print("-" * 80)

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
            
            res = fetch_and_analyze(tv, asset, history, interval)
            
            if res:
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
