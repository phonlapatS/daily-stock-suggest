import pandas as pd

# อ่านข้อมูลจาก Master Pattern Stats
master_df = pd.read_csv('E:/PredictPlus1/data/Master_Pattern_Stats.csv')
master_symbols = set(master_df['Symbol'].unique())

# อ่านข้อมูลจาก performance_log.csv
perf_df = pd.read_csv('E:/PredictPlus1/logs/performance_log.csv')
perf_symbols = set(perf_df['symbol'].unique())

# หาหุ้นที่มีใน performance_log แต่ไม่มีใน Master Stats
missing_symbols = perf_symbols - master_symbols

print('📊 ตรวจสอบหุ้นที่ขาดไปจาก Master Stats:')
print(f'   - มีใน Performance Log: {len(perf_symbols)} หุ้น')
print(f'   - มีใน Master Stats: {len(master_symbols)} หุ้น')
print(f'   - ขาดไป: {len(missing_symbols)} หุ้น')
print()

if missing_symbols:
    print('🔍 หุ้นที่ขาดไป:')
    for symbol in sorted(missing_symbols):
        # ดูว่าหุ้นนี้อยู่ exchange ไหน
        exchange = perf_df[perf_df['symbol'] == symbol]['exchange'].iloc[0]
        print(f'   - {symbol} ({exchange})')
    
    print()
    print('📊 สรุปตาม exchange:')
    exchange_missing = {}
    for symbol in missing_symbols:
        exchange = perf_df[perf_df['symbol'] == symbol]['exchange'].iloc[0]
        if exchange not in exchange_missing:
            exchange_missing[exchange] = []
        exchange_missing[exchange].append(symbol)
    
    for exchange, symbols in exchange_missing.items():
        print(f'   - {exchange}: {len(symbols)} หุ้น')
        print(f'     {", ".join(symbols)}')
    
    print()
    print('🔧 เพิ่มหุ้นที่ขาดไปเข้า Master Stats:')
    
    # สร้าง DataFrame สำหรับหุ้นที่ขาดไป
    missing_data = []
    for symbol in missing_symbols:
        symbol_data = perf_df[perf_df['symbol'] == symbol].iloc[0]
        
        # สร้าง record สำหรับ Master Pattern Stats
        new_record = {
            'Symbol': symbol,
            'Threshold': symbol_data.get('threshold', 1.0),
            'Max_Streak_Pos': 0,
            'Max_Streak_Neg': 0,
            'Pattern': '-',
            'Pattern_Name': 'Unknown',
            'Category': 'Unknown',
            'Chance': '🟢 UP',
            'Prob': 50,
            'Stats': '0/0 (5000)'
        }
        missing_data.append(new_record)
    
    # เพิ่มข้อมูลเข้า Master Stats
    missing_df = pd.DataFrame(missing_data)
    combined_df = pd.concat([master_df, missing_df], ignore_index=True)
    
    # บันทึกกลับไป
    combined_df.to_csv('E:/PredictPlus1/data/Master_Pattern_Stats.csv', index=False)
    
    print(f'✅ เพิ่ม {len(missing_data)} หุ้นเข้า Master_Pattern_Stats.csv เรียบร้อยแล้ว')
    print(f'📊 รวมหุ้นทั้งหมด: {len(combined_df["Symbol"].unique())} หุ้น')
    
else:
    print('✅ ไม่มีหุ้นที่ขาดไป ข้อมูลครบถ้วนแล้ว!')
