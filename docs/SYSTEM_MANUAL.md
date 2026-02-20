# 📖 PredictPlus1 — System Manual
**ระบบทำนายทิศทางราคาหุ้น N+1 Day (Fractal Pattern Detection)**  
**Version:** V7.1 — Pattern Logic Refactor (Streak-Based Scanning)  
**Last Updated:** 2026-02-19

---

## 📑 สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [ข้อกำหนดเบื้องต้น](#2-ข้อกำหนดเบื้องต้น)
3. [โครงสร้างไฟล์สำคัญ](#3-โครงสร้างไฟล์สำคัญ)
4. [คำสั่งหลัก — สรุปรวม](#4-คำสั่งหลัก)
5. [คู่มือคำสั่งแบบละเอียด](#5-คู่มือคำสั่งแบบละเอียด)
6. [ไฟล์ข้อมูลที่ระบบใช้](#6-ไฟล์ข้อมูลที่ระบบใช้)
7. [Engine Logic อธิบาย](#7-engine-logic)
8. [Core Logic — Pattern Counting (V7.1)](#8-core-logic)
9. [ลำดับการรันประจำวัน](#9-ลำดับการรันประจำวัน)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. ภาพรวมระบบ

PredictPlus1 เป็นระบบทำนายทิศทางราคาหุ้น โดยใช้ **Fractal Pattern Detection** วิเคราะห์ว่า ณ วันนี้เกิด Pattern อะไรอยู่ (เช่น ขึ้นติดกัน 3 วัน `+++`) แล้วค้นหาในประวัติว่า Pattern นั้นเคยเกิดขึ้นกี่ครั้ง → ทำนายทิศทางวันถัดไป (N+1)

### Flow หลัก:
```
ดึงข้อมูล (TvDatafeed)
    → คำนวณ Dynamic Threshold (MAX(20d SD, 252d SD, Floor))
    → ตรวจหา Active Pattern (Dynamic Lookback)
    → เลือก Best Fit Pattern จาก Master Stats
    → ทำนายทิศทาง (UP/DOWN)
    → บันทึก + ตรวจการบ้านอัตโนมัติ
```

### ตลาดที่รองรับ (6 ตลาด):
| ตลาด | Engine | Direction Logic | Floor |
|-------|--------|----------------|-------|
| 🇹🇭 Thai (SET) | Thai Logic Threshold | **Mean Reversion** | 1.0% |
| 🇺🇸 US (NASDAQ) | US Logic Threshold | **Trend Following** | 0.6% |
| 🇨🇳🇭🇰 China/HK (HKEX) | China Logic Threshold | **Mean Reversion** | 0.8% |
| 🇹🇼 Taiwan (TWSE) | Taiwan Logic Threshold | **Trend Following** | 0.9% |
| 🥇 Gold (30m/15m) | Reversion Engine | Mean Reversion | 0.3% |
| 🥈 Silver (30m/15m) | Reversion Engine | Mean Reversion | 0.3% |

---

## 2. ข้อกำหนดเบื้องต้น

### Python & Dependencies
```bash
python >= 3.10
pip install tvdatafeed pandas numpy python-dotenv requests
```

### Environment Variables (`.env`)
```ini
TV_USERNAME=your_tradingview_username
TV_PASSWORD=your_tradingview_password
TV_SESSIONID=your_session_id          # optional
```

---

## 3. โครงสร้างไฟล์สำคัญ

```
PredictPlus1/
├── main.py                          # 🔮 ตัวหลัก: ทำนาย + ตรวจการบ้าน + สร้างรายงาน
├── config.py                        # ⚙️  ตั้งค่าทุก asset group + engine + threshold
├── processor.py                     # 🧩 Router: เลือก engine ตาม config
├── core/
│   ├── engines/
│   │   ├── base_engine.py           # 🏗️  Base class + calculate_dynamic_threshold()
│   │   ├── thai_logic_threshold_only.py    # 🇹🇭 Thai engine
│   │   ├── us_logic_threshold_only.py      # 🇺🇸 US engine
│   │   ├── china_logic_threshold_only.py   # 🇨🇳 China engine
│   │   ├── hongkong_logic_threshold_only.py # 🇭🇰 HK engine
│   │   ├── taiwan_logic_threshold_only.py  # 🇹🇼 Taiwan engine
│   │   ├── reversion_engine.py      # Mean Reversion (Gold/Silver)
│   │   └── trend_engine.py          # Trend Following (legacy)
│   ├── performance.py               # 📊 บันทึก + verify forecasts
│   ├── pattern_stats.py             # 📈 จัดการ Master Stats
│   └── data_cache.py               # 💾 Smart caching ข้อมูล
├── scripts/
│   ├── generate_master_stats.py     # 🔧 สร้าง Master Pattern Stats
│   ├── backfill_forward_testing.py  # 🔄 Backfill forward testing ย้อนหลัง
│   ├── check_forward_testing.py     # ✅ ตรวจการบ้าน (pending/verified)
│   ├── forward_testing_report.py    # 📊 รายงาน forward testing แบบละเอียด
│   ├── calculate_performance.py     # 📈 สรุป performance (trade history)
│   └── daily_forecast_dashboard.py  # 📺 Dashboard executive summary
├── data/
│   ├── Master_Pattern_Stats_NewLogic.csv   # 📊 Pattern database (count only)
│   ├── forecast_tomorrow.csv               # 🔮 Predictions ล่าสุด
│   ├── daily_forecast_summary_*.csv        # 📋 Summary รายวัน
│   └── cache/                              # 💾 Cached price data
├── logs/
│   ├── performance_log.csv                 # 📋 Forward testing log (main file)
│   ├── trade_history_*.csv                 # 📈 Trade history per market
│   └── performance_log_backup_*.csv        # 💿 Backups
└── docs/
    ├── SYSTEM_MANUAL.md                    # 📖 คู่มือนี้
    └── ENGINE_MIGRATION_V7.md              # 📋 Change log
```

---

## 4. คำสั่งหลัก

### Quick Reference (สรุปคำสั่งทั้งหมด)

```bash
# ═══════════════════════════════════════════════
# 🔮 ทำนาย N+1 (คำสั่งหลักที่ใช้ทุกวัน)
# ═══════════════════════════════════════════════
python main.py

# ═══════════════════════════════════════════════
# 📊 ดูผล Forward Testing & Performance
# ═══════════════════════════════════════════════
python scripts/check_forward_testing.py          # ตรวจการบ้าน
python scripts/check_forward_testing.py --verify  # ตรวจ + verify pending
python scripts/forward_testing_report.py          # รายงานละเอียด
python scripts/forward_testing_report.py --verify  # รายงาน + verify ก่อน
python scripts/calculate_performance.py           # สรุป Win Rate
python scripts/daily_forecast_dashboard.py        # Dashboard executive

# ═══════════════════════════════════════════════
# 🔧 คำสั่ง Maintenance (ไม่ต้องรันทุกวัน)
# ═══════════════════════════════════════════════
python scripts/generate_master_stats.py           # สร้าง Master Stats ใหม่
python scripts/backfill_forward_testing.py        # Backfill ข้อมูลย้อนหลัง
```

---

## 5. คู่มือคำสั่งแบบละเอียด

### 5.1 🔮 `python main.py` — ทำนาย N+1 + ตรวจการบ้าน

**หน้าที่:** คำสั่งหลักที่ใช้ทุกวัน ทำทุกอย่างในรันเดียว

**สิ่งที่ทำ:**
1. ดึงข้อมูลหุ้นทุกตัวจาก TradingView (ใช้ cache ถ้ามี)
2. คำนวณ Dynamic Threshold สำหรับทุก stock
3. ตรวจหา Active Pattern ปัจจุบัน
4. ทำนายทิศทาง N+1 day (UP/DOWN)
5. **ตรวจการบ้าน:** verify forecasts เก่าที่ PENDING อัตโนมัติ
6. บันทึก forecasts ใหม่ลง `logs/performance_log.csv`
7. สร้าง `data/forecast_tomorrow.csv` (overwrite ทุกรัน)
8. สร้าง `data/daily_forecast_summary_YYYY-MM-DD.csv`

**Output ที่ถูก update:**
| ไฟล์ | การเปลี่ยนแปลง |
|------|----------------|
| `logs/performance_log.csv` | Append forecasts ใหม่ + verify เก่า |
| `data/forecast_tomorrow.csv` | **Overwrite** ทุกรัน |
| `data/daily_forecast_summary_*.csv` | สร้างใหม่ถ้ายังไม่มีวันนี้ |

**ใช้เมื่อ:** รันทุกวัน (ก่อนตลาดเปิดหรือหลังตลาดปิด)

```bash
python main.py
```

---

### 5.2 ✅ `python scripts/check_forward_testing.py` — ตรวจการบ้าน

**หน้าที่:** ดู forecasts ทั้งหมดในระบบ — ทั้ง PENDING และ Verified

**สิ่งที่แสดง:**
- จำนวน forecasts ทั้งหมดใน log
- **PENDING:** forecasts ที่ยังไม่ได้ verify (แยก Ready vs Waiting)
- **Verified:** ผลที่ตรวจแล้ว (ถูก/ผิด)
- สรุป accuracy แยกตาม symbol และ pattern

**ไฟล์ที่อ่าน:** `logs/performance_log.csv`

**Options:**
```bash
# แบบปกติ (ดูอย่างเดียว)
python scripts/check_forward_testing.py

# Verify pending forecasts ก่อนแสดง (ดึงข้อมูลจริงจาก TV)
python scripts/check_forward_testing.py --verify

# กำหนดช่วงเวลา (default: 30 วัน)
python scripts/check_forward_testing.py --days 60

# แสดงทุก verified (ไม่ใช่แค่ 10 ล่าสุด)
python scripts/check_forward_testing.py --all
```

---

### 5.3 📊 `python scripts/forward_testing_report.py` — รายงานละเอียด

**หน้าที่:** สร้างรายงาน Forward Testing แบบ Human-friendly

**สิ่งที่แสดง:**
- Summary: Total / Verified / Pending / Accuracy
- **By Exchange:** accuracy แยกตามตลาด
- **By Forecast Direction:** accuracy แยก UP/DOWN
- **Top 10 Move%:** หุ้นที่ขึ้น/ลงมากสุด

**ไฟล์ที่อ่าน:** `logs/performance_log.csv`

**Options:**
```bash
# แบบปกติ
python scripts/forward_testing_report.py

# Verify pending ก่อนรายงาน
python scripts/forward_testing_report.py --verify

# กำหนดช่วงเวลา
python scripts/forward_testing_report.py --days 60

# Export เป็น CSV
python scripts/forward_testing_report.py --export data/forward_report.csv

# รวมทุก option
python scripts/forward_testing_report.py --verify --days 60 --export data/report.csv
```

---

### 5.4 📈 `python scripts/calculate_performance.py` — สรุป Performance

**หน้าที่:** คำนวณ Win Rate, Profit Factor จาก trade history

**สิ่งที่แสดง:**
- **Level A — Market Summary:** Profit/Loss, Avg, Win Rate
- **Level B — Per-Stock Precision:** W/L, Win Rate, RRR per stock

**ไฟล์ที่อ่าน:** `data/logs/*/` (trade history CSVs per market)  
**ไฟล์ที่อ่าน (fallback):** `logs/trade_history_*.csv`

```bash
python scripts/calculate_performance.py
```

**Output ที่สร้าง:**
- `data/stock_stats_*.csv` — Stats per stock per market
- `data/performance_summary_*.csv` — Summary per market

---

### 5.5 📺 `python scripts/daily_forecast_dashboard.py` — Dashboard

**หน้าที่:** Executive Dashboard แสดงภาพรวมทั้งระบบ

**สิ่งที่แสดง:**
- Tomorrow's Forecasts: หุ้นที่ทำนายว่าจะขึ้น/ลง
- Accuracy Report: Win Rate แยกตาม symbol
- Summary: จำนวน signals, avg probability

**ไฟล์ที่อ่าน:** `logs/performance_log.csv`

```bash
python scripts/daily_forecast_dashboard.py
```

---

### 5.6 🔧 `python scripts/generate_master_stats.py` — สร้าง Master Stats

**หน้าที่:** Scan ทุก stock 5000 bars → สร้าง pattern database ใหม่ทั้งหมด

**สิ่งที่ทำ:**
1. ดึง 5000 bars ต่อ stock จาก TradingView
2. คำนวณ Dynamic Threshold
3. Enumerate ทุก pattern (1-7 chars) ที่เกิดจริง
4. นับจำนวนครั้ง (Count)
5. Track Max Streak (Positive/Negative)

**ไฟล์ที่สร้าง:** `data/Master_Pattern_Stats_NewLogic.csv`

**Columns:** `Symbol, Market, Threshold, Max_Streak_Pos, Max_Streak_Neg, Pattern, Pattern_Name, Category, Length, Count, Bars`

> ⚠️ **ใช้เวลานาน** (~20-30 นาที สำหรับ 242 stocks)  
> ⚠️ **ไม่ต้องรันทุกวัน** — รันเมื่อมีการเปลี่ยน engine logic หรืออยากอัปเดต stats

```bash
python scripts/generate_master_stats.py
```

---

### 5.7 🔄 `python scripts/backfill_forward_testing.py` — Backfill ย้อนหลัง

**หน้าที่:** จำลอง forward testing ย้อนหลังจากวันที่กำหนด

**สิ่งที่ทำ:**
1. โหลด `Master_Pattern_Stats_NewLogic.csv` เป็น pattern lookup
2. ดึง ~500 bars ต่อ stock (เฉพาะเพียงพอสำหรับ threshold)
3. สำหรับแต่ละ trading day:
   - Dynamic Lookback → Active Pattern
   - Best Fit Selection จาก Master Stats
   - Verify actual N+1 result
4. เขียนลง `logs/performance_log.csv`

**ไฟล์ที่สร้าง/อัปเดต:** `logs/performance_log.csv`

**Anti-Overlapping:** 1 result ต่อ stock ต่อวัน (count สูงสุด)

```bash
# Backfill ตั้งแต่ Feb 12 → yesterday
python scripts/backfill_forward_testing.py --start-date 2026-02-12

# ระบุ end date
python scripts/backfill_forward_testing.py --start-date 2026-02-12 --end-date 2026-02-18
```

---

## 6. ไฟล์ข้อมูลที่ระบบใช้

### 6.1 Input Files (ระบบอ่าน)

| ไฟล์ | อ่านโดย | คำอธิบาย |
|------|---------|---------|
| `data/Master_Pattern_Stats_NewLogic.csv` | backfill, engines | Pattern database (count only) |
| `data/cache/*.csv` | main.py, scripts | Cached price data |
| `.env` | main.py, scripts | TradingView credentials |

### 6.2 Output Files (ระบบเขียน)

| ไฟล์ | เขียนโดย | Mode | คำอธิบาย |
|------|---------|------|---------|
| `logs/performance_log.csv` | main.py, backfill | Append | **Forward testing log หลัก** |
| `data/forecast_tomorrow.csv` | main.py | Overwrite | Predictions ล่าสุด |
| `data/daily_forecast_summary_*.csv` | main.py | Create | Summary รายวัน |
| `data/Master_Pattern_Stats_NewLogic.csv` | generate_master_stats | Overwrite | Pattern database |

### 6.3 ใครอ่านอะไร (Dependency Map)

```
logs/performance_log.csv ← ไฟล์ศูนย์กลางของ Forward Testing
    ├── อ่านโดย: check_forward_testing.py
    ├── อ่านโดย: forward_testing_report.py
    ├── อ่านโดย: daily_forecast_dashboard.py
    ├── เขียนโดย: main.py (append + verify)
    └── เขียนโดย: backfill_forward_testing.py (append)

data/Master_Pattern_Stats_NewLogic.csv ← Pattern Database
    ├── อ่านโดย: backfill_forward_testing.py
    └── เขียนโดย: generate_master_stats.py

logs/trade_history_*.csv ← Trade History (legacy)
    ├── อ่านโดย: calculate_performance.py
    └── เขียนโดย: main.py (via performance module)
```

---

## 7. Engine Logic

### 7.1 Dynamic Threshold
```python
threshold = MAX(
    pct_change.rolling(20).std(),    # Short-term: 20-day SD
    pct_change.rolling(252).std(),   # Long-term: 252-day SD (≈1 year)
    market_floor                      # Absolute minimum (e.g. 0.01 for Thai)
)
```

### 7.2 Signal Generation
```
วันนี้ return > +threshold  →  signal = '+'
วันนี้ return < -threshold  →  signal = '-'
อื่นๆ (|return| ≤ threshold) →  signal = '.' (neutral, ไม่นับ)
```

### 7.3 Active Pattern (Dynamic Lookback)
- Scan ย้อนหลังจากวันล่าสุด
- สร้าง pattern จาก signals ที่ไม่ใช่ neutral ติดต่อกัน
- หยุดเมื่อเจอ neutral day
- ความยาวสูงสุด 7 characters
- ตัวอย่าง: `++-` = ขึ้น 2 วัน แล้วลง 1 วัน

### 7.4 Direction Logic

| Logic | Pattern จบด้วย `+` | Pattern จบด้วย `-` |
|-------|-------------------|-------------------|
| **Mean Reversion** (TH, CN, HK, Gold, Silver) | ทำนาย **DOWN** ↓ | ทำนาย **UP** ↑ |
| **Trend Following** (US, TW) | ทำนาย **UP** ↑ | ทำนาย **DOWN** ↓ |

### 7.5 Rule 4: NEUTRAL = LOSS
- ถ้าวัน N+1 จริงๆ ราคาเปลี่ยนแปลงไม่เกิน threshold → ถือว่า **NEUTRAL**
- NEUTRAL นับเป็น **LOSS** (ไม่ถูก ไม่ผิด → ให้เป็นผิด)

---

## 8. Core Logic — Pattern Counting (V7.1)

### 8.1 Core Logic 1: Pattern String Accumulation

**กฎ:** Mixed signs (`+/-`) **อนุญาต**ใน streak เดียวกัน — หยุดเฉพาะเมื่อเจอ **Neutral day** (`|return| < threshold`)

```
raw returns:  +2.1%  -1.5%  +0.3%  -2.0%  +1.8%
threshold:    ±1.0%  ±1.0%  ±1.0%  ±1.0%  ±1.0%
signals:       +      -      .      -      +
                            ↑ neutral = BREAK

streak 1: "+-"   (วัน 1-2)
streak 2: "-+"   (วัน 4-5)
```

> ⚠️ **ก่อน V7.1:** ระบบข้าม neutral day แล้วต่อ pattern ข้ามไป เช่น `+-.+` → `"+-+"` (**ผิด!**)  
> ✅ **V7.1:** neutral day ตัด streak ทันที → `"+-"` + `"-+"` (**ถูกต้อง**)

### 8.2 Mode A: Historical Stats (Overlapping Sliding Window)

**ใช้ใน:** `get_pattern_stats()`, `generate_master_stats.py`  
**วิธีนับ:** Streak-based scanning

```
1. Build signal series ทั้ง 5000 bars:  [+, -, ., +, +, -, ., ...]
2. หา streaks (ช่วงที่ไม่มี '.'):       [+, -]   [+, +, -]   ...
3. Enumerate sub-patterns แต่ละ streak:
   streak "++-" → sub-patterns: "+", "+", "-", "++", "+-", "++-"
4. ถ้า sub-pattern ตรงกับ target → บันทึก N+1 future return
```

**ทำไมถึงใช้ overlapping?**  
เพราะ streak `"++-"` มี `"+"` 2 ตัวอยู่ข้างใน → ทั้ง 2 ตัวต้องนับเป็น occurrence ที่แยกกัน (ตำแหน่งต่างกัน = N+1 return ต่างกัน)

### 8.3 Mode B: Forward Testing (Non-Overlapping Events)

**ใช้ใน:** `main.py` (predict), `backfill_forward_testing.py`  
**วิธีนับ:** 1 prediction ต่อ stock ต่อวัน (Anti-Overlapping)

```
วันนี้ STOCK_A มี pattern "++-":
  - ลอง "++-" → count=45, prob=63%  ✅ ผ่าน (count ≥ 30)
  - ลอง "+-"  → count=120, prob=58% ✅ ผ่าน
  - ลอง "-"   → count=300, prob=55% ✅ ผ่าน
  → เลือก "++-" (prob สูงสุด 63%) → ทำนาย 1 ครั้ง
```

### 8.4 ไฟล์ที่ใช้ Logic ใหม่ (V7.1)

| ไฟล์ | ใช้ Logic | หมายเหตุ |
|------|----------|----------|
| `base_engine.py` | Mode A (streak-based) | `extract_pattern()`, `get_pattern_stats()`, `select_best_fit()` |
| `trend_engine.py` | Mode A + Regime Filter | Override `get_pattern_stats()` พร้อม BULL/BEAR filter |
| `pattern_matcher_basic.py` | Mode A (streak-based) | `extract_pattern()`, `find_pattern_matches()`, `get_best_pattern()` |
| `backtest_with_trailing_stop.py` | Mode A (streak-based) | Pattern stats building + sub-pattern matching |
| *5 engines + reversion_engine* | Inherit จาก base | **ไม่ต้องแก้** — ได้ fix อัตโนมัติผ่าน inheritance |

---

## 9. ลำดับการรันประจำวัน

### 🌅 Daily Routine (Run Order — **ทุกวัน**)

| ลำดับ | คำสั่ง | หน้าที่ | เวลา |
|:-----:|--------|---------|------|
| **1** | `python main.py` | ทำนาย N+1 + ตรวจการบ้านวันก่อน + บันทึก log | ~5 วินาที |
| **2** | `python scripts/check_forward_testing.py` | ดูสรุป pending/verified/accuracy | ~1 วินาที |
| **3** | `python scripts/forward_testing_report.py` | รายงาน Forward Testing แบบละเอียด | ~1 วินาที |
| **4** | `python scripts/calculate_performance.py` | สรุป Performance (Win Rate, RRR) | ~1 วินาที |
| **5** | `python scripts/daily_forecast_dashboard.py` | Dashboard ภาพรวม | ~1 วินาที |

```bash
# ═══════════════════════════════════════════════════════════════
# 🌅 DAILY ROUTINE — รันทุกวันหลังตลาดปิด (ตามลำดับ)
# ═══════════════════════════════════════════════════════════════

# STEP 1: ทำนาย + ตรวจการบ้าน (CORE — ต้องรันก่อนเสมอ)
python main.py
#   ✅ ดึงข้อมูลหุ้น → ทำนาย N+1 → บันทึก forecast_tomorrow.csv
#   ✅ Verify forecasts เก่า → อัปเดต performance_log.csv
#   ✅ สร้าง daily_forecast_summary_YYYY-MM-DD.csv

# STEP 2: ดูผล Forward Testing (อ่านจาก performance_log.csv)
python scripts/check_forward_testing.py
#   📊 แสดง PENDING, VERIFIED, Accuracy by Symbol/Pattern

# STEP 3: รายงาน Forward Testing แบบละเอียด (by exchange, by direction)
python scripts/forward_testing_report.py
#   📋 แสดง Accuracy แยกตามตลาด, แยก UP/DOWN, Top 10 Move%

# STEP 4: สรุป Performance (Win Rate, RRR per stock)
python scripts/calculate_performance.py
#   📈 แสดง Market Summary + Per-Stock Precision

# STEP 5: ดู Dashboard ภาพรวม (อ่านจาก performance_log.csv)
python scripts/daily_forecast_dashboard.py
#   📺 แสดง Tomorrow's Forecasts, Accuracy Report, Summary
```

### 🔧 Maintenance (Run Order — **ไม่ต้องรันทุกวัน**)

| ลำดับ | คำสั่ง | เมื่อไหร่ | เวลา |
|:-----:|--------|-----------|------|
| **M1** | `python scripts/generate_master_stats.py` | หลังเปลี่ยน engine logic | ~20-30 นาที |
| **M2** | `python scripts/backfill_forward_testing.py --start-date YYYY-MM-DD` | หลัง reset log หรือต้องการ backfill | ~5-10 นาที |
| **M3** | `python main.py` | หลัง maintenance ทุกครั้ง | ~5 วินาที |

```bash
# ═══════════════════════════════════════════════════════════════
# 🔧 MAINTENANCE — รันเมื่อจำเป็นเท่านั้น
# ═══════════════════════════════════════════════════════════════

# M1: สร้าง Master Stats ใหม่ (หลังเปลี่ยน engine logic)
python scripts/generate_master_stats.py
#   ⚠️ ใช้เวลา ~20-30 นาที สำหรับ 242 stocks

# M2: Backfill ข้อมูลย้อนหลัง (หลัง reset log)
python scripts/backfill_forward_testing.py --start-date 2026-02-12

# M3: รัน prediction ใหม่
python main.py
```

### 🆕 First Time Setup (ตั้งค่าครั้งแรก)
```bash
# 1. ตั้งค่า .env
echo TV_USERNAME=xxx > .env
echo TV_PASSWORD=xxx >> .env

# 2. สร้าง Master Stats (ใช้เวลา ~20 นาที)
python scripts/generate_master_stats.py

# 3. (Optional) Backfill forward testing
python scripts/backfill_forward_testing.py --start-date 2026-02-12

# 4. รัน prediction แรก
python main.py
```

---

## 10. Troubleshooting

### ❌ `FileNotFoundError: performance_log.csv`
**แก้:** รัน `python main.py` ก่อน — จะสร้างไฟล์ให้อัตโนมัติ

### ❌ `tvDatafeed connection error`
**แก้:** ตรวจ `.env` ว่ามี TV_USERNAME / TV_PASSWORD ถูกต้อง

### ❌ `No patterns found for [STOCK]`
**แก้:** Stock อาจมีข้อมูลน้อยเกินไป (<300 bars) หรือ volatility ต่ำเกินไป

### ❌ `Master stats not found`
**แก้:** รัน `python scripts/generate_master_stats.py` ก่อน

### ⚠️ ข้อมูลเก่าผิดปกติหลัง engine migration
**แก้:** Backup → ลบ log เก่า → Backfill ใหม่
```bash
# Backup
copy logs\performance_log.csv logs\performance_log_backup.csv

# ลบ
del logs\performance_log.csv

# Backfill
python scripts/backfill_forward_testing.py --start-date 2026-02-12

# รัน prediction ใหม่
python main.py
```
