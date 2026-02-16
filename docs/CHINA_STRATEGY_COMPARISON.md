# China Market - Strategy Comparison

## 📋 คำถาม

**"แล้วหุ้นประเทศจีน ใช้ strategy เหมือนหุ้นประเทศอื่นไม่ได้หรอ"**

---

## 🔍 สถานะปัจจุบัน

### Strategy ที่ใช้ในแต่ละตลาด:

| Market | Current Strategy | Engine | Logic |
|--------|------------------|--------|-------|
| **Thai** | MEAN_REVERSION | MEAN_REVERSION | Fade the move (ขายเมื่อขึ้น, ซื้อเมื่อลง) |
| **US** | US_HYBRID_VOL | TREND_MOMENTUM | Follow the move (LONG ONLY) |
| **Taiwan** | REGIME_AWARE | TREND_MOMENTUM | Follow the move |
| **China** | MEAN_REVERSION | MEAN_REVERSION | Fade the move (เหมือน Thai) |

### สรุป:
- **China ใช้ MEAN_REVERSION** (เหมือน Thai)
- **US และ Taiwan ใช้ TREND_MOMENTUM** (Follow the move)

---

## 🤔 ทำไม China ใช้ MEAN_REVERSION?

### เหตุผลที่ใช้ MEAN_REVERSION:
1. **Market Characteristics:**
   - China market มีความผันผวนสูง
   - Mean reversion ทำงานได้ดีในตลาดที่ผันผวน

2. **Historical Testing:**
   - มีการทดสอบแล้วว่า MEAN_REVERSION ดีกว่า TREND_FOLLOWING สำหรับ China
   - (ดู `scripts/analyze_china.py`)

3. **Similar to Thai:**
   - China market มีลักษณะคล้าย Thai market
   - ใช้ strategy เดียวกัน

---

## 🧪 การทดสอบ Strategy อื่นๆ

### มีการทดสอบแล้ว:

**File:** `scripts/analyze_china.py`

ทดสอบ 3 strategies:
1. **STAT_FOLLOW** (Current - ใช้ historical probability)
2. **MEAN_REVERSION** (Fade the move)
3. **TREND_FOLLOWING** (Follow the move)

### ผลลัพธ์:
- ต้องรัน `python scripts/analyze_china.py` เพื่อดูผลลัพธ์
- เปรียบเทียบ Win Rate, RRR ของแต่ละ strategy

---

## 💡 แนวทางทดสอบ Strategy อื่นๆ

### Option 1: ทดสอบ TREND_FOLLOWING สำหรับ China

**เปลี่ยน Engine ใน config.py:**

```python
"GROUP_C_CHINA_HK": {
    "description": "China/HK Market",
    "engine": "TREND_MOMENTUM",  # เปลี่ยนจาก MEAN_REVERSION
    ...
}
```

**หรือทดสอบผ่าน backtest.py:**

```python
# ใน backtest.py line 703-704
elif is_thai_market:
    strategy = "MEAN_REVERSION"
elif is_china_market:
    strategy = "TREND_FOLLOWING"  # ทดสอบเปลี่ยนเป็น TREND
else:
    strategy = "REGIME_AWARE"
```

### Option 2: ทดสอบ US_HYBRID_VOL สำหรับ China

```python
elif is_china_market:
    strategy = "US_HYBRID_VOL"  # ทดสอบใช้ strategy เหมือน US
```

### Option 3: ทดสอบ REGIME_AWARE สำหรับ China

```python
elif is_china_market:
    strategy = "REGIME_AWARE"  # ทดสอบใช้ strategy เหมือน Taiwan
```

---

## 🔬 แผนการทดสอบ

### Step 1: วิเคราะห์ผลลัพธ์ปัจจุบัน

```bash
python scripts/analyze_china.py
```

ดูว่า:
- STAT_FOLLOW (current) มี Win Rate และ RRR เท่าไหร่
- MEAN_REVERSION มี Win Rate และ RRR เท่าไหร่
- TREND_FOLLOWING มี Win Rate และ RRR เท่าไหร่

### Step 2: ทดสอบ TREND_FOLLOWING

**เปลี่ยน strategy ใน backtest.py:**

```python
elif is_china_market:
    strategy = "TREND_FOLLOWING"  # หรือ "US_HYBRID_VOL"
```

**รัน backtest:**

```bash
python scripts/backtest.py --full --bars 2000 --group CHINA --fast
python scripts/calculate_metrics.py
```

**เปรียบเทียบผลลัพธ์:**
- Win Rate
- RRR
- Count
- Stocks passing

### Step 3: ทดสอบ US_HYBRID_VOL

ทำเหมือน Step 2 แต่เปลี่ยนเป็น `"US_HYBRID_VOL"`

### Step 4: เปรียบเทียบและสรุป

เปรียบเทียบ:
- MEAN_REVERSION (current)
- TREND_FOLLOWING
- US_HYBRID_VOL
- REGIME_AWARE

เลือก strategy ที่ดีที่สุด

---

## 📊 Expected Results

### ถ้า TREND_FOLLOWING ดีกว่า:

**Signs:**
- Win Rate สูงกว่า
- RRR สูงกว่า
- Stocks passing มากขึ้น

**Action:**
- เปลี่ยน strategy เป็น TREND_FOLLOWING

### ถ้า MEAN_REVERSION ดีกว่า (current):

**Signs:**
- Win Rate สูงกว่า
- RRR สูงกว่า
- Stocks passing มากขึ้น

**Action:**
- ใช้ MEAN_REVERSION ต่อไป (current)

---

## 🚀 Quick Test

### ทดสอบ TREND_FOLLOWING:

1. **แก้ไข backtest.py:**
   ```python
   # Line 703-704
   elif is_thai_market:
       strategy = "MEAN_REVERSION"
   elif is_china_market:
       strategy = "TREND_FOLLOWING"  # เปลี่ยนตรงนี้
   ```

2. **รัน backtest:**
   ```bash
   python scripts/backtest.py --full --bars 2000 --group CHINA --fast
   python scripts/calculate_metrics.py
   ```

3. **เปรียบเทียบกับผลลัพธ์เดิม**

---

## ⚠️ ข้อควรระวัง

1. **Engine vs Strategy:**
   - Engine = Logic engine (MEAN_REVERSION, TREND_MOMENTUM)
   - Strategy = Label ที่แสดงในผลลัพธ์
   - ต้องเปลี่ยนทั้ง engine และ strategy

2. **Config.py:**
   - ถ้าเปลี่ยน engine ใน config.py ต้อง restart backtest
   - ถ้าเปลี่ยน strategy ใน backtest.py จะ override config

3. **Testing:**
   - ทดสอบทีละ strategy
   - บันทึกผลลัพธ์เพื่อเปรียบเทียบ

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR TESTING**

