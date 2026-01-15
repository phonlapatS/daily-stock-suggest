# Quick Guide: Incremental Download

## 🎯 Usage

### **Default: Skip Existing (แนะนำ)**
```bash
python pipeline/data_updater.py
```
หรือ
```bash
python pipeline/data_updater.py --skip
```

**ผลลัพธ์:**
```
⚙️ Mode: Incremental (Skip Existing)
📦 Found 51 existing files
⬇️ Downloading 8 missing stocks...
```

---

### **Full Update: Update All**
```bash
python pipeline/data_updater.py --full
```

**ผลลัพธ์:**
```
⚙️ Mode: Full Update (All Stocks)
📊 Target Stocks: 59
```

---

## 📊 Logic Explained

### **Step 1: Scan Existing**
```python
existing_files = list(data_dir.glob("*.parquet"))
existing_symbols = {file.stem.split('_')[0] for file in existing_files}

# Example:
# PTT_SET.parquet -> 'PTT'
# DELTA_SET.parquet -> 'DELTA'
```

### **Step 2: Filter Missing**
```python
missing_stocks = [
    stock for stock in stock_list 
    if stock['symbol'] not in existing_symbols
]
```

### **Step 3: Download Only Missing**
```python
# Only loop through missing stocks
for stock in missing_stocks:
    download(stock)
```

---

## ⚡ Performance Comparison

### **Before (Full Update):**
```
📊 Stocks to update: 59
⏱️ Time: ~150 seconds
```

### **After (Incremental):**
```
📦 Found 51 existing files
⬇️ Downloading 8 missing stocks...
⏱️ Time: ~20 seconds (7.5x faster!)
```

---

## 💡 Use Cases

### **Use Case 1: เพิ่มหุ้นใหม่**
```python
# Add new stocks to STOCK_LIST
STOCK_LIST.append({'symbol': 'NEWSTOCK', 'exchange': 'SET'})

# Run incremental
python pipeline/data_updater.py --skip
# -> จะดึงแค่ NEWSTOCK
```

### **Use Case 2: Re-download ทุกอย่าง**
```bash
python pipeline/data_updater.py --full
# -> จะ update ทุกหุ้น (ทั้งเก่าและใหม่)
```

### **Use Case 3: เพิ่มหุ้นเยอะๆ**
```python
# เพิ่ม 100 หุ้นใหม่ใน STOCK_LIST

# Run incremental
python pipeline/data_updater.py --skip
# Found 51 existing files
# Downloading 100 missing stocks...
# ใช้เวลา ~4 นาที (แทนที่จะ ~6 นาที)
```

---

## ✅ Benefits

1. **ประหยัดเวลา** - Skip หุ้นที่มีแล้ว
2. **ประหยัด API calls** - ไม่ซ้ำซ้อน
3. **Flexible** - เลือกได้ว่าจะ skip หรือ update ทั้งหมด
4. **Safe** - ไม่ลบไฟล์เก่า

---

## 🚀 Recommended Workflow

```bash
# สัปดาห์แรก - Download ทั้งหมด
python pipeline/data_updater.py --full

# จากนั้น - เพิ่มหุ้นใหม่ตามต้องการ
# แก้ STOCK_LIST ใน data_updater.py

# Run incremental (จะดึงแค่ตัวใหม่)
python pipeline/data_updater.py --skip

# ถ้าต้องการอัพเดททั้งหมด (ทุกเดือน)
python pipeline/data_updater.py --full
```

**Everything is ready! 🎉**
