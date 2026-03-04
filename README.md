# Predict N+1: Statistical Pattern-Based Trading Suggestion Engine

> **Version 5.0.0** · Live Pilot Phase · February 2026  
> A data-driven system that forecasts next-day (N+1) market direction using historical pattern recognition and total probability consensus.

---

## Table of Contents

- [Overview](#overview)
- [Supported Markets](#supported-markets)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Daily Usage](#daily-usage)
- [CLI Command Reference](#cli-command-reference)
- [Core Engines](#core-engines)
- [System Architecture](#system-architecture)
- [Libraries & Dependencies](#libraries--dependencies)
- [Technical Documentation](#technical-documentation)
- [License](#license)

---

## Overview

Predict N+1 is a **daily statistical trading suggestion engine** that forecasts the next trading day's direction (UP or DOWN) for 255+ assets across 5 global markets.

### How It Works
1. **Encode** daily price movements using a fixed ±0.5% threshold → `+` (Up), `-` (Down), `.` (Flat)
2. **Extract** the current active pattern by reading backward until a flat day (1–8 day suffix patterns)
3. **Scan** 5,000 bars of historical data for matching pattern occurrences
4. **Vote** — aggregate total UP vs DOWN counts from all qualified sub-patterns
5. **Filter** — only output signals where patterns have ≥30 historical occurrences

### Key Principles
- **No ML / No Indicators** — uses only raw price data and fixed threshold classification
- **Total Weighted Probability** — aggregates all historical outcomes, weighted by sample size
- **Statistical Gatekeeper** — minimum 30 occurrences per pattern (Central Limit Theorem)
- **Daily Forward Testing** — every forecast is logged and verified against actual market closes

---

## Supported Markets

| Group | Market | Assets | Timeframe | Engine |
|:------|:-------|:-------|:----------|:-------|
| 🇹🇭 **Thai** | SET100+ | ~114 stocks | Daily (1D) | Mean Reversion |
| 🇺🇸 **US** | NASDAQ | ~95 stocks | Daily (1D) | Mean Reversion |
| 🇨🇳 **China/HK** | HKEX | ~14 stocks | Daily (1D) | Mean Reversion |
| 🇹🇼 **Taiwan** | TWSE | ~10 stocks | Daily (1D) | Mean Reversion |
| 🥇 **Gold** | OANDA | XAUUSD | Intraday (15m/30m) | Trend Momentum |
| 🥈 **Silver** | OANDA | XAGUSD | Intraday (15m/30m) | Mean Reversion |

---

## Project Structure

```
predict/
├── main.py                      # Main orchestrator — scan, predict, verify
├── processor.py                 # Engine router — delegates to correct engine
├── config.py                    # Asset groups, thresholds, engine mappings
├── run_daily_routine.py         # End-to-end daily automation runner
├── requirements.txt             # Python dependencies
├── .env                         # TradingView credentials (not in repo)
│
├── core/                        # Core prediction engines
│   ├── engines/
│   │   ├── base_engine.py       # Base class — pattern detection & voting logic
│   │   ├── reversion_engine.py  # Mean Reversion engine (SET, NASDAQ, etc.)
│   │   └── trend_engine.py      # Trend Momentum engine (Gold)
│   ├── data_cache.py            # Smart caching with delta-fetch
│   ├── dynamic_streak_v2.py     # Dynamic streak extraction
│   ├── gatekeeper_basic.py      # Statistical significance filter
│   ├── pattern_matcher_basic.py # Historical pattern scanner
│   └── performance.py           # Forward testing & verification
│
├── scripts/
│   ├── core_reports/
│   │   ├── check_forward_testing.py    # Verify past forecasts
│   │   ├── daily_forecast_dashboard.py # Executive dashboard
│   │   ├── view_report.py             # Consensus summary report
│   │   ├── view_log.py                # Performance log viewer

│   ├── backtest/
│   │   └── backtest.py          # Full backtesting system
│   ├── backfill/
│   │   ├── backfill_forward_testing.py # Backfill missing N+1 results
│   │   └── backfill_performance_log.py
│   ├── maintenance/
│   │   ├── clean_all_cache.py   # Clear all cached data
│   │   ├── clear_cache.py       # Clear specific cache
│   │   └── cleanup_duplicate_forecasts.py
│   └── analysis/                # Research & analysis scripts
│
├── data/
│   ├── forecast_tomorrow.csv    # Latest N+1 forecasts
│   ├── cache/                   # Cached price data (.parquet/.csv)
│   ├── thai_set100.txt          # Thai stock list
│   └── nasdaq_stocks.txt        # US stock list
│
├── logs/
│   └── performance_log.csv      # Forward testing results
│
└── docs/
    ├── PredictPlus1_SYSTEM_MASTER_HANDBOOK.md
    ├── PredictPlus1_OPERATIONAL_MANUAL.md
    └── VERSION_HISTORY.md
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/phonlapatS/daily-stock-suggest.git
cd daily-stock-suggest
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the project root:
```env
TV_USERNAME=your_tradingview_username
TV_PASSWORD=your_tradingview_password
```

> **Note:** A TradingView account is required for data access via the tvDatafeed library.

### Step 4: Initial Run
```bash
# First run — will fetch and cache data for all assets (~15-30 min)
python main.py
```

After the initial run, subsequent executions will use cached data and only fetch missing bars (delta-fetch), reducing runtime to ~1-2 minutes.

---

## Configuration

All system configuration is centralized in `config.py`:

| Parameter | Default | Description |
|:----------|:--------|:------------|
| `FIXED_THRESHOLD` | `0.5` | Price movement classification threshold (%) |
| `HISTORY_BARS` | `5000` | Historical bars to scan per asset |
| `MIN_MATCHES_THRESHOLD` | `30` | Minimum pattern occurrences required |
| `MIN_PROB_THRESHOLD` | `50.0` | Minimum probability to generate a signal |
| `REQUEST_DELAY` | `0.5` | Delay between API calls (seconds) |

### Asset Groups
Each market group in `ASSET_GROUPS` defines:
- `description` — Group name for display
- `interval` — Timeframe (Daily, 15min, 30min)
- `history_bars` — Number of bars to fetch
- `assets` — List of `{symbol, exchange}` pairs
- `fixed_threshold` — Classification threshold
- `engine` — Engine type (`MEAN_REVERSION` or `TREND_MOMENTUM`)

---

## Daily Usage

### Quick Start — Full Daily Routine
Run the complete daily pipeline (scan → verify → report → dashboard):
```bash
python run_daily_routine.py
```

### Step-by-Step Manual Execution

#### 1. Generate N+1 Forecasts
Scan all 255+ assets and generate directional predictions for tomorrow:
```bash
python main.py
```
**Output:** Updates `data/forecast_tomorrow.csv` and `logs/performance_log.csv`

#### 2. Verify Past Forecasts
Fetch actual closing prices and verify yesterday's PENDING predictions:
```bash
python scripts/core_reports/check_forward_testing.py --verify
```

#### 3. View Executive Dashboard
Display high-confidence signals and performance metrics:
```bash
# Full dashboard (all markets)
python scripts/core_reports/daily_forecast_dashboard.py

# Filter by market
python scripts/core_reports/daily_forecast_dashboard.py --market SET
python scripts/core_reports/daily_forecast_dashboard.py --market NASDAQ
python scripts/core_reports/daily_forecast_dashboard.py --market HKEX
```

#### 4. View Consensus Summary
Detailed mathematical breakdown of pattern signals:
```bash
python scripts/core_reports/view_report.py ALL
```

#### 5. View Performance Log
Review historical forward-testing results:
```bash
python scripts/core_reports/view_log.py
```

---

## CLI Command Reference

### Main Commands

| Command | Description |
|:--------|:------------|
| `python main.py` | Run full scan, predict N+1, verify pending forecasts |
| `python run_daily_routine.py` | Automated full daily routine (scan → report → dashboard) |

### Reports & Dashboard

| Command | Description |
|:--------|:------------|
| `python scripts/core_reports/daily_forecast_dashboard.py` | Executive dashboard with tomorrow's signals |
| `python scripts/core_reports/daily_forecast_dashboard.py --market SET` | Dashboard filtered by market |
| `python scripts/core_reports/check_forward_testing.py --verify` | Verify and stamp pending forecasts |
| `python scripts/core_reports/view_report.py ALL` | Full consensus report for all markets |
| `python scripts/core_reports/view_log.py` | View performance log |


### Backtesting

```bash
# Backtest a single stock
python scripts/backtest/backtest.py PTT SET

# Backtest a single stock with custom bars
python scripts/backtest/backtest.py AAPL NASDAQ --bars 500

# Quick test (4 representative stocks)
python scripts/backtest/backtest.py --quick

# Sample scan (10 stocks per group)
python scripts/backtest/backtest.py --all

# Full scan (all 255+ stocks)
python scripts/backtest/backtest.py --full

# Filter by market group
python scripts/backtest/backtest.py --all --group THAI
python scripts/backtest/backtest.py --all --group US

# Production mode (includes slippage, commission, liquidity filter)
python scripts/backtest/backtest.py --full --production
```

#### Backtest Advanced Options

| Flag | Type | Default | Description |
|:-----|:-----|:--------|:------------|
| `--bars` | int | 200 | Number of test bars |
| `--group` | str | — | Filter by group name (THAI, US, GOLD, etc.) |
| `--multiplier` | float | auto | Threshold multiplier |
| `--production` | flag | — | Enable production mode (slippage + commission) |
| `--fast` | flag | — | Fast mode (skip slow operations) |
| `--stop_loss` | float | — | Override stop loss % |
| `--take_profit` | float | — | Override take profit % |
| `--max_hold` | int | — | Override max holding days |
| `--trail_activate` | float | — | Override trailing stop activation % |
| `--trail_distance` | float | — | Override trailing stop distance % |
| `--min_prob` | float | — | Override minimum probability % |
| `--min_stats` | int | — | Override minimum pattern occurrences |
| `--atr_sl_mult` | float | — | Override ATR stop loss multiplier |
| `--atr_tp_mult` | float | — | Override ATR take profit multiplier |

### Maintenance

| Command | Description |
|:--------|:------------|
| `python scripts/maintenance/clean_all_cache.py` | Clear all cached data files |
| `python scripts/maintenance/clear_cache.py` | Clear specific cache files |
| `python scripts/maintenance/cleanup_duplicate_forecasts.py` | Remove duplicate forecast entries |
| `python scripts/backfill/backfill_forward_testing.py` | Backfill missing forward-test results |

---

## Core Engines

### Mean Reversion Engine
**Used for:** SET, NASDAQ, HKEX, TWSE, Silver  
**Logic:** After a significant directional move, the market tends to revert — the system bets on the opposite direction of the current pattern.

### Trend Momentum Engine
**Used for:** Gold (XAUUSD) Intraday 15min/30min  
**Logic:** Gold tends to continue its momentum during active sessions — the system follows the direction of the current pattern (breakout logic).

### Shared Pipeline
Both engines share the same core pipeline from `BasePatternEngine`:
1. **Encode** → classify each bar as `+`, `-`, or `.` using ±0.5% threshold
2. **Extract** → read backward from today until a flat day (dynamic streak, 1–8 bars)
3. **Suffix Breakdown** → decompose the pattern into all sub-patterns
4. **Historical Scan** → search 5,000 bars for each sub-pattern occurrence
5. **Aggregate Voting** → for each sub-pattern, tally UP vs DOWN wins; discard weak patterns (count < 30)
6. **Total Weighted Probability** → sum winning-side counts / total counts from all qualified patterns
7. **Gatekeeper** → filter signals by minimum probability threshold

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Orchestrator)                │
│  Iterates all asset groups from config.py               │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  data_cache.py  │
              │  Cache fresh?   │
              │  Yes → .parquet │
              │  No  → Delta    │
              │       Fetch API │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  processor.py   │
              │  Engine Router  │
              └───┬────────┬────┘
                  │        │
      ┌───────────▼┐   ┌──▼────────────┐
      │ MeanRev    │   │ TrendMomentum │
      │ Engine     │   │ Engine        │
      └──────┬─────┘   └──────┬────────┘
             │                │
      ┌──────▼────────────────▼──────┐
      │     base_engine.py           │
      │  Pattern Detect → Streak     │
      │  → Suffix → Scan → Vote     │
      │  → Total Weighted Prob       │
      └──────────────┬───────────────┘
                     │
          ┌──────────▼──────────┐
          │  Gatekeeper Filter  │
          │  Count ≥ 30         │
          │  Prob ≥ 50%         │
          └──────────┬──────────┘
                     │
     ┌───────────────▼───────────────┐
     │  forecast_tomorrow.csv        │
     │  performance_log.csv          │
     │  (PENDING → CORRECT/INCORRECT)│
     └───────────────────────────────┘
```

---

## Libraries & Dependencies

### Core Dependencies

| Library | Version | Purpose |
|:--------|:--------|:--------|
| **pandas** | ≥ 2.0.0 | DataFrame management, time series operations, CSV/Parquet I/O |
| **numpy** | ≥ 1.24.0 | Numerical computation, statistical calculations |
| **tvDatafeed** | latest | TradingView historical price data API (OHLCV) |
| **python-dotenv** | ≥ 1.0.0 | Loads `.env` file for secure credential management |
| **requests** | ≥ 2.31.0 | HTTP session handling for TradingView authentication |
| **tabulate** | ≥ 0.9.0 | Formatted table output for performance log viewer |
| **pytz** | ≥ 2023.3 | Timezone handling for market close time checks |

### Install All Dependencies
```bash
pip install -r requirements.txt
```

### `requirements.txt` Contents
```
pandas>=2.0.0
numpy>=1.24.0
git+https://github.com/rongardF/tvdatafeed.git
python-dotenv>=1.0.0
requests>=2.31.0
tabulate>=0.9.0
pytz>=2023.3
```

> **Note:** `tvDatafeed` is installed directly from GitHub. Requires `git` to be available on your system.

---

## Technical Documentation

| Document | Description |
|:---------|:------------|
| [System Master Handbook](PredictPlus1_SYSTEM_MASTER_HANDBOOK.md) | Full technical report — architecture, algorithms, performance data |
| [Operational Manual](PredictPlus1_OPERATIONAL_MANUAL.md) | Detailed CLI guide for daily operations & maintenance |
| [Version History](VERSION_HISTORY.md) | Changelog from V1.0 to V5.0 |

---

## License

This project is developed for educational and research purposes.

---

*Last Updated: March 4, 2026 · Version 5.0.0*
