#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backtest_with_volume_filter.py - Backtest with Volume Filter
=================================================
Backtest logic ที่มี risk management และกรองด้วย volume
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engines.reversion_engine import MeanReversionEngine
from core.engines.trend_engine import TrendMomentumEngine
from core.data_cache import get_data_with_cache

class VolumeFilter:
    """Volume filter สำหรับกรองหุ้นที่มี volume สูงพอ"""
    
    def __init__(self, min_volume_ratio=1.0):
        self.min_volume_ratio = min_volume_ratio
    
    def filter_by_volume(self, df, symbol, exchange):
        """กรองหุ้นตาม volume ratio"""
        if len(df) < 20:
            return False
        
        # คำนวณ average volume (20 วัน)
        avg_volume = df['volume'].tail(20).mean()
        current_volume = df['volume'].iloc[-1]
        
        if avg_volume == 0:
            return False
        
        volume_ratio = current_volume / avg_volume
        
        # กรองเฉพาะที่มี volume สูงกว่าค่าเฉลี่ย
        return volume_ratio >= self.min_volume_ratio

class BacktestWithVolumeFilter:
    """Backtest ที่มี volume filter"""
    
    def __init__(self):
        self.engines = {
            'MEAN_REVERSION': MeanReversionEngine(),
            'TREND_MOMENTUM': TrendMomentumEngine()
        }
        self.volume_filter = VolumeFilter(min_volume_ratio=1.2)  # 20% สูงกว่าค่าเฉลี่ย
    
    def backtest_symbol(self, symbol, exchange, engine_type='MEAN_REVERSION'):
        """Backtest หุ้นเดียวพร้อม volume filter"""
        
        try:
            # ดึงข้อมูล
            df = get_data_with_cache(symbol, exchange, "1D")
            
            if df is None or len(df) < 100:
                return None
            
            # ตรวจสอบ volume filter
            if not self.volume_filter.filter_by_volume(df, symbol, exchange):
                return None
            
            # เลือก engine
            engine = self.engines.get(engine_type, self.engines['MEAN_REVERSION'])
            
            # ตั้งค่า settings
            settings = {
                'exchange': exchange,
                'fixed_threshold': None,
                'min_threshold': self._get_min_threshold(exchange)
            }
            
            # วิเคราะห์
            results = engine.analyze(df, symbol, settings)
            
            if not results:
                return None
            
            # กรองผลลัพธ์ที่ดีที่สุด
            best_results = []
            for result in results:
                if self._is_tradeable(result):
                    best_results.append(result)
            
            return best_results
            
        except Exception as e:
            print(f"❌ Error backtesting {symbol}: {e}")
            return None
    
    def _get_min_threshold(self, exchange):
        """กำหนด minimum threshold ตาม exchange"""
        thresholds = {
            'SET': 1.0,
            'NASDAQ': 0.6,
            'TWSE': 0.9,
            'HKEX': 0.7
        }
        return thresholds.get(exchange, 0.8)
    
    def _is_tradeable(self, result):
        """ตรวจสอบว่าเป็น trade ที่น่าสนใจหรือไม่"""
        return (
            result.get('prob', 0) >= 55 and
            result.get('rr', 0) >= 1.3 and
            result.get('matches', 0) >= 20
        )
    
    def backtest_portfolio(self, symbols, exchanges, engine_type='MEAN_REVERSION'):
        """Backtest หลายๆ หุ้น"""
        
        print(f"🔍 Backtesting with Volume Filter")
        print(f"   Engine: {engine_type}")
        print(f"   Volume Filter: ≥{self.volume_filter.min_volume_ratio}x average")
        print("=" * 60)
        
        all_results = []
        total_symbols = len(symbols)
        
        for i, (symbol, exchange) in enumerate(zip(symbols, exchanges)):
            print(f"📊 [{i+1}/{total_symbols}] {symbol} ({exchange})")
            
            results = self.backtest_symbol(symbol, exchange, engine_type)
            
            if results:
                for result in results:
                    result['symbol'] = symbol
                    result['exchange'] = exchange
                    result['engine'] = engine_type
                    all_results.append(result)
                
                print(f"   ✅ Found {len(results)} tradeable patterns")
            else:
                print(f"   ❌ No tradeable patterns")
        
        return all_results
    
    def generate_report(self, results):
        """สร้างรายงานผลการ backtest"""
        
        if not results:
            print("❌ No results to report")
            return
        
        print(f"\n📊 Backtest Results with Volume Filter")
        print("=" * 80)
        
        # แปลงเป็น DataFrame
        df = pd.DataFrame(results)
        
        # แบ่งตาม exchange
        exchanges = df['exchange'].unique()
        
        for exchange in exchanges:
            exchange_data = df[df['exchange'] == exchange]
            
            exchange_names = {
                'SET': '🇹🇭 THAI MARKET',
                'NASDAQ': '🇺🇸 US STOCK',
                'TWSE': '🇹🇼 TAIWAN MARKET',
                'HKEX': '🇭🇰 CHINA & HK MARKET'
            }
            
            print(f"\n{exchange_names.get(exchange, exchange)}")
            print("=" * 60)
            
            # กำหนด criteria ตาม exchange
            prob_threshold = self._get_prob_threshold(exchange)
            rrr_threshold = self._get_rrr_threshold(exchange)
            count_threshold = self._get_count_threshold(exchange)
            
            # กรองตาม criteria
            filtered = exchange_data[
                (exchange_data['prob'] >= prob_threshold) &
                (exchange_data['rr'] >= rrr_threshold) &
                (exchange_data['matches'] >= count_threshold)
            ].copy()
            
            if len(filtered) == 0:
                print("   ❌ No stocks meet criteria")
                continue
            
            # เรียงลำดับตาม prob
            filtered = filtered.sort_values('prob', ascending=False)
            
            print(f"Criteria: Prob ≥ {prob_threshold}% | RRR ≥ {rrr_threshold} | Count ≥ {count_threshold}")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Count':>6} {'Prob%':>7} {'RRR':>6} {'AvgWin%':>9} {'AvgLoss%':>9}")
            print("-" * 60)
            
            for _, row in filtered.iterrows():
                symbol = row['symbol']
                count = row['matches']
                prob = row['prob']
                rrr = row['rr']
                avg_win = row.get('avg_win', 0)
                avg_loss = row.get('avg_loss', 0)
                
                print(f"{symbol:<12} {count:>6} {prob:>7.1f}% {rrr:>6.2f} {avg_win:>9.2f}% {avg_loss:>9.2f}%")
        
        # สรุปโดยรวม
        print(f"\n📈 SUMMARY STATISTICS")
        print("=" * 60)
        
        total_stocks = len(df['symbol'].unique())
        exchanges_count = df['exchange'].value_counts()
        
        print(f"[1] Total stocks passing criteria: {total_stocks} stocks")
        print(f"\n[2] Stocks per country:")
        for exchange, count in exchanges_count.items():
            exchange_names = {
                'SET': 'THAI',
                'NASDAQ': 'US',
                'TWSE': 'TAIWAN',
                'HKEX': 'CHINA/HK'
            }
            print(f"    {exchange_names.get(exchange, exchange)}: {count} stocks")
        
        # หา balanced stocks
        balanced = df[
            (df['prob'] >= 55) &
            (df['rr'] >= 1.5) &
            (df['matches'] >= 30)
        ]
        
        print(f"\n[3] Balanced Stocks (Prob ≥ 55% AND RRR ≥ 1.5 AND Count ≥ 30): {len(balanced)} stocks")
        
        # บันทึกผลลัพธ์
        output_file = "data/backtest_volume_filter_results.csv"
        df.to_csv(output_file, index=False)
        print(f"\n[Detailed report saved to: {output_file}]")
    
    def _get_prob_threshold(self, exchange):
        """กำหนด prob threshold ตาม exchange"""
        thresholds = {
            'SET': 55,
            'NASDAQ': 55,
            'TWSE': 50,
            'HKEX': 50
        }
        return thresholds.get(exchange, 50)
    
    def _get_rrr_threshold(self, exchange):
        """กำหนด RRR threshold ตาม exchange"""
        thresholds = {
            'SET': 1.5,
            'NASDAQ': 1.3,
            'TWSE': 1.0,
            'HKEX': 1.0
        }
        return thresholds.get(exchange, 1.0)
    
    def _get_count_threshold(self, exchange):
        """กำหนด count threshold ตาม exchange"""
        thresholds = {
            'SET': 20,
            'NASDAQ': 20,
            'TWSE': 15,
            'HKEX': 10
        }
        return thresholds.get(exchange, 10)

def main():
    """Main function"""
    
    # ตัวอย่าง symbols
    thai_stocks = ['THG', 'BANPU', 'PTT', 'AOT']
    us_stocks = ['NETEASE', 'ADP', 'AAPL', 'MSFT']
    taiwan_stocks = ['TSMC', 'QUANTA', 'DELTA', 'ASUSTEK']
    china_stocks = ['PINDUODUO', 'NETEASE', 'YUM-CHINA', 'BYD']
    
    # รวม symbols
    all_symbols = thai_stocks + us_stocks + taiwan_stocks + china_stocks
    all_exchanges = ['SET'] * len(thai_stocks) + ['NASDAQ'] * len(us_stocks) + ['TWSE'] * len(taiwan_stocks) + ['HKEX'] * len(china_stocks)
    
    # สร้าง backtester
    backtester = BacktestWithVolumeFilter()
    
    # Backtest
    results = backtester.backtest_portfolio(all_symbols, all_exchanges, 'MEAN_REVERSION')
    
    # สร้างรายงาน
    backtester.generate_report(results)

if __name__ == "__main__":
    main()
