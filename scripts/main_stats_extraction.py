"""
Main Execution Script - รัน statistics extraction
Pure data-driven analysis - No ML models
"""

import argparse
from data_fetcher import StockDataFetcher
from stats_analyzer import StatsAnalyzer
from visualizer import StatsVisualizer
from predictor import HistoricalPredictor
from utils import save_to_json, format_stats_report, ensure_directories
from config import RESULTS_DIR, DEFAULT_STOCKS, EXCHANGES
import os


def analyze_single_stock(symbol, exchange, timeframe='daily', interval='15', threshold=1.0, n_bars=5000, predict=False):
    """
    วิเคราะห์หุ้นตัวเดียว
    
    Args:
        symbol: รหัสหุ้น
        exchange: ตลาด
        timeframe: 'daily' หรือ 'intraday'
        interval: '15', '30', '60' (สำหรับ intraday)
        threshold: % threshold
        n_bars: จำนวน bars
        predict: ทำ prediction หรือไม่
    
    Returns:
        dict: statistics report
    """
    print("\n" + "="*70)
    print(f"🎯 ANALYZING {symbol} ({exchange}) - {timeframe.upper()}")
    print("="*70)
    
    # 1. Fetch data
    fetcher = StockDataFetcher()
    
    if timeframe == 'daily':
        df = fetcher.fetch_daily_data(symbol, exchange, n_bars=n_bars)
    else:
        df = fetcher.fetch_intraday_data(symbol, exchange, interval=interval, n_bars=n_bars)
    
    if df is None or df.empty:
        print(f"❌ Failed to fetch data for {symbol}")
        return None
    
    # 2. Analyze statistics
    analyzer = StatsAnalyzer(threshold=threshold)
    stats = analyzer.generate_full_report(df)
    
    # 3. Create visualizations
    visualizer = StatsVisualizer()
    visualizer.create_full_report_plots(df, stats, symbol)
    
    # 4. Prediction (if requested)
    if predict:
        print("\n" + "="*70)
        print("🔮 PREDICTION MODE: Forecasting next day based on latest movement")
        print("="*70)
        
        predictor = HistoricalPredictor(df, threshold=threshold)
        
        # Get latest price change
        latest_change = df.iloc[-1]['pct_change']
        
        if abs(latest_change) >= threshold:
            print(f"\n📊 Latest movement: {latest_change:+.2f}% (triggers prediction)")
            prediction = predictor.predict_tomorrow(latest_change)
            
            # Save prediction
            pred_filename = f"{symbol}_prediction.json"
            pred_filepath = os.path.join(RESULTS_DIR, pred_filename)
            save_to_json(prediction, pred_filepath)
        else:
            print(f"\n⚠️ Latest movement: {latest_change:+.2f}% (below threshold {threshold}%)")
            print("   No prediction needed - wait for significant movement")
    
    # 5. Save results
    filename = f"{symbol}_{timeframe}_stats.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    save_to_json(stats, filepath)
    
    # 6. Print report
    print("\n" + format_stats_report(stats))
    
    return stats



def analyze_multiple_stocks(stocks_list, threshold=1.0):
    """
    วิเคราะห์หลายหุ้นพร้อมกัน
    
    Args:
        stocks_list: list of dicts with 'symbol' and 'exchange'
        threshold: % threshold
    
    Returns:
        dict: results for all stocks
    """
    results = {}
    
    for stock in stocks_list:
        symbol = stock['symbol']
        exchange = stock['exchange']
        
        try:
            stats = analyze_single_stock(symbol, exchange, threshold=threshold)
            results[symbol] = stats
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            results[symbol] = None
    
    return results


def main():
    """
    Main function - รันผ่าน command line
    """
    parser = argparse.ArgumentParser(description='Stock Statistics Extraction - Pure Data-Driven Analysis')
    
    parser.add_argument('--symbol', type=str, help='Stock symbol (e.g., PTT, AAPL)')
    parser.add_argument('--exchange', type=str, help='Exchange (e.g., SET, NASDAQ)')
    parser.add_argument('--market', type=str, choices=['thai', 'us'], help='Market to analyze (all stocks)')
    parser.add_argument('--timeframe', type=str, default='daily', choices=['daily', 'intraday'],
                       help='Timeframe to analyze')
    parser.add_argument('--interval', type=str, default='15', choices=['15', '30', '60'],
                       help='Interval for intraday (minutes)')
    parser.add_argument('--threshold', type=float, default=1.0,
                       help='Percentage threshold for significant moves')
    parser.add_argument('--nbars', type=int, default=5000,
                       help='Number of bars to fetch')
    parser.add_argument('--predict', action='store_true',
                       help='Enable prediction mode (forecast tomorrow based on latest movement)')
    
    args = parser.parse_args()
    
    # สร้าง directories
    ensure_directories()
    
    print("\n" + "="*70)
    print("📈 STOCK STATISTICS EXTRACTION SYSTEM")
    print("🎯 Pure Data-Driven Analysis - No ML Models")
    print("="*70)
    
    if args.symbol and args.exchange:
        # Single stock analysis
        analyze_single_stock(
            symbol=args.symbol,
            exchange=args.exchange,
            timeframe=args.timeframe,
            interval=args.interval,
            threshold=args.threshold,
            n_bars=args.nbars,
            predict=args.predict
        )
    
    elif args.market:
        # Multiple stocks analysis
        if args.market == 'thai':
            stocks = [{'symbol': s, 'exchange': EXCHANGES['thai']} for s in DEFAULT_STOCKS['thai']]
        else:
            stocks = DEFAULT_STOCKS['us']
        
        print(f"\n🔍 Analyzing {len(stocks)} stocks from {args.market.upper()} market...")
        analyze_multiple_stocks(stocks, threshold=args.threshold)
    
    else:
        # Default: analyze sample Thai stocks
        print("\n💡 No arguments provided. Running default analysis on Thai stocks...")
        print("   Use --help to see all options\n")
        
        stocks = [
            {'symbol': 'PTT', 'exchange': 'SET'},
            {'symbol': 'CPALL', 'exchange': 'SET'},
        ]
        
        analyze_multiple_stocks(stocks, threshold=1.0)
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print(f"📁 Results saved to: {RESULTS_DIR}")
    print(f"📊 Plots saved to: plots/")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
