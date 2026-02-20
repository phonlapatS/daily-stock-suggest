import pandas as pd
from datetime import datetime
from core.performance import verify_forecast

print('🔧 บังคับตรวจสอบ forecasts วันนี้:')
print()

# รัน verify_forecast โดยตรง
result = verify_forecast()

print(f'📊 ผลลัพธ์: {result}')

# ตรวจสอบข้อมูลหลังจาก verify_forecast
df = pd.read_csv('logs/performance_log.csv')
today = '2026-02-18'
today_forecasts = df[df['scan_date'] == today]

print()
print('🔍 ตรวจสอบข้อมูลหลังจาก verify_forecast:')
print(f'   - จำนวน forecasts: {len(today_forecasts)}')
print(f'   - สถานะ actual:')
print(f'     - Pending: {len(today_forecasts[today_forecasts["actual"] == "PENDING"])}')
print(f'     - Verified: {len(today_forecasts[today_forecasts["actual"] != "PENDING"])}')
print()

if len(today_forecasts) > 0:
    print('📊 รายละเอียด forecasts วันนี้:')
    for _, row in today_forecasts.iterrows():
        symbol = row['symbol']
        exchange = row['exchange']
        scan_date = row['scan_date']
        target_date = row['target_date']
        actual = row['actual']
        forecast = row['forecast']
        price_actual = row['price_actual']
        correct = row['correct']
        
        print(f'   - {symbol} ({exchange})')
        print(f'     Scan: {scan_date} -> Target: {target_date}')
        print(f'     Forecast: {forecast} | Actual: {actual} | Correct: {correct}')
        print(f'     Price: {price_actual}')
        print()
