# Project Structure

```
predict/
├── 📄 README.md                    # Main documentation
├── 📄 requirements.txt             # Dependencies
│
├── 📂 core/                        # Core Analysis Modules
│   ├── config.py                   # Configuration
│   ├── utils.py                    # Helper functions
│   ├── data_fetcher.py             # TradingView API
│   ├── stats_analyzer.py           # Statistical analysis
│   ├── predictor.py                # Prediction logic
│   └── visualizer.py               # Plotting
│
├── 📂 pipeline/                    # Data Pipeline
│   ├── data_updater.py             # Main updater (50+ stocks)
│   ├── data_cache.py               # Caching system
│   ├── data_cleaner.py             # Data cleaning
│   └── batch_processor.py          # Batch processing
│
├── 📂 scripts/                     # User Scripts
│   ├── run.py                      # Single stock analysis
│   ├── run_from_parquet.py         # Analyze from parquet
│   └── main_stats_extraction.py    # Legacy script
│
├── 📂 docs/                        # Documentation
│   ├── guides/
│   │   ├── DATA_PIPELINE_GUIDE.md
│   │   ├── DATA_CLEANING_GUIDE.md
│   │   ├── PARQUET_USAGE_GUIDE.md
│   │   └── PERFORMANCE_OPTIMIZATION.md
│   └── flows/
│       ├── SYSTEM_FLOW.md
│       ├── SIMPLE_FLOW.md
│       └── OVERVIEW_FLOW.md
│
├── 📂 data/                        # Data Storage
│   ├── stocks/                     # Parquet files (42 stocks)
│   └── cache/                      # Cache files
│
├── 📂 results/                     # Analysis Results
└── 📂 logs/                        # Logs
```

## 🎯 Quick Start

### Option 1: Single Stock (Quick)
```bash
python scripts/run.py PTT SET
```

### Option 2: Batch Update (Production)
```bash
# 1. Update data
python pipeline/data_updater.py

# 2. Analyze
python scripts/run_from_parquet.py PTT SET
```

## 📚 Documentation

- **Main:** [README.md](README.md)
- **Guides:** [docs/guides/](docs/guides/)
- **Flow Diagrams:** [docs/flows/](docs/flows/)
