# 📊 ตารางรายละเอียดการตั้งค่าของแต่ละประเทศ

**วันที่อัพเดท:** 2026-02-13  
**วัตถุประสงค์:** สรุปการตั้งค่า threshold, logic, และเกณฑ์การแสดงผลของแต่ละประเทศ

---

## 📋 ตารางสรุปการตั้งค่า

| ประเทศ | Threshold Multiplier | Market Floor | Min Stats | Gatekeeper (min_prob) | Strategy Logic | Display Criteria |
|--------|---------------------|--------------|-----------|---------------------|----------------|------------------|
| **🇹🇭 THAI** | **1.0x SD** | **0.7%** | **25** | **53.0%** | **MEAN_REVERSION** | Prob >= 60% \| RRR >= 1.3 \| Count >= 30 |
| **🇺🇸 US** | **0.9x SD** | **0.6%** | **20** | **52.0%** | **US_HYBRID_VOL** | Prob >= 60% \| RRR >= 1.5 \| Count >= 15 |
| **🇹🇼 TAIWAN** | **0.9x SD** | **0.5%** | **25** | **51.0%** | **REGIME_AWARE** | Prob >= 55% \| RRR >= 1.5 \| Count >= 15 |
| **🇨🇳 CHINA/HK** | **0.9x SD** | **0.5%** | **30** | **50.0%** | **MEAN_REVERSION** | Prob >= 60% \| RRR >= 1.2 \| Count >= 15 |
| **⚪ METALS** | **0.9x SD** | **0.5%** | **25** | **50.0%** | **MEAN_REVERSION** | Prob >= 50% |

---

## 🔍 รายละเอียดแต่ละประเทศ

### 🇹🇭 **THAI Market**

#### **1. Pattern Detection Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  effective_std = max(20-day SD, 252-day SD)
  effective_std = max(effective_std, 0.7%)  # Floor
  threshold = effective_std * 1.0          # Multiplier
  ```
- **Threshold Multiplier:** `1.0x SD` (ไม่ลด)
- **Market Floor:** `0.7%` (0.007)
- **Threshold Range:** ~0.7% - 1.5% (ขึ้นอยู่กับ volatility)

#### **2. Pattern Matching:**
- **Min Stats:** `25` (จำนวน pattern matches ขั้นต่ำ)
- **Gatekeeper:** `min_prob >= 53.0%` (Prob% ขั้นต่ำสำหรับการเทรด)

#### **3. Strategy Logic:**
- **Type:** **MEAN_REVERSION**
- **Description:** Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง)
- **Direction:**
  - Pattern `+` → SHORT (intended_dir = -1)
  - Pattern `-` → LONG (intended_dir = 1)

#### **4. Risk Management:**
- **Stop Loss:** 1.5%
- **Take Profit:** 3.5%
- **Max Hold:** 5 days
- **Trailing Stop:** Activate 1.5%, Distance 50%

#### **5. Display Criteria (ใน calculate_metrics.py):**
- **Prob%:** >= 60%
- **RRR:** >= 1.3
- **Count:** >= 30

---

### 🇺🇸 **US Market**

#### **1. Pattern Detection Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  effective_std = max(20-day SD, 252-day SD)
  effective_std = max(effective_std, 0.6%)  # Floor
  threshold = effective_std * 0.9         # Multiplier
  ```
- **Threshold Multiplier:** `0.9x SD` (ลด 10%)
- **Market Floor:** `0.6%` (0.006)
- **Threshold Range:** ~0.54% - 1.08% (ขึ้นอยู่กับ volatility)

#### **2. Pattern Matching:**
- **Min Stats:** `20` (relaxed - เพิ่มสัญญาณ)
- **Gatekeeper:** `min_prob >= 52.0%`
- **Quality Filter:** `AvgWin > AvgLoss` (key differentiator)

#### **3. Strategy Logic:**
- **Type:** **US_HYBRID_VOL** (Hybrid Volatility Strategy)
- **Description:** 
  - **HIGH_VOL** (current_vol > avg_vol * 1.2) → **REVERSION** (fade the spike)
  - **LOW_VOL** (current_vol <= avg_vol * 1.2) → **TREND** (ride momentum)
- **Direction:**
  - HIGH_VOL + Pattern `+` → SHORT
  - HIGH_VOL + Pattern `-` → LONG
  - LOW_VOL + Pattern `+` → LONG
  - LOW_VOL + Pattern `-` → SHORT

#### **4. Risk Management:**
- **Stop Loss:** 1.5%
- **Take Profit:** 5.0%
- **Max Hold:** 5 days
- **Trailing Stop:** Activate 1.5%, Distance 50%

#### **5. Display Criteria (ใน calculate_metrics.py):**
- **Prob%:** >= 60%
- **RRR:** >= 1.5
- **Count:** >= 15

---

### 🇹🇼 **TAIWAN Market**

#### **1. Pattern Detection Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  effective_std = max(20-day SD, 252-day SD)
  effective_std = max(effective_std, 0.5%)  # Floor
  threshold = effective_std * 0.9          # Multiplier
  ```
- **Threshold Multiplier:** `0.9x SD` (ลด 10%)
- **Market Floor:** `0.5%` (0.005)
- **Threshold Range:** ~0.45% - 0.9% (ขึ้นอยู่กับ volatility)

#### **2. Pattern Matching:**
- **Min Stats:** `25` (เพิ่มคุณภาพ)
- **Gatekeeper:** `min_prob >= 51.0%`

#### **3. Strategy Logic:**
- **Type:** **REGIME_AWARE** (Regime-Aware Strategy)
- **Description:** 
  - **BULL Market** (Price > SMA50 > SMA200) → **TREND FOLLOWING** (follow the move)
  - **BEAR/SIDEWAYS Market** (ไม่ใช่ BULL) → **MEAN REVERSION** (fade the move)
- **Direction:**
  - BULL + Pattern `+` → LONG
  - BULL + Pattern `-` → SHORT
  - BEAR/SIDEWAYS + Pattern `+` → SHORT
  - BEAR/SIDEWAYS + Pattern `-` → LONG

#### **4. Risk Management:**
- **Stop Loss:** 1.0%
- **Take Profit:** 6.5%
- **Max Hold:** 10 days
- **Trailing Stop:** Activate 1.0%, Distance 30%

#### **5. Display Criteria (ใน calculate_metrics.py):**
- **Prob%:** >= 55%
- **RRR:** >= 1.5
- **Count:** >= 15 (และ <= 2000)

---

### 🇨🇳 **CHINA/HK Market**

#### **1. Pattern Detection Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  effective_std = max(20-day SD, 252-day SD)
  effective_std = max(effective_std, 0.5%)  # Floor
  threshold = effective_std * 0.9         # Multiplier
  ```
- **Threshold Multiplier:** `0.9x SD` (ลด 10%)
- **Market Floor:** `0.5%` (0.005)
- **Threshold Range:** ~0.45% - 0.9% (ขึ้นอยู่กับ volatility)

#### **2. Pattern Matching:**
- **Min Stats:** `30` (V13.7: เพิ่มจาก 25 → 30 เพื่อเพิ่มคุณภาพ)
- **Gatekeeper:** `min_prob >= 50.0%`

#### **3. Strategy Logic:**
- **Type:** **MEAN_REVERSION**
- **Description:** Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง) - เหมือน Thai
- **Direction:**
  - Pattern `+` → SHORT (intended_dir = -1)
  - Pattern `-` → LONG (intended_dir = 1)

#### **4. Risk Management:**
- **Stop Loss:** 1.0%
- **Take Profit:** 4.0%
- **Max Hold:** 3 days
- **Trailing Stop:** Activate 1.0%, Distance 40%

#### **5. Display Criteria (ใน calculate_metrics.py):**
- **Prob%:** >= 60%
- **RRR:** >= 1.2
- **Count:** >= 15

---

### ⚪ **METALS Market**

#### **1. Pattern Detection Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  effective_std = max(20-day SD, 252-day SD)
  effective_std = max(effective_std, 0.5%)  # Floor
  threshold = effective_std * 0.9         # Multiplier
  ```
- **Threshold Multiplier:** `0.9x SD`
- **Market Floor:** `0.5%` (0.005)

#### **2. Pattern Matching:**
- **Min Stats:** `25`
- **Gatekeeper:** `min_prob >= 50.0%`

#### **3. Strategy Logic:**
- **Type:** **MEAN_REVERSION**
- **Description:** Fade the move (เหมือน Thai/China)

#### **4. Display Criteria (ใน calculate_metrics.py):**
- **Prob%:** >= 50%
- **Note:** ไม่มีหุ้นที่ Prob >= 60% และ RRR >= 1.5

---

## 📊 สรุปเปรียบเทียบ

### **Threshold Configuration:**

| ประเทศ | Multiplier | Floor | Threshold Range | เหตุผล |
|--------|-----------|-------|-----------------|--------|
| **THAI** | 1.0x | 0.7% | 0.7-1.5% | หุ้นไทยผันผวนต่ำ → threshold สูงเพื่อกรอง noise |
| **US** | 0.9x | 0.6% | 0.54-1.08% | หุ้น US ผันผวนสูง → threshold ต่ำเพื่อจับสัญญาณมากขึ้น |
| **TAIWAN** | 0.9x | 0.5% | 0.45-0.9% | Threshold ต่ำ → เพิ่มสัญญาณ |
| **CHINA/HK** | 0.9x | 0.5% | 0.45-0.9% | Threshold ต่ำ → เพิ่มสัญญาณ |

### **Strategy Logic:**

| ประเทศ | Strategy | Logic Type | Description |
|--------|----------|------------|-------------|
| **THAI** | MEAN_REVERSION | Reversion | Fade the move (100%) |
| **US** | US_HYBRID_VOL | Hybrid | HIGH_VOL → REVERSION, LOW_VOL → TREND |
| **TAIWAN** | REGIME_AWARE | Hybrid | BULL → TREND, BEAR/SIDEWAYS → REVERSION |
| **CHINA/HK** | MEAN_REVERSION | Reversion | Fade the move (100%) |
| **METALS** | MEAN_REVERSION | Reversion | Fade the move (100%) |

### **Gatekeeper (min_prob):**

| ประเทศ | min_prob | เหตุผล |
|--------|----------|--------|
| **THAI** | 53.0% | สูงสุด - คุณภาพสูง |
| **US** | 52.0% | + Quality Filter (AvgWin > AvgLoss) |
| **TAIWAN** | 51.0% | กลาง |
| **CHINA/HK** | 50.0% | ต่ำสุด - เพิ่มสัญญาณ |
| **METALS** | 50.0% | ต่ำสุด |

### **Display Criteria (ใน calculate_metrics.py):**

| ประเทศ | Prob% | RRR | Count | เหตุผล |
|--------|------|-----|-------|--------|
| **THAI** | >= 60% | >= 1.3 | >= 30 | High frequency, high accuracy |
| **US** | >= 60% | >= 1.5 | >= 15 | Lower frequency, high impact |
| **TAIWAN** | >= 55% | >= 1.5 | >= 15 | Quality over quantity |
| **CHINA/HK** | >= 60% | >= 1.2 | >= 15 | Realistic win rate |
| **METALS** | >= 50% | - | - | ไม่มีหุ้นที่ผ่านเกณฑ์สูง |

---

## 📝 หมายเหตุ

1. **Threshold Calculation:**
   - `effective_std = max(20-day SD, 252-day SD)`
   - `effective_std = max(effective_std, market_floor)`
   - `threshold = effective_std * threshold_multiplier`

2. **Strategy Logic:**
   - **MEAN_REVERSION:** Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง)
   - **TREND FOLLOWING:** Follow the move (ซื้อเมื่อขึ้น, ขายเมื่อลง)
   - **US_HYBRID_VOL:** ปรับตาม volatility (HIGH_VOL → REVERSION, LOW_VOL → TREND)
   - **REGIME_AWARE:** ปรับตาม market regime (BULL → TREND, BEAR/SIDEWAYS → REVERSION)

3. **Display Criteria:**
   - เกณฑ์ที่ใช้ในการแสดงผลใน `calculate_metrics.py`
   - อาจแตกต่างจาก Gatekeeper (min_prob) ที่ใช้ในการเทรดจริง

---

**Last Updated:** 2026-02-13  
**Status:** ✅ Complete - ตารางสรุปรายละเอียดการตั้งค่าของแต่ละประเทศ

