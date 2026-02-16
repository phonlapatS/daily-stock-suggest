# Simplified System V6.1 - Back to Original Simple Approach

## 🎯 เป้าหมาย

กลับไปใช้ระบบเดิมที่เรียบง่าย:
- **ไม่มี Indicator** (ADX, SMA50, Volume Ratio, RSI)
- **ไม่มี Trailing Stop** - ใช้แค่ 1-day exit
- **ไม่มี Filter ซับซ้อน** - แค่ Pattern Matching จาก History Statistics

---

## ✅ สิ่งที่ลบออก (V6.1)

### 1. Indicators ที่ลบออก
- ❌ ADX Filter
- ❌ SMA50 Filter  
- ❌ Volume Ratio Filter
- ❌ RSI (ไม่ได้ใช้อยู่แล้ว)
- ❌ Volume Advance

### 2. Exit Strategy ที่ลบออก
- ❌ Trailing Stop Loss
- ❌ Take Profit
- ❌ ATR Multiplier
- ❌ Max Hold Days

### 3. Filters ที่ลบออก
- ❌ China FOMO Volume Filter
- ❌ Market Regime Filter (SMA50)
- ❌ ADX Pre-filter

---

## ✅ สิ่งที่เหลืออยู่ (Simple System)

### Core Logic (เหมือนเดิม)
1. **Pattern Detection**: นับวันที่หุ้นวิ่งเกิน threshold (มีแค่ + และ - ไม่มี .)
2. **History Statistics**: หา Prob, AvgWin, AvgLoss, RRR จาก pattern history
3. **Gatekeeper**: Prob > 60% และ RRR > 1.2
4. **1-Day Exit**: ทายวันพรุ่งนี้ → ตรวจผลวันรุ่งขึ้น → Log ผลลัพธ์

### Pattern Matching
```python
# Simple: แค่ดูว่า price move เกิน threshold หรือไม่
if pct_change > threshold:
    pattern += '+'
elif pct_change < -threshold:
    pattern += '-'
# ไม่มี '.' - skip ถ้าไม่เกิน threshold
```

### Statistics Calculation
```python
# จาก pattern history
Prob% = (Wins / Total) × 100
AvgWin% = Average of winning trades
AvgLoss% = Average of losing trades
RRR = AvgWin% / AvgLoss%
```

### Exit Strategy
```python
# Simple: 1-day exit only
trade_ret = next_day_return
# ไม่มี Trailing Stop, ไม่มี Take Profit
```

---

## 📊 เปรียบเทียบ

| Feature | V6.0 (Complex) | V6.1 (Simple) |
|---------|----------------|---------------|
| **Indicators** | ADX, SMA50, Volume Ratio | ❌ None |
| **Exit Strategy** | Trailing Stop + Take Profit | ✅ 1-Day Exit |
| **Filters** | Volume, Regime, ADX | ❌ None |
| **Complexity** | สูง | ✅ ต่ำ |
| **Philosophy** | Indicator-based | ✅ Pure Statistics |

---

## 🎯 เป้าหมายของระบบ

1. **Pattern Matching**: จาก history statistics เท่านั้น
2. **Probability**: ทายว่าพรุ่งนี้จะขึ้นหรือลง
3. **Logging**: บันทึกผลว่าทายถูก/ผิดกี่ครั้ง และ RRR
4. **Simple**: ไม่ต้องใช้ model หรือ indicator เยอะ

---

## 📝 สรุป

**V6.1 = ระบบเดิมที่เรียบง่าย**
- ✅ Pattern Matching จาก History
- ✅ Statistics (Prob, AvgWin, AvgLoss, RRR)
- ✅ 1-Day Exit
- ✅ Logging ผลลัพธ์
- ❌ ไม่มี Indicator (ตอนนี้)
- ❌ ไม่มี Trailing Stop
- ❌ ไม่มี Filter ซับซ้อน (ตอนนี้)

**Philosophy**: "เอาข้อมูลมาหาความน่าจะเป็นว่าพรุ่งนี้จะขึ้นหรือลง จากสถิติความน่าจะเป็น แค่นั้นเอง"

---

## 📚 Indicator Filters Archive

**หมายเหตุ**: Indicator Filters ที่ดี (ADX, SMA50, Volume Ratio) ถูกบันทึกไว้ใน `docs/INDICATOR_FILTERS_ARCHIVE.md` สำหรับอนาคต

ถ้าต้องการเพิ่ม filter เพื่อปรับปรุงผลลัพธ์ สามารถนำกลับมาใช้ได้:
- **ADX Filter**: เหมาะกับ Trend Following (US Market)
- **SMA50 Filter**: เหมาะกับ LONG ONLY (China Market)
- **Volume Ratio Filter**: เหมาะกับ Mean Reversion (China Market)

ดูรายละเอียดเพิ่มเติมใน `docs/INDICATOR_FILTERS_ARCHIVE.md`

