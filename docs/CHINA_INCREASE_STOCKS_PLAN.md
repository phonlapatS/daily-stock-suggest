# China Market - Increase Stocks Plan

## 📊 Current Status

**Current Criteria:**
- Prob >= 53%
- RRR >= 1.0
- Count >= 15

**Passing:** 3 stocks (MEITUAN, BYD, JD-COM)

---

## 🔍 Test Results

### Scenario A: RRR >= 0.95, Count >= 10
- **Passing:** 4 stocks (+1)
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - LI-AUTO (80.0%, RRR 1.00, Count 10) ⚠️ Count ต่ำ
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### Scenario B: RRR >= 0.95, Count >= 5 ⭐ **BEST**
- **Passing:** 5 stocks (+2)
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - LI-AUTO (80.0%, RRR 1.00, Count 10)
  - XIAOMI (77.8%, RRR 0.96, Count 9) ⚠️ Count ต่ำ, RRR ต่ำ
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### Scenario C: RRR >= 0.9, Count >= 10
- **Passing:** 4 stocks (+1)
  - Same as Scenario A

### Scenario D: RRR >= 0.9, Count >= 5
- **Passing:** 5 stocks (+2)
  - Same as Scenario B

---

## 💡 Two Approaches

### Approach 1: Lower Display Criteria (Quick Win)

**Change:**
- RRR >= 1.0 → RRR >= 0.95
- Count >= 15 → Count >= 10

**Expected:**
- 4 stocks passing (เพิ่มจาก 3 → 4)
- เพิ่ม LI-AUTO (Prob 80.0%, RRR 1.00)

**Pros:**
- ✅ ง่าย - แค่เปลี่ยน display criteria
- ✅ ไม่ต้องรัน backtest ใหม่
- ✅ LI-AUTO มี Prob% สูงมาก (80%)

**Cons:**
- ⚠️ LI-AUTO Count ต่ำ (10) - ข้อมูลไม่เพียงพอ
- ⚠️ RRR requirement ลดลง (1.0 → 0.95)

---

### Approach 2: Optimize RM Parameters (Better Quality)

**Goal:** เพิ่ม RRR และ Count โดยปรับ RM parameters

**Current RM:**
- SL: 1.5%
- TP: 3.5%
- RRR: 2.33 (theoretical)
- Max Hold: 5 days
- Trailing: Activate 1.5%, Distance 50%

**Options:**

#### Option 2A: Increase TP (Higher RRR)
- TP: 3.5% → 4.5%
- RRR: 2.33 → 3.0 (theoretical)
- **Expected:** RRR ของหุ้นเพิ่มขึ้น

#### Option 2B: Tighten SL (Higher RRR)
- SL: 1.5% → 1.2%
- TP: 3.5% → 4.0%
- RRR: 2.33 → 3.33 (theoretical)
- **Expected:** RRR ของหุ้นเพิ่มขึ้น

#### Option 2C: Lower min_prob (More Count)
- min_prob: 53.0% → 51.0%
- **Expected:** Count ของหุ้นเพิ่มขึ้น

#### Option 2D: Combined (TP + min_prob)
- TP: 3.5% → 4.5%
- min_prob: 53.0% → 51.0%
- **Expected:** RRR และ Count เพิ่มขึ้น

---

## 🎯 Recommended: Approach 1 + Approach 2D

### Step 1: Lower Display Criteria (Immediate)
- RRR >= 1.0 → RRR >= 0.95
- Count >= 15 → Count >= 10

**Result:** 4 stocks passing (เพิ่ม LI-AUTO)

### Step 2: Optimize RM Parameters (Better Quality)
- TP: 3.5% → 4.5% (เพิ่ม RRR)
- min_prob: 53.0% → 51.0% (เพิ่ม Count)
- **Note:** ต้องรัน backtest ใหม่

**Expected:**
- RRR ของหุ้นเพิ่มขึ้น
- Count ของหุ้นเพิ่มขึ้น
- อาจได้หุ้นเพิ่ม (XIAOMI, etc.)

---

## ⚠️ Considerations

### LI-AUTO Count ต่ำ (10):
- ข้อมูลไม่เพียงพอ
- อาจไม่น่าเชื่อถือ
- **Recommendation:** ใช้ Count >= 10 (ไม่ลดเป็น 5)

### XIAOMI Count ต่ำ (9) และ RRR ต่ำ (0.96):
- Count ต่ำมาก (9)
- RRR ต่ำ (0.96)
- **Recommendation:** ไม่แนะนำ (ต้อง Count >= 5 และ RRR >= 0.95)

---

## 📝 Implementation Plan

### Phase 1: Quick Win (Display Criteria)
1. ✅ Change display criteria: RRR >= 0.95, Count >= 10
2. ✅ Test and verify results
3. ✅ Document changes

### Phase 2: RM Optimization (if needed)
1. ⏳ Adjust RM parameters (TP, min_prob)
2. ⏳ Run backtest
3. ⏳ Evaluate results
4. ⏳ Document changes

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR IMPLEMENTATION**

