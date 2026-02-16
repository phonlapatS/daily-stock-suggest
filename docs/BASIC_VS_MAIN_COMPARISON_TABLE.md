# 📊 Basic System vs Main System: ตารางเปรียบเทียบ

**วันที่:** 2026-02-13  
**เปรียบเทียบ:** Basic System (สถิติเพียวๆ) vs Main System (Max Hold 5-8 วัน)

---

## 📋 ตารางเปรียบเทียบ Logic

### **1. Pattern Matching Threshold**

| Country | Main System | Basic System |
|---------|-------------|--------------|
| **THAI** | Dynamic (Rolling), Floor 0.7%, Multiplier 1.0x | Dynamic (Rolling), Floor 0.7%, Multiplier 1.0x |
| **US** | Dynamic (Rolling), Floor 0.6%, Multiplier 0.9x | Dynamic (Rolling), Floor 0.6%, Multiplier 0.9x |
| **TAIWAN** | Dynamic (Rolling), Floor 0.5%, Multiplier 0.9x | Dynamic (Rolling), Floor 0.5%, Multiplier 0.9x |
| **CHINA/HK** | Dynamic (Rolling), Floor 0.5%, Multiplier 0.9x | Dynamic (Overall SD), Floor 0.6%, Multiplier 0.8x |

**หมายเหตุ:** 
- Main System: ใช้ Rolling Window (20-day, 252-day) ทุกประเทศ
- Basic System: CHINA/HK ใช้ Overall SD จากทั้งหมด 5000 bars

---

### **2. Gatekeeper Criteria**

| Country | Main System | Basic System |
|---------|-------------|--------------|
| **THAI** | Prob >= 53%, Expectancy > 0 | Prob >= 55%, Expectancy ไม่มี |
| **US** | Prob >= 52%, Expectancy > 0, AvgWin > AvgLoss | Prob >= 55%, Expectancy ไม่มี |
| **TAIWAN** | Prob >= 51%, Expectancy > 0 | Prob >= 55%, Expectancy ไม่มี |
| **CHINA/HK** | Prob >= 54%, Expectancy > 0 | Prob >= 48%, Expectancy ไม่มี |

**Min Stats:**
| Country | Main System | Basic System |
|---------|-------------|--------------|
| **THAI** | 25 | 25 |
| **US** | 20 | 25 |
| **TAIWAN** | 25 | 25 |
| **CHINA/HK** | 30 | 25 |

---

### **3. Risk Management**

| Aspect | Main System | Basic System |
|--------|-------------|--------------|
| **Max Hold** | ✅ 5-10 วัน (ตามประเทศ) | ❌ ไม่มี |
| **Stop Loss** | ✅ ATR-based หรือ Fixed | ❌ ไม่มี |
| **Take Profit** | ✅ ATR-based หรือ Fixed | ❌ ไม่มี |
| **Trailing Stop** | ✅ Activate 1.5-2.0%, Distance 40-50% | ❌ ไม่มี |
| **Trade Simulation** | ✅ มี (simulate_trade_with_rm) | ❌ ไม่มี |
| **Position Sizing** | ✅ มี (Risk 2% per trade) | ❌ ไม่มี |

**Max Hold ตามประเทศ:**
| Country | Main System |
|---------|-------------|
| **THAI** | 5 วัน |
| **US** | 7 วัน |
| **CHINA/HK** | 8 วัน |
| **TAIWAN** | 10 วัน |

---

### **4. Direction Logic**

| Country | Main System | Basic System |
|---------|-------------|--------------|
| **THAI** | Mean Reversion | Try Both → เลือก Prob สูงสุด |
| **US** | Hybrid Volatility (HIGH_VOL → REVERSION, LOW_VOL → TREND) | Try Both → เลือก Prob สูงสุด |
| **TAIWAN** | Regime-Aware (BULL → TREND, BEAR/SIDEWAYS → REVERSION) | Try Both → เลือก Prob สูงสุด |
| **CHINA/HK** | Mean Reversion + Volume Ratio Filter | Mean Reversion + Volume Ratio Filter |

---

### **5. Risk Filters**

| Filter | Main System | Basic System |
|--------|-------------|--------------|
| **Volume Ratio (VR)** | ✅ มี (CHINA/HK: VR < 0.5 = skip) | ✅ มี (CHINA/HK: VR < 0.5 = skip) |
| **Regime Filter** | ✅ มี (CHINA/HK: LONG only if Price > SMA50) | ❌ ไม่มี |
| **Quality Filter** | ✅ มี (US: AvgWin > AvgLoss) | ❌ ไม่มี |

---

## 📈 ตารางเปรียบเทียบผลลัพธ์

### **Overall Results**

| Metric | Main System | Basic System |
|--------|-------------|--------------|
| **Total Symbols** | - | 147 symbols |
| **Passed/Trades** | 565 trades | 29 หุ้นผ่าน |
| **Accuracy/Prob%** | 51.86% | 56.8% |
| **RRR** | 0.79 (Realized) | 1.28 (Historical) |
| **Total Return%** | -58.35% | N/A (ไม่ simulate) |

---

### **ผลลัพธ์รายประเทศ**

#### **🇹🇭 THAI Market**

| Metric | Main System | Basic System |
|--------|-------------|--------------|
| **Prob Threshold** | 53% | 55% |
| **Max Hold** | 5 วัน | ไม่มี |
| **Passed/Trades** | PTT: 280 trades | **7 หุ้นผ่าน** |
| **Accuracy/Prob%** | PTT: 57.50% | **Avg: 57.20%** |
| **RRR** | PTT: 0.94 | **Avg: 2.02** |
| **Avg Match Count** | N/A | **210** |
| **Return%** | PTT: +26.64% | N/A |

**สรุป:** Basic System มี Prob% และ RRR สูงกว่า

---

#### **🇺🇸 US Market**

| Metric | Main System | Basic System |
|--------|-------------|--------------|
| **Prob Threshold** | 52% + Quality Filter | 55% |
| **Max Hold** | 7 วัน | ไม่มี |
| **Passed/Trades** | NVDA: 70 trades | **19 หุ้นผ่าน** |
| **Accuracy/Prob%** | NVDA: 28.57% | **Avg: 57.35%** |
| **RRR** | NVDA: 1.00 | **Avg: 1.06** |
| **Avg Match Count** | N/A | **772** |
| **Return%** | NVDA: -98.70% | N/A |

**สรุป:** Basic System มี Prob% สูงกว่า (57.35% vs 28.57%)

---

#### **🇨🇳 CHINA/HK Market**

| Metric | Main System | Basic System |
|--------|-------------|--------------|
| **Prob Threshold** | 54% | 48% |
| **Max Hold** | 8 วัน | ไม่มี |
| **Threshold Type** | Dynamic (Rolling) | Dynamic (Overall SD) |
| **Threshold Multiplier** | 0.9x | 0.8x |
| **Volume Ratio Filter** | ✅ มี | ✅ มี |
| **Passed/Trades** | ไม่มีข้อมูล | **2 หุ้นผ่าน** |
| **Accuracy/Prob%** | N/A | **Avg: 50.06%** |
| **RRR** | N/A | **Avg: 0.94** |
| **Avg Match Count** | N/A | **1,248** |

**สรุป:** Basic System ได้หุ้นผ่าน (2 หุ้น: 700, 1211)

---

#### **🇹🇼 TAIWAN Market**

| Metric | Main System | Basic System |
|--------|-------------|--------------|
| **Prob Threshold** | 51% | 55% |
| **Max Hold** | 10 วัน | ไม่มี |
| **Passed/Trades** | ไม่มีข้อมูล | **1 หุ้นผ่าน** |
| **Accuracy/Prob%** | N/A | **57.95%** |
| **RRR** | N/A | **0.99** |
| **Avg Match Count** | N/A | **352** |

**สรุป:** Basic System ได้หุ้นผ่าน (1 หุ้น)

---

## 🔍 ตารางเปรียบเทียบข้อดี/ข้อเสีย

### **Main System**

| ข้อดี | ข้อเสีย |
|------|--------|
| ✅ มี Risk Management (SL/TP/Trailing) | ❌ Realized RRR ต่ำ (0.79) |
| ✅ มี Trade Simulation | ❌ Accuracy ต่ำ (51.86%) |
| ✅ มี Position Sizing | ❌ Total Return% ติดลบ (-58.35%) |
| ✅ มี Quality Filter | ❌ Max Hold 5-10 วัน อาจยาวเกินไป |
| ✅ มี Regime Filter (CHINA/HK) | ❌ Logic ซับซ้อน |

---

### **Basic System**

| ข้อดี | ข้อเสีย |
|------|--------|
| ✅ Historical RRR สูง (1.28) | ❌ ไม่มี Risk Management |
| ✅ Prob% สูง (56.8%) | ❌ ไม่มี Trade Simulation |
| ✅ Logic เรียบง่าย | ❌ ไม่ได้ simulate trade จริง |
| ✅ ไม่มี Max Hold (N+1 prediction) | ❌ ไม่มี Position Sizing |
| ✅ ได้หุ้นผ่านมากขึ้น (29 หุ้น) | ❌ ไม่มี Quality Filter |

---

## 📊 สรุปเปรียบเทียบ

### **Main System:**
- **Logic:** ซับซ้อน (Market-Specific, Risk Management)
- **Risk Management:** ✅ มี (SL/TP/Trailing/Max Hold)
- **Trade Simulation:** ✅ มี
- **ผลลัพธ์:** Realized RRR ต่ำ (0.79), Accuracy ต่ำ (51.86%), Return ติดลบ (-58.35%)

### **Basic System:**
- **Logic:** เรียบง่าย (สถิติเพียวๆ)
- **Risk Management:** ❌ ไม่มี
- **Trade Simulation:** ❌ ไม่มี
- **ผลลัพธ์:** Historical RRR สูง (1.28), Prob% สูง (56.8%), ได้หุ้นผ่านมากขึ้น (29 หุ้น)

---

## 💡 คำแนะนำ

### **Option 1: ใช้ Basic System + Risk Management แบบเรียบง่าย**
- ใช้ Basic System สำหรับ pattern matching
- เพิ่ม Risk Management แบบเรียบง่าย (SL/TP แบบ Fixed)
- ลด Max Hold เป็น 1-3 วัน

### **Option 2: ปรับ Main System**
- ลด Max Hold จาก 5-10 วัน → 1-3 วัน
- ปรับ Risk Management ให้เหมาะสม
- เพิ่ม Prob Threshold

---

## 🔗 Related Documents

- [BASIC_VS_MAIN_SYSTEM_COMPARISON.md](BASIC_VS_MAIN_SYSTEM_COMPARISON.md) - เปรียบเทียบละเอียด
- [BASIC_SYSTEM_COUNTRY_LOGIC.md](BASIC_SYSTEM_COUNTRY_LOGIC.md) - Logic ของแต่ละประเทศ

