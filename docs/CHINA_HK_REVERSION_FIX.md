# 🔧 China/HK Reversion Logic Fix

**วันที่:** 2026-02-13  
**ปัญหา:** Basic System ไม่ได้ใช้ reversion logic สำหรับจีน/ฮ่องกง

---

## 🔍 ปัญหาที่พบ

### **1. Basic System ไม่ได้ใช้ Reversion Logic**

**เดิม:**
```python
# ลองทั้ง LONG และ SHORT แล้วเลือก Prob สูงสุด
for direction in ["LONG", "SHORT"]:
    stats = calculate_stats(next_returns, direction)
    if stats['prob'] > best_prob:
        best_direction = direction
```

**ปัญหา:**
- ไม่ได้ใช้ reversion logic สำหรับจีน/ฮ่องกง
- อาจเลือก direction ที่ไม่เหมาะสม

### **2. Threshold ใช้ Dynamic อยู่แล้ว**

**Code:**
```python
short_std = pct_change.rolling(20).std()
long_std = pct_change.rolling(252).std()
effective_std = np.maximum(short_std, long_std.fillna(0))
market_floor, threshold_multiplier = self._get_market_threshold(exchange)
effective_std = np.maximum(effective_std, market_floor)
threshold = effective_std * threshold_multiplier
```

**สรุป:** ✅ ใช้ dynamic threshold อยู่แล้ว

---

## ✅ การแก้ไข

### **เพิ่ม Reversion Logic สำหรับจีน/ฮ่องกง**

```python
# ตรวจสอบว่าเป็นจีน/ฮ่องกงหรือไม่
is_china_hk = exchange and any(x in exchange.upper() for x in ['HKEX', 'HK', 'SHANGHAI', 'SHENZHEN', 'CN'])

if is_china_hk:
    # China/HK: Mean Reversion (Fade the move)
    # + (Up anomaly) -> SHORT (expect reversion down)
    # - (Down anomaly) -> LONG (expect reversion up)
    last_char = pattern_str[-1]
    if last_char == '+':
        directions_to_try = ["SHORT"]
    elif last_char == '-':
        directions_to_try = ["LONG"]
    else:
        continue
else:
    # อื่นๆ: Try both directions (เลือก Prob สูงสุด)
    directions_to_try = ["LONG", "SHORT"]
```

---

## 📊 ผลลัพธ์ที่คาดหวัง

### **ก่อนแก้ไข:**
- ลองทั้ง LONG และ SHORT → เลือก Prob สูงสุด
- อาจเลือก direction ที่ไม่เหมาะสม

### **หลังแก้ไข:**
- จีน/ฮ่องกง: ใช้ reversion logic
  - Pattern '+' → SHORT (expect reversion down)
  - Pattern '-' → LONG (expect reversion up)
- **Prob% สูงขึ้น** (ใช้ direction ที่เหมาะสม)
- **เสี่ยงน้อยลง** (ใช้ reversion logic)

---

## 🎯 สรุป

### **✅ แก้ไขแล้ว:**
1. ✅ เพิ่ม reversion logic สำหรับจีน/ฮ่องกง
2. ✅ Threshold ใช้ dynamic อยู่แล้ว (ไม่ต้องแก้)

### **📊 ผลลัพธ์ที่คาดหวัง:**
- Prob% สูงขึ้น (ใช้ direction ที่เหมาะสม)
- เสี่ยงน้อยลง (ใช้ reversion logic)
- RRR คุ้มค่า (ยังคงใช้ RRR เป็น metric)
- Count น่าเชื่อถือ (min_stats 25)

---

## 🔗 Related Documents

- [CHINA_HK_OPTIMIZATION_PLAN.md](CHINA_HK_OPTIMIZATION_PLAN.md) - แผนการปรับปรุง
- [CHINA_HK_THRESHOLD_ANALYSIS.md](CHINA_HK_THRESHOLD_ANALYSIS.md) - วิเคราะห์ threshold

