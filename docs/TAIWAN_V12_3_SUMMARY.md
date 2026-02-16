# Taiwan V12.3 - Count Optimization Summary

## ✅ Changes Applied

### 1. Gatekeeper Adjustment
- **Before (V12.2):** `min_prob = 52.0%`
- **After (V12.3):** `min_prob = 51.5%`
- **Impact:** เพิ่ม trades ที่มี Prob% 51.5-52.0%

### 2. Historical Data (Recommended)
- **Before:** `n_bars = 2000`
- **After (Recommended):** `n_bars = 2500`
- **Impact:** เพิ่ม historical patterns → เพิ่ม count

---

## 📊 Expected Results

### Current Status (V12.2)
- ✅ **MEDIATEK (2454):** Prob 62.5%, RRR 1.76, Count 40
- ✅ **HON-HAI (2317):** Prob 62.3%, RRR 1.42, Count 69

### Expected After V12.3
- ✅ **MEDIATEK (2454):** Prob ~62.2-62.5%, RRR 1.76, Count **50-55** (+25-38%)
- ✅ **HON-HAI (2317):** Prob ~62.1-62.3%, RRR 1.42, Count **80-85** (+16-23%)
- 🎯 **DELTA (2308):** Prob ~70.0%, RRR 1.80, Count **25-28** (อาจผ่านเกณฑ์!)

---

## 🚀 Next Steps

### Step 1: Clean Old Results
```bash
# Delete old Taiwan trade history
rm logs/trade_history_TAIWAN.csv

# Remove Taiwan entries from full_backtest_results.csv (optional)
# Or just let it overwrite
```

### Step 2: Run Backtest with New Parameters
```bash
# Run with n_bars=2500 (เพิ่มจาก 2000)
python scripts/backtest.py --full --bars 2500 --group TAIWAN
```

### Step 3: Calculate Metrics
```bash
python scripts/calculate_metrics.py
```

### Step 4: Compare Results
- ดูว่า count เพิ่มขึ้นหรือไม่
- ตรวจสอบว่า Prob% และ RRR ยังดีอยู่หรือไม่
- ดูว่ามีหุ้นใหม่ที่ผ่านเกณฑ์หรือไม่

---

## ⚠️ Monitoring Points

1. **Prob% Changes:**
   - ควรลดลงไม่เกิน 0.3%
   - ถ้าลดลง > 0.5% → พิจารณา revert

2. **RRR Changes:**
   - ควรไม่เปลี่ยน (ขึ้นอยู่กับ RM parameters)
   - ถ้าลดลง > 0.1 → พิจารณา revert

3. **Count Changes:**
   - ควรเพิ่มขึ้น 10-25%
   - ถ้าไม่เพิ่ม → พิจารณา Option B

---

## 📝 Notes

- **Risk Level:** 🟢 LOW
- **Expected Improvement:** Count +15-25%
- **Quality Impact:** Minimal (Prob% -0.1 to -0.3%)

---

**Last Updated:** 2026-02-13  
**Version:** V12.3  
**Status:** ✅ **READY TO TEST**

