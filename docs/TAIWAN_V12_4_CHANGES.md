# Taiwan V12.4 - Increase Tradable Stocks (Mentor Request)

## 🎯 Goal

เพิ่มจำนวนหุ้นที่เทรดได้ตามที่ mentor ขอ

---

## 📊 Changes Made

### 1. Lower min_prob (Gatekeeper)
- **Before (V12.3):** min_prob = 51.5%
- **After (V12.4):** min_prob = 51.0%
- **Impact:** เพิ่ม trades ที่มี Prob% 51.0-51.5%

### 2. Lower RRR Requirement (Display Filter)
- **Before (V12.3):** RRR >= 1.3
- **After (V12.4):** RRR >= 1.25
- **Impact:** HON-HAI จะผ่านเกณฑ์ (RRR 1.26)

---

## 📈 Expected Results

### Current Status (V12.3, n_bars=2500):
- DELTA (2308): Prob 71.1%, RRR 1.91, Count 90 ✅
- HON-HAI (2317): Prob 61.0%, RRR 1.26, Count 123 ❌ (RRR < 1.3)
- **Total Passing:** 1 stock

### Expected After V12.4:
- DELTA (2308): Prob ~71%, RRR ~1.91, Count ~90+ ✅
- HON-HAI (2317): Prob ~61%, RRR ~1.26, Count ~120+ ✅ (RRR >= 1.25)
- **Total Passing:** 2+ stocks (เพิ่มขึ้น)

---

## ⚠️ Trade-offs

### Pros:
- ✅ เพิ่มจำนวนหุ้นที่เทรดได้
- ✅ HON-HAI จะผ่านเกณฑ์
- ✅ อาจมีหุ้นอื่นๆ ผ่านเกณฑ์เพิ่มขึ้น

### Cons:
- ⚠️ RRR requirement ลดลง (1.3 → 1.25)
- ⚠️ min_prob ลดลง (51.5% → 51.0%) → Prob% อาจลดลงเล็กน้อย
- ⚠️ คุณภาพอาจลดลงเล็กน้อย

---

## 🚀 Next Steps

1. ✅ **Changes Applied** - min_prob=51.0%, RRR >= 1.25
2. ⏳ **Re-run Backtest** - ต้องรัน backtest ใหม่ด้วย min_prob=51.0%
3. ⏳ **Check Results** - ดูว่ามีหุ้นเพิ่มขึ้นหรือไม่
4. ⏳ **Compare with V12.3** - เปรียบเทียบผลลัพธ์

---

## 📝 Command to Re-run

```bash
# Clean old results
rm logs/trade_history_TAIWAN.csv

# Run backtest with new min_prob=51.0%
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# Calculate metrics
python scripts/calculate_metrics.py
```

---

**Last Updated:** 2026-02-13  
**Version:** V12.4  
**Status:** ✅ **CHANGES APPLIED** (Need to re-run backtest)

