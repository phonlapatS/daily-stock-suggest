# Taiwan Market - Parameter Testing Plan

## 🎯 Objective

ทดสอบหลายค่า parameters เพื่อหาค่าที่เหมาะสมที่สุดสำหรับ Taiwan market:
- เพิ่มจำนวนหุ้นที่ผ่านเกณฑ์
- เพิ่ม count โดยไม่ลด Prob% และ RRR
- หาค่าที่สมดุลระหว่างคุณภาพและปริมาณ

---

## 📊 Parameters to Test

### 1. min_prob (Gatekeeper Threshold)

**Current:** 51.5% (V12.3)

**Test Values:**
- 51.0% (ลด 0.5% จาก V12.3)
- 51.5% (V12.3 current)
- 52.0% (V12.2)
- 52.5% (เพิ่มคุณภาพ)

**Expected Impact:**
- **51.0%:** เพิ่ม count มาก แต่ Prob% อาจลดลง
- **51.5%:** สมดุล (current)
- **52.0%:** คุณภาพดีขึ้น แต่ count อาจลดลง
- **52.5%:** คุณภาพดีมาก แต่ count อาจลดลงมาก

---

### 2. n_bars (Historical Data)

**Fixed:** 2500 bars (all tests)

**Why Fixed:**
- ✅ เปรียบเทียบผลของ min_prob ได้ชัดเจน
- ✅ ไม่มีตัวแปรอื่นมาทำให้ผลคลาดเคลื่อน
- ✅ เพิ่ม historical data เพียงพอ (25% จาก 2000)

---

## 📋 Test Matrix

| Test # | min_prob | n_bars | Expected Focus |
|--------|----------|--------|----------------|
| 1 | 51.0% | 2500 | Count (aggressive) |
| 2 | 51.5% | 2500 | Baseline (V12.3) |
| 3 | 52.0% | 2500 | Quality (V12.2) |
| 4 | 52.5% | 2500 | High quality |

**Total Tests:** 4 combinations (simplified)

---

## 📊 Metrics to Compare

สำหรับแต่ละ combination:

1. **Passing Stocks Count**
   - จำนวนหุ้นที่ผ่านเกณฑ์ (Prob >= 53%, RRR >= 1.3, Count 25-150)

2. **Average Prob%**
   - Prob% เฉลี่ยของหุ้นที่ผ่าน

3. **Average RRR**
   - RRR เฉลี่ยของหุ้นที่ผ่าน

4. **Average Count**
   - Count เฉลี่ยของหุ้นที่ผ่าน

5. **Total Trades**
   - จำนวน trades รวมของหุ้นที่ผ่าน

6. **Best RRR**
   - RRR สูงสุด

7. **Best Prob%**
   - Prob% สูงสุด

---

## 🎯 Success Criteria

### Best Combination Should Have:

1. **High Passing Stocks Count**
   - Target: >= 3 stocks (ดีกว่า V12.3 ที่มี 2)

2. **Good Average Metrics**
   - Avg Prob% >= 60%
   - Avg RRR >= 1.4
   - Avg Count 40-100 (สมดุล)

3. **Balanced Trade Count**
   - Total Trades: 150-300 (ไม่น้อยเกินไป ไม่มากเกินไป)

4. **Quality Maintained**
   - Best RRR >= 1.5
   - Best Prob% >= 65%

---

## 🚀 How to Run Tests

### Option 1: Manual Testing (Recommended)

```bash
# Test each combination manually
# 1. Edit backtest.py: min_prob = 51.0
python scripts/backtest.py --full --bars 2000 --group TAIWAN
python scripts/calculate_metrics.py
# Record results

# 2. Edit backtest.py: min_prob = 51.0
python scripts/backtest.py --full --bars 2500 --group TAIWAN
python scripts/calculate_metrics.py
# Record results

# ... repeat for all combinations
```

### Option 2: Automated Script

```bash
# Run automated testing (will take several hours)
python scripts/test_taiwan_parameters.py
```

**Note:** Automated script will:
- Modify backtest.py temporarily
- Run backtest for each combination
- Restore original file
- Save results to CSV

---

## 📝 Results Template

### For Each Test:

```
Test #X: min_prob=X%, n_bars=XXXX

Passing Stocks: X
- Symbol1: Prob X%, RRR X.XX, Count XX
- Symbol2: Prob X%, RRR X.XX, Count XX
- ...

Average Metrics:
- Avg Prob%: X%
- Avg RRR: X.XX
- Avg Count: XX
- Total Trades: XXX

Best Metrics:
- Best Prob%: X% (Symbol)
- Best RRR: X.XX (Symbol)
```

---

## 📊 Comparison Table Template

| Test | min_prob | n_bars | Passing | Avg Prob% | Avg RRR | Avg Count | Total Trades | Best RRR | Best Prob% |
|------|----------|--------|---------|----------|---------|-----------|--------------|----------|------------|
| 1 | 51.0% | 2000 | X | X% | X.XX | XX | XXX | X.XX | X% |
| 2 | 51.0% | 2500 | X | X% | X.XX | XX | XXX | X.XX | X% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 💡 Expected Findings

### Hypothesis 1: Lower min_prob = More Count
- **51.0%** → มากที่สุด แต่ Prob% อาจลดลง
- **52.5%** → น้อยที่สุด แต่ Prob% สูงสุด

### Hypothesis 2: Higher n_bars = More Count
- **3000** → มากที่สุด แต่ใช้เวลานาน
- **2000** → น้อยที่สุด แต่เร็ว

### Hypothesis 3: Optimal Balance
- **51.5% + 2500** → สมดุลระหว่างคุณภาพและปริมาณ
- **52.0% + 3000** → คุณภาพดี + count เพิ่ม

---

## ⚠️ Notes

1. **Time Required:**
   - Each backtest: 10-30 minutes
   - Total time: 40-120 minutes (4 tests)

2. **Resource Usage:**
   - High CPU/Memory during backtest
   - Large disk space for trade_history files

3. **Recommendation:**
   - Test sequentially (one at a time)
   - Start with Test #2 (51.5% - baseline) to confirm current results
   - Then test others to compare

---

## 🎯 Next Steps

1. ✅ **Create test script** (done)
2. ⏳ **Run tests** (user will do)
3. ⏳ **Collect results** (user will provide)
4. ⏳ **Analyze and compare** (we will do)
5. ⏳ **Select best combination** (we will recommend)
6. ⏳ **Implement V12.4** (final version)

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR TESTING**

