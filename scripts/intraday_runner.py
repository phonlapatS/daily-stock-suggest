
import sys
import os
import time
import pandas as pd
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# Configure paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from processor import analyze_asset

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_intraday_scan(tv):
    print(f"\n========================================================")
    print(f"⏰ INTRADAY SCAN: {get_timestamp()}")
    print(f"========================================================")
    
    # Target Groups: Split Gold/Silver with Optimized Thresholds
    target_groups = [
        "GROUP_C1_GOLD_30M", 
        "GROUP_C2_GOLD_15M", 
        "GROUP_D1_SILVER_30M", 
        "GROUP_D2_SILVER_15M"
    ]
    
    found_any = False
    
    for group_key in target_groups:
        group_conf = config.ASSET_GROUPS[group_key]
        interval = group_conf['interval']
        interval_str = "15m" if interval == Interval.in_15_minute else "30m"
        
        print(f"🔎 Scanning {group_key} ({interval_str})...")
        
        for asset in group_conf['assets']:
            symbol = asset['symbol']
            exchange = asset['exchange']
            
            try:
                # Fetch recent data (need enough for pattern matching)
                df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=500)
                
                if df is None or df.empty:
                    continue
                
                # Get fixed_threshold from config (if exists)
                fixed_thresh = group_conf.get('fixed_threshold', None)
                
                # Analyze with threshold override
                results = analyze_asset(df, symbol=symbol, fixed_threshold=fixed_thresh)
                
                if not results:
                    continue
                    
                # Check for Market Probability Setup (Intraday is Noisy, so > 50% is enough)
                for res in results:
                    # Filter: Prob > 50% (Specific for XAU/XAG Intraday Scalping)
                    if res['prob'] >= 50.0:
                        found_any = True
                        print(f"   🚀 ALERT: {symbol} ({interval_str}) | {res['forecast']} | Prob: {res['prob']:.1f}%")
                        print(f"      👉 Action: Scalp {res['forecast']} on Next Candle")
                        print(f"      Pattern: {res['pattern']} (Matches: {res['matches_found']})")
                        print(f"      Stats: AvgWin {res['avg_win']:.2f}% | AvgLoss {res['avg_loss']:.2f}% | RR: {res['rr_ratio']:.2f}")
                        print("-" * 40)
                        
            except Exception as e:
                print(f"   ❌ Error {symbol}: {e}")
                
    if not found_any:
        print("   ✅ No high-probability setups found this round.")

def main():
    print("🚀 STARTING INTRADAY MONITOR (GOLD/SILVER)...")
    print("Press Ctrl+C to stop.")
    
    tv = TvDatafeed()
    
    try:
        while True:
            try:
                run_intraday_scan(tv)
            except Exception as e:
                print(f"❌ Critical Error in Scan Loop: {e}")
                
            # Sleep for 5 minutes before next check
            # (Markets move every minute, but 5m check is sufficient for 15m candles)
            next_scan = 300
            print(f"\n💤 Sleeping {next_scan}s (Next scan in 5 mins)...")
            time.sleep(next_scan)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor Stopped by User.")

if __name__ == "__main__":
    main()
