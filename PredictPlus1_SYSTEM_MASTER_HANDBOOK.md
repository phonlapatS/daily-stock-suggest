# PredictPlus1 System Documentation (V5.0)
## Unified Fractal Prediction Architecture

**Project Status (2026-02-23):** ระบบเข้าสู่ความเสถียรในระดับ **V5.0 Audited Logic** มีการแก้ไขความคลาดเคลื่อนทางสถิติ (Probability Overflow) และปรับการรายงานผล P/L ให้เป็นมาตรฐานเดียวกัน (`realized_change`) ทุกลำดับ พร้อมผลการตรวจสอบความแม่นยำย้อนหลังแบบ 100% สอดคล้องกับ Dashboard ครับ

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
*   **Consensus Probability (Prob%)**: ตั้งแต่ V5.0 ระบบใช้การหา **ค่าเฉลี่ยของความแม่นยำ (Average of Probabilities)** จากทุก Suffix Patterns ที่โหวตชนะ และมีการ **Cap ค่าไม่ให้เกิน 100%** เพื่อความถูกต้องทางคณิตศาสตร์
    *   สูตร: `MIN(SUM(Win_Rate_i) / Number_of_Patterns, 100.0)`
    *   หน้าจอรายงานจะแสดงผลในรูปแบบ `Prob (Stats)` เช่น `76.0% (290)` โดย 290 คือจำนวนครั้งทั้งหมด (Historical Samples) ที่พบข้อมูล
    *   **Reporting Synchronicity**: ระบบบังคับใช้เกณฑ์กรองเดียวกันทั่วทั้งระบบ (`Stats >= 30` และ `Prob >= 50%`) เพื่อให้ตัวเลขใน Dashboard และสรุปผลประกอบการตรงกัน 100%

#### Step 4: Verification (Forward Testing)
The system does not just predict; it "marks its own homework."
*   **Target Date**: N+1 (The next trading day).
*   **Verification**: Once the target day's market closes, the system fetches the actual price action.
*   **Accuracy Check**: If `Forecast == Actual Direction`, it is marked as `Correct (1)`.

---

### 3. Unified Market Configurations
As of V4.4, all markets are unified under the `MeanReversionEngine` logic for N+1 prediction:

| Market | Engine | Min Matches | Min Prob | Filtering Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Thai (SET)** | MEAN_REVERSION | 30 | 50% | Stats >= 30, Prob >= 50% |
| **US (NASDAQ)** | MEAN_REVERSION | 30 | 50% | Stats >= 30, Prob >= 50% |
| **Taiwan (TWSE)** | MEAN_REVERSION | 30 | 50% | Stats >= 30, Prob >= 50% |
| **China (HKEX)** | MEAN_REVERSION | 30 | 50% | Stats >= 30, Prob >= 50% |

> [!NOTE]
> **Dashboard Filter**: ตลาดที่มีข้อมูลน้อยกว่า 30 ครั้ง (Sample Size) หรือความน่าจะเป็นต่ำกว่า 50% จะไม่ถูกแสดงใน Dashboard เพื่อลดสัญญาณหลอก (Noise) และรักษาระดับคุณภาพของสัญญาณ (Signal Quality)

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
**Version 5.0 - Audited Statistics & Sync Complete**
*Date: February 23, 2026*
