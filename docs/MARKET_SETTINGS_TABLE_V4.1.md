# 📊 ตารางสรุปการตั้งค่าตลาด V4.1

> **เวอร์ชัน**: 4.1  
> **วันที่**: 2026-02-14  
> **Repository**: [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

---

## 📋 ตารางสรุปการตั้งค่า (Overview Table)

| Market | Timeframe | Threshold | Strategy | Gatekeeper | Display Criteria |
|--------|-----------|-----------|----------|------------|------------------|
| **🇹🇭 THAI** | Daily | 1.0x SD (Floor 0.7%) | MEAN_REVERSION | Prob >= 53% | Prob >= 60% \| RRR >= 1.3 \| Count >= 30 |
| **🇺🇸 US** | Daily | 0.9x SD (Floor 0.6%) | US_HYBRID_VOL | Prob >= 52% | Prob >= 60% \| RRR >= 1.5 \| Count >= 15 |
| **🇨🇳 CHINA/HK** | Daily | 0.9x SD (Floor 0.5%) | MEAN_REVERSION | Prob >= 54% | Prob >= 60% \| RRR >= 1.2 \| Count >= 15 |
| **🇹🇼 TAIWAN** | Daily | 0.9x SD (Floor 0.5%) | REGIME_AWARE | Prob >= 51% | Prob >= 50% \| RRR >= 1.0 \| Count >= 15 |
| **🥇 GOLD 30M** | 30min | 0.60% (Fixed) | TREND_FOLLOWING | Prob >= 58% | Prob >= 40% \| RRR >= 0.75 \| Count >= 20 |
| **🥇 GOLD 15M** | 15min | 0.25% (Fixed) | TREND_FOLLOWING | Prob >= 50% | Prob >= 25% \| RRR >= 0.8 \| Count >= 20 |
| **🥈 SILVER 30M** | 30min | 0.25% (Fixed) | MEAN_REVERSION | Prob >= 58% | Prob >= 40% \| RRR >= 0.75 \| Count >= 20 |
| **🥈 SILVER 15M** | 15min | 0.60% (Fixed) | MEAN_REVERSION | Prob >= 60% | Prob >= 25% \| RRR >= 0.8 \| Count >= 20 |

---

## 📊 ตารางรายละเอียด (Detailed Table)

### 🇹🇭 THAI MARKET (Daily)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Dynamic | 1.0x SD (Multiplier), Floor 0.7% |
| **Threshold Calculation** | `max(20-day SD, 252-day SD) * 1.0` | Minimum 0.7% |
| **Min Stats** | 25 | Minimum pattern matches required |
| **Strategy** | MEAN_REVERSION | Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง) |
| **Gatekeeper** | Prob >= 53% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 60% \| RRR >= 1.3 \| Count >= 30 | Statistical significance (Central Limit Theorem) |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 5 days | Maximum holding period |
| - Trailing Stop | Enabled | Activate at 1.5%, Distance 50% |

---

### 🇺🇸 US MARKET (Daily)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Dynamic | 0.9x SD (Multiplier), Floor 0.6% |
| **Threshold Calculation** | `max(20-day SD, 252-day SD) * 0.9` | Minimum 0.6% |
| **Min Stats** | 20 | Minimum pattern matches required |
| **Strategy** | US_HYBRID_VOL | Hybrid Volatility Strategy |
| **Strategy Logic** | | |
| - HIGH_VOL (vol > avg_vol * 1.2) | REVERSION | Fade the spike |
| - LOW_VOL (vol <= avg_vol * 1.2) | TREND | Ride momentum |
| **Gatekeeper** | Prob >= 52% | Minimum probability to pass filter |
| **Quality Filter** | AvgWin > AvgLoss | Additional filter for US market |
| **Display Criteria** | Prob >= 60% \| RRR >= 1.5 \| Count >= 15 | Quality over quantity |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 5 days | Maximum holding period |
| - Trailing Stop | Enabled | Activate at 2.0%, Distance 40% |

---

### 🇨🇳 CHINA/HK MARKET (Daily)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Dynamic | 0.9x SD (Multiplier), Floor 0.5% |
| **Threshold Calculation** | `max(20-day SD, 252-day SD) * 0.9` | Minimum 0.5% |
| **Min Stats** | 30 | Minimum pattern matches required |
| **Strategy** | MEAN_REVERSION | Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง) |
| **Gatekeeper** | Prob >= 54% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 60% \| RRR >= 1.2 \| Count >= 15 | Quality over quantity |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 5 days | Maximum holding period |
| - Trailing Stop | Enabled | Activate at 2.0%, Distance 40% |

---

### 🇹🇼 TAIWAN MARKET (Daily)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Dynamic | 0.9x SD (Multiplier), Floor 0.5% |
| **Threshold Calculation** | `max(20-day SD, 252-day SD) * 0.9` | Minimum 0.5% |
| **Min Stats** | 25 | Minimum pattern matches required |
| **Strategy** | REGIME_AWARE | Regime-Aware Strategy |
| **Strategy Logic** | | |
| - BULL Market (Price > SMA50 > SMA200) | TREND | Follow momentum |
| - BEAR/SIDEWAYS Market | REVERSION | Fade the move |
| **Gatekeeper** | Prob >= 51% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 50% \| RRR >= 1.0 \| Count >= 15 | Realistic criteria for Taiwan market |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 5 days | Maximum holding period |
| - Trailing Stop | Enabled | Activate at 2.0%, Distance 40% |

---

### 🥇 GOLD (XAUUSD) - 30min Intraday

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Fixed | 0.60% (Fixed threshold) |
| **Min Stats** | 35 | Minimum pattern matches required |
| **Strategy** | TREND_FOLLOWING | Breakout Logic ตาม Session |
| **Strategy Logic** | | |
| - Pattern `+` | LONG | Follow momentum (Breakout) |
| - Pattern `-` | SHORT | Follow momentum (Breakdown) |
| **Gatekeeper** | Prob >= 58% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 40% \| RRR >= 0.75 \| Count >= 20 | Intraday has more noise |
| **Rolling Windows** | | |
| - Short Window | 48 bars | 1 วัน (24 ชั่วโมง / 30 นาที) |
| - Long Window | 336 bars | 1 สัปดาห์ (7 วัน * 48 bars/day) |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 48 bars | 1 วัน (24 ชั่วโมง) |
| - Trailing Stop | Enabled | Activate at 1.5%, Distance 50% |

---

### 🥇 GOLD (XAUUSD) - 15min Intraday

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Fixed | 0.25% (Fixed threshold) |
| **Min Stats** | 32 | Minimum pattern matches required |
| **Strategy** | TREND_FOLLOWING | Breakout Logic ตาม Session |
| **Strategy Logic** | | |
| - Pattern `+` | LONG | Follow momentum (Breakout) |
| - Pattern `-` | SHORT | Follow momentum (Breakdown) |
| **Gatekeeper** | Prob >= 50% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 25% \| RRR >= 0.8 \| Count >= 20 | 15min has more noise than 30min |
| **Rolling Windows** | | |
| - Short Window | 96 bars | 1 วัน (24 ชั่วโมง / 15 นาที) |
| - Long Window | 672 bars | 1 สัปดาห์ (7 วัน * 96 bars/day) |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 4.5x ATR (เพิ่ม RRR) |
| - RRR Theoretical | 4.5 | TP/SL ratio (เพิ่มจาก 3.5) |
| - Max Hold | 96 bars | 1 วัน (24 ชั่วโมง) |
| - Trailing Stop | Enabled | Activate at 1.5%, Distance 50% |

---

### 🥈 SILVER (XAGUSD) - 30min Intraday

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Fixed | 0.25% (Fixed threshold) |
| **Min Stats** | 35 | Minimum pattern matches required |
| **Strategy** | MEAN_REVERSION | Mean Reversion/Fakeout Logic |
| **Strategy Logic** | | |
| - Pattern `+` | SHORT | Fade the move (Fakeout) |
| - Pattern `-` | LONG | Fade the move (Fakeout) |
| **Gatekeeper** | Prob >= 58% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 40% \| RRR >= 0.75 \| Count >= 20 | Intraday has more noise |
| **Rolling Windows** | | |
| - Short Window | 48 bars | 1 วัน (24 ชั่วโมง / 30 นาที) |
| - Long Window | 336 bars | 1 สัปดาห์ (7 วัน * 48 bars/day) |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 48 bars | 1 วัน (24 ชั่วโมง) |
| - Trailing Stop | Enabled | Activate at 1.5%, Distance 50% |

---

### 🥈 SILVER (XAGUSD) - 15min Intraday

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Threshold Type** | Fixed | 0.60% (Fixed threshold) |
| **Min Stats** | 40 | Minimum pattern matches required |
| **Strategy** | MEAN_REVERSION | Mean Reversion/Fakeout Logic |
| **Strategy Logic** | | |
| - Pattern `+` | SHORT | Fade the move (Fakeout) |
| - Pattern `-` | LONG | Fade the move (Fakeout) |
| **Gatekeeper** | Prob >= 60% | Minimum probability to pass filter |
| **Display Criteria** | Prob >= 25% \| RRR >= 0.8 \| Count >= 20 | 15min has more noise than 30min |
| **Rolling Windows** | | |
| - Short Window | 96 bars | 1 วัน (24 ชั่วโมง / 15 นาที) |
| - Long Window | 672 bars | 1 สัปดาห์ (7 วัน * 96 bars/day) |
| **Risk Management** | | |
| - SL Type | ATR-based | 1.0x ATR |
| - TP Type | ATR-based | 3.5x ATR |
| - RRR Theoretical | 3.5 | TP/SL ratio |
| - Max Hold | 96 bars | 1 วัน (24 ชั่วโมง) |
| - Trailing Stop | Enabled | Activate at 1.5%, Distance 50% |

---

## 🔍 สรุป Strategy Logic

### MEAN_REVERSION (Thai, China/HK, Silver)
- **Logic**: Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง)
- **Direction**:
  - Pattern `+` (ขึ้นแรง) → SHORT (intended_dir = -1)
  - Pattern `-` (ลงแรง) → LONG (intended_dir = 1)

### TREND_FOLLOWING (Gold)
- **Logic**: Follow momentum (ซื้อเมื่อขึ้น, ขายเมื่อลง)
- **Direction**:
  - Pattern `+` (ขึ้นแรง) → LONG (intended_dir = 1)
  - Pattern `-` (ลงแรง) → SHORT (intended_dir = -1)

### US_HYBRID_VOL (US)
- **Logic**: Hybrid Volatility Strategy
- **HIGH_VOL** (current_vol > avg_vol * 1.2):
  - Pattern `+` → SHORT (REVERSION - fade the spike)
  - Pattern `-` → LONG (REVERSION - fade the spike)
- **LOW_VOL** (current_vol <= avg_vol * 1.2):
  - Pattern `+` → LONG (TREND - ride momentum)
  - Pattern `-` → SHORT (TREND - ride momentum)

### REGIME_AWARE (Taiwan)
- **Logic**: Regime-Aware Strategy
- **BULL Market** (Price > SMA50 > SMA200):
  - Pattern `+` → LONG (TREND - follow momentum)
  - Pattern `-` → SHORT (TREND - follow momentum)
- **BEAR/SIDEWAYS Market**:
  - Pattern `+` → SHORT (REVERSION - fade the move)
  - Pattern `-` → LONG (REVERSION - fade the move)

---

## 📈 สรุป Risk Management

### 🇹🇭 THAI MARKET

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (3.5x ATR) | **Max Hold**: 5 days | **Trailing**: Activate 1.5%, Distance 50%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based เพื่อยืดหยุ่นตามความผันผวน (หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ)
- **TP**: เป้าหมาย RRR 3.5 (สมดุลคุณภาพและจำนวน)
- **Max Hold**: ป้องกันการถือหุ้นนานเกินไป
- **Trailing**: Activate 1.5% (เร็ว) + Distance 50% เพราะ Mean Reversion → ราคากลับตัวเร็ว → ต้อง Lock กำไรเร็ว

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของหุ้นแต่ละตัว (หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ)
- **TP**: ATR-based (3.5x ATR)
  - **เหตุผล**: เป้าหมาย RRR 3.5 (ชนะได้กำไรมากกว่าขาดทุน 3.5 เท่า) - สมดุลระหว่างคุณภาพและจำนวน
- **Max Hold**: 5 days
  - **เหตุผล**: ป้องกันการถือหุ้นนานเกินไป (ถ้ายังไม่ถึง TP หรือ SL จะขายอัตโนมัติ)
- **Trailing**: Activate 1.5%, Distance 50%
  - **Activate 1.5%**: เปิดใช้งานเร็ว (เมื่อกำไรถึง 1.5%) เพื่อ Lock กำไรเร็ว
  - **Distance 50%**: Lock กำไร 50% ของจุดสูงสุด (สมดุลระหว่าง Lock กำไรและให้ราคาเคลื่อนไหว)
  - **เหตุผล**: THAI market ใช้ Mean Reversion → ราคามักจะกลับตัวเร็ว → ต้อง Lock กำไรเร็ว

### 🇺🇸 US STOCK

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (3.5x ATR) | **Max Hold**: 5 days | **Trailing**: Activate 2.0%, Distance 40%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based (เหมือน THAI) เพื่อยืดหยุ่นตามความผันผวน
- **TP**: เป้าหมาย RRR 3.5 แต่มี TP 5.0% (สูงกว่า THAI) เพื่อชดเชย Trailing Stop ที่ activate ช้า
- **Max Hold**: ป้องกันการถือหุ้นนานเกินไป
- **Trailing**: Activate 2.0% (ช้า) + Distance 40% เพราะ Hybrid Volatility → ราคาอาจเคลื่อนไหวต่อเนื่อง → ต้องให้มีเวลาไปถึง TP

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของหุ้นแต่ละตัว (เหมือน THAI)
- **TP**: ATR-based (3.5x ATR)
  - **เหตุผล**: เป้าหมาย RRR 3.5 (เหมือน THAI) - แต่ US market มี TP 5.0% (สูงกว่า THAI) เพื่อชดเชย Trailing Stop ที่ activate ช้า
- **Max Hold**: 5 days
  - **เหตุผล**: ป้องกันการถือหุ้นนานเกินไป (เหมือน THAI)
- **Trailing**: Activate 2.0%, Distance 40%
  - **Activate 2.0%**: เปิดใช้งานช้า (เมื่อกำไรถึง 2.0%) เพื่อให้มีเวลาไปถึง TP (5.0%)
  - **Distance 40%**: Lock กำไร 40% ของจุดสูงสุด (แน่นกว่า THAI ที่ 50%) เพื่อ Lock กำไรดีขึ้น
  - **เหตุผล**: US market ใช้ Hybrid Volatility Strategy → ราคาอาจเคลื่อนไหวต่อเนื่อง → ต้องให้มีเวลาไปถึง TP ก่อน Trailing Stop activate

### 🇨🇳 CHINA & HK MARKET

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (3.5x ATR) | **Max Hold**: 5 days | **Trailing**: Activate 2.0%, Distance 40%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based (เหมือน US) เพื่อยืดหยุ่นตามความผันผวน
- **TP**: เป้าหมาย RRR 3.5 (สมดุลคุณภาพและจำนวน)
- **Max Hold**: ป้องกันการถือหุ้นนานเกินไป
- **Trailing**: Activate 2.0% (ช้า) + Distance 40% เพราะ Mean Reversion แต่มี volatility สูง → ต้องให้มีเวลาไปถึง TP และ Lock กำไรดีขึ้น

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของหุ้นแต่ละตัว (เหมือน US)
- **TP**: ATR-based (3.5x ATR)
  - **เหตุผล**: เป้าหมาย RRR 3.5 (เหมือน US) - สมดุลระหว่างคุณภาพและจำนวน
- **Max Hold**: 5 days
  - **เหตุผล**: ป้องกันการถือหุ้นนานเกินไป (เหมือน US)
- **Trailing**: Activate 2.0%, Distance 40%
  - **Activate 2.0%**: เปิดใช้งานช้า (เมื่อกำไรถึง 2.0%) เพื่อให้มีเวลาไปถึง TP
  - **Distance 40%**: Lock กำไร 40% ของจุดสูงสุด (แน่นกว่า THAI ที่ 50%)
  - **เหตุผล**: CHINA/HK market ใช้ Mean Reversion แต่มี volatility สูง → ต้องให้มีเวลาไปถึง TP และ Lock กำไรดีขึ้น

### 🇹🇼 TAIWAN MARKET

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (3.5x ATR) | **Max Hold**: 5 days | **Trailing**: Activate 2.0%, Distance 40%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based (เหมือน US/CHINA) เพื่อยืดหยุ่นตามความผันผวน
- **TP**: เป้าหมาย RRR 3.5 แต่ Market RRR ต่ำ (0.87) → ต้องลดเกณฑ์ Display Criteria
- **Max Hold**: ป้องกันการถือหุ้นนานเกินไป
- **Trailing**: Activate 2.0% (ช้า) + Distance 40% เพราะ Regime-Aware → ราคาอาจเคลื่อนไหวต่อเนื่องใน BULL market → ต้องให้มีเวลาไปถึง TP

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของหุ้นแต่ละตัว (เหมือน US/CHINA)
- **TP**: ATR-based (3.5x ATR)
  - **เหตุผล**: เป้าหมาย RRR 3.5 (เหมือน US/CHINA) - แต่ Taiwan market มี RRR ต่ำ (Market RRR 0.87) → ต้องลดเกณฑ์ Display Criteria
- **Max Hold**: 5 days
  - **เหตุผล**: ป้องกันการถือหุ้นนานเกินไป (เหมือน US/CHINA)
- **Trailing**: Activate 2.0%, Distance 40%
  - **Activate 2.0%**: เปิดใช้งานช้า (เมื่อกำไรถึง 2.0%) เพื่อให้มีเวลาไปถึง TP
  - **Distance 40%**: Lock กำไร 40% ของจุดสูงสุด (แน่นกว่า THAI ที่ 50%)
  - **เหตุผล**: Taiwan market ใช้ Regime-Aware Strategy → ราคาอาจเคลื่อนไหวต่อเนื่องใน BULL market → ต้องให้มีเวลาไปถึง TP และ Lock กำไรดีขึ้น

### 🥇 METALS (30min)

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (3.5x ATR) | **Max Hold**: 48 bars (1 วัน) | **Trailing**: Activate 1.5%, Distance 50%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based (เหมือน Daily Markets) เพื่อยืดหยุ่นตามความผันผวน
- **TP**: เป้าหมาย RRR 3.5 (สมดุลคุณภาพและจำนวนสำหรับ intraday)
- **Max Hold**: 48 bars (1 วัน = 24 ชั่วโมง) เพราะ intraday ควรถือหุ้นไม่เกิน 1 วัน
  - **⚠️ สำหรับการเทรดจริง**: แนะนำลดเป็น 24-32 bars (12-16 ชั่วโมง) เพื่อหลีกเลี่ยง overnight risk
- **Trailing**: Activate 1.5% (เร็ว) + Distance 50% เพราะ intraday มี noise มาก → ต้อง Lock กำไรเร็ว

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของ Gold/Silver (เหมือน Daily Markets)
- **TP**: ATR-based (3.5x ATR)
  - **เหตุผล**: เป้าหมาย RRR 3.5 (เหมือน Daily Markets) - สมดุลระหว่างคุณภาพและจำนวนสำหรับ intraday
- **Max Hold**: 48 bars (1 วัน = 24 ชั่วโมง)
  - **เหตุผล**: Intraday ควรถือหุ้นไม่เกิน 1 วัน (30min = 48 bars/day) - ป้องกันการถือหุ้นนานเกินไป
  - **⚠️ หมายเหตุสำหรับการเทรดจริง**: 
    - Metals เป็นตลาด 24 ชั่วโมง แต่มี session ที่แตกต่างกัน (London, New York, Asian)
    - การถือหุ้นข้ามคืนมีความเสี่ยง (overnight risk, gap risk)
    - **แนะนำ**: ปิด position ก่อน session เปลี่ยนหรือลด Max Hold เป็น 24-32 bars (12-16 ชั่วโมง) เพื่อหลีกเลี่ยง overnight risk
- **Trailing**: Activate 1.5%, Distance 50%
  - **Activate 1.5%**: เปิดใช้งานเร็ว (เมื่อกำไรถึง 1.5%) เพื่อ Lock กำไรเร็ว
  - **Distance 50%**: Lock กำไร 50% ของจุดสูงสุด (สมดุลระหว่าง Lock กำไรและให้ราคาเคลื่อนไหว)
  - **เหตุผล**: Intraday มี noise มาก → ต้อง Lock กำไรเร็ว (เหมือน THAI)

### 🥇 METALS (15min)

**สรุป Risk Management:**
- **SL**: ATR-based (1.0x ATR) | **TP**: ATR-based (Gold: 4.5x, Silver: 3.5x) | **Max Hold**: 96 bars (1 วัน) | **Trailing**: Activate 1.5%, Distance 50%

**เหตุผลโดยย่อ:**
- **SL**: ใช้ ATR-based (เหมือน 30min) เพื่อยืดหยุ่นตามความผันผวน
- **TP**: Gold 4.5x (เพิ่ม RRR ให้ใกล้ 1.5), Silver 3.5x (สมดุลคุณภาพและจำนวน)
- **Max Hold**: 96 bars (1 วัน = 24 ชั่วโมง) เพราะ intraday ควรถือหุ้นไม่เกิน 1 วัน
  - **⚠️ สำหรับการเทรดจริง**: แนะนำลดเป็น 48-64 bars (12-16 ชั่วโมง) เพื่อหลีกเลี่ยง overnight risk
- **Trailing**: Activate 1.5% (เร็ว) + Distance 50% เพราะ 15min มี noise มากกว่า 30min → ต้อง Lock กำไรเร็ว

**รายละเอียด:**
- **SL**: ATR-based (1.0x ATR)
  - **เหตุผล**: ใช้ ATR-based เพื่อให้ยืดหยุ่นตามความผันผวนของ Gold/Silver (เหมือน 30min)
- **TP**: ATR-based
  - **Gold (XAUUSD)**: 4.5x ATR (เพิ่ม RRR)
    - **เหตุผล**: เพิ่ม TP จาก 3.5x → 4.5x เพื่อเพิ่ม RRR ให้ใกล้ 1.5 (ตามที่ user ต้องการ)
    - **RRR Theoretical**: 4.5 (ชนะได้กำไรมากกว่าขาดทุน 4.5 เท่า)
  - **Silver (XAGUSD)**: 3.5x ATR
    - **เหตุผล**: ใช้ค่าเดิม (3.5x) เพื่อสมดุลระหว่างคุณภาพและจำนวน
    - **RRR Theoretical**: 3.5 (ชนะได้กำไรมากกว่าขาดทุน 3.5 เท่า)
- **Max Hold**: 96 bars (1 วัน = 24 ชั่วโมง)
  - **เหตุผล**: Intraday ควรถือหุ้นไม่เกิน 1 วัน (15min = 96 bars/day) - ป้องกันการถือหุ้นนานเกินไป
  - **⚠️ หมายเหตุสำหรับการเทรดจริง**: 
    - Metals เป็นตลาด 24 ชั่วโมง แต่มี session ที่แตกต่างกัน (London, New York, Asian)
    - การถือหุ้นข้ามคืนมีความเสี่ยง (overnight risk, gap risk)
    - **แนะนำ**: ปิด position ก่อน session เปลี่ยนหรือลด Max Hold เป็น 48-64 bars (12-16 ชั่วโมง) เพื่อหลีกเลี่ยง overnight risk
- **Trailing**: Activate 1.5%, Distance 50%
  - **Activate 1.5%**: เปิดใช้งานเร็ว (เมื่อกำไรถึง 1.5%) เพื่อ Lock กำไรเร็ว
  - **Distance 50%**: Lock กำไร 50% ของจุดสูงสุด (สมดุลระหว่าง Lock กำไรและให้ราคาเคลื่อนไหว)
  - **เหตุผล**: 15min มี noise มากกว่า 30min → ต้อง Lock กำไรเร็ว (เหมือน 30min และ THAI)

---

## 📝 หมายเหตุ

1. **Threshold Calculation (Dynamic)**:
   - `effective_std = max(20-day SD, 252-day SD)`
   - `threshold = effective_std * multiplier`
   - `threshold = max(threshold, floor)`

2. **Rolling Windows (Intraday)**:
   - **30min**: Short 48 bars (1 วัน), Long 336 bars (1 สัปดาห์)
   - **15min**: Short 96 bars (1 วัน), Long 672 bars (1 สัปดาห์)

3. **Display Criteria**:
   - **Daily Markets**: Prob >= 50-60%, RRR >= 1.0-1.5, Count >= 15-30
   - **Intraday Metals**: Prob >= 25-40%, RRR >= 0.75-0.8, Count >= 20
   - Intraday มี noise มากกว่า daily → เกณฑ์ต่ำกว่า

4. **Strategy Rationale**:
   - **Gold**: Breakout Logic ตาม Session (Flow เงินเข้าชัดเจนช่วงเปิดตลาด)
   - **Silver**: Mean Reversion/Fakeout (High Volatility, False Break บ่อย)

5. **Max Hold สำหรับการเทรดจริง (Metals Intraday)**:
   - **ปัจจุบัน (Backtest)**: 
     - 30min: 48 bars (1 วัน = 24 ชั่วโมง)
     - 15min: 96 bars (1 วัน = 24 ชั่วโมง)
   - **⚠️ ปัญหาในการเทรดจริง**:
     - Metals เป็นตลาด 24 ชั่วโมง แต่มี session ที่แตกต่างกัน (London, New York, Asian)
     - การถือหุ้นข้ามคืนมีความเสี่ยง (overnight risk, gap risk)
     - Session เปลี่ยนอาจมี gap ราคา (price gap) ที่ทำให้ SL/TP ไม่ทำงานตามที่ตั้งไว้
   - **💡 แนะนำสำหรับการเทรดจริง**:
     - **30min**: ลด Max Hold เป็น **24-32 bars** (12-16 ชั่วโมง) หรือปิด position ก่อน session เปลี่ยน
     - **15min**: ลด Max Hold เป็น **48-64 bars** (12-16 ชั่วโมง) หรือปิด position ก่อน session เปลี่ยน
     - **Session Management**: ปิด position ก่อน London session ปิด (ประมาณ 22:00 GMT) หรือก่อน New York session ปิด (ประมาณ 21:00 EST)
     - **เหตุผล**: หลีกเลี่ยง overnight risk และ gap risk ที่อาจเกิดขึ้นเมื่อ session เปลี่ยน

6. **การวิเคราะห์ Max Hold ที่เหมาะสม (Holding Period Analysis)**:
   - **ใช้ Script**: `python scripts/calculate_metrics_streak.py`
   - **⚠️ สิ่งสำคัญ**: Script นี้ **ไม่ได้รัน backtest ใหม่** แต่ใช้ข้อมูลจาก CSV ที่มีอยู่แล้ว
   - **วิธีการทำงาน**:
     1. โหลดข้อมูลจาก `logs/trade_history_*.csv` (ข้อมูล trades ที่มีอยู่แล้ว)
     2. ดึงข้อมูลราคาเพิ่มเติม (historical price data) เพื่อคำนวณ returns สำหรับ N+1, N+3, N+5 days
     3. คำนวณ Win Rate, Avg Win, Avg Loss, RRR สำหรับแต่ละ holding period
   - **สิ่งที่วิเคราะห์**:
     - **Win Rate**: อัตราชนะในแต่ละ holding period
     - **Avg Win**: กำไรเฉลี่ยในแต่ละ holding period
     - **Avg Loss**: ขาดทุนเฉลี่ยในแต่ละ holding period
     - **RRR**: Risk-Reward Ratio ในแต่ละ holding period
   - **วิธีใช้ผลลัพธ์**:
     - ดูว่า holding period ไหนให้ **RRR สูงสุด** (เช่น N+3 หรือ N+5)
     - ดูว่า holding period ไหนให้ **Win Rate สูงสุด** (เช่น N+1)
     - หาจุดที่เหมาะสมระหว่าง RRR และ Win Rate
     - **ตัวอย่าง**: ถ้า N+3 ให้ RRR 2.0 และ Win Rate 60% → ควรตั้ง Max Hold = 3 days
   - **⚠️ หมายเหตุ**:
     - Script นี้วิเคราะห์ **Daily Markets** เท่านั้น (ไม่รองรับ Intraday Metals)
     - สำหรับ Intraday Metals ต้องใช้การวิเคราะห์แยก (ดูจาก backtest results)
     - ผลลัพธ์จาก script นี้ช่วย **ยืนยัน** ว่า Max Hold ที่ตั้งไว้เหมาะสมหรือไม่
     - **ต้องรัน backtest ก่อน**: ต้องมีไฟล์ `trade_history_*.csv` จาก backtest ก่อนรัน script นี้

7. **ความแตกต่างระหว่าง `calculate_metrics.py` และ `calculate_metrics_streak.py`**:
   - **ไม่ขัดแย้งกัน** แต่เป็น **การวิเคราะห์ที่แตกต่างกัน**:
   
   | Aspect | `calculate_metrics.py` | `calculate_metrics_streak.py` |
   |--------|------------------------|-------------------------------|
   | **ข้อมูลที่ใช้** | `actual_return` จาก CSV (มี Risk Management) | คำนวณ returns ใหม่ (ไม่มี Risk Management) |
   | **Risk Management** | ✅ มี (SL, TP, Trailing Stop, Max Hold) | ❌ ไม่มี (แค่ถือหุ้น N+1, N+3, N+5 days แล้วขาย) |
   | **วัตถุประสงค์** | แสดงผลลัพธ์จริงจากการเทรด | หา holding period ที่เหมาะสมที่สุด |
   | **Max Hold** | ใช้ Max Hold ที่ตั้งไว้ (5 days, 48 bars, 96 bars) | วิเคราะห์ N+1, N+3, N+5 days เพื่อหา Max Hold ที่ดีที่สุด |
   | **ผลลัพธ์** | Prob%, AvgWin%, AvgLoss%, RRR (จริง) | Win Rate, Avg Win, Avg Loss, RRR (ทฤษฎี) |
   
   - **สรุป**:
     - `calculate_metrics.py`: แสดงผลลัพธ์จริงจากการเทรด (มี Risk Management) → ใช้ดูผลลัพธ์จริง
     - `calculate_metrics_streak.py`: แสดงผลลัพธ์ทฤษฎี (ไม่มี Risk Management) → ใช้หาว่า Max Hold ควรเป็นเท่าไหร่
     - **ใช้ร่วมกัน**: ใช้ `calculate_metrics_streak.py` หา Max Hold ที่เหมาะสม แล้วตั้งใน backtest → ใช้ `calculate_metrics.py` ดูผลลัพธ์จริง

---

**Last Updated:** 2026-02-14  
**Version:** 4.1  
**Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

