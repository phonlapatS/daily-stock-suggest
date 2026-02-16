# คำสั่งรันการทดสอบ China Market

## 🚀 คำสั่งหลัก

### 1. รันการทดสอบ Realistic Settings
```bash
python scripts/test_china_realistic_settings.py
```

**ทดสอบ:**
- TP: 3.5%, 4.0%, 4.5%
- Max Hold: 5, 6, 7 days
- SL: 1.0%, 1.2%
- Total: 18 combinations

---

### 2. ลบไฟล์เก่าก่อนรัน (ถ้าจำเป็น)
```bash
python scripts/fix_test_china.py
```

หรือลบด้วยตนเอง:
```bash
# Windows PowerShell
Remove-Item "data/full_backtest_results.csv" -ErrorAction SilentlyContinue
Remove-Item "logs/trade_history_CHINA.csv" -ErrorAction SilentlyContinue
Remove-Item "data/china_realistic_settings_results.csv" -ErrorAction SilentlyContinue
```

---

### 3. ตรวจสอบสถานะการทดสอบ
```bash
python scripts/check_test_status.py
```

---

### 4. รอและแจ้งเมื่อเสร็จ
```bash
python scripts/notify_when_done.py
```

---

## 📊 คำสั่งอื่นๆ ที่เกี่ยวข้อง

### รัน Backtest สำหรับ China (ครั้งเดียว)
```bash
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --take_profit 4.0 --max_hold 6 --stop_loss 1.2
```

### คำนวณ Metrics
```bash
python scripts/calculate_metrics.py
```

### ดูผลลัพธ์
```bash
python scripts/show_china_results_table.py
```

### วิเคราะห์ TP Reality
```bash
python scripts/analyze_china_tp_reality.py
```

### วิเคราะห์ Hold Period
```bash
python scripts/analyze_hold_period_reality.py
```

---

## 🔍 ตรวจสอบผลลัพธ์

### ดูไฟล์ผลลัพธ์
```bash
# Windows PowerShell
Get-Content "data/china_realistic_settings_results.csv" | Select-Object -First 20
```

### ดูด้วย Python
```python
import pandas as pd
df = pd.read_csv('data/china_realistic_settings_results.csv')
print(df.sort_values('score', ascending=False).head(10))
```

---

## ⚡ Quick Start

### Step 1: ลบไฟล์เก่า (ถ้าจำเป็น)
```bash
python scripts/fix_test_china.py
```

### Step 2: รันการทดสอบ
```bash
python scripts/test_china_realistic_settings.py
```

### Step 3: ตรวจสอบสถานะ (ในอีก terminal)
```bash
python scripts/check_test_status.py
```

---

## 📝 หมายเหตุ

- การทดสอบใช้เวลา **30-60 นาที** สำหรับ 18 combinations
- ตรวจสอบสถานะได้ด้วย `check_test_status.py`
- ผลลัพธ์จะถูกบันทึกที่ `data/china_realistic_settings_results.csv`

---

**Last Updated:** 2026-02-13

