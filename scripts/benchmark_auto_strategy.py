"""
Auto-Strategy Benchmark: ทดสอบระบบ Auto-Classification
เปรียบเทียบผลลัพธ์ระหว่าง Manual Config vs Auto-Classification
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed
from scripts.backtest import backtest_single
from core.market_classifier import get_auto_strategy
import time

def run_auto_benchmark():
    """
    ทดสอบระบบ Auto-Classification กับ 10 หุ้น US
    """
    stocks = [
        'NVDA', 'TSLA', 'AMD', 'AAPL', 'MSFT',
        'GOOGL', 'META', 'AMZN', 'NFLX', 'INTC'
    ]
    
    tv = TvDatafeed()
    results = []
    
    print("=" * 80)
    print("AUTO-CLASSIFICATION BENCHMARK")
    print("=" * 80)
    print(f"Testing {len(stocks)} stocks with Auto Strategy Selection\n")
    
    for i, symbol in enumerate(stocks, 1):
        print(f"[{i}/{len(stocks)}] Processing {symbol}...")
        
        try:
            # 1. ดึงข้อมูล
            df = tv.get_hist(symbol, 'NASDAQ', n_bars=500)
            if df is None:
                print(f"   ❌ No data")
                continue
            
            # 2. Auto-Classify Strategy
            strategy = get_auto_strategy(symbol, df, 'NASDAQ', verbose=False)
            
            # 3. Run Backtest with Auto Strategy
            res = backtest_single(
                tv, symbol, 'NASDAQ', 
                n_bars=500,
                fixed_threshold=strategy['fixed_threshold'],
                inverse_logic=strategy['inverse_logic'],
                verbose=False
            )
            
            if res:
                results.append({
                    'symbol': symbol,
                    'category': strategy['category'],
                    'volatility': strategy['volatility'],
                    'strategy': f"{'Inverse' if strategy['inverse_logic'] else 'Direct'} + "
                               f"{'Dynamic' if strategy['fixed_threshold'] is None else 'Fixed'}",
                    'accuracy': res['accuracy'],
                    'trades': res['total']
                })
                print(f"   ✅ {strategy['category']}: {res['accuracy']:.1f}% ({res['total']} trades)")
            else:
                print(f"   ❌ Backtest failed")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Print Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n{'Stock':<8} | {'Category':<18} | {'Vol%':<6} | {'Strategy':<20} | {'Acc%':<6} | {'Trades':<6}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['symbol']:<8} | {r['category']:<18} | {r['volatility']:<6.2f} | {r['strategy']:<20} | {r['accuracy']:<6.1f} | {r['trades']:<6}")
    
    # Group by Category
    if results:
        print("\n" + "=" * 80)
        print("PERFORMANCE BY CATEGORY")
        print("=" * 80)
        
        categories = {}
        for r in results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r['accuracy'])
        
        for cat, accs in categories.items():
            avg_acc = sum(accs) / len(accs)
            print(f"{cat:<18}: {avg_acc:.1f}% average ({len(accs)} stocks)")
        
        # Overall
        overall_avg = sum(r['accuracy'] for r in results) / len(results)
        print(f"\n{'OVERALL AVERAGE':<18}: {overall_avg:.1f}%")
        print("=" * 80)
        
        # Compare with Manual Config (from previous benchmark)
        print("\n📊 COMPARISON WITH MANUAL CONFIG:")
        print(f"   Manual Fixed 0.6%:  48.9%")
        print(f"   Manual Dynamic:     49.3%")
        print(f"   Auto-Classification: {overall_avg:.1f}%")
        
        if overall_avg > 49.3:
            print(f"\n✅ Auto-Classification WINS! (+{overall_avg - 49.3:.1f}% improvement)")
        else:
            print(f"\n⚠️  Auto-Classification: {overall_avg:.1f}% (comparable to manual)")

if __name__ == "__main__":
    run_auto_benchmark()
