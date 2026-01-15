# Pattern Detection V2 + Master Scanner - Unified Logic

## 🎯 Overview

Master Scanner ใช้ **V2 Logic** แบบเต็มรูปแบบ:
- Percentile threshold (แทน SD)
- Mixed streak (ไม่สนทิศทาง)
- Timeframe-aware (1D vs intraday)

---

## 🔬 V2 Logic Differences

### **V1 vs V2 Comparison:**

| Feature | V1 (Directional) | V2 (Mixed) |
|---------|------------------|------------|
| Threshold | SD × 1.5 (90 days) | 90th Percentile (126 days) |
| Streak Type | Same direction only | Any significant move |
| Pattern | +++, --- | +-+, -+-, +++, --- |
| Use Case | Trend prediction | Volatility analysis |

---

## 📊 Step-by-Step V2 Logic

### **Step 1: Percentile Threshold**

**Algorithm:**
```python
def calculate_dynamic_threshold(df, lookback, floor):
    """
    V2: ใช้ 90th percentile แทน SD
    """
    periods = min(len(df), lookback)
    
    # Calculate 90th percentile of ABSOLUTE changes
    threshold = df['pct_change'].abs().tail(periods).quantile(0.90)
    
    # Apply floor (1.0% for daily, 0.2% for intraday)
    return max(threshold, floor)
```

**Example (PTT, Daily):**
```python
# Last 126 days absolute changes:
[0.5%, 1.2%, 0.8%, 2.1%, ..., 3.5%]

# Sort and find 90th percentile:
sorted: [0.1%, 0.2%, ..., 2.5%, 3.0%, 3.5%]
                              ↑
                         90th percentile

# Result
threshold = 2.5%
threshold = max(2.5%, 1.0%) = 2.5%

# Meaning: Top 10% ของการเปลี่ยนแปลง = "significant"
```

**Example (Gold, 15M):**
```python
# Intraday มีการเคลื่อนไหวน้อยกว่า
# Last 3000 bars (15M):
threshold = 0.35%
threshold = max(0.35%, 0.2%) = 0.35%

# Floor ต่ำกว่า (0.2% vs 1.0%)
```

---

### **Step 2: Volatility Classification**

**Purpose:** จำแนกระดับความผันผวน

**Algorithm:**
```python
def calculate_volatility(df):
    """
    Annual volatility = Daily SD × √252
    """
    annual_vol = df['pct_change'].std() * np.sqrt(252)
    return annual_vol

def classify_volatility(vol):
    """
    แบ่งเป็น 3 ระดับ
    """
    if vol < 20:
        return 'Low'    # หุ้นเสถียร
    elif vol <= 60:
        return 'Med'    # หุ้นปกติ
    else:
        return 'High'   # หุ้นผันผวนสูง
```

**Example (PTT):**
```python
# Daily pct_change std = 1.69%
annual_vol = 1.69 × √252 = 1.69 × 15.87 = 26.8%

# Classification
26.8% → 'Med' (20-60%)
```

**Example (THAI):**
```python
# High volatility stock
annual_vol = 80%
classification = 'High' (> 60%)
```

---

### **Step 3: Mixed Streak Detection**

**Key Difference:** ไม่สนทิศทาง นับทุกการเคลื่อนไหวที่เกิน threshold

**Algorithm:**
```python
def detect_volatility_streak(df, threshold):
    """
    V2: Mixed streak (direction-agnostic)
    """
    streak = 0
    
    # เดินย้อนจากวันล่าสุด
    for i in range(len(df) - 1, -1, -1):
        change = df.iloc[i]['pct_change']
        
        # เช็คแค่ว่าเกิน threshold ไหม (ไม่สนทิศทาง)
        if abs(change) > threshold:
            streak += 1
        else:
            break  # ไม่เกิน → หยุด
    
    return streak
```

**Example (V1 vs V2):**

**V1 (Directional):**
```
Date    Change   vs Threshold  Direction  V1 Streak
Day 1   +3.0%    > 2.5%        UP         1
Day 2   +2.6%    > 2.5%        UP         2
Day 3   -2.7%    > 2.5%        DOWN       BREAK! (Direction changed)

V1 Result: Streak = 2 (Up 2 Days)
```

**V2 (Mixed):**
```
Date    Change   vs Threshold  |Change|   V2 Streak
Day 1   +3.0%    > 2.5%        3.0%       1
Day 2   +2.6%    > 2.5%        2.6%       2
Day 3   -2.7%    > 2.5%        2.7%       3 (ยังนับต่อ!)

V2 Result: Streak = 3 (Volatility 3)
```

**Key Point:** V2 นับ **ความผันผวน** ไม่ใช่ **ทิศทาง**

---

### **Step 4: Calculate All Streaks (V2)**

**Algorithm:**
```python
def calculate_all_streaks_v2(df, threshold):
    """
    คำนวณ mixed streak สำหรับทุกวัน
    """
    df['streak'] = 0
    
    for i in range(len(df)):
        streak = 0
        
        # เดินย้อนจากวันที่ i
        for j in range(i, -1, -1):
            change = df.iloc[j]['pct_change']
            
            # V2: เช็คแค่ abs(change) > threshold
            if abs(change) > threshold:
                streak += 1
            else:
                break
        
        df.iloc[i, df.columns.get_loc('streak')] = streak
    
    return df
```

**Example Output:**
```
Date    Change   |Change|  Threshold  Streak  Status
Jan 1   +2.0%    2.0%     2.5%        0       Quiet
Jan 2   +3.0%    3.0%     2.5%        1       🟢 Up Vol 1
Jan 3   -2.7%    2.7%     2.5%        2       🔴 Down Vol 2
Jan 4   +2.6%    2.6%     2.5%        3       🟢 Up Vol 3
Jan 5   +1.0%    1.0%     2.5%        0       Quiet (break)
```

---

### **Step 5: Find Matches (V2)**

**Same as V1 but matches are different patterns:**

```python
def find_matches_v2(df, current_streak, threshold):
    """
    หาวันที่มี streak เดียวกัน (ไม่สนทิศทาง)
    """
    # Calculate streaks for all days
    df = calculate_all_streaks_v2(df, threshold)
    
    # Add next day return
    df['next_return'] = df['pct_change'].shift(-1)
    
    # Find matches (exclude last day)
    history = df.iloc[:-1]
    matches = history[history['streak'] == current_streak]
    matches = matches.dropna(subset=['next_return'])
    
    return matches
```

**Example:**
```
Current: Streak = 3 (Volatility 3)

Matches found:
Date       Streak  Last 3 Days Pattern    Next Day
2020-05    3       +2.6%, -2.7%, +3.0%    +0.5%
2020-08    3       -2.5%, +2.8%, -2.6%    -0.3%
2021-02    3       +3.1%, +2.9%, -2.7%    +0.8%
2021-06    3       -2.6%, -2.7%, +2.8%    +0.2%

Total: 150 matches (less than V1's 272)
→ หลากหลายมากกว่า (มีทั้ง +++, ---, +-+, -+-)
```

---

### **Step 6: Calculate Probability (V2)**

**Same calculation as V1:**

```python
# Statistics
events = 150
wins = 73 (next_return > 0)
losses = 77 (next_return < 0)

win_rate = 73 / 150 = 48.7%
avg_return = sum(all returns) / 150 = +0.05%
max_risk = min(all returns) = -8.2%
```

---

## 🌐 Master Scanner Integration

### **Timeframe-Aware Logic:**

```python
def analyze_asset(filepath, symbol, exchange, timeframe):
    """
    Master Scanner: รองรับหลาย timeframe
    """
    df = pd.read_parquet(filepath)
    
    # 1. Determine parameters by timeframe
    if timeframe in ['1D', 'D1', 'DAILY']:
        lookback = 126
        floor = 1.0      # Daily: 1%
    else:  # Intraday (15M, 30M)
        lookback = 3000
        floor = 0.2      # Intraday: 0.2%
    
    # 2. Calculate V2 threshold
    threshold = calculate_dynamic_threshold(df, lookback, floor)
    
    # 3. Calculate volatility
    vol = calculate_volatility(df)
    vol_class = classify_volatility(vol)
    
    # 4. Detect V2 streak
    streak = detect_volatility_streak(df, threshold)
    
    # 5. Status (based on today's direction)
    latest_change = df.iloc[-1]['pct_change']
    if streak > 0:
        if latest_change > 0:
            status = f"🟢 Up Vol {streak}"
        else:
            status = f"🔴 Down Vol {streak}"
    else:
        status = "⚪ Quiet"
    
    # 6. Historical probability
    prob = calculate_historical_probability_v2(df, streak, threshold)
    
    return {
        'Symbol': symbol,
        'Threshold': threshold,
        'Vol_Class': vol_class,
        'Streak': streak,
        'Status': status,
        'WinRate': prob['win_rate'],
        'AvgRet': prob['avg_return'],
        'MaxRisk': prob['max_risk'],
        'Events': prob['events']
    }
```

---

## 📊 Real Example (PTT with V2)

### **Calculation:**

```python
# 1. Threshold (Percentile)
last_126 = df['pct_change'].abs().tail(126)
threshold = last_126.quantile(0.90)
threshold = max(2.35%, 1.0%) = 2.35%

# 2. Volatility
annual_vol = 1.69 × √252 = 26.8% → 'Med'

# 3. Last 5 days
Date    Change   |Change|  Streak
Jan 11  +1.61%   1.61%    0       (< 2.35%)
Jan 12  +1.58%   1.58%    0
Jan 13  -0.78%   0.78%    0
Jan 14  +3.15%   3.15%    1       (> 2.35%) ✅
Jan 15  +0.00%   0.00%    0       (break)

Current: Streak was 1 หลัง Jan 14

# 4. Find matches: "Volatility 1"
Found: 180 events

# 5. Statistics
WinRate: 48.5%
AvgRet: +0.08%
MaxRisk: -10.2%
Events: 180
```

---

## 🎯 V2 Advantages & Disadvantages

### **Advantages:**
✅ **Robust to outliers** - Percentile ไม่ไวต่อค่าผิดปกติ  
✅ **Captures volatility** - เห็นความผันผวนทุกทิศทาง  
✅ **More events** - Pattern หลากหลาย (+++, ---, +-+)  
✅ **Timeframe-agnostic** - ใช้ได้กับทุก timeframe

### **Disadvantages:**
⚠️ **Less directional** - ไม่ดีสำหรับ trend prediction  
⚠️ **Mixed patterns** - +-+ ไม่มีความหมายชัดเจน  
⚠️ **Lower WinRate** - มักได้ ~48-52% (random)

---

## ✅ Summary

### **V2 + Master Scanner Logic:**

1. **Percentile Threshold** (90th, 126 days)
   - Daily: min 1.0%
   - Intraday: min 0.2%

2. **Volatility Classification**
   - Annual SD × √252
   - Low / Med / High

3. **Mixed Streak Detection**
   - abs(change) > threshold
   - Direction-agnostic

4. **Historical Probability**
   - Same calculation as V1
   - Different pattern matching

5. **Timeframe-Aware**
   - Auto-adjust parameters
   - Separate dashboards

### **Best Use:**
- ✅ Volatility analysis
- ✅ Risk assessment
- ✅ Multi-timeframe scanning
- ❌ NOT for trend prediction

**V2 เหมาะกับการดู "ความผันผวน" ไม่ใช่ "ทิศทาง"!** 🌊📊
