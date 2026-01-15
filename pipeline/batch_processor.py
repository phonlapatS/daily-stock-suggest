"""
Batch Processor - ประมวลผลหลายหุ้นพร้อมกัน
Optimization: Rate limiting, Parallel processing, Progress tracking
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import json
from pathlib import Path
from data_cache import OptimizedDataFetcher
from stats_analyzer import StatsAnalyzer
from predictor import HistoricalPredictor
from utils import save_to_json
from config import RESULTS_DIR


class BatchStockProcessor:
    """
    ประมวลผลหลายหุ้นพร้อมกัน พร้อม optimization
    """
    
    def __init__(self, use_cache=True, max_workers=3, rate_limit_seconds=1.0):
        """
        Args:
            use_cache: ใช้ cache หรือไม่
            max_workers: จำนวน threads สูงสุด
            rate_limit_seconds: หน่วงเวลาระหว่างการดึงข้อมูล (เพื่อไม่ให้โดน rate limit)
        """
        self.fetcher = OptimizedDataFetcher(use_cache=use_cache)
        self.max_workers = max_workers
        self.rate_limit_seconds = rate_limit_seconds
        self.results = []
    
    def process_single_stock(self, symbol, exchange, threshold=1.0, n_bars=1250):
        """
        ประมวลผลหุ้นตัวเดียว
        
        Returns:
            dict: ผลลัพธ์การวิเคราะห์
        """
        result = {
            'symbol': symbol,
            'exchange': exchange,
            'status': 'pending',
            'error': None,
            'stats': None,
            'prediction': None
        }
        
        try:
            print(f"   📊 {symbol} ({exchange})...")
            
            # Rate limiting
            time.sleep(self.rate_limit_seconds)
            
            # Fetch data
            df = self.fetcher.fetch_daily_data(symbol, exchange, n_bars=n_bars)
            
            if df is None or df.empty:
                result['status'] = 'failed'
                result['error'] = 'No data'
                return result
            
            # Analyze
            analyzer = StatsAnalyzer(threshold=threshold)
            stats = analyzer.generate_full_report(df)
            
            result['stats'] = {
                'total_days': stats['total_days'],
                'significant_days': stats['total_significant_days'],
                'positive_moves': stats['positive_moves'],
                'negative_moves': stats['negative_moves']
            }
            
            # Predict (if latest movement > threshold)
            latest_change = df.iloc[-1]['pct_change']
            
            if abs(latest_change) >= threshold:
                predictor = HistoricalPredictor(df, threshold=threshold)
                prediction = predictor.predict_tomorrow(latest_change)
                
                result['prediction'] = {
                    'today_change': latest_change,
                    'direction': prediction['prediction']['direction'],
                    'expected_change': prediction['prediction']['expected_change_avg'],
                    'confidence': prediction['prediction']['confidence'],
                    'num_patterns': prediction['evidence']['historical_samples']
                }
            else:
                result['prediction'] = {
                    'today_change': latest_change,
                    'message': 'Below threshold - WAIT & SEE'
                }
            
            result['status'] = 'success'
            
            # บันทึกผลลัพธ์
            save_path = Path(RESULTS_DIR) / f"{symbol}_{exchange}_batch.json"
            save_to_json(result, str(save_path))
            
            print(f"   ✅ {symbol} เสร็จสิ้น")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            print(f"   ❌ {symbol} failed: {e}")
        
        return result
    
    def process_batch(self, stocks_list: List[Dict], threshold=1.0, n_bars=1250):
        """
        ประมวลผลหลายหุ้นพร้อมกัน
        
        Args:
            stocks_list: [{'symbol': 'PTT', 'exchange': 'SET'}, ...]
            threshold: % threshold
            n_bars: จำนวน bars
        
        Returns:
            list: ผลลัพธ์ทั้งหมด
        """
        print("\n" + "="*80)
        print(f"🚀 Batch Processing: {len(stocks_list)} หุ้น")
        print("="*80)
        print(f"⚙️ Settings:")
        print(f"   - Cache: {'✅ ON' if self.fetcher.use_cache else '❌ OFF'}")
        print(f"   - Max workers: {self.max_workers}")
        print(f"   - Rate limit: {self.rate_limit_seconds} วินาที/หุ้น")
        print(f"   - Data bars: {n_bars}")
        print()
        
        start_time = time.time()
        results = []
        
        # ประมวลผลแบบ sequential (ปลอดภัยกว่าสำหรับ API)
        for i, stock in enumerate(stocks_list, 1):
            print(f"\n[{i}/{len(stocks_list)}]", end=" ")
            result = self.process_single_stock(
                stock['symbol'],
                stock['exchange'],
                threshold=threshold,
                n_bars=n_bars
            )
            results.append(result)
        
        elapsed = time.time() - start_time
        
        # สรุปผลลัพธ์
        self._print_summary(results, elapsed)
        
        return results
    
    def _print_summary(self, results, elapsed):
        """
        แสดงสรุปผลลัพธ์
        """
        success = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        # หุ้นที่มี prediction signal
        with_signals = [r for r in results if r['status'] == 'success' and 
                       r['prediction'] and 'direction' in r['prediction']]
        
        print("\n" + "="*80)
        print("📊 BATCH PROCESSING SUMMARY")
        print("="*80)
        print(f"\n⏱️ เวลาทั้งหมด: {elapsed:.1f} วินาที ({elapsed/60:.1f} นาที)")
        print(f"   - เฉลี่ย: {elapsed/len(results):.1f} วินาที/หุ้น")
        
        print(f"\n📈 สถานะ:")
        print(f"   - ✅ สำเร็จ: {success}/{len(results)}")
        print(f"   - ❌ ล้มเหลว: {failed}/{len(results)}")
        
        print(f"\n🔮 Prediction Signals:")
        print(f"   - มี signal: {len(with_signals)} หุ้น")
        
        if with_signals:
            print(f"\n   📋 รายการ:")
            for r in with_signals[:10]:  # แสดง 10 อันดับแรก
                pred = r['prediction']
                print(f"   - {r['symbol']:6s}: {pred['direction']:8s} "
                      f"{pred['expected_change']:+6.2f}% "
                      f"(confidence: {pred['confidence']:5.1f}%, "
                      f"patterns: {pred['num_patterns']})")
            
            if len(with_signals) > 10:
                print(f"   ... และอีก {len(with_signals) - 10} หุ้น")
        
        print("\n" + "="*80)


# Example usage
if __name__ == "__main__":
    from config import DEFAULT_STOCKS, EXCHANGES
    
    # เลือกหุ้นที่จะวิเคราะห์
    test_stocks = [
        {'symbol': 'PTT', 'exchange': 'SET'},
        {'symbol': 'CPALL', 'exchange': 'SET'},
        {'symbol': 'AOT', 'exchange': 'SET'},
        {'symbol': 'AAPL', 'exchange': 'NASDAQ'},
        {'symbol': 'MSFT', 'exchange': 'NASDAQ'},
    ]
    
    # สร้าง processor
    processor = BatchStockProcessor(
        use_cache=True,
        max_workers=3,
        rate_limit_seconds=0.5  # หน่วง 0.5 วินาที
    )
    
    # ประมวลผล
    results = processor.process_batch(
        test_stocks,
        threshold=1.0,
        n_bars=1000  # ลดลงเพื่อทดสอบเร็วขึ้น
    )
    
    # ผลลัพธ์ถูกบันทึกใน results/ แล้ว
    print(f"\n💾 ผลลัพธ์ถูกบันทึกใน: {RESULTS_DIR}")
