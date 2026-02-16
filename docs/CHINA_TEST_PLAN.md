# China Market - Test Plan for RM & Threshold Optimization

## 📋 Overview

ทดสอบหลายค่าเพื่อหาค่าที่เหมาะสมที่สุด:
- **Max Hold:** 5, 6, 7, 8, 9, 10 days
- **Threshold Multiplier:** 0.8, 0.85, 0.9, 0.95, 1.0

**Total Tests:** 6 × 5 = 30 combinations

---

## 🎯 Goals

1. **หาค่า Max Hold ที่เหมาะสม** - ไม่สั้นเกินไป (ถึง TP น้อย) ไม่ยาวเกินไป (over-trading)
2. **หาค่า Threshold ที่เหมาะสม** - ไม่ต่ำเกินไป (สัญญาณมากเกิน) ไม่สูงเกินไป (สัญญาณน้อยเกิน)
3. **เพิ่ม RRR จริง** จาก 1.11 → 1.5+
4. **รักษาจำนวนหุ้นที่ผ่านเกณฑ์** (4+ stocks)

---

## 🔧 Implementation

### Step 1: แยก China Market Logic ✅

**Changes in `scripts/backtest.py`:**

1. **Threshold Multiplier:**
   ```python
   elif is_china_market:
       threshold_multiplier = kwargs.get('threshold_multiplier', 0.9)
   ```

2. **Min Stats:**
   ```python
   elif is_china_market:
       min_stats = kwargs.get('min_stats', 25)
   ```

3. **Risk Management:**
   ```python
   elif is_china_market:
       RM_STOP_LOSS = kwargs.get('stop_loss', 1.2)
       RM_TAKE_PROFIT = kwargs.get('take_profit', 5.5)
       RM_MAX_HOLD = kwargs.get('max_hold', 8)
       RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 1.0)
       RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)
   ```

4. **Gatekeeper:**
   ```python
   elif is_china_market:
       min_prob = kwargs.get('min_prob', 51.0)
   ```

5. **backtest_all accepts kwargs:**
   ```python
   def backtest_all(..., **kwargs):
       ...
       result = backtest_single(..., **kwargs)
   ```

### Step 2: Test Script

**File:** `scripts/test_china_rm_threshold.py`

**Usage:**
```bash
python scripts/test_china_rm_threshold.py
```

**What it does:**
1. Loop through all combinations of max_hold and threshold
2. For each combination:
   - Clean old results
   - Run backtest with custom parameters
   - Analyze results
   - Save to CSV
3. Generate summary report

### Step 3: Manual Testing (Alternative)

If test script doesn't work, use manual approach:

```bash
# Test Max Hold = 6, Threshold = 0.9
python scripts/backtest.py --full --bars 2000 --group CHINA --fast \
  --stop_loss 1.2 --take_profit 5.5 --max_hold 6 \
  --threshold_multiplier 0.9

# Test Max Hold = 8, Threshold = 0.85
python scripts/backtest.py --full --bars 2000 --group CHINA --fast \
  --stop_loss 1.2 --take_profit 5.5 --max_hold 8 \
  --threshold_multiplier 0.85
```

**Note:** Need to add CLI arguments to `backtest.py` for these parameters.

---

## 📊 Test Matrix

| Max Hold | Threshold | Expected Impact |
|----------|-----------|----------------|
| 5 | 0.8 | สัญญาณมาก, ถึง TP น้อย |
| 5 | 0.9 | สัญญาณปานกลาง, ถึง TP น้อย |
| 5 | 1.0 | สัญญาณน้อย, ถึง TP น้อย |
| 6 | 0.8 | สัญญาณมาก, ถึง TP ปานกลาง |
| 6 | 0.9 | สัญญาณปานกลาง, ถึง TP ปานกลาง |
| 6 | 1.0 | สัญญาณน้อย, ถึง TP ปานกลาง |
| 7 | 0.8 | สัญญาณมาก, ถึง TP ดี |
| 7 | 0.9 | สัญญาณปานกลาง, ถึง TP ดี |
| 7 | 1.0 | สัญญาณน้อย, ถึง TP ดี |
| 8 | 0.8 | สัญญาณมาก, ถึง TP ดีมาก |
| 8 | 0.9 | สัญญาณปานกลาง, ถึง TP ดีมาก ⭐ Current |
| 8 | 1.0 | สัญญาณน้อย, ถึง TP ดีมาก |
| 9 | 0.8 | สัญญาณมาก, ถึง TP ดีมาก (อาจ over-trading) |
| 9 | 0.9 | สัญญาณปานกลาง, ถึง TP ดีมาก (อาจ over-trading) |
| 9 | 1.0 | สัญญาณน้อย, ถึง TP ดีมาก (อาจ over-trading) |
| 10 | 0.8 | สัญญาณมาก, ถึง TP ดีมาก (อาจ over-trading มาก) |
| 10 | 0.9 | สัญญาณปานกลาง, ถึง TP ดีมาก (อาจ over-trading มาก) |
| 10 | 1.0 | สัญญาณน้อย, ถึง TP ดีมาก (อาจ over-trading มาก) |

---

## 📈 Metrics to Track

For each test combination:

1. **Stocks Passing:** จำนวนหุ้นที่ผ่านเกณฑ์
2. **Avg RRR:** RRR เฉลี่ย
3. **Avg Prob%:** Prob% เฉลี่ย
4. **Total Count:** จำนวน trades รวม
5. **Avg Count:** จำนวน trades เฉลี่ยต่อหุ้น
6. **Best RRR:** RRR สูงสุด
7. **Worst RRR:** RRR ต่ำสุด
8. **Stocks List:** รายชื่อหุ้นที่ผ่าน

---

## 🎯 Success Criteria

### Minimum Requirements:
- ✅ **Stocks Passing:** ≥ 4 stocks
- ✅ **Avg RRR:** ≥ 1.3
- ✅ **Avg Prob%:** ≥ 52%
- ✅ **Avg Count:** 10-50 (ไม่น้อยเกินไป, ไม่มากเกินไป)

### Ideal Results:
- ✅ **Stocks Passing:** 5-6 stocks
- ✅ **Avg RRR:** ≥ 1.5
- ✅ **Avg Prob%:** ≥ 53%
- ✅ **Avg Count:** 15-40

---

## ⚠️ Trade-offs to Consider

### Max Hold:
- **ต่ำ (5-6):** ถึง TP น้อย → RRR ต่ำ
- **ปานกลาง (7-8):** สมดุล → RRR ดี
- **สูง (9-10):** อาจ over-trading → Count สูงเกิน

### Threshold:
- **ต่ำ (0.8):** สัญญาณมาก → Count สูง, Prob% อาจต่ำ
- **ปานกลาง (0.9):** สมดุล → Count ปานกลาง, Prob% ดี
- **สูง (1.0):** สัญญาณน้อย → Count ต่ำ, Prob% สูง

---

## 📝 Results Template

```csv
max_hold,threshold,stocks_passing,avg_rrr,avg_prob,total_count,avg_count,best_rrr,worst_rrr,stocks
8,0.9,4,1.22,53.5,156,39,1.45,1.00,"MEITUAN,BYD,JD-COM,LI-AUTO"
...
```

---

## 🚀 Next Steps

1. ✅ **แยก China market logic** (done)
2. ⏳ **สร้าง test script** (done - needs CLI args)
3. ⏳ **เพิ่ม CLI arguments** to `backtest.py` for custom parameters
4. ⏳ **Run tests** (30 combinations)
5. ⏳ **Analyze results** and select best combination
6. ⏳ **Document findings** in `docs/CHINA_V13_3_RESULTS.md`

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR TESTING** (needs CLI args implementation)

