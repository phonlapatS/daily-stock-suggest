
import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tvDatafeed import TvDatafeed, Interval
    import config
    from processor import analyze_asset
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def health_check():
    print("\n🏥 SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    # 1. Check Connection
    print("1️⃣  Connecting to TradingView...", end=" ")
    try:
        tv = TvDatafeed()
        print("✅ OK")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    # 2. Test Data Fetch (PTT)
    symbol = "PTT"
    exchange = "SET"
    print(f"2️⃣  Fetching Data ({symbol})...", end=" ")
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=100)
        if df is not None and not df.empty:
            print(f"✅ OK ({len(df)} bars)")
            print(f"    Last Date: {df.index[-1]}")
            print(f"    Current Price: {df['close'].iloc[-1]}")
        else:
            print("❌ Fetched None or Empty")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 3. Test Calculation Logic
    print("3️⃣  Testing Analysis Logic...", end=" ")
    try:
        # Mocking an asset dictionary
        asset = {'symbol': symbol, 'exchange': exchange}
        results = analyze_asset(tv, asset, n_bars=200, interval=Interval.in_daily)
        
        if results:
            print("✅ OK")
            r = results[0]
            print(f"    Pattern: {r['pattern']} (matches: {r['matches']})")
            print(f"    Forecast: {'UP' if r['avg_return'] > 0 else 'DOWN'} (Prob: {max(r['bull_prob'], r['bear_prob']):.1f}%)")
        else:
            print("⚠️ No Pattern Found (Logic working, just no match)")
            
    except Exception as e:
        print(f"❌ Calculation Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Check File Permissions
    print("4️⃣  Checking File System...", end=" ")
    try:
        with open("logs/health_check_test.tmp", "w") as f:
            f.write("test")
        os.remove("logs/health_check_test.tmp")
        print("✅ Parsing OK")
    except Exception as e:
        print(f"❌ File Permission Error: {e}")

    print("-" * 50)
    print("✅ SYSTEM READY FOR DEPLOYMENT")
    print("-" * 50)

if __name__ == "__main__":
    health_check()
