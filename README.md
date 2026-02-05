# Stock Prediction System (v3.4)

📊 **Fractal N+1 Prediction System - Pure Data-Driven**

> **🆕 Version 3.4 Updates (2026-02-05):** "The Adaptive Engine"
> - ✅ **Adaptive Logic:** Scans pattern lengths from 3 to 8 days dynamically.
> - ✅ **Smart Cache:** Reduces API calls by 99% using local OHLC storage.
> - ✅ **Intraday Scanner:** Real-time monitoring for Gold/Silver (15m/30m).
> - ✅ **Market Sentiment:** New dashboard for global market direction.

## 🌎 Supported Assets (Total: 255+)

| Group | Description | Count | Details |
|-------|-------------|-------|---------|
| **🇹🇭 THAI** | SET100+ | 118 | Large & Mid-cap Thai Stocks (ADVANC, PTT, KBANK) |
| **🇺🇸 US** | NASDAQ 100 | 98 | US Tech Giants (NVDA, TSLA, AAPL, MSFT) |
| **🇨🇳 CHINA** | Tech & Economy | 13 | US ADRs (BABA, JD, PDD) |
| **⚡ METALS** | Gold & Silver | 4 | XAUUSD, XAGUSD (15m, 30m) |

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

## 💡 Concept: The Adaptive Engine

**1. Dynamic Pattern Recognition**
Unlike previous versions that fixed pattern length (e.g., 3 days), V3.4 finds the "Golden Length" for each asset (3-8 days) based on historical accuracy.

**2. 4-Table Strategy**
*   **Table 1: Thai Strict** (Prob > 60%, RR > 2.0) → *Sniper Mode*
*   **Table 2: Thai Balanced** (Prob > 60%, RR > 1.5) → *Cash Flow*
*   **Table 3: Intl Observation** (Prob > 55%) → *Watchlist*
*   **Table 4: Market Direction** (Prob > 50%) → *Market Radar*

---

## 📈 Changelog

### v3.4 (2026-02-05)
- **Adaptive Engine:** Dynamic pattern length (3-8 days).
- **Caching System:** `core/data_cache.py` for speed.
- **Reporting:** Rebranded "Signals" to "Count" and "Sensitivity" to "Market Direction".

### v3.1 (2026-01-21)
- **Strict Logic:** FLAT days break streaks.
- **Hybrid Threshold:** `Max(20d SD, 0.5 * 1y SD)`.

---

*Developed for Quantitative Trading Research*
