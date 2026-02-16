# สรุป Threshold และเกณฑ์หุ้นแต่ละประเทศ

**อัพเดทล่าสุด:** 2026-02-13

---

## 📊 ตารางสรุป Threshold และเกณฑ์

| ประเทศ | Engine | Threshold | Fixed? | ADX | Timeframe | Prob% | RRR | Count |
|--------|--------|-----------|--------|-----|-----------|-------|-----|-------|
| **🇹🇭 THAI** | MEAN_REVERSION | 1.0% | ❌ Dynamic | - | Daily | ≥60% | ≥1.20 | ≥30 |
| **🇺🇸 US** | TREND_MOMENTUM | 0.5% | ❌ Dynamic | ≥20 | Daily | ≥55% | ≥1.20 | ≥15 |
| **🇨🇳 CHINA/HK** | MEAN_REVERSION | 0.5% | ❌ Dynamic | - | Daily | ≥55% | ≥1.20 | ≥15 |
| **🇹🇼 TAIWAN** | TREND_MOMENTUM | 0.5% | ❌ Dynamic | ≥20 | Daily | ≥55% | ≥1.20 | ≥15 |
| **🥇 GOLD 30M** | MEAN_REVERSION | 0.10% | ✅ Fixed | - | 30min | ≥50% | - | - |
| **🥇 GOLD 15M** | MEAN_REVERSION | 0.10% | ✅ Fixed | - | 15min | ≥50% | - | - |
| **🥈 SILVER 30M** | MEAN_REVERSION | 0.15% | ✅ Fixed | - | 30min | ≥50% | - | - |
| **🥈 SILVER 15M** | MEAN_REVERSION | 0.20% | ✅ Fixed | - | 15min | ≥50% | - | - |

---

## 📋 รายละเอียดแต่ละประเทศ

### 🇹🇭 THAI MARKET (SET)

**Engine:** `MEAN_REVERSION`  
**Strategy:** Fade the move (ขายเมื่อขึ้นมาก, ซื้อเมื่อลงมาก)

**Threshold:**
- **Min Threshold:** 1.0% (0.01)
- **Fixed Threshold:** ❌ ไม่มี (ใช้ Dynamic Base)
- **Dynamic Base:** คำนวณจาก Volatility และ Historical Stats

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 60.0%** (ความแม่นยำสูง)
- **RRR >= 1.20** (Risk-Reward Ratio)
- **Count >= 30** (ข้อมูลเพียงพอ - เน้นความถี่สูง)

**Timeframe:** Daily  
**History Bars:** 5000 bars (~20 ปี)

**เหตุผล:**
- หุ้นไทยใช้ Mean Reversion → ต้องการความถี่สูงและความแม่นยำสูง
- Threshold สูงสุด (1.0%) เพราะหุ้นไทยมีความผันผวนต่ำกว่า
- ต้องการ Count สูง (30) เพื่อความน่าเชื่อถือทางสถิติ

---

### 🇺🇸 US STOCK (NASDAQ)

**Engine:** `TREND_MOMENTUM`  
**Strategy:** Follow the move (LONG ONLY - ซื้อตามเทรนด์)

**Threshold:**
- **Min Threshold:** 0.5% (0.005)
- **Fixed Threshold:** ❌ ไม่มี (ใช้ Dynamic Base)
- **Dynamic Base:** คำนวณจาก Volatility และ Historical Stats
- **Min ADX:** 20 (Trend Strength Filter)

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 55.0%** (ความแม่นยำปานกลาง)
- **RRR >= 1.20** (Risk-Reward Ratio)
- **Count >= 15** (ข้อมูลปานกลาง - Trend มีความถี่ต่ำ)

**Timeframe:** Daily  
**History Bars:** 5000 bars (~20 ปี)

**เหตุผล:**
- หุ้น US ใช้ Trend Momentum → ความถี่ต่ำแต่ผลตอบแทนสูง
- Threshold ต่ำกว่า (0.5%) เพราะหุ้น US มีความผันผวนสูงกว่า
- ต้องการ ADX >= 20 เพื่อยืนยันว่าเป็น Trend จริง
- Count ต่ำกว่า (15) เพราะ Trend มีความถี่ต่ำกว่า Mean Reversion

**📈 ผลลัพธ์:** ผ่านเกณฑ์ 14/94 (14.9%) - ดีขึ้นมาก!

---

### 🇨🇳 CHINA & HK MARKET (HKEX)

**Engine:** `MEAN_REVERSION` (เปลี่ยนจาก TREND ใน V4.4)  
**Strategy:** Fade the move

**Threshold:**
- **Min Threshold:** 0.5% (0.005)
- **Fixed Threshold:** ❌ ไม่มี (ใช้ Dynamic Base)
- **Dynamic Base:** คำนวณจาก Volatility และ Historical Stats

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 55.0%**
- **RRR >= 1.20**
- **Count >= 15**

**Timeframe:** Daily  
**History Bars:** 5000 bars

**เหตุผล:**
- เปลี่ยนเป็น Mean Reversion เพราะผลการทดสอบดีกว่า
- Threshold ต่ำ (0.5%) เพราะหุ้นจีนมีความผันผวนสูง
- **ปัญหา:** RRR เฉลี่ยต่ำ (0.96) ทำให้ผ่านเกณฑ์ยาก

**📈 ผลลัพธ์:** ผ่านเกณฑ์ 1/10 (10.0%)

---

### 🇹🇼 TAIWAN MARKET (TWSE)

**Engine:** `TREND_MOMENTUM`  
**Strategy:** Follow the move

**Threshold:**
- **Min Threshold:** 0.5% (0.005) - ลดจาก 1.0% ใน V4.4
- **Fixed Threshold:** ❌ ไม่มี (ใช้ Dynamic Base)
- **Dynamic Base:** คำนวณจาก Volatility และ Historical Stats
- **Min ADX:** 20 (Trend Strength Filter)

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 55.0%**
- **RRR >= 1.20**
- **Count >= 15**

**Timeframe:** Daily  
**History Bars:** 5000 bars

**เหตุผล:**
- Threshold ลดจาก 1.0% → 0.5% เพื่อเพิ่มโอกาสในการเทรด
- ต้องการ ADX >= 20 เพื่อยืนยัน Trend
- **ปัญหา:** RRR เฉลี่ยต่ำมาก (0.84) ทำให้ผ่านเกณฑ์ยากมาก

**📈 ผลลัพธ์:** ผ่านเกณฑ์ 0/10 (0.0%) - ต้องปรับปรุง

---

### 🥇 GOLD (XAUUSD)

**Engine:** `MEAN_REVERSION`  
**Strategy:** Fade the move

**Threshold:**
- **30min:** 0.10% (0.001) - Fixed
- **15min:** 0.10% (0.001) - Fixed
- **Backtest Results:**
  - 30min: 90 trades, RR 1.74
  - 15min: 108 trades, RR 0.96

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 50.0%** (เกณฑ์ต่ำสุด)
- **ไม่มีเกณฑ์ RRR** (ไม่บังคับ)
- **ไม่มีเกณฑ์ Count** (ไม่บังคับ)

**Timeframe:** 30min, 15min  
**History Bars:** 5000 bars

**เหตุผล:**
- Threshold ต่ำมาก (0.10%) เพราะทองมีความผันผวนสูง
- Fixed Threshold เพราะผลการทดสอบชัดเจน
- เกณฑ์แสดงผลต่ำสุด (Prob% >= 50% เท่านั้น)

**📈 ผลลัพธ์:** ผ่านเกณฑ์ 4/4 (100.0%)

---

### 🥈 SILVER (XAGUSD)

**Engine:** `MEAN_REVERSION`  
**Strategy:** Fade the move

**Threshold:**
- **30min:** 0.15% (0.0015) - Fixed
- **15min:** 0.20% (0.002) - Fixed
- **Backtest Results:**
  - 30min: 34 trades, Acc 61.8%, RR 1.01
  - 15min: 53 trades, RR 1.42

**เกณฑ์การแสดงผล (Metrics):**
- **Prob% >= 50.0%** (เกณฑ์ต่ำสุด)
- **ไม่มีเกณฑ์ RRR** (ไม่บังคับ)
- **ไม่มีเกณฑ์ Count** (ไม่บังคับ)

**Timeframe:** 30min, 15min  
**History Bars:** 5000 bars

**เหตุผล:**
- Threshold สูงกว่าทอง (0.15-0.20%) เพราะเงินมีความผันผวนสูงกว่า
- Fixed Threshold เพราะผลการทดสอบชัดเจน
- เกณฑ์แสดงผลต่ำสุด (Prob% >= 50% เท่านั้น)

**📈 ผลลัพธ์:** ผ่านเกณฑ์ 4/4 (100.0%)

---

## 🔍 สรุป Threshold

### Threshold จากสูง → ต่ำ:

1. **THAI:** 1.0% (สูงสุด - ความผันผวนต่ำ)
2. **SILVER 15M:** 0.20%
3. **SILVER 30M:** 0.15%
4. **GOLD:** 0.10%
5. **US/CHINA/TAIWAN:** 0.5% (ต่ำสุด - ความผันผวนสูง)

### Fixed vs Dynamic:

- **Fixed Threshold:** GOLD, SILVER (ผลการทดสอบชัดเจน)
- **Dynamic Threshold:** THAI, US, CHINA, TAIWAN (ปรับตาม Volatility)

---

## 📊 สรุปเกณฑ์การแสดงผล

### เกณฑ์เข้มงวดที่สุด → ง่ายที่สุด:

1. **THAI:** Prob% ≥60%, RRR ≥1.20, Count ≥30
2. **US/CHINA/TAIWAN:** Prob% ≥55%, RRR ≥1.20, Count ≥15
3. **METALS:** Prob% ≥50% (ไม่มีเกณฑ์ RRR/Count)

---

## 💡 ข้อสังเกต

1. **หุ้นไทย:** Threshold สูงสุด (1.0%) + เกณฑ์เข้มงวดที่สุด → เน้นคุณภาพ
2. **หุ้น US:** Threshold ต่ำ (0.5%) + ADX Filter → เน้น Trend ที่ชัดเจน
3. **หุ้นจีน/ไต้หวัน:** Threshold ต่ำ (0.5%) แต่ RRR เฉลี่ยต่ำ → ต้องปรับปรุง
4. **ทอง/เงิน:** Threshold ต่ำมาก (0.10-0.20%) + Fixed → เน้นความถี่

---

## 📝 หมายเหตุ

- **Dynamic Threshold:** คำนวณจาก Historical Volatility และ Stats
- **Fixed Threshold:** ใช้ค่าคงที่ตามผลการทดสอบ
- **ADX Filter:** ใช้เฉพาะ Trend Momentum Engine (US, TAIWAN)
- **เกณฑ์การแสดงผล:** ใช้ใน `calculate_metrics.py` เพื่อกรองหุ้นที่มีประสิทธิภาพ

