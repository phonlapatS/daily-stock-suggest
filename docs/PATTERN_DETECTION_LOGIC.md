# Predict N+1 System V3.2: Pattern Detection & Backtesting Logic

## 🎯 Overview

This document details the core logic used in **Predict N+1 System V3.2**, focusing on how patterns are detected, how statistical thresholds are determined, and how backtesting verifies accuracy.

---

## 📊 1. Core Logic: Pattern Detection

The system calculates patterns based on daily price movements relative to a **Volatility Threshold**.

### Step 1: Calculate Volatility Threshold
Instead of a fixed percentage, we use a dynamic threshold adjusted to market conditions.
- **Short-term Volatility**: Rolling 20-day standard deviation.
- **Long-term Volatility**: Rolling 252-day standard deviation (weighted 0.5).
- **Effective Threshold**: `max(Short_Std, Long_Std * 0.5) * 1.25`

**Formula:**
```python
short_std = pct_change.rolling(20).std()
long_std = pct_change.rolling(252).std()
threshold = max(short_std, long_std * 0.5) * 1.25
```
*Why?* This filters out "noise" in low-volatility periods while capturing significant moves in high-volatility periods.

### Step 2: Define Daily Movement (Pattern Element)
Each day is classified into one of three states relative to the threshold:
- `+` (UP): `% Change > +Threshold`
- `-` (DOWN): `% Change < -Threshold`
- `.` (SIDE/NOISE): `Abs(% Change) <= Threshold` (Ignored in strict pattern matching)

### Step 3: Construct the Pattern
A pattern consists of the **last 4 days** of price action.
- Example: `++--` (Up, Up, Down, Down)
- This 4-day sequence captures recent momentum and reversal behaviors.

---

## 📈 2. Statistical Forecasting

Once the current pattern (e.g., `++--`) is identified, the system searches historical data (last 5,000 bars) for all previous occurrences of this exact pattern.

### Probability Calculation
1. **Find Matches**: Count how many times `++--` occurred in the past.
2. **Observe Next Day**: For each match, check if the *next day* was UP or DOWN.
3. **Calculate Probabilities**:
   - `Bull Prob` = (Up Counts / Total Matches) * 100
   - `Bear Prob` = (Down Counts / Total Matches) * 100
4. **Dominant Direction**: The forecast is simply the direction with higher probability (>50%).

### Confidence Score
Confidence is a function of both **Probability** and **Sample Size**. A high probability is meaningless if the sample size is too small (e.g., 100% from 1 match).

**Formula:**
```python
conf_score = (probability - 50) * log(matches) / log(100)
```
- A safe minimum match count is set to **30**. If matches < 30, the result is hidden or marked as low confidence.

---

## 🔬 3. Backtesting Methodology

The backtest process simulates real-world usage using historical data.

### Split Verification
1. **Training Data**: All data up to Day `N`.
   - Used to build the pattern statistics database.
2. **Testing Data**: Data from Day `N+1` to Present.
   - The system "predicts" Day `N+1` using only data available up to Day `N`.
   - Then, it checks if the prediction was correct.

### Metrics
- **Accuracy**: (Correct Forecasts / Total Forecasts) * 100
- **Expectancy**: Average return per trade based on the forecast.

---

## 🚀 4. Performance Logging

The system maintains a `logs/performance_log.csv` to track real-time performance.
- **Log**: Saves `Date`, `Symbol`, `Forecast`, `Pattern` for tomorrow.
- **Verify**: On the next run, checks yesterdays log against actual market close.
- **Self-Correction**: This allows the user to monitor if the system's "High Confidence" signals are actually performing well in current market conditions.

---

## ✅ Summary of V3.2 Improvements
- **Dynamic Threshold**: More adaptive than fixed %.
- **Performance Logging**: Automated verification loop.
- **Strict Filtering**: Hiding results with <30 historical matches.
- **Robustness**: Added retry logic and delays to prevent API timeouts.
