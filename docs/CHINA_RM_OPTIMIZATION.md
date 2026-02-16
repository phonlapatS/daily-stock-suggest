# China Market - Risk Management Optimization

## 📊 Current Status

### Current RM Parameters:
- **SL:** 1.5%
- **TP:** 4.5%
- **RRR (Theoretical):** 3.0
- **Max Hold:** 6 days
- **Trailing Stop:** Activate 1.5%, Distance 50%

### Current RRR (Actual):
- MEITUAN: 1.22
- BYD: 1.00
- JD-COM: 1.20
- LI-AUTO: 1.00
- **Average:** ~1.11 ⚠️ ต่ำมาก!

### Problem:
- RRR จริง (1.11) ต่ำกว่า theoretical (3.0) มาก
- แสดงว่า TP 4.5% อาจสูงเกินไป (ถึง TP น้อย)
- หรือ trailing stop exit ก่อนถึง TP

---

## 💡 Optimization Strategy

### Goal:
- เพิ่ม RRR จริงให้สูงขึ้น (target: 1.5+)
- คุ้มกับความเสี่ยง (RRR >= 1.5)

### Approach 1: Tighten SL + Increase TP (Recommended)

**Changes:**
- SL: 1.5% → 1.2% (tighter SL)
- TP: 4.5% → 5.5% (higher TP)
- RRR: 3.0 → 4.58 (theoretical)
- Max Hold: 6 → 8 days (ให้มีเวลาไปถึง TP)
- Trailing: Activate 1.0% (activate early), Distance 40% (let profits run)

**Rationale:**
- Tighter SL → RRR สูงขึ้น
- Higher TP → RRR สูงขึ้น
- Longer hold → มีเวลาไปถึง TP
- Early trailing → lock profits early

**Expected:**
- RRR จริง: 1.11 → 1.5+ ✅

---

### Approach 2: Moderate (Balanced)

**Changes:**
- SL: 1.5% → 1.3% (slightly tighter)
- TP: 4.5% → 5.0% (moderate increase)
- RRR: 3.0 → 3.85 (theoretical)
- Max Hold: 6 → 7 days
- Trailing: Activate 1.2%, Distance 45%

**Rationale:**
- Balanced approach
- ไม่เสี่ยงมาก

**Expected:**
- RRR จริง: 1.11 → 1.3-1.4

---

### Approach 3: Aggressive (Maximum RRR)

**Changes:**
- SL: 1.5% → 1.0% (very tight)
- TP: 4.5% → 6.0% (high TP)
- RRR: 3.0 → 6.0 (theoretical)
- Max Hold: 6 → 10 days
- Trailing: Activate 1.0%, Distance 30%

**Rationale:**
- Maximum RRR
- แต่เสี่ยงมาก (SL ต่ำ)

**Expected:**
- RRR จริง: 1.11 → 1.6-1.8
- แต่ Win Rate อาจลดลง

---

## 🎯 Recommended: Approach 1

### Final Parameters:
```python
RM_STOP_LOSS = 1.2        # ลดจาก 1.5% → 1.2% (tighter SL)
RM_TAKE_PROFIT = 5.5      # เพิ่มจาก 4.5% → 5.5% (higher TP)
RM_MAX_HOLD = 8           # เพิ่มจาก 6 → 8 (ให้มีเวลาไปถึง TP)
RM_TRAIL_ACTIVATE = 1.0   # ลดจาก 1.5% → 1.0% (activate early)
RM_TRAIL_DISTANCE = 40.0  # ลดจาก 50% → 40% (let profits run)
```

### Expected Results:
- **RRR (Theoretical):** 4.58 ✅
- **RRR (Actual):** 1.5+ ✅ (เพิ่มจาก 1.11)
- **Win Rate:** อาจลดลงเล็กน้อย (SL ต่ำ)
- **Count:** อาจลดลงเล็กน้อย (SL ต่ำ)

---

## ⚠️ Trade-offs

### Pros:
- ✅ RRR สูงขึ้น (1.11 → 1.5+)
- ✅ คุ้มกับความเสี่ยงมากขึ้น
- ✅ Trailing stop lock profits early

### Cons:
- ⚠️ SL ต่ำ (1.2%) → โดน SL บ่อยขึ้น
- ⚠️ TP สูง (5.5%) → ถึง TP น้อยลง
- ⚠️ Win Rate อาจลดลง

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY TO IMPLEMENT**

