# Project Structure (Version 2.0)

## 📁 โครงสร้างโปรเจกต์

```
PredictPlus1/
├── 📄 README.md                    # Documentation (V2.0)
├── 📄 requirements.txt             # Dependencies
├── 📄 config.py                    # Asset groups & parameters
├── 📄 processor.py                 # Pattern detection logic
├── 📄 main.py                      # Main execution script
│
├── 📂 data/                        # Data Storage
│   ├── pattern_results.csv         # Latest scan results (CSV export)
│   └── cache/                      # Cache files (if any)
│
├── 📂 docs/                        # Documentation
│   ├── guides/                     # User guides
│   ├── flows/                      # Flow diagrams
│   ├── PATTERN_DETECTION_V2.md
│   ├── SYSTEM_WORKFLOW.md
│   └── ...
│
└── 📂 logs/                        # Logs (optional)
```

---

## 🎯 Main Files

### **config.py**
- Asset groups (SET100+, NASDAQ, Metals)
- History bars: **5000** (~20 years)
- Volatility window: 20

### **processor.py**
- Hybrid Volatility calculation
- **SD Threshold: 1.25** (V2.0)
- Pattern detection (30 patterns)
- Min matches: **0.1% of data**

### **main.py**
- **4-Layer Filtering:**
  1. Min Matches
  2. Context-Aware
  3. **Stats ≥ 30** (V2.0)
  4. Probability-Based
  5. Deduplication
- Report generation
- **CSV Export** (V2.0)
- **Execution Timer** (V2.0)

---

## 🚀 Quick Start

### Run Scanner
```bash
python main.py
```

**Output:**
- Console report (grouped by asset type)
- CSV file: `data/pattern_results.csv`
- Execution time: ~9 minutes (220 symbols)

---

## 📊 Data Flow (V2.0)

```
1. main.py starts
   ↓
2. Connect to TvDatafeed
   ↓
3. For each asset group:
   ├─ Fetch 5000 bars
   ├─ Call processor.analyze_asset()
   │  ├─ Calculate hybrid volatility
   │  ├─ Threshold = effective_std × 1.25
   │  ├─ Detect patterns (30 types)
   │  └─ Filter by min_matches (≥5)
   └─ Return results
   ↓
4. Filter results (4 layers):
   ├─ Stats ≥ 30
   ├─ Context-aware
   ├─ Probability-based
   └─ Deduplication
   ↓
5. Generate report
   ├─ Print to console
   └─ Export to CSV
   ↓
6. Show execution time
```

---

## 🔧 Configuration

### Asset Groups (config.py)

**GROUP_A_THAI:**
- 118 stocks (SET100+)
- Interval: 1D
- History: **5000 bars**

**GROUP_B_US:**
- 98 stocks (NASDAQ)
- Interval: 1D
- History: **5000 bars**

**GROUP_C_METALS_30M:**
- XAUUSD, XAGUSD
- Interval: 30min
- History: **5000 bars**

**GROUP_D_METALS_15M:**
- XAUUSD, XAGUSD
- Interval: 15min
- History: **5000 bars**

**GROUP_E_CHINA:**
- 13 ADRs (Tech & Economy)
- Interval: 1D
- History: **5000 bars**

---

## 📈 Version History

### **V2.0 (2026-01-21)** - Current
- SD: 2.0 → **1.25**
- History: 3000 → **5000 bars**
- Stats filter: **≥ 30**
- CSV export
- Execution timer
- Flexible min matches (0.1%)

### **V1.1.1 (2026-01-18)**
- Flexible filtering
- Better UX
- Deduplication

### **V1.1 (2026-01-17)**
- Multi-pattern support
- Context-aware filter
- Probability-based filter

### **V1.0** - Initial
- Basic pattern detection

---

## 📝 Key Parameters (V2.0)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **SD Multiplier** | 1.25 | Optimal balance |
| **History Bars** | 5000 | ~20 years data |
| **Min Matches** | 0.1% (≥5) | Flexible threshold |
| **Stats Filter** | ≥ 30 | Quality control |
| **Volatility Window** | 20 days | Short-term SD |
| **Long-term Floor** | 252 days × 50% | Floor protection |

---

## 🎯 Pattern Support

**Total: 30 Patterns**
- 1-char: 2 (`+`, `-`)
- 2-char: 4 (`++`, `+-`, `-+`, `--`)
- 3-char: 8 (e.g., `+++`, `---`)
- 4-char: 16 (e.g., `++++`, `----`)

---

**Simple, Clean, Powerful!** ✨
