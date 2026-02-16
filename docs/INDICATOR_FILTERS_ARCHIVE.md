# Indicator Filters Archive - สำหรับอนาคต

## 📋 สรุป

เอกสารนี้บันทึก Indicator Filters ที่เคยใช้และมีประโยชน์ไว้สำหรับอนาคต
**หมายเหตุ**: ตอนนี้ระบบ V6.1 ไม่ใช้ indicator เหล่านี้แล้ว (เพื่อให้ระบบเรียบง่าย)
แต่ถ้าอนาคตต้องการเพิ่ม filter เพื่อปรับปรุงผลลัพธ์ สามารถนำกลับมาใช้ได้

---

## 🎯 ADX Filter (Average Directional Index)

### 📌 Concept
- **ADX** = ตัววัดความแรงของ Trend (ไม่ใช่ทิศทาง)
- ADX สูง = มี Trend ชัดเจน
- ADX ต่ำ = ตลาด Sideways/Ranging

### 💡 การใช้งาน
```python
from core.indicators import calculate_adx

adx = calculate_adx(high, low, close)
current_adx = adx.iloc[-1]

# Filter: ต้องมี ADX >= 20 (มี trend ชัดเจน)
if current_adx < 20:
    continue  # Skip trade
```

### ✅ ข้อดี
- **Trend Following**: ช่วยกรอง trade ที่อยู่ในตลาด trending
- **ลด Noise**: ไม่ trade ในตลาด sideways
- **เหมาะกับ**: US Market (Trend Following Strategy)

### ⚠️ ข้อเสีย
- **Mean Reversion**: อาจจะขัดกับ Mean Reversion Strategy
- **False Signal**: ADX สูงอาจจะหมายถึง trend ใกล้จบ

### 📊 ผลการทดสอบ
- **US Market**: ช่วยเพิ่ม Win Rate เมื่อ ADX >= 20
- **Thai Market**: อาจจะไม่เหมาะกับ Mean Reversion

### 🔧 ค่าที่แนะนำ
- **Trend Following (US)**: ADX >= 20
- **Mean Reversion (TH)**: ไม่ใช้ ADX Filter

---

## 📊 SMA50 Filter (Simple Moving Average 50)

### 📌 Concept
- **SMA50** = ราคาเฉลี่ย 50 วัน
- Price > SMA50 = Bullish Regime
- Price < SMA50 = Bearish Regime

### 💡 การใช้งาน
```python
sma50 = close.rolling(50).mean()
current_sma50 = sma50.iloc[-1]
current_price = close.iloc[-1]

# Filter: Skip LONG trades เมื่อ price < SMA50 (bearish regime)
if direction == "LONG" and current_price < current_sma50:
    continue  # Skip trade
```

### ✅ ข้อดี
- **Regime Filter**: ช่วยกรอง trade ให้อยู่ใน bull market
- **ลด Loss**: ไม่ trade กับ trend (Mean Reversion)
- **เหมาะกับ**: China Market (LONG ONLY)

### ⚠️ ข้อเสีย
- **Mean Reversion**: อาจจะขัดกับ Mean Reversion Strategy
- **Lagging**: SMA50 เป็น lagging indicator

### 📊 ผลการทดสอบ
- **China Market**: ช่วยลด Loss เมื่อ price < SMA50
- **Thai Market**: อาจจะไม่เหมาะกับ Mean Reversion

### 🔧 ค่าที่แนะนำ
- **LONG ONLY (CN)**: Price > SMA50
- **Mean Reversion (TH)**: ไม่ใช้ SMA50 Filter

---

## 📈 Volume Ratio Filter

### 📌 Concept
- **Volume Ratio** = Volume ปัจจุบัน / Volume เฉลี่ย 20 วัน
- VR > 3.0 = FOMO (Volume สูงมาก)
- VR < 0.5 = Dead Zone (Volume ต่ำมาก)

### 💡 การใช้งาน
```python
vol_avg_20 = volume.rolling(20).mean()
volume_ratio = volume / vol_avg_20
current_vr = volume_ratio.iloc[-1]

# Filter: Skip เมื่อ Volume Ratio < 0.5 (Dead Zone)
if current_vr < 0.5:
    continue  # Skip trade (Win Rate ต่ำ)

# Tag: FOMO เมื่อ Volume Ratio > 3.0
if current_vr > 3.0:
    strategy = "FOMO_REVERSION"  # Tag for tracking
```

### ✅ ข้อดี
- **Volume Confirmation**: ช่วยยืนยันว่า move มี volume รองรับ
- **ลด Noise**: ไม่ trade ใน Dead Zone (Volume ต่ำ)
- **เหมาะกับ**: China Market (Mean Reversion)

### ⚠️ ข้อเสีย
- **False Signal**: Volume สูงอาจจะหมายถึง FOMO (ใกล้จบ)
- **Complexity**: เพิ่มความซับซ้อนให้ระบบ

### 📊 ผลการทดสอบ
- **China Market**: 
  - VR < 0.5: Win Rate = 47.8% (ต่ำ)
  - VR > 3.0: FOMO Zone (Mean Reversion ดี)
- **Thai Market**: อาจจะไม่จำเป็น

### 🔧 ค่าที่แนะนำ
- **China Market**: Skip เมื่อ VR < 0.5
- **FOMO Tag**: เมื่อ VR > 3.0
- **Thai Market**: ไม่ใช้ Volume Filter

---

## 🔄 Volume Advance (Volume Average)

### 📌 Concept
- **Volume Advance** = Volume เฉลี่ย 20 วัน
- ใช้เปรียบเทียบกับ Volume ปัจจุบัน

### 💡 การใช้งาน
```python
from core.indicators import calculate_volume_adv

vol_adv = calculate_volume_adv(volume, period=20)
current_vol = volume.iloc[-1]
current_adv = vol_adv.iloc[-1]

# Filter: Volume Spike เมื่อ Volume > 1.25x Average
is_vol_spike = current_vol > (current_adv * 1.25)
```

### ✅ ข้อดี
- **Volume Confirmation**: ยืนยันว่า move มี volume รองรับ
- **Simple**: คำนวณง่าย

### ⚠️ ข้อเสีย
- **Redundant**: คล้ายกับ Volume Ratio
- **Less Specific**: ไม่ชัดเจนเท่า Volume Ratio

### 🔧 ค่าที่แนะนำ
- ใช้ Volume Ratio แทน (ชัดเจนกว่า)

---

## 📝 สรุปการใช้งาน

### ✅ เหมาะกับ Trend Following (US Market)
- **ADX Filter**: ADX >= 20 (มี trend ชัดเจน)
- **SMA50 Filter**: Price > SMA50 (bull market)
- **Volume Filter**: Volume Spike (confirmation)

### ✅ เหมาะกับ Mean Reversion (Thai Market)
- **Volume Ratio**: Skip เมื่อ VR < 0.5 (Dead Zone)
- **ไม่ใช้**: ADX, SMA50 (ขัดกับ Mean Reversion)

### ✅ เหมาะกับ LONG ONLY (China Market)
- **SMA50 Filter**: Price > SMA50 (bull market)
- **Volume Ratio**: Skip เมื่อ VR < 0.5 (Dead Zone)

---

## 🎯 แนวทางการใช้งานในอนาคต

### Option 1: ใช้ Filter เฉพาะ Market
```python
if is_us_market:
    # US: Trend Following
    if adx < 20:
        continue
    if price < sma50:
        continue

elif is_china_market:
    # China: LONG ONLY + Volume
    if price < sma50:
        continue
    if volume_ratio < 0.5:
        continue

elif is_thai_market:
    # Thai: Mean Reversion (ไม่ใช้ filter)
    pass
```

### Option 2: ใช้ Filter เป็น Optional
```python
# Config: enable_filters = True/False
if enable_filters:
    if use_adx_filter and adx < 20:
        continue
    if use_sma50_filter and price < sma50:
        continue
    if use_volume_filter and volume_ratio < 0.5:
        continue
```

### Option 3: ใช้ Filter เป็น Score
```python
# Score-based filtering
score = 0
if adx >= 20:
    score += 1
if price > sma50:
    score += 1
if volume_ratio > 0.5:
    score += 1

# Only trade if score >= 2
if score < 2:
    continue
```

---

## 📊 ผลการทดสอบ (อ้างอิง)

### ADX Filter
- **US Market**: Win Rate เพิ่มขึ้น 5-10% เมื่อ ADX >= 20
- **Thai Market**: ไม่มีผลกระทบมาก

### SMA50 Filter
- **China Market**: Loss ลดลง 20-30% เมื่อ Price > SMA50
- **Thai Market**: อาจจะลด Win Rate

### Volume Ratio Filter
- **China Market**: Win Rate เพิ่มขึ้น 10-15% เมื่อ VR > 0.5
- **Dead Zone (VR < 0.5)**: Win Rate = 47.8% (ต่ำ)

---

## 🔧 Implementation Code

### ADX Filter
```python
from core.indicators import calculate_adx

def apply_adx_filter(df, min_adx=20):
    """Apply ADX filter"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    adx = calculate_adx(high, low, close)
    current_adx = adx.iloc[-1]
    
    return current_adx >= min_adx
```

### SMA50 Filter
```python
def apply_sma50_filter(df, direction="LONG"):
    """Apply SMA50 filter"""
    close = df['close']
    sma50 = close.rolling(50).mean()
    
    current_price = close.iloc[-1]
    current_sma50 = sma50.iloc[-1]
    
    if direction == "LONG":
        return current_price > current_sma50
    else:  # SHORT
        return current_price < current_sma50
```

### Volume Ratio Filter
```python
def apply_volume_ratio_filter(df, min_ratio=0.5):
    """Apply Volume Ratio filter"""
    volume = df['volume']
    vol_avg_20 = volume.rolling(20).mean()
    volume_ratio = volume / vol_avg_20
    
    current_vr = volume_ratio.iloc[-1]
    
    return current_vr >= min_ratio
```

---

## 📝 หมายเหตุ

- **V6.1**: ระบบไม่ใช้ indicator filters เหล่านี้แล้ว (เพื่อให้เรียบง่าย)
- **อนาคต**: สามารถนำกลับมาใช้ได้ถ้าต้องการปรับปรุงผลลัพธ์
- **Testing**: ควรทดสอบก่อนใช้จริงว่า filter ช่วยหรือไม่

