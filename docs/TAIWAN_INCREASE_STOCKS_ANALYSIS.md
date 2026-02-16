# Taiwan Market - Analysis: เพิ่มหุ้นที่ผ่านเกณฑ์ 1-3 ตัว

## 🎯 Goal

วิเคราะห์หาหุ้นที่ใกล้ผ่านเกณฑ์และหาวิธีเพิ่มให้ผ่านเกณฑ์

---

## 📊 Current Status

### Passing Stocks (2 Stocks):
- DELTA (2308): Prob 71.4%, RRR 1.95, Count 35 ✅
- QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96 ✅

### Current Criteria:
- Prob >= 53%
- RRR >= 1.25
- Count 25-150

---

## 🔍 Near Passing Stocks Analysis

### Category 1: RRR < 1.25 (แต่ Prob% และ Count ดี)

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 2303 | UMC | 65.8% | 1.14 | 79 | RRR -0.11 | ลด RRR requirement → 1.15 |
| 2317 | HON-HAI | 59.3% | 1.07 | 27 | RRR -0.18 | ลด RRR requirement → 1.10 |

**Analysis:**
- UMC: Prob% สูงมาก (65.8%) แต่ RRR ต่ำ (1.14)
- HON-HAI: Prob% ดี (59.3%) แต่ RRR ต่ำ (1.07)

**Recommendation:**
- ลด RRR requirement จาก 1.25 → 1.15 จะได้ UMC ผ่าน
- ลด RRR requirement จาก 1.25 → 1.10 จะได้ HON-HAI ผ่าน

---

### Category 2: Count > 150 (แต่ Prob% และ RRR ดี)

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 3008 | LARGAN | 65.0% | 1.93 | 311 | Count +161 | เพิ่ม Count cap → 400 |
| 2395 | ADVANTECH | 64.2% | 1.36 | 369 | Count +219 | เพิ่ม Count cap → 400 |
| 2330 | TSMC | 58.2% | 1.42 | 565 | Count +415 | Count สูงเกินไป |

**Analysis:**
- LARGAN: Prob% และ RRR ดีมาก (65.0%, 1.93) แต่ Count สูง (311)
- ADVANTECH: Prob% และ RRR ดี (64.2%, 1.36) แต่ Count สูง (369)
- TSMC: Prob% และ RRR ดี (58.2%, 1.42) แต่ Count สูงมาก (565)

**Recommendation:**
- เพิ่ม Count cap จาก 150 → 300 จะได้ LARGAN และ ADVANTECH ผ่าน
- หรือเพิ่ม Count cap → 400 จะได้ 3 ตัว (แต่ TSMC ยังเกิน)

---

### Category 3: Prob% < 53% (แต่ RRR และ Count ดี)

| Symbol | Name | Prob% | RRR | Count | Gap | Solution |
|--------|------|-------|-----|-------|-----|----------|
| 3711 | ASE | 50.0% | 0.52 | 60 | Prob -3%, RRR ต่ำ | ไม่แนะนำ |
| 2454 | MEDIATEK | 49.1% | 0.89 | 53 | Prob -3.9%, RRR ต่ำ | ไม่แนะนำ |

**Analysis:**
- Prob% ต่ำเกินไป (< 50%)
- RRR ต่ำเกินไป (< 1.0)

**Recommendation:**
- ไม่แนะนำให้ลด Prob% requirement

---

## 💡 Options to Increase Passing Stocks

### Option 1: Lower RRR Requirement (Recommended)

**Change:**
- RRR >= 1.25 → RRR >= 1.15

**Expected Results:**
- ✅ UMC (2303): Prob 65.8%, RRR 1.14, Count 79 → **PASS**
- ✅ DELTA (2308): Prob 71.4%, RRR 1.95, Count 35 → **PASS**
- ✅ QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96 → **PASS**
- **Total: 3 stocks** (เพิ่มจาก 2 → 3)

**Pros:**
- เพิ่มหุ้นที่ผ่านเกณฑ์ (2 → 3)
- UMC มี Prob% สูงมาก (65.8%)

**Cons:**
- RRR requirement ลดลง (1.25 → 1.15)
- คุณภาพอาจลดลงเล็กน้อย

---

### Option 2: Increase Count Cap

**Change:**
- Count <= 150 → Count <= 300

**Expected Results:**
- ✅ DELTA (2308): Prob 71.4%, RRR 1.95, Count 35 → **PASS**
- ✅ QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96 → **PASS**
- ✅ LARGAN (3008): Prob 65.0%, RRR 1.93, Count 311 → **PASS**
- ✅ ADVANTECH (2395): Prob 64.2%, RRR 1.36, Count 369 → **PASS**
- **Total: 4 stocks** (เพิ่มจาก 2 → 4)

**Pros:**
- เพิ่มหุ้นที่ผ่านเกณฑ์มาก (2 → 4)
- LARGAN และ ADVANTECH มี metrics ดี

**Cons:**
- Count cap เพิ่มขึ้น (150 → 300)
- อาจ over-trading

---

### Option 3: Combined (RRR + Count)

**Change:**
- RRR >= 1.25 → RRR >= 1.15
- Count <= 150 → Count <= 300

**Expected Results:**
- ✅ DELTA (2308): Prob 71.4%, RRR 1.95, Count 35 → **PASS**
- ✅ QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96 → **PASS**
- ✅ UMC (2303): Prob 65.8%, RRR 1.14, Count 79 → **PASS**
- ✅ LARGAN (3008): Prob 65.0%, RRR 1.93, Count 311 → **PASS**
- ✅ ADVANTECH (2395): Prob 64.2%, RRR 1.36, Count 369 → **PASS**
- **Total: 5 stocks** (เพิ่มจาก 2 → 5)

**Pros:**
- เพิ่มหุ้นที่ผ่านเกณฑ์มากที่สุด (2 → 5)
- ครอบคลุมหุ้นที่มี metrics ดี

**Cons:**
- RRR requirement ลดลง
- Count cap เพิ่มขึ้น
- คุณภาพอาจลดลง

---

### Option 4: Lower RRR to 1.10 (Aggressive)

**Change:**
- RRR >= 1.25 → RRR >= 1.10

**Expected Results:**
- ✅ UMC (2303): Prob 65.8%, RRR 1.14, Count 79 → **PASS**
- ✅ HON-HAI (2317): Prob 59.3%, RRR 1.07, Count 27 → **PASS**
- ✅ DELTA (2308): Prob 71.4%, RRR 1.95, Count 35 → **PASS**
- ✅ QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96 → **PASS**
- **Total: 4 stocks** (เพิ่มจาก 2 → 4)

**Pros:**
- เพิ่มหุ้นที่ผ่านเกณฑ์ (2 → 4)
- HON-HAI ผ่านเกณฑ์

**Cons:**
- RRR requirement ลดลงมาก (1.25 → 1.10)
- คุณภาพลดลงมาก

---

## 🎯 Recommended: Option 1 (Lower RRR to 1.15)

### Rationale:
1. **เพิ่มหุ้นที่ผ่านเกณฑ์** (2 → 3)
2. **UMC มี Prob% สูงมาก** (65.8%) - คุณภาพดี
3. **RRR 1.15 ยังสมเหตุสมผล** - ไม่ต่ำเกินไป
4. **ไม่ต้องเปลี่ยน Count cap** - ยังคงคุณภาพ

### Implementation:
```python
# ใน calculate_metrics.py
tw_trend = summary_df[
    (summary_df['Country'] == 'TW') & 
    (summary_df['Prob%'] >= 53.0) &
    (summary_df['RR_Ratio'] >= 1.15) &  # ลดจาก 1.25 → 1.15
    (summary_df['Count'] >= 25) &
    (summary_df['Count'] <= 150)
]
```

### Expected Results:
- **3 stocks passing:**
  1. DELTA (2308): Prob 71.4%, RRR 1.95, Count 35
  2. QUANTA (2382): Prob 62.5%, RRR 1.41, Count 96
  3. UMC (2303): Prob 65.8%, RRR 1.14, Count 79

---

## 📊 Comparison Table

| Option | RRR Req | Count Cap | Passing Stocks | Change | Quality |
|--------|---------|-----------|----------------|--------|---------|
| Current | >= 1.25 | <= 150 | 2 | - | High |
| Option 1 | >= 1.15 | <= 150 | 3 | +1 | High |
| Option 2 | >= 1.25 | <= 300 | 4 | +2 | Medium |
| Option 3 | >= 1.15 | <= 300 | 5 | +3 | Medium |
| Option 4 | >= 1.10 | <= 150 | 4 | +2 | Low |

---

## 💡 Alternative: Adjust min_prob

### Current: min_prob = 51.0%

**Option A: Increase to 51.2%**
- อาจเพิ่ม Count สำหรับ DELTA
- แต่หุ้นอื่นอาจไม่ผ่าน

**Option B: Keep 51.0%**
- สมดุลระหว่างคุณภาพและปริมาณ

---

## 🎯 Final Recommendation

### Best Option: **Option 1 (RRR >= 1.15)**

**Why:**
1. ✅ เพิ่มหุ้นที่ผ่านเกณฑ์ (2 → 3)
2. ✅ UMC มี Prob% สูงมาก (65.8%)
3. ✅ RRR 1.15 ยังสมเหตุสมผล
4. ✅ ไม่ต้องเปลี่ยน Count cap

**Implementation:**
- แก้ไข `calculate_metrics.py`: RRR >= 1.25 → RRR >= 1.15
- ไม่ต้องรัน backtest ใหม่ (ใช้ข้อมูลเดิม)

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **ANALYSIS COMPLETE**

