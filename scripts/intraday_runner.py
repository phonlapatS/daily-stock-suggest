
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
    
    # Target Groups: C (30m) & D (15m)
    target_groups = ["GROUP_C_METALS", "GROUP_D_METALS_15M"]
    
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
                    
                # Analyze
                results = analyze_asset(df, symbol=symbol)
                
                if not results:
                    continue
                    
                # Check for High Probability Setup
                for res in results:
                    # Filter: Prob > 60%
                    if res['prob'] >= 60.0:
                        found_any = True
                        print(f"   🚀 SIGNAL FOUND: {symbol} ({interval_str})")
                        print(f"      Pattern: {res['pattern']}")
                        print(f"      Forecast: {res['forecast']} (Prob: {res['prob']:.1f}%)")
                        print(f"      Stats: AvgWin {res['avg_win']:.2f}% | AvgLoss {res['avg_loss']:.2f}%")
                        print(f"      RR Ratio: {res['rr_ratio']:.2f}")
                        print(f"      Matches: {res['matches_found']}")
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
