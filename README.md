# Stock Prediction System (v4.1)

📊 **Fractal N+1 Prediction System - Production-Ready Risk Management System**

> **🆕 Version 4.1 Updates (2026-02-14):** "Production-Ready Risk Management System"
> - ✅ **Risk Management Focus:** Stop Loss, Take Profit, Trailing Stop, Position Sizing
> - ✅ **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter
> - ✅ **Transparent Display:** Count prominent, all stocks shown, sorted by Prob%
> - ✅ **Philosophy Shift:** From Indicator-based → Risk Management-based
> - ✅ **5,000-Bar Verified:** Backtested on 260k+ trades with affirmed Alpha (70% Win Rates)
> - ✅ **Statistical Reliability:** Count >= 30 for THAI (Central Limit Theorem)
> - ✅ **Intraday Metals Support:** Gold & Silver 15min/30min with separated logic
> - ✅ **Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

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
Analyzes all 255+ assets and generates the 4-Table Report.
```bash
python3 main.py
```
*Best Time:* 18:00 (Evening) - Catch SET closing & US pre-market.

### 2. Intraday Scanner (Gold/Silver)
Real-time loop for spotting 15m/30m scalping opportunities.
```bash
python3 scripts/intraday_runner.py
```

### 3. Check Market Sentiment
View the overall Bullish/Bearish balance for tomorrow.
```bash
python3 scripts/market_sentiment.py
```

---

## 📖 Documentation

### User Manuals
- **[User Manual](docs/USER_MANUAL.md)** - คู่มือระบบครบถ้วน (คำสั่งทั้งหมด)
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - คำสั่งที่ใช้บ่อย

### Key Commands
```bash
# Backtest
python scripts/backtest.py --full --bars 2500 --group TAIWAN

# Calculate Metrics
python scripts/calculate_metrics.py

# Daily Report
python main.py
```

**ดูรายละเอียดเพิ่มเติม:** [docs/USER_MANUAL.md](docs/USER_MANUAL.md)

---

## 💡 Concept: Risk Management-Based System

**1. Pattern Matching + History Statistics**
*   **Pattern Length:** 3-8 days (Dynamic)
*   **Threshold:** Market-specific (Thai: 1.0x, US: 0.9x, TW/CN: 0.9x)
*   **Statistics:** History-based (Prob, AvgWin, AvgLoss, RRR)

**2. Risk Management (Core Focus)**
*   **Stop Loss:** 1.5-2.0% (Fixed, market-specific)
*   **Take Profit:** 3.5-5.0% (Fixed, market-specific)
*   **Trailing Stop:** Enabled (Activate at 1.5%, Keep 50% of peak)
*   **Position Sizing:** Based on Prob% and RRR
*   **Production Mode:** Slippage, Commission, Gap Risk, Liquidity Filter

**3. Market-Specific Display Criteria**
*   **THAI:** Prob >= 60%, RRR >= 1.3, Count >= 30 (High frequency + High accuracy)
*   **US:** Prob >= 60%, RRR >= 1.5, Count >= 15 (Quality over quantity)
*   **CHINA/HK:** Prob >= 60%, RRR >= 1.2, Count >= 15
*   **TAIWAN:** Prob >= 50%, RRR >= 1.0, Count >= 15
*   **METALS (30min):** Prob >= 40%, RRR >= 0.75, Count >= 20
*   **METALS (15min):** Prob >= 25%, RRR >= 0.8, Count >= 20

---

## 📈 Changelog

### v4.1 (2026-02-14) - Current
- **Intraday Metals Support:** Gold & Silver 15min/30min with separated logic
- **Logic Separation:** 15min and 30min use different rolling windows and max_hold
- **Strategy Differentiation:** Gold uses TREND_FOLLOWING, Silver uses MEAN_REVERSION
- **Parameter Optimization:** Market-specific min_prob, min_stats, and fixed_threshold
- **Display Criteria:** Separate criteria for 15min and 30min timeframes
- **Bug Fixes:** Fixed debug print duplication, indentation errors

### v3.4 Final (2026-02-07)
- **Hybrid Threshold:** Implemented market-specific logic (Dynamic vs Fixed).
- **Extended Validation:** 5,000-Bar Backtest confirmed system robustness.
- **Reporting:** 4-Table Report optimized for clarity (Signal Count & RRR Focus).

### v3.1 (2026-01-21)
- **Strict Logic:** FLAT days break streaks.
- **Hybrid Threshold:** `Max(20d SD, 0.5 * 1y SD)`.

---

**Repository:** [https://github.com/phonlapatS/daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

*Developed for Quantitative Trading Research*
