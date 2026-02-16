# China Market V13.1 - Test Results Summary

## 📊 Current Status

### Configuration Applied:
- **Display Criteria:**
  - Prob >= 53%
  - RRR >= 0.95 (ลดจาก 1.0)
  - Count >= 10 (ลดจาก 15)

- **Risk Management (Updated in backtest.py):**
  - SL: 1.5%
  - TP: 4.5% (เพิ่มจาก 3.5%)
  - Max Hold: 6 days (เพิ่มจาก 5)
  - RRR: 3.0 (theoretical)

- **Gatekeeper (Updated in backtest.py):**
  - min_prob: 51.0% (ลดจาก 53.0%)

---

## ⚠️ Issue Found

### Problem:
- Backtest skip symbols ที่มีอยู่ใน `symbol_performance.csv` แล้ว
- เมื่อรันหุ้นเดียว (เช่น `python scripts/backtest.py 3690 HKEX`) จะบันทึกไปที่ `trade_history.csv` แทน `trade_history_CHINA.csv`
- `calculate_metrics.py` ใช้ `trade_history_*.csv` (split files) ไม่ใช่ `trade_history.csv`

### Solution Needed:
1. ลบ `symbol_performance.csv` เพื่อบังคับให้รันใหม่
2. รัน backtest ผ่าน `--group CHINA` เพื่อให้บันทึกไปที่ `trade_history_CHINA.csv`
3. หรือแก้ไข `calculate_metrics.py` ให้อ่าน `trade_history.csv` ด้วย

---

## 📈 Expected Results (Based on Previous Data)

### Before V13.1 (V13.0):
- **Passing:** 3 stocks
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### After V13.1 (Expected):
- **Passing:** 4 stocks (+1)
  - LI-AUTO (80.0%, RRR 1.00, Count 10) ⚠️ Count ต่ำ
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### After RM Changes (After Re-running Backtest):
- **Expected:** RRR และ Count เพิ่มขึ้น
- **Expected:** อาจได้หุ้นเพิ่ม (XIAOMI, etc.)

---

## 🎯 Next Steps

### To See Full Results:

1. **Delete symbol_performance.csv:**
   ```bash
   Remove-Item "data/symbol_performance.csv" -Force
   ```

2. **Run backtest with --group CHINA:**
   ```bash
   python scripts/backtest.py --full --bars 2500 --group CHINA
   ```

3. **Calculate metrics:**
   ```bash
   python scripts/calculate_metrics.py
   ```

### Alternative (If backtest still skips):

1. **Delete all trade history files:**
   ```bash
   Remove-Item "logs/trade_history*.csv" -Force
   ```

2. **Run backtest:**
   ```bash
   python scripts/backtest.py --full --bars 2500 --group CHINA
   ```

3. **Calculate metrics:**
   ```bash
   python scripts/calculate_metrics.py
   ```

---

## 📝 Summary

### Changes Made:
1. ✅ **Display Criteria:** RRR >= 0.95, Count >= 10
2. ✅ **RM Parameters:** TP 4.5%, Max Hold 6 days
3. ✅ **Gatekeeper:** min_prob 51.0%

### Status:
- ⏳ **Display criteria applied** (done)
- ⏳ **RM parameters updated** (done)
- ⏳ **Backtest pending** (needs re-run to see RM impact)

### Expected Outcome:
- 4 stocks passing (เพิ่มจาก 3 → 4)
- RRR และ Count เพิ่มขึ้น (หลังรัน backtest ใหม่)

---

**Last Updated:** 2026-02-13  
**Version:** V13.1  
**Status:** ⏳ **CONFIGURATION COMPLETE** - Backtest re-run needed to see full results

