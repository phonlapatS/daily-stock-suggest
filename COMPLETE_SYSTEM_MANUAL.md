# 📚 คู่มือระบบ PredictPlus1 ฉบับสมบูรณ์ (V14.3)

**Last Updated:** 2026-01-XX  
**Version:** V14.3  
**Status:** Production-Ready

---

## 📑 สารบัญ

1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [Flow การทำงาน](#flow-การทำงาน)
3. [คำสั่งทั้งหมด (Complete Command Reference)](#คำสั่งทั้งหมด-complete-command-reference)
4. [Risk Management Parameters](#risk-management-parameters)
5. [การใช้งานแต่ละส่วน](#การใช้งานแต่ละส่วน)
6. [Troubleshooting](#troubleshooting)
7. [Configuration Files](#configuration-files)

---

## 🎯 ภาพรวมระบบ

### ระบบคืออะไร?
**PredictPlus1** เป็นระบบทำนายทิศทางหุ้น (N+1 Prediction) ที่ใช้:
- **Pattern Matching** (3-8 วัน) + **Historical Statistics** (Prob%, RRR, Count)
- **Risk Management** (ATR-based SL/TP, Trailing Stop, Max Hold)
- **Forward Testing** (ทำนายและตรวจสอบผลจริง)

### สิ่งที่ระบบทำได้
1. ✅ **ทำนายทิศทางหุ้น** (UP/DOWN) สำหรับวันถัดไป
2. ✅ **แสดงหุ้นที่ผ่านเกณฑ์** (Prob%, RRR, Count) แยกตามประเทศ
3. ✅ **Backtest** ประวัติศาสตร์เพื่อประเมินประสิทธิภาพ
4. ✅ **Forward Testing** ทำนายและตรวจสอบผลจริง
5. ✅ **Equity Curve** แสดงผลการเทรดแบบ cumulative

### ตลาดที่รองรับ
- 🇹🇭 **THAI (SET):** 118 หุ้น
- 🇺🇸 **US (NASDAQ/NYSE):** 98 หุ้น
- 🇨🇳 **CHINA/HK (HKEX):** 13 หุ้น
- 🇹🇼 **TAIWAN (TWSE):** 10 หุ้น
- ⚡ **METALS (Gold/Silver):** 2 สินค้า (15min/30min intraday)

**รวม:** 255+ หุ้น

---

## 🔄 Flow การทำงาน

### 1. Main System Flow (main.py)

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN SYSTEM FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. เริ่มต้น (Initialization)
   ├─ โหลด config.py (Asset Groups, Settings)
   ├─ เชื่อมต่อ TradingView API
   └─ โหลด Cache (ถ้ามี)

2. สำหรับแต่ละ Asset Group:
   ├─ GROUP_A_THAI (118 หุ้น)
   ├─ GROUP_B_US (98 หุ้น)
   ├─ GROUP_C_CHINA_HK (13 หุ้น)
   ├─ GROUP_D_TAIWAN (10 หุ้น)
   └─ GROUP_E_METALS (2 สินค้า)

3. สำหรับแต่ละหุ้น:
   ├─ Fetch Data (TradingView API)
   │  ├─ ใช้ Cache ถ้ามี (Delta Fetch)
   │  └─ Fetch ใหม่ถ้าไม่มี Cache
   │
   ├─ Pattern Matching (processor.py)
   │  ├─ สแกน Pattern 3-8 วัน
   │  ├─ คำนวณ Threshold (Market-specific)
   │  ├─ หา Historical Matches
   │  └─ คำนวณ Prob%, RRR, Count
   │
   ├─ Gatekeeper Filter
   │  ├─ Min Prob (48-52% ตามตลาด)
   │  ├─ Min Stats (20-35 ตามตลาด)
   │  └─ Quality Filter (AvgWin > AvgLoss)
   │
   └─ Log Forecast (ถ้าผ่านเกณฑ์)
      ├─ บันทึกไปที่ performance_log.csv
      └─ แสดงใน Report

4. สร้าง Report
   ├─ แสดง 4 ตาราง (THAI, US, CHINA/HK, TAIWAN)
   ├─ แสดง Pending Forecasts
   ├─ แสดง Verified Forecasts
   └─ บันทึกไปที่ forecast_tomorrow.csv

5. Forward Testing (ถ้ามี)
   ├─ ตรวจสอบ Pending Forecasts
   ├─ Verify ผลจริง (หลังตลาดปิด)
   └─ อัปเดต performance_log.csv
```

### 2. Backtest Flow (scripts/backtest.py)

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKTEST FLOW                              │
└─────────────────────────────────────────────────────────────┘

1. โหลดข้อมูล (Load Data)
   ├─ Fetch Historical Data (5000 bars)
   ├─ คำนวณ ATR (14 periods)
   └─ แบ่ง Train/Test (80/20 Adaptive Split)

2. สำหรับแต่ละ Pattern:
   ├─ หา Historical Matches
   ├─ คำนวณ Prob%, RRR, Count
   └─ ตรวจสอบ Gatekeeper

3. Simulate Trade (ถ้าผ่าน Gatekeeper)
   ├─ Entry: Close ของวันที่มี Signal
   ├─ Risk Management:
   │  ├─ ATR-based SL (1.0-1.2x ตามตลาด)
   │  ├─ ATR-based TP (2.5-3.5x ตามตลาด)
   │  ├─ Trailing Stop (Activate 2.0%, Distance 40-60%)
   │  └─ Max Hold (5-10 days ตามตลาด)
   │
   ├─ Exit Logic:
   │  ├─ TP Hit → Exit (Take Profit)
   │  ├─ SL Hit → Exit (Stop Loss)
   │  ├─ Trailing Stop → Exit (Lock Profit)
   │  └─ Max Hold → Exit (Time Stop)
   │
   └─ บันทึกผล (trade_history_*.csv)

4. สร้าง Trade History Logs
   ├─ trade_history_THAI.csv
   ├─ trade_history_US.csv
   ├─ trade_history_CHINA.csv
   ├─ trade_history_TAIWAN.csv
   └─ trade_history_METALS.csv
```

### 3. Calculate Metrics Flow (scripts/calculate_metrics.py)

```
┌─────────────────────────────────────────────────────────────┐
│              CALCULATE METRICS FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. โหลด Trade History Logs
   ├─ อ่าน trade_history_*.csv
   ├─ แยกตาม Country (TH, US, CN, TW, GL)
   └─ คำนวณ PnL (actual_return × direction)

2. สำหรับแต่ละ Symbol:
   ├─ คำนวณ Metrics:
   │  ├─ Count (จำนวน trades)
   │  ├─ Prob% (Win Rate)
   │  ├─ AvgWin% (Average Winning Trade)
   │  ├─ AvgLoss% (Average Losing Trade)
   │  └─ RRR (Risk-Reward Ratio = AvgWin / AvgLoss)
   │
   └─ ตรวจสอบ Filter Criteria:
      ├─ THAI: Prob > 60%, RRR > 2.0, Count >= 5
      ├─ US: Prob >= 60%, RRR >= 1.5, Count >= 15
      ├─ CHINA/HK: Prob > 60%, RRR > 2.0, Count >= 5
      ├─ TAIWAN: Prob >= 50%, RRR >= 1.0, Count >= 15
      └─ METALS: Prob >= 40% (30min) / 25% (15min), RRR >= 0.75/0.8, Count >= 20

3. สร้าง Report
   ├─ แสดง 4 ตาราง (THAI, US, CHINA/HK, TAIWAN)
   ├─ แสดง SUPER ELITE ALPHA TIER
   └─ บันทึกไปที่ symbol_performance.csv
```

### 4. Forward Testing Flow (core/performance.py)

```
┌─────────────────────────────────────────────────────────────┐
│              FORWARD TESTING FLOW                             │
└─────────────────────────────────────────────────────────────┘

1. Log Forecast (log_forecast)
   ├─ รับข้อมูล: symbol, pattern, forecast (UP/DOWN), target_date, prob, matches
   ├─ ตรวจสอบ Deduplication (ไม่ให้ซ้ำ)
   ├─ กำหนด Tier (A: Prob>=60%, B: Prob 50-59%)
   └─ บันทึกไปที่ performance_log.csv

2. Verify Forecast (verify_forecast)
   ├─ ตรวจสอบ Pending Forecasts (target_date ผ่านไปแล้ว)
   ├─ Fetch ข้อมูลจริง (TradingView API)
   ├─ เปรียบเทียบ Forecast vs Actual
   ├─ คำนวณ actual_return
   └─ อัปเดต performance_log.csv (verified=True)

3. Check Forward Testing (scripts/check_forward_testing.py)
   ├─ แสดง Pending Forecasts
   ├─ แสดง Verified Forecasts
   └─ แสดง Summary (Win Rate, Accuracy)
```

---

## 📋 คำสั่งทั้งหมด (Complete Command Reference)

### 🚀 Main System Commands

#### 1. รันระบบหลัก (Daily Report)
```bash
# รันระบบทั้งหมด (255+ หุ้น)
python main.py

# Output:
# - Console report (4 ตาราง: THAI, US, CHINA/HK, TAIWAN)
# - data/forecast_tomorrow.csv
# - data/performance_log.csv (ถ้ามี forecast ใหม่)
```

**เมื่อไหร่ใช้:**
- ทุกวันหลังตลาดปิด (17:00 ICT สำหรับตลาดเอเชีย, 05:00 ICT สำหรับตลาดอเมริกา)
- ต้องการดูสัญญาณสำหรับวันถัดไป

**เวลาที่แนะนำ:**
- 🇹🇭 **THAI:** 17:00-18:00 ICT (หลัง SET ปิด)
- 🇺🇸 **US:** 05:00-06:00 ICT (หลัง NASDAQ/NYSE ปิด)
- 🇹🇼 **TAIWAN:** 13:00-14:00 ICT (หลัง TWSE ปิด)
- 🇨🇳 **CHINA/HK:** 15:30-16:30 ICT (หลัง HKEX ปิด)

---

### 🔬 Backtest Commands

#### 2. รัน Backtest (Full Scan)
```bash
# Backtest ทั้งหมด (ทุกตลาด)
python scripts/backtest.py --full --bars 2500

# Backtest เฉพาะตลาด
python scripts/backtest.py --full --bars 2500 --group THAI
python scripts/backtest.py --full --bars 2500 --group US
python scripts/backtest.py --full --bars 2500 --group CHINA
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# Backtest แบบ Interactive (เลือกตลาด)
python scripts/run_single_backtest.py

# Backtest ทั้งหมด (Automated)
python scripts/run_all_backtests_new_settings.py
```

**Parameters:**
- `--full`: Full scan (ทุกหุ้นในกลุ่ม)
- `--bars 2500`: ใช้ข้อมูล 2500 bars (ประมาณ 10 ปี)
- `--group THAI/US/CHINA/TAIWAN`: เลือกตลาด

**Output:**
- `logs/trade_history_THAI.csv`
- `logs/trade_history_US.csv`
- `logs/trade_history_CHINA.csv`
- `logs/trade_history_TAIWAN.csv`
- `data/full_backtest_results.csv`

**เวลาที่ใช้:**
- THAI: ~30-60 นาที (118 หุ้น)
- US: ~60-90 นาที (98 หุ้น)
- CHINA/HK: ~10-20 นาที (13 หุ้น)
- TAIWAN: ~15-30 นาที (10 หุ้น)

#### 3. Override Risk Management Parameters (สำหรับ Testing)
```bash
# Override TP, Trailing, Max Hold
python scripts/backtest.py --full --bars 2500 --group THAI \
    --atr_tp_mult 2.5 \
    --atr_sl_mult 1.2 \
    --trail_activate 2.0 \
    --trail_distance 60.0 \
    --max_hold 10

# Override Gatekeeper
python scripts/backtest.py --full --bars 2500 --group THAI \
    --min_prob 48.0 \
    --min_stats 30 \
    --multiplier 1.1
```

**Parameters:**
- `--atr_tp_mult`: ATR TP Multiplier (default: 2.5-3.5x ตามตลาด)
- `--atr_sl_mult`: ATR SL Multiplier (default: 1.0-1.2x ตามตลาด)
- `--trail_activate`: Trailing Stop Activation % (default: 2.0%)
- `--trail_distance`: Trailing Stop Distance % (default: 40-60% ตามตลาด)
- `--max_hold`: Max Hold Days (default: 5-10 ตามตลาด)
- `--min_prob`: Min Probability % (default: 48-52% ตามตลาด)
- `--min_stats`: Min Stats (default: 20-35 ตามตลาด)
- `--multiplier`: Threshold Multiplier (default: 0.9-1.1 ตามตลาด)

---

### 📊 Metrics & Reports Commands

#### 4. คำนวณ Metrics (Performance Analysis)
```bash
# คำนวณ Metrics จาก Trade History
python scripts/calculate_metrics.py

# Output:
# - Console report (4 ตาราง: THAI, US, CHINA/HK, TAIWAN)
# - data/symbol_performance.csv
```

**ใช้ทำอะไร:**
- คำนวณ Prob%, RRR, Count สำหรับแต่ละหุ้น
- แสดงหุ้นที่ผ่านเกณฑ์ (Filter Criteria)
- สร้าง symbol_performance.csv สำหรับ Equity Curve

**เมื่อไหร่ใช้:**
- หลังรัน Backtest เสร็จ
- ต้องการดูผลลัพธ์ Performance

#### 5. เปรียบเทียบผลลัพธ์ (Before/After Comparison)
```bash
# เปรียบเทียบผลลัพธ์ก่อน/หลังปรับ TP
python scripts/compare_before_after_tp_adjustment.py

# Output:
# - Console report (Before/After comparison)
# - แสดง TP Exits, SL Exits, RRR, Win Rate
```

**ใช้ทำอะไร:**
- เปรียบเทียบผลลัพธ์ก่อน/หลังปรับ Risk Management
- วิเคราะห์ผลกระทบของการปรับ TP/SL

---

### 📈 Visualization Commands

#### 6. สร้าง Equity Curves
```bash
# สร้าง Equity Curves (ทุกตลาด)
python scripts/plot_equity_curves.py

# Output:
# - data/plots/equity_THAI.png
# - data/plots/equity_US.png
# - data/plots/equity_CHINA.png
# - data/plots/equity_TAIWAN.png
# - data/plots/equity_all_markets.png
```

**ใช้ทำอะไร:**
- แสดง Equity Curve (Cumulative Profit/Loss)
- วิเคราะห์ Performance ตามเวลา
- เปรียบเทียบ Performance ระหว่างตลาด

**เมื่อไหร่ใช้:**
- หลังรัน Backtest และ Calculate Metrics เสร็จ
- ต้องการดูภาพรวม Performance

---

### 🔍 Forward Testing Commands

#### 7. ตรวจสอบ Forward Testing
```bash
# แสดง Pending + Verified Forecasts
python scripts/check_forward_testing.py

# Verify Pending Forecasts (อัตโนมัติ)
python scripts/check_forward_testing.py --verify

# แสดง Summary (30 วันล่าสุด)
python scripts/check_forward_testing.py --days 30

# แสดงทั้งหมด
python scripts/check_forward_testing.py --all
```

**ใช้ทำอะไร:**
- ตรวจสอบ Forecasts ที่ยัง Pending
- Verify Forecasts ที่ target_date ผ่านไปแล้ว
- ดู Win Rate และ Accuracy

**เมื่อไหร่ใช้:**
- ทุกวันหลังตลาดปิด (เพื่อ Verify Forecasts)
- ต้องการดูผล Forward Testing

---

### 🛠️ Utility Commands

#### 8. Clear Cache
```bash
# Clear Cache ทั้งหมด
python scripts/clear_cache.py

# หรือ
python scripts/clean_all_cache.py
```

**ใช้ทำอะไร:**
- ลบ Cache เพื่อ Fetch ข้อมูลใหม่
- แก้ปัญหา Cache เก่า/เสีย

**เมื่อไหร่ใช้:**
- ต้องการ Fetch ข้อมูลใหม่ทั้งหมด
- Cache มีปัญหา

#### 9. Auto Scheduler (Automated Daily Runs)
```bash
# รัน Auto Scheduler
python scripts/auto_scheduler.py
```

**ใช้ทำอะไร:**
- รันระบบอัตโนมัติตาม Schedule
- รองรับหลายตลาด (THAI, US, CHINA/HK, TAIWAN)

**Schedule:**
- 🇹🇼 **TAIWAN:** 13:00 ICT
- 🇨🇳 **CHINA/HK:** 15:30 ICT
- 🇹🇭 **THAI:** 17:00 ICT
- 🇺🇸 **US:** 05:00 ICT

#### 10. Market Sentiment
```bash
# ดู Market Sentiment
python scripts/market_sentiment.py
```

**ใช้ทำอะไร:**
- ดูภาพรวมตลาด (Bullish/Bearish)
- วิเคราะห์ Sentiment สำหรับวันถัดไป

#### 11. Intraday Scanner (Gold/Silver)
```bash
# รัน Intraday Scanner (15min/30min)
python scripts/intraday_runner.py
```

**ใช้ทำอะไร:**
- สแกน Gold/Silver แบบ real-time
- ตรวจสอบทุก 5-15 นาที
- แจ้งเตือนเมื่อเจอสัญญาณ Prob > 60%

**เมื่อไหร่ใช้:**
- ระหว่างเทรด intraday
- ต้องการสัญญาณแบบ real-time

---

### 📝 Complete Workflow Examples

#### Workflow 1: Daily Trading (Normal Use)
```bash
# 1. รันระบบหลัก (หลังตลาดปิด)
python main.py

# 2. ตรวจสอบ Forward Testing (Verify Forecasts)
python scripts/check_forward_testing.py --verify

# 3. ดู Market Sentiment (Optional)
python scripts/market_sentiment.py
```

#### Workflow 2: Backtest & Analysis (Testing/Research)
```bash
# 1. Clear Cache (ถ้าต้องการข้อมูลใหม่)
python scripts/clear_cache.py

# 2. รัน Backtest (เลือกตลาด)
python scripts/run_single_backtest.py
# หรือ
python scripts/backtest.py --full --bars 2500 --group THAI

# 3. คำนวณ Metrics
python scripts/calculate_metrics.py

# 4. สร้าง Equity Curves
python scripts/plot_equity_curves.py

# 5. เปรียบเทียบผลลัพธ์ (ถ้ามี)
python scripts/compare_before_after_tp_adjustment.py
```

#### Workflow 3: Full System Test (All Markets)
```bash
# 1. Clear Cache
python scripts/clear_cache.py

# 2. รัน Backtest ทั้งหมด (Automated)
python scripts/run_all_backtests_new_settings.py

# 3. คำนวณ Metrics
python scripts/calculate_metrics.py

# 4. สร้าง Equity Curves
python scripts/plot_equity_curves.py
```

---

## ⚙️ Risk Management Parameters

### 🇹🇭 THAI MARKET (SET)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **ATR SL Multiplier** | `1.2x` | V14.3: เพิ่มจาก 1.0x เพื่อลด SL exits |
| **ATR TP Multiplier** | `2.5x` | V14.3: ลดจาก 3.0x เพื่อเพิ่ม TP exits |
| **Max Hold Days** | `10 days` | V14.3: เพิ่มจาก 7 → 10 ให้มีเวลาไปถึง TP |
| **Trailing Activate** | `2.0%` | Activate ช้าลง - ให้มีเวลาไปถึง TP |
| **Trailing Distance** | `60%` | V14.3: เพิ่มจาก 50% → 60% ให้กำไร run ได้มากขึ้น |
| **Min Prob (Gatekeeper)** | `48%` | V14.3: ลดจาก 50% เพื่อเพิ่ม Win Rate |
| **Min Stats (Gatekeeper)** | `30` | V14.2: เพิ่มจาก 25 |
| **Threshold Multiplier** | `1.1` | V14.0: เพิ่มจาก 1.0 |

**Filter Criteria (Display):**
- Prob > 60%
- RRR > 2.0
- Count >= 5

---

### 🇺🇸 US MARKET (NASDAQ/NYSE)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **ATR SL Multiplier** | `1.0x` | |
| **ATR TP Multiplier** | `3.5x` | ปรับจาก 5.0x → 3.5x เพื่อให้ถึง TP ได้มากขึ้น |
| **Max Hold Days** | `5 days` | Revert: ค่าที่เสถียร |
| **Trailing Activate** | `2.0%` | Activate ช้าลง - ให้มีเวลาไปถึง TP |
| **Trailing Distance** | `40%` | Trail แน่นขึ้น - lock กำไรดีขึ้น |
| **Min Prob (Gatekeeper)** | `52.0%` | |
| **Min Stats (Gatekeeper)** | `20` | |
| **Threshold Multiplier** | `0.9` | |
| **Quality Filter** | `AvgWin >= AvgLoss * 0.9` | US Quality Filter |

**Filter Criteria (Display):**
- Prob >= 60%
- RRR >= 1.5
- Count >= 15

---

### 🇹🇼 TAIWAN MARKET (TWSE)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **ATR SL Multiplier** | `1.0x` | |
| **ATR TP Multiplier** | `3.5x` | ปรับจาก 6.5x → 3.5x เพื่อให้ถึง TP ได้มากขึ้น |
| **Max Hold Days** | `5 days` | Revert: ค่าที่เสถียร |
| **Trailing Activate** | `2.0%` | Activate ช้าลง - ให้มีเวลาไปถึง TP |
| **Trailing Distance** | `40%` | Trail แน่นขึ้น - lock กำไรดีขึ้น |
| **Min Prob (Gatekeeper)** | `51.0%` | |
| **Min Stats (Gatekeeper)** | `25` | |
| **Threshold Multiplier** | `0.9` | |

**Filter Criteria (Display):**
- Prob >= 50%
- RRR >= 1.0
- Count >= 15

---

### 🇨🇳 CHINA/HK MARKET (HKEX)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **ATR SL Multiplier** | `1.0x` | |
| **ATR TP Multiplier** | `3.0x` | V14.1: ลดจาก 4.5x → 3.0x เพื่อให้ถึง TP ได้ง่ายขึ้น |
| **Max Hold Days** | `7 days` | V14.1: คงเดิม |
| **Trailing Activate** | `2.0%` | V14.1: เพิ่มจาก 1.5% → 2.0% activate ช้าลง |
| **Trailing Distance** | `50%` | V14.1: เพิ่มจาก 35% → 50% ให้กำไร run ได้มากขึ้น |
| **Min Prob (Gatekeeper)** | `52.0%` | V14.1: ลดจาก 55% เพื่อเพิ่ม Win Rate |
| **Min Stats (Gatekeeper)** | `35` | V14.0: เพิ่มจาก 30 |
| **Threshold Multiplier** | `0.9` | |
| **Quality Filter** | `AvgWin > AvgLoss` | V14.1: เพิ่ม quality filter |

**Filter Criteria (Display):**
- Prob > 60%
- RRR > 2.0
- Count >= 5

---

### 📊 ATR-Based Risk Management System

**ATR Calculation:**
- **Period:** 14 bars
- **Formula:** `ATR = Average(True Range)`
  - `True Range = max(High-Low, abs(High-PrevClose), abs(Low-PrevClose))`

**SL/TP Calculation:**
- `SL = Entry Price ± (ATR × ATR_SL_Multiplier)`
- `TP = Entry Price ± (ATR × ATR_TP_Multiplier)`

**Caps:**
- Max SL: `7%` (ป้องกัน SL กว้างเกินไป)
- Max TP: `15%` (ป้องกัน TP สูงเกินไป)

**ข้อดี:**
- ✅ ยืดหยุ่นตาม volatility (หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ)
- ✅ เอาไปใช้จริงง่าย (Auto system)
- ✅ Realistic (ใช้ความผันผวนจริงของหุ้น)

---

### 🔄 Trailing Stop System

**How It Works:**
1. **Activation:** เมื่อกำไรถึง `Trail Activate %` (เช่น 2.0%) → trailing stop เริ่มทำงาน
2. **Distance:** Trailing stop จะตามห่างจาก peak profit `Trail Distance %` (เช่น 60% = ถ้า peak profit 10% → trailing stop จะอยู่ที่ 4% จาก entry)
3. **Lock Profit:** เมื่อราคาตกลง → trailing stop จะ lock กำไรไว้

**Example (Thai Market):**
- Entry: $100
- Peak Profit: $110 (10% profit)
- Trail Activate: 2.0% ✅ (activated)
- Trail Distance: 60%
- Trailing Stop Level: $100 + (10% × 40%) = $104 (4% profit locked)
- ถ้าราคาตกลงถึง $104 → exit ที่ $104 (lock กำไร 4%)

---

## 📖 การใช้งานแต่ละส่วน

### 1. Main System (main.py)

**Purpose:** รันระบบหลักเพื่อทำนายทิศทางหุ้น

**Input:**
- `config.py` (Asset Groups, Settings)
- TradingView API (Data Fetching)
- Cache (ถ้ามี)

**Output:**
- Console Report (4 ตาราง: THAI, US, CHINA/HK, TAIWAN)
- `data/forecast_tomorrow.csv`
- `data/performance_log.csv` (ถ้ามี forecast ใหม่)

**Process:**
1. โหลด Asset Groups จาก `config.py`
2. สำหรับแต่ละหุ้น:
   - Fetch Data (ใช้ Cache ถ้ามี)
   - Pattern Matching (3-8 วัน)
   - คำนวณ Prob%, RRR, Count
   - ตรวจสอบ Gatekeeper
   - Log Forecast (ถ้าผ่านเกณฑ์)
3. สร้าง Report

**When to Use:**
- ทุกวันหลังตลาดปิด
- ต้องการดูสัญญาณสำหรับวันถัดไป

---

### 2. Backtest System (scripts/backtest.py)

**Purpose:** Simulate การเทรดด้วยข้อมูลประวัติศาสตร์

**Input:**
- Historical Data (5000 bars)
- Risk Management Parameters

**Output:**
- `logs/trade_history_*.csv` (Trade History Logs)
- `data/full_backtest_results.csv`

**Process:**
1. โหลดข้อมูลประวัติศาสตร์
2. แบ่ง Train/Test (80/20)
3. สำหรับแต่ละ Pattern:
   - หา Historical Matches
   - ตรวจสอบ Gatekeeper
   - Simulate Trade (ถ้าผ่าน)
4. บันทึกผล

**When to Use:**
- ต้องการประเมินประสิทธิภาพ
- ต้องการทดสอบ Risk Management Parameters
- ต้องการวิเคราะห์ Performance

---

### 3. Calculate Metrics (scripts/calculate_metrics.py)

**Purpose:** คำนวณ Performance Metrics จาก Trade History

**Input:**
- `logs/trade_history_*.csv`

**Output:**
- Console Report (4 ตาราง)
- `data/symbol_performance.csv`

**Process:**
1. โหลด Trade History Logs
2. สำหรับแต่ละ Symbol:
   - คำนวณ Prob%, RRR, Count
   - ตรวจสอบ Filter Criteria
3. สร้าง Report

**When to Use:**
- หลังรัน Backtest เสร็จ
- ต้องการดูผลลัพธ์ Performance

---

### 4. Forward Testing (core/performance.py)

**Purpose:** ทำนายและตรวจสอบผลจริง

**Input:**
- Forecasts จาก `main.py`
- Actual Data (TradingView API)

**Output:**
- `data/performance_log.csv` (Updated with verified results)

**Process:**
1. Log Forecast (เมื่อ `main.py` ทำนาย)
2. Verify Forecast (เมื่อ `target_date` ผ่านไป)
3. อัปเดต `performance_log.csv`

**When to Use:**
- ทุกวันหลังตลาดปิด (เพื่อ Verify Forecasts)
- ต้องการดูผล Forward Testing

---

## 🔧 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Cache เก่า/เสีย
**อาการ:**
- ข้อมูลไม่อัปเดต
- Error เมื่อ Fetch Data

**แก้ไข:**
```bash
python scripts/clear_cache.py
```

#### 2. Backtest ไม่รัน
**อาการ:**
- Backtest เสร็จเร็วเกินไป
- ไม่มี Trade History Logs

**แก้ไข:**
```bash
# ตรวจสอบว่าใช้ --full หรือ --all
python scripts/backtest.py --full --bars 2500 --group THAI

# ลบ Trade History Logs เก่า
del logs\trade_history_*.csv
del data\full_backtest_results.csv
```

#### 3. Forward Testing ไม่ Verify
**อาการ:**
- Forecasts ยัง Pending อยู่แม้ว่า target_date ผ่านไปแล้ว

**แก้ไข:**
```bash
# Verify แบบ Manual
python scripts/check_forward_testing.py --verify
```

#### 4. Equity Curve ไม่แสดง
**อาการ:**
- กราฟว่างเปล่า
- ไม่มีข้อมูลในกราฟ

**แก้ไข:**
```bash
# ตรวจสอบว่า Calculate Metrics รันแล้ว
python scripts/calculate_metrics.py

# รัน Plot Equity Curves อีกครั้ง
python scripts/plot_equity_curves.py
```

#### 5. Connection Timeout
**อาการ:**
- Error เมื่อ Fetch Data
- Connection Timed Out

**แก้ไข:**
- ตรวจสอบ Internet Connection
- ตรวจสอบ TradingView API Credentials (`.env`)
- รอสักครู่แล้วลองใหม่

---

## 📁 Configuration Files

### 1. config.py

**Purpose:** กำหนด Asset Groups, Settings, Thresholds

**Key Settings:**
```python
# Forecast Logging Thresholds
MIN_PROB_THRESHOLD = 50.0  # Minimum probability for logging
MIN_MATCHES_THRESHOLD = 30  # Minimum matches for logging
USE_TIER_CLASSIFICATION = True  # Enable tier A/B classification

# Asset Groups
ASSET_GROUPS = {
    "GROUP_A_THAI": {...},
    "GROUP_B_US": {...},
    "GROUP_C_CHINA_HK": {...},
    "GROUP_D_TAIWAN": {...},
    "GROUP_E_METALS": {...}
}
```

**Location:** `config.py`

---

### 2. .env

**Purpose:** เก็บ TradingView API Credentials

**Format:**
```
TV_USERNAME=your_username
TV_PASSWORD=your_password
TV_SESSIONID=your_session_id (optional)
```

**Location:** `.env` (root directory)

---

### 3. data/symbol_performance.csv

**Purpose:** เก็บ Performance Metrics สำหรับแต่ละ Symbol

**Columns:**
- `symbol`: Symbol name
- `Country`: Country code (TH, US, CN, TW, GL)
- `Count`: Number of trades
- `Prob%`: Win Rate
- `AvgWin%`: Average Winning Trade
- `AvgLoss%`: Average Losing Trade
- `RR_Ratio`: Risk-Reward Ratio

**Location:** `data/symbol_performance.csv`

---

### 4. data/performance_log.csv

**Purpose:** เก็บ Forward Testing Logs

**Columns:**
- `scan_date`: Date when forecast was made
- `symbol`: Symbol name
- `pattern`: Pattern description
- `forecast`: UP/DOWN
- `target_date`: Date to verify
- `prob`: Probability
- `matches`: Number of matches
- `tier`: A/B (optional)
- `verified`: True/False
- `actual`: UP/DOWN (after verification)
- `actual_return`: Actual return %

**Location:** `data/performance_log.csv`

---

## 📚 Additional Resources

### Documentation Files
- **[README.md](README.md)** - ภาพรวมระบบ
- **[RISK_MANAGEMENT_SUMMARY.md](RISK_MANAGEMENT_SUMMARY.md)** - Risk Management Parameters
- **[BACKTEST_COMMANDS.md](BACKTEST_COMMANDS.md)** - Backtest Commands
- **[docs/USER_MANUAL.md](docs/USER_MANUAL.md)** - คู่มือผู้ใช้
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - คำสั่งที่ใช้บ่อย

### Important Notes
1. **Market Close Timing:** รันระบบหลังตลาดปิดเพื่อให้ได้ข้อมูลที่ถูกต้อง
2. **Forward Testing:** ต้องใช้เวลา 3-4 วันเพื่อให้ได้ผลลัพธ์ที่เชื่อถือได้
3. **Risk Management:** ใช้ Risk Management ที่เหมาะสมในการเทรดจริง
4. **Backtesting:** ผลลัพธ์มาจากข้อมูลประวัติศาสตร์ ไม่ได้การันตีผลลัพธ์ในอนาคต

---

**Last Updated:** 2026-01-XX (V14.3)  
**Status:** Production-Ready  
**Maintainer:** PredictPlus1 Team

