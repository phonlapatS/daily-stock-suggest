# Taiwan Parameter Test Results Template

## 📊 Test Results Table

**All tests use n_bars=2500 for fair comparison**

| Test # | min_prob | n_bars | Passing | Symbols | Avg Prob% | Avg RRR | Avg Count | Total Trades | Best Prob% | Best RRR | Notes |
|--------|----------|--------|---------|---------|-----------|---------|-----------|--------------|-----------|----------|-------|
| 1 | 51.0% | 2500 | ? | ? | ? | ? | ? | ? | ? | ? | Count (aggressive) |
| 2 | 51.5% | 2500 | ? | ? | ? | ? | ? | ? | ? | ? | Baseline (V12.3) |
| 3 | 52.0% | 2500 | ? | ? | ? | ? | ? | ? | ? | ? | Quality (V12.2) |
| 4 | 52.5% | 2500 | ? | ? | ? | ? | ? | ? | ? | ? | High quality | |

---

## 📝 Detailed Results

### Test #1: min_prob=51.0%, n_bars=2500 (V12.4)

**Passing Stocks:** 2
- 2308 (DELTA): Prob 71.4%, RRR 1.95, Count 35
- 2382 (QUANTA): Prob 62.5%, RRR 1.41, Count 96

**Average Metrics:**
- Avg Prob%: 67.0%
- Avg RRR: 1.68
- Avg Count: 65.5
- Total Trades: 131

**Best Metrics:**
- Best Prob%: 71.4% (2308)
- Best RRR: 1.95 (2308)

**Notes:**
- จำนวนหุ้นที่ผ่านเพิ่มขึ้น (1 → 2) ✅
- QUANTA ผ่านเกณฑ์แล้ว (RRR 1.41 >= 1.25) ✅
- DELTA metrics ดีขึ้น (Prob 71.4%, RRR 1.95) ✅
- DELTA Count ลดลง (90 → 35) - อาจเป็นเพราะ min_prob ลดลง
- HON-HAI หายไป - ต้องตรวจสอบ 

---

### Test #2: min_prob=51.5%, n_bars=2500 (V12.3 Baseline)

**Passing Stocks:** 1
- 2308 (DELTA): Prob 71.1%, RRR 1.91, Count 90

**Average Metrics:**
- Avg Prob%: 71.1%
- Avg RRR: 1.91
- Avg Count: 90
- Total Trades: 90

**Best Metrics:**
- Best Prob%: 71.1% (2308)
- Best RRR: 1.91 (2308)

**Notes:**
- DELTA Count เพิ่มขึ้นมาก (55 → 90, +64%)
- DELTA Prob% และ RRR ดีขึ้น (70.9% → 71.1%, 1.89 → 1.91)
- HON-HAI ไม่ผ่านเกณฑ์ (RRR 1.26 < 1.3)
- จำนวนหุ้นที่ผ่านลดลง (2 → 1) 

---

### Test #3: min_prob=52.0%, n_bars=2500

**Passing Stocks:** ?
- Symbol1: Prob ?%, RRR ?.??, Count ??
- Symbol2: Prob ?%, RRR ?.??, Count ??

**Average Metrics:**
- Avg Prob%: ?%
- Avg RRR: ?.??
- Avg Count: ??
- Total Trades: ???

**Best Metrics:**
- Best Prob%: ?% (Symbol)
- Best RRR: ?.?? (Symbol)

**Notes:**
- 

---

### Test #4: min_prob=52.5%, n_bars=2500

**Passing Stocks:** ?
- Symbol1: Prob ?%, RRR ?.??, Count ??
- Symbol2: Prob ?%, RRR ?.??, Count ??

**Average Metrics:**
- Avg Prob%: ?%
- Avg RRR: ?.??
- Avg Count: ??
- Total Trades: ???

**Best Metrics:**
- Best Prob%: ?% (Symbol)
- Best RRR: ?.?? (Symbol)

**Notes:**
- 

---

## 📊 Summary & Analysis

### Best Combination

**Test #?:** min_prob=?%, n_bars=?

**Why:**
- 

### Key Findings

1. **min_prob Impact (with n_bars=2500 fixed):**
   - 51.0%: 
   - 51.5%: 
   - 52.0%: 
   - 52.5%: 

2. **Optimal min_prob:**
   - 

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **AWAITING TEST RESULTS**

