"""
Statistics Analyzer Module - วิเคราะห์สถิติจากข้อมูลจริง
100% Data-driven: ไม่มี ML model ใดๆ, ใช้เฉพาะข้อมูลประวัติศาสตร์
"""

import pandas as pd
import numpy as np
from config import THRESHOLD_PERCENT, MIN_STREAK_LENGTH, SIDEWAYS_THRESHOLD
from utils import classify_direction


class StatsAnalyzer:
    """
    Class สำหรับวิเคราะห์สถิติของการเคลื่อนไหวราคา
    """
    
    def __init__(self, threshold=THRESHOLD_PERCENT):
        """
        Args:
            threshold: % threshold สำหรับการกรองการเคลื่อนไหวที่มีนัยสำคัญ
        """
        self.threshold = threshold
    
    def filter_significant_moves(self, df):
        """
        กรองเฉพาะวันที่มี % change ≥ threshold (บวกหรือลบ)
        
        Args:
            df: DataFrame with 'pct_change' column
        
        Returns:
            DataFrame: เฉพาะ rows ที่มีการเคลื่อนไหวมากกว่า threshold
        """
        # กรอง rows ที่มี absolute % change >= threshold
        significant = df[abs(df['pct_change']) >= self.threshold].copy()
        
        print(f"📊 Found {len(significant)} days with ±{self.threshold}% moves out of {len(df)} total days")
        print(f"   - Positive: {len(significant[significant['pct_change'] > 0])}")
        print(f"   - Negative: {len(significant[significant['pct_change'] < 0])}")
        
        return significant
    
    def analyze_next_day_behavior(self, df):
        """
        วิเคราะห์ว่าหลังจากวันที่ ±threshold% แล้ว วันถัดไปเป็นอย่างไร
        
        Args:
            df: DataFrame ที่มี pct_change column
        
        Returns:
            dict: สถิติการเคลื่อนไหววันถัดไป
        """
        # กรองเฉพาะวันที่มีการเคลื่อนไหวมีนัยสำคัญ
        significant = self.filter_significant_moves(df)
        
        if len(significant) == 0:
            print("⚠️ No significant moves found")
            return None
        
        # เตรียม data structure สำหรับเก็บผลลัพธ์
        stats = {
            'after_positive': {'up': 0, 'down': 0, 'sideways': 0, 'changes': []},
            'after_negative': {'up': 0, 'down': 0, 'sideways': 0, 'changes': []}
        }
        
        # วนลูปดูแต่ละวันที่มีการเคลื่อนไหว
        for idx in significant.index:
            try:
                # หาตำแหน่งของวันนี้ใน original df
                current_pos = df.index.get_loc(idx)
                
                # ตรวจสอบว่ามีวันถัดไปหรือไม่
                if current_pos + 1 >= len(df):
                    continue
                
                # ดึง % change ของวันถัดไป
                next_day_change = df.iloc[current_pos + 1]['pct_change']
                current_day_change = df.iloc[current_pos]['pct_change']
                
                # จัดประเภทวันถัดไป
                next_direction = classify_direction(next_day_change, SIDEWAYS_THRESHOLD)
                
                # บันทึกสถิติ
                if current_day_change > 0:
                    # วันนี้เป็นบวก
                    stats['after_positive'][next_direction] += 1
                    stats['after_positive']['changes'].append(next_day_change)
                else:
                    # วันนี้เป็นลบ
                    stats['after_negative'][next_direction] += 1
                    stats['after_negative']['changes'].append(next_day_change)
                    
            except Exception as e:
                continue
        
        # คำนวณค่าเฉลี่ย
        if stats['after_positive']['changes']:
            stats['after_positive']['avg_change'] = np.mean(stats['after_positive']['changes'])
            stats['after_positive']['std_change'] = np.std(stats['after_positive']['changes'])
        else:
            stats['after_positive']['avg_change'] = 0
            stats['after_positive']['std_change'] = 0
        
        if stats['after_negative']['changes']:
            stats['after_negative']['avg_change'] = np.mean(stats['after_negative']['changes'])
            stats['after_negative']['std_change'] = np.std(stats['after_negative']['changes'])
        else:
            stats['after_negative']['avg_change'] = 0
            stats['after_negative']['std_change'] = 0
        
        return stats
    
    def detect_streaks(self, df, min_length=MIN_STREAK_LENGTH):
        """
        หาช่วงที่มีการ ±threshold% ติดต่อกันหลายวัน
        
        Args:
            df: DataFrame with pct_change
            min_length: ความยาวขั้นต่ำของ streak
        
        Returns:
            list: รายการ streaks
        """
        streaks = []
        current_streak = []
        
        for idx, row in df.iterrows():
            pct_change = row['pct_change']
            
            # ตรวจสอบว่าเป็นวันที่มีการเคลื่อนไหวมีนัยสำคัญหรือไม่
            if abs(pct_change) >= self.threshold:
                current_streak.append({
                    'date': idx,
                    'pct_change': pct_change,
                    'direction': 'up' if pct_change > 0 else 'down'
                })
            else:
                # Streak หยุด
                if len(current_streak) >= min_length:
                    streaks.append(self._process_streak(current_streak, df))
                current_streak = []
        
        # ตรวจสอบ streak สุดท้าย
        if len(current_streak) >= min_length:
            streaks.append(self._process_streak(current_streak, df))
        
        print(f"🔥 Found {len(streaks)} streaks (length >= {min_length})")
        return streaks
    
    def _process_streak(self, streak_data, df):
        """
        ประมวลผล streak เพื่อหาข้อมูลเพิ่มเติม
        """
        start_date = streak_data[0]['date']
        end_date = streak_data[-1]['date']
        length = len(streak_data)
        
        # หาทิศทางโดยรวมของ streak
        up_count = sum(1 for d in streak_data if d['direction'] == 'up')
        down_count = length - up_count
        
        if up_count > down_count:
            overall_direction = 'bullish'
        elif down_count > up_count:
            overall_direction = 'bearish'
        else:
            overall_direction = 'mixed'
        
        # หาว่าวันถัดไปหลัง streak จบเป็นอย่างไร
        try:
            end_pos = df.index.get_loc(end_date)
            if end_pos + 1 < len(df):
                next_day_change = df.iloc[end_pos + 1]['pct_change']
            else:
                next_day_change = None
        except:
            next_day_change = None
        
        return {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'length': length,
            'direction': overall_direction,
            'up_days': up_count,
            'down_days': down_count,
            'next_day_change': next_day_change
        }
    
    def calculate_probabilities(self, next_day_stats):
        """
        คำนวณความน่าจะเป็นจากสถิติจริง
        
        Args:
            next_day_stats: dict จาก analyze_next_day_behavior()
        
        Returns:
            dict: probabilities
        """
        probs = {}
        
        # After positive day
        ap = next_day_stats['after_positive']
        total_after_pos = ap['up'] + ap['down'] + ap['sideways']
        
        if total_after_pos > 0:
            probs['up_after_positive'] = (ap['up'] / total_after_pos) * 100
            probs['down_after_positive'] = (ap['down'] / total_after_pos) * 100
            probs['sideways_after_positive'] = (ap['sideways'] / total_after_pos) * 100
        
        # After negative day
        an = next_day_stats['after_negative']
        total_after_neg = an['up'] + an['down'] + an['sideways']
        
        if total_after_neg > 0:
            probs['up_after_negative'] = (an['up'] / total_after_neg) * 100
            probs['down_after_negative'] = (an['down'] / total_after_neg) * 100
            probs['sideways_after_negative'] = (an['sideways'] / total_after_neg) * 100
        
        return probs
    
    def calculate_risk_metrics(self, next_day_stats):
        """
        คำนวณความเสี่ยงจากข้อมูลจริง
        
        Args:
            next_day_stats: dict จาก analyze_next_day_behavior()
        
        Returns:
            dict: risk metrics
        """
        risk = {}
        
        # Risk after positive day
        if next_day_stats['after_positive']['changes']:
            changes = next_day_stats['after_positive']['changes']
            risk['avg_error_after_positive'] = abs(np.mean(changes))
            risk['max_loss_after_positive'] = min(changes)
            risk['std_dev_after_positive'] = np.std(changes)
        
        # Risk after negative day
        if next_day_stats['after_negative']['changes']:
            changes = next_day_stats['after_negative']['changes']
            risk['avg_error_after_negative'] = abs(np.mean(changes))
            risk['max_loss_after_negative'] = abs(max(changes))  # max คือขาดทุนสูงสุดถ้าเป็นลบ
            risk['std_dev_after_negative'] = np.std(changes)
        
        return risk
    
    def generate_full_report(self, df):
        """
        สร้าง report สถิติแบบครบถ้วน
        
        Args:
            df: DataFrame with pct_change
        
        Returns:
            dict: complete statistics report
        """
        print("\n" + "="*60)
        print("🔍 ANALYZING STATISTICS FROM HISTORICAL DATA")
        print("="*60 + "\n")
        
        # 1. Filter significant moves
        significant = self.filter_significant_moves(df)
        
        # 2. Analyze next day behavior
        print("\n📈 Analyzing next day behavior...")
        next_day_stats = self.analyze_next_day_behavior(df)
        
        # 3. Detect streaks
        print("\n🔥 Detecting streaks...")
        streaks = self.detect_streaks(df)
        
        # 4. Calculate probabilities
        print("\n🎯 Calculating probabilities...")
        probabilities = self.calculate_probabilities(next_day_stats)
        
        # 5. Calculate risk
        print("\n⚠️ Calculating risk metrics...")
        risk = self.calculate_risk_metrics(next_day_stats)
        
        # Compile full report
        report = {
            'threshold': self.threshold,
            'total_days': len(df),
            'total_significant_days': len(significant),
            'positive_moves': len(significant[significant['pct_change'] > 0]),
            'negative_moves': len(significant[significant['pct_change'] < 0]),
            'next_day_stats': {
                'after_positive': {
                    'up': next_day_stats['after_positive']['up'],
                    'down': next_day_stats['after_positive']['down'],
                    'sideways': next_day_stats['after_positive']['sideways'],
                    'avg_change': next_day_stats['after_positive']['avg_change'],
                    'std_change': next_day_stats['after_positive']['std_change']
                },
                'after_negative': {
                    'up': next_day_stats['after_negative']['up'],
                    'down': next_day_stats['after_negative']['down'],
                    'sideways': next_day_stats['after_negative']['sideways'],
                    'avg_change': next_day_stats['after_negative']['avg_change'],
                    'std_change': next_day_stats['after_negative']['std_change']
                }
            },
            'streaks': streaks,
            'probabilities': probabilities,
            'risk': risk
        }
        
        print("\n✅ Analysis complete!")
        return report


# Example usage
if __name__ == "__main__":
    # ทดสอบด้วยข้อมูลจริง
    from data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    df = fetcher.fetch_daily_data('PTT', 'SET', n_bars=2000)
    
    if df is not None:
        analyzer = StatsAnalyzer(threshold=1.0)
        report = analyzer.generate_full_report(df)
        
        from utils import format_stats_report
        print("\n" + format_stats_report(report))
