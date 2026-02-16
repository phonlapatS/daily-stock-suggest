# Stock Prediction System (v4.1)

📊 **Fractal N+1 Prediction System - Production-Ready Risk Management System**

> **🆕 Version 4.1 Updates (2026-02-14):** "Production-Ready Risk Management System"
> - ✅ **Risk Management Focus:** Stop Loss, Take Profit, Trailing Stop, Position Sizing
> - ✅ **Forward Testing System:** Predict N+1 with automatic verification
> - ✅ **Auto Scheduler:** Multi-market support with smart timing (17:00 ICT Asia, 05:00 ICT US)
> - ✅ **Market Time Management:** Smart skip logic for market close times
> - ✅ **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter
> - ✅ **Transparent Display:** Count prominent, all stocks shown, sorted by Prob%
> - ✅ **Philosophy Shift:** From Indicator-based → Risk Management-based
> - ✅ **5,000-Bar Verified:** Backtested on 260k+ trades with affirmed Alpha (70% Win Rates)
> - ✅ **Statistical Reliability:** Count >= 30 for THAI (Central Limit Theorem)
> - ✅ **Intraday Metals Support:** Gold & Silver 15min/30min with separated logic
> - ✅ **Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)
> - ✅ **Branch:** [version-4.1](https://github.com/phonlapatS/daily-stock-suggest/tree/version-4.1)

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

## 📖 Documentation

### User Manuals
- **[User Manual](docs/USER_MANUAL.md)** - คู่มือระบบครบถ้วน (คำสั่งทั้งหมด)
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - คำสั่งที่ใช้บ่อย
- **[Project Master Manual](docs/PROJECT_MASTER_MANUAL.md)** - คู่มือระบบฉบับสมบูรณ์
- **[Forward Testing Guide](docs/FORECAST_VS_FORWARD_TESTING_ANALYSIS.md)** - คู่มือ Forward Testing
- **[Multi-Market Schedule](docs/MULTI_MARKET_SCHEDULE.md)** - ตารางเวลารันระบบหลายตลาด

### Key Commands

```bash
# Main System
python main.py                                    # Run full prediction system
python scripts/check_forward_testing.py          # Check forward testing results
python scripts/auto_scheduler.py                  # Auto scheduler

# Backtest
python scripts/backtest.py --full --bars 5000    # Full backtest (5000 bars)
python scripts/backtest.py --full --bars 5000 --group GROUP_A_THAI  # Specific market

# Calculate Metrics
python scripts/calculate_metrics.py              # Calculate performance metrics

# View Reports
python scripts/view_report.py SYMBOL             # View report for specific symbol
python scripts/view_report.py --all              # View all reports
```

**ดูรายละเอียดเพิ่มเติม:** [docs/USER_MANUAL.md](docs/USER_MANUAL.md)

---

## 💡 Concept: Risk Management-Based System

### 1. Pattern Matching + History Statistics
- **Pattern Length:** 3-8 days (Dynamic)
- **Threshold:** Market-specific (Thai: 1.0x, US: 0.9x, TW/CN: 0.9x)
- **Statistics:** History-based (Prob, AvgWin, AvgLoss, RRR)

### 2. Risk Management (Core Focus)
- **Stop Loss:** 1.5-2.0% (Fixed, market-specific)
- **Take Profit:** 3.5-5.0% (Fixed, market-specific)
- **Trailing Stop:** Enabled (Activate at 1.5%, Keep 50% of peak)
- **Position Sizing:** Based on Prob% and RRR
- **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter

### 3. Forward Testing System
- **Predict N+1:** Forecast tomorrow's direction
- **Automatic Verification:** Verify predictions after market close
- **Performance Logging:** Complete logs for retrospective analysis
- **Accuracy Tracking:** Track prediction accuracy by pattern

### 4. Market-Specific Display Criteria
- **THAI:** Prob >= 60%, RRR >= 1.3, Count >= 30 (High frequency + High accuracy)
- **US:** Prob >= 60%, RRR >= 1.5, Count >= 15 (Quality over quantity)
- **CHINA/HK:** Prob >= 60%, RRR >= 1.2, Count >= 15
- **TAIWAN:** Prob >= 50%, RRR >= 1.0, Count >= 15
- **METALS (30min):** Prob >= 40%, RRR >= 0.75, Count >= 20
- **METALS (15min):** Prob >= 25%, RRR >= 0.8, Count >= 20

---

## 📈 Changelog

### v4.1 (2026-02-14) - Current
- **Forward Testing System:** Predict N+1 with automatic verification
- **Auto Scheduler:** Multi-market support with optimal timing
- **Market Time Management:** Smart skip logic for market close times
- **Performance Logging:** Complete forward testing logs
- **Risk Management Focus:** Stop Loss, Take Profit, Trailing Stop, Position Sizing
- **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter
- **Intraday Metals Support:** Gold & Silver 15min/30min with separated logic
- **Logic Separation:** 15min and 30min use different rolling windows and max_hold
- **Strategy Differentiation:** Gold uses TREND_FOLLOWING, Silver uses MEAN_REVERSION
- **Parameter Optimization:** Market-specific min_prob, min_stats, and fixed_threshold
- **Display Criteria:** Separate criteria for 15min and 30min timeframes
- **Bug Fixes:** Fixed calculate_metrics.py indentation error, improved error handling

### v3.4 Final (2026-02-07)
- **Hybrid Threshold:** Implemented market-specific logic (Dynamic vs Fixed).
- **Extended Validation:** 5,000-Bar Backtest confirmed system robustness.
- **Reporting:** 4-Table Report optimized for clarity (Signal Count & RRR Focus).

### v3.1 (2026-01-21)
- **Strict Logic:** FLAT days break streaks.
- **Hybrid Threshold:** `Max(20d SD, 0.5 * 1y SD)`.

---

## 🔧 Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file with:
```
TV_USERNAME=your_tradingview_username
TV_PASSWORD=your_tradingview_password
TV_SESSIONID=your_session_id (optional)
```

---

## 📊 System Architecture

```
main.py
├── Data Fetching (TradingView API)
├── Pattern Matching (3-8 days dynamic)
├── Statistics Calculation (Prob, RRR, Count)
├── Risk Management (SL, TP, Trailing Stop)
├── Forward Testing (Predict N+1, Verify)
└── Report Generation (Daily predictions)
```

---

## 🎯 Key Features

### Forward Testing
- **Predict Tomorrow:** Forecast next day direction
- **Automatic Verification:** Verify after market close
- **Performance Tracking:** Track accuracy by pattern
- **Complete Logs:** Full history for analysis

### Auto Scheduler
- **Multi-Market Support:** Different schedules for different markets
- **Optimal Timing:** Run after market close for accurate data
- **Smart Skip Logic:** Skip if already scanned today

### Risk Management
- **Stop Loss:** Market-specific (1.5-2.0%)
- **Take Profit:** Market-specific (3.5-5.0%)
- **Trailing Stop:** Dynamic protection
- **Position Sizing:** Based on probability and RRR

---

## 📚 Additional Resources

- **Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)
- **Branch:** [version-4.1](https://github.com/phonlapatS/daily-stock-suggest/tree/version-4.1)
- **Documentation:** [docs/](docs/)
- **Version History:** [docs/VERSION_HISTORY.md](docs/VERSION_HISTORY.md)

---

## ⚠️ Important Notes

1. **Market Close Timing:** Run the system **after market close** to get accurate close prices
2. **Forward Testing:** Requires 3-4 days of data to get reliable accuracy results
3. **Risk Management:** Always use proper risk management in real trading
4. **Backtesting:** Results are based on historical data, past performance doesn't guarantee future results

---

## 📝 License

Developed for Quantitative Trading Research

---

## 🤝 Contributing

This is a research project. For questions or suggestions, please open an issue on GitHub.

---

*Last Updated: 2026-02-14*
