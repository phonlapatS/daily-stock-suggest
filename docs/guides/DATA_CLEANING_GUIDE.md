# คู่มือ Data Cleaning & Preprocessing

## 🎯 ภาพรวม

**data_cleaner.py** = โมดูลทำความสะอาดข้อมูล OHLCV อย่างเข้มงวด

### ปัญหาที่แก้:
- ❌ ข้อมูลซ้ำ (duplicate timestamps)
- ❌ ราคาผิดปกติ (price <= 0, High < Low)
- ❌ ข้อมูลหาย (NaN values)
- ❌ Timezone ไม่ตรง (สำหรับ intraday)
- ❌ ขาด % change

### วิธีแก้:
- ✅ Deduplication (เก็บตัวใหม่สุด)
- ✅ Sanity Checks (ลบข้อมูลผิดปกติ)
- ✅ Timezone Handling (Bangkok time)
- ✅ Feature Calculation (pct_change)

---

## 📋 Function: `clean_and_preprocess_data()`

### ขั้นตอนการทำงาน (6 Steps):

#### **Step 1: Standardization**
```python
# 1.1 Lowercase columns
'Close' → 'close'
' Open ' → 'open'

# 1.2 DatetimeIndex
df.index = pd.DatetimeIndex

# 1.3 Sort chronologically
df = df.sort_index()
```

**เหตุผล:** ชื่อ column ต้องเหมือนกันทุกที่, เรียงตาม date

---

#### **Step 2: Deduplication** ⭐ **สำคัญ!**
```python
# ลบ timestamp ซ้ำ
df = df[~df.index.duplicated(keep='last')]
```

**Logic:**
- `keep='last'` = เก็บตัวใหม่สุด
- **เหตุผล:** สมมติว่าข้อมูลที่ดึงทีหลังแม่นกว่า

**ตัวอย่าง:**
```
Before:
2024-01-01  100.0  <- เก่า
2024-01-01  101.0  <- ใหม่ (ราคาแก้ไข)

After:
2024-01-01  101.0  <- เก็บตัวนี้
```

**Use Case ในระบบเรา:**
- วัน่นี้ดึง 100 bars
- พรุ่งนี้ดึง 100 bars อีก
- มีวันซ้ำ → เก็บตัวใหม่ (ถูกต้องกว่า)

---

#### **Step 3: Sanity Checks** 🔍
```python
# 3.1 ราคา > 0
df = df[df['close'] > 0]

# 3.2 High >= Low (logic error)
df = df[df['high'] >= df['low']]

# 3.3 ลบ NaN
df = df.dropna()
```

**ตัวอย่างข้อมูลผิด:**
```
Date        Open  High  Low   Close
2024-01-01  0.0   100   99    101    <- Open = 0 ❌
2024-01-02  100   99    102   101    <- High < Low ❌
2024-01-03  100   NaN   99    101    <- NaN ❌
```

**หลังทำความสะอาด:**
```
ลบทั้ง 3 rows!
```

---

#### **Step 4: Timezone Handling** 🌏
```python
if asset_type == 'intraday':
    # แปลงเป็น Asia/Bangkok (UTC+7)
    df.index = df.index.tz_convert('Asia/Bangkok')
```

**Use Case:**
- หุ้นไทย (Daily): ไม่ต้อง timezone
- ทองคำ (Intraday 15m): ต้อง Bangkok time

**ตัวอย่าง:**
```
Before: 2024-01-01 02:00:00 (UTC)
After:  2024-01-01 09:00:00 (Asia/Bangkok)
```

---

#### **Step 5: Feature Calculation** 📊
```python
# คำนวณ % change
df['pct_change'] = df['close'].pct_change() * 100

# ลบแถวแรก (NaN)
df = df.iloc[1:]
```

**ตัวอย่าง:**
```
Date        Close  pct_change
2024-01-01  100    NaN        <- ลบ
2024-01-02  102    +2.00%     ✅
2024-01-03   99    -2.94%     ✅
```

---

#### **Step 6: Reporting** 📝
```python
✅ Cleaned: Removed 5 duplicates and 2 bad rows
   Original: 3000 → Final: 2993 (7 removed)
```

---

## 🔧 วิธีนำไปใช้กับระบบ

### **1. ใน `data_updater.py`** (Production Pipeline)

```python
from data_cleaner import clean_and_preprocess_data

def fetch_data(self, symbol, exchange, n_bars):
    # ... ดึงข้อมูล ...
    df = self.tv.get_hist(...)
    
    # 🆕 Clean ก่อนบันทึก!
    df = clean_and_preprocess_data(df, asset_type='stock')
    
    # บันทึก parquet
    df.to_parquet(file_path)
```

**ประโยชน์:**
- ✅ ข้อมูลใน parquet สะอาดเสมอ
- ✅ ไม่ต้อง clean ทุกครั้งที่วิเคราะห์

---

### **2. ใน `run_from_parquet.py`** (Analysis)

```python
from data_cleaner import validate_cleaned_data

def analyze_from_parquet(symbol, exchange):
    df = pd.read_parquet(f'data/stocks/{symbol}_{exchange}.parquet')
    
    # ตรวจสอบว่าสะอาดแล้วหรือยัง
    if not validate_cleaned_data(df):
        print("⚠️ Data needs cleaning!")
        df = clean_and_preprocess_data(df)
```

---

### **3. Incremental Update** (Merge Logic)

```python
def merge_and_deduplicate(self, old_df, new_df):
    # รวมข้อมูล
    combined = pd.concat([old_df, new_df])
    
    # 🆕 Clean (ลบซ้ำ + sanity check)
    combined = clean_and_preprocess_data(combined)
    
    return combined
```

**สถานการณ์:**
```
Old data: 2024-01-01 → 2024-12-31 (3,000 bars)
New data: 2024-12-01 → 2025-01-15 (100 bars)

Overlap: 2024-12-01 → 2024-12-31 (31 วันซ้ำ)

After clean:
- เก็บ new data (31 วัน)
- ทิ้ง old data (31 วัน)
- Total: 3,069 bars (3,000 - 31 + 100)
```

---

## 📊 ตัวอย่างการใช้งาน

### Basic:
```bash
python data_cleaner.py
```

### ใน Script:
```python
from data_cleaner import clean_and_preprocess_data

# โหลดข้อมูลดิบ
df_raw = pd.read_csv('raw_data.csv')

# Clean
df_clean = clean_and_preprocess_data(df_raw, asset_type='stock')

# ตรวจสอบ
print(f"Before: {len(df_raw)} rows")
print(f"After: {len(df_clean)} rows")
```

---

## 🎯 Integration Workflow

### **Recommended:** ใส่ใน data_updater.py

```python
# ใน data_updater.py
from data_cleaner import clean_and_preprocess_data

class StockDataUpdater:
    def fetch_data(self, symbol, exchange, n_bars):
        # ดึงข้อมูล
        df = self.tv.get_hist(...)
        
        if df is not None:
            # 🆕 Clean ทันที!
            df = clean_and_preprocess_data(
                df,
                asset_type='intraday' if self.intraday else 'stock'
            )
        
        return df
```

### ผลลัพธ์:
- ✅ ข้อมูลใน parquet สะอาดเสมอ
- ✅ ไม่มี duplicate
- ✅ ไม่มีข้อมูลผิดปกติ
- ✅ พร้อมวิเคราะห์ทันที

---

## 💡 Best Practices

### 1. **Clean ตอนดึง (Recommended)**
```python
# ใน data_updater.py
df = clean_and_preprocess_data(df)
df.to_parquet(file_path)
```

**ข้อดี:**
- Clean ครั้งเดียว
- Parquet สะอาดเสมอ

### 2. **Validate ก่อนวิเคราะห์**
```python
# ใน run_from_parquet.py
df = pd.read_parquet(file_path)

if not validate_cleaned_data(df):
    df = clean_and_preprocess_data(df)
```

**ข้อดี:**
- ตรวจสอบความถูกต้อง
- แก้ไขถ้าผิดปกติ

### 3. **Log การทำความสะอาด**
```python
# เก็บ log
with open('cleaning_log.txt', 'a') as f:
    f.write(f"{symbol}: Removed {removed} rows\n")
```

---

## 🔍 Validation

```python
from data_cleaner import validate_cleaned_data

df = pd.read_parquet('data/stocks/PTT_SET.parquet')

# ตรวจสอบ
is_clean = validate_cleaned_data(df)

# Output:
📊 Validation Results:
   ✅ DatetimeIndex
   ✅ No duplicates
   ✅ No NaN
   ✅ open > 0
   ✅ high > 0
   ✅ low > 0
   ✅ close > 0
   ✅ High >= Low
   ✅ Has pct_change
```

---

## 🎯 สรุป

### การนำไปใช้:
1. **ใส่ใน data_updater.py** - Clean ตอนดึง
2. **Validate ใน analysis** - ตรวจสอบ
3. **Use in merge** - รวมข้อมูลแบบปลอดภัย

### ประโยชน์:
- ✅ ข้อมูลสะอาดเสมอ
- ✅ ไม่มี duplicate
- ✅ ไม่มีข้อมูลผิดปกติ
- ✅ พร้อมวิเคราะห์ทันที

**Production Ready! 🚀**
