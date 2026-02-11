# 🔍 Current System Audit (V4.3 - Raw Data Capture)

Based on the latest code inspection of `backtest.py` and core engines, here is the **exact filtering logic** currently active in the system.

## 1. Data Fetching Level (`backtest.py`)
These filters are applied *before* any analysis happens to ensure data integrity.
- **Minimum History**: Requires at least **250 bars** of daily data. If less, the stock is skipped (`❌ Not enough data`).
- **Data Completeness**: Uses `get_data_with_cache` to fetch up to **5,000 bars** (~20 years).
- **Test Set Split**:
  - If total bars >= 1000: Uses last **200 bars** (or user-defined `n_bars`) for testing.
  - If total bars < 1000: Uses last **20%** of data for testing.

## 2. Pattern Recognition Level (`base_engine.py` & `backtest.py`)
This determines what counts as a "valid pattern" (`+`, `-`, or `.`).
- **Dynamic Threshold**: Moves require to exceed a dynamic volatility threshold to be recorded.
  - Formula: `Effective_SD = Max(20-day SD, 252-day SD, Market_Floor)`
  - **Market Floor (Minimum Move)**:
    - 🇺🇸 **US Market**: **0.6%** (0.006)
    - 🇹🇭 **Thai Market**: **1.0%** (0.01)
  - **Multiplier**: Default is **1.25x** applied to the Effective_SD.
- **Pattern Length**: Only patterns with length **3 to 8 bars** are considered.

## 3. Backtest Execution Level (`backtest.py`)
This is where the "Trade" is simulated. **IMPORTANT: All engine-specific gatekeepers (RSI, ADX) are BYPASSED in this step to capture RAW data.**

- **Historical Occurrence (Min Stats)**:
  - A pattern must have occurred at least **30 times** in the past (Training Data) to be considered statistically significant. 
  - *If a pattern appeared only 5 times in 20 years, it is ignored.*
- **Directional Bias (Strategic Logic)**:
  - 🇺🇸 **US Market**: Follows the Last Character (Trend Following). Ex: `++` -> predicts `UP`.
  - 🇹🇭 **Thai Market**: Fades the Last Character (Mean Reversion). Ex: `++` -> predicts `DOWN`.
- **Conflict Resolution**:
  - If multiple pattern lengths match (e.g., length 3 and length 5), the system picks the one with the **highest historical probability**.

## 4. Reporting Level (`calculate_metrics.py`)
This is where the "Elite" filtering happens (Post-Processing).
- **Raw Count**: Includes EVERYTHING that passed steps 1-3.
- **Elite Count**: Filters trades where:
  - **Confidence (Prob)** >= 60%
  - **Historical Occurrences** >= 5 (in the filtered set)

---
**Summary for Mentor:**
"Currently, our raw backtest (Step 3) is extremely pure. It only filters for **Data Quality** (Min 250 bars) and **Statistical Significance** (Min 30 historical occurrences). We removed all indicator-based filters (RSI, ADX) to expose the true raw performance of the price patterns."
