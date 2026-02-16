# TSMC (2330) - Why Doesn't It Pass?

## 🔍 Problem Analysis

### Current Status
- **Symbol:** 2330 (TSMC)
- **Raw Count:** 426 trades
- **Elite Count:** 1 trade (Prob >= 60%)
- **Prob%:** 58.0% (Raw)
- **RRR:** 0.00
- **AvgWin%:** 0.00%
- **AvgLoss%:** 1.18%
- **Count:** 426 (too high > 150)

### Why TSMC Doesn't Pass Criteria

| Criteria | Requirement | TSMC Value | Status |
|----------|-------------|------------|--------|
| **Prob%** | >= 53% | 58.0% | ⚠️ Pass (but low) |
| **RRR** | >= 1.3 | 0.00 | ❌ **FAIL** |
| **Count** | 25-150 | 426 | ❌ **FAIL** (too high) |

---

## 🔎 Root Cause Analysis

### Issue 1: Elite Count = 1 (Too Low)

**Problem:**
- TSMC มี trades 426 ตัว (Raw Count)
- แต่มีแค่ **1 ตัว** ที่ผ่าน elite filter (Prob >= 60%)
- Elite trade ตัวนั้นมี Prob = 100.0% แต่ถูกนับเป็น RRR = 0

**Why Elite Count = 1?**
- Prob% ส่วนใหญ่ของ TSMC ต่ำกว่า 60%
- จาก trade history: Prob = 52.51%, 55.92%, 60.0%, etc.
- มีแค่ 1 ตัวที่ Prob >= 60%

### Issue 2: RRR = 0.00

**Problem:**
- Elite trade ตัวเดียวมี actual_return = 1.18% (win)
- แต่ RRR = 0.00 แสดงว่าไม่มี wins ใน elite group

**Possible Reasons:**
1. Elite trade ถูกนับเป็น loss (แม้ actual_return > 0)
2. การคำนวณ PnL อาจจะผิด (forecast vs actual direction)
3. Elite trade อาจจะถูก filter ออกไปก่อนคำนวณ RRR

### Issue 3: Count = 426 (Too High)

**Problem:**
- Count 426 > 150 (maximum requirement)
- แสดงว่า TSMC มี trades เยอะเกินไป
- อาจจะต้อง cap หรือ filter เพื่อลด count

---

## 📊 TSMC Trade Statistics

### From Trade History (Sample)

| Date | Forecast | Actual | Prob% | Return% | Correct |
|------|----------|--------|-------|---------|---------|
| 2017-11-27 | DOWN | UP | 60.0% | +1.18% | ❌ 0 |
| 2017-11-30 | UP | UP | 55.92% | +2.32% | ✅ 1 |
| 2017-12-06 | UP | DOWN | 52.51% | -1.0% | ❌ 0 |
| 2017-12-07 | UP | UP | 52.51% | +1.39% | ✅ 1 |

**Observation:**
- Elite trade (Prob 60.0%) มี Forecast = DOWN แต่ Actual = UP → Loss
- นี่คือสาเหตุที่ RRR = 0 (elite trade loss)

---

## 💡 Why TSMC Has Low Prob%

### Possible Reasons

1. **Pattern Matching ไม่เหมาะกับ TSMC**
   - TSMC เป็นหุ้นใหญ่ (large cap) → volatility ต่ำ
   - Pattern matching อาจจะไม่เหมาะกับหุ้นที่เคลื่อนไหวช้า

2. **Regime-Aware Strategy ไม่เหมาะ**
   - TSMC ใช้ Regime-Aware (BULL → TREND, BEAR → REVERSION)
   - อาจจะไม่เหมาะกับ TSMC

3. **Threshold ไม่เหมาะ**
   - Threshold 0.9 อาจจะสูงเกินไปสำหรับ TSMC
   - ทำให้มีสัญญาณน้อย

4. **Prob% Calculation**
   - Prob% = Win Rate จาก historical patterns
   - ถ้า patterns ของ TSMC ไม่แม่น → Prob% ต่ำ

---

## 🎯 Recommendations

### Option 1: Adjust Criteria for TSMC

**Relax Count Requirement:**
- Count 25-200 (เพิ่มจาก 150)
- เพื่อให้ TSMC ผ่านเกณฑ์

**But:** ยังมีปัญหา RRR = 0

### Option 2: Use Raw Prob% Instead of Elite

**Change Logic:**
- ถ้า Elite Count < 5 → ใช้ Raw Prob%
- TSMC: Raw Prob% = 58.0% (ผ่าน 53% requirement)
- แต่ยังมีปัญหา RRR = 0

### Option 3: Investigate Why RRR = 0

**Debug Steps:**
1. ตรวจสอบ elite trade ว่าทำไม RRR = 0
2. ตรวจสอบการคำนวณ PnL
3. ตรวจสอบว่า elite trade ถูก filter ออกไปหรือไม่

### Option 4: TSMC-Specific Logic

**Custom Parameters:**
- Threshold: 0.8 (ลดจาก 0.9)
- Min Stats: 20 (ลดจาก 25)
- Prob Filter: 50% (ลดจาก 52%)
- เพื่อเพิ่มสัญญาณสำหรับ TSMC

---

## 📝 Summary

### Why TSMC Doesn't Pass

1. **Elite Count = 1** (น้อยเกินไป)
   - มีแค่ 1 trade ที่ Prob >= 60%
   - Elite trade ตัวนั้น loss → RRR = 0

2. **Count = 426** (สูงเกินไป)
   - เกิน 150 requirement

3. **Prob% = 58.0%** (ต่ำ)
   - ผ่าน 53% requirement แต่ต่ำ
   - แสดงว่า pattern matching ไม่เหมาะกับ TSMC

### Key Insight

**TSMC เป็นหุ้นใหญ่ (large cap) ที่:**
- Volatility ต่ำ → Pattern matching ยาก
- Prob% ต่ำ (58.0%) → แสดงว่าระบบไม่เหมาะ
- มี trades เยอะ (426) → แต่คุณภาพไม่ดี

**Conclusion:** TSMC อาจจะไม่เหมาะกับระบบ pattern matching นี้ เพราะ volatility ต่ำและ pattern ไม่ชัดเจน

---

**Last Updated:** 2026-02-13  
**Status:** TSMC doesn't pass due to low Prob% and RRR = 0

