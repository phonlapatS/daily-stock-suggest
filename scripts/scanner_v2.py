#!/usr/bin/env python
"""
scanner_v2.py - Market Scanner with Mixed Streak Logic
======================================================

New Features:
- 90th Percentile Dynamic Threshold (126 days)
- Volatility Classification (Low/Med/High)
- Mixed Streak Logic (+-+- patterns)
"""

import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('core')
from dynamic_streak_v2 import apply_dynamic_logic, calculate_historical_probability_mixed


class MarketScannerV2:
    """
    Market Scanner V2 - With Mixed Streak Logic
    """
    
    def __init__(self, data_dir='data/stocks'):
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    def analyze_stock(self, file_path):
        """
        Analyze 1 stock with new logic
        """
        try:
            # Load data
            df = pd.read_parquet(file_path)
            df.index = pd.to_datetime(df.index)
            
            # Drop duplicates & NaNs
            df = df[~df.index.duplicated(keep='last')]
            df = df.dropna()
            
            # Calculate pct_change if not exists
            if 'pct_change' not in df.columns:
                df['pct_change'] = df['close'].pct_change() * 100
                df = df.dropna()
            
            if len(df) < 130:  # Need at least 126 + some buffer
                return None
            
            # Apply dynamic logic
            df_processed = apply_dynamic_logic(df)
            
            # Get latest data
            latest = df_processed.iloc[-1]
            symbol = file_path.stem.split('_')[0]
            
            # Calculate historical probability
            prob = calculate_historical_probability_mixed(df, latest['Threshold'])
            
            # Streak status (with emoji)
            streak = latest['Streak']
            if streak > 0:
                if latest['pct_change'] > 0:
                    streak_status = f"🟢 Up (Vol {streak})"
                else:
                    streak_status = f"🔴 Down (Vol {streak})"
            else:
                streak_status = "⚪ Quiet"
            
            return {
                'Symbol': symbol,
                'Price': latest['close'],
                'Change': latest['pct_change'],
                'Thres.': latest['Threshold'],
                'Vol_Type': latest['Vol_Type'],
                'Streak': streak,
                'Streak_Status': streak_status,
                'WinRate': prob['win_rate'],
                'AvgRet': prob['avg_return'],
                'MaxRisk': prob['max_risk'],
                'Events': prob['sample_size']
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path.name}: {e}")
            return None
    
    def scan_all(self):
        """
        Scan all stocks
        """
        parquet_files = list(self.data_dir.glob("*.parquet"))
        
        if not parquet_files:
            print(f"❌ No parquet files found in {self.data_dir}")
            return pd.DataFrame()
        
        print(f"\n🚀 Scanning {len(parquet_files)} stocks (V2 - Mixed Streak)...")
        print("="*70)
        
        results = []
        for pf in parquet_files:
            result = self.analyze_stock(pf)
            if result:
                results.append(result)
        
        if not results:
            print("❌ No valid results")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Sort by absolute change
        df['Abs_Chg'] = df['Change'].abs()
        df = df.sort_values('Abs_Chg', ascending=False)
        df = df.drop('Abs_Chg', axis=1)
        
        return df
    
    def print_dashboard(self, df):
        """
        Print dashboard
        """
        if df.empty:
            print("\n❌ No stocks found")
            return
        
        print(f"\n{'='*70}")
        print("📊 MARKET SCANNER V2 DASHBOARD (Mixed Streak)")
        print(f"{'='*70}\n")
        
        # Format columns
        df_display = df.copy()
        
        # Format Price
        df_display['Price'] = df_display['Price'].apply(lambda x: f"฿{x:.2f}")
        
        # Format signed percentages
        df_display['Change'] = df_display['Change'].apply(lambda x: f"{x:+.2f}%")
        df_display['AvgRet'] = df_display['AvgRet'].apply(lambda x: f"{x:+.2f}%")
        df_display['MaxRisk'] = df_display['MaxRisk'].apply(lambda x: f"{x:+.2f}%")
        
        # Format unsigned percentages
        df_display['Thres.'] = df_display['Thres.'].apply(lambda x: f"{x:.2f}%")
        df_display['WinRate'] = df_display['WinRate'].apply(lambda x: f"{x:.1f}%")
        
        # Select columns
        cols = ['Symbol', 'Price', 'Change', 'Streak_Status', 'Vol_Type', 'Thres.', 'WinRate', 'AvgRet', 'MaxRisk', 'Events']
        
        print(df_display[cols].to_string(index=False))
        print(f"\n{'='*70}")
        
        # Statistics
        active_streaks = len(df[df['Streak'] > 0])
        quiet = len(df[df['Streak'] == 0])
        
        # Vol type breakdown
        low_vol = len(df[df['Vol_Type'] == 'Low'])
        med_vol = len(df[df['Vol_Type'] == 'Med'])
        high_vol = len(df[df['Vol_Type'] == 'High'])
        
        print(f"📈 Total Stocks: {len(df)}")
        print(f"   🔥 Active Streaks: {active_streaks}")
        print(f"   ⚪ Quiet: {quiet}")
        print(f"\n📊 Volatility:")
        print(f"   🟢 Low: {low_vol}")
        print(f"   🟡 Med: {med_vol}")
        print(f"   🔴 High: {high_vol}")
        print(f"{'='*70}\n")


def main():
    """
    Main execution
    """
    scanner = MarketScannerV2(data_dir='data/stocks')
    
    # Scan
    df = scanner.scan_all()
    
    # Display
    scanner.print_dashboard(df)
    
    # Save with timestamp
    if not df.empty:
        # สร้างโฟลเดอร์
        results_dir = Path('results/scanner_v2_history')
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # ไฟล์ล่าสุด
        latest_file = 'results/market_scanner_v2.csv'
        df.to_csv(latest_file, index=False)
        print(f"💾 Latest: {latest_file}")
        
        # ไฟล์สำรอง
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = results_dir / f"scanner_v2_{timestamp}.csv"
        df.to_csv(archive_file, index=False)
        print(f"📦 Archive: {archive_file}")
        
        archive_count = len(list(results_dir.glob('scanner_v2_*.csv')))
        print(f"📊 Total archives: {archive_count}\n")


if __name__ == "__main__":
    main()
