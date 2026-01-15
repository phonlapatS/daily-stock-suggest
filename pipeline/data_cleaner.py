"""
data_cleaner.py - Robust Financial Data Cleaning & Preprocessing
================================================================

Purpose: ทำความสะอาดข้อมูล OHLCV จาก TradingView
- Standardization (lowercase, DatetimeIndex)
- Deduplication (ลบซ้ำ)
- Sanity Checks (ลบข้อมูลผิดปกติ)
- Timezone Handling (intraday)
- Feature Calculation (pct_change)
"""

import pandas as pd
import numpy as np
from datetime import datetime


def clean_and_preprocess_data(df, asset_type='stock'):
    """
    ทำความสะอาดและเตรียมข้อมูล OHLCV
    
    Args:
        df: Raw DataFrame จาก TradingView
        asset_type: 'stock' (daily) หรือ 'intraday' (gold/silver)
    
    Returns:
        DataFrame: ข้อมูลที่สะอาดและพร้อมใช้งาน
    
    Cleaning Steps:
        1. Standardization - lowercase columns, sort by date
        2. Deduplication - ลบ timestamp ซ้ำ (เก็บตัวใหม่)
        3. Sanity Checks - ลบข้อมูลผิดปกติ
        4. Timezone - แปลงเป็น Asia/Bangkok (ถ้า intraday)
        5. Feature Calc - คำนวณ % change
    """
    
    # เก็บจำนวนเริ่มต้น
    original_count = len(df)
    
    if df is None or df.empty:
        print("❌ DataFrame is None or empty")
        return df
    
    print(f"\n🔧 Cleaning data ({original_count} rows)...")
    
    # ==========================================
    # Step 1: Standardization
    # ==========================================
    
    # 1.1 Lowercase column names + strip whitespace
    df.columns = df.columns.str.lower().str.strip()
    
    # 1.2 Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        # ถ้า index ไม่ใช่ datetime แปลงให้
        if 'datetime' in df.columns:
            df.set_index('datetime', inplace=True)
        elif 'date' in df.columns:
            df.set_index('date', inplace=True)
        
        # แปลงเป็น DatetimeIndex
        df.index = pd.to_datetime(df.index)
    
    # 1.3 Sort by date (chronological)
    df = df.sort_index()
    
    # ==========================================
    # Step 2: Deduplication (Critical!)
    # ==========================================
    
    duplicates_before = df.index.duplicated().sum()
    
    if duplicates_before > 0:
        # keep='last' = เก็บตัวใหม่สุด (สมมติว่าถูกต้องกว่า)
        df = df[~df.index.duplicated(keep='last')]
    
    # ==========================================
    # Step 3: Sanity Checks
    # ==========================================
    
    bad_rows = 0
    
    # 3.1 Drop rows where OHLC <= 0
    price_cols = ['open', 'high', 'low', 'close']
    for col in price_cols:
        if col in df.columns:
            invalid = (df[col] <= 0).sum()
            if invalid > 0:
                df = df[df[col] > 0]
                bad_rows += invalid
    
    # 3.2 Drop rows where High < Low (logical error)
    if 'high' in df.columns and 'low' in df.columns:
        invalid_hl = (df['high'] < df['low']).sum()
        if invalid_hl > 0:
            df = df[df['high'] >= df['low']]
            bad_rows += invalid_hl
    
    # 3.3 Drop rows with NaN
    nan_before = df.isna().any(axis=1).sum()
    if nan_before > 0:
        df = df.dropna()
        bad_rows += nan_before
    
    # ==========================================
    # Step 4: Timezone Handling (Intraday)
    # ==========================================
    
    if asset_type == 'intraday':
        # แปลงเป็น Asia/Bangkok (UTC+7)
        if df.index.tz is None:
            # Naive datetime -> ต้องระบุ timezone ก่อน
            df.index = df.index.tz_localize('UTC')
        
        # แปลงเป็น Bangkok time
        df.index = df.index.tz_convert('Asia/Bangkok')
    
    # ==========================================
    # Step 5: Feature Calculation
    # ==========================================
    
    if 'close' in df.columns:
        # คำนวณ % change
        df['pct_change'] = df['close'].pct_change() * 100
        
        # Drop first row (NaN after pct_change)
        if not df.empty and pd.isna(df.iloc[0]['pct_change']):
            df = df.iloc[1:]
    
    # ==========================================
    # Step 6: Reporting
    # ==========================================
    
    final_count = len(df)
    total_removed = original_count - final_count
    
    print(f"✅ Cleaned: Removed {duplicates_before} duplicates and {bad_rows} bad rows")
    print(f"   Original: {original_count} → Final: {final_count} ({total_removed} removed)")
    
    if asset_type == 'intraday':
        print(f"   Timezone: {df.index.tz}")
    
    return df


def validate_cleaned_data(df):
    """
    ตรวจสอบว่าข้อมูลสะอาดแล้วหรือยัง
    
    Returns:
        bool: True ถ้าผ่านทุกเงื่อนไข
    """
    
    checks = []
    
    # 1. DatetimeIndex
    checks.append(("DatetimeIndex", isinstance(df.index, pd.DatetimeIndex)))
    
    # 2. No duplicates
    checks.append(("No duplicates", not df.index.duplicated().any()))
    
    # 3. No NaN
    checks.append(("No NaN", not df.isna().any().any()))
    
    # 4. OHLC > 0
    for col in ['open', 'high', 'low', 'close']:
        if col in df.columns:
            checks.append((f"{col} > 0", (df[col] > 0).all()))
    
    # 5. High >= Low
    if 'high' in df.columns and 'low' in df.columns:
        checks.append(("High >= Low", (df['high'] >= df['low']).all()))
    
    # 6. Has pct_change
    checks.append(("Has pct_change", 'pct_change' in df.columns))
    
    # Print results
    print("\n📊 Validation Results:")
    all_passed = True
    for name, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"   {icon} {name}")
        if not passed:
            all_passed = False
    
    return all_passed


# ==========================================
# Example Usage
# ==========================================

if __name__ == "__main__":
    # สร้างข้อมูลทดสอบ (มี errors)
    test_data = {
        'datetime': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Open': [100, 101, 0, 103, 104, 105, 106, 107, 108, 109],  # มี 0
        'High': [102, 103, 104, 105, 100, 107, 108, 109, 110, 111],  # High < Low
        'Low': [99, 100, 101, 102, 106, 104, 105, 106, 107, 108],
        'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'Volume': [1000] * 10
    }
    
    df = pd.DataFrame(test_data)
    df.set_index('datetime', inplace=True)
    
    # เพิ่ม duplicate
    df = pd.concat([df, df.iloc[[0]]])
    
    print("Before cleaning:")
    print(df.head())
    print(f"Shape: {df.shape}")
    
    # Clean
    df_clean = clean_and_preprocess_data(df, asset_type='stock')
    
    print("\nAfter cleaning:")
    print(df_clean.head())
    print(f"Shape: {df_clean.shape}")
    
    # Validate
    validate_cleaned_data(df_clean)
