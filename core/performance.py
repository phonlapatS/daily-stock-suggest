"""
performance.py - Performance Logging Module
============================================
บันทึก forecast และ verify ผลจริงเพื่อวัดความแม่นยำ

Functions:
- log_forecast(): บันทึก forecast วันนี้
- verify_forecast(): เช็คผลจริง + อัปเดต correct
- get_accuracy(): คำนวณ % accuracy
- backtest(): ทดสอบ accuracy ด้วย historical data
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed, Interval

# Path to log file
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'performance_log.csv')

# CSV Columns
COLUMNS = [
    'scan_date',      # วันที่สแกน
    'target_date',    # วันที่ทำนาย (N+1)
    'symbol',         # หุ้น
    'exchange',       # ตลาด
    'pattern',        # Pattern ที่ตรวจจับ
    'forecast',       # UP / DOWN
    'prob',           # Probability %
    'conf',           # Confidence %
    'stats',          # จำนวนครั้ง
    'price_at_scan',  # ราคา ณ เวลาสแกน
    'actual',         # UP / DOWN / PENDING
    'price_actual',   # ราคาวันถัดไป
    'correct',        # 1 / 0 / null
    'last_update'     # Timestamp อัปเดตล่าสุด
]


def _ensure_log_file():
    """สร้าง log file ถ้ายังไม่มี"""
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(LOG_FILE, index=False)
        print(f"📁 Created: {LOG_FILE}")


def log_forecast(results, group_info=None):
    """
    บันทึก forecast ลง CSV
    
    Args:
        results: list of dicts จาก main.py (filtered_data)
        group_info: dict ข้อมูล asset group (optional)
    
    Returns:
        int: จำนวน records ที่บันทึก
    """
    _ensure_log_file()
    
    if not results:
        return 0
    
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    records = []
    for r in results:
        # Determine forecast direction
        avg_ret = r.get('avg_return', 0)
        if avg_ret > 0:
            forecast = 'UP'
            prob = r.get('bull_prob', 50)
        elif avg_ret < 0:
            forecast = 'DOWN'
            prob = r.get('bear_prob', 50)
        else:
            forecast = 'NEUTRAL'
            prob = 50
        
        record = {
            'scan_date': today,
            'target_date': tomorrow,
            'symbol': r.get('symbol', 'Unknown'),
            'exchange': r.get('exchange', 'SET'),  # Use actual exchange, not group name
            'pattern': r.get('pattern_display', ''),
            'forecast': forecast,
            'prob': round(prob, 1),
            'conf': round(r.get('conf', 0), 1),
            'stats': r.get('matches', 0),
            'price_at_scan': round(r.get('price', 0), 2),
            'actual': 'PENDING',
            'price_actual': None,
            'correct': None,
            'last_update': now
        }
        records.append(record)
    
    # Append to CSV (handle empty file case)
    df_existing = pd.read_csv(LOG_FILE)
    df_new = pd.DataFrame(records)
    
    if df_existing.empty:
        # First time logging - use new data directly
        print("📝 [Note] First time logging - creating new log file")
        df_combined = df_new
    else:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    
    df_combined.to_csv(LOG_FILE, index=False)
    
    print(f"📝 Logged {len(records)} forecasts to {LOG_FILE}")
    return len(records)


def verify_forecast(tv=None):
    """
    ตรวจสอบ forecast ที่ยัง PENDING และอัปเดตผลจริง
    
    Args:
        tv: TvDatafeed instance (optional, จะสร้างใหม่ถ้าไม่มี)
    
    Returns:
        dict: สรุปผลการ verify
    """
    _ensure_log_file()
    
    df = pd.read_csv(LOG_FILE)
    
    if df.empty:
        print("📊 No forecasts to verify (log file is empty)")
        return {'verified': 0, 'correct': 0, 'incorrect': 0}
    
    # Filter PENDING rows ที่ target_date <= วันนี้
    today = datetime.now().strftime('%Y-%m-%d')
    pending = df[(df['actual'] == 'PENDING') & (df['target_date'] <= today)]
    
    if pending.empty:
        print("📊 No pending forecasts to verify (all forecasts are either verified or target_date is in future)")
        return {'verified': 0, 'correct': 0, 'incorrect': 0}
    
    # Connect to TradingView if needed
    if tv is None:
        try:
            tv = TvDatafeed()
        except Exception as e:
            print(f"⚠️ Cannot connect to TradingView: {e}")
            return {'verified': 0, 'correct': 0, 'incorrect': 0, 'error': str(e)}
    
    verified = 0
    correct = 0
    incorrect = 0
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for idx, row in pending.iterrows():
        try:
            # Fetch latest price
            symbol = row['symbol']
            exchange = row['exchange']
            
            # Get 2 bars to compare
            data = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=5
            )
            
            if data is None or len(data) < 2:
                continue
            
            # Get price at scan date and target date
            price_at_scan = row['price_at_scan']
            price_actual = data['close'].iloc[-1]
            
            # Determine actual direction
            if price_actual > price_at_scan:
                actual = 'UP'
            elif price_actual < price_at_scan:
                actual = 'DOWN'
            else:
                actual = 'NEUTRAL'
            
            # Check if correct
            is_correct = 1 if row['forecast'] == actual else 0
            
            # Update row
            df.loc[idx, 'actual'] = actual
            df.loc[idx, 'price_actual'] = round(price_actual, 2)
            df.loc[idx, 'correct'] = is_correct
            df.loc[idx, 'last_update'] = now
            
            verified += 1
            if is_correct:
                correct += 1
            else:
                incorrect += 1
                
        except Exception as e:
            print(f"⚠️ Error verifying {row['symbol']}: {e}")
            continue
    
    # Save updated CSV
    df.to_csv(LOG_FILE, index=False)
    
    print(f"✅ Verified: {verified} | Correct: {correct} | Incorrect: {incorrect}")
    return {'verified': verified, 'correct': correct, 'incorrect': incorrect}


def get_accuracy(days=30):
    """
    คำนวณ accuracy summary
    
    Args:
        days: จำนวนวันย้อนหลัง (default 30)
    
    Returns:
        dict: สรุป accuracy
    """
    _ensure_log_file()
    
    df = pd.read_csv(LOG_FILE)
    
    if df.empty:
        return {'total': 0, 'accuracy': 0}
    
    # Filter by date range
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    df_period = df[(df['scan_date'] >= cutoff) & (df['actual'] != 'PENDING')]
    
    if df_period.empty:
        return {'total': 0, 'accuracy': 0}
    
    total = len(df_period)
    correct = df_period['correct'].sum()
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    # By symbol
    by_symbol = df_period.groupby('symbol').agg({
        'correct': ['sum', 'count']
    }).reset_index()
    by_symbol.columns = ['symbol', 'correct', 'total']
    by_symbol['accuracy'] = (by_symbol['correct'] / by_symbol['total'] * 100).round(1)
    
    return {
        'total': total,
        'correct': int(correct),
        'accuracy': round(accuracy, 1),
        'by_symbol': by_symbol.to_dict('records') if len(by_symbol) <= 20 else None
    }


def backtest(symbol, exchange, n_bars=500, threshold_multiplier=1.25, min_stats=30):
    """
    🔬 Backtest: ทดสอบ accuracy ของ pattern matching ด้วย historical data
    
    ไม่ต้องรอผลจริง - ใช้ข้อมูลในอดีตมาทดสอบทันที
    
    Args:
        symbol: สัญลักษณ์หุ้น เช่น 'PTT', 'NVDA'
        exchange: ตลาด เช่น 'SET', 'NASDAQ'
        n_bars: จำนวนวันที่จะใช้ทดสอบ (default 500)
        threshold_multiplier: ตัวคูณ SD สำหรับ threshold (default 1.25)
        min_stats: จำนวน sample ขั้นต่ำ (default 30)
    
    Returns:
        dict: สรุปผล backtest
    
    How it works:
        1. ดึงข้อมูล 5000+ bars
        2. แบ่งเป็น: Training (4500 bars) + Test (500 bars)
        3. คำนวณ patterns จาก Training data
        4. ทดสอบ accuracy กับ Test data
    """
    print(f"\n🔬 BACKTEST: {symbol} ({exchange})")
    print("=" * 50)
    
    try:
        tv = TvDatafeed()
        df = tv.get_hist(symbol=symbol, exchange=exchange, 
                         interval=Interval.in_daily, n_bars=5000)
        
        if df is None or len(df) < 1000:
            print(f"❌ Not enough data for {symbol}")
            return None
        
        print(f"📊 Data: {len(df)} bars")
        
        # Calculate returns and threshold
        close = df['close']
        pct_change = close.pct_change()
        
        # Rolling volatility
        short_std = pct_change.rolling(20).std()
        long_std = pct_change.rolling(252).std()
        effective_std = np.maximum(short_std, long_std.fillna(0) * 0.5)
        threshold = effective_std * threshold_multiplier
        
        # Convert to +/- pattern
        patterns = []
        for i in range(len(pct_change)):
            if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
                patterns.append('')
            elif pct_change.iloc[i] > threshold.iloc[i]:
                patterns.append('+')
            elif pct_change.iloc[i] < -threshold.iloc[i]:
                patterns.append('-')
            else:
                patterns.append('')
        
        # Split: Train (first 4500) / Test (last 500)
        train_end = len(df) - n_bars
        
        print(f"   Train: 0 → {train_end} ({train_end} bars)")
        print(f"   Test:  {train_end} → {len(df)} ({n_bars} bars)")
        
        # Build pattern stats from Training data
        pattern_stats = {}  # {pattern: {'up': count, 'down': count}}
        
        for i in range(10, train_end - 1):
            # Get 4-day pattern ending at day i
            pat = ''.join(patterns[i-3:i+1])
            if len(pat) < 2:  # Skip if too few significant days
                continue
            
            # Next day result
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            if pat not in pattern_stats:
                pattern_stats[pat] = {'up': 0, 'down': 0}
            
            if next_ret > 0:
                pattern_stats[pat]['up'] += 1
            else:
                pattern_stats[pat]['down'] += 1
        
        print(f"   Patterns found: {len(pattern_stats)}")
        
        # Test on Test data
        total_predictions = 0
        correct_predictions = 0
        predictions = []
        
        for i in range(train_end, len(df) - 1):
            # Get 4-day pattern
            pat = ''.join(patterns[i-3:i+1])
            if len(pat) < 2 or pat not in pattern_stats:
                continue
            
            stats = pattern_stats[pat]
            total = stats['up'] + stats['down']
            
            if total < min_stats:
                continue
            
            # Predict
            if stats['up'] > stats['down']:
                forecast = 'UP'
                prob = stats['up'] / total * 100
            else:
                forecast = 'DOWN'
                prob = stats['down'] / total * 100
            
            # Actual result
            next_ret = pct_change.iloc[i+1]
            if pd.isna(next_ret):
                continue
            
            actual = 'UP' if next_ret > 0 else 'DOWN'
            is_correct = 1 if forecast == actual else 0
            
            total_predictions += 1
            correct_predictions += is_correct
            
            predictions.append({
                'date': df.index[i],
                'pattern': pat,
                'forecast': forecast,
                'prob': prob,
                'actual': actual,
                'correct': is_correct
            })
        
        if total_predictions == 0:
            print("❌ No predictions made (no patterns met min_stats threshold)")
            return None
        
        accuracy = correct_predictions / total_predictions * 100
        
        print(f"\n📊 BACKTEST RESULTS")
        print("-" * 50)
        print(f"   Total Predictions: {total_predictions}")
        print(f"   Correct:          {correct_predictions}")
        print(f"   Accuracy:         {accuracy:.1f}%")
        
        # By pattern
        if predictions:
            df_pred = pd.DataFrame(predictions)
            by_pattern = df_pred.groupby('pattern').agg({
                'correct': ['sum', 'count']
            }).reset_index()
            by_pattern.columns = ['pattern', 'correct', 'total']
            by_pattern['accuracy'] = (by_pattern['correct'] / by_pattern['total'] * 100).round(1)
            by_pattern = by_pattern.sort_values('total', ascending=False).head(10)
            
            print(f"\n📈 Top 10 Patterns:")
            print(f"   {'Pattern':<10} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
            print("-" * 50)
            for _, row in by_pattern.iterrows():
                print(f"   {row['pattern']:<10} {int(row['correct']):<10} {int(row['total']):<10} {row['accuracy']:.1f}%")
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'total': total_predictions,
            'correct': correct_predictions,
            'accuracy': round(accuracy, 1),
            'patterns_tested': len(pattern_stats)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# For direct testing
if __name__ == "__main__":
    print("📊 Performance Module Test")
    print("=" * 50)
    
    # Test get_accuracy
    stats = get_accuracy()
    print(f"Total: {stats['total']}")
    print(f"Accuracy: {stats['accuracy']}%")
    
    print("\n" + "=" * 50)
    print("🔬 Running Backtest...")
    print("=" * 50)
    
    # Quick backtest example
    backtest('PTT', 'SET', n_bars=200)
