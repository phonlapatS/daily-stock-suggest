# System Workflow - Stock Analysis System (V4.1)

## 📐 System Architecture

```mermaid
graph TB
    subgraph "Data Layer"
        TV[TvDatafeed] -->|fetch| PROC[processor.py]
        PROC -->|cache| CSV[(Master_Pattern_Stats.csv)]
        PROC -->|incremental| PSM[core/pattern_stats.py]
    end
    
    subgraph "Analysis Layer"
        PROC -->|detect| PAT[Dynamic Pattern 3-8 Days]
        PAT -->|calculate| PROB[Probability & Odds]
        PSM -->|update| STATS[Pattern Statistics]
    end
    
    subgraph "Validation Layer"
        BT[scripts/backtest.py] -->|simulate| HIST[Historical Data]
        BT -->|adaptive split| SPLIT[80/20 Smart Split]
        BT -->|log| LOGS[logs/trade_history.csv]
        LOGS -->|audit| METRICS[scripts/calculate_metrics.py]
        METRICS -->|filter| SCREEN[4-Table Report]
    end
    
    subgraph "Intraday Layer (24h)"
        INTRA[scripts/intraday_runner.py] -->|15m/30m| METALS[Gold/Silver]
        METALS -->|alert| SIGNAL[High-Prob Signal]
    end
    
    subgraph "Output Layer"
        SCREEN -->|report| RPT[Symbol Performance Report]
        METRICS -->|csv| FINAL[data/symbol_performance.csv]
    end
    
    style TV fill:#e1f5ff
    style CSV fill:#fff4e1
    style LOGS fill:#e8f5e9
    style FINAL fill:#f3e5f5
    style INTRA fill:#ffe0b2
```

---

## 🔄 Data Flow (V4.1)

```mermaid
sequenceDiagram
    participant User
    participant Processor as processor.py
    participant StatsMgr as PatternStatsManager
    participant CSV as Master_Pattern_Stats.csv
    participant Backtest as backtest.py
    participant Intraday as intraday_runner.py
    
    User->>Processor: Run Analysis
    Processor->>Processor: Dynamic Pattern Scan (3-8 days)
    Processor->>StatsMgr: Check Last Update Date
    StatsMgr-->>Processor: Returns Last Date
    Processor->>Processor: Fetch Only New Data (Delta)
    Processor->>StatsMgr: Update (Win/Loss/Count)
    StatsMgr->>CSV: Commit Incremental Changes
    
    User->>Backtest: Run Full Scan (38k+ trades)
    Backtest->>Backtest: Adaptive Train/Test Split
    Backtest->>Backtest: Simulate Strategy
    Backtest->>CSV: Export trade_history.csv
    User->>Metrics: Run Calculate Metrics
    Metrics->>User: Show 4 Tables (Thai/International)
    
    loop 24h Monitoring
        Intraday->>Intraday: Scan Gold/Silver (15m/30m)
        Intraday-->>User: Alert if Prob > 60%
    end
```

---

## 📁 File Structure (V4.1)

```
predict/
├── core/                           # Core logic
│   ├── pattern_stats.py           # ✅ Incremental Stats Manager
│   ├── performance.py             # Performance Logging
│   └── ...
│
├── scripts/                        # User Scripts
│   ├── backtest.py                # ✅ Full Market Simulator (Dynamic 3-8 Days)
│   ├── calculate_metrics.py       # ✅ Pop & RR Calculator (4 Tables)
│   ├── intraday_runner.py         # ✅ NEW: 24h Gold/Silver Monitor
│   ├── fact_check.py              # Audit Tool
│   └── view_report.py             # Single Stock Viewer
│
├── logs/                          # Logs
│   └── trade_history.csv          # ✅ Detailed Trade Logs (38k+ rows)
│
├── data/                          # Data Storage
│   ├── Master_Pattern_Stats.csv   # Pattern Knowledge Base
│   └── symbol_performance.csv     # ✅ Final Screener Results
│
└── docs/                          # Documentation
    └── SYSTEM_WORKFLOW.md         # This file
```

---

## ⚙️ Key Components (V4.1)

### **1. Dynamic Pattern Detection (V4.1)**
```
File: processor.py

Features:
✅ Dynamic Length: Scans patterns from 3 to 8 days
✅ Max Effective Length: Selects the LONGEST pattern that exceeds threshold
✅ Adaptive: Each stock gets its optimal pattern length automatically

Logic:
- Extract current market "tail" (last 3-8 bars)
- Scan history for matching patterns at EACH length
- Select longest one with Probability > 55% (or fallback to longest available)
```

### **2. Backtest Engine with Risk Management (V4.1)**
```
File: scripts/backtest.py

Features:
✅ Risk Management: Stop Loss, Take Profit, Trailing Stop, Position Sizing
✅ Production Mode: Slippage, Commission, Gap Risk, Liquidity Filter
✅ Market-Specific Parameters: Thai (1.0x), US (0.9x), TW/CN (0.9x)
✅ Gatekeeper Logic: Prob >= 53% (Thai), 52% (US), 53% (TW/CN)
✅ Dynamic Split: 80% Train / 20% Test for short-history stocks
✅ Auto-Reconnect: Handles network drops during long scans

Usage:
python scripts/backtest.py --full 5000  # Run all stocks, 5000 bars
```

### **3. Market-Specific Metrics Report (V4.1)**
```
File: scripts/calculate_metrics.py

Features:
✅ Count Prominent: Width 12, Comma formatting (Statistical Reliability)
✅ All Passing Stocks: Displayed (No .head() limit - Transparent)
✅ Sorting: By Prob% (Descending)
✅ Market-Specific Criteria:
   - THAI: Prob >= 60%, RRR >= 1.2, Count >= 30
   - US: Prob >= 55%, RRR >= 1.2, Count >= 15
   - CHINA/HK: Prob >= 55%, RRR >= 1.2, Count >= 15
   - TAIWAN: Prob >= 55%, RRR >= 1.2, Count >= 15

Usage:
python scripts/calculate_metrics.py
```

### **4. Intraday Scanner (NEW in V3.4)**
```
File: scripts/intraday_runner.py

Features:
✅ 24h Monitoring: Runs continuously for Gold/Silver
✅ Multi-Timeframe: 15-minute and 30-minute intervals
✅ Auto-Alert: Prints signal when Prob > 60%

Usage:
python scripts/intraday_runner.py  # Runs forever, Ctrl+C to stop
```

---

## 📊 Calculation Logic (Verified)

### **1. Risk-Reward Ratio (RR)**
สูตรที่ได้รับการยืนยันจาก User:
```python
RR = Avg(Real Profit) / Avg(Real Loss)
```
*   **Real Profit:** กำไรที่เกิดขึ้นจริงเมื่อทายถูก
*   **Real Loss:** ขาดทุนที่เกิดขึ้นจริงเมื่อทายผิด

### **2. Probability (Prob%)**
*   **Formula:** `Wins / Total Occurrences`
*   **Note:** คัดเฉพาะ Pattern ที่มีความเชื่อมั่นสูง

### **3. Dynamic Pattern Selection (V4.1)**
*   **Scan:** Lengths 3, 4, 5, 6, 7, 8 days
*   **Select:** Longest pattern with Prob >= 53% (Thai), 52% (US), 53% (TW/CN)
*   **Fallback:** If none exceed threshold, use longest available
*   **Gatekeeper:** Prob >= 53% (Thai), 52% (US), 53% (TW/CN) + Expectancy > 0

---

## 📈 Version History

| Version | Key Changes |
|---------|-------------|
| V3.4    | Dynamic Pattern (3-8 days), Adaptive Split, Intraday Scanner |
| V4.1    | **Production-Ready Risk Management, Transparent Display, Statistical Reliability** |

---

## 📝 Summary

**ระบบ V4.1 คือ "Production-Ready Risk Management System"**
*   **Philosophy Shift:** จาก Indicator-based → Risk Management-based
*   **Risk Management:** Stop Loss, Take Profit, Trailing Stop, Position Sizing
*   **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter
*   **Transparent Display:** Count prominent, All stocks shown, Sorted by Prob%
*   **Statistical Reliability:** Count >= 30 for THAI (Central Limit Theorem)
*   ครอบคลุมตลาดโลก (Thai + US + China + HK + Taiwan)
*   ระบบเสถียร พร้อมใช้งานจริงแบบ Production

---

