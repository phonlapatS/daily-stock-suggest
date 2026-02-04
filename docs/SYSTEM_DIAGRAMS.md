# ⚠️ DEPRECATED DOCUMENT
> **NOTE:** This document shows V1/V2 architecture. For the new V3.4 System Diagrams, please refer to section "System Architecture" in **[PROJECT_MASTER_MANUAL.md](PROJECT_MASTER_MANUAL.md)**.

# System Architecture - Mermaid Diagrams & Logic Explanation

## 🏗️ Complete System Architecture

```mermaid
graph TB
    subgraph "📥 DATA LAYER"
        TV[TradingView API<br/>tvDatafeed]
        SX[starfishX<br/>Stock List]
        
        TV -->|OHLCV| DU[data_updater.py<br/>Incremental Download]
        SX -->|Stock Names| DU
        
        DU -->|Save| PQ[(Parquet Storage<br/>data/stocks/<br/>71 files, 4MB)]
    end
    
    subgraph "🔬 ANALYSIS LAYER"
        PQ -->|Load| S1[scanner.py<br/>V1 Directional]
        PQ -->|Load| S2[scanner_v2.py<br/>V2 Mixed]
        PQ -->|Load| SM[master_scanner.py<br/>Universal Multi-Asset]
        
        S1 --> L1[Logic V1:<br/>SD × 1.5<br/>Same Direction Streak<br/>Historical Match]
        S2 --> L2[Logic V2:<br/>90th Percentile<br/>Volatility Streak<br/>Direction-agnostic]
        SM --> L3[Logic Universal:<br/>Timeframe-aware<br/>Dynamic Floor<br/>Multi-Asset]
        
        L1 --> HP1[Calculate:<br/>WinRate, AvgRet<br/>MaxRisk, Events]
        L2 --> HP2[Calculate:<br/>WinRate, AvgRet<br/>Vol Classification]
        L3 --> HP3[Calculate:<br/>Per-Timeframe Stats<br/>Separate Dashboards]
    end
    
    subgraph "📊 OUTPUT LAYER"
        HP1 -->|Export| CSV1[market_scanner.csv]
        HP2 -->|Export| CSV2[market_scanner_v2.csv]
        HP3 -->|Export| CSV3[master_results/]
        
        CSV1 -->|Archive| H1[scanner_history/<br/>Timestamped]
        CSV2 -->|Archive| H2[scanner_v2_history/<br/>Timestamped]
        
        CSV1 -->|Display| VIEW[view_scanner.py<br/>Filter & View]
    end
    
    subgraph "👤 USER INTERFACE"
        VIEW -->|Show| D1[Dashboard:<br/>All Stocks]
        VIEW -->|Show| D2[Dashboard:<br/>Active Streaks Only]
        VIEW -->|Show| D3[Dashboard:<br/>Top Movers]
        VIEW -->|Show| D4[Compare:<br/>Historical]
    end
    
    style TV fill:#e3f2fd
    style PQ fill:#fff3e0
    style S1 fill:#e8f5e9
    style S2 fill:#f3e5f5
    style SM fill:#fce4ec
    style CSV1 fill:#e0f2f1
    style VIEW fill:#fff9c4
```

---

## 🔄 Data Flow Sequence (Daily Workflow)

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant DU as data_updater.py
    participant TV as TradingView API
    participant FS as File System
    participant SC as scanner.py
    participant AN as Analysis Engine
    participant OU as Output/Display
    
    rect rgb(230, 240, 255)
        Note over U,OU: 17:00 - Market Close
    end
    
    rect rgb(255, 245, 230)
        Note over U,FS: STEP 1: UPDATE DATA
        U->>DU: python data_updater.py --skip
        DU->>FS: Check existing files
        FS-->>DU: Found 71 files
        DU->>TV: Fetch missing stocks
        TV-->>DU: OHLCV data (if any)
        DU->>FS: Save/Update parquet
        FS-->>U: ✅ Data updated
    end
    
    rect rgb(232, 245, 233)
        Note over U,OU: STEP 2: RUN ANALYSIS
        U->>SC: python scanner.py
        SC->>FS: Load all parquet files
        FS-->>SC: 71 stocks data
        
        SC->>AN: Calculate Threshold (SD×1.5)
        AN-->>SC: Threshold per stock
        
        SC->>AN: Detect Streaks (Directional)
        AN-->>SC: Streak counts
        
        SC->>AN: Calculate Historical Probability
        Note right of AN: For each streak:<br/>1. Find matches<br/>2. Check next day<br/>3. Calc WinRate
        AN-->>SC: {WinRate, AvgRet, MaxRisk, Events}
        
        SC->>OU: Generate Dashboard
        SC->>FS: Save CSV + Archive
        OU-->>U: 📊 Display Results
    end
    
    rect rgb(243, 229, 245)
        Note over U,OU: STEP 3: FILTER SIGNALS
        U->>OU: python view_scanner.py streaks
        OU->>FS: Read market_scanner.csv
        FS-->>OU: All data
        OU->>OU: Filter: Streak > 0
        OU-->>U: 🔥 Active signals only
    end
    
    rect rgb(255, 249, 196)
        Note over U,OU: STEP 4: DECISION
        U->>U: Review:<br/>WinRate > 55%?<br/>Events > 50?<br/>MaxRisk acceptable?
        alt Signal Good
            U->>U: Plan Trade for Tomorrow
        else Signal Bad
            U->>U: Wait for better signal
        end
    end
```

---

## 🧮 Calculation Logic Flow

```mermaid
flowchart TD
    START([📁 Load Stock Data]) --> PREP[Preprocessing]
    
    PREP --> DEDUP[Remove Duplicates<br/>Drop NaN]
    DEDUP --> CALC_PCT[Calculate pct_change<br/>pct = close.pct_change × 100]
    
    CALC_PCT --> CHOOSE{Choose Scanner}
    
    CHOOSE -->|V1| V1_THRESH[Calculate Threshold V1<br/>std = pct_change.tail90.std<br/>threshold = std × 1.5<br/>clamp 0.5% - 5.0%]
    CHOOSE -->|V2| V2_THRESH[Calculate Threshold V2<br/>threshold = pct_change.abs<br/>.tail126.quantile0.90<br/>min = 1.0%]
    
    V1_THRESH --> V1_STREAK[Detect Directional Streak<br/>Walk backward from latest:<br/>Count same direction days<br/>where abs > threshold]
    V2_THRESH --> V2_VOL[Calculate Volatility<br/>annual_vol = std × √252]
    
    V2_VOL --> V2_CLASS{Classify}
    V2_CLASS -->|vol < 20| VOL_LOW[Low Vol]
    V2_CLASS -->|20 ≤ vol ≤ 60| VOL_MED[Med Vol]
    V2_CLASS -->|vol > 60| VOL_HIGH[High Vol]
    
    VOL_LOW --> V2_STREAK
    VOL_MED --> V2_STREAK
    VOL_HIGH --> V2_STREAK
    
    V2_STREAK[Detect Volatility Streak<br/>Walk backward:<br/>Count all days<br/>where abs > threshold<br/>direction-agnostic]
    
    V1_STREAK --> HIST_PROB[Calculate Historical Probability]
    V2_STREAK --> HIST_PROB
    
    HIST_PROB --> STEP1[STEP 1: Build History<br/>For each day in past:<br/>Calculate its streak value]
    
    STEP1 --> STEP2[STEP 2: Add Next Day<br/>next_day = pct_change.shift-1]
    
    STEP2 --> STEP3[STEP 3: Find Matches<br/>events = history where<br/>streak == current_streak]
    
    STEP3 --> STEP4[STEP 4: Calculate Stats<br/>wins = count next_day > 0<br/>WinRate = wins / events × 100<br/>AvgRet = mean next_day<br/>MaxRisk = min next_day]
    
    STEP4 --> OUTPUT[Generate Output<br/>Symbol, Price, Change<br/>Streak, WinRate, AvgRet<br/>MaxRisk, Events]
    
    OUTPUT --> FILTER{Active<br/>Streak?}
    FILTER -->|Yes| DISPLAY[📊 Display in Dashboard]
    FILTER -->|No| SKIP[⚪ Mark as Quiet]
    
    DISPLAY --> SAVE[💾 Save CSV + Archive]
    SKIP --> SAVE
    
    SAVE --> END([✅ Complete])
    
    style START fill:#e3f2fd
    style HIST_PROB fill:#fff3e0
    style DISPLAY fill:#e8f5e9
    style SAVE fill:#e0f2f1
    style END fill:#c8e6c9
```

---

## 📊 Historical Probability Calculation

```mermaid
flowchart LR
    subgraph "Input"
        I1[Current State:<br/>PTT<br/>Streak = Up 3 Days<br/>Threshold = 1.61%]
    end
    
    subgraph "Process"
        P1[Scan All History<br/>3000 days] --> P2[For each day:<br/>Calculate streak]
        
        P2 --> P3{Streak == 3?}
        P3 -->|Yes| P4[Mark as Event<br/>Record next day return]
        P3 -->|No| P5[Skip]
        
        P4 --> P6[Accumulate Events]
        P5 --> P2
    end
    
    subgraph "Events Found"
        E1[Event #1: Day 50<br/>Up 3 → Next: +0.5%]
        E2[Event #2: Day 100<br/>Up 3 → Next: -0.3%]
        E3[Event #3: Day 150<br/>Up 3 → Next: +0.8%]
        E4[...]
        E5[Event #272: Day 2990<br/>Up 3 → Next: -0.1%]
    end
    
    subgraph "Statistics"
        S1[Total Events: 272]
        S2[Wins: 117 times<br/>next_day > 0]
        S3[Losses: 155 times<br/>next_day < 0]
    end
    
    subgraph "Output"
        O1[WinRate:<br/>117/272 = 43.0%]
        O2[AvgRet:<br/>sum/272 = +0.13%]
        O3[MaxRisk:<br/>min = -9.43%]
        O4[Events: 272]
    end
    
    I1 --> P1
    P6 --> E1 & E2 & E3 & E4 & E5
    E1 & E2 & E3 & E4 & E5 --> S1 & S2 & S3
    S1 --> O1 & O4
    S2 --> O1
    S3 --> O1
    S1 --> O2
    E1 & E2 & E3 & E4 & E5 --> O3
    
    style I1 fill:#e3f2fd
    style P1 fill:#fff3e0
    style E1 fill:#e8f5e9
    style O1 fill:#ffebee
```

---

## 🎯 Decision Tree

```mermaid
flowchart TD
    START([📊 Scanner Results]) --> CHECK1{Events >= 50?}
    
    CHECK1 -->|No| REJECT1[❌ SKIP<br/>Insufficient Data]
    CHECK1 -->|Yes| CHECK2{WinRate > 55%?}
    
    CHECK2 -->|No| WEAK[⚠️ WEAK SIGNAL<br/>No Edge]
    CHECK2 -->|Yes| CHECK3{AvgRet > 0.3%?}
    
    CHECK3 -->|No| SMALL[⚠️ SMALL EDGE<br/>Not Worth It]
    CHECK3 -->|Yes| CHECK4{MaxRisk acceptable?}
    
    CHECK4 -->|No| HIGH_RISK[❌ HIGH RISK<br/>Skip]
    CHECK4 -->|Yes| GOOD[✅ GOOD SIGNAL]
    
    GOOD --> ACTION[Calculate Position<br/>Set Stop Loss<br/>Plan Entry]
    
    WEAK --> WAIT[⏸️ Wait for<br/>Better Signal]
    SMALL --> WAIT
    REJECT1 --> WAIT
    HIGH_RISK --> WAIT
    
    ACTION --> EXECUTE[Tomorrow:<br/>Execute Trade]
    WAIT --> NEXT[Tomorrow:<br/>Scan Again]
    
    EXECUTE --> MONITOR[Monitor Position]
    NEXT --> START
    
    style GOOD fill:#c8e6c9
    style REJECT1 fill:#ffcdd2
    style WEAK fill:#fff9c4
    style HIGH_RISK fill:#ffcdd2
    style EXECUTE fill:#e1f5fe
```

---

## 📈 Complete Daily Cycle

```mermaid
graph LR
    subgraph "Day N (Today)"
        D1[17:00 Market Close] --> D2[17:05 Update Data]
        D2 --> D3[17:10 Run Scanner]
        D3 --> D4[17:15 Filter Signals]
        D4 --> D5[17:30 Analysis]
        D5 --> D6{Good Signal?}
    end
    
    subgraph "Planning"
        D6 -->|Yes| P1[Calculate Position]
        P1 --> P2[Set Stop Loss]
        P2 --> P3[Plan Entry Price]
        P3 --> P4[Ready for Tomorrow]
        
        D6 -->|No| P5[Mark as Wait]
        P5 --> P4
    end
    
    subgraph "Day N+1 (Tomorrow)"
        P4 --> N1[09:00 Market Open]
        N1 --> N2{Execute?}
        N2 -->|Yes| N3[Enter Position]
        N2 -->|No| N4[Continue Monitoring]
        N3 --> N5[16:30 Monitor/Close]
        N4 --> N5
    end
    
    subgraph "Evening"
        N5 --> E1[17:00 Market Close]
        E1 --> E2[Update Data N+1]
        E2 --> E3[Scan for N+2]
    end
    
    E3 --> D1
    
    style D1 fill:#e3f2fd
    style D3 fill:#fff3e0
    style P1 fill:#e8f5e9
    style N3 fill:#c8e6c9
    style E3 fill:#f3e5f5
```

---

## 🔧 System Components Map

```mermaid
mindmap
  root((Stock Analysis<br/>System))
    Data Pipeline
      data_updater.py
        Incremental Download
        Rate Limiting
        Error Handling
      bulk_data_loader.py
        Bulk Download
        Skip Existing
        Progress Tracking
    
    Analysis Engines
      scanner.py V1
        SD-based Threshold
        Directional Streak
        Historical Prob
      scanner_v2.py V2
        Percentile Threshold
        Mixed Streak
        Volatility Class
      master_scanner.py
        Multi-Asset
        Timeframe-aware
        Universal Logic
    
    Output Tools
      CSV Export
        Latest Results
        Timestamped Archive
      view_scanner.py
        View All
        Filter Streaks
        Top Movers
        Compare History
    
    Documentation
      SYSTEM_WORKFLOW.md
        Architecture
        Calculation Logic
      SCANNER_GUIDE.md
        User Guide
      COMPLETE_TRADING_WORKFLOW.md
        Trading Strategy
```

---

## ✅ Summary

**ระบบมี 3 Scanners:**

1. **V1 (Directional)** - Trend following
2. **V2 (Mixed)** - Volatility analysis  
3. **Universal** - Multi-asset, multi-timeframe

**Logic หลัก:**
1. Calculate Threshold (adaptive)
2. Detect Streak (directional or mixed)
3. Find Historical Matches
4. Calculate Probability
5. Display Results

**Daily Workflow:**
```
Update → Scan → Filter → Analyze → Decide → Execute → Repeat
```

**Ready for:** Live trading with proper risk management! 🚀
