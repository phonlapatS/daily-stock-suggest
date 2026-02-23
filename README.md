# PredictPlus1: Fractal N+1 Prediction System (V5.0 Stable)
> **Advanced Statistical Pattern Matching for Global Equity Markets**

## 🎯 Current Status: V5.0 Audited Reliability (Feb 2026)
This version marks the shift from algorithmic expansion to **Statistical Integrity**. Version 5.0 is the result of a full system audit, fixing mathematical discrepancies and ensuring that data reporting is 100% synchronized across all tools.

- **High-Fidelity Reporting**: Synchronized P/L reporting across all scripts using `realized_change` (Scan Price -> Target Price).
- **Audited Statistics**: Fixed probability calculations (removed overflow > 100%) and conducted a full data reconstruction from Feb 2nd, 2026.
- **Statistical Gatekeeper**: Strict enforced filters (`Stats >= 30` and `Prob >= 50%`) to eliminate noise and low-confidence signals.
- **Market Coverage**: SET (Thai), NASDAQ (US), TWSE (Taiwan), HKEX (China/HK), OANDA (Gold/Silver).

---

## 🌎 Supported Markets (Total: 255+ Assets)

| Group | Description | Count | Core Engine |
| :--- | :--- | :--- | :--- |
| **🇹🇭 THAI** | SET100+ | 118 | Mean Reversion (Fractal Consensus) |
| **🇺🇸 US** | NASDAQ 100 | 98 | Mean Reversion (Fractal Consensus) |
| **🇨🇳 CHINA/HK** | Tech & Economy | 13 | Mean Reversion (Fractal Consensus) |
| **🇹🇼 TAIWAN** | Semicon | 10 | Mean Reversion (Fractal Consensus) |
| **⚡ METALS** | Gold & Silver | 2 | Fixed Threshold (Intraday 15m/30m) |

---

## 🚀 Daily Operational Routine

### 1. Generate New Predictions (N+1)
Scans all 255+ assets and logs new directional forecasts for the next trading day.
```bash
python main.py
```

### 2. Verify Past Results (Profit/Loss)
Fetches recent market data to verify if previous forecasts were correct and updates the performance log.
```bash
python scripts/core_reports/check_forward_testing.py --verify
```

### 3. Review Executive Dashboard (V5.0 Live)
Show high-confidence signals for tomorrow and audited performance metrics.
```bash
# View Full Dashboard
python scripts/core_reports/daily_forecast_dashboard.py

# View Specific Market only (e.g. Thai Market) to prevent terminal wrapping
python scripts/core_reports/daily_forecast_dashboard.py --market SET
```

### 4. Deep-Dive Strategy Analysis
Analyze the mathematical breakdown of specific signals and historical probabilities.
```bash
python scripts/view_report.py ALL
```

---

## ⚡ Technical Documentation
All system manuals are located in the root directory for quick access:

- 📘 **[SYSTEM MASTER HANDBOOK](PredictPlus1_SYSTEM_MASTER_HANDBOOK.md)**: Technical logic, pattern consensus formulas, and engine parameters.
- 📜 **[OPERATIONAL COMMANDS MANUAL](PredictPlus1_OPERATIONAL_MANUAL.md)**: Detailed CLI guide for maintenance, backfilling, and debugging.
- 🕰️ **[VERSION HISTORY](VERSION_HISTORY.md)**: Evolution log from V1.0 Foundation to V5.0 Audited Stability.

---

## 🔧 Installation & Setup
1. **Requirements**: `pip install -r requirements.txt`
2. **Environment**: Create a `.env` file with `TV_USERNAME` and `TV_PASSWORD`.
3. **Data Core**: Ensure `logs/performance_log.csv` is present for reporting. If starting fresh, historical data can be generated using `scripts/backfill/backfill_forward_testing.py`.

---

## 💡 Core Philosophy: Audited Consensus Voting
PredictPlus1 V5.0 utilizes **Audited Consensus Voting**. The system breaks price action into 1-7 day suffix fractals. A signal only triggers if there is a **30-sample minimum** agreement across these fractals. V5.0 specifically ensures that the reported winrates and reward-to-risk ratios are filtered for mathematical significance, providing a "No-Noise" view of strategy performance.

---
*Last Updated: 2026-02-23 | Branch: [version-5.0](https://github.com/phonlapatS/daily-stock-suggest/tree/version-5)*
