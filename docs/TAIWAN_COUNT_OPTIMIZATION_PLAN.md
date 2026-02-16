# Taiwan Market - Count Optimization Plan (V12.3)

## 📊 Current Status (V12.2)

### ✅ Passing Stocks (2 Stocks)

| Symbol | Name | Prob% | RRR | Count | Status |
|--------|------|-------|-----|-------|--------|
| 2454 | MEDIATEK | 62.5% | **1.76** | 40 | ✅ PASS |
| 2317 | HON-HAI | 62.3% | 1.42 | 69 | ✅ PASS |

**Summary:**
- ✅ Prob% ดี (62.3-62.5%)
- ✅ RRR ดี (1.42-1.76)
- ⚠️ Count ต่ำ (40, 69) - ต้องการเพิ่มเพื่อความน่าเชื่อถือ

### ⚠️ Close to Passing (3 Stocks)

| Symbol | Name | Prob% | RRR | Count | Issue |
|--------|------|-------|-----|-------|-------|
| 2308 | DELTA | **70.0%** | **1.80** | 20 | Count < 25 |
| 3008 | LARGAN | 64.5% | 1.55 | 327 | Count > 150 |
| 2395 | ADVANTECH | 61.1% | 1.29 | 95 | RRR < 1.3 (very close!) |

**Key Insight:**
- DELTA มี Prob% และ RRR ดีที่สุด แต่ Count ต่ำ (20)
- ADVANTECH ใกล้ผ่าน (RRR 1.29 < 1.3)

---

## 🎯 Goal: Increase Count While Maintaining Prob% and RRR

### Strategy 1: Relax Gatekeeper Slightly (Recommended)

**Current:**
- `min_prob = 52.0%` (Taiwan V12.2)

**Proposed:**
- `min_prob = 51.5%` (ลด 0.5%)

**Expected Impact:**
- ✅ เพิ่ม count สำหรับหุ้นที่มี Prob% 52-51.5%
- ✅ ไม่กระทบ Prob% มาก (ลดลงเล็กน้อย)
- ✅ RRR ไม่เปลี่ยน (ขึ้นอยู่กับ RM parameters)

**Risk:**
- ⚠️ Prob% อาจลดลงเล็กน้อย (0.1-0.3%)
- ⚠️ อาจเพิ่ม trades ที่คุณภาพต่ำกว่า

**Recommendation:** ⭐ **TRY THIS FIRST**

---

### Strategy 2: Reduce min_stats (Pattern Quality)

**Current:**
- `min_stats = 25` (Taiwan V12.2)

**Proposed:**
- `min_stats = 22` (ลด 3)

**Expected Impact:**
- ✅ เพิ่ม patterns ที่ใช้ได้ (patterns ที่มี 22-24 occurrences)
- ✅ เพิ่ม count สำหรับหุ้นที่มี patterns หลากหลาย
- ✅ ไม่กระทบ Prob% และ RRR (ถ้า patterns ยังมีคุณภาพ)

**Risk:**
- ⚠️ Patterns ที่มี occurrences น้อยอาจไม่แม่น
- ⚠️ อาจเพิ่ม noise

**Recommendation:** ⚠️ **USE WITH CAUTION**

---

### Strategy 3: Increase n_bars (More Historical Data)

**Current:**
- `n_bars = 2000` (default)

**Proposed:**
- `n_bars = 2500` หรือ `3000`

**Expected Impact:**
- ✅ เพิ่ม historical data → เพิ่ม patterns
- ✅ เพิ่ม count สำหรับหุ้นที่มี patterns หลากหลาย
- ✅ ไม่กระทบ Prob% และ RRR (ถ้า patterns ยังมีคุณภาพ)

**Risk:**
- ⚠️ อาจใช้เวลานานขึ้นในการ backtest
- ⚠️ Patterns เก่าอาจไม่เหมาะกับ market regime ปัจจุบัน

**Recommendation:** ✅ **SAFE OPTION**

---

### Strategy 4: Adjust threshold_multiplier (Pattern Sensitivity)

**Current:**
- `threshold_multiplier = 0.9` (Taiwan V12.2)

**Proposed:**
- `threshold_multiplier = 0.85` (ลด 0.05)

**Expected Impact:**
- ✅ เพิ่ม sensitivity → เพิ่ม patterns
- ✅ เพิ่ม count สำหรับหุ้นที่มี volatility ต่ำ
- ✅ ไม่กระทบ Prob% และ RRR (ถ้า patterns ยังมีคุณภาพ)

**Risk:**
- ⚠️ อาจเพิ่ม noise patterns
- ⚠️ อาจลดคุณภาพของ patterns

**Recommendation:** ⚠️ **USE WITH CAUTION**

---

## 📋 Recommended Approach: V12.3

### Option A: Conservative (Recommended)

**Changes:**
1. `min_prob`: 52.0% → **51.5%** (ลด 0.5%)
2. `n_bars`: 2000 → **2500** (เพิ่ม 500)

**Expected Results:**
- ✅ เพิ่ม count สำหรับ MEDIATEK และ HON-HAI (40 → 50+, 69 → 80+)
- ✅ DELTA อาจผ่านเกณฑ์ (20 → 25+)
- ✅ Prob% ลดลงเล็กน้อย (0.1-0.3%)
- ✅ RRR ไม่เปลี่ยน

**Risk Level:** 🟢 **LOW**

---

### Option B: Moderate

**Changes:**
1. `min_prob`: 52.0% → **51.0%** (ลด 1.0%)
2. `min_stats`: 25 → **22** (ลด 3)
3. `n_bars`: 2000 → **2500** (เพิ่ม 500)

**Expected Results:**
- ✅ เพิ่ม count มากขึ้น (40 → 60+, 69 → 90+)
- ✅ DELTA อาจผ่านเกณฑ์ (20 → 30+)
- ✅ ADVANTECH อาจผ่านเกณฑ์ (RRR 1.29 → 1.3+)
- ⚠️ Prob% อาจลดลง (0.2-0.5%)
- ⚠️ RRR อาจลดลงเล็กน้อย

**Risk Level:** 🟡 **MEDIUM**

---

### Option C: Aggressive (Not Recommended)

**Changes:**
1. `min_prob`: 52.0% → **50.5%** (ลด 1.5%)
2. `min_stats`: 25 → **20** (ลด 5)
3. `threshold_multiplier`: 0.9 → **0.85** (ลด 0.05)

**Expected Results:**
- ✅ เพิ่ม count มาก (40 → 80+, 69 → 120+)
- ✅ DELTA อาจผ่านเกณฑ์ (20 → 40+)
- ⚠️ Prob% อาจลดลงมาก (0.5-1.0%)
- ⚠️ RRR อาจลดลง (1.76 → 1.6, 1.42 → 1.3)

**Risk Level:** 🔴 **HIGH**

---

## 🎯 Recommended: Option A (Conservative)

### Rationale

1. **Maintain Quality:**
   - Prob% และ RRR ดีอยู่แล้ว (62.3-62.5%, 1.42-1.76)
   - ไม่ควรเสี่ยงลดคุณภาพ

2. **Increase Count Safely:**
   - `min_prob`: 52.0% → 51.5% (ลดเล็กน้อย)
   - `n_bars`: 2000 → 2500 (เพิ่ม historical data)
   - ไม่กระทบคุณภาพมาก

3. **Target Stocks:**
   - MEDIATEK: 40 → 50+ (เพิ่ม 25%)
   - HON-HAI: 69 → 80+ (เพิ่ม 16%)
   - DELTA: 20 → 25+ (ผ่านเกณฑ์!)

---

## 📊 Implementation Plan

### Step 1: Update backtest.py

```python
# Taiwan V12.3: เพิ่ม count โดยไม่ลด Prob และ RRR
elif is_tw_market:
    min_prob = 51.5  # V12.3: ลดจาก 52% → 51.5% (เพิ่ม count)
    # ... other parameters unchanged
```

### Step 2: Update backtest command

```bash
# เพิ่ม n_bars จาก 2000 → 2500
python scripts/backtest.py --full --bars 2500 --group TAIWAN
```

### Step 3: Re-run backtest

```bash
# Clean old results
rm logs/trade_history_TAIWAN.csv
# Remove Taiwan entries from full_backtest_results.csv

# Run backtest
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# Calculate metrics
python scripts/calculate_metrics.py
```

### Step 4: Compare Results

- Compare V12.2 vs V12.3:
  - Count changes
  - Prob% changes
  - RRR changes
  - Number of passing stocks

---

## 📈 Expected Outcomes

### Best Case Scenario

| Symbol | V12.2 Count | V12.3 Count | Change | Status |
|--------|-------------|-------------|--------|--------|
| 2454 (MEDIATEK) | 40 | 55 | +15 | ✅ PASS |
| 2317 (HON-HAI) | 69 | 85 | +16 | ✅ PASS |
| 2308 (DELTA) | 20 | 28 | +8 | ✅ **NEW PASS** |
| 2395 (ADVANTECH) | 95 | 105 | +10 | ⚠️ RRR 1.29 → 1.3? |

**Total Passing Stocks:** 2 → **3-4** ✅

### Worst Case Scenario

| Symbol | V12.2 Count | V12.3 Count | Change | Status |
|--------|-------------|-------------|--------|--------|
| 2454 (MEDIATEK) | 40 | 45 | +5 | ✅ PASS |
| 2317 (HON-HAI) | 69 | 75 | +6 | ✅ PASS |
| 2308 (DELTA) | 20 | 23 | +3 | ⚠️ Still < 25 |

**Total Passing Stocks:** 2 → **2** (no change)

---

## ⚠️ Risks and Mitigation

### Risk 1: Prob% Decreases

**Mitigation:**
- Monitor Prob% changes closely
- If Prob% drops > 0.5%, revert changes
- Focus on stocks with Prob% >= 60% (Elite Filter)

### Risk 2: RRR Decreases

**Mitigation:**
- RRR ขึ้นอยู่กับ RM parameters (SL/TP)
- ไม่ควรเปลี่ยน RM parameters
- Monitor RRR changes closely

### Risk 3: Count Doesn't Increase Enough

**Mitigation:**
- Try Option B (Moderate) if Option A doesn't work
- Consider increasing n_bars further (2500 → 3000)

---

## 📝 Next Steps

1. ✅ **Review this plan** - Confirm approach
2. ⏳ **Implement Option A** - Update backtest.py
3. ⏳ **Run backtest** - Test with new parameters
4. ⏳ **Compare results** - V12.2 vs V12.3
5. ⏳ **Document findings** - Update VERSION_HISTORY.md

---

**Last Updated:** 2026-02-13  
**Version:** V12.3 (Proposed)  
**Status:** 📋 **PLANNING**

