# 📊 Basic System: Logic ของแต่ละประเทศ

**วันที่:** 2026-02-13  
**เป้าหมาย:** สรุป logic, threshold, และเกณฑ์การคัดกรองของแต่ละประเทศ

---

## 📋 สรุป Logic ของแต่ละประเทศ

### **🇹🇭 THAI Market**

#### **1. Pattern Matching Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  short_std = pct_change.rolling(20).std()
  long_std = pct_change.rolling(252).std()
  effective_std = np.maximum(short_std, long_std.fillna(0))
  market_floor = 0.7% (0.007)
  threshold_multiplier = 1.0x
  threshold = max(effective_std, market_floor) * 1.0
  ```
- **Floor:** 0.7% (0.007)
- **Multiplier:** 1.0x

#### **2. Gatekeeper Criteria:**
- **Prob Threshold:** 55%
- **Min Stats:** 25
- **RRR:** Metric เท่านั้น (ไม่ใช่ filter)

#### **3. Direction Logic:**
- **Strategy:** Try both LONG และ SHORT → เลือก Prob สูงสุด

#### **4. Risk Management:**
- **Volume Ratio Filter:** ไม่มี
- **Regime Filter:** ไม่มี

---

### **🇺🇸 US Market**

#### **1. Pattern Matching Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  short_std = pct_change.rolling(20).std()
  long_std = pct_change.rolling(252).std()
  effective_std = np.maximum(short_std, long_std.fillna(0))
  market_floor = 0.6% (0.006)
  threshold_multiplier = 0.9x
  threshold = max(effective_std, market_floor) * 0.9
  ```
- **Floor:** 0.6% (0.006)
- **Multiplier:** 0.9x

#### **2. Gatekeeper Criteria:**
- **Prob Threshold:** 55%
- **Min Stats:** 25
- **RRR:** Metric เท่านั้น (ไม่ใช่ filter)

#### **3. Direction Logic:**
- **Strategy:** Try both LONG และ SHORT → เลือก Prob สูงสุด

#### **4. Risk Management:**
- **Volume Ratio Filter:** ไม่มี
- **Regime Filter:** ไม่มี

---

### **🇹🇼 TAIWAN Market**

#### **1. Pattern Matching Threshold:**
- **Type:** Dynamic (Rolling Window)
- **Calculation:**
  ```python
  short_std = pct_change.rolling(20).std()
  long_std = pct_change.rolling(252).std()
  effective_std = np.maximum(short_std, long_std.fillna(0))
  market_floor = 0.5% (0.005)
  threshold_multiplier = 0.9x
  threshold = max(effective_std, market_floor) * 0.9
  ```
- **Floor:** 0.5% (0.005)
- **Multiplier:** 0.9x

#### **2. Gatekeeper Criteria:**
- **Prob Threshold:** 55%
- **Min Stats:** 25
- **RRR:** Metric เท่านั้น (ไม่ใช่ filter)

#### **3. Direction Logic:**
- **Strategy:** Try both LONG และ SHORT → เลือก Prob สูงสุด

#### **4. Risk Management:**
- **Volume Ratio Filter:** ไม่มี
- **Regime Filter:** ไม่มี

---

### **🇨🇳 CHINA/HK Market**

#### **1. Pattern Matching Threshold:**
- **Type:** Dynamic (Overall SD จากทั้งหมด 5000 bars)
- **Calculation:**
  ```python
  overall_std = pct_change.std()  # SD จากทั้งหมด 5000 bars
  effective_std = pd.Series([overall_std] * len(df), index=df.index)
  market_floor = 0.6% (0.006)
  threshold_multiplier = 0.8x  # ลดจาก 1.0x เพื่อให้ได้ pattern มากขึ้น
  threshold = max(effective_std, market_floor) * 0.8
  ```
- **Floor:** 0.6% (0.006)
- **Multiplier:** 0.8x (ลดลงเพื่อให้ได้ pattern มากขึ้น)
- **พิเศษ:** ใช้ SD จากทั้งหมด 5000 bars (ไม่ใช่ rolling window)

#### **2. Gatekeeper Criteria:**
- **Prob Threshold:** 48% (ลดจาก 50% เพื่อให้ได้หุ้นมากขึ้น)
- **Min Stats:** 25 (เพิ่มจาก 20 เพื่อให้ count น่าเชื่อถือขึ้น)
- **RRR:** Metric เท่านั้น (ไม่ใช่ filter)

#### **3. Direction Logic:**
- **Strategy:** Mean Reversion (Fade the move)
  ```python
  # + (Up anomaly) -> SHORT (expect reversion down)
  # - (Down anomaly) -> LONG (expect reversion up)
  last_char = pattern_str[-1]
  if last_char == '+':
      direction = "SHORT"
  elif last_char == '-':
      direction = "LONG"
  ```

#### **4. Risk Management:**
- **Volume Ratio Filter:** ✅ มี
  ```python
  vr = volume.iloc[-1] / vol_avg_20.iloc[-1]
  if vr < 0.5:
      return None  # Dead Zone - no liquidity
  ```
- **Regime Filter:** ไม่มี (ใน Basic System)

---

## 📊 ตารางเปรียบเทียบ

| Country | Threshold Type | Floor | Multiplier | Prob Threshold | Min Stats | Direction Logic | VR Filter |
|---------|---------------|-------|------------|----------------|-----------|-----------------|-----------|
| **THAI** | Dynamic (Rolling) | 0.7% | 1.0x | 55% | 25 | Try Both | ❌ |
| **US** | Dynamic (Rolling) | 0.6% | 0.9x | 55% | 25 | Try Both | ❌ |
| **TAIWAN** | Dynamic (Rolling) | 0.5% | 0.9x | 55% | 25 | Try Both | ❌ |
| **CHINA/HK** | Dynamic (Overall) | 0.6% | 0.8x | 48% | 25 | Reversion | ✅ |

---

## 🔍 รายละเอียดเพิ่มเติม

### **1. Threshold Calculation:**

#### **Dynamic (Rolling Window) - THAI, US, TAIWAN:**
```python
short_std = pct_change.rolling(20).std()      # 20-day SD
long_std = pct_change.rolling(252).std()      # 252-day SD
effective_std = np.maximum(short_std, long_std.fillna(0))
effective_std = np.maximum(effective_std, market_floor)
threshold = effective_std * threshold_multiplier
```

**ผลลัพธ์:** Threshold เปลี่ยนแปลงตาม volatility (rolling window)

#### **Dynamic (Overall SD) - CHINA/HK:**
```python
overall_std = pct_change.std()  # SD จากทั้งหมด 5000 bars
effective_std = pd.Series([overall_std] * len(df), index=df.index)
effective_std = np.maximum(effective_std, market_floor)
threshold = effective_std * threshold_multiplier
```

**ผลลัพธ์:** Threshold คงที่ (ใช้ SD จากทั้งหมด)

---

### **2. Direction Logic:**

#### **Try Both (THAI, US, TAIWAN):**
```python
for direction in ["LONG", "SHORT"]:
    stats = calculate_stats(next_returns, direction)
    if stats['prob'] > best_prob:
        best_direction = direction
```

**ผลลัพธ์:** เลือก direction ที่ Prob สูงสุด

#### **Reversion (CHINA/HK):**
```python
last_char = pattern_str[-1]
if last_char == '+':
    direction = "SHORT"  # Fade the up move
elif last_char == '-':
    direction = "LONG"   # Fade the down move
```

**ผลลัพธ์:** ใช้ reversion logic (Fade the move)

---

### **3. Risk Management:**

#### **Volume Ratio Filter (CHINA/HK only):**
```python
vr = volume.iloc[-1] / vol_avg_20.iloc[-1]
if vr < 0.5:
    return None  # Dead Zone - no liquidity
```

**ผลลัพธ์:** กรองหุ้นที่ไม่มี liquidity (VR < 0.5)

---

## ✅ สรุป

### **THAI:**
- Threshold: Dynamic (Rolling), Floor 0.7%, Multiplier 1.0x
- Gatekeeper: Prob >= 55%, Min Stats >= 25
- Direction: Try Both → เลือก Prob สูงสุด
- Risk Management: ไม่มี

### **US:**
- Threshold: Dynamic (Rolling), Floor 0.6%, Multiplier 0.9x
- Gatekeeper: Prob >= 55%, Min Stats >= 25
- Direction: Try Both → เลือก Prob สูงสุด
- Risk Management: ไม่มี

### **TAIWAN:**
- Threshold: Dynamic (Rolling), Floor 0.5%, Multiplier 0.9x
- Gatekeeper: Prob >= 55%, Min Stats >= 25
- Direction: Try Both → เลือก Prob สูงสุด
- Risk Management: ไม่มี

### **CHINA/HK:**
- Threshold: Dynamic (Overall SD), Floor 0.6%, Multiplier 0.8x
- Gatekeeper: Prob >= 48%, Min Stats >= 25
- Direction: Reversion (Fade the move)
- Risk Management: Volume Ratio Filter (VR < 0.5 = skip)

---

## 🔗 Related Documents

- [BASIC_SYSTEM_ARCHITECTURE.md](BASIC_SYSTEM_ARCHITECTURE.md) - Architecture
- [CHINA_HK_RISK_MANAGEMENT.md](CHINA_HK_RISK_MANAGEMENT.md) - Risk Management สำหรับจีน/ฮ่องกง

