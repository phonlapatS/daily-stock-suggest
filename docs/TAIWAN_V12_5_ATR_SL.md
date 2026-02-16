# Taiwan Market V12.5 - ATR-based SL/TP

## 📋 Summary
เปลี่ยนจาก Fixed SL/TP เป็น ATR-based SL/TP เพื่อให้ยืดหยุ่นและเอาไปใช้จริงง่ายขึ้น (auto system)

---

## ✅ Changes

### Risk Management Parameters:

**Before (V12.4 - Fixed):**
- `RM_STOP_LOSS`: 1.0% (fixed)
- `RM_TAKE_PROFIT`: 6.5% (fixed)
- `RM_USE_ATR`: False

**After (V12.5 - ATR-based):**
- `RM_ATR_SL`: 1.0x (ATR multiplier)
- `RM_ATR_TP`: 6.5x (ATR multiplier)
- `RM_USE_ATR`: True

**Unchanged:**
- `RM_MAX_HOLD`: 10 days
- `RM_TRAIL_ACTIVATE`: 1.0%
- `RM_TRAIL_DISTANCE`: 30.0%

---

## 🎯 Benefits

### 1. **Flexibility (ยืดหยุ่น)**
- ✅ หุ้นที่ผันผวนมาก → SL กว้างขึ้น (ตาม ATR)
- ✅ หุ้นที่ผันผวนน้อย → SL แคบลง (ตาม ATR)
- ✅ AvgLoss% ไม่ lock ไว้ที่ 1.0% แล้ว

### 2. **Realistic (สมจริง)**
- ✅ ใช้ความผันผวนจริงของหุ้น (ATR)
- ✅ ปรับตาม market conditions

### 3. **Auto System (ใช้งานจริงง่าย)**
- ✅ ไม่ต้องตั้งค่า fixed SL/TP สำหรับแต่ละหุ้น
- ✅ ระบบคำนวณ SL/TP อัตโนมัติตาม ATR

---

## 📊 How It Works

### ATR Calculation:
```
ATR = Average True Range (14 periods)
True Range = max(
    High - Low,
    |High - Previous Close|,
    |Low - Previous Close|
)
```

### SL/TP Calculation:
```
Actual SL% = (ATR × 1.0) / Entry Price × 100
Actual TP% = (ATR × 6.5) / Entry Price × 100

Capped at:
- Max SL: 5.0% (safety)
- Max TP: 12.0% (safety)
```

### Example:
```
หุ้น A: ATR = 2%, Entry = 100
  → SL = (2 × 1.0) / 100 × 100 = 2.0%
  → TP = (2 × 6.5) / 100 × 100 = 13.0% (capped at 12.0%)

หุ้น B: ATR = 0.5%, Entry = 100
  → SL = (0.5 × 1.0) / 100 × 100 = 0.5%
  → TP = (0.5 × 6.5) / 100 × 100 = 3.25%
```

---

## 🔧 Testing Parameters

สามารถ override ได้ผ่าน kwargs:
```python
# Test different ATR multipliers
backtest_single(..., atr_sl_mult=1.0, atr_tp_mult=6.5)
```

---

## 📝 Files Modified

1. `scripts/backtest.py`:
   - Lines 468-482: Taiwan RM parameters (V12.5)
   - Lines 715: Updated comments

---

## 🚀 Next Steps

1. ✅ **Code Updated**: เปลี่ยนเป็น ATR-based แล้ว
2. ⏳ **Test**: รัน backtest เพื่อดูผลลัพธ์
3. ⏳ **Compare**: เปรียบเทียบกับ V12.4 (fixed SL)

---

**Date**: 2024-12-XX  
**Version**: V12.5  
**Market**: Taiwan Only  
**Status**: ✅ Code Updated - Ready for Testing

