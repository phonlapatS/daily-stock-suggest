# Market Scanner - CSV Archive System

## 📦 ระบบบันทึก CSV

### 2 ไฟล์:

#### 1. **Latest** (ล่าสุด)
```
results/market_scanner.csv
```
- เขียนทับทุกครั้ง
- ใช้สำหรับดูผลล่าสุด

#### 2. **Archive** (สำรอง)
```
results/scanner_history/scanner_YYYYMMDD_HHMMSS.csv
```
- บันทึกพร้อม timestamp
- เก็บประวัติทุกครั้งที่รัน

---

## 🗂️ ตัวอย่าง

```
results/
├── market_scanner.csv                           # ล่าสุด
└── scanner_history/
    ├── scanner_20260115_080000.csv             # เช้า
    ├── scanner_20260115_120000.csv             # เที่ยง
    └── scanner_20260115_180000.csv             # เย็น
```

---

## 📊 การใช้งาน

### รันทุกวัน:
```bash
# เช้า 8:00
python scripts/scanner.py  
# -> สร้าง scanner_20260115_080000.csv

# เที่ยง 12:00
python scripts/scanner.py
# -> สร้าง scanner_20260115_120000.csv
```

### ดูประวัติ:
```bash
ls -lh results/scanner_history/
```

### เปรียบเทียบ:
```python
import pandas as pd

morning = pd.read_csv('results/scanner_history/scanner_20260115_080000.csv')
evening = pd.read_csv('results/scanner_history/scanner_20260115_180000.csv')

# เปรียบเทียบราคา
merged = morning.merge(evening, on='Symbol', suffixes=('_morning', '_evening'))
merged['Price_Diff'] = merged['Price_evening'] - merged['Price_morning']
```

---

## ⏰ Automated (Cron)

```bash
# รันทุก 4 ชั่วโมง
0 */4 * * * cd /path/to/predict && python scripts/scanner.py >> logs/scanner.log 2>&1
```

**ผลลัพธ์:**
- เช้า 8 AM: scanner_20260115_080000.csv
- เที่ยง 12 PM: scanner_20260115_120000.csv
- บ่าย 4 PM: scanner_20260115_160000.csv
- เย็น 8 PM: scanner_20260115_200000.csv

---

## 🧹 การจัดการ Archive

### ลบไฟล์เก่า (เก็บแค่ 30 วัน):
```bash
find results/scanner_history -name "scanner_*.csv" -mtime +30 -delete
```

### นับจำนวน:
```bash
ls results/scanner_history/scanner_*.csv | wc -l
```

---

## ✅ ประโยชน์

1. **Track Changes** - เห็นการเปลี่ยนแปลงของตลาด
2. **Backtest** - ทดสอบกลับว่า signal แม่นไหม
3. **Report** - สร้าง daily/weekly report
4. **Analysis** - วิเคราะห์ pattern ข้ามเวลา

**ข้อมูลไม่หายแล้ว! 📦✅**
