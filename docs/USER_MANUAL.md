# 📖 คู่มือระบบ PredictPlus1 - User Manual

**Last Updated:** 2026-02-22  
**Version:** V4.4

---

## 📑 สารบัญ

1. [คำสั่งหลัก (Main Commands)](#คำสั่งหลัก-main-commands)
2. [Backtest & Analysis](#backtest--analysis)
3. [Metrics & Reports](#metrics--reports)
4. [Visualization](#visualization)
5. [Testing & Optimization](#testing--optimization)
6. [Utilities & Helpers](#utilities--helpers)
7. [Workflow Examples](#workflow-examples)

---

## 🚀 คำสั่งหลัก (Main Commands)

### 1. ดูรายงานประจำวัน (Daily Report)
```bash
python main.py
```
**ใช้ทำอะไร:**
- วิเคราะห์หุ้นทั้งหมด (255+ หุ้น)
- สร้างรายงาน 4 ตาราง (THAI, US, CHINA/HK, TAIWAN)
- แสดงหุ้นที่ผ่านเกณฑ์พร้อม Prob%, RRR, Count

**เมื่อไหร่ใช้:**
- ทุกวันหลังตลาดปิด (17:00-18:00)
- ดูสัญญาณสำหรับวันถัดไป (N+1)

**Output:**
- Console report
- `data/pattern_results.csv`

---

### 2. Intraday Scanner (Gold/Silver)
```bash
python scripts/intraday_runner.py
```
**ใช้ทำอะไร:**
- สแกนหาสัญญาณ Gold/Silver แบบ real-time
- ตรวจสอบทุก 5-15 นาที
- แจ้งเตือนเมื่อเจอสัญญาณ Prob > 60%

**เมื่อไหร่ใช้:**
- ระหว่างเทรด intraday
- ต้องการสัญญาณแบบ real-time

---

### 3. ดู Market Sentiment
```bash
python scripts/market_sentiment.py
```
**ใช้ทำอะไร:**
- ดูภาพรวมตลาด (Bullish/Bearish)
- วิเคราะห์ sentiment สำหรับวันถัดไป

---

## 📊 Backtest & Analysis

### 4. รัน Backtest (หลัก)
```bash
# Backtest ทุกตลาด
python scripts/backtest.py --full --bars 2000

# Backtest ตลาดเฉพาะ
python scripts/backtest.py --full --bars 2000 --group TAIWAN
python scripts/backtest.py --full --bars 2000 --group US
python scripts/backtest.py --full --bars 2000 --group THAI
python scripts/backtest.py --full --bars 2000 --group CHINA

# Backtest แบบเร็ว (skip validation)
python scripts/backtest.py --full --bars 2000 --group TAIWAN --fast
```
**ใช้ทำอะไร:**
- รัน backtest บน historical data
- สร้าง trade history
- คำนวณ Prob%, RRR, Count

**Parameters:**
- `--full`: รันทุกหุ้น
- `--bars`: จำนวน historical bars (2000, 2500, 3000)
- `--group`: ตลาดที่ต้องการ (TAIWAN, US, THAI, CHINA)
- `--fast`: ข้าม validation (เร็วขึ้น)

**Output:**
- `logs/trade_history_TAIWAN.csv`
- `logs/trade_history_US.csv`
- `logs/trade_history_THAI.csv`
- `logs/trade_history_CHINA.csv`
- `data/full_backtest_results.csv`

---

### 5. คำนวณ Metrics
```bash
python scripts/calculate_metrics.py
```
**ใช้ทำอะไร:**
- อ่าน trade history
- คำนวณ Prob%, RRR, AvgWin%, AvgLoss%, Count
- แสดงรายงานตามเกณฑ์ของแต่ละตลาด

**Output:**
- Console report (4 ตาราง)
- `data/symbol_performance.csv`

**เกณฑ์ Display (V4.4 Simplified):**
- **THAI:** Prob >= 55% (Consensus), Min Stats 30 per suffix
- **US:** Prob >= 55% (Consensus), Min Stats 30 per suffix
- **CHINA/HK:** Prob >= 55% (Consensus), Min Stats 30 per suffix
- **TAIWAN:** Prob >= 55% (Consensus), Min Stats 30 per suffix

---

### 6. วิเคราะห์ Backtest Results
```bash
python scripts/analyze_backtest_results.py
```
**ใช้ทำอะไร:**
- วิเคราะห์ผลลัพธ์ backtest แบบละเอียด
- ดู win rate, RRR, drawdown

---

## 📈 Metrics & Reports

### 7. ดู Performance Metrics
```bash
python scripts/view_accuracy.py
```
**ใช้ทำอะไร:**
- ตรวจสอบความแม่นยำของ predictions
- เปรียบเทียบ Forecast vs Actual

---

### 8. ดูรายงาน
```bash
python scripts/view_report.py
```
**ใช้ทำอะไร:**
- ดูรายงานสรุป
- วิเคราะห์ performance

---

## 📊 Visualization

### 9. Plot Equity Curve
```bash
python scripts/plot_equity.py
```
**ใช้ทำอะไร:**
- สร้างกราฟ equity curve
- แสดงผลกำไร/ขาดทุนตามเวลา

**Output:**
- `plots/equity_curve.png`

---

### 10. Plot Market Comparison
```bash
python scripts/plot_markets_from_metrics.py
```
**ใช้ทำอะไร:**
- เปรียบเทียบ performance ระหว่างตลาด
- แสดง equity curve ของแต่ละตลาด

**Output:**
- `plots/equity_per_market.png`

---

### 11. Plot Elite Stocks
```bash
python scripts/plot_elite_from_metrics.py
```
**ใช้ทำอะไร:**
- แสดง equity curve ของ elite stocks (Prob >= 60%, RRR >= 2.0)

---

## 🧪 Testing & Optimization

### 12. ทดสอบ Taiwan Parameters
```bash
python scripts/test_taiwan_parameters.py
```
**ใช้ทำอะไร:**
- ทดสอบหลายค่า min_prob และ n_bars
- หาค่าที่เหมาะสมที่สุด

**Note:** ใช้เวลานาน (2-6 ชั่วโมง)

---

### 13. Quick Test Taiwan Params
```bash
python scripts/quick_test_taiwan_params.py
```
**ใช้ทำอะไร:**
- Helper สำหรับบันทึกผลการทดสอบ
- แสดง test matrix

---

### 14. วิเคราะห์ TSMC
```bash
python scripts/analyze_tsmc.py
```
**ใช้ทำอะไร:**
- วิเคราะห์ TSMC (2330) แบบละเอียด
- ดู Prob% vs Actual Win Rate
- วิเคราะห์ Elite Trades

---

## 🛠️ Utilities & Helpers

### 15. Health Check
```bash
python scripts/health_check.py
```
**ใช้ทำอะไร:**
- ตรวจสอบสถานะระบบ
- ตรวจสอบ data files
- ตรวจสอบ dependencies

---

### 16. Clean Duplicate Forecasts
```bash
python scripts/cleanup_duplicate_forecasts.py
```
**ใช้ทำอะไร:**
- ลบ duplicate forecasts
- ทำความสะอาด data

---

### 17. Fetch Missing Cache
```bash
python scripts/fetch_missing_cache.py
```
**ใช้ทำอะไร:**
- ดึงข้อมูลที่หายไป
- อัพเดท cache

---

### 18. Split Trade History by Market
```bash
python scripts/split_trade_history_by_market.py
```
**ใช้ทำอะไร:**
- แยก trade history ตามตลาด
- จัดระเบียบไฟล์

---

## 📋 Workflow Examples

### Workflow 1: Daily Trading Decision

```bash
# 1. รัน backtest (ถ้ายังไม่มี)
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# 2. คำนวณ metrics
python scripts/calculate_metrics.py

# 3. ดูรายงาน
python main.py
```

**เมื่อไหร่ใช้:**
- ทุกวันหลังตลาดปิด
- ต้องการดูสัญญาณสำหรับวันถัดไป

---

### Workflow 2: Optimize Taiwan Market

```bash
# 1. ทดสอบหลายค่า parameters
# แก้ไข backtest.py: min_prob = 51.0 (หรือ 51.5, 52.0, 52.5)
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# 2. คำนวณ metrics
python scripts/calculate_metrics.py

# 3. บันทึกผลลัพธ์
python scripts/quick_test_taiwan_params.py

# 4. เปรียบเทียบผลลัพธ์
# ดู docs/TAIWAN_PARAMETER_TEST_TEMPLATE.md
```

**เมื่อไหร่ใช้:**
- ต้องการปรับปรุง performance
- ทดสอบ parameters ใหม่

---

### Workflow 3: Analyze Specific Stock

```bash
# 1. รัน backtest (ถ้ายังไม่มี)
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# 2. วิเคราะห์หุ้นเฉพาะ (เช่น TSMC)
python scripts/analyze_tsmc.py

# 3. ดู metrics
python scripts/calculate_metrics.py
```

**เมื่อไหร่ใช้:**
- ต้องการวิเคราะห์หุ้นเฉพาะ
- ตรวจสอบ performance ของหุ้น

---

### Workflow 4: Full System Update

```bash
# 1. Clean old results
rm logs/trade_history_*.csv

# 2. รัน backtest ทุกตลาด
python scripts/backtest.py --full --bars 2500 --group TAIWAN
python scripts/backtest.py --full --bars 2500 --group US
python scripts/backtest.py --full --bars 2500 --group THAI
python scripts/backtest.py --full --bars 2500 --group CHINA

# 3. คำนวณ metrics
python scripts/calculate_metrics.py

# 4. สร้าง visualizations
python scripts/plot_equity.py
python scripts/plot_markets_from_metrics.py
```

**เมื่อไหร่ใช้:**
- อัพเดทระบบทั้งหมด
- หลังปรับ parameters
- ต้องการผลลัพธ์ใหม่ทั้งหมด

---

## 📝 คำสั่งที่ใช้บ่อยที่สุด

### Top 5 คำสั่งที่ใช้บ่อย:

1. **`python scripts/backtest.py --full --bars 2500 --group TAIWAN`**
   - รัน backtest ตลาดไต้หวัน

2. **`python scripts/calculate_metrics.py`**
   - คำนวณ metrics และแสดงรายงาน

3. **`python main.py`**
   - ดูรายงานประจำวัน

4. **`python scripts/plot_equity.py`**
   - สร้างกราฟ equity curve

5. **`python scripts/analyze_tsmc.py`**
   - วิเคราะห์หุ้นเฉพาะ

---

## ⚠️ หมายเหตุสำคัญ

### 1. ต้องรัน Backtest ก่อน
- คำสั่ง `calculate_metrics.py` ต้องมี trade history ก่อน
- ถ้ายังไม่มี → รัน `backtest.py` ก่อน

### 2. Clean Old Results
- ถ้าต้องการผลลัพธ์ใหม่ → ลบ `logs/trade_history_*.csv` ก่อน
- หรือลบ entries ใน `data/full_backtest_results.csv`

### 3. Parameters ที่สำคัญ
- `--bars`: จำนวน historical bars (2000, 2500, 3000)
- `--group`: ตลาดที่ต้องการ (TAIWAN, US, THAI, CHINA)
- `--fast`: ข้าม validation (เร็วขึ้น แต่ไม่แนะนำ)

### 4. เวลาที่เหมาะสม
- **THAI:** 17:00-18:00 (หลังตลาดปิด)
- **US:** 18:00 (evening) หรือ 07:00 (morning)
- **TAIWAN/CHINA:** 17:00-18:00

---

## 🔗 เอกสารที่เกี่ยวข้อง

- `README.md` - ภาพรวมระบบ
- `docs/VERSION_HISTORY.md` - ประวัติการเปลี่ยนแปลง
- `docs/TAIWAN_PARAMETER_TEST_PLAN.md` - แผนการทดสอบ
- `docs/ELITE_FILTER_EXPLANATION.md` - อธิบาย Elite Filter

---

## ❓ FAQ

### Q: ต้องรัน backtest ทุกวันไหม?
**A:** ไม่จำเป็น ถ้าไม่ได้เปลี่ยน parameters → รันเมื่อต้องการอัพเดทผลลัพธ์

### Q: ใช้ `--bars` เท่าไหร่ดี?
**A:** 
- **2000:** Baseline (เร็ว)
- **2500:** Recommended (สมดุล)
- **3000:** Maximum (ช้า แต่ข้อมูลมาก)

### Q: ทำไมหุ้นบางตัวไม่แสดงในรายงาน?
**A:** ตรวจสอบเกณฑ์ display:
- THAI: Prob >= 60%, RRR >= 1.2, Count >= 30
- US: Prob >= 55%, RRR >= 1.2, Count >= 15
- TAIWAN: Prob >= 53%, RRR >= 1.25, Count 25-150

### Q: ต้องการดูหุ้นที่ผ่านเกณฑ์เพิ่มขึ้น?
**A:** 
- ลด `min_prob` ใน `backtest.py` (51.5% → 51.0%)
- ลด RRR requirement ใน `calculate_metrics.py` (1.3 → 1.25)

---

**Last Updated:** 2026-02-13  
**Version:** V12.4  
**Status:** ✅ Complete

