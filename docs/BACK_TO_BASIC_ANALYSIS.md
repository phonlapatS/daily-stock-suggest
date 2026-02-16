# 🔄 Back to Basic: สถิติเพียวๆ

**วันที่:** 2026-02-13  
**เป้าหมาย:** กลับไปใช้สถิติเพียวๆ แทน risk management ที่ซับซ้อน

---

## ⚠️ ปัญหาของระบบปัจจุบัน

### 1. **Max Hold สูงเกินไป (5-8 วัน)**
- **China Market**: Max Hold 8 days
- **US Market**: Max Hold 7 days  
- **Taiwan Market**: Max Hold 10 days
- **Thai Market**: Max Hold 5 days

**ปัญหา:**
- ❌ Pattern decay: Pattern matching ใช้ historical patterns → valid ในระยะสั้น
- ❌ Hold นาน = Risk สูงขึ้น (volatility compounding)
- ❌ Psychological pressure: ความกดดันสูงเมื่อ hold นาน
- ❌ User ไม่มั่นใจ: รู้สึกว่า "อาจจะไม่ work"

### 2. **Risk Management ซับซ้อนเกินไป**
ระบบปัจจุบันมี:
- ✅ ATR-based SL/TP
- ✅ Trailing Stop (Activate %, Distance %)
- ✅ Position Sizing (Risk 2% per trade)
- ✅ Production Mode (Slippage, Commission, Gap Risk)
- ✅ Multi-day hold simulation

**ปัญหา:**
- ❌ Logic ปนกันใน `backtest.py` (700+ บรรทัด)
- ❌ ยากต่อการ debug และ maintain
- ❌ ยากต่อการทดสอบ
- ❌ User ไม่มั่นใจว่า logic ถูกต้องหรือไม่

### 3. **ไม่ใช่ "สถิติเพียวๆ"**
ระบบปัจจุบัน:
- ❌ Simulate trade ด้วย risk management
- ❌ คำนวณ exit_reason, hold_days, position_pct
- ❌ ต้องผ่านหลายขั้นตอน (SL, TP, Trailing, Max Hold)

**สิ่งที่ต้องการ:**
- ✅ สถิติเพียวๆ: Prob%, RRR, match_count
- ✅ ทำนาย N+1 เพียวๆ (ไม่ต้อง simulate trade)
- ✅ เรียบง่าย เข้าใจง่าย

---

## 💡 แนวทาง "Back to Basic"

### **Core Concept: สถิติเพียวๆ**

```
1. Pattern Matching → หา match ในประวัติ
2. คำนวณสถิติ:
   - Prob% = Win Rate (จาก match results)
   - AvgWin% = ค่าเฉลี่ยของ winning trades
   - AvgLoss% = ค่าเฉลี่ยของ losing trades
   - RRR = AvgWin% / AvgLoss%
   - match_count = จำนวน match
3. Gatekeeper: Prob > 60%, match_count >= Nmin
4. Output: Direction, Prob%, RRR, match_count
```

**ไม่ต้อง:**
- ❌ Simulate trade
- ❌ Risk management (SL, TP, Trailing)
- ❌ Multi-day hold
- ❌ Position sizing

---

## 🏗️ Architecture: แยก Logic

### **Current Architecture (ซับซ้อน):**
```
backtest.py (700+ lines)
├── Pattern Matching
├── Threshold Calculation
├── Risk Management (SL, TP, Trailing, Max Hold)
├── Trade Simulation
├── Position Sizing
└── CSV Output
```

### **Proposed Architecture (เรียบง่าย):**
```
core/
├── pattern_matcher.py      # Pattern Matching Logic
│   ├── build_pattern()
│   ├── match_history()
│   └── calculate_stats()   # สถิติเพียวๆ
│
├── predictor.py            # Prediction Logic
│   ├── predict_n1()        # ทำนาย N+1
│   ├── get_direction()    # ทิศทาง (UP/DOWN)
│   └── get_probability()   # Prob%
│
└── gatekeeper.py          # Gatekeeper Logic
    ├── check_prob()        # Prob > 60%
    ├── check_match_count() # match_count >= Nmin
    └── decide_signal()     # BUY/SELL/NO-TRADE

scripts/
└── backtest_basic.py      # Core Pipeline (เรียบง่าย)
    ├── fetch_data()
    ├── run_prediction()   # เรียก pattern_matcher + predictor
    ├── apply_gatekeeper() # เรียก gatekeeper
    └── save_results()     # CSV Output
```

---

## 📊 สถิติเพียวๆ: วิธีการคำนวณ

### **1. Pattern Matching**
```python
# หา pattern ในประวัติ
pattern = "++--"  # ตัวอย่าง
matches = find_pattern_in_history(df, pattern, lookback=5000)

# แต่ละ match → ดู N+1 return
next_returns = []
for match_idx in matches:
    next_return = (df['close'].iloc[match_idx+1] - df['close'].iloc[match_idx]) / df['close'].iloc[match_idx]
    next_returns.append(next_return)
```

### **2. คำนวณสถิติ**
```python
# Prob% = Win Rate
wins = [r for r in next_returns if r > 0]
losses = [r for r in next_returns if r <= 0]
prob = len(wins) / len(next_returns) * 100

# AvgWin% = ค่าเฉลี่ยของ winning trades
avg_win = np.mean(wins) * 100 if wins else 0

# AvgLoss% = ค่าเฉลี่ยของ losing trades (absolute)
avg_loss = abs(np.mean(losses)) * 100 if losses else 0

# RRR = AvgWin% / AvgLoss%
rrr = avg_win / avg_loss if avg_loss > 0 else 0

# match_count = จำนวน match
match_count = len(next_returns)
```

### **3. Gatekeeper**
```python
# เกณฑ์: Prob > 60%, match_count >= Nmin
if prob > 60.0 and match_count >= 30:
    signal = "BUY" if direction == "UP" else "SELL"
else:
    signal = "NO-TRADE"
```

---

## 🎯 เปรียบเทียบ: Current vs Basic

| Aspect | Current System | Basic System |
|--------|----------------|--------------|
| **Pattern Matching** | ✅ มี | ✅ มี |
| **สถิติ** | ✅ มี (แต่ผ่าน RM) | ✅ มี (เพียวๆ) |
| **Risk Management** | ✅ ซับซ้อน (SL, TP, Trailing) | ❌ ไม่มี |
| **Max Hold** | ✅ 5-8 วัน | ❌ ไม่มี (N+1 เพียวๆ) |
| **Trade Simulation** | ✅ มี | ❌ ไม่มี |
| **Position Sizing** | ✅ มี | ❌ ไม่มี |
| **Complexity** | 🔴 สูง (700+ lines) | 🟢 ต่ำ (100-200 lines) |
| **Debug** | 🔴 ยาก | 🟢 ง่าย |
| **Maintain** | 🔴 ยาก | 🟢 ง่าย |
| **User Confidence** | 🔴 ต่ำ | 🟢 สูง |

---

## 📝 Implementation Plan

### **Phase 1: สร้าง Basic Pattern Matcher**
```python
# core/pattern_matcher.py
class BasicPatternMatcher:
    def match_pattern(self, df, pattern, lookback=5000):
        """หา pattern ในประวัติ"""
        pass
    
    def calculate_stats(self, matches, df):
        """คำนวณสถิติเพียวๆ"""
        pass
```

### **Phase 2: สร้าง Basic Predictor**
```python
# core/predictor.py
class BasicPredictor:
    def predict_n1(self, df, pattern):
        """ทำนาย N+1"""
        pass
    
    def get_direction(self, stats):
        """ทิศทาง (UP/DOWN)"""
        pass
```

### **Phase 3: สร้าง Basic Gatekeeper**
```python
# core/gatekeeper.py
class BasicGatekeeper:
    def check_prob(self, prob, threshold=60.0):
        """Prob > 60%"""
        pass
    
    def decide_signal(self, prob, match_count, direction):
        """BUY/SELL/NO-TRADE"""
        pass
```

### **Phase 4: สร้าง Basic Backtest**
```python
# scripts/backtest_basic.py
def backtest_basic(symbol, exchange, n_bars=200):
    """Backtest แบบเรียบง่าย"""
    # 1. Fetch data
    # 2. Pattern matching
    # 3. Calculate stats
    # 4. Apply gatekeeper
    # 5. Save results
    pass
```

---

## ✅ ข้อดีของ "Back to Basic"

1. **เรียบง่าย**: เข้าใจง่าย, debug ง่าย, maintain ง่าย
2. **มั่นใจ**: ไม่มี logic ซับซ้อน → user มั่นใจมากขึ้น
3. **เร็ว**: ไม่ต้อง simulate trade → รันเร็วขึ้น
4. **ชัดเจน**: สถิติเพียวๆ → เห็นผลลัพธ์ชัดเจน
5. **ยืดหยุ่น**: สามารถเพิ่ม logic ทีหลังได้

---

## ⚠️ ข้อควรระวัง

1. **ไม่มี Risk Management**: ต้องจัดการเองตอนเทรดจริง
2. **N+1 เพียวๆ**: ไม่ได้ simulate multi-day hold
3. **สถิติอาจไม่ realistic**: ไม่มี slippage, commission, gap risk

**แต่:**
- ✅ ใช้สำหรับ **evaluation** และ **pattern discovery**
- ✅ Risk management จัดการตอนเทรดจริง
- ✅ เรียบง่าย → user มั่นใจมากขึ้น

---

## 🎯 Next Steps

1. **สร้าง Basic Pattern Matcher** (Phase 1)
2. **สร้าง Basic Predictor** (Phase 2)
3. **สร้าง Basic Gatekeeper** (Phase 3)
4. **สร้าง Basic Backtest** (Phase 4)
5. **ทดสอบและเปรียบเทียบ** กับระบบปัจจุบัน

---

## 🔗 Related Documents

- [PROMPT_ANALYSIS_ARCHITECTURE.md](PROMPT_ANALYSIS_ARCHITECTURE.md) - Architecture analysis
- [PATTERN_DETECTION_LOGIC.md](PATTERN_DETECTION_LOGIC.md) - Current pattern detection
- [RISK_MANAGEMENT_EXPLANATION.md](RISK_MANAGEMENT_EXPLANATION.md) - Current risk management

