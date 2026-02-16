# China Market V13.1 - Changes & Results

## 📊 Changes Summary

### Display Criteria (calculate_metrics.py):
- **RRR:** >= 1.0 → >= 0.95 (ลด 0.05)
- **Count:** >= 15 → >= 10 (ลด 5)
- **Prob:** >= 53% (คงเดิม)

### Risk Management (backtest.py):
- **TP:** 3.5% → 4.5% (เพิ่ม 1.0%)
- **SL:** 1.5% (คงเดิม)
- **RRR:** 2.33 → 3.0 (theoretical)
- **Max Hold:** 5 → 6 days (เพิ่ม 1 วัน)

### Gatekeeper (backtest.py):
- **min_prob:** 53.0% → 51.0% (ลด 2%)
- **Expected:** เพิ่ม Count ของหุ้น

---

## ✅ Expected Results

### Before (V13.0):
- **Passing:** 3 stocks
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### After (V13.1 - Display Only):
- **Passing:** 4 stocks (+1)
  - LI-AUTO (80.0%, RRR 1.00, Count 10) ⚠️ Count ต่ำ
  - MEITUAN (76.9%, RRR 1.22, Count 39)
  - BYD (59.1%, RRR 1.00, Count 159)
  - JD-COM (54.2%, RRR 1.20, Count 24)

### After (V13.1 - After Backtest):
- **Expected:** RRR และ Count เพิ่มขึ้น
- **Expected:** อาจได้หุ้นเพิ่ม (XIAOMI, etc.)

---

## 🎯 Goals

1. ✅ **เพิ่มหุ้นที่ผ่าน** (3 → 4-5)
2. ✅ **เพิ่ม RRR** (ปรับ TP)
3. ✅ **เพิ่ม Count** (ปรับ min_prob)

---

## ⚠️ Considerations

### LI-AUTO Count ต่ำ (10):
- ข้อมูลไม่เพียงพอ
- อาจไม่น่าเชื่อถือ
- **Recommendation:** Monitor closely

### RM Changes:
- TP เพิ่มขึ้น (3.5% → 4.5%) → อาจถึง TP น้อยลง
- Max Hold เพิ่มขึ้น (5 → 6) → ให้เวลาไปถึง TP
- min_prob ลดลง (53% → 51%) → Count เพิ่มขึ้น

---

## 📝 Next Steps

1. ✅ **Apply display criteria changes** (done)
2. ⏳ **Run backtest with new RM parameters**
3. ⏳ **Evaluate results**
4. ⏳ **Document final configuration**

---

**Last Updated:** 2026-02-13  
**Version:** V13.1  
**Status:** ⏳ **IN PROGRESS** - Display criteria applied, backtest pending

