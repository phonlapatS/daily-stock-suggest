# China Market V13.2 - Separated Logic

## 📋 Summary

แยก logic ของ China market ให้ชัดเจน ไม่ปนกับ logic อื่นๆ เพื่อให้:
- **Maintain ง่าย** - แก้ไขเฉพาะส่วน China market
- **Test ง่าย** - ทดสอบหลายค่าได้โดยไม่กระทบตลาดอื่น
- **Debug ง่าย** - หา logic ของ China market ได้เร็ว

---

## ✅ Changes Made

### 1. Threshold Multiplier

**Before:**
```python
else:
    threshold_multiplier = 0.9     # CN: sweet spot
```

**After:**
```python
elif is_china_market:
    # China Market: Default threshold (can be overridden via kwargs)
    threshold_multiplier = kwargs.get('threshold_multiplier', 0.9)  # CN: sweet spot
else:
    threshold_multiplier = 0.9     # Default fallback
```

**Location:** `scripts/backtest.py` line ~375

---

### 2. Min Stats

**Before:**
```python
else:
    min_stats = 25                 # CN: balanced
```

**After:**
```python
elif is_china_market:
    # China Market: Default min_stats (can be overridden via kwargs)
    min_stats = kwargs.get('min_stats', 25)  # CN: balanced
else:
    min_stats = 25                 # Default fallback
```

**Location:** `scripts/backtest.py` line ~385

---

### 3. Risk Management Parameters

**Before:**
```python
elif is_china_market:
    RM_STOP_LOSS = kwargs.get('stop_loss', 1.2)
    RM_TAKE_PROFIT = kwargs.get('take_profit', 5.5)
    RM_MAX_HOLD = kwargs.get('max_hold', 8)
    RM_TRAIL_ACTIVATE = 1.0
    RM_TRAIL_DISTANCE = 40.0
```

**After:**
```python
elif is_china_market:
    # ========================================================================
    # CHINA MARKET RISK MANAGEMENT - Separated for clarity and testing
    # ========================================================================
    # All parameters can be overridden via kwargs for testing:
    #   - stop_loss: Override SL %
    #   - take_profit: Override TP %
    #   - max_hold: Override max hold days
    #   - trail_activate: Override trailing stop activation %
    #   - trail_distance: Override trailing stop distance %
    # ========================================================================
    RM_STOP_LOSS = kwargs.get('stop_loss', 1.2)
    RM_TAKE_PROFIT = kwargs.get('take_profit', 5.5)
    RM_MAX_HOLD = kwargs.get('max_hold', 8)
    RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 1.0)
    RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)
```

**Location:** `scripts/backtest.py` line ~474-490

---

### 4. Gatekeeper (Min Prob)

**Before:**
```python
elif is_china_market:
    min_prob = 51.0  # China V13.1: ลดจาก 53.0% → 51.0% (เพิ่ม Count)
```

**After:**
```python
elif is_china_market:
    # ====================================================================
    # CHINA MARKET GATEKEEPER - Separated for clarity
    # ====================================================================
    # China V13.1: ลดจาก 53.0% → 51.0% (เพิ่มหุ้นที่เทรดได้)
    # Can be overridden via kwargs['min_prob'] for testing
    # ====================================================================
    min_prob = kwargs.get('min_prob', 51.0)
```

**Location:** `scripts/backtest.py` line ~660

---

### 5. CLI Arguments for Testing

**Added:**
```python
# China Market Testing Parameters
parser.add_argument('--stop_loss', type=float, default=None, help='Override stop loss % (for testing)')
parser.add_argument('--take_profit', type=float, default=None, help='Override take profit % (for testing)')
parser.add_argument('--max_hold', type=int, default=None, help='Override max hold days (for testing)')
parser.add_argument('--trail_activate', type=float, default=None, help='Override trailing stop activation % (for testing)')
parser.add_argument('--trail_distance', type=float, default=None, help='Override trailing stop distance % (for testing)')
parser.add_argument('--min_prob', type=float, default=None, help='Override min_prob % for gatekeeper (for testing)')
```

**Location:** `scripts/backtest.py` line ~1141-1147

---

### 6. Pass kwargs through backtest_all

**Before:**
```python
def backtest_all(..., threshold_multiplier=None, ...):
    ...
    result = backtest_single(..., threshold_multiplier=threshold_multiplier, ...)
```

**After:**
```python
def backtest_all(..., threshold_multiplier=None, ..., **kwargs):
    ...
    result = backtest_single(..., threshold_multiplier=threshold_multiplier, ..., **kwargs)
```

**Location:** `scripts/backtest.py` line ~870, ~973

---

## 🎯 Benefits

### 1. **Maintainability**
- แก้ไข logic ของ China market ได้โดยไม่กระทบตลาดอื่น
- หา logic ของ China market ได้เร็ว (มี comment ชัดเจน)

### 2. **Testability**
- ทดสอบหลายค่าได้โดยไม่ต้องแก้ code
- ใช้ CLI arguments หรือ kwargs ผ่าน Python script

### 3. **Clarity**
- Logic ของ China market แยกชัดเจน
- มี comment อธิบายแต่ละส่วน

---

## 📝 Usage Examples

### Example 1: Test Max Hold = 6 days

```bash
python scripts/backtest.py --full --bars 2000 --group CHINA --fast \
  --max_hold 6
```

### Example 2: Test Threshold = 0.85

```bash
python scripts/backtest.py --full --bars 2000 --group CHINA --fast \
  --multiplier 0.85
```

### Example 3: Test Multiple Parameters

```bash
python scripts/backtest.py --full --bars 2000 --group CHINA --fast \
  --max_hold 7 \
  --multiplier 0.9 \
  --stop_loss 1.2 \
  --take_profit 5.5
```

### Example 4: Via Python Script

```python
from scripts.backtest import backtest_all

# Test Max Hold = 8, Threshold = 0.9
backtest_all(
    n_bars=2000,
    full_scan=True,
    target_group='CHINA',
    fast_mode=True,
    max_hold=8,
    threshold_multiplier=0.9
)
```

---

## 🔍 How to Find China Market Logic

### Search for:
1. `is_china_market` - เงื่อนไขหลัก
2. `CHINA MARKET` - Comment header
3. `CN:` - Comment สำหรับ China market

### Key Locations:
- **Threshold:** Line ~375
- **Min Stats:** Line ~385
- **Floor:** Line ~392
- **RM Parameters:** Line ~474-490
- **Gatekeeper:** Line ~660

---

## ⚠️ Notes

1. **Default Values:** ถ้าไม่ส่ง kwargs จะใช้ค่า default (V13.2)
2. **Override Priority:** kwargs > Default values
3. **Other Markets:** Logic ของตลาดอื่นไม่เปลี่ยน (Thai, US, Taiwan)

---

**Last Updated:** 2026-02-13  
**Version:** V13.2  
**Status:** ✅ **COMPLETED**

