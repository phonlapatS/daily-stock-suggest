# China Market - Realistic Settings Test Plan

## 🎯 เป้าหมาย

ทดสอบค่าที่แนะนำเพื่อหาค่าที่เหมาะสมกับความเป็นจริง:
- Max Hold: 5-6 days (ไม่เกิน 7)
- TP: 3.5-4.0% (ไม่สูงเกินไป)
- SL: 1.0-1.2% (Tight)

---

## 📊 Test Parameters

### TP Options:
- 3.5% (ต่ำ - ถึงง่าย)
- 4.0% (ปานกลาง)
- 4.5% (สูง)

### Max Hold Options:
- 5 days (สั้น)
- 6 days (ปานกลาง)
- 7 days (สูงสุดที่แนะนำ)

### SL Options:
- 1.0% (Tight)
- 1.2% (ปานกลาง)

**Total Tests:** 3 × 3 × 2 = 18 combinations

---

## ✅ Success Criteria

### 1. TP Hit Rate
- **Target:** >= 20-30%
- **Acceptable:** >= 15%

### 2. MAX_HOLD Rate
- **Target:** < 50%
- **Acceptable:** < 60%

### 3. RRR
- **Target:** >= 1.3
- **Acceptable:** >= 1.2

### 4. Hold Days <= 7
- **Target:** > 80% ของ trades
- **Acceptable:** > 70%

### 5. MAX_HOLD Exits Return
- **Target:** > 0.5%
- **Acceptable:** > 0%

---

## 📋 Score System

### TP Hit Rate:
- >= 25%: +3 points
- >= 20%: +2 points
- >= 15%: +1 point

### MAX_HOLD Rate:
- < 40%: +3 points
- < 50%: +2 points
- < 60%: +1 point

### Hold Days <= 7:
- < 10% hold >7 days: +2 points
- < 20% hold >7 days: +1 point

### RRR:
- >= 1.4: +3 points
- >= 1.3: +2 points
- >= 1.2: +1 point

### MAX_HOLD Return:
- > 0.5%: +2 points
- > 0%: +1 point

**Max Score:** 13 points

---

## 🧪 Testing

### Run Test:
```bash
python scripts/test_china_realistic_settings.py
```

**Expected Time:** 30-60 minutes (18 tests)

**Output:**
- Comparison table (sorted by score)
- Best combination
- Assessment (Acceptable or Not)

---

## 📊 Expected Results

### Best Case Scenario:
- TP: 4.0%, Max Hold: 6 days, SL: 1.2%
- TP Hit Rate: 25-30% ✅
- MAX_HOLD Rate: 30-40% ✅
- RRR: 1.4-1.5 ✅
- Hold >7 days: < 10% ✅
- Score: 10-13 points ✅

### Acceptable Scenario:
- TP: 3.5-4.0%, Max Hold: 5-6 days, SL: 1.0-1.2%
- TP Hit Rate: 20-25% ✅
- MAX_HOLD Rate: 40-50% ✅
- RRR: 1.3-1.4 ✅
- Hold >7 days: < 20% ✅
- Score: 8-10 points ✅

---

## 🎯 Decision Criteria

### ถ้าผลลัพธ์ Acceptable:
✅ **ใช้ค่าที่ดีที่สุด**
- อัพเดท `backtest.py`
- บันทึกผลลัพธ์
- ทดสอบอีกครั้งเพื่อยืนยัน

### ถ้าผลลัพธ์ Not Acceptable:
⚠️ **พิจารณา:**
- ปรับ parameters
- ทดสอบเพิ่มเติม
- วิเคราะห์ปัญหา

---

## 📋 Action Plan

### Step 1: รันทดสอบ
```bash
python scripts/test_china_realistic_settings.py
```

### Step 2: วิเคราะห์ผลลัพธ์
- ดู comparison table
- ดู best combination
- ดู assessment

### Step 3: ตัดสินใจ
- ถ้า Acceptable → ปรับ `backtest.py`
- ถ้า Not Acceptable → พิจารณาทางเลือกอื่น

### Step 4: ปรับ Parameters (ถ้า Acceptable)
- อัพเดท `backtest.py`
- ทดสอบอีกครั้งเพื่อยืนยัน

---

**Last Updated:** 2026-02-13  
**Status:** 🧪 **TESTING IN PROGRESS**

