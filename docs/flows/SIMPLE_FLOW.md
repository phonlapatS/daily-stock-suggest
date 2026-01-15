# Simple Flow Diagram

## 🌟 Workflow - จากบนลงล่าง

```mermaid
flowchart TD
    START([� USER INPUT<br/>python run.py PTT SET])
    
    START --> CACHE{💾 มี Cache?<br/>อายุ < 24 ชม.}
    
    CACHE -->|มี ✅| LOAD[📂 โหลด Cache<br/>0.1 วินาที ⚡]
    CACHE -->|ไม่มี ❌| FETCH[📡 ดึงจาก TradingView<br/>3 วินาที]
    
    FETCH --> SAVE[💾 บันทึก Cache]
    SAVE --> DATA
    LOAD --> DATA
    
    DATA[� ได้ข้อมูล 1,250 วัน<br/>date | open | high | low | close | % change]
    
    DATA --> FILTER[🔍 กรอง: เอาเฉพาะวันที่ ±1%<br/>1,250 วัน → 398 วัน]
    
    FILTER --> STATS[� วิเคราะห์สถิติ<br/><br/>หลังวันที่ +1%:<br/>• พรุ่งนี้ขึ้น: 33%<br/>• พรุ่งนี้ลง: 41%<br/>• พรุ่งนี้ sideways: 26%<br/><br/>หลังวันที่ -1%:<br/>• พรุ่งนี้ขึ้น: 39%<br/>• พรุ่งนี้ลง: 41%<br/>• พรุ่งนี้ sideways: 20%]
    
    STATS --> LATEST[👁️ ดูวันล่าสุด<br/>PTT: +2.36%<br/>2026-01-13]
    
    LATEST --> CHECK{เคลื่อนไหว ≥ ±1%?}
    
    CHECK -->|ไม่ ❌| WAIT1[⚠️ WAIT & SEE<br/>ไม่มีสัญญาณชัดเจน]
    
    CHECK -->|ใช่ ✅| SEARCH[🔎 ค้นหา Historical Patterns<br/><br/>เคยมีวันที่ขึ้น +2.36% (±0.5%)<br/>กี่ครั้งในอดีต?<br/><br/>→ พบ 57 ครั้ง]
    
    SEARCH --> ANALYZE[📊 วิเคราะห์ 57 patterns<br/><br/>วันถัดไปของ 57 ครั้งนั้น:<br/>• ขึ้น: 19 ครั้ง 33%<br/>• ลง: 26 ครั้ง 46% ← สูงสุด!<br/>• Sideways: 12 ครั้ง 21%]
    
    ANALYZE --> PREDICT[🎯 ทำนาย<br/><br/>Direction: DOWN<br/>Expected: -0.0% avg<br/>Confidence: 46%<br/>Risk if wrong: +3.2%]
    
    PREDICT --> ACTION[💡 คำนวณ Action<br/><br/>เงื่อนไข:<br/>• Confidence: 46% < 60% ❌<br/>• Patterns: 57 ≥ 50 ✅<br/>• Risk/Reward: 0.8 < 1.5 ❌<br/><br/>→ Action: WAIT & SEE]
    
    ACTION --> OUTPUT
    WAIT1 --> OUTPUT
    
    OUTPUT[📺 แสดงผล<br/><br/>🔮 PTT Prediction<br/>→ Tomorrow: DOWN-0.0% at 46%<br/>→ Risk if wrong: +3.2%<br/>→ Action: WAIT & SEE<br/>→ Based on 57 patterns]
    
    OUTPUT --> SAVE_JSON[💾 บันทึก JSON<br/>results/PTT_SET_report.json]
    
    SAVE_JSON --> END([✅ เสร็จสิ้น])
    
    style START fill:#e1f5e1,stroke:#28a745,stroke-width:3px
    style CACHE fill:#fff3cd,stroke:#ffc107,stroke-width:2px
    style FETCH fill:#cfe2ff,stroke:#007bff,stroke-width:2px
    style DATA fill:#e7f3ff,stroke:#007bff,stroke-width:2px
    style FILTER fill:#fff9e6,stroke:#ffc107,stroke-width:2px
    style STATS fill:#d1ecf1,stroke:#17a2b8,stroke-width:2px
    style SEARCH fill:#ffe6e6,stroke:#dc3545,stroke-width:2px
    style PREDICT fill:#ffd6d6,stroke:#dc3545,stroke-width:2px
    style ACTION fill:#d4edda,stroke:#28a745,stroke-width:2px
    style OUTPUT fill:#e7f3ff,stroke:#007bff,stroke-width:3px
    style END fill:#e1f5e1,stroke:#28a745,stroke-width:3px
```


---

## 🎯 Flow แบบง่ายที่สุด


```mermaid
graph TB
    Start([👤 User<br/>python run.py PTT SET])
    
    Start --> Data[📡 ดึงข้อมูล<br/>TradingView<br/>1,250 วัน 5 ปี]
    
    Data --> Filter[🔍 กรองข้อมูล<br/>เอาเฉพาะวันที่ ±1%<br/>ได้ 398 วัน]
    
    Filter --> Learn[📊 เรียนรู้<br/>ดูว่าหลัง ±1%<br/>วันถัดไปเป็นยังไง<br/><br/>ขึ้น: 33%<br/>ลง: 41%<br/>sideways: 26%]
    
    Learn --> Check[👁️ ดูวันล่าสุด<br/>PTT วันนี้: +2.36%]
    
    Check --> Predict{เคลื่อนไหว<br/>≥ ±1%?}
    
    Predict -->|ใช่ ✅| Search[🔎 ค้นหา Patterns<br/>เคยขึ้น +2.36% กี่ครั้ง?<br/><br/>พบ 57 ครั้ง]
    
    Search --> Result[🎯 ทำนาย<br/><br/>พรุ่งนี้: DOWN -0.0%<br/>Confidence: 46%<br/>Risk: +3.2%<br/><br/>Action: WAIT & SEE]
    
    Predict -->|ไม่ ❌| NoPredict[⚠️ WAIT & SEE<br/>ไม่มีสัญญาณ]
    
    Result --> Output[📺 แสดงผล<br/>+<br/>💾 บันทึก JSON]
    NoPredict --> Output
    
    Output --> End([✅ เสร็จสิ้น])
    
    style Start fill:#e1f5e1,stroke:#333,stroke-width:2px
    style Data fill:#cfe2ff
    style Filter fill:#fff3cd
    style Learn fill:#d1ecf1
    style Search fill:#ffe6e6
    style Result fill:#d4edda
    style Output fill:#e7f3ff
    style End fill:#e1f5e1,stroke:#333,stroke-width:2px
```

---

## 📊 Flow แบบ 3 Phase

```mermaid
graph LR
    A[🎯 INPUT<br/><br/>PTT<br/>SET] --> B[📊 PROCESS<br/><br/>ดึงข้อมูล<br/>กรอง ±1%<br/>วิเคราะห์<br/>ทำนาย]
    
    B --> C[📺 OUTPUT<br/><br/>Direction: DOWN<br/>Confidence: 46%<br/>Action: WAIT & SEE]
    
    style A fill:#e1f5e1,stroke:#333,stroke-width:3px,color:#000
    style B fill:#cfe2ff,stroke:#333,stroke-width:3px,color:#000
    style C fill:#d4edda,stroke:#333,stroke-width:3px,color:#000
```

---

## 🔄 Complete Flow (Vertical)

```mermaid
flowchart TD
    U[👤 User Input<br/>PTT, SET]
    
    U --> C{มี Cache?}
    C -->|มี| C1[ใช้ Cache<br/>0.1 วิ ⚡]
    C -->|ไม่มี| C2[ดึง API<br/>3 วิ]
    
    C1 --> D[📊 Data<br/>1,250 วัน]
    C2 --> D
    
    D --> F[กรอง ±1%<br/>398 วัน]
    
    F --> S[สถิติ<br/>หลัง +1% → พรุ่งนี้?<br/>ขึ้น 33% | ลง 41%]
    
    S --> L[วันล่าสุด<br/>+2.36%]
    
    L --> P{≥ ±1%?}
    
    P -->|Yes| M[Match<br/>57 patterns]
    P -->|No| W1[WAIT & SEE]
    
    M --> R[Predict<br/>DOWN 46%]
    
    R --> A[Action<br/>WAIT & SEE]
    
    A --> O[📺 Output]
    W1 --> O
    
    O --> E[✅ Done]
    
    style U fill:#e1f5e1
    style D fill:#cfe2ff
    style F fill:#fff3cd
    style S fill:#d1ecf1
    style M fill:#ffe6e6
    style R fill:#ffd6d6
    style A fill:#d4edda
    style O fill:#e7f3ff
    style E fill:#e1f5e1
```

---

## 🎨 แบบมี Icon (Horizontal)

```mermaid
graph LR
    A["🎯<br/>INPUT"] --> B["📡<br/>FETCH"]
    B --> C["🔍<br/>FILTER"]
    C --> D["📊<br/>LEARN"]
    D --> E["🔮<br/>PREDICT"]
    E --> F["💡<br/>ACTION"]
    F --> G["📺<br/>OUTPUT"]
    
    style A fill:#e1f5e1,stroke:#28a745,stroke-width:3px
    style B fill:#cce5ff,stroke:#007bff,stroke-width:2px
    style C fill:#fff3cd,stroke:#ffc107,stroke-width:2px
    style D fill:#d1ecf1,stroke:#17a2b8,stroke-width:2px
    style E fill:#ffe6e6,stroke:#dc3545,stroke-width:2px
    style F fill:#d4edda,stroke:#28a745,stroke-width:2px
    style G fill:#e7f3ff,stroke:#007bff,stroke-width:3px
```

---

## สรุป Flow 1 บรรทัด

```
INPUT → FETCH DATA → FILTER ±1% → LEARN STATS → PREDICT TOMORROW → ACTION → OUTPUT
```

**เลือกแบบไหนก็ได้ครับ! ง่ายและชัดเจน 📊**
