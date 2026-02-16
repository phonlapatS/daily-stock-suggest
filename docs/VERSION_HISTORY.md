# Version History - Fractal N+1 Prediction System

> **Complete version history and evolution of the system with detailed explanations**

---

## 📊 Version Timeline

| Version | Codename | Date | Key Features | Status |
|---------|----------|------|--------------|--------|
| V1.0 | Foundation | 2025-12 | Basic Pattern Matching | ❌ Deprecated |
| V2.0 | Enhanced | 2026-01 | Multi-timeframe Support | ❌ Deprecated |
| V3.0 | Statistical | 2026-01 | Statistical Filtering | ❌ Deprecated |
| V3.1 | Strict | 2026-01 | Streak Logic + Thresholds | ❌ Deprecated |
| V3.2 | Scored | 2026-01 | Confidence & Risk Scoring | ❌ Deprecated |
| V3.3 | Metrics | 2026-02 | Performance Logging + 4-Table Report | ❌ Deprecated |
| V3.4 | Adaptive | 2026-02 | Dynamic Pattern + Cache System | ❌ Deprecated |
| V4.0 | Realtime Alert | 2026-02 | Real-time Alert Plan | ❌ Deprecated |
| V4.5 | Market-Specific | 2026-02 | Market-Specific Optimization | ❌ Deprecated |
| V6.0 | Indicator-based | 2026-02 | ADX, SMA50, Volume Ratio filters | ❌ Deprecated |
| V6.1 | Simplified | 2026-02 | Removed Indicator filters | ⚠️ Transition |
| V10.0 | Balanced Markets | 2026-02 | Market-specific parameters, Trailing Stop | ✅ Stable |
| V10.1 | All Markets Balanced | 2026-02 | Thai aligned with international, Trailing Stop ON | ✅ Stable |
| **V4.1** | **Production-Ready** | **2026-02** | **Production Mode, Enhanced RM, Transparent Display** | **✅ Stable** |
| V12.0 | Taiwan Optimization | 2026-02 | Taiwan-specific logic separation, increased signals | ✅ Stable |
| V12.1 | Taiwan Quality | 2026-02 | Improved RRR, balanced Count, quality focus | ✅ Stable |
| V12.2 | RRR Optimization | 2026-02 | Maximize RRR (SL 1.0%, TP 6.5%), longer hold | ✅ Stable |
| V12.3 | Count Optimization | 2026-02 | Lower min_prob (51.5%), increase n_bars (2500) | ✅ Stable |
| V12.4 | Real-World Ready | 2026-02 | Option A: RRR 1.25, Count 150 - Best for real trading | ✅ Stable |
| V13.0 | China Market Focus | 2026-02 | Lower RRR (1.0) and Prob (53%) - Increase tradable stocks | ✅ Stable |
| V13.1 | China Market - Increase Stocks | 2026-02 | Lower RRR (0.95) and Count (10), Optimize RM (TP 4.5%) | ✅ Stable |
| **V13.2** | **China Market - RM Optimization** | **2026-02** | **Tighten SL (1.2%), Increase TP (5.5%), Better RRR (4.58)** | **✅ Current** |

---

## 📖 Detailed Version Explanations

### V1.0 - Foundation (2025-12)
**แนวคิด:** ระบบพื้นฐาน Pattern Matching

**สิ่งที่ทำ:**
- Pattern Matching แบบง่ายๆ
- ทายทิศทางราคาวันถัดไป

**ข้อดี:**
- ✅ เรียบง่าย เข้าใจง่าย
- ✅ เริ่มต้นได้เร็ว

**ข้อเสีย:**
- ❌ ไม่มี Filter
- ❌ ไม่มี Risk Management
- ❌ ไม่มีสถิติที่เชื่อถือได้

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่ซับซ้อนและเชื่อถือได้มากขึ้น

---

### V2.0 - Enhanced (2026-01)
**แนวคิด:** เพิ่ม Multi-timeframe Support

**สิ่งที่ทำ:**
- รองรับหลาย Timeframe
- ขยายตลาดที่รองรับ

**ข้อดี:**
- ✅ ยืดหยุ่นมากขึ้น
- ✅ รองรับตลาดหลายแบบ

**ข้อเสีย:**
- ❌ ยังไม่มี Filter ที่ดี
- ❌ Logic ยังไม่เข้มงวด

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่เข้มงวดและแม่นยำมากขึ้น

---

### V3.0 - Statistical (2026-01)
**แนวคิด:** เพิ่ม Statistical Filtering

**สิ่งที่ทำ:**
- เพิ่มการกรองด้วยสถิติ
- ใช้ Threshold แบบ Dynamic

**ข้อดี:**
- ✅ มี Filter แล้ว
- ✅ ใช้สถิติในการตัดสินใจ

**ข้อเสีย:**
- ❌ Logic ยังไม่เข้มงวด (Flexible Logic - ข้ามวัน FLAT ได้)
- ❌ Probability Calculation ยังมีปัญหา (รวม FLAT days)

**ทำไมถึงเปลี่ยน:** ต้องการ Logic ที่เข้มงวดและแม่นยำมากขึ้น

---

### V3.1 - Strict (2026-01)
**แนวคิด:** ใช้ Strict Logic + แก้ไข Probability Calculation

**สิ่งที่ทำ:**
- **Strict Logic:** วันไหนไม่เกิน threshold → streak ขาดทันที (ไม่ข้าม FLAT)
- **แก้ไข Probability:** `Prob = dominant / (up + down)` ไม่รวม FLAT
- เพิ่ม Avg_Return และ Avg_Intensity metrics
- Unified Report Tool

**ข้อดี:**
- ✅ Logic เข้มงวด → แม่นยำมากขึ้น
- ✅ Prob >= 50% เสมอ (ไม่สับสน)
- ✅ มี Metrics เพิ่มเติม (Avg_Return, Avg_Intensity)

**ข้อเสีย:**
- ⚠️ เข้มงวดเกินไป → สัญญาณน้อยลง
- ⚠️ อาจพลาดโอกาสบางอย่าง

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่ยืดหยุ่นและครอบคลุมมากขึ้น

---

### V3.2 - Scored (2026-01)
**แนวคิด:** เพิ่ม Confidence & Risk Scoring

**สิ่งที่ทำ:**
- เพิ่มระบบให้คะแนนความเชื่อมั่น
- เพิ่มระบบให้คะแนนความเสี่ยง

**ข้อดี:**
- ✅ มีระบบให้คะแนน
- ✅ ช่วยตัดสินใจได้ดีขึ้น

**ข้อเสีย:**
- ⚠️ ซับซ้อนมากขึ้น
- ⚠️ อาจ Over-engineer

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่เรียบง่ายและมีประสิทธิภาพมากขึ้น

---

### V3.3 - Metrics (2026-02)
**แนวคิด:** เพิ่ม Performance Logging + 4-Table Report

**สิ่งที่ทำ:**
- Performance Logging
- 4-Table Report System:
  - Table 1: Thai Strict (Prob > 60%, RR > 2.0)
  - Table 2: Thai Balanced (Prob > 60%, 1.5 < RR ≤ 2.0)
  - Table 3: International Observation (Prob > 55%, RR > 1.1)
  - Table 4: International Sensitivity (Prob > 50%, 0.5 < RR ≤ 1.1)

**ข้อดี:**
- ✅ มี Performance Logging
- ✅ มี 4-Table Report ที่ชัดเจน
- ✅ แบ่งหุ้นตามคุณภาพ

**ข้อเสีย:**
- ⚠️ ยังใช้ Fixed Pattern (4 วัน)
- ⚠️ ไม่มี Cache System → ช้า

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่ Adaptive และเร็วขึ้น

---

### V3.4 - Adaptive (2026-02)
**แนวคิด:** Dynamic Pattern Detection + Cache System

**สิ่งที่ทำ:**
- **Dynamic Pattern:** Scan pattern lengths 3-8 days (ไม่ใช่ Fixed 4 วัน)
- **Smart Cache System:** ลด API calls 99% (5000 bars → 50 bars)
- Adaptive Split สำหรับหุ้นใหม่ (IPO)

**ข้อดี:**
- ✅ Adaptive → หา Pattern ที่เหมาะสมที่สุด
- ✅ เร็วขึ้นมาก (Cache System)
- ✅ รองรับหุ้นใหม่

**ข้อเสีย:**
- ⚠️ ยังไม่มี Market-Specific Logic
- ⚠️ ยังไม่มี Risk Management ที่ดี

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่ปรับแต่งตามตลาดและมี Risk Management ที่ดีขึ้น

---

### V4.0 - Realtime Alert (2026-02)
**แนวคิด:** Real-time Alert Plan

**สิ่งที่ทำ:**
- วางแผนระบบ Real-time Alert

**ข้อดี:**
- ✅ มีแผนสำหรับ Real-time

**ข้อเสีย:**
- ⚠️ ยังไม่ได้ Implement จริง
- ⚠️ ยังไม่มี Market-Specific Logic

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่ปรับแต่งตามตลาดจริงๆ

---

### V4.5 - Market-Specific (2026-02)
**แนวคิด:** Market-Specific Optimization + Smart Filters

**สิ่งที่ทำ:**
- **Market-Specific Thresholds:**
  - Thai: 1.0% (Mean Reversion)
  - US: 0.6% (Trend Following)
  - China: 0.5% (ลดจาก 1.2% → Early Entry)
  - Taiwan: 0.5% (ลดจาก 1.0% → Accumulation)
- **Smart Filters:**
  - China: SMA50 + FOMO Filter (Volume Ratio < 3.0)
  - Taiwan: ADX > 20
  - US: ADX > 20 + Quality Gate (Prob >= 60%)

**ข้อดี:**
- ✅ ปรับแต่งตามตลาด → เข้าได้ต้นน้ำ (Early Entry)
- ✅ มี Smart Filters → คุณภาพสูง
- ✅ คุมความเสี่ยงได้ดี

**ข้อเสีย:**
- ⚠️ **ซับซ้อนมาก** → ใช้ Indicator หลายตัว
- ⚠️ **ไม่ตรงกับแนวคิดระบบในตอนแรก** → ระบบควรเป็น Pure Statistics ไม่ใช่ Indicator-based
- ⚠️ **ยากต่อการดูแลรักษา** → Logic ซับซ้อน

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่เรียบง่ายและเน้น Pure Statistics ตามแนวคิดเดิม

---

### V6.0 - Indicator-based (2026-02)
**แนวคิด:** ใช้ Indicator เป็น Filter (ต่อจาก V4.5)

**สิ่งที่ทำ:**
- **ADX Filter:** ADX >= 20 (มี trend ชัดเจน)
- **SMA50 Filter:** Price > SMA50 (Bull market)
- **Volume Ratio Filter:** VR > 0.5 (มี volume)
- Trailing Stop Loss
- Take Profit

**ข้อดี:**
- ✅ **กรองข้อมูลได้ดีจริง** → คุณภาพสูง
- ✅ มี Risk Management (Trailing Stop, Take Profit)

**ข้อเสีย:**
- ❌ **ไม่ตรงกับแนวคิดระบบในตอนแรก** → ระบบควรเป็น Pure Statistics (Pattern Matching + History Statistics) ไม่ใช่ Indicator-based
- ❌ **ซับซ้อนเกินไป** → ใช้ Indicator หลายตัว
- ❌ **ยากต่อการดูแลรักษา** → Logic ซับซ้อน
- ❌ **ไม่ Balance** → อาจพลาดโอกาสบางอย่างเพราะ Filter เข้มงวดเกินไป

**ทำไมถึงเปลี่ยน:** ต้องการกลับไปใช้ระบบที่เรียบง่ายและเน้น Pure Statistics ตามแนวคิดเดิม

---

### V6.1 - Simplified (2026-02)
**แนวคิด:** กลับไปใช้ระบบเดิมที่เรียบง่าย (Pure Statistics)

**สิ่งที่ทำ:**
- **ลบ Indicator Filters ทั้งหมด:**
  - ❌ ADX Filter
  - ❌ SMA50 Filter
  - ❌ Volume Ratio Filter
  - ❌ RSI
- **ลบ Exit Strategy ที่ซับซ้อน:**
  - ❌ Trailing Stop Loss
  - ❌ Take Profit
  - ❌ ATR Multiplier
  - ❌ Max Hold Days
- **กลับไปใช้:**
  - ✅ Pattern Matching จาก History Statistics
  - ✅ 1-Day Exit (N+1)
  - ✅ Gatekeeper: Prob > 60% และ RRR > 1.2

**ข้อดี:**
- ✅ **เรียบง่าย** → เข้าใจง่าย ดูแลรักษาง่าย
- ✅ **ตรงกับแนวคิดระบบ** → Pure Statistics (Pattern Matching + History Statistics)
- ✅ **ไม่ซับซ้อน** → ไม่ใช้ Indicator

**ข้อเสีย:**
- ⚠️ **ไม่มี Risk Management** → ไม่มี Stop Loss, Take Profit, Trailing Stop
- ⚠️ **อาจขาดทุนมาก** → ถ้าไม่มี Risk Management

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่มี Risk Management ที่ดี แต่ยังคงเรียบง่ายและเน้น Pure Statistics

---

### V10.0 - Balanced Markets (2026-02)
**แนวคิด:** Market-Specific Parameters + Risk Management

**สิ่งที่ทำ:**
- **Market-Specific Parameters:**
  - Threshold multiplier: 0.9 for international (was 1.25)
  - 10-13x more trades with minimal accuracy loss
- **Risk Management:**
  - Trailing Stop enabled
  - Stop Loss, Take Profit (market-specific)

**ข้อดี:**
- ✅ **Balance** → มีสัญญาณมากขึ้น (10-13x) แต่ยังแม่นยำ
- ✅ **มี Risk Management** → Trailing Stop, Stop Loss, Take Profit
- ✅ **Market-Specific** → ปรับแต่งตามตลาด

**ข้อเสีย:**
- ⚠️ **Thai ยังไม่ Balance** → ยังใช้ threshold_multiplier 1.25 (สูงเกินไป)

**ทำไมถึงเปลี่ยน:** ต้องการให้ Thai Balance เหมือน International

---

### V10.1 - All Markets Balanced (2026-02)
**แนวคิด:** Thai Aligned with International + Trailing Stop ON

**สิ่งที่ทำ:**
- **Thai Parameters (Aligned with International):**
  - threshold_multiplier: 1.25 → 1.0 (เพิ่มสัญญาณ)
  - floor: 1.0% → 0.7% (เพิ่มสัญญาณ)
  - min_stats: 30 → 25 (เพิ่มสัญญาณ)
  - gatekeeper Prob: 55% → 53% (เพิ่มสัญญาณ)
- **Risk Management:**
  - Thai RM SL: 2.0% → 1.5%, TP: 4.0% → 3.5% (Aligned with International)
  - Trailing Stop: Enabled for all markets

**ข้อดี:**
- ✅ **Balance** → Thai มีสัญญาณมากขึ้น (10-13x) แต่ยังแม่นยำ
- ✅ **All Markets Aligned** → ใช้ Logic เดียวกัน
- ✅ **Risk Management ครบถ้วน** → Trailing Stop, Stop Loss, Take Profit

**ข้อเสีย:**
- ⚠️ **ยังไม่มี Production Mode** → Backtest ยัง Ideal (ไม่มี Slippage, Commission)

**ทำไมถึงเปลี่ยน:** ต้องการระบบที่พร้อมใช้งานจริง (Production-Ready)

---

### V4.1 - Production-Ready (2026-02-14) ⭐ CURRENT
**แนวคิด:** Production-Ready Risk Management System

**สิ่งที่ทำ:**
- **Production Mode:**
  - Entry at next bar's OPEN (realistic) instead of current close (ideal)
  - Slippage (market-specific)
  - Commission (market-specific)
  - Gap Risk (Stop Loss can be worse due to gap)
  - Liquidity Filter (skip low-volume days)
- **Enhanced Display:**
  - Count prominent (Width 12, Comma formatting)
  - All passing stocks displayed (No .head() limit)
  - Sorting by Prob% (Descending)
- **Statistical Reliability:**
  - Count >= 30 for THAI (Central Limit Theorem)
  - Count >= 15 for US/CHINA/TAIWAN (Acceptable)
- **Intraday Metals Support (NEW):**
  - Gold & Silver 15min/30min with separated logic
  - Gold: TREND_FOLLOWING (Breakout Logic)
  - Silver: MEAN_REVERSION (Fakeout Logic)
  - Separated rolling windows and max_hold for 15min and 30min
  - Market-specific min_prob, min_stats, and fixed_threshold
  - Separate display criteria for 15min and 30min

**ข้อดี:**
- ✅ **Production-Ready** → Backtest สะท้อนความเป็นจริง (Slippage, Commission, Gap Risk)
- ✅ **Transparent Display** → Count เด่นชัด, แสดงหุ้นทั้งหมด
- ✅ **Statistical Reliability** → Count >= 30 for THAI (Central Limit Theorem)
- ✅ **Balance** → มีสัญญาณมากขึ้น แต่ยังแม่นยำ
- ✅ **Risk Management ครบถ้วน** → Trailing Stop, Stop Loss, Take Profit, Position Sizing
- ✅ **ตรงกับแนวคิดระบบ** → Pure Statistics (Pattern Matching + History Statistics) + Risk Management
- ✅ **Intraday Metals Support** → Gold & Silver 15min/30min with separated logic

**ข้อเสีย:**
- ⚠️ **US/CHINA/TAIWAN Count >= 15** → ต่ำกว่า 30 (Central Limit Theorem) แต่ยังใช้ได้
- ⚠️ **Taiwan ยังใช้ SMA50/SMA200** → ไม่ใช่ Filter แต่ใช้กำหนด Direction (Regime-Aware Strategy)
- ⚠️ **Metals 15min Prob% threshold ต่ำ (25%)** → เนื่องจาก intraday มี noise มาก

**ทำไมถึงเป็น Current:** ระบบ Balance, Production-Ready, และตรงกับแนวคิดระบบ (Pure Statistics + Risk Management) + รองรับ Intraday Metals

**Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

---

### V12.0 - Taiwan Optimization (2026-02)
**แนวคิด:** แยก Logic ไต้หวันออกจาก US/China + เพิ่มสัญญาณ

**สิ่งที่ทำ:**
- **แยก Logic ไต้หวัน:**
  - แยก `is_tw_market_early` และ `is_tw_market` จาก US/China
  - Logic แยกชัดเจน → Maintain ง่ายขึ้น
- **Parameters (เพิ่มสัญญาณ):**
  - threshold_multiplier: 0.9 → 0.85 (เพิ่มสัญญาณ)
  - min_stats: 25 → 20 (เพิ่ม patterns)
  - floor: 0.5% → 0.4% (เพิ่มสัญญาณ)
  - prob filter: 53% → 51% (เพิ่มหุ้นที่ผ่าน)
  - TP: 3.5% → 4.0% (RRR 2.67, ชดเชย commission 0.44%)
- **เกณฑ์ใน calculate_metrics:**
  - Prob >= 50%, RRR >= 1.05, Count >= 15

**ผลลัพธ์:**
- ✅ มีหุ้นผ่านเกณฑ์ 4 ตัว (เดิม: 0 ตัว)
- ✅ แยก Logic ชัดเจน → Maintain ง่ายขึ้น
- ✅ เพิ่มสัญญาณได้จริง

**ข้อเสีย:**
- ⚠️ RRR ต่ำเกินไป (1.05-1.19) → ไม่คุ้มเสี่ยง
- ⚠️ Count ไม่สมดุล (20-327) → บางตัวน้อยเกินไป บางตัวเยอะเกินไป

**ทำไมถึงเปลี่ยน:** ต้องการ RRR ที่ดีขึ้นและ Count ที่สมดุล

---

### V12.1 - Taiwan Quality (2026-02) ⭐ CURRENT
**แนวคิด:** Quality over Quantity - ปรับ RRR ให้ดีขึ้น + Count สมดุล

**สิ่งที่ทำ:**
- **Risk Management (ปรับ RRR):**
  - SL: 1.5% → 1.2% (tight SL)
  - TP: 4.0% → 5.0% (RRR 4.17)
  - Max Hold: 5 → 7 วัน (ให้มีเวลาไปถึง TP)
  - Trail Activate: 1.5% → 1.0% (activate เร็วขึ้น)
  - Trail Distance: 50% → 40% (lock in กำไรมากขึ้น)
- **Parameters (เพิ่มคุณภาพ):**
  - threshold_multiplier: 0.85 → 0.9 (ลดสัญญาณ, เพิ่มคุณภาพ)
  - min_stats: 20 → 25 (ลด patterns, เพิ่มคุณภาพ)
  - prob filter: 51% → 53% (เพิ่มคุณภาพสัญญาณ)
- **เกณฑ์ใน calculate_metrics:**
  - Prob >= 53%, RRR >= 1.3, Count 25-150

**ผลลัพธ์ที่คาดหวัง:**
- ✅ RRR ดีขึ้น (>= 1.3) → คุ้มเสี่ยงมากขึ้น
- ✅ Count สมดุล (25-150) → ไม่น้อยเกินไป ไม่เยอะเกินไป
- ✅ คุณภาพดีขึ้น (Prob >= 53%, RRR >= 1.3)

**ข้อดี:**
- ✅ RRR ดีขึ้นมาก (4.17 จาก RM) → ชดเชย commission 0.44% ได้ดี
- ✅ Count สมดุล (25-150) → ไม่น้อยเกินไป ไม่เยอะเกินไป
- ✅ คุณภาพดีขึ้น (Prob >= 53%, RRR >= 1.3)

**ข้อเสีย:**
- ⚠️ ยังต้องทดสอบ → ต้องรอผล backtest

**ทำไมถึงเป็น Current:** ปรับ RRR ให้ดีขึ้นและ Count สมดุล เน้นคุณภาพมากกว่าปริมาณ

---

## 🔄 Major Philosophy Shifts

### V4.5/V6.0 → V6.1: Indicator Removal
**Before:** ใช้ Indicator เป็น Filter (ADX, SMA50, Volume Ratio)  
**After:** ลบ Indicator ทั้งหมด เน้น Pure Statistics (Pattern Matching + History Statistics)  
**Reason:** 
- ระบบควรเป็น Pure Statistics ตามแนวคิดเดิม
- Indicator ซับซ้อนเกินไป ดูแลรักษายาก
- ไม่ Balance → กรองข้อมูลได้ดีจริงแต่พลาดโอกาสบางอย่าง

### V6.1 → V10.1: Risk Management Emphasis
**Before:** ไม่มี Risk Management (1-Day Exit เท่านั้น)  
**After:** Risk Management ครบถ้วน (Stop Loss, Take Profit, Trailing Stop, Position Sizing)  
**Reason:** 
- ป้องกัน Loss (Stop Loss)
- รับกำไร (Take Profit)
- ป้องกันกำไร (Trailing Stop)
- ควบคุม Risk (Position Sizing)

### V10.1 → V4.1: Production-Ready
**Before:** Ideal backtest (ไม่มี Slippage, Commission, Gap Risk)  
**After:** Production Mode (Slippage, Commission, Gap Risk, Liquidity Filter)  
**Reason:** 
- Backtest ควรสะท้อนความเป็นจริง
- Production Mode ช่วยให้เห็นผลลัพธ์ที่แท้จริง

---

## 📊 Comparison Table

| Version | Philosophy | Complexity | Balance | Risk Management | Production-Ready |
|---------|------------|------------|---------|-----------------|-----------------|
| V3.1 | Strict Logic | Low | ⚠️ Low (เข้มงวดเกินไป) | ❌ None | ❌ No |
| V4.5 | Indicator-based | High | ⚠️ Medium (กรองดีแต่พลาดโอกาส) | ✅ Basic | ❌ No |
| V6.0 | Indicator-based | High | ⚠️ Low (กรองดีแต่ไม่ Balance) | ✅ Good | ❌ No |
| V6.1 | Pure Statistics | Low | ⚠️ Medium (เรียบง่ายแต่ไม่มี RM) | ❌ None | ❌ No |
| V10.0 | Balanced | Medium | ✅ Good | ✅ Good | ❌ No |
| V10.1 | Balanced | Medium | ✅ Good | ✅ Excellent | ❌ No |
| **V4.1** | **Pure Stats + RM** | **Medium** | **✅ Excellent** | **✅ Excellent** | **✅ Yes** |

---

## 🎯 Current System (V4.1)

### Core Logic
- **Pattern Matching:** 3-8 days (Dynamic)
- **Threshold:** Market-specific (Thai: 1.0x, US: 0.9x, TW/CN: 0.9x)
- **Statistics:** History-based (Prob, AvgWin, AvgLoss, RRR)

### Risk Management
- **Stop Loss:** 1.5-2.0% (Fixed, market-specific)
- **Take Profit:** 3.5-5.0% (Fixed, market-specific)
- **Trailing Stop:** Enabled (Activate at 1.5%, Keep 50% of peak)
- **Position Sizing:** Based on Prob% and RRR
- **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter

### Display Criteria
- **THAI:** Prob >= 60%, RRR >= 1.2, Count >= 30
- **US:** Prob >= 55%, RRR >= 1.2, Count >= 15
- **CHINA/HK:** Prob >= 55%, RRR >= 1.2, Count >= 15
- **TAIWAN (V12.2):** Prob >= 53%, RRR >= 1.3, Count 25-150

---

## 📚 Documentation

### Version-Specific Documents
- [V4.1_UPDATE_LOG.md](V4.1_UPDATE_LOG.md) - Current version
- [V4.5_UPDATE_LOG.md](V4.5_UPDATE_LOG.md) - V4.5 details
- [V3.1_UPDATE_LOG.md](V3.1_UPDATE_LOG.md) - V3.1 details
- [V3.4_ROADMAP.md](V3.4_ROADMAP.md) - V3.4 roadmap

### System Documents
- [PROJECT_MASTER_MANUAL.md](PROJECT_MASTER_MANUAL.md) - Main manual
- [SYSTEM_WORKFLOW.md](SYSTEM_WORKFLOW.md) - Workflow
- [SIMPLIFIED_SYSTEM_V6.1.md](SIMPLIFIED_SYSTEM_V6.1.md) - V6.1 details
- [INDICATOR_FILTERS_ARCHIVE.md](INDICATOR_FILTERS_ARCHIVE.md) - Indicator archive

---

## 💡 Key Lessons Learned

1. **Balance is Key:** ระบบที่เข้มงวดเกินไป (V3.1, V6.0) → สัญญาณน้อย แต่ระบบที่ง่ายเกินไป (V6.1) → ไม่มี Risk Management
2. **Pure Statistics > Indicators:** ระบบ Pure Statistics (V4.1) ดีกว่า Indicator-based (V4.5, V6.0) เพราะตรงกับแนวคิดระบบและดูแลรักษาง่าย
3. **Risk Management is Essential:** ระบบที่ไม่มี Risk Management (V6.1) → อาจขาดทุนมาก
4. **Production Mode Matters:** Backtest ควรสะท้อนความเป็นจริง (V4.1) ไม่ใช่ Ideal (V10.1)

---

---

## 📝 Taiwan Market Evolution (V12.0 → V12.1 → V12.2)

### V12.0 - Taiwan Optimization
- **Goal:** เพิ่มสัญญาณ, แยก logic
- **Result:** 4 stocks passing
- **หุ้นที่ดีที่สุด:**
  - DELTA (2308): Prob 70.0%, RRR 1.19, Count 20
  - LARGAN (3008): Prob 61.2%, RRR 1.10, Count 327
  - MEDIATEK (2454): Prob 55.0%, RRR 1.08, Count 40
  - QUANTA (2382): Prob 51.0%, RRR 1.36, Count 51
- **Issue:** RRR ต่ำ, Count ไม่สมดุล

### V12.1 - Taiwan Quality
- **Goal:** เพิ่ม RRR, Count สมดุล, คุณภาพดีขึ้น
- **Result:** 1 stock passing (คุณภาพดี)
- **หุ้นผ่านเกณฑ์:**
  - MEDIATEK (2454): Prob 62.5%, RRR 1.45, Count 40
- **Total Trades:** 2,129
- **Avg RRR:** 1.15
- **Issue:** เกณฑ์เข้มเกินไป, หุ้นผ่านน้อย

### V12.2 - RRR Optimization
- **Goal:** เพิ่ม RRR ก่อน แล้วค่อยเพิ่ม Count
- **Changes:**
  - SL: 1.2% → 1.0% (tighter)
  - TP: 5.0% → 6.5% (wider)
  - Max Hold: 7 → 10 วัน
  - Trail Distance: 40% → 30% (let profits run)
  - Prob Filter: 53% → 52%
- **Result:** 2 stocks passing, RRR 1.76 (ดีขึ้นมาก!)
- **หุ้นผ่านเกณฑ์:**
  - MEDIATEK (2454): Prob 62.5%, RRR 1.76, Count 40
  - HON-HAI (2317): Prob 62.3%, RRR 1.42, Count 69

---

### V12.3 - Count Optimization
- **Goal:** เพิ่ม Count โดยไม่ลด Prob และ RRR
- **Changes:**
  - min_prob: 52.0% → 51.5% (เพิ่ม trades)
  - n_bars: 2000 → 2500 (เพิ่ม historical data)
- **Result:** 2 stocks passing (DELTA, HON-HAI)
- **หุ้นผ่านเกณฑ์:**
  - DELTA (2308): Prob 70.9%, RRR 1.89, Count 55
  - HON-HAI (2317): Prob 61.5%, RRR 1.31, Count 96
- **Note:** HON-HAI ไม่ผ่านเกณฑ์ (RRR 1.31 < 1.3)

---

### V12.4 - Real-World Ready ⭐ CURRENT
- **Goal:** เพิ่มหุ้นที่เทรดได้ตามที่ mentor ขอ + หาตัวเลือกที่เหมาะสมสำหรับการเทรดจริง
- **Changes:**
  - min_prob: 51.5% → 51.0% (เพิ่มหุ้นที่เทรดได้)
  - RRR Requirement: 1.3 → 1.25 (เพิ่มหุ้นที่เทรดได้)
  - n_bars: 2500 (คงเดิม)
- **Testing:**
  - Tested Option 3 (RRR 1.15, Count 300): ❌ ไม่เพิ่มหุ้น
  - Tested Option B (RRR 1.25, Count 400): ⚠️ เพิ่มหุ้นได้แต่ over-trading risk สูง
  - **Final Decision: Option A (RRR 1.25, Count 150)** - Best for real trading
- **Result:** **2 stocks passing (DELTA, QUANTA)**
- **หุ้นผ่านเกณฑ์:**
  - DELTA (2308): Prob 71.4%, RRR 1.95, Count 35
  - QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96
- **Average Metrics:**
  - Avg Prob%: 66.95% ✅
  - Avg RRR: 1.68 ✅
  - Avg Count: 65.5 ✅
  - Total Trades: 131
- **Real-World Analysis:**
  - Commission Cost: 37.33% (ต่ำ)
  - Over-trading Risk: 0% (ไม่มีหุ้นที่ Count > 200)
  - Quality: สูง (Prob 66.95%, RRR 1.68)
- **Success:** ✅ เหมาะสำหรับการเทรดจริง - คุณภาพดี, ปลอดภัย, ค่าคอมต่ำ

---

### V13.0 - China Market Focus ⭐ CURRENT
- **Goal:** โฟกัสที่ตลาดหุ้นจีนเป็นหลัก - เพิ่มหุ้นที่เทรดได้
- **Changes:**
  - Prob Requirement: 55% → 53% (เพิ่มหุ้นที่เทรดได้)
  - RRR Requirement: 1.2 → 1.0 (เพิ่มหุ้นที่เทรดได้)
  - Count Requirement: >= 15 (คงเดิม)
- **Result:** **3 stocks passing (เพิ่มจาก 1 → 3)**
- **หุ้นผ่านเกณฑ์:**
  - MEITUAN (3690): Prob 76.9%, RRR 1.22, Count 39
  - BYD (1211): Prob 59.1%, RRR 1.00, Count 159
  - JD-COM (9618): Prob 54.2%, RRR 1.20, Count 24
- **Average Metrics:**
  - Avg Prob%: 63.4%
  - Avg RRR: 1.14
  - Avg Count: 74
  - Total Trades: 222
- **Success:** ✅ เพิ่มหุ้นที่เทรดได้ (1 → 3) - Focus on China market

---

### V13.1 - China Market - Increase Stocks ⭐ CURRENT
- **Goal:** เพิ่มหุ้นที่เทรดได้ - ลด RRR และ Count requirement + ปรับ RM
- **Changes:**
  - Display Criteria:
    - RRR >= 1.0 → 0.95 (เพิ่มหุ้นที่เทรดได้)
    - Count >= 15 → 10 (เพิ่มหุ้นที่เทรดได้)
  - Risk Management:
    - TP: 3.5% → 4.5% (เพิ่ม RRR)
    - Max Hold: 5 → 6 days (ให้เวลาไปถึง TP)
    - RRR: 2.33 → 3.0 (theoretical)
  - Gatekeeper:
    - min_prob: 53.0% → 51.0% (เพิ่ม Count)
- **Result:** **4 stocks passing (เพิ่มจาก 3 → 4)**
- **หุ้นผ่านเกณฑ์:**
  - LI-AUTO (2015): Prob 80.0%, RRR 1.00, Count 10 ⚠️ Count ต่ำ
  - MEITUAN (3690): Prob 76.9%, RRR 1.22, Count 39
  - BYD (1211): Prob 59.1%, RRR 1.00, Count 159
  - JD-COM (9618): Prob 54.2%, RRR 1.20, Count 24
- **Average Metrics:**
  - Avg Prob%: 67.6% ✅
  - Avg RRR: 1.11 ⚠️
  - Avg Count: 58 ⚠️
- **Success:** ✅ เพิ่มหุ้นที่เทรดได้ (3 → 4) - LI-AUTO มี Prob% สูงมาก (80%)

---

### V13.2 - China Market - RM Optimization ⭐ CURRENT
- **Goal:** ปรับ Risk Management ให้ RRR คุ้มกับความเสี่ยงมากขึ้น
- **Changes:**
  - SL: 1.5% → 1.2% (tighter SL)
  - TP: 4.5% → 5.5% (higher TP)
  - RRR: 3.0 → 4.58 (theoretical)
  - Max Hold: 6 → 8 days (ให้มีเวลาไปถึง TP)
  - Trailing: Activate 1.5% → 1.0% (activate early)
  - Trailing: Distance 50% → 40% (let profits run)
- **Target:** RRR actual 1.5+ (เพิ่มจาก 1.11)
- **Rationale:**
  - RRR จริง (1.11) ต่ำกว่า theoretical (3.0) มาก
  - ปรับ SL และ TP เพื่อเพิ่ม RRR
  - Trailing stop lock profits early
- **Expected Results:**
  - RRR actual: 1.11 → 1.5+ ✅
  - Win Rate: อาจลดลงเล็กน้อย (SL ต่ำ)
  - Count: อาจลดลงเล็กน้อย (SL ต่ำ)

---

**Last Updated:** 2026-02-14  
**Current Version:** V4.1 (Production-Ready Risk Management System)  
**Status:** ✅ **PRODUCTION-READY** - Complete with Intraday Metals Support  
**Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)
