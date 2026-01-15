# System Flow - ระบบทำนายหุ้น

## 🔄 Flow การทำงานทั้งระบบ

```mermaid
flowchart TD
    Start([User รัน python run.py PTT SET]) --> Input[1. รับ Input: Symbol + Exchange]
    
    Input --> Cache{2. ตรวจสอบ Cache}
    Cache -->|มี Cache & ยังไม่หมดอายุ| UseCache[ใช้ข้อมูลจาก Cache]
    Cache -->|ไม่มี / หมดอายุ| FetchData[ดึงข้อมูลจาก TradingView]
    
    FetchData --> SaveCache[บันทึก Cache]
    SaveCache --> DataReady[3. ข้อมูลพร้อม]
    UseCache --> DataReady
    
    DataReady --> Filter[4. กรองวันที่ ±1%]
    
    Filter --> Analyze[5. วิเคราะห์สถิติ]
    
    Analyze --> CheckLatest{6. วันล่าสุด\nเคลื่อนไหว ±1%?}
    
    CheckLatest -->|ใช่| Predict[7. ทำนาย\nHistorical Pattern Matching]
    CheckLatest -->|ไม่| NoPredict[แสดง: WAIT & SEE]
    
    Predict --> CalcAction[8. คำนวณ Action\nConfidence + Risk/Reward]
    
    CalcAction --> ShowResult[9. แสดงผลลัพธ์]
    NoPredict --> ShowResult
    
    ShowResult --> SaveJSON[10. บันทึก JSON]
    
    SaveJSON --> End([จบ])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Predict fill:#fff3cd
    style CalcAction fill:#fff3cd
    style ShowResult fill:#cfe2ff
```

---

## 📊 Flow แบบละเอียด

### Phase 1: Data Acquisition
```
User Input (PTT, SET)
    ↓
ตรวจสอบ Cache
    ├─ มี Cache (< 24 ชม.) → ใช้ทันที (0.1 วินาที) ⚡
    └─ ไม่มี/หมดอายุ → ดึงจาก TradingView (3 วินาที)
    ↓
ได้ DataFrame: 1,250 วัน × [date, open, high, low, close, volume, % change]
```

### Phase 2: Statistics Analysis
```
ข้อมูล 1,250 วัน
    ↓
กรองเฉพาะวันที่ ±1%
    ↓
ได้ ~400 วัน (significant days)
    ↓
วิเคราะห์วันถัดไป:
    ├─ หลังวันขึ้น +1% → พรุ่งนี้เป็นอย่างไร?
    │   ├─ ขึ้น: 33%
    │   ├─ ลง: 41%
    │   └─ Sideways: 26%
    │
    └─ หลังวันลง -1% → พรุ่งนี้เป็นอย่างไร?
        ├─ ขึ้น: 39%
        ├─ ลง: 41%
        └─ Sideways: 20%
```

### Phase 3: Prediction (ถ้าวันนี้ ±1%)
```
วันนี้: PTT +2.36% ✅
    ↓
ค้นหา Historical Patterns:
    "เคยมีวันที่ขึ้น +2.36% (±0.5%) กี่ครั้ง?"
    ↓
พบ 57 patterns คล้ายกัน
    ↓
ดูวันถัดไปของ 57 ครั้งนั้น:
    ├─ ขึ้น: 19 ครั้ง (33%)
    ├─ ลง: 26 ครั้ง (46%) ← มากที่สุด!
    └─ Sideways: 12 ครั้ง (21%)
    ↓
คำนวณ:
    ├─ Direction: DOWN (ตาม probability สูงสุด)
    ├─ Expected: -0.02% (ค่าเฉลี่ย)
    ├─ Confidence: 46% (จาก probability)
    └─ Risk: +3.2% (worst case จาก 57 patterns)
```

### Phase 4: Action Recommendation
```
Confidence: 46%
Patterns: 57
Risk/Reward: 0.8
    ↓
ตรวจสอบเงื่อนไข:
    ├─ Confidence ≥ 60% + Patterns ≥ 50? → ❌
    ├─ Confidence ≥ 50% + Patterns ≥ 30? → ❌
    └─ อื่นๆ → ✅
    ↓
Action: WAIT & SEE (low confidence)
```

---

## 🎯 Output Flow

```
📊 CONSOLE OUTPUT
├─ สถิติโดยรวม (1,249 วัน)
├─ ความน่าจะเป็น (หลัง ±1%)
├─ 🔮 Prediction
│   ├─ Tomorrow: DOWN (-0.0%) at 46% confidence
│   ├─ Risk if wrong: +3.2%
│   ├─ Action: WAIT & SEE
│   └─ Based on 57 patterns
└─ สถิติเพิ่มเติม

💾 JSON FILE (results/PTT_SET_report.json)
├─ total_days: 1249
├─ significant_days: 395
├─ probabilities: {...}
├─ next_day_stats: {...}
└─ risk_metrics: {...}
```

---

## 🔍 Decision Logic Flow

```mermaid
flowchart TD
    Input[วันล่าสุด: +2.36%]
    
    Input --> Check1{เคลื่อนไหว\n≥ ±1%?}
    
    Check1 -->|ไม่| NoSignal[WAIT & SEE\nno clear signal]
    Check1 -->|ใช่| FindPatterns[ค้นหา\nHistorical Patterns]
    
    FindPatterns --> Patterns[พบ 57 patterns]
    
    Patterns --> Predict[ทำนายจาก\n57 patterns]
    
    Predict --> Check2{Confidence ≥ 60%\n& Patterns ≥ 50?}
    
    Check2 -->|ใช่| CheckRR{Risk/Reward\n≥ 1.5?}
    Check2 -->|ไม่| Check3{Confidence ≥ 50%\n& Patterns ≥ 30?}
    
    CheckRR -->|ใช่| ActionBuy[CONSIDER BUY/SELL\ngood risk/reward]
    CheckRR -->|ไม่| CheckRR2{Risk/Reward\n≥ 1.0?}
    
    CheckRR2 -->|ใช่| ActionAccept[CONSIDER BUY/SELL\nacceptable risk/reward]
    CheckRR2 -->|ไม่| ActionPoor[WAIT & SEE\npoor risk/reward]
    
    Check3 -->|ใช่| ActionMod[WAIT & SEE\nmoderate confidence]
    Check3 -->|ไม่| ActionLow[WAIT & SEE\nlow confidence]
    
    style ActionBuy fill:#d4edda
    style ActionAccept fill:#fff3cd
    style ActionPoor fill:#f8d7da
    style ActionMod fill:#f8d7da
    style ActionLow fill:#f8d7da
    style NoSignal fill:#f8d7da
```

---

## 💡 Key Concepts

### 1. Historical Pattern Matching
```
วันนี้ PTT +2.36%
    ↓
ค้นหาในอดีต: "เคยมีวันที่ขึ้น +1.86% ถึง +2.86% กี่ครั้ง?"
    ↓
พบ 57 ครั้ง
    ↓
ดูวันถัดไป → สรุปเป็นสถิติ
```

### 2. Confidence Calculation
```
Confidence = (จำนวนที่ทายถูก / จำนวนทั้งหมด) × 100

ตัวอย่าง:
- ทาย DOWN
- จาก 57 patterns → 26 ครั้งที่ลงจริง
- Confidence = 26/57 × 100 = 46%
```

### 3. Risk Assessment
```
จาก 57 patterns:
- Best case: ลงมากที่สุด -2.56%
- Worst case: ขึ้นมากที่สุด +3.21%
- Average: -0.02%
```

---

## 🚀 Daily Suggest Flow

```mermaid
flowchart LR
    A[8:00 AM\nCron รันอัตโนมัติ] --> B[Scan หุ้นทั้งหมด\n700 ตัว]
    
    B --> C{ใช้ Cache?}
    C -->|ใช่| D[เร็ว: 5-10 นาที]
    C -->|ไม่| E[ช้า: 30-40 นาที]
    
    D --> F[กรองเฉพาะที่\nเคลื่อนไหว ±1%]
    E --> F
    
    F --> G[วิเคราะห์ + ทำนาย]
    
    G --> H{มี signal ดี?}
    
    H -->|ใช่| I[ส่ง Notification\nTelegram/Line]
    H -->|ไม่| J[ไม่ส่ง]
    
    I --> K[จบ]
    J --> K
    
    style A fill:#e1f5e1
    style I fill:#cfe2ff
```

---

**สรุป:** ระบบใช้ Pure Historical Pattern Matching ไม่มี ML model - ทุกอย่างมาจากข้อมูลจริง 100% 📊
