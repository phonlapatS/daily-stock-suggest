# 📘 Project Manual: Fractal N+1 Prediction System (V3.4)

> **Status:** Active | **Codename:** The Adaptive Engine | **Version:** 3.4  
> **Last Updated:** 2026-02-05

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Data Pipeline & Caching](#3-data-pipeline--caching)
4. [Core Logic: The Adaptive Engine](#4-core-logic-the-adaptive-engine)
   - [Dynamic Pattern Detection](#41-dynamic-pattern-detection-3-8-days)
   - [Volatility Thresholds](#42-volatility-thresholds)
   - [Scoring System](#43-scoring-system-confidence--risk)
5. [Reporting System](#5-reporting-system)
   - [The 4-Table Strategy](#51-the-4-table-strategy)
6. [Intraday Scanner (Metals)](#6-intraday-scanner-metals)
7. [Operations Guide](#7-operations-guide)

---

## 1. Executive Summary

The **Fractal N+1 Prediction System** is a statistical arbitrage tool designed to forecast the "Next Day" direction of financial assets. Unlike traditional technical analysis which uses indicators (RSI, MACD), this system uses **Pattern Recognition** based on historical probability.

**Key Philosophy:** "History doesn't repeat itself, but it often rhymes."

**Current Capabilities (V3.4):**
- **Multi-Market:** Supports Thai Stocks (SET), US Tech (NASDAQ), China (A-Shares/ADR), and Precious Metals.
- **Adaptive Logic:** Automatically finds the most effective pattern length (3 to 8 days) for each asset.
- **Smart Caching:** Local OHLC caching to minimize API usage and maximize speed.
- **Intraday Monitoring:** Real-time scanning for Gold/Silver on 15m/30m timeframes.

---

## 2. System Architecture

The system has evolved from a simple script to a modular architecture.

```mermaid
graph TB
    subgraph "External"
        TV[TradingView API]
    end

    subgraph "Core System"
        CACHE[Data Cache Layer<br/>(core/data_cache.py)]
        MAIN[Main Runner<br/>(main.py)]
        PROC[Pattern Processor<br/>(processor.py)]
        BACK[Backtest Engine<br/>(scripts/backtest.py)]
        INTRA[Intraday Runner<br/>(scripts/intraday_runner.py)]
    end

    subgraph "Output"
        CSV[Results CSV]
        LOGS[Performance Logs]
    end

    TV -->|OHLC Data| CACHE
    CACHE -->|Formatted Data| MAIN
    MAIN -->|DataFrame| PROC
    PROC -->|Signals| MAIN
    PROC -->|Verify| BACK
    MAIN -->|Export| CSV
    MAIN -->|Record| LOGS
    
    INTRA -->|Loop| TV
    INTRA -->|Alert| LOGS
```

---

## 3. Data Pipeline & Caching (New in V3.4)

To resolve API rate limits and improve performance, V3.4 introduced a **Smart Caching System**.

### 🔧 mechanism
1.  **Check Cache:** `core/data_cache.py` checks if `data/cache/{symbol}_{interval}.csv` exists.
2.  **Smart Fetch:**
    *   **Cache Miss (First Run):** Fetch 5,000 bars from TradingView.
    *   **Cache Hit (Next Runs):** Fetch only the last 50 bars (Delta) + Merge with local file.
    *   **Stale Check:** If cache is older than 12 hours, force refresh (optional).
3.  **Rate Limiting:**
    *   Enforced 1.0s delay between API calls.
    *   Exponential Backoff (2s → 4s → 8s) on connection errors.

**Benefit:** Reduces API load by **99%** (5000 bars → 50 bars) on repeat runs.

---

## 4. Core Logic: The Adaptive Engine

### 4.1 Dynamic Pattern Detection (3-8 Days)
In previous versions (V3.2), the system looked for a fixed 4-day pattern (e.g., `++--`).
**V3.4 is Adaptive:**
1.  The system scans multiple pattern lengths: **3 days, 4 days, ..., up to 8 days**.
2.  For each length, it calculates:
    *   **Win Rate:** Probability of N+1 directional move.
    *   **Match Count:** How many times this pattern occurred in history.
3.  **Selection Logic:** It prioritizes the **longest pattern** that meets the minimum confidence threshold (>60%).
    *   *Why?* A 6-day pattern match is rarer but more significant than a 3-day match.

### 4.2 Volatility Thresholds
How do we define "UP" (`+`) or "DOWN" (`-`)?
*   We do not use fixed % (e.g., +1%).
*   We use **Dynamic Volatility**:
    *   `Short_Vol` = 20-day Rolling STD.
    *   `Long_Vol` = 252-day Rolling STD.
    *   `Threshold` = `Max(Short, 0.5*Long) * 1.25`.
*   If Price Change > Threshold → **`+`**
*   If Price Change < -Threshold → **`-`**
*   Otherwise → **`.`** (Noise/Sideways)

### 4.3 Scoring System: Confidence & Risk
Every signal is graded:
1.  **Probability (Win Rate):** `(Wins / Total Matches) %`
2.  **Confidence Score:** Adjusted for sample size.
    *   A 100% win rate from 2 matches is **Low Confidence**.
    *   A 65% win rate from 100 matches is **High Confidence**.
    *   *Formula involves Logarithmic decay of sample size.*
3.  **Risk Score:** Based on "Max Drawdown" of that pattern in history.
4.  **Reward-to-Risk (RR):** `Avg_Return / Avg_Loss`.

---

## 5. Reporting System

The system classifies results into 4 strategic tables to guide decision-making (`scripts/calculate_metrics.py`).

| Table Name | Criteria | Strategy |
|------------|----------|----------|
| **1. Thai Strict** | Prob > 60%, RR > 2.0 | **Aggressive / Sniper** (High conviction) |
| **2. Thai Balanced** | Prob > 60%, 1.5 < RR ≤ 2.0 | **Standard Trade** (Good edge) |
| **3. Intl Observation** | Prob > 55%, RR > 1.1 | **Watchlist** (Global markets are noisier) |
| **4. Intl Sensitivity** | Prob > 50%, RR (Low) | **Directional Bias** (For options/hedging) |

***Note:** Minimum 30 historical matches required for Table 1 & 2.*

---

## 6. Intraday Scanner (Metals)

A new module for **Gold (XAUUSD)** and **Silver (XAGUSD)**.
*   **Script:** `scripts/intraday_runner.py`
*   **Timeframes:** 15 Minute & 30 Minute.
*   **Workflow:** Runs in a loop (every 5-15 mins), checking for high-probability setups (>60%).
*   **Output:** Prints Alert to console/log if a signal is found.

---

## 7. Operations Guide

### Prerequisites
- Python 3.10+
- `.env` file with `TV_USERNAME` and `TV_PASSWORD`.

### Daily Routine (End of Day)
To update data and generate the N+1 forecast:
```bash
python3 main.py
```
*Output:* `data/pattern_results.csv` and Console Report.

#### 🕒 Recommended Run Times (Thailand Time)
| Market Focus | Best Time | Logic |
| :--- | :--- | :--- |
| **THAI Stocks (SET)** | **17:00 - 18:00** | Market closes ~16:40. Data is fresh for tomorrow's plan. |
| **US/Global Stocks** | **18:00 (Evening)** | Uses **last night's** close. Perfect for planning tonight's trade (Market opens 21:30). |
| **US/Global Stocks** | **07:00 (Morning)** | Uses **tonight's** close. Best for "Post-Market" analysis (but too late for trade planning). |

> **💡 Pro Tip:** Run at **18:00** to catch both markets effectively (SET for tomorrow, US for tonight).

### Intraday Monitoring (Real-time)
To start the Gold/Silver scanner:
```bash
python3 scripts/intraday_runner.py
```

### View Performance Accuracy
To check how accurate previous forecasts were:
```bash
python3 scripts/view_accuracy.py
```

---

## 8. Project Evolution & History (The Journey)
This section documents the development timeline from the initial prototype to the current Adaptive Engine.

### 📅 Phase 1: The Foundation (V1.0 - V2.0)
*   **V1.0 (Inception):**
    *   *Concept:* Can we predict tomorrow's price based on the last 3 days?
    *   *Logic:* Fixed 3-day pattern matching (e.g., `++-` → ?).
    *   *Limit:* Only worked on single stock (hardcoded).
*   **V2.0 (Multi-Timeframe):**
    *   *Upgrade:* Added support for Day/Week/Month timeframes.
    *   *Feature:* Basic Euclidean distance matching (finding "similar" shapes).

### 📅 Phase 2: The Statistical Era (V3.0 - V3.3)
*   **V3.0 (Statistical Filtering):**
    *   *Shift:* Moved from "Shape Matching" to "Binary Pattern" (`+` or `-`).
    *   *Metric:* Added "Win Rate" calculation (Probability).
*   **V3.1 (Strict Thresholds):**
    *   *Problem:* Small noise (0.1%) was counted as a trend.
    *   *Solution:* Integrated **Dynamic Volatility Thresholds** (Adaptive +/-).
    *   *Outcome:* "Wait & See" signal added for sideways markets.
*   **V3.2 (Scoring System):**
    *   *Feature:* Introduced **Confidence Score** (Sample Size weight) & **Risk Score** (Drawdown).
*   **V3.3 (Reporting & Metrics):**
    *   *Output:* Created the **4-Table Strategy** (Strict, Balanced, Obs, Sens).
    *   *Logging:* Added `core/performance.py` to track daily accuracy vs actuals.

### 📅 Phase 3: The Adaptive Engine (Current V3.4)
*   **V3.4 (Adaptive Logic):**
    *   *Breakthrough:* System now scans **3 to 8 day patterns** dynamically.
    *   *Optimization:* Finds the "Golden Length" for each stock (some respect 3-day cycles, others 5-day).
    *   *Infrastructure:* Added **Local Caching System** (reduces API time by 99%).
    *   *Expansion:* Full Universe support (Thai SET100, US Tech, China, Metals).
    *   *Real-time:* Added **Intraday Scanner** for Gold/Silver (15m/30m).

---

## 9. Next Steps (Roadmap V3.5+)
*   **Trend Following:** Integrate Moving Averages (EMA20/50) to filter counter-trend signals.
*   **Web Dashboard:** Move from Console/CSV to a simple Web UI (Streamlit).
*   **Notification Bot:** Connect `intraday_runner.py` to Line/Telegram API.

---
*End of Master Manual*
