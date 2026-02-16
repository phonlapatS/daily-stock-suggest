# China Market - Current Status & Optimization Plan

## 📊 Current Status

### Passing Stocks (1 Stock):
- **MEITUAN (3690):** Prob 76.9%, RRR 1.22, Count 39 ✅

### Current Criteria:
- Prob >= 55%
- RRR >= 1.2
- Count >= 15

---

## 🔍 All China Stocks Analysis

| Symbol | Name | Prob% | RRR | Count | Status | Issue |
|--------|------|-------|-----|-------|--------|-------|
| 2015 | LI-AUTO | 80.0% | 1.00 | 10 | ❌ | RRR < 1.2, Count < 15 |
| 1810 | XIAOMI | 77.8% | 0.96 | 9 | ❌ | RRR < 1.2, Count < 15 |
| 9868 | XPENG | 77.8% | 0.67 | 9 | ❌ | RRR ต่ำมาก, Count < 15 |
| **3690** | **MEITUAN** | **76.9%** | **1.22** | **39** | ✅ **PASS** | - |
| 1211 | BYD | 59.1% | 1.00 | 159 | ❌ | RRR < 1.2 |
| 9988 | ALIBABA | 56.7% | 0.86 | 30 | ❌ | RRR < 1.2 |
| 9618 | JD-COM | 54.2% | 1.20 | 24 | ❌ | Prob < 55%, RRR ดี |
| 9888 | BAIDU | 53.2% | 0.84 | 94 | ❌ | Prob < 55%, RRR ต่ำ |
| 700 | TENCENT | 48.1% | 1.04 | 135 | ❌ | Prob < 55% |
| 9866 | NIO | 47.8% | 0.81 | 23 | ❌ | Prob < 55%, RRR ต่ำ |

---

## 🔍 Near Passing Stocks

### Category 1: Prob% สูง แต่ RRR ต่ำ + Count ต่ำ

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 2015 | LI-AUTO | 80.0% | 1.00 | 10 | RRR -0.2, Count -5 | ลด RRR req, เพิ่ม Count |
| 1810 | XIAOMI | 77.8% | 0.96 | 9 | RRR -0.24, Count -6 | ลด RRR req, เพิ่ม Count |

**Analysis:**
- Prob% สูงมาก (77-80%) แต่ RRR ต่ำ (0.96-1.00)
- Count ต่ำ (9-10) - ข้อมูลไม่เพียงพอ

---

### Category 2: Prob% ดี แต่ RRR ต่ำ

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 1211 | BYD | 59.1% | 1.00 | 159 | RRR -0.2 | ลด RRR requirement |
| 9988 | ALIBABA | 56.7% | 0.86 | 30 | RRR -0.34 | ลด RRR requirement |

**Analysis:**
- Prob% ดี (56-59%) แต่ RRR ต่ำ (0.86-1.00)
- Count ดี (30-159)

---

### Category 3: Prob% ต่ำ แต่ RRR ดี

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 9618 | JD-COM | 54.2% | 1.20 | 24 | Prob -0.8% | ลด Prob requirement |

**Analysis:**
- Prob% ต่ำ (54.2%) แต่ RRR ดี (1.20)
- Count ดี (24)

---

## 💡 Optimization Strategies

### Strategy 1: Lower RRR Requirement (Recommended)

**Current:** RRR >= 1.2

**Option A: RRR >= 1.0**
- จะได้: LI-AUTO (80.0%, RRR 1.00), XIAOMI (77.8%, RRR 0.96), BYD (59.1%, RRR 1.00)
- **Total: 4 stocks** (เพิ่มจาก 1 → 4)

**Option B: RRR >= 1.1**
- จะได้: LI-AUTO (80.0%, RRR 1.00) ❌, XIAOMI (77.8%, RRR 0.96) ❌
- **Total: 1 stock** (ไม่เพิ่ม)

**Recommendation:** Option A (RRR >= 1.0)

---

### Strategy 2: Lower Prob Requirement

**Current:** Prob >= 55%

**Option: Prob >= 53%**
- จะได้: JD-COM (54.2%, RRR 1.20), BAIDU (53.2%, RRR 0.84)
- **Total: 3 stocks** (เพิ่มจาก 1 → 3)

**But:** BAIDU RRR ต่ำ (0.84) - อาจไม่คุ้มเสี่ยง

---

### Strategy 3: Lower Count Requirement

**Current:** Count >= 15

**Option: Count >= 10**
- จะได้: LI-AUTO (80.0%, RRR 1.00, Count 10), XIAOMI (77.8%, RRR 0.96, Count 9)
- **Total: 3 stocks** (เพิ่มจาก 1 → 3)

**But:** Count ต่ำ (9-10) - ข้อมูลไม่เพียงพอ

---

### Strategy 4: Combined (RRR 1.0 + Prob 53%)

**Change:**
- RRR >= 1.2 → RRR >= 1.0
- Prob >= 55% → Prob >= 53%

**Expected:**
- LI-AUTO (80.0%, RRR 1.00, Count 10) - Count ต่ำ
- XIAOMI (77.8%, RRR 0.96, Count 9) - Count ต่ำ, RRR ต่ำ
- BYD (59.1%, RRR 1.00, Count 159) ✅
- JD-COM (54.2%, RRR 1.20, Count 24) ✅
- **Total: 4-5 stocks** (ขึ้นอยู่กับ Count requirement)

---

## 🎯 Recommended Approach

### Phase 1: Quick Win (Lower RRR to 1.0)

**Change:**
- RRR >= 1.2 → RRR >= 1.0

**Expected Results:**
- ✅ MEITUAN (76.9%, RRR 1.22, Count 39) - ผ่านอยู่แล้ว
- ✅ LI-AUTO (80.0%, RRR 1.00, Count 10) - ผ่าน (แต่ Count ต่ำ)
- ✅ BYD (59.1%, RRR 1.00, Count 159) - ผ่าน
- **Total: 3 stocks** (เพิ่มจาก 1 → 3)

**Trade-off:**
- RRR requirement ลดลง (1.2 → 1.0)
- LI-AUTO Count ต่ำ (10) - ต้องระวัง

---

### Phase 2: Increase Count (if needed)

**Change:**
- Count >= 15 → Count >= 10

**Expected:**
- XIAOMI (77.8%, RRR 0.96, Count 9) - ยังไม่ผ่าน (RRR < 1.0)

**Note:** ต้องลด RRR เป็น 0.95 ถึงจะได้ XIAOMI

---

## 📊 Current Parameters

### Backtest Parameters:
- **min_prob:** 53.0% (gatekeeper)
- **threshold_multiplier:** Market-specific
- **min_stats:** Market-specific

### Risk Management:
- **SL:** 1.5%
- **TP:** 3.5%
- **RRR:** 2.33 (theoretical)
- **Max Hold:** 5 days
- **Trailing Stop:** Enabled (Activate 1.5%, Distance 50%)

### Display Criteria:
- Prob >= 55%
- RRR >= 1.2
- Count >= 15

---

## 🚀 Next Steps

1. ✅ **Analyze current status** (done)
2. ⏳ **Test Strategy 1** (Lower RRR to 1.0)
3. ⏳ **Evaluate results**
4. ⏳ **Optimize further if needed**

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **ANALYSIS COMPLETE** - Ready for optimization

