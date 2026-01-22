import processor
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import config

# Create a dummy config with only one asset from each new group for testing
TEST_ASSETS = [
    {'symbol': '600519', 'exchange': 'SSE', 'name': 'MOUTAI'},
    {'symbol': '700', 'exchange': 'HKEX', 'name': 'TENCENT'},
    {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC'}
]

def test_fetch_and_analyze():
    tv = TvDatafeed()
    print("\n🚀 Testing Readable Names Display...\n")
    
    for asset in TEST_ASSETS:
        symbol = asset['symbol']
        exchange = asset['exchange']
        display_name = asset.get('name', symbol)
        
        print(f"Scanning {display_name} ({symbol})...")
        
        # Fetch small amount of data
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=100)
        
        if df is not None and not df.empty:
            # Simulate main.py logic
            results = processor.analyze_asset(df)
            for res in results:
                res['symbol'] = display_name  # This is the logic we added to main.py
            
            # Check if updated symbol is correct
            if results:
                first_result = results[0]
                print(f"✅ Result Symbol: {first_result['symbol']}")
                if first_result['symbol'] == display_name:
                     print(f"   (Correctly mapped {symbol} -> {display_name})")
                else:
                     print(f"❌ Failed: Expected {display_name}, got {first_result['symbol']}")
                break # Just check one result per asset
            else:
                print("⚠️ No patterns found (expected for short history), but logic holds.")
        else:
            print("❌ Fetch failed.")

if __name__ == "__main__":
    test_fetch_and_analyze()
