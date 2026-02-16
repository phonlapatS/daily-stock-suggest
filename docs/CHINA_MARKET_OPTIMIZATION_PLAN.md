# China Market - Optimization Plan

## 📊 Current Status Summary

### Passing Stocks: 1 stock
- **MEITUAN (3690):** Prob 76.9%, RRR 1.22, Count 39 ✅

### Current Criteria:
- Prob >= 55%
- RRR >= 1.2
- Count >= 15

### Total China Stocks: 10

---

## 🔍 Near Passing Stocks Analysis

### High Prob% but Low RRR/Count:
1. **LI-AUTO (2015):** Prob 80.0%, RRR 1.00, Count 10
   - Gap: RRR -0.2, Count -5
   
2. **XIAOMI (1810):** Prob 77.8%, RRR 0.96, Count 9
   - Gap: RRR -0.24, Count -6

### Good Prob% but Low RRR:
3. **BYD (1211):** Prob 59.1%, RRR 1.00, Count 159
   - Gap: RRR -0.2

### Low Prob% but Good RRR:
4. **JD-COM (9618):** Prob 54.2%, RRR 1.20, Count 24
   - Gap: Prob -0.8%

---

## 💡 Optimization Strategies

### Strategy 1: Lower RRR to 1.0 (Quick Win)

**Change:**
- RRR >= 1.2 → RRR >= 1.0

**Expected Results:**
- ✅ MEITUAN (76.9%, RRR 1.22, Count 39) - ผ่านอยู่แล้ว
- ✅ LI-AUTO (80.0%, RRR 1.00, Count 10) - ผ่าน (แต่ Count ต่ำ)
- ✅ BYD (59.1%, RRR 1.00, Count 159) - ผ่าน
- **Total: 3 stocks** (เพิ่มจาก 1 → 3)

**Pros:**
- เพิ่มหุ้นที่ผ่าน (1 → 3)
- LI-AUTO และ BYD มี Prob% ดี

**Cons:**
- RRR requirement ลดลง (1.2 → 1.0)
- LI-AUTO Count ต่ำ (10) - ต้องระวัง

---

### Strategy 2: Lower Prob to 53% (Get JD-COM)

**Change:**
- Prob >= 55% → Prob >= 53%

**Expected Results:**
- ✅ MEITUAN (76.9%, RRR 1.22, Count 39) - ผ่านอยู่แล้ว
- ✅ JD-COM (54.2%, RRR 1.20, Count 24) - ผ่าน
- **Total: 2 stocks** (เพิ่มจาก 1 → 2)

**Pros:**
- JD-COM มี RRR ดี (1.20)
- Count สมดุล (24)

**Cons:**
- เพิ่มแค่ 1 หุ้น
- Prob% ลดลงเล็กน้อย

---

### Strategy 3: Combined (RRR 1.0 + Prob 53%)

**Change:**
- RRR >= 1.2 → RRR >= 1.0
- Prob >= 55% → Prob >= 53%

**Expected Results:**
- ✅ MEITUAN (76.9%, RRR 1.22, Count 39) - ผ่านอยู่แล้ว
- ✅ LI-AUTO (80.0%, RRR 1.00, Count 10) - ผ่าน (แต่ Count ต่ำ)
- ✅ BYD (59.1%, RRR 1.00, Count 159) - ผ่าน
- ✅ JD-COM (54.2%, RRR 1.20, Count 24) - ผ่าน
- **Total: 4 stocks** (เพิ่มจาก 1 → 4)

**Pros:**
- เพิ่มหุ้นที่ผ่านมาก (1 → 4)
- ครอบคลุมหุ้นที่มี metrics ดี

**Cons:**
- RRR และ Prob% ลดลง
- LI-AUTO Count ต่ำ (10)

---

### Strategy 4: Lower Count to 10 (Get LI-AUTO & XIAOMI)

**Change:**
- Count >= 15 → Count >= 10

**Expected Results:**
- ✅ MEITUAN (76.9%, RRR 1.22, Count 39) - ผ่านอยู่แล้ว
- ❌ LI-AUTO (80.0%, RRR 1.00, Count 10) - ยังไม่ผ่าน (RRR < 1.2)
- ❌ XIAOMI (77.8%, RRR 0.96, Count 9) - ยังไม่ผ่าน (RRR < 1.2)

**Note:** ต้องลด RRR ด้วยถึงจะได้ LI-AUTO และ XIAOMI

---

## 🎯 Recommended: Strategy 1 (Lower RRR to 1.0)

### Rationale:
1. ✅ เพิ่มหุ้นที่ผ่าน (1 → 3)
2. ✅ LI-AUTO และ BYD มี Prob% ดี (80%, 59%)
3. ✅ RRR 1.0 ยังสมเหตุสมผล (ไม่ต่ำเกินไป)
4. ✅ ไม่ต้องเปลี่ยน Prob% requirement

### Implementation:
```python
# ใน calculate_metrics.py
china_trend = summary_df[
    (summary_df['Country'] == 'CN') & 
    (summary_df['Prob%'] >= 55.0) &
    (summary_df['RR_Ratio'] >= 1.0) &  # ลดจาก 1.2 → 1.0
    (summary_df['Count'] >= 15)
]
```

### Expected Results:
- **3 stocks passing:**
  1. MEITUAN (76.9%, RRR 1.22, Count 39)
  2. LI-AUTO (80.0%, RRR 1.00, Count 10) ⚠️ Count ต่ำ
  3. BYD (59.1%, RRR 1.00, Count 159)

---

## ⚠️ Considerations

### LI-AUTO Count ต่ำ (10):
- ข้อมูลไม่เพียงพอ (Count < 15)
- อาจไม่น่าเชื่อถือ
- **Recommendation:** ใช้ Count >= 15 (ไม่ลด Count requirement)

### Alternative: Count >= 15 + RRR >= 1.0
- ✅ MEITUAN (39) - ผ่าน
- ✅ BYD (159) - ผ่าน
- ❌ LI-AUTO (10) - ไม่ผ่าน (Count < 15)
- **Total: 2 stocks** (เพิ่มจาก 1 → 2)

---

## 📝 Next Steps

1. ✅ **Analyze current status** (done)
2. ⏳ **Test Strategy 1** (RRR >= 1.0, Count >= 15)
3. ⏳ **Evaluate results**
4. ⏳ **Consider Strategy 3** (RRR 1.0 + Prob 53%) if needed

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR TESTING**

