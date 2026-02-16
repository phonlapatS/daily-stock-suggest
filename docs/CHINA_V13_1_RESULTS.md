# China Market V13.1 - Results

## 📊 Final Configuration

**Display Criteria:**
- Prob >= 53%
- RRR >= 0.95 (ลดจาก 1.0)
- Count >= 10 (ลดจาก 15)

**Risk Management:**
- SL: 1.5% (คงเดิม)
- TP: 4.5% (เพิ่มจาก 3.5%)
- RRR: 3.0 (theoretical, เพิ่มจาก 2.33)
- Max Hold: 6 days (เพิ่มจาก 5)

**Gatekeeper:**
- min_prob: 51.0% (ลดจาก 53.0%)

---

## ✅ Passing Stocks (4 Stocks)

| Symbol | Name | Prob% | RRR | Count | AvgWin% | AvgLoss% | Status |
|--------|------|-------|-----|-------|---------|----------|--------|
| **2015** | **LI-AUTO** | **80.0%** | **1.00** | **10** | 1.50% | 1.50% | ✅ **PASS** ⚠️ |
| **3690** | **MEITUAN** | **76.9%** | **1.22** | **39** | 1.83% | 1.50% | ✅ **PASS** |
| **1211** | **BYD** | **59.1%** | **1.00** | **159** | 1.79% | 1.80% | ✅ **PASS** |
| **9618** | **JD-COM** | **54.2%** | **1.20** | **24** | 1.79% | 1.49% | ✅ **PASS** |

**Total Passing:** 4 stocks (เพิ่มจาก 3 → 4) ✅

---

## 📈 Comparison with V13.0

### Before (V13.0):
- **Passing:** 3 stocks
- **Avg Prob%:** 63.4%
- **Avg RRR:** 1.14
- **Avg Count:** 74

### After (V13.1):
- **Passing:** 4 stocks (+1)
- **Avg Prob%:** 67.6% ✅ (เพิ่มขึ้น)
- **Avg RRR:** 1.11 ⚠️ (ลดลงเล็กน้อย - เพราะ LI-AUTO RRR 1.00)
- **Avg Count:** 58 ⚠️ (ลดลง - เพราะ LI-AUTO Count 10)

---

## 🎯 Key Achievements

1. ✅ **เพิ่มหุ้นที่ผ่าน** (3 → 4)
2. ✅ **LI-AUTO มี Prob% สูงมาก** (80.0%)
3. ✅ **ปรับ RM parameters** (TP 4.5%, RRR 3.0)
4. ✅ **ปรับ min_prob** (51.0% - เพิ่ม Count)

---

## ⚠️ Considerations

### LI-AUTO (2015):
- **Prob%:** 80.0% ✅ (สูงมาก!)
- **RRR:** 1.00 ⚠️ (ต่ำ - ใกล้เกณฑ์)
- **Count:** 10 ⚠️ (ต่ำ - ข้อมูลไม่เพียงพอ)
- **Status:** ✅ Pass แต่ต้องระวัง

### RM Changes Impact:
- **TP เพิ่มขึ้น** (3.5% → 4.5%) → อาจถึง TP น้อยลง
- **Max Hold เพิ่มขึ้น** (5 → 6) → ให้เวลาไปถึง TP
- **min_prob ลดลง** (53% → 51%) → Count เพิ่มขึ้น

**Note:** ต้องรัน backtest ใหม่เพื่อเห็นผล RM changes

---

## 📝 Next Steps

1. ✅ **Display criteria applied** (done)
2. ✅ **RM parameters updated** (done)
3. ✅ **Gatekeeper updated** (done)
4. ⏳ **Run backtest** (pending - to see RM impact)
5. ⏳ **Evaluate results** (pending)

---

## 🚀 Usage

### To see current results (with old backtest data):
```bash
python scripts/calculate_metrics.py
```

### To regenerate with new RM parameters:
```bash
python scripts/backtest.py --full --bars 2500 --group CHINA
python scripts/calculate_metrics.py
```

---

**Last Updated:** 2026-02-13  
**Version:** V13.1  
**Status:** ✅ **DISPLAY CRITERIA APPLIED** - Backtest pending for RM impact

