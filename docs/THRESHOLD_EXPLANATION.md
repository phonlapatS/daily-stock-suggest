# 📊 Threshold: Multiplier vs Floor

**วันที่อัพเดท:** 2026-02-13  
**คำถาม:** ไทยใช้ 1.25 SD? US ใช้ 0.6 SD? Taiwan/China ใช้ 0.5 SD?

---

## 🎯 คำตอบ: ไม่ใช่!

### **Threshold มี 2 ส่วน:**

1. **Threshold Multiplier** (คูณกับ SD) → ใช้คูณกับ `effective_std`
2. **Market Floor** (ค่าต่ำสุด) → ป้องกัน threshold ต่ำเกินไป

---

## 📋 Threshold ตามประเทศ (จริงๆ)

### **สูตร Threshold:**
```python
effective_std = max(20-day SD, 252-day SD)
effective_std = max(effective_std, market_floor)  # ← Floor ใช้ที่นี่
threshold = effective_std * threshold_multiplier   # ← Multiplier ใช้ที่นี่
```

### **ตาราง Threshold:**

| ประเทศ | **Threshold Multiplier** | **Market Floor** | **Threshold จริง** |
|--------|------------------------|-----------------|-------------------|
| **🇹🇭 THAI** | **1.0x SD** | **0.7%** | `max(SD, 0.7%) * 1.0` |
| **🇺🇸 US** | **0.9x SD** | **0.6%** | `max(SD, 0.6%) * 0.9` |
| **🇹🇼 TAIWAN** | **0.9x SD** | **0.5%** | `max(SD, 0.5%) * 0.9` |
| **🇨🇳 CHINA/HK** | **0.9x SD** | **0.5%** | `max(SD, 0.5%) * 0.9` |

---

## 🔍 อธิบายรายละเอียด

### **1. Threshold Multiplier (คูณกับ SD)**

- **THAI:** `1.0x SD` → คูณด้วย 1.0 (ไม่ลด)
- **US/TAIWAN/CHINA:** `0.9x SD` → คูณด้วย 0.9 (ลด 10%)

**หมายเหตุ:** 
- ❌ **ไม่ใช่** 1.25 SD สำหรับไทย (เคยใช้แต่เปลี่ยนเป็น 1.0 แล้ว)
- ❌ **ไม่ใช่** 0.6 SD สำหรับ US (0.6 คือ floor ไม่ใช่ multiplier)
- ❌ **ไม่ใช่** 0.5 SD สำหรับ Taiwan/China (0.5 คือ floor ไม่ใช่ multiplier)

### **2. Market Floor (ค่าต่ำสุด)**

- **THAI:** `0.7%` → threshold ต่ำสุด 0.7%
- **US:** `0.6%` → threshold ต่ำสุด 0.6%
- **TAIWAN/CHINA:** `0.5%` → threshold ต่ำสุด 0.5%

**หมายเหตุ:**
- Floor **ไม่ใช่** multiplier
- Floor เป็น **ค่าต่ำสุด** ที่ threshold ต้องมี
- ถ้า SD < Floor → ใช้ Floor แทน

---

## 💡 ตัวอย่างการคำนวณ

### **ตัวอย่าง 1: THAI Market**
```python
# สมมติ SD = 0.8%
effective_std = max(0.8%, 0.7%) = 0.8%  # SD สูงกว่า floor
threshold = 0.8% * 1.0 = 0.8%

# สมมติ SD = 0.5%
effective_std = max(0.5%, 0.7%) = 0.7%  # ใช้ floor เพราะ SD ต่ำกว่า
threshold = 0.7% * 1.0 = 0.7%
```

### **ตัวอย่าง 2: US Market**
```python
# สมมติ SD = 1.0%
effective_std = max(1.0%, 0.6%) = 1.0%  # SD สูงกว่า floor
threshold = 1.0% * 0.9 = 0.9%

# สมมติ SD = 0.4%
effective_std = max(0.4%, 0.6%) = 0.6%  # ใช้ floor เพราะ SD ต่ำกว่า
threshold = 0.6% * 0.9 = 0.54%
```

### **ตัวอย่าง 3: Taiwan/China Market**
```python
# สมมติ SD = 0.8%
effective_std = max(0.8%, 0.5%) = 0.8%  # SD สูงกว่า floor
threshold = 0.8% * 0.9 = 0.72%

# สมมติ SD = 0.3%
effective_std = max(0.3%, 0.5%) = 0.5%  # ใช้ floor เพราะ SD ต่ำกว่า
threshold = 0.5% * 0.9 = 0.45%
```

---

## ⚠️ ความเข้าใจผิด

### **❌ ความเข้าใจผิด:**
- "ไทยใช้ 1.25 SD" → **ไม่ใช่** (ใช้ 1.0x SD)
- "US ใช้ 0.6 SD" → **ไม่ใช่** (0.6 คือ floor, multiplier คือ 0.9x)
- "Taiwan/China ใช้ 0.5 SD" → **ไม่ใช่** (0.5 คือ floor, multiplier คือ 0.9x)

### **✅ ความจริง:**
- **THAI:** `1.0x SD` (multiplier) + `0.7%` (floor)
- **US:** `0.9x SD` (multiplier) + `0.6%` (floor)
- **TAIWAN/CHINA:** `0.9x SD` (multiplier) + `0.5%` (floor)

---

## 📊 เปรียบเทียบ Threshold จริง

| ประเทศ | SD ต่ำ | SD สูง | Threshold (ประมาณ) |
|--------|--------|--------|-------------------|
| **THAI** | 0.7% (floor) | 1.5% * 1.0 = 1.5% | **0.7-1.5%** |
| **US** | 0.54% (0.6% * 0.9) | 1.2% * 0.9 = 1.08% | **0.54-1.08%** |
| **TAIWAN/CHINA** | 0.45% (0.5% * 0.9) | 1.0% * 0.9 = 0.9% | **0.45-0.9%** |

---

## 🔧 Code Reference

### **Location:** `scripts/backtest.py` (lines 389-435)

```python
# Threshold Multiplier
if is_thai_market:
    threshold_multiplier = 1.0     # 1.0x SD
elif is_us_market:
    threshold_multiplier = 0.9     # 0.9x SD
elif is_tw_market_early:
    threshold_multiplier = 0.9     # 0.9x SD
elif is_china_market:
    threshold_multiplier = 0.9     # 0.9x SD

# Market Floor
if is_us_market: 
    current_floor = 0.006          # 0.6%
elif is_thai_market: 
    current_floor = 0.007          # 0.7%
elif is_tw_market_early: 
    current_floor = 0.005          # 0.5%
elif is_china_market: 
    current_floor = 0.005          # 0.5%

# Calculate threshold
effective_std = np.maximum(short_std, long_std.fillna(0))
effective_std = np.maximum(effective_std, current_floor)  # Apply floor
threshold = effective_std * threshold_multiplier           # Apply multiplier
```

---

## 📝 สรุป

1. **Threshold Multiplier:**
   - THAI: **1.0x** (ไม่ลด)
   - US/TAIWAN/CHINA: **0.9x** (ลด 10%)

2. **Market Floor:**
   - THAI: **0.7%** (สูงสุด)
   - US: **0.6%**
   - TAIWAN/CHINA: **0.5%** (ต่ำสุด)

3. **Threshold จริง:**
   - `threshold = max(SD, floor) * multiplier`
   - THAI: `max(SD, 0.7%) * 1.0`
   - US: `max(SD, 0.6%) * 0.9`
   - TAIWAN/CHINA: `max(SD, 0.5%) * 0.9`

---

## 🔗 Related Documents

- [STRATEGY_TABLE_BY_COUNTRY.md](STRATEGY_TABLE_BY_COUNTRY.md) - Threshold configuration
- [BASIC_SYSTEM_THRESHOLD.md](BASIC_SYSTEM_THRESHOLD.md) - Basic System threshold

