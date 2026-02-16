# 📊 Basic System vs Main System: เปรียบเทียบผลลัพธ์

**วันที่:** 2026-02-13  
**เป้าหมาย:** เปรียบเทียบ Basic System กับ Main System (Max Hold 5-8 วัน) จากผลลัพธ์จริง

---

## 🔍 เปรียบเทียบ Logic

### **Main System (backtest.py)**

#### **1. Pattern Matching:**
- **Threshold:** Dynamic (Rolling Window: 20-day, 252-day)
- **Floor:** 0.5-0.7% (ตามประเทศ)
- **Multiplier:** 0.9-1.0x (ตามประเทศ)

#### **2. Risk Management:**
- **Max Hold:** 
  - THAI: 5 วัน
  - US: 7 วัน
  - CHINA/HK: 8 วัน
  - TAIWAN: 10 วัน
- **Stop Loss / Take Profit:**
  - ATR-based หรือ Fixed (ตามประเทศ)
  - Trailing Stop: Activate 1.5-2.0%, Distance 40-50%
- **Trade Simulation:** ✅ มี (simulate_trade_with_rm)

#### **3. Gatekeeper:**
- **Prob Threshold:** 
  - THAI: 53%
  - US: 52% + Quality Filter (AvgWin > AvgLoss)
  - CHINA/HK: 54%
  - TAIWAN: 51%
- **Expectancy > 0:** ✅ ต้องผ่าน
- **Quality Filter:** ✅ มี (US)

#### **4. Direction Logic:**
- **THAI:** Mean Reversion
- **US:** Hybrid Volatility (HIGH_VOL → REVERSION, LOW_VOL → TREND)
- **CHINA/HK:** Mean Reversion + Volume Ratio Filter
- **TAIWAN:** Regime-Aware (BULL → TREND, BEAR/SIDEWAYS → REVERSION)

---

### **Basic System (backtest_basic.py)**

#### **1. Pattern Matching:**
- **Threshold:** 
  - THAI, US, TAIWAN: Dynamic (Rolling Window: 20-day, 252-day)
  - CHINA/HK: Dynamic (Overall SD จากทั้งหมด 5000 bars)
- **Floor:** 0.5-0.7% (ตามประเทศ)
- **Multiplier:** 0.8-1.0x (ตามประเทศ)

#### **2. Risk Management:**
- **Max Hold:** ❌ ไม่มี (N+1 prediction เท่านั้น)
- **Stop Loss / Take Profit:** ❌ ไม่มี
- **Trailing Stop:** ❌ ไม่มี
- **Trade Simulation:** ❌ ไม่มี

#### **3. Gatekeeper:**
- **Prob Threshold:** 
  - THAI, US, TAIWAN: 55%
  - CHINA/HK: 48%
- **Expectancy > 0:** ❌ ไม่มี
- **Quality Filter:** ❌ ไม่มี

#### **4. Direction Logic:**
- **THAI, US, TAIWAN:** Try Both → เลือก Prob สูงสุด
- **CHINA/HK:** Mean Reversion (Fade the move) + Volume Ratio Filter

---

## 📊 ตารางเปรียบเทียบ Logic

| Aspect | Main System | Basic System |
|--------|-------------|--------------|
| **Threshold Type** | Dynamic (Rolling) | Dynamic (Rolling/Overall) |
| **Max Hold** | ✅ 5-10 วัน | ❌ ไม่มี |
| **Risk Management** | ✅ SL/TP/Trailing | ❌ ไม่มี |
| **Trade Simulation** | ✅ มี | ❌ ไม่มี |
| **Prob Threshold** | 51-54% | 48-55% |
| **Expectancy Filter** | ✅ มี | ❌ ไม่มี |
| **Quality Filter** | ✅ มี (US) | ❌ ไม่มี |
| **Direction Logic** | Market-Specific | Try Both / Reversion |

---

## 📈 เปรียบเทียบผลลัพธ์ (จาก Data)

### **Basic System (ล่าสุด - 29 หุ้นผ่าน):**

#### **Overall Results:**
- ✅ **Passed:** 29 หุ้น (จาก 147 symbols)
- **By Exchange:**
  - **SET (THAI):** 7 หุ้นผ่าน
  - **NASDAQ (US):** 19 หุ้นผ่าน
  - **HKEX (CHINA/HK):** 2 หุ้นผ่าน
  - **TWSE (TAIWAN):** 1 หุ้นผ่าน

#### **Stats (29 หุ้นที่ผ่าน):**
- **Avg Prob%:** 56.8%
- **Avg RRR:** 1.28
- **Avg Match Count:** 655

#### **รายละเอียด:**
- **Prob%:** 48-73% (ส่วนใหญ่ 55-60%)
- **RRR:** 0.88-6.24 (ส่วนใหญ่ 1.0-2.0)
- **Match Count:** 25-3150 (ส่วนใหญ่ 100-1000)

---

### **Main System (จากเอกสาร - 565 trades):**

#### **Overall Results:**
- **Total Trades:** 565 trades
- **Accuracy:** 51.86%
- **Realized RRR:** 0.79
- **Total Return%:** -58.35%

#### **Stats (ตัวอย่าง):**
- **PTT:** 280 trades, 57.50% accuracy, RRR 0.94, +26.64%
- **ADVANC:** 179 trades, 50.28% accuracy, RRR 0.74, -27.86%
- **PTTEP:** 36 trades, 61.11% accuracy, RRR 1.79, +41.57%
- **NVDA:** 70 trades, 28.57% accuracy, RRR 1.00, -98.70%

---

## 🔍 วิเคราะห์ความแตกต่าง

### **1. Risk Management:**

#### **Main System:**
- ✅ มี Max Hold (5-10 วัน)
- ✅ มี SL/TP (ATR-based หรือ Fixed)
- ✅ มี Trailing Stop
- ✅ มี Trade Simulation

**ผลลัพธ์:**
- Realized RRR ต่ำ (0.79) แม้ Historical RRR >= 1.5
- Accuracy ต่ำ (51.86%)
- Total Return% ติดลบ (-58.35%)

**สาเหตุที่เป็นไปได้:**
- Max Hold 5-10 วัน อาจยาวเกินไป
- Risk Management อาจไม่เหมาะสม
- Market conditions เปลี่ยนไป

#### **Basic System:**
- ❌ ไม่มี Max Hold (N+1 prediction เท่านั้น)
- ❌ ไม่มี SL/TP
- ❌ ไม่มี Trailing Stop
- ❌ ไม่มี Trade Simulation

**ผลลัพธ์:**
- Historical RRR: 1.28 (ดีกว่า Main System)
- Prob%: 56.8% (ดีกว่า Main System)
- แต่ไม่ได้ simulate trade จริง

---

### **2. Gatekeeper:**

#### **Main System:**
- Prob Threshold: 51-54% (ต่ำกว่า)
- Expectancy > 0: ✅ ต้องผ่าน
- Quality Filter: ✅ มี (US)

**ผลลัพธ์:**
- ได้ trades มาก (565 trades)
- แต่ Accuracy ต่ำ (51.86%)
- Realized RRR ต่ำ (0.79)

#### **Basic System:**
- Prob Threshold: 48-55% (สูงกว่า)
- Expectancy > 0: ❌ ไม่มี
- Quality Filter: ❌ ไม่มี

**ผลลัพธ์:**
- ได้หุ้นน้อย (29 หุ้น)
- Prob% สูงกว่า (56.8%)
- Historical RRR สูงกว่า (1.28)

---

### **3. Direction Logic:**

#### **Main System:**
- Market-Specific (Reversion/Trend/Regime-Aware)
- ใช้ Volume Ratio, Regime Filter (CHINA/HK)

**ผลลัพธ์:**
- Logic ซับซ้อนกว่า
- แต่ Accuracy ต่ำ (51.86%)

#### **Basic System:**
- Try Both → เลือก Prob สูงสุด (THAI, US, TAIWAN)
- Reversion (CHINA/HK)

**ผลลัพธ์:**
- Logic เรียบง่ายกว่า
- Prob% สูงกว่า (56.8%)

---

## 📊 เปรียบเทียบผลลัพธ์รายประเทศ

### **🇹🇭 THAI Market:**

#### **Main System:**
- Prob Threshold: 53%
- Max Hold: 5 วัน
- **ผลลัพธ์:** PTT 280 trades, 57.50% accuracy, RRR 0.94

#### **Basic System:**
- Prob Threshold: 55%
- Max Hold: ไม่มี
- **ผลลัพธ์:** 7 หุ้นผ่าน, Avg Prob 56.8%, Avg RRR 1.28

**สรุป:** Basic System มี Prob% และ RRR สูงกว่า

---

### **🇺🇸 US Market:**

#### **Main System:**
- Prob Threshold: 52% + Quality Filter
- Max Hold: 7 วัน
- **ผลลัพธ์:** NVDA 70 trades, 28.57% accuracy, RRR 1.00

#### **Basic System:**
- Prob Threshold: 55%
- Max Hold: ไม่มี
- **ผลลัพธ์:** 19 หุ้นผ่าน, Avg Prob 56.8%, Avg RRR 1.28

**สรุป:** Basic System มี Prob% สูงกว่า (56.8% vs 28.57%)

---

### **🇨🇳 CHINA/HK Market:**

#### **Main System:**
- Prob Threshold: 54%
- Max Hold: 8 วัน
- Volume Ratio Filter: ✅ มี
- **ผลลัพธ์:** ไม่มีข้อมูล

#### **Basic System:**
- Prob Threshold: 48%
- Max Hold: ไม่มี
- Volume Ratio Filter: ✅ มี
- **ผลลัพธ์:** 2 หุ้นผ่าน (700, 1211), Avg Prob 49.5%, Avg RRR 0.92

**สรุป:** Basic System ได้หุ้นผ่าน (2 หุ้น)

---

### **🇹🇼 TAIWAN Market:**

#### **Main System:**
- Prob Threshold: 51%
- Max Hold: 10 วัน
- **ผลลัพธ์:** ไม่มีข้อมูล

#### **Basic System:**
- Prob Threshold: 55%
- Max Hold: ไม่มี
- **ผลลัพธ์:** 1 หุ้นผ่าน

**สรุป:** Basic System ได้หุ้นผ่าน (1 หุ้น)

---

## 💡 ข้อสังเกต

### **1. Main System มีปัญหา:**
- Realized RRR ต่ำ (0.79) แม้ Historical RRR >= 1.5
- Accuracy ต่ำ (51.86%)
- Total Return% ติดลบ (-58.35%)

**สาเหตุที่เป็นไปได้:**
- Max Hold 5-10 วัน อาจยาวเกินไป
- Risk Management อาจไม่เหมาะสม
- Market conditions เปลี่ยนไป
- Slippage, Commission

### **2. Basic System:**
- Historical RRR: 1.28 (ดีกว่า Main System)
- Prob%: 56.8% (ดีกว่า Main System)
- แต่ไม่ได้ simulate trade จริง

**ข้อดี:**
- Logic เรียบง่าย
- Prob% สูงกว่า
- ไม่มี Max Hold (N+1 prediction เท่านั้น)

**ข้อเสีย:**
- ไม่ได้ simulate trade จริง
- ไม่มี Risk Management

---

## 🎯 สรุป

### **Main System:**
- ✅ มี Risk Management (SL/TP/Trailing/Max Hold)
- ✅ มี Trade Simulation
- ❌ Realized RRR ต่ำ (0.79)
- ❌ Accuracy ต่ำ (51.86%)
- ❌ Total Return% ติดลบ (-58.35%)

### **Basic System:**
- ❌ ไม่มี Risk Management
- ❌ ไม่มี Trade Simulation
- ✅ Historical RRR สูง (1.28)
- ✅ Prob% สูง (56.8%)
- ✅ Logic เรียบง่าย

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

- [BASIC_SYSTEM_COUNTRY_LOGIC.md](BASIC_SYSTEM_COUNTRY_LOGIC.md) - Logic ของแต่ละประเทศ
- [BACK_TO_BASIC_ANALYSIS.md](BACK_TO_BASIC_ANALYSIS.md) - วิเคราะห์ Back to Basic
