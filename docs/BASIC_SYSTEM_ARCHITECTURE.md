# 🏗️ Basic System Architecture: แยก Logic

**วันที่:** 2026-02-13  
**ระบบ:** Back to Basic - สถิติเพียวๆ

---

## ✅ ใช่! แยก Logic แล้ว

Basic System แยก logic ตามที่ prompt ต้องการแล้ว:

---

## 📁 โครงสร้าง Modules

### **1. Core Pipeline** (`scripts/backtest_basic.py`)
**หน้าที่:**
- ✅ รันงานประจำวัน
- ✅ เตรียมข้อมูล (fetch data, split train/test)
- ✅ เรียกโมดูลย่อย (Pattern Matcher, Gatekeeper)
- ✅ ส่งออกผล (CSV output)

**Code:**
```python
def backtest_basic_single(...):
    # 1. Fetch data
    df = get_data_with_cache(...)
    
    # 2. Split train/test
    df_train = df.iloc[:train_end]
    df_test = df.iloc[train_end:]
    
    # 3. เรียก Pattern Matcher
    matcher = BasicPatternMatcher()
    best_pattern_info = matcher.get_best_pattern(...)
    
    # 4. เรียก Gatekeeper
    gatekeeper = BasicGatekeeper()
    signal = gatekeeper.decide_signal(...)
    
    # 5. Save results
    return result
```

---

### **2. Pattern & Signal Logic** (`core/pattern_matcher_basic.py`)
**หน้าที่:**
- ✅ สร้าง pattern signature (extract_pattern)
- ✅ Match history (find_pattern_matches)
- ✅ คำนวณสถิติ (calculate_stats: prob, avgWin, avgLoss, RRR, match_count)
- ✅ หา best pattern (get_best_pattern)

**Code:**
```python
class BasicPatternMatcher:
    def extract_pattern(self, pct_change, threshold):
        """แปลง pct_change เป็น pattern string (+/-)"""
        pass
    
    def find_pattern_matches(self, df, pattern_str, ...):
        """หา pattern ในประวัติ"""
        pass
    
    def calculate_stats(self, df, matches, direction):
        """คำนวณสถิติเพียวๆ"""
        # Prob%, AvgWin%, AvgLoss%, RRR, match_count
        pass
    
    def get_best_pattern(self, df, ...):
        """หา pattern ที่ดีที่สุด"""
        pass
```

---

### **3. Gatekeeper Logic** (`core/gatekeeper_basic.py`)
**หน้าที่:**
- ✅ ตรวจสอบ Prob > 60% (check_prob)
- ✅ ตรวจสอบ match_count >= Nmin (check_match_count)
- ✅ ตัดสินใจสัญญาณ (decide_signal: BUY/SELL/NO-TRADE)

**Code:**
```python
class BasicGatekeeper:
    def check_prob(self, prob):
        """Prob > 60%"""
        pass
    
    def check_match_count(self, match_count):
        """match_count >= 30"""
        pass
    
    def decide_signal(self, prob, match_count, direction, rrr):
        """BUY/SELL/NO-TRADE"""
        pass
```

---

## 🔄 Flow การทำงาน

```
┌─────────────────────────────────────┐
│   Core Pipeline                      │
│   (backtest_basic.py)                │
│                                      │
│   1. Fetch Data                      │
│   2. Split Train/Test                │
│   3. ────────────────────┐          │
│   4. ────────────────────┼───┐      │
│   5. Save Results         │   │      │
└───────────────────────────┼───┼──────┘
                            │   │
                            ▼   ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ Pattern Matcher  │   │ Gatekeeper       │
        │                  │   │                  │
        │ - extract_pattern│   │ - check_prob     │
        │ - find_matches   │   │ - check_count    │
        │ - calculate_stats│   │ - decide_signal  │
        │ - get_best_pattern│   │                  │
        └──────────────────┘   └──────────────────┘
```

---

## ✅ เปรียบเทียบ: Current vs Basic

| Aspect | Current System | Basic System |
|--------|----------------|--------------|
| **Module Separation** | ❌ Logic ปนกัน (700+ lines) | ✅ แยกชัดเจน (3 modules) |
| **Pattern Logic** | ❌ ปนกับ Core | ✅ แยกเป็น module |
| **Gatekeeper Logic** | ❌ ปนกับ Core | ✅ แยกเป็น module |
| **Core Pipeline** | ❌ ซับซ้อน (RM, Trade Sim) | ✅ เรียบง่าย (เรียก modules) |
| **Maintainability** | 🔴 ยาก | 🟢 ง่าย |
| **Testability** | 🔴 ยาก | 🟢 ง่าย |

---

## 📊 Module Responsibilities

### **Core Pipeline** (`backtest_basic.py`)
- ✅ Data fetching
- ✅ Train/test split
- ✅ Orchestration (เรียก modules)
- ✅ CSV output

### **Pattern Matcher** (`pattern_matcher_basic.py`)
- ✅ Pattern extraction
- ✅ Pattern matching
- ✅ Statistics calculation
- ✅ Best pattern selection

### **Gatekeeper** (`gatekeeper_basic.py`)
- ✅ Prob% validation
- ✅ Match count validation
- ✅ Signal decision (BUY/SELL/NO-TRADE)

---

## 🎯 สรุป

### **✅ แยก Logic แล้ว:**
1. **Core Pipeline** → `scripts/backtest_basic.py`
2. **Pattern & Signal Logic** → `core/pattern_matcher_basic.py`
3. **Gatekeeper Logic** → `core/gatekeeper_basic.py`

### **✅ ข้อดี:**
- Logic แยกชัดเจน
- แต่ละ module ทำหน้าที่ชัดเจน
- แก้ไขได้ทีละส่วน
- ทดสอบได้ทีละส่วน
- เข้าใจง่าย

### **✅ ตาม Prompt:**
- ✅ Module Separation
- ✅ Core Pipeline แยกจาก Pattern Logic
- ✅ Gatekeeper แยกเป็น module
- ✅ เรียบง่าย เข้าใจง่าย

---

## 🔗 Related Documents

- [BACK_TO_BASIC_ANALYSIS.md](BACK_TO_BASIC_ANALYSIS.md) - แนวทาง Back to Basic
- [PROMPT_ANALYSIS_ARCHITECTURE.md](PROMPT_ANALYSIS_ARCHITECTURE.md) - วิเคราะห์ Prompt

