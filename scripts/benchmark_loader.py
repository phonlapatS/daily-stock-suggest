
import time
from tvDatafeed import TvDatafeed, Interval

def benchmark_loading():
    tv = TvDatafeed()
    symbol = 'PTT'
    exchange = 'SET'

    print(f"\n⚡ BENCHMARKING DATA LOAD: {symbol} ({exchange})")
    print("=" * 50)

    # 1. OLD METHOD (Full History)
    start = time.time()
    try:
        _ = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=5000)
        dur_full = time.time() - start
        print(f"🔴 OLD (Full 5000 bars):  {dur_full:.4f} seconds")
    except Exception as e:
        print(f"OLD Failed: {e}")
        dur_full = 0

    # 2. NEW METHOD (Incremental)
    start = time.time()
    try:
        _ = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=5)
        dur_inc = time.time() - start
        print(f"🟢 NEW (Last 5 bars):    {dur_inc:.4f} seconds")
    except Exception as e:
        print(f"NEW Failed: {e}")
        dur_inc = 0

    if dur_inc > 0:
        speedup = dur_full / dur_inc
        print("-" * 50)
        print(f"🚀 SPEEDUP FACTOR: {speedup:.1f}x Faster")
        print("=" * 50)

if __name__ == "__main__":
    benchmark_loading()
