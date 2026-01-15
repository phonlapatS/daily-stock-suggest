"""
Predictor Module - ทำนายวันพรุ่งนี้จากสถิติในอดีต
Pure Pattern Matching - ไม่ใช้ ML model แต่ใช้ historical data เปรียบเทียบ

โจทย์: ถ้าวันนี้หุ้นขึ้น/ลง เกิน 1% → ทายว่าพรุ่งนี้จะเป็นยังไง
- ทิศทาง: ขึ้น หรือ ลง
- เปอร์เซ็นต์: กี่ %
- ความน่าจะเป็น: กี่ %
"""

import numpy as np
import pandas as pd
from utils import classify_direction
from config import SIDEWAYS_THRESHOLD


class HistoricalPredictor:
    """
    Class สำหรับทำนายวันพรุ่งนี้โดยใช้ pattern matching จากข้อมูลในอดีต
    """
    
    def __init__(self, df, threshold=1.0):
        """
        Args:
            df: DataFrame with historical data (must have 'pct_change' column)
            threshold: % threshold สำหรับการกรองการเคลื่อนไหว
        """
        self.df = df.copy()
        self.threshold = threshold
        
        # เตรียม historical patterns
        self._prepare_historical_patterns()
    
    def _prepare_historical_patterns(self):
        """
        เตรียมข้อมูลประวัติศาสตร์สำหรับการจับคู่
        """
        patterns = []
        
        for i in range(len(self.df) - 1):
            today_change = self.df.iloc[i]['pct_change']
            
            # กรองเฉพาะวันที่มีการเคลื่อนไหว >= threshold
            if abs(today_change) >= self.threshold:
                tomorrow_change = self.df.iloc[i + 1]['pct_change']
                
                patterns.append({
                    'today_change': today_change,
                    'today_direction': 'up' if today_change > 0 else 'down',
                    'tomorrow_change': tomorrow_change,
                    'tomorrow_direction': classify_direction(tomorrow_change, SIDEWAYS_THRESHOLD),
                    'date': self.df.index[i]
                })
        
        self.patterns = pd.DataFrame(patterns)
        print(f"✅ Prepared {len(self.patterns)} historical patterns for prediction")
    
    def predict_tomorrow(self, today_pct_change, match_range=0.5, min_samples=5):
        """
        ทำนายวันพรุ่งนี้จากการเคลื่อนไหววันนี้
        
        Args:
            today_pct_change: % change ของวันนี้ (เช่น 1.5 หรือ -2.0)
            match_range: ช่วงการค้นหา pattern ที่ใกล้เคียง (±%) 
            min_samples: จำนวนตัวอย่างขั้นต่ำเพื่อให้การทำนายน่าเชื่อถือ
        
        Returns:
            dict: prediction results
        """
        print(f"\n{'='*60}")
        print(f"🔮 PREDICTING TOMORROW BASED ON TODAY'S MOVEMENT: {today_pct_change:+.2f}%")
        print(f"{'='*60}")
        
        # ตรวจสอบว่าวันนี้เข้าเงื่อนไข threshold หรือไม่
        if abs(today_pct_change) < self.threshold:
            print(f"⚠️ Today's movement ({today_pct_change:.2f}%) is below threshold ({self.threshold}%)")
            print("   No prediction needed - market is not moving significantly")
            return {
                'prediction': 'WAIT & SEE',
                'reason': f'Movement below threshold ({self.threshold}%)',
                'confidence': 0
            }
        
        # หา similar patterns ในอดีต
        today_direction = 'up' if today_pct_change > 0 else 'down'
        
        # กรอง patterns ที่อยู่ในช่วงใกล้เคียง
        similar_patterns = self.patterns[
            (self.patterns['today_direction'] == today_direction) &
            (self.patterns['today_change'] >= today_pct_change - match_range) &
            (self.patterns['today_change'] <= today_pct_change + match_range)
        ]
        
        print(f"\n📊 Found {len(similar_patterns)} similar patterns in history")
        print(f"   (Looking for {today_direction} movements around {today_pct_change:+.2f}% ± {match_range}%)")
        
        if len(similar_patterns) < min_samples:
            print(f"⚠️ Not enough samples ({len(similar_patterns)} < {min_samples})")
            print("   Prediction may not be reliable - expanding search range...")
            
            # ขยายช่วงการค้นหา
            similar_patterns = self.patterns[
                self.patterns['today_direction'] == today_direction
            ]
            
            print(f"   Found {len(similar_patterns)} patterns with same direction")
        
        if len(similar_patterns) == 0:
            return {
                'prediction': 'INSUFFICIENT DATA',
                'reason': 'No historical patterns found',
                'confidence': 0
            }
        
        # วิเคราะห์ผลลัพธ์วันถัดไป
        tomorrow_changes = similar_patterns['tomorrow_change'].values
        tomorrow_directions = similar_patterns['tomorrow_direction'].values
        
        # นับทิศทาง
        up_count = sum(tomorrow_directions == 'up')
        down_count = sum(tomorrow_directions == 'down')
        sideways_count = sum(tomorrow_directions == 'sideways')
        total_count = len(tomorrow_directions)
        
        # หาทิศทางที่มีโอกาสมากที่สุด
        direction_counts = {
            'up': up_count,
            'down': down_count,
            'sideways': sideways_count
        }
        predicted_direction = max(direction_counts, key=direction_counts.get)
        
        # คำนวณค่าเฉลี่ย % change ที่คาดว่าจะเกิด
        avg_change = np.mean(tomorrow_changes)
        median_change = np.median(tomorrow_changes)
        std_change = np.std(tomorrow_changes)
        
        # คำนวณ probability
        probability = (direction_counts[predicted_direction] / total_count) * 100
        
        # คำนวณความเสี่ยง
        worst_case = min(tomorrow_changes) if predicted_direction == 'up' else max(tomorrow_changes)
        best_case = max(tomorrow_changes) if predicted_direction == 'up' else min(tomorrow_changes)
        
        # สร้าง prediction report
        prediction = {
            'input': {
                'today_change': today_pct_change,
                'today_direction': today_direction
            },
            'prediction': {
                'direction': predicted_direction.upper(),
                'expected_change_avg': avg_change,
                'expected_change_median': median_change,
                'confidence': probability
            },
            'probability_breakdown': {
                'up': (up_count / total_count) * 100,
                'down': (down_count / total_count) * 100,
                'sideways': (sideways_count / total_count) * 100
            },
            'risk_assessment': {
                'std_deviation': std_change,
                'worst_case': worst_case,
                'best_case': best_case,
                'risk_reward_ratio': abs(best_case / worst_case) if worst_case != 0 else 0
            },
            'evidence': {
                'historical_samples': total_count,
                'match_range': match_range,
                'dates': similar_patterns['date'].astype(str).tolist()[:10]  # แสดง 10 วันแรก
            }
        }
        
        # แสดงผลสรุป
        self._print_prediction_summary(prediction)
        
        return prediction
    
    def _print_prediction_summary(self, pred):
        """
        แสดงผลสรุปการทำนาย
        """
        print(f"\n{'='*60}")
        print(f"📊 PREDICTION SUMMARY")
        print(f"{'='*60}")
        
        print(f"\n🎯 Input:")
        print(f"   Today's movement: {pred['input']['today_change']:+.2f}% ({pred['input']['today_direction'].upper()})")
        
        print(f"\n🔮 Prediction for Tomorrow:")
        print(f"   Direction: {pred['prediction']['direction']}")
        print(f"   Expected change (average): {pred['prediction']['expected_change_avg']:+.2f}%")
        print(f"   Expected change (median): {pred['prediction']['expected_change_median']:+.2f}%")
        print(f"   Confidence: {pred['prediction']['confidence']:.1f}%")
        
        print(f"\n📈 Probability Breakdown:")
        print(f"   Up: {pred['probability_breakdown']['up']:.1f}%")
        print(f"   Down: {pred['probability_breakdown']['down']:.1f}%")
        print(f"   Sideways: {pred['probability_breakdown']['sideways']:.1f}%")
        
        print(f"\n⚠️ Risk Assessment:")
        print(f"   Standard deviation: ±{pred['risk_assessment']['std_deviation']:.2f}%")
        print(f"   Best case: {pred['risk_assessment']['best_case']:+.2f}%")
        print(f"   Worst case: {pred['risk_assessment']['worst_case']:+.2f}%")
        print(f"   Risk/Reward ratio: {pred['risk_assessment']['risk_reward_ratio']:.2f}")
        
        print(f"\n📚 Evidence:")
        print(f"   Based on {pred['evidence']['historical_samples']} similar historical patterns")
        print(f"   Match range: ±{pred['evidence']['match_range']}%")
        
        print(f"\n{'='*60}")
    
    def batch_predict(self, recent_days=10):
        """
        ทำนายสำหรับหลายๆ วันล่าสุด (ใช้สำหรับ backtesting)
        
        Args:
            recent_days: จำนวนวันล่าสุดที่ต้องการทำนาย
        
        Returns:
            list: รายการ predictions
        """
        predictions = []
        
        for i in range(-recent_days, 0):
            try:
                today_change = self.df.iloc[i]['pct_change']
                
                if abs(today_change) >= self.threshold:
                    pred = self.predict_tomorrow(today_change, match_range=0.5, min_samples=3)
                    
                    # เพิ่มข้อมูลจริงของวันถัดไป
                    if i + 1 < 0:
                        actual_tomorrow = self.df.iloc[i + 1]['pct_change']
                        actual_direction = classify_direction(actual_tomorrow, SIDEWAYS_THRESHOLD)
                        
                        pred['actual'] = {
                            'change': actual_tomorrow,
                            'direction': actual_direction.upper(),
                            'correct_direction': pred['prediction']['direction'] == actual_direction.upper()
                        }
                    
                    predictions.append(pred)
            except Exception as e:
                continue
        
        return predictions


# Example usage
if __name__ == "__main__":
    from data_fetcher import StockDataFetcher
    
    # Fetch data
    fetcher = StockDataFetcher()
    df = fetcher.fetch_daily_data('PTT', 'SET', n_bars=2000)
    
    if df is not None:
        # สร้าง predictor
        predictor = HistoricalPredictor(df, threshold=1.0)
        
        # ทดสอบ: สมมติวันนี้หุ้นขึ้น +1.8%
        print("\n" + "="*70)
        print("TEST SCENARIO 1: วันนี้หุ้นขึ้น +1.8%")
        print("="*70)
        prediction = predictor.predict_tomorrow(today_pct_change=1.8)
        
        print("\n" + "="*70)
        print("TEST SCENARIO 2: วันนี้หุ้นลง -2.5%")
        print("="*70)
        prediction = predictor.predict_tomorrow(today_pct_change=-2.5)
        
        # Batch predict สำหรับ 5 วันล่าสุด
        print("\n" + "="*70)
        print("BACKTESTING: 5 วันล่าสุด")
        print("="*70)
        batch_results = predictor.batch_predict(recent_days=5)
        
        for i, pred in enumerate(batch_results, 1):
            print(f"\n{i}. Today: {pred['input']['today_change']:+.2f}% → Predicted: {pred['prediction']['direction']} ({pred['prediction']['confidence']:.1f}%)")
            if 'actual' in pred:
                print(f"   Actual: {pred['actual']['direction']} ({pred['actual']['change']:+.2f}%) - {'✅ CORRECT' if pred['actual']['correct_direction'] else '❌ WRONG'}")
