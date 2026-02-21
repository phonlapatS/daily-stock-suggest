# ⚡ Quick Reference - คำสั่งที่ใช้บ่อย

**Last Updated:** 2026-02-22  
**Version:** V4.4

---

## 🎯 คำสั่งที่ใช้บ่อยที่สุด

### 1. รัน Backtest
```bash
# Taiwan
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# US
python scripts/backtest.py --full --bars 2500 --group US

# Thai
python scripts/backtest.py --full --bars 2500 --group THAI

# China
python scripts/backtest.py --full --bars 2500 --group CHINA
```

### 2. คำนวณ Metrics
```bash
python scripts/calculate_metrics.py
```

### 3. ดูรายงานประจำวัน
```bash
python main.py
```

### 4. สร้างกราฟ
```bash
python scripts/plot_equity.py
python scripts/plot_markets_from_metrics.py
```

---

## 📊 Workflow แบบเร็ว

### Daily Workflow
```bash
# 1. Backtest
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# 2. Metrics
python scripts/calculate_metrics.py

# 3. Report
python main.py
```

### Full Update
```bash
# Clean
rm logs/trade_history_*.csv

# Backtest all
python scripts/backtest.py --full --bars 2500 --group TAIWAN
python scripts/backtest.py --full --bars 2500 --group US
python scripts/backtest.py --full --bars 2500 --group THAI
python scripts/backtest.py --full --bars 2500 --group CHINA

# Metrics
python scripts/calculate_metrics.py
```

---

## 🔧 Parameters ที่สำคัญ

| Parameter | Values | Description |
|-----------|--------|-------------|
| `--bars` | 2000, 2500, 3000 | จำนวน historical bars |
| `--group` | TAIWAN, US, THAI, CHINA | ตลาดที่ต้องการ |
| `--full` | - | รันทุกหุ้น |
| `--fast` | - | ข้าม validation (เร็วขึ้น) |

---

## 📁 ไฟล์ Output ที่สำคัญ

| File | Description |
|------|-------------|
| `logs/trade_history_TAIWAN.csv` | Trade history ตลาดไต้หวัน |
| `data/symbol_performance.csv` | Performance metrics ทั้งหมด |
| `data/full_backtest_results.csv` | Backtest results |
| `plots/equity_curve.png` | กราฟ equity curve |

---

## ⚠️ หมายเหตุ

- ต้องรัน `backtest.py` ก่อน `calculate_metrics.py`
- ถ้าต้องการผลลัพธ์ใหม่ → ลบ `logs/trade_history_*.csv` ก่อน
- ใช้ `--bars 2500` สำหรับการทดสอบ (สมดุลระหว่างความเร็วและข้อมูล)

---

**ดูรายละเอียดเพิ่มเติม:** `docs/USER_MANUAL.md`

