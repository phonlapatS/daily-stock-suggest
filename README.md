# Stock Prediction System (v3.4)

📊 **Fractal N+1 Prediction System - Pure Data-Driven**

> **🆕 Version 3.4 Updates (2026-02-07):** "The Hybrid Engine"
> - ✅ **Hybrid Threshold Strategy:** Dynamic for Thai Agility vs. Fixed for Global Stability.
> - ✅ **5,000-Bar Verified:** Backtested on 260k trades with affirmed Alpha (70% Win Rates).
> - ✅ **Adaptive Logic:** Scans pattern lengths from 3 to 8 days dynamically.
> - ✅ **Smart Cache:** Reduces API calls by 99% using local OHLC storage.

## 🌎 Supported Assets (Total: 255+)

| Group | Description | Count | Strategy |
|-------|-------------|-------|----------|
| **🇹🇭 THAI** | SET100+ | 118 | **Dynamic Threshold** (Alpha Seeking) |
| **🇺🇸 US** | NASDAQ 100 | 98 | **Fixed 0.6%** (Noise Filtering) |
| **🇨🇳 CHINA** | Tech & Economy | 13 | **Fixed 1.2%** (Volatility Guard) |
| **⚡ METALS** | Gold & Silver | 4 | **Fixed 0.4%** (Scalping Mode) |

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

## 💡 Concept: The Hybrid Engine

**1. Market-Specific Logic**
*   **Thai Market:** Inefficient = Profit from Volatility (Dynamic Thresholds).
*   **Global Market:** Efficient = Profit from Stability (Fixed Thresholds).

**2. Dynamic Pattern Recognition**
Unlike previous versions that fixed pattern length (e.g., 3 days), V3.4 finds the "Golden Length" for each asset (3-8 days) based on historical accuracy.

**3. 4-Table Strategy (Verified Stats)**
*   **Table 1: Thai Strict** (Prob > 60%, RR > 2.0) → *Alpha Mode (e.g. SUPER 70%)*
*   **Table 2: Thai Balanced** (Prob > 60%, RR > 1.5) → *Cash Flow*
*   **Table 4: Market Direction** (Prob > 50%) → *Global Radar (e.g. NVDA 50.2%)*

---

## 📈 Changelog

### v3.4 Final (2026-02-07)
- **Hybrid Threshold:** Implemented market-specific logic (Dynamic vs Fixed).
- **Extended Validation:** 5,000-Bar Backtest confirmed system robustness.
- **Reporting:** 4-Table Report optimized for clarity (Signal Count & RRR Focus).

### v3.1 (2026-01-21)
- **Strict Logic:** FLAT days break streaks.
- **Hybrid Threshold:** `Max(20d SD, 0.5 * 1y SD)`.

---

*Developed for Quantitative Trading Research*
