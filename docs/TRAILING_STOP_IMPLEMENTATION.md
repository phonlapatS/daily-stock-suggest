# Trailing Stop Loss Implementation - ปรับปรุง RRR ให้ > 2.0

## 📋 สรุปการปรับปรุง

### ✅ สิ่งที่ทำเสร็จแล้ว

1. **เพิ่มฟังก์ชัน Trailing Stop ใน BasePatternEngine**
   - `calculate_atr()`: คำนวณ Average True Range
   - `simulate_trailing_stop_exit()`: จำลองการ exit ด้วย Trailing Stop
   - รองรับทั้ง LONG และ SHORT positions

2. **ปรับปรุง backtest.py ให้ใช้ Trailing Stop**
   - เปลี่ยนจาก 1-day exit เป็น Trailing Stop Loss
   - ปรับ ATR Multiplier ตามตลาด:
     - **US Market (Trend Following)**: ATR × 2.5 (หลวม)
     - **Thai/China Market (Mean Reversion)**: ATR × 1.5 (แน่น)
   - Max Hold = 10 days

3. **สร้างสคริปต์วิเคราะห์**
   - `improve_rrr_with_trailing_stop.py`: วิเคราะห์ผลกระทบของ Trailing Stop
   - `backtest_with_trailing_stop.py`: ทดสอบ Trailing Stop Strategy

## 🎯 Trailing Stop Logic

### สำหรับ LONG Position:
```
Initial Stop = Entry Price - (ATR × Multiplier)
Trailing Stop = Highest Price - (ATR × Multiplier)
Update: เมื่อ High ใหม่ > Highest Price
Exit: เมื่อ Low <= Trailing Stop หรือ Max Hold Days
```

### สำหรับ SHORT Position:
```
Initial Stop = Entry Price + (ATR × Multiplier)
Trailing Stop = Lowest Price + (ATR × Multiplier)
Update: เมื่อ Low ใหม่ < Lowest Price
Exit: เมื่อ High >= Trailing Stop หรือ Max Hold Days
```

## 📊 ผลลัพธ์ที่คาดหวัง

### ปัจจุบัน (1-day exit):
- AvgWin: 1.71%
- AvgLoss: 1.35%
- **RRR: 1.27** ❌ (ต่ำกว่า 2.0)
- Win Rate: 44.2%

### หลังใช้ Trailing Stop:
- AvgWin: เพิ่มขึ้น (ให้กำไรเดินทาง)
- AvgLoss: คงที่หรือลดลง (Trailing Stop ป้องกัน)
- **RRR: > 2.0** ✅ (เป้าหมาย)
- Win Rate: อาจลดลงเล็กน้อย (แต่ RRR สูงขึ้น)

## 🔧 การใช้งาน

### รัน Backtest ด้วย Trailing Stop:
```bash
python scripts/backtest.py PTTEP SET --bars 500
```

### วิเคราะห์ผลกระทบ:
```bash
python scripts/improve_rrr_with_trailing_stop.py
```

## 📝 สิ่งที่ต้องทำต่อ

1. ✅ **ปรับปรุง Engine** - เสร็จแล้ว
2. ✅ **ปรับปรุง backtest.py** - เสร็จแล้ว
3. ⏳ **ทดสอบ RRR > 2.0** - ต้องรัน backtest จริงๆ
4. ⏳ **ปรับ Multiplier** - ตามผลการทดสอบ

## 🎯 เป้าหมาย

- **RRR > 2.0** สำหรับทุกตลาด
- ให้กำไรเดินทาง (let profit run)
- Lock profit เมื่อ price pullback
- ปรับตามพฤติกรรมตลาด (Trend Following vs Mean Reversion)

## 📌 หมายเหตุ

- Trailing Stop จะช่วยให้ RRR สูงขึ้นโดยการ:
  1. ให้กำไรเดินทาง (ไม่ exit เร็วเกินไป)
  2. Lock profit เมื่อ price pullback
  3. ป้องกัน loss ใหญ่ด้วย Initial Stop Loss

- ATR Multiplier จะปรับตามตลาด:
  - **Trend Following (US)**: หลวม (2.5) เพื่อให้กำไรเดินทาง
  - **Mean Reversion (TH/CN)**: แน่น (1.5) เพื่อ lock profit เร็ว

