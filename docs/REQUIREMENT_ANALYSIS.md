# 📋 Requirement Analysis: Predict N+1

**วันที่วิเคราะห์:** 2026-02-13  
**เป้าหมาย:** วิเคราะห์ว่าระบบปัจจุบันมี requirement ครบหรือยัง

---

## 🎯 Requirement จากภาพ

### **1. Main Goal**
> ทำนายว่าหุ้นจะขึ้นหรือลงวันพรุ่งนี้

### **2. Analysis Condition**
> วิเคราะห์เฉพาะเมื่อวันนี้ราคาเปลี่ยนมากกว่า 1% (บวกหรือลบ)

### **3. Asset Scope**
- **หุ้น (ไทย, US, จีน):** ใช้ Day timeframe
- **ทอง/เงิน:** ใช้ Intraday (15-30 นาที)

### **4. Required Output**
1. **Direction** (Up/Down)
2. **Expected percentage change**
3. **Probability** (เช่น "Expected to go up 5% with 80% confidence")
4. **Risk associated with incorrect prediction**

### **5. Assumption**
> การเปลี่ยนแปลงราคามาก (>1%) มีผลกระทบมากกว่าหุ้นใหญ่ vs หุ้นเล็ก

---

## ✅ วิเคราะห์: ระบบปัจจุบันมีครบหรือยัง?

### **1. Main Goal: ทำนายทิศทางวันพรุ่งนี้**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| ทำนายทิศทาง (Up/Down) | ✅ มี - `predictor.py`, `backtest_basic.py` | ✅ **ครบ** |
| ทำนายจากข้อมูลวันนี้ | ✅ มี - ใช้ pattern matching | ✅ **ครบ** |

**Code Reference:**
- `core/predictor.py` → `predict_tomorrow()` → `direction: predicted_direction.upper()`
- `scripts/backtest_basic.py` → `direction: "LONG"` หรือ `"SHORT"`

---

### **2. Analysis Condition: ราคาเปลี่ยน > 1%**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| ตรวจสอบว่าเปลี่ยน > 1% | ✅ มี - `predictor.py` line 75 | ✅ **ครบ** |
| วิเคราะห์เฉพาะเมื่อ > 1% | ✅ มี - `stats_analyzer.py` → `filter_significant_moves()` | ✅ **ครบ** |

**Code Reference:**
```python
# core/predictor.py line 75
if abs(today_pct_change) < self.threshold:
    return {'prediction': 'WAIT & SEE', ...}

# core/stats_analyzer.py line 35
significant = df[abs(df['pct_change']) >= self.threshold].copy()
```

**⚠️ หมายเหตุ:**
- ระบบปัจจุบันใช้ **dynamic threshold** (ไม่ใช่ fixed 1%)
- THAI: ~0.7-1.5% (dynamic)
- US/CHINA/TAIWAN: ~0.5-1.0% (dynamic)
- **อาจไม่ตรงกับ requirement ที่ต้องการ fixed 1%**

---

### **3. Asset Scope: Day vs Intraday**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| หุ้น (ไทย, US, จีน): Day | ✅ มี - `Interval.in_daily` | ✅ **ครบ** |
| ทอง/เงิน: Intraday 15-30min | ✅ มี - `Interval.in_15_minute`, `Interval.in_30_minute` | ✅ **ครบ** |

**Code Reference:**
- `config.py` → `ASSET_GROUPS`:
  - `GROUP_A_THAI`: `Interval.in_daily`
  - `GROUP_B_US`: `Interval.in_daily`
  - `GROUP_C_CHINA_HK`: `Interval.in_daily`
  - `GROUP_C1_GOLD_30M`: `Interval.in_30_minute`
  - `GROUP_C2_GOLD_15M`: `Interval.in_15_minute`

---

### **4. Required Output**

#### **4.1 Direction (Up/Down)**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| Direction | ✅ มี - `direction: "UP"` หรือ `"DOWN"` | ✅ **ครบ** |

**Code Reference:**
- `core/predictor.py` → `prediction['prediction']['direction']`
- `scripts/backtest_basic.py` → `direction: "LONG"` หรือ `"SHORT"`

#### **4.2 Expected Percentage Change**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| Expected % change | ✅ มี - `expected_change_avg`, `expected_change_median` | ✅ **ครบ** |

**Code Reference:**
- `core/predictor.py` line 134-135:
  ```python
  avg_change = np.mean(tomorrow_changes)
  median_change = np.median(tomorrow_changes)
  ```

#### **4.3 Probability**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| Probability | ✅ มี - `confidence`, `prob` | ✅ **ครบ** |
| Format: "Expected to go up 5% with 80% confidence" | ⚠️ มีแต่ไม่ใช่ format นี้ | ⚠️ **มีแต่ format ต่าง** |

**Code Reference:**
- `core/predictor.py` line 139:
  ```python
  probability = (direction_counts[predicted_direction] / total_count) * 100
  ```

**⚠️ หมายเหตุ:**
- ระบบมี probability แต่ไม่ใช่ format ที่ requirement ต้องการ
- Requirement ต้องการ: "Expected to go up 5% with 80% confidence"
- ระบบปัจจุบัน: แยก direction, expected_change, confidence

#### **4.4 Risk Assessment**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| Risk associated with incorrect prediction | ✅ มี - `worst_case`, `best_case`, `risk_reward_ratio` | ✅ **ครบ** |

**Code Reference:**
- `core/predictor.py` line 142-143:
  ```python
  worst_case = min(tomorrow_changes) if predicted_direction == 'up' else max(tomorrow_changes)
  best_case = max(tomorrow_changes) if predicted_direction == 'up' else min(tomorrow_changes)
  ```

---

### **5. Assumption: Large-cap vs Small-cap**

| Requirement | ระบบปัจจุบัน | สถานะ |
|------------|-------------|-------|
| การเปลี่ยนแปลงราคามาก (>1%) มีผลกระทบมากกว่าหุ้นใหญ่ vs หุ้นเล็ก | ❌ ไม่มี | ❌ **ยังไม่มี** |

**หมายเหตุ:**
- Requirement ต้องการให้พิจารณา market cap
- ระบบปัจจุบันไม่แยก large-cap vs small-cap
- อาจต้องเพิ่ม logic สำหรับ market cap classification

---

## 📊 สรุป: Requirement Coverage

| Requirement | Status | Notes |
|------------|--------|-------|
| **1. Main Goal** | ✅ **ครบ** | ทำนายทิศทางวันพรุ่งนี้ |
| **2. Analysis Condition** | ⚠️ **มีแต่ต่าง** | ใช้ dynamic threshold ไม่ใช่ fixed 1% |
| **3. Asset Scope** | ✅ **ครบ** | Day + Intraday |
| **4.1 Direction** | ✅ **ครบ** | Up/Down |
| **4.2 Expected % Change** | ✅ **ครบ** | avg_change, median_change |
| **4.3 Probability** | ⚠️ **มีแต่ format ต่าง** | มีแต่ไม่ใช่ format ที่ต้องการ |
| **4.4 Risk Assessment** | ✅ **ครบ** | worst_case, best_case |
| **5. Large-cap vs Small-cap** | ❌ **ยังไม่มี** | ไม่แยก market cap |

---

## 🔍 รายละเอียดที่ต้องปรับปรุง

### **1. Analysis Condition: Fixed 1% vs Dynamic Threshold**

**Requirement:** วิเคราะห์เฉพาะเมื่อวันนี้ราคาเปลี่ยนมากกว่า **1%** (fixed)

**ระบบปัจจุบัน:** ใช้ **dynamic threshold** (0.5-1.5% ตามประเทศ)

**คำแนะนำ:**
- ✅ เก็บ dynamic threshold ไว้ (ดีกว่า fixed)
- ⚠️ แต่ต้องมี option สำหรับ fixed 1% (ถ้า requirement ต้องการ)

### **2. Output Format**

**Requirement:** "Expected to go up 5% with 80% confidence"

**ระบบปัจจุบัน:** แยก direction, expected_change, confidence

**คำแนะนำ:**
- ✅ ข้อมูลมีครบ
- ⚠️ แต่ต้อง format output ให้ตรงกับ requirement

### **3. Large-cap vs Small-cap**

**Requirement:** การเปลี่ยนแปลงราคามาก (>1%) มีผลกระทบมากกว่าหุ้นใหญ่ vs หุ้นเล็ก

**ระบบปัจจุบัน:** ไม่แยก market cap

**คำแนะนำ:**
- ❌ ต้องเพิ่ม logic สำหรับ market cap classification
- ❌ ต้องปรับ threshold หรือ logic ตาม market cap

---

## ✅ สรุป

### **มีครบแล้ว (7/9):**
1. ✅ Main Goal: ทำนายทิศทาง
2. ✅ Analysis Condition: ตรวจสอบ > threshold (แต่ใช้ dynamic ไม่ใช่ fixed 1%)
3. ✅ Asset Scope: Day + Intraday
4. ✅ Direction: Up/Down
5. ✅ Expected % Change: avg_change, median_change
6. ✅ Probability: confidence, prob
7. ✅ Risk Assessment: worst_case, best_case

### **ต้องปรับปรุง (2/9):**
1. ⚠️ **Output Format:** ต้อง format ให้ตรงกับ requirement
2. ❌ **Large-cap vs Small-cap:** ยังไม่มี logic สำหรับ market cap

---

## 🎯 Next Steps (ถ้าต้องการให้ตรง requirement 100%)

1. **เพิ่ม Fixed 1% Option:**
   - เพิ่ม option สำหรับใช้ fixed 1% threshold (ถ้า requirement ต้องการ)

2. **ปรับ Output Format:**
   - Format output เป็น: "Expected to go up 5% with 80% confidence"

3. **เพิ่ม Market Cap Classification:**
   - เพิ่ม logic สำหรับแยก large-cap vs small-cap
   - ปรับ threshold หรือ logic ตาม market cap

---

## 🔗 Related Documents

- [BACK_TO_BASIC_ANALYSIS.md](BACK_TO_BASIC_ANALYSIS.md) - Basic System
- [PROMPT_ANALYSIS_ARCHITECTURE.md](PROMPT_ANALYSIS_ARCHITECTURE.md) - Architecture analysis

