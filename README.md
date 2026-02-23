# PredictPlus1: Fractal N+1 Prediction System (V5.0)
> **Advanced Statistical Pattern Matching for Global Equity Markets**

## 🎯 Current Status: V5.0 Audited Reliability (Feb 2026)
- **High-Fidelity Reporting**: Synchronized P/L reporting across all scripts using `realized_change`.
- **Audited Statistics**: Fixed probability calculations and cleared legacy data reconstruction from Feb 2nd.
- **Statistical Gatekeeper**: All dashboards strictly filter for `Stats >= 30` and `Prob >= 50%` to ensure quality over quantity.
- **Market Coverage**: SET (Thai), NASDAQ (US), TWSE (Taiwan), HKEX (China/HK), OANDA (Gold/Silver).
- ✅ **Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)
- ✅ **Branch:** [version-5.0](https://github.com/phonlapatS/daily-stock-suggest/tree/version-5.0) (Recommended)

## 🌎 Supported Assets (Total: 255+)

| Group | Description | Count | Strategy |
|-------|-------------|-------|----------|
| **🇹🇭 THAI** | SET100+ | 118 | **Dynamic Threshold** (Alpha Seeking) |
| **🇺🇸 US** | NASDAQ 100 | 98 | **Dynamic Threshold** (Hybrid Volatility) |
| **🇨🇳 CHINA/HK** | Tech & Economy | 13 | **Dynamic Threshold** (Mean Reversion) |
| **🇹🇼 TAIWAN** | Semicon | 10 | **Dynamic Threshold** (Regime-Aware) |
| **⚡ METALS** | Gold & Silver | 2 | **Fixed Threshold** (Intraday 15min/30min) |

---

## 🚀 Usage (Quick Start)

### 1. View Daily Report (The Main Tool)
Analyzes all 255+ assets and generates the prediction report with forward testing results.

```bash
python main.py
```

**Best Time:** After market close (17:00 ICT for Asian markets, 05:00 ICT for US market)

### 2. Forward Testing (Check Prediction Results)
Check pending and verified forecasts from forward testing system.

```bash
# View all forecasts (pending + verified)
python scripts/check_forward_testing.py

# Verify pending forecasts
python scripts/check_forward_testing.py --verify

# Show summary (last 30 days)
python scripts/check_forward_testing.py --days 30

# Show all forecasts
python scripts/check_forward_testing.py --all
```

### 3. Auto Scheduler (Automated Daily Runs)
Automatically run the system at optimal times for different markets.

```bash
python scripts/auto_scheduler.py
```

**Schedule:**
- **13:00 ICT** - Taiwan Semicon Market (TWSE)
- **15:30 ICT** - China & HK Tech Market (HKEX)
- **17:00 ICT** - Thai Market (SET)
- **05:00 ICT** - US Market (NASDAQ/NYSE)

### 4. Run Specific Market Groups
Run the system for specific market groups only.

```bash
python scripts/run_market_groups.py GROUP_A_THAI
python scripts/run_market_groups.py GROUP_B_US
python scripts/run_market_groups.py GROUP_C_CHINA_HK
python scripts/run_market_groups.py GROUP_D_TAIWAN
```

### 5. Intraday Scanner (Gold/Silver)
Real-time loop for spotting 15m/30m scalping opportunities.

```bash
python scripts/intraday_runner.py
```

### 6. Check Market Sentiment
View the overall Bullish/Bearish balance for tomorrow.

```bash
python scripts/market_sentiment.py
```

---

## 📖 Documentation & Guides

To keep the workspace clean and efficient, all system documentation has been consolidated into two main balanced files:

*   📘 **[SYSTEM MASTER HANDBOOK](file:///e:/PredictPlus1/PredictPlus1_SYSTEM_MASTER_HANDBOOK.md)** — technical patterns, risk logic, and evolution history.
*   📜 **[OPERATIONAL COMMANDS MANUAL](file:///e:/PredictPlus1/PredictPlus1_OPERATIONAL_MANUAL.md)** — detailed CLI usage, backfilling, and maintenance.
*   🕰️ **[VERSION HISTORY](file:///e:/PredictPlus1/VERSION_HISTORY.md)** — log of all changes from V1.0 to V4.4.7.

---

## ⚡ Quick Command Reference

| Category | Command |
| :--- | :--- |
| **New Scan** | `python main.py` |
| **View Report** | `python scripts/core_reports/view_report.py ALL` |
| **Verify Results** | `python scripts/core_reports/check_forward_testing.py --verify` |
| **Check Stats** | `python scripts/analysis/calculate_performance.py` |
| **Dashboard** | `python scripts/core_reports/daily_forecast_dashboard.py` |

---

## 💡 Core Philosophy: V4.4.7 Aggregate Voting
PredictPlus1 V4.4.7 moves away from single-pattern selection and uses **Aggregate Voting (Consensus)**. By analyzing multiple suffix levels (1-day to 7-day patterns) and enforcing a **30-sample minimum**, the system provides high-confidence directional forecasts backed by statistical reliability.

---

## 🔧 Installation & Setup
1.  **Requirements:** `pip install -r requirements.txt`
2.  **Credentials:** Set up `TV_USERNAME` and `TV_PASSWORD` in a `.env` file.
3.  **Bootstrap:** Run `python scripts/backfill/generate_master_stats.py` to build the initial pattern database (recommended once).

---
*Last Updated: 2026-02-23 | V4.5 Production*
