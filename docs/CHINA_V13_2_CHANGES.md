# China Market V13.2 - Risk Management Optimization

## 📊 Changes Summary

### Risk Management Parameters:

| Parameter | V13.1 | V13.2 | Change | Rationale |
|-----------|-------|-------|--------|-----------|
| **SL** | 1.5% | 1.2% | -0.3% | Tighter SL → Higher RRR |
| **TP** | 4.5% | 5.5% | +1.0% | Higher TP → Higher RRR |
| **RRR (Theoretical)** | 3.0 | 4.58 | +1.58 | Much better RRR |
| **Max Hold** | 6 days | 8 days | +2 days | More time to reach TP |
| **Trail Activate** | 1.5% | 1.0% | -0.5% | Activate early to lock profits |
| **Trail Distance** | 50% | 40% | -10% | Let profits run more |

---

## 🎯 Goals

### Primary Goal:
- **เพิ่ม RRR จริง** จาก 1.11 → 1.5+ ✅

### Secondary Goals:
- คุ้มกับความเสี่ยงมากขึ้น
- Lock profits early (trailing stop)
- ให้มีเวลาไปถึง TP (longer hold)

---

## 📈 Expected Results

### Before (V13.1):
- **RRR (Actual):** ~1.11 ⚠️ ต่ำ
- **RRR (Theoretical):** 3.0
- **AvgWin%:** ~1.8%
- **AvgLoss%:** ~1.6%

### After (V13.2):
- **RRR (Actual):** 1.5+ ✅ (เพิ่มขึ้น)
- **RRR (Theoretical):** 4.58 ✅
- **AvgWin%:** อาจเพิ่มขึ้น (TP สูงขึ้น)
- **AvgLoss%:** อาจลดลง (SL ต่ำลง)

---

## ⚠️ Trade-offs

### Pros:
- ✅ RRR สูงขึ้นมาก (1.11 → 1.5+)
- ✅ Theoretical RRR ดีมาก (4.58)
- ✅ Trailing stop lock profits early
- ✅ Longer hold → มีเวลาไปถึง TP

### Cons:
- ⚠️ SL ต่ำ (1.2%) → โดน SL บ่อยขึ้น
- ⚠️ TP สูง (5.5%) → ถึง TP น้อยลง
- ⚠️ Win Rate อาจลดลง
- ⚠️ Count อาจลดลง (SL ต่ำ)

---

## 📝 Implementation

### Code Changes:
```python
# scripts/backtest.py
elif is_china_market:
    RM_STOP_LOSS = 1.2        # V13.2: ลดจาก 1.5% → 1.2%
    RM_TAKE_PROFIT = 5.5      # V13.2: เพิ่มจาก 4.5% → 5.5%
    RM_MAX_HOLD = 8           # V13.2: เพิ่มจาก 6 → 8
    RM_TRAIL_ACTIVATE = 1.0   # V13.2: ลดจาก 1.5% → 1.0%
    RM_TRAIL_DISTANCE = 40.0  # V13.2: ลดจาก 50% → 40%
```

---

## 🚀 Next Steps

1. ✅ **Apply RM changes** (done)
2. ⏳ **Run backtest** (pending)
3. ⏳ **Evaluate results** (pending)
4. ⏳ **Compare with V13.1** (pending)

---

**Last Updated:** 2026-02-13  
**Version:** V13.2  
**Status:** ✅ **IMPLEMENTED** - Ready for testing

