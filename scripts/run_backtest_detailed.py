#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_backtest_detailed.py - รัน Backtest แบบละเอียด
================================================================================

รัน backtest กับหุ้นหลายตัวและแสดงผลลัพธ์แบบละเอียด:
- แสดงผลลัพธ์แต่ละหุ้น
- สรุปผลลัพธ์แต่ละประเทศ
- แสดงหุ้นที่ผ่านเกณฑ์

Author: Stock Analysis System
Date: 2026-01-XX
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import config
from core.data_cache import get_data_with_cache
from scripts.backtest import backtest_single


def run_backtest_detailed(symbols_config, n_bars=500, threshold_multiplier=1.25, min_stats=30):
    """
    รัน backtest กับหุ้นหลายตัวและแสดงผลลัพธ์แบบละเอียด
    
    Args:
        symbols_config: List of dicts with 'symbol', 'exchange', 'country'
        n_bars: Number of test bars
        threshold_multiplier: Threshold multiplier
        min_stats: Minimum statistics required
    """
    print("\n" + "="*100)
    print("[DETAILED BACKTEST] รัน Backtest แบบละเอียด")
    print("="*100)
    print(f"\n📊 Configuration:")
    print(f"   Test Bars: {n_bars}")
    print(f"   Threshold Multiplier: {threshold_multiplier}")
    print(f"   Min Stats: {min_stats}")
    print(f"   Total Symbols: {len(symbols_config)}")
    
    tv = TvDatafeed()
    results = []
    
    print("\n[1] รัน Backtest แต่ละหุ้น")
    print("="*100)
    
    for idx, item in enumerate(symbols_config, 1):
        symbol = item['symbol']
        exchange = item['exchange']
        country = item.get('country', 'UNKNOWN')
        
        print(f"\n[{idx}/{len(symbols_config)}] {symbol} ({exchange}) - {country}")
        print("-" * 100)
        
        try:
            result = backtest_single(
                tv=tv,
                symbol=symbol,
                exchange=exchange,
                n_bars=n_bars,
                threshold_multiplier=threshold_multiplier,
                min_stats=min_stats,
                verbose=False
            )
            
            if result and result['total'] > 0:
                print(f"   ✅ Found {result['total']} signals")
                print(f"   Accuracy: {result['accuracy']:.1f}%")
                print(f"   AvgWin: {result.get('avg_win', 0):.2f}%")
                print(f"   AvgLoss: {result.get('avg_loss', 0):.2f}%")
                print(f"   RRR: {result.get('risk_reward', 0):.2f}")
                
                result['country'] = country
                results.append(result)
            else:
                print(f"   ⚠️ No signals found")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    if not results:
        print("\n❌ No results found")
        return
    
    # Summary by country
    print("\n" + "="*100)
    print("[2] สรุปผลลัพธ์แต่ละประเทศ")
    print("="*100)
    
    df_results = pd.DataFrame(results)
    countries = df_results['country'].unique()
    
    for country in sorted(countries):
        country_df = df_results[df_results['country'] == country]
        
        print(f"\n[{country}] Market")
        print("-" * 100)
        print(f"{'Symbol':<12} {'Total':<8} {'Correct':<8} {'Accuracy':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<8}")
        print("-" * 100)
        
        for _, row in country_df.iterrows():
            print(f"{row['symbol']:<12} {row['total']:<8} {row['correct']:<8} {row['accuracy']:<9.1f}% "
                  f"{row.get('avg_win', 0):<9.2f}% {row.get('avg_loss', 0):<9.2f}% {row.get('risk_reward', 0):<7.2f}")
        
        # Country summary
        total_signals = country_df['total'].sum()
        total_correct = country_df['correct'].sum()
        avg_accuracy = (total_correct / total_signals * 100) if total_signals > 0 else 0
        
        # Weighted averages
        total_win_sum = sum(row.get('avg_win', 0) * row['total'] for _, row in country_df.iterrows())
        total_loss_sum = sum(row.get('avg_loss', 0) * row['total'] for _, row in country_df.iterrows())
        avg_win = total_win_sum / total_signals if total_signals > 0 else 0
        avg_loss = total_loss_sum / total_signals if total_signals > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        print("-" * 100)
        print(f"{'TOTAL':<12} {total_signals:<8} {total_correct:<8} {avg_accuracy:<9.1f}% "
              f"{avg_win:<9.2f}% {avg_loss:<9.2f}% {rrr:<7.2f}")
        
        # Quality metrics
        good_prob = len(country_df[country_df['accuracy'] > 60])
        good_rrr = len(country_df[country_df.get('risk_reward', 0) > 2.0])
        good_both = len(country_df[(country_df['accuracy'] > 60) & (country_df.get('risk_reward', 0) > 2.0)])
        
        print(f"\n   Quality:")
        print(f"   - Symbols with Prob > 60%: {good_prob}/{len(country_df)}")
        print(f"   - Symbols with RRR > 2.0: {good_rrr}/{len(country_df)}")
        print(f"   - Symbols with Prob > 60% AND RRR > 2.0: {good_both}/{len(country_df)}")
    
    # Overall summary
    print("\n" + "="*100)
    print("[3] สรุปโดยรวม")
    print("="*100)
    
    total_signals = df_results['total'].sum()
    total_correct = df_results['correct'].sum()
    overall_accuracy = (total_correct / total_signals * 100) if total_signals > 0 else 0
    
    total_win_sum = sum(row.get('avg_win', 0) * row['total'] for _, row in df_results.iterrows())
    total_loss_sum = sum(row.get('avg_loss', 0) * row['total'] for _, row in df_results.iterrows())
    overall_avg_win = total_win_sum / total_signals if total_signals > 0 else 0
    overall_avg_loss = total_loss_sum / total_signals if total_signals > 0 else 0
    overall_rrr = overall_avg_win / overall_avg_loss if overall_avg_loss > 0 else 0
    
    print(f"\n   Total Symbols: {len(df_results)}")
    print(f"   Total Signals: {total_signals}")
    print(f"   Total Correct: {total_correct}")
    print(f"   Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"   Overall AvgWin: {overall_avg_win:.2f}%")
    print(f"   Overall AvgLoss: {overall_avg_loss:.2f}%")
    print(f"   Overall RRR: {overall_rrr:.2f}")
    
    # Top performers
    print("\n" + "="*100)
    print("[4] Top Performers")
    print("="*100)
    
    print("\n   Top 10 by Accuracy:")
    top_accuracy = df_results.nlargest(10, 'accuracy')
    for _, row in top_accuracy.iterrows():
        print(f"   {row['symbol']:<12} ({row['country']}): Accuracy={row['accuracy']:.1f}%, "
              f"RRR={row.get('risk_reward', 0):.2f}, Signals={row['total']}")
    
    print("\n   Top 10 by RRR:")
    top_rrr = df_results[df_results['total'] >= 5].nlargest(10, 'risk_reward')
    for _, row in top_rrr.iterrows():
        print(f"   {row['symbol']:<12} ({row['country']}): RRR={row.get('risk_reward', 0):.2f}, "
              f"Accuracy={row['accuracy']:.1f}%, Signals={row['total']}")
    
    print("\n   Symbols with Prob > 60% AND RRR > 2.0:")
    good_both = df_results[(df_results['accuracy'] > 60) & (df_results.get('risk_reward', 0) > 2.0)]
    if not good_both.empty:
        for _, row in good_both.iterrows():
            print(f"   ✅ {row['symbol']:<12} ({row['country']}): Prob={row['accuracy']:.1f}%, "
                  f"RRR={row.get('risk_reward', 0):.2f}, Signals={row['total']}")
    else:
        print("   ⚠️ No symbols found")
    
    print("\n" + "="*100)
    print("[COMPLETE] เสร็จสิ้นการทดสอบ")
    print("="*100)
    
    return df_results


def main():
    """Main function"""
    # Load symbols from config or metrics file
    metrics_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "symbol_performance.csv")
    
    if os.path.exists(metrics_file):
        df_metrics = pd.read_csv(metrics_file)
        
        # Select top symbols from each country
        symbols_config = []
        
        for country in ['TH', 'US', 'CN', 'TW']:
            country_df = df_metrics[df_metrics['Country'] == country].nlargest(10, 'Count')
            
            for _, row in country_df.iterrows():
                if country == 'TH':
                    exchange = 'SET'
                elif country == 'US':
                    exchange = 'NASDAQ'
                elif country == 'CN':
                    exchange = 'HKEX'
                elif country == 'TW':
                    exchange = 'TWSE'
                else:
                    exchange = 'SET'
                
                symbols_config.append({
                    'symbol': row['symbol'],
                    'exchange': exchange,
                    'country': country
                })
    else:
        # Fallback: Use config symbols
        symbols_config = [
            {'symbol': 'PTTEP', 'exchange': 'SET', 'country': 'TH'},
            {'symbol': 'DOHOME', 'exchange': 'SET', 'country': 'TH'},
            {'symbol': 'TPIPP', 'exchange': 'SET', 'country': 'TH'},
            {'symbol': 'PTT', 'exchange': 'SET', 'country': 'TH'},
            {'symbol': 'ADVANC', 'exchange': 'SET', 'country': 'TH'},
            {'symbol': 'NVDA', 'exchange': 'NASDAQ', 'country': 'US'},
            {'symbol': 'AAPL', 'exchange': 'NASDAQ', 'country': 'US'},
            {'symbol': 'VRTX', 'exchange': 'NASDAQ', 'country': 'US'},
        ]
    
    # Run backtest
    results = run_backtest_detailed(
        symbols_config=symbols_config,
        n_bars=500,
        threshold_multiplier=1.25,
        min_stats=30
    )
    
    # Save results
    if results is not None and not results.empty:
        output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backtest_results_detailed.csv")
        results.to_csv(output_file, index=False)
        print(f"\n💾 Saved results to: {output_file}")


if __name__ == "__main__":
    main()

