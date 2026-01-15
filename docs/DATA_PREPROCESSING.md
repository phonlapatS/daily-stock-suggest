# Data Preprocessing Pipeline - Complete Guide

## 🔄 Overview

Data Preprocessing คือขั้นตอนทำความสะอาดและเตรียมข้อมูลก่อนนำไปวิเคราะห์

---

## 📦 Pipeline Components

### **1. data_cleaner.py** - Data Cleaning

#### **Purpose:**
ทำความสะอาดข้อมูลที่ดาวน์โหลดมา

#### **Functions:**

##### **A. Remove Duplicates**
```python
def remove_duplicates(df):
    """
    ลบข้อมูลซ้ำ (duplicate timestamps)
    """
    # ก่อนทำความสะอาด
    print(f"Before: {len(df)} rows")
    
    # ลบ duplicate index (เก็บตัวล่าสุด)
    df = df[~df.index.duplicated(keep='last')]
    
    print(f"After: {len(df)} rows")
    print(f"Removed: {removed} duplicates")
    
    return df
```

**Example:**
```
Before: 3005 rows
After:  3001 rows
Removed: 4 duplicates (same timestamp occurred twice)
```

##### **B. Remove NaN Values**
```python
def remove_nan(df):
    """
    ลบแถวที่มีข้อมูลหาย (NaN)
    """
    # ก่อน
    print(f"NaN in close: {df['close'].isna().sum()}")
    
    # ลบแถวที่มี NaN
    df = df.dropna()
    
    # หลัง
    print(f"Clean data: {len(df)} rows")
    
    return df
```

**Example:**
```
NaN in close: 3 rows
NaN in volume: 1 row
Dropped: 4 rows
Clean data: 2997 rows
```

##### **C. Validate Price Range**
```python
def validate_prices(df):
    """
    เช็คว่าราคาสมเหตุสมผล
    """
    # ราคาติดลบ?
    if (df['close'] < 0).any():
        print("❌ Negative prices found!")
        df = df[df['close'] >= 0]
    
    # ราคากระโดดผิดปกติ? (>50% ใน 1 วัน)
    pct_change = df['close'].pct_change() * 100
    outliers = df[abs(pct_change) > 50]
    
    if len(outliers) > 0:
        print(f"⚠️ {len(outliers)} extreme moves found")
        # สำหรับหุ้นไทย circuit breaker = 30%
        # >50% น่าจะผิดพลาด
```

##### **D. Sort by Date**
```python
def sort_by_date(df):
    """
    เรียงตามวันที่ (เก่า → ใหม่)
    """
    df = df.sort_index()
    
    # ตรวจสอบว่าเรียงถูกแล้ว
    assert df.index.is_monotonic_increasing
    
    return df
```

---

### **2. batch_processor.py** - Batch Operations

#### **Purpose:**
ประมวลผลหลายไฟล์พร้อมกัน

#### **Functions:**

##### **A. Batch Clean**
```python
def batch_clean(data_dir='data/stocks'):
    """
    ทำความสะอาดทุกไฟล์ในครั้งเดียว
    """
    files = glob('data/stocks/*.parquet')
    
    for file in files:
        df = pd.read_parquet(file)
        
        # Clean
        df = remove_duplicates(df)
        df = remove_nan(df)
        df = sort_by_date(df)
        
        # Save cleaned
        df.to_parquet(file)
        
    print(f"✅ Cleaned {len(files)} files")
```

##### **B. Batch Calculate**
```python
def batch_calculate_pct_change(data_dir):
    """
    คำนวณ pct_change ให้ทุกไฟล์
    """
    files = glob('data/stocks/*.parquet')
    
    for file in files:
        df = pd.read_parquet(file)
        
        # Calculate pct_change
        if 'pct_change' not in df.columns:
            df['pct_change'] = df['close'].pct_change() * 100
        
        # Save
        df.to_parquet(file)
```

---

### **3. data_cache.py** - Caching System

#### **Purpose:**
เก็บ cache เพื่อเร็วขึ้น

#### **Functions:**

##### **A. Load with Cache**
```python
def load_stock_cached(symbol, exchange):
    """
    Load ข้อมูลพร้อม cache
    """
    cache_key = f"{symbol}_{exchange}"
    
    # Check cache first
    if cache_key in cache:
        return cache[cache_key]
    
    # Load from file
    df = pd.read_parquet(f'data/stocks/{cache_key}.parquet')
    
    # Store in cache
    cache[cache_key] = df
    
    return df
```

**Performance:**
```
First load:  0.05 seconds (from disk)
Cached:      0.001 seconds (50x faster!)
```

---

## 🔄 Complete Preprocessing Workflow

### **Step-by-Step:**

```python
# 1. Download Raw Data
df = tv.get_hist(symbol='PTT', exchange='SET', n_bars=3000)

# 2. Remove Duplicates
df = df[~df.index.duplicated(keep='last')]
# Before: 3005 rows → After: 3001 rows

# 3. Remove NaN
df = df.dropna()
# Before: 3001 rows → After: 2998 rows

# 4. Sort by Date
df = df.sort_index()
# Ensure: oldest → newest

# 5. Validate Prices
assert (df['close'] > 0).all()
assert df['close'].max() < 1000  # Sanity check

# 6. Calculate pct_change
df['pct_change'] = df['close'].pct_change() * 100
# NaN for first row

# 7. Save to Parquet
df.to_parquet('data/stocks/PTT_SET.parquet')
```

---

## 📊 Data Quality Checks

### **Automated Checks:**

```python
def validate_data_quality(df):
    """
    เช็คคุณภาพข้อมูล
    """
    checks = {
        'no_duplicates': not df.index.duplicated().any(),
        'no_nan': not df['close'].isna().any(),
        'sorted': df.index.is_monotonic_increasing,
        'positive_prices': (df['close'] > 0).all(),
        'volume_exists': (df['volume'] > 0).any(),
        'pct_change_calculated': 'pct_change' in df.columns
    }
    
    # Report
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all(checks.values())
```

**Example Output:**
```
✅ no_duplicates
✅ no_nan
✅ sorted
✅ positive_prices
✅ volume_exists
✅ pct_change_calculated

Result: PASS ✅
```

---

## 🐛 Common Issues & Fixes

### **Issue 1: Duplicate Timestamps**
```python
# Problem
2026-01-14 09:00:00   32.75   100M
2026-01-14 09:00:00   32.80   50M   ← duplicate!

# Fix
df = df[~df.index.duplicated(keep='last')]
# Keep latest value: 32.80
```

### **Issue 2: Missing Data (NaN)**
```python
# Problem
2026-01-14   32.75   100M
2026-01-15   NaN     NaN     ← missing!
2026-01-16   33.00   80M

# Fix
df = df.dropna()
# Remove row with NaN
```

### **Issue 3: Wrong Order**
```python
# Problem
2026-01-15   32.75   ← latest first
2026-01-14   32.50
2026-01-13   31.75

# Fix
df = df.sort_index()
# Oldest → Newest
2026-01-13   31.75
2026-01-14   32.50
2026-01-15   32.75
```

### **Issue 4: Extreme Values**
```python
# Problem
2026-01-14   32.75   +3%     ← normal
2026-01-15   65.50   +100%   ← error!

# Fix
pct = df['close'].pct_change() * 100
outliers = df[abs(pct) > 50]
print(f"Outliers: {outliers}")
# Manual review required
```

---

## 💡 Best Practices

### **1. Always Clean Before Analysis**
```python
# Bad
df = pd.read_parquet('stock.parquet')
analyze(df)  # May have duplicates, NaN!

# Good
df = pd.read_parquet('stock.parquet')
df = clean_data(df)  # Clean first
analyze(df)  # Safe!
```

### **2. Validate After Download**
```python
# After download
df = download_stock('PTT')

# Immediate check
assert len(df) > 100  # Enough data?
assert not df['close'].isna().any()  # Complete?
assert df.index.is_monotonic_increasing  # Sorted?
```

### **3. Use Caching for Speed**
```python
# Slow (load every time)
for i in range(100):
    df = pd.read_parquet('PTT.parquet')  # 0.05s × 100 = 5s

# Fast (load once)
df = load_cached('PTT')  # 0.05s once
for i in range(100):
    use(df)  # 0.001s × 100 = 0.1s
```

---

## 🎯 Real Example

### **PTT Data Processing:**

```python
# 1. Download
raw_df = download_from_tradingview('PTT')
print(f"Raw: {len(raw_df)} rows")
# Raw: 3005 rows

# 2. Clean
cleaned = remove_duplicates(raw_df)
print(f"After dedup: {len(cleaned)} rows")
# After dedup: 3001 rows

cleaned = cleaned.dropna()
print(f"After NaN: {len(cleaned)} rows")
# After NaN: 3001 rows (no NaN!)

# 3. Sort
cleaned = cleaned.sort_index()

# 4. Calculate
cleaned['pct_change'] = cleaned['close'].pct_change() * 100

# 5. Validate
assert validate_data_quality(cleaned)
print("✅ Data quality: PASS")

# 6. Save
cleaned.to_parquet('data/stocks/PTT_SET.parquet')
print("💾 Saved clean data")
```

**Result:**
```
Raw data:        3005 rows
Duplicates:      -4 rows
NaN values:       0 rows
Final:           3001 rows
Quality:         ✅ PASS
```

---

## ✅ Summary

### **Preprocessing Steps:**

1. **Download** - ดึงข้อมูลดิบ
2. **Deduplicate** - ลบซ้ำ
3. **Remove NaN** - ลบข้อมูลหาย
4. **Sort** - เรียงตามวันที่
5. **Validate** - ตรวจสอบคุณภาพ
6. **Calculate** - คำนวณ pct_change
7. **Save** - บันทึก clean data

### **Tools:**
- `data_cleaner.py` - ทำความสะอาด
- `batch_processor.py` - ประมวลผลเป็น batch
- `data_cache.py` - เพิ่มความเร็วด้วย cache

### **Quality Checks:**
- ✅ No duplicates
- ✅ No NaN
- ✅ Sorted by date
- ✅ Positive prices
- ✅ pct_change calculated

**ข้อมูลพร้อมใช้ 100%!** 🔄✨
