# 📊 Basic System: Threshold ตามประเทศ

**วันที่อัพเดท:** 2026-02-13  
**ระบบ:** Back to Basic - สถิติเพียวๆ

---

## 🎯 Threshold Configuration

Basic System ใช้ threshold ตามประเทศเหมือนกับระบบหลัก:

### **Threshold Formula:**
```
effective_std = max(20-day SD, 252-day SD)
effective_std = max(effective_std, market_floor)
threshold = effective_std * threshold_multiplier
```

---

## 📋 Threshold ตามประเทศ

| ประเทศ | Exchange | Market Floor | Threshold Multiplier | Threshold (ประมาณ) |
|--------|----------|--------------|---------------------|-------------------|
| **🇹🇭 THAI** | SET, MAI | **0.7%** (0.007) | **1.0x** | ~0.7-1.5% |
| **🇺🇸 US** | NASDAQ, NYSE | **0.6%** (0.006) | **0.9x** | ~0.5-1.2% |
| **🇹🇼 TAIWAN** | TWSE | **0.5%** (0.005) | **0.9x** | ~0.5-1.0% |
| **🇨🇳 CHINA/HK** | HKEX, SHANGHAI, SHENZHEN | **0.5%** (0.005) | **0.9x** | ~0.5-1.0% |
| **Default** | อื่นๆ | **0.5%** (0.005) | **0.9x** | ~0.5-1.0% |

---

## 🔍 รายละเอียดแต่ละประเทศ

### 🇹🇭 **THAI Market**
- **Market Floor:** 0.7% (0.007)
- **Threshold Multiplier:** 1.0x
- **เหตุผล:** หุ้นไทยมีความผันผวนต่ำ → ต้องการ threshold สูงเพื่อกรอง noise
- **Threshold จริง:** ~0.7-1.5% (ขึ้นอยู่กับ volatility)

### 🇺🇸 **US Market**
- **Market Floor:** 0.6% (0.006)
- **Threshold Multiplier:** 0.9x
- **เหตุผล:** หุ้น US มีความผันผวนสูง → threshold ต่ำเพื่อจับสัญญาณมากขึ้น
- **Threshold จริง:** ~0.5-1.2% (ขึ้นอยู่กับ volatility)

### 🇹🇼 **Taiwan Market**
- **Market Floor:** 0.5% (0.005)
- **Threshold Multiplier:** 0.9x
- **เหตุผล:** หุ้นไต้หวันมีความผันผวนปานกลาง
- **Threshold จริง:** ~0.5-1.0% (ขึ้นอยู่กับ volatility)

### 🇨🇳 **China/HK Market**
- **Market Floor:** 0.5% (0.005)
- **Threshold Multiplier:** 0.9x
- **เหตุผล:** หุ้นจีน/ฮ่องกงมีความผันผวนปานกลาง
- **Threshold จริง:** ~0.5-1.0% (ขึ้นอยู่กับ volatility)

---

## 💡 เปรียบเทียบกับระบบหลัก

| Aspect | ระบบหลัก (backtest.py) | Basic System |
|--------|----------------------|--------------|
| **Threshold Logic** | ✅ ตามประเทศ | ✅ ตามประเทศ |
| **Market Floor** | ✅ ตามประเทศ | ✅ ตามประเทศ |
| **Multiplier** | ✅ ตามประเทศ | ✅ ตามประเทศ |
| **Dynamic** | ✅ ใช่ (20d SD, 252d SD) | ✅ ใช่ (20d SD, 252d SD) |

**สรุป:** Basic System ใช้ threshold เหมือนกับระบบหลัก ✅

---

## 🔧 Implementation

### **Code Location:**
- `core/pattern_matcher_basic.py` → `_get_market_threshold()`

### **Usage:**
```python
from core.pattern_matcher_basic import BasicPatternMatcher

matcher = BasicPatternMatcher()
market_floor, multiplier = matcher._get_market_threshold('SET')  # THAI
# Returns: (0.007, 1.0)

market_floor, multiplier = matcher._get_market_threshold('NASDAQ')  # US
# Returns: (0.006, 0.9)
```

---

## 📝 หมายเหตุ

1. **Threshold เป็น Dynamic:** ปรับตาม volatility ของแต่ละหุ้น
2. **Market Floor:** ป้องกัน threshold ต่ำเกินไป
3. **Multiplier:** ปรับความเข้มงวดของ pattern detection
4. **THAI สูงสุด:** 0.7% floor + 1.0x multiplier → เข้มงวดที่สุด
5. **US/CHINA/TAIWAN ต่ำกว่า:** 0.5-0.6% floor + 0.9x multiplier → ยืดหยุ่นกว่า

---

## 🔗 Related Documents

- [STRATEGY_TABLE_BY_COUNTRY.md](STRATEGY_TABLE_BY_COUNTRY.md) - Threshold ของระบบหลัก
- [BACK_TO_BASIC_ANALYSIS.md](BACK_TO_BASIC_ANALYSIS.md) - แนวทาง Back to Basic

