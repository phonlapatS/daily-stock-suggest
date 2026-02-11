
import sys
import os
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

# Load environment variables
load_dotenv()

def fetch_data(tv, symbol, exchange, interval, n_bars=5000):
    print(f"📥 Fetching {symbol} ({exchange}) - Interval: {interval}")
    try:
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=n_bars
        )
        if df is None or df.empty:
            print(f"❌ Failed to fetch data for {symbol}")
            return None
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None

def main():
    username = os.getenv("TV_USERNAME")
    password = os.getenv("TV_PASSWORD")
    
    if not username or not password:
        print("⚠️  TradingView credentials not found in env. Trying anonymous access...")
        tv = TvDatafeed()
    else:
        print(f"🔐 Authenticating with TradingView as {username}...")
        tv = TvDatafeed(username, password)
    
    metals = [
        {'symbol': 'XAUUSD', 'exchange': 'OANDA'},
        {'symbol': 'XAGUSD', 'exchange': 'OANDA'}
    ]
    
    intervals = [
        (Interval.in_15_minute, '15m'),
        (Interval.in_30_minute, '30m')
    ]
    
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    for metal in metals:
        for interval_obj, interval_name in intervals:
            print(f"\n--- Processing {metal['symbol']} [{interval_name}] ---")
            df = fetch_data(tv, metal['symbol'], metal['exchange'], interval_obj)
            
            if df is not None:
                # Save to cache
                filename = f"{metal['exchange']}_{metal['symbol']}_{interval_name}.csv"
                filepath = os.path.join(cache_dir, filename)
                df.to_csv(filepath)
                print(f"✅ Saved {len(df)} bars to {filepath}")
                
                # Show recent data
                print(df.tail(3)[['open', 'high', 'low', 'close', 'volume']])

if __name__ == "__main__":
    main()
