# PredictPlus1 System Documentation (V4.5)
## Unified Fractal Prediction Architecture

**Project Status (2026-02-23):** ระบบเข้าสู่ความเสถียรในระดับ **V4.5 Final Logic** มีการปรับปรุงการคำนวณความน่าจะเป็นแบบ **Consensus (Average of Probabilities)** และการแสดงผลรายงานแบบมืออาชีพควบคู่กับค่าสถิติย้อนหลัง (Stats) เพื่อความโปร่งใสสูงสุด

---

### 1. Core Philosophy: Statistical Pattern Matching
PredictPlus1 V4.4 operates as a **Pure Statistical Prediction Engine**. Its primary goal is to identify high-probability price movements for the next trading day (N+1) based on historical fractal patterns.

*   **Fractal Consistency**: The system assumes that market behavior repeats in recognizable fractal sequences.
*   **Volatility-Based Trigger**: Predictions are only generated when the current day's price movement exceeds a dynamic volatility threshold (Threshold-Only logic).
*   **Indicator Separation**: Technical indicators (SMA, ADX, RSI, etc.) are strictly reserved for the **Backtest/Execution** phase. The **Prediction (N+1)** phase is purely data-driven based on pattern matching.

---

### 2. The N+1 Prediction Pipeline

The system follows a rigid sequence to generate and verify forecasts:

#### Step 1: Data Acquisition & Pre-processing
*   **Source**: Real-time and historical data from TradingView.
*   **Window**: 5,000 bars of historical data per symbol (approx. 20 years for daily data).
*   **Normalization**: Raw prices are converted to percentage changes (`(Close - Open) / Open`) to ensure scale-invariance across different stock prices.

#### Step 2: Dynamic Volatility Thresholding
Every symbol has its own "Normal Range" of movement.
*   **Calculation**: `Max(20-day SD, 252-day SD, Market Floor)`.
*   **Market Floors**: 
    *   Thai Market: 1.0%
    *   US Market: 0.5%
    *   Taiwan/China: 0.5%
*   **Trigger**: A pattern is only "Active" if today's move is greater than this threshold.

#### Step 3: Fractal Pattern Consensus (Aggregate Voting)
When a move is detected, the system breaks the recent price action into "Suffix Patterns" (e.g., if the pattern is `+ - +`, it checks `+`, `- +`, and `+ - +`).
*   **Global Standard**: Every pattern must have occurred at least **30 times** in the last 20 years to be statistically significant.
*   **Consensus Probability (Prob%)**: ตั้งแต่ V4.5 ระบบใช้การหา **ค่าเฉลี่ยของความแม่นยำ (Average of Probabilities)** จากทุก Suffix Patterns ที่โหวตชนะ
    *   สูตร: `SUM(Win_Rate_i) / Number_of_Patterns`
    *   หน้าจอรายงานจะแสดงผลในรูปแบบ `Prob (Stats)` เช่น `76.0% (290)` โดย 290 คือจำนวนครั้งทั้งหมด (Historical Samples) ที่พบข้อมูล
    *   **Strict Logic**: ระบบใช้ค่าดิบทางคณิตศาสตร์ (Raw Math) โดยไม่มีการปรุงแต่งค่า (No Artificial Caps) เพื่อให้สะท้อนความจริงของข้อมูลมากที่สุด

#### Step 4: Verification (Forward Testing)
The system does not just predict; it "marks its own homework."
*   **Target Date**: N+1 (The next trading day).
*   **Verification**: Once the target day's market closes, the system fetches the actual price action.
*   **Accuracy Check**: If `Forecast == Actual Direction`, it is marked as `Correct (1)`.

---

### 3. Unified Market Configurations
As of V4.4, all markets are unified under the `MeanReversionEngine` logic for N+1 prediction:

| Market | Engine | Min Matches | Min Prob | ADX/SMA Filters |
| :--- | :--- | :--- | :--- | :--- |
| **Thai (SET)** | MEAN_REVERSION | 30 | 50% | None (Predict Only) |
| **US (NASDAQ)** | MEAN_REVERSION | 30 | 50% | None (Predict Only) |
| **Taiwan (TWSE)** | MEAN_REVERSION | 30 | 50% | None (Predict Only) |
| **China (HKEX)** | MEAN_REVERSION | 30 | 50% | None (Predict Only) |

---

### 4. Operational Commands (Daily Routine)

| Task | Command | Description |
| :--- | :--- | :--- |
| **1. Run Prediction** | `python main.py` | Scans all markets and logs new forecasts. |
| **2. Deep Dive** | `python scripts/view_report.py ALL` | Shows mathematical breakdown of the decision. |
| **3. Executive View** | `python scripts/daily_forecast_dashboard.py` | Summarizes performance and signals. |
| **4. Verify Results** | `python scripts/check_forward_testing.py --verify` | Checks if yesterday's predictions were correct. |
| **5. Full Statistics** | `python scripts/calculate_performance.py` | Computes Winrates and RRR per market. |

---

### 5. Maintenance & Cleaning
*   **Cache Management**: `python scripts/maintenance/clear_cache.py` - Clears old data to force a fresh scan.
*   **Duplicate Cleanup**: `python scripts/maintenance/cleanup_duplicate_forecasts.py` - Ensures the log is clean for calculation.

---
**Version 4.5 - Final Consensus Logic Complete**
*Date: February 23, 2026*
