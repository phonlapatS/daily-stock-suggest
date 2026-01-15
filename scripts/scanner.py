#!/usr/bin/env python
"""
scanner.py - Market Scanner Dashboard
=====================================

Purpose: สแกนหุ้นทั้งหมดและแสดง Streak + Historical Probability

Features:
- Adaptive Threshold (volatility-based)
- Consecutive Streak Detection
- Historical Probability Engine
- Dashboard Output

Author: Stock Prediction System
Date: 2026-01-15
"""

import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path


class MarketScanner:
    """
    Market Scanner Dashboard
    
    ฟีเจอร์:
    1. Dynamic Threshold (ปรับตาม volatility)
    2. Streak Counter (นับวันติดต่อกัน)
    3. Historical Probability (คำนวณโอกาส)
    """
    
    def __init__(self, data_dir='data/stocks'):
        """
        Args:
            data_dir: โฟลเดอร์ที่เก็บ parquet files
        """
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    def calculate_dynamic_threshold(self, df, lookback=90, multiplier=1.5):
        """
        คำนวณ Threshold แบบ Dynamic (adaptive)
        
        Logic:
        - ใช้ Standard Deviation ของ 90 วันล่าสุด
        - คูณด้วย 1.5 เพื่อหาความผันผวน "สำคัญ"
        
        Returns:
            float: Threshold (%)
        """
        # ดึง 90 วันล่าสุด
        recent = df.tail(lookback)
        
        if len(recent) < 30:
            # ถ้าข้อมูลน้อย ใช้ fixed threshold
            return 1.0
        
        # คำนวณ SD
        std = recent['pct_change'].std()
        
        # Threshold = SD * multiplier
        threshold = std * multiplier
        
        # จำกัดให้อยู่ใน range สมเหตุสมผล
        threshold = max(0.5, min(threshold, 5.0))
        
        return threshold
    
    def detect_streak(self, df, threshold):
        """
        นับ Consecutive Streak (วันติดต่อกัน)
        
        Logic:
        - Up Day: pct_change > threshold
        - Down Day: pct_change < -threshold
        - Quiet: อยู่ใน range
        
        Returns:
            int: Streak (+ = up, - = down, 0 = quiet)
        """
        if df.empty or len(df) < 2:
            return 0
        
        streak = 0
        current_direction = None
        
        # เริ่มจากวันล่าสุด ไล่ย้อนกลับ
        for i in range(len(df) - 1, -1, -1):
            change = df.iloc[i]['pct_change']
            
            # ตรวจสอบทิศทาง
            if change > threshold:
                direction = 'UP'
            elif change < -threshold:
                direction = 'DOWN'
            else:
                # Quiet day - break streak
                break
            
            # ถ้าทิศทางเดียวกัน
            if current_direction is None:
                current_direction = direction
                streak = 1 if direction == 'UP' else -1
            elif current_direction == direction:
                # เพิ่ม streak
                if direction == 'UP':
                    streak += 1
                else:
                    streak -= 1
            else:
                # ทิศทางเปลี่ยน - break
                break
        
        return streak
    
    def calculate_historical_probability(self, df, threshold):
        """
        คำนวณ Historical Probability (Improved Version)
        
        Logic:
        1. เพิ่ม 'streak' column ให้ทุกแถว
        2. เพิ่ม 'next_day_return' column
        3. ดู streak วันนี้ (บรรทัดสุดท้าย)
        4. ค้นหาในอดีตที่ streak เท่ากัน
        5. คำนวณ win rate
        
        Args:
            df: DataFrame
            threshold: Threshold
        
        Returns:
            dict: {win_rate, avg_return, max_risk, sample_size}
        """
        if len(df) < 3:
            return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
        
        # เตรียม DataFrame
        df = df.copy()
        
        # 1. คำนวณ streak สำหรับทุกแถว
        df['streak'] = 0
        
        for i in range(len(df)):
            # คำนวณ streak ณ index นี้
            streak = 0
            current_direction = None
            
            # ไล่ย้อนกลับจาก i
            for j in range(i, -1, -1):
                change = df.iloc[j]['pct_change']
                
                if change > threshold:
                    direction = 'UP'
                elif change < -threshold:
                    direction = 'DOWN'
                else:
                    break
                
                if current_direction is None:
                    current_direction = direction
                    streak = 1 if direction == 'UP' else -1
                elif current_direction == direction:
                    streak = streak + 1 if direction == 'UP' else streak - 1
                else:
                    break
            
            df.iloc[i, df.columns.get_loc('streak')] = streak
        
        # 2. คำนวณ next_day_return
        df['next_day_return'] = df['pct_change'].shift(-1)
        
        # 3. ดึง streak วันนี้ (บรรทัดสุดท้าย)
        current_streak = df['streak'].iloc[-1]
        
        # 4. ถ้าไม่มี streak -> skip
        if current_streak == 0:
            return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
        
        # 5. ตัดบรรทัดสุดท้าย (วันนี้) ออก
        history_df = df.iloc[:-1].copy()
        
        # 6. กรองเฉพาะวันที่มี streak เท่ากับวันนี้
        matching_events = history_df[history_df['streak'] == current_streak]
        
        # 7. ลบแถวที่ next_day_return เป็น NaN
        matching_events = matching_events.dropna(subset=['next_day_return'])
        
        sample_size = len(matching_events)
        
        if sample_size == 0:
            return {'win_rate': 0, 'avg_return': 0, 'max_risk': 0, 'sample_size': 0}
        
        # 8. คำนวณสถิติ
        wins = matching_events[matching_events['next_day_return'] > 0]
        win_rate = (len(wins) / sample_size) * 100
        avg_return = matching_events['next_day_return'].mean()
        max_risk = matching_events['next_day_return'].min()
        
        return {
            'win_rate': win_rate,
            'avg_return': avg_return,
            'max_risk': max_risk,
            'sample_size': sample_size
        }
    
    def _calculate_streak_at_index(self, df, end_idx, threshold):
        """
        คำนวณ streak ณ index ที่กำหนด (helper function)
        """
        if end_idx < 1:
            return 0
        
        streak = 0
        current_direction = None
        
        # ไล่จาก end_idx ย้อนกลับ
        for i in range(end_idx, -1, -1):
            change = df.iloc[i]['pct_change']
            
            if change > threshold:
                direction = 'UP'
            elif change < -threshold:
                direction = 'DOWN'
            else:
                break
            
            if current_direction is None:
                current_direction = direction
                streak = 1 if direction == 'UP' else -1
            elif current_direction == direction:
                streak = streak + 1 if direction == 'UP' else streak - 1
            else:
                break
        
        return streak
    
    def analyze_stock(self, file_path):
        """
        วิเคราะห์ 1 หุ้น
        
        Returns:
            dict: ผลลัพธ์การวิเคราะห์
        """
        try:
            # โหลดข้อมูล
            df = pd.read_parquet(file_path)
            df.index = pd.to_datetime(df.index)
            
            # Drop duplicates & NaNs
            df = df[~df.index.duplicated(keep='last')]
            df = df.dropna()
            
            # คำนวณ pct_change ถ้ายังไม่มี
            if 'pct_change' not in df.columns:
                df['pct_change'] = df['close'].pct_change() * 100
                df = df.dropna()
            
            if len(df) < 30:
                return None
            
            # ข้อมูลล่าสุด
            latest = df.iloc[-1]
            symbol = file_path.stem.split('_')[0]
            
            # 1. Dynamic Threshold
            threshold = self.calculate_dynamic_threshold(df)
            
            # 2. Current Streak
            current_streak = self.detect_streak(df, threshold)
            
            # 3. Historical Probability (ใช้ method ใหม่)
            prob_stats = self.calculate_historical_probability(df, threshold)
            
            # 4. Streak Status (with emoji)
            if current_streak > 0:
                streak_status = f"🟢 Up {current_streak} Days"
            elif current_streak < 0:
                streak_status = f"🔴 Down {abs(current_streak)} Days"
            else:
                streak_status = "⚪ Quiet"
            
            return {
                'Symbol': symbol,
                'Price': latest['close'],
                'Chg%': latest['pct_change'],
                'Threshold': threshold,
                'Streak': current_streak,
                'Streak_Status': streak_status,
                'Win_Rate': prob_stats['win_rate'],
                'Avg_Return': prob_stats['avg_return'],
                'Max_Risk': prob_stats['max_risk'],
                'Events': prob_stats['sample_size']  # เปลี่ยนจาก Samples
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path.name}: {e}")
            return None
    
    def scan_all(self):
        """
        สแกนหุ้นทั้งหมด
        
        Returns:
            DataFrame: Dashboard
        """
        parquet_files = list(self.data_dir.glob("*.parquet"))
        
        if not parquet_files:
            print(f"❌ No parquet files found in {self.data_dir}")
            return pd.DataFrame()
        
        print(f"\n🚀 Scanning {len(parquet_files)} stocks...")
        print("="*70)
        
        results = []
        for pf in parquet_files:
            result = self.analyze_stock(pf)
            if result:
                results.append(result)
        
        if not results:
            print("❌ No valid results")
            return pd.DataFrame()
        
        # สร้าง DataFrame
        df = pd.DataFrame(results)
        
        # เรียงตาม Absolute Change (เคลื่อนไหวมากสุด)
        df['Abs_Chg'] = df['Chg%'].abs()
        df = df.sort_values('Abs_Chg', ascending=False)
        df = df.drop('Abs_Chg', axis=1)
        
        return df
    
    def print_dashboard(self, df):
        """
        แสดงผล Dashboard สวยๆ
        """
        if df.empty:
            print("\n❌ No stocks found")
            return
        
        print(f"\n{'='*70}")
        print("📊 MARKET SCANNER DASHBOARD")
        print(f"{'='*70}\n")
        
        # Format columns with proper +/- signs
        df_display = df.copy()
        
        # Format Price
        df_display['Price'] = df_display['Price'].apply(lambda x: f"฿{x:.2f}")
        
        # Format signed percentages (with +/-)
        df_display['Change'] = df_display['Chg%'].apply(lambda x: f"{x:+.2f}%")
        df_display['AvgRet'] = df_display['Avg_Return'].apply(lambda x: f"{x:+.2f}%")
        df_display['MaxRisk'] = df_display['Max_Risk'].apply(lambda x: f"{x:+.2f}%")
        
        # Format unsigned percentages (no sign needed)
        df_display['Thres.'] = df_display['Threshold'].apply(lambda x: f"{x:.2f}%")
        df_display['WinRate'] = df_display['Win_Rate'].apply(lambda x: f"{x:.1f}%")
        
        # Select and reorder columns
        cols = ['Symbol', 'Price', 'Change', 'Streak_Status', 'Thres.', 'WinRate', 'AvgRet', 'MaxRisk', 'Events']
        
        print(df_display[cols].to_string(index=False))
        print(f"\n{'='*70}")
        
        # นับสถิติ
        active_streaks = len(df[df['Streak'] != 0])
        up_streaks = len(df[df['Streak'] > 0])
        down_streaks = len(df[df['Streak'] < 0])
        
        print(f"📈 Total Stocks: {len(df)}")
        print(f"   🟢 Up Streaks: {up_streaks}")
        print(f"   🔴 Down Streaks: {down_streaks}")
        print(f"   ⚪ Quiet: {len(df) - active_streaks}")
        print(f"{'='*70}\n")


def main():
    """
    Main execution
    """
    from datetime import datetime
    
    scanner = MarketScanner(data_dir='data/stocks')
    
    # Scan
    df = scanner.scan_all()
    
    # Display
    scanner.print_dashboard(df)
    
    # Save with timestamp
    if not df.empty:
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        results_dir = Path('results/scanner_history')
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # ไฟล์ล่าสุด (overwrite)
        latest_file = 'results/market_scanner.csv'
        df.to_csv(latest_file, index=False)
        print(f"💾 Latest: {latest_file}")
        
        # ไฟล์สำรอง (timestamped)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = results_dir / f"scanner_{timestamp}.csv"
        df.to_csv(archive_file, index=False)
        print(f"📦 Archive: {archive_file}")
        
        # แสดงจำนวนไฟล์เก่า
        archive_count = len(list(results_dir.glob('scanner_*.csv')))
        print(f"📊 Total archives: {archive_count}\n")


if __name__ == "__main__":
    main()
