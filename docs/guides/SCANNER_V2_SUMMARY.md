# Scanner V2 - Mixed Streak System Summary

## ✅ สิ่งที่ Implement แล้ว

### 1. **Dynamic Threshold** (90th Percentile)
```python
threshold = df['pct_change'].abs().rolling(126).quantile(0.90)
threshold = max(threshold, 1.0)  # Floor = 1.0%
```

**ผลลัพธ์:**
- PTT: 1.61% (แทนที่จะเป็น 1.65% แบบเดิม)
- SCC: 2.86%
- CENTEL: 4.54%

**ข้อดี:**
- Robust to outliers
- Adaptive to market regime (6 เดือน)
- ไม่ต้องสมมติ distribution

---

### 2. **Volatility Classification**
```python
annual_vol = std(pct_change) * sqrt(252)

if annual_vol < 20%: "Low"
elif annual_vol <= 60%: "Med"
else: "High"
```

**ผลลัพธ์:**
- Low: 0 หุ้น
- **Med: 40 หุ้น** (ส่วนใหญ่)
- High: 1 หุ้น (THAI)

**ประโยชน์:**
- แบ่งกลุ่มหุ้น
- Portfolio management
- Risk assessment

---

### 3. **Mixed Streak Logic**
```python
# นับวันที่ abs(change) > threshold ติดต่อกัน
# ไม่สนทิศทาง (+ หรือ - ก็นับ)

Example:
Day 1: +5% > threshold → Streak = 1
Day 2: -4% > threshold → Streak = 2 (mixed!)
Day 3: +6% > threshold → Streak = 3
Day 4: +0.5% < threshold → Break!
```

**ผลลัพธ์:**
```
Symbol  Streak_Status    Events  WinRate
SCC     🟢 Up (Vol 1)    282     41.1%
MINT    🔴 Down (Vol 1)  259     42.5%
PTT     🟢 Up (Vol 1)    262     46.6%
ADVANC  🟢 Up (Vol 1)    254     47.2%
```

**ตีความ:**
- "Vol 1" = volatility streak (1 วันที่ผันผวนเกิน threshold)
- WinRate ~42-47% = ใกล้เคียง 50% (random)
- Sample size ใหญ่ (254-282 events)

---

## 📊 เปรียบเทียบกับระบบเดิม

### **V1 (Directional Streak):**
```
Symbol  Streak_Status    Events  WinRate
PTT     🟢 Up 1 Days     272     43.0%
SCC     🟢 Up 1 Days     90      43.3%
CENTEL  🔴 Down 1 Days   116     51.7%
MINT    🔴 Down 1 Days   215     44.7%
```

**ลักษณะ:**
- แยก Up/Down streak
- Sample size น้อยกว่า (90-272)
- WinRate ชัดเจนกว่า (43-51%)

---

### **V2 (Mixed Streak):**
```
Symbol  Streak_Status    Events  WinRate
PTT     🟢 Up (Vol 1)    262     46.6%
SCC     🟢 Up (Vol 1)    282     41.1%
CENTEL  ⚪ Quiet          0       0%
MINT    🔴 Down (Vol 1)  259     42.5%
```

**ลักษณะ:**
- นับ volatility (ไม่สนทิศทาง)
- Sample size มากกว่า (254-282)
- WinRate ใกล้ 50% (less predictive)

---

## 💡 การวิเคราะห์

### **V2 เหมาะกับ:**
1. **Volatility Trading** - หา high vol periods
2. **Options Trading** - IV trading
3. **Risk Management** - identify volatile stocks

### **V2 ไม่เหมาะกับ:**
1. **Trend Following** - ไม่บอก trend direction
2. **Momentum Trading** - WinRate ใกล้ 50%
3. **Directional Prediction** - mixed pattern ไม่มีนัย

---

## 🎯 Recommendation

### **ใช้ทั้ง 2 ระบบ:**

#### **V1 (Directional)** → สำหรับ Prediction
```bash
python scripts/scanner.py
```
- บอก trend direction
- Historical probability มีนัย
- WinRate มีความหมาย

#### **V2 (Mixed)** → สำหรับ Volatility Analysis
```bash
python scripts/scanner_v2.py
```
- บอก volatility periods
- Volatility classification
- Risk assessment

---

## 📋 Files Created

1. **`core/dynamic_streak_v2.py`** - Core logic
   - `apply_dynamic_logic()` - Main function
   - `calculate_historical_probability_mixed()` - Probability calc

2. **`scripts/scanner_v2.py`** - Scanner V2
   - Mixed streak scanner
   - Volatility classification
   - Dashboard output

3. **`results/market_scanner_v2.csv`** - Output
   - Latest scan results
   - CSV format

4. **`results/scanner_v2_history/`** - Archives
   - Timestamped backups

---

## 🚀 Usage

```bash
# Directional Streak (Prediction)
python scripts/scanner.py

# Mixed Streak (Volatility)
python scripts/scanner_v2.py

# วิเคราะห์ทั้ง 2 ระบบ
python scripts/scanner.py && python scripts/scanner_v2.py
```

---

## ✅ สรุป

**V2 implement สมบูรณ์ตาม prompt!**
- ✅ 90th Percentile Threshold
- ✅ Volatility Classification  
- ✅ Mixed Streak Logic
- ✅ Tested with 41 stocks
- ✅ CSV export with history

**แต่:**
- V2 เหมาะกับ Volatility Analysis
- V1 เหมาะกับ Prediction
- **ใช้ทั้ง 2 ระบบร่วมกันดีที่สุด!** 🎯
