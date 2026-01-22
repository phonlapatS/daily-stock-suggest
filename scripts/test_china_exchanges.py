from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()

test_assets = [
    {'symbol': '600519', 'exchange': 'SSE', 'name': 'Moutai (Shanghai)'},
    {'symbol': '000858', 'exchange': 'SZSE', 'name': 'Wuliangye (Shenzhen)'},
    {'symbol': '700', 'exchange': 'HKEX', 'name': 'Tencent (Hong Kong)'},
    {'symbol': '2330', 'exchange': 'TWSE', 'name': 'TSMC (Taiwan)'}
]

print("🚀 Testing Chinese Market Connectivity...")

for asset in test_assets:
    print(f"\nTesting {asset['name']} ({asset['symbol']} @ {asset['exchange']})...")
    try:
        df = tv.get_hist(symbol=asset['symbol'], exchange=asset['exchange'], interval=Interval.in_daily, n_bars=10)
        if df is not None and not df.empty:
            print(f"✅ Success! Got {len(df)} bars. Last Close: {df['close'].iloc[-1]}")
        else:
            print("❌ Failed: No data returned (Empty DF).")
    except Exception as e:
        print(f"❌ Error: {e}")
