# Stock Prediction System (v3.1)

📊 **Fractal N+1 Prediction System - Pure Data-Driven**

> **🆕 Version 3.1 Updates (2026-01-21):** Refined Logic & Enhanced Reporting!
> - ✅ **Strict Logic:** "FLAT" days (within threshold) now **break the streak**. Logic is tighter and more precise.
> - ✅ **Hybrid Volatility Threshold:** Uses `Max(20-day SD, 50% of 1-Year SD)` to handle both volatile and flat markets.
> - ✅ **Corrected Probability:** Prob = `Count / (UP + DOWN)`. FLAT days are excluded from the denominator to ensure `Prob >= 50%`.
> - ✅ **Streak Profile:** New "Momentum" table showing the survival rate of consecutive UP/DOWN streaks.
> - ✅ **Intraday Metals:** Support for Gold (XAUUSD) & Silver (XAGUSD) analysis.

## 🌎 Supported Assets (Total: 255+)

| Group | Description | Count | Details |
|-------|-------------|-------|---------|
| **🇹🇭 THAI** | SET100+ | 118 | Large & Mid-cap Thai Stocks (ADVANC, PTT, KBANK) |
| **🇺🇸 US** | NASDAQ 100 | 98 | US Tech Giants (NVDA, TSLA, AAPL, MSFT) |
| **🇨🇳 CHINA** | Tech & Economy | 13 | US ADRs (BABA, JD, PDD) |
| **⚡ METALS** | Gold & Silver | 4 | XAUUSD, XAGUSD (15m, 30m, 1h) |

---

## 💡 Concept: Hybrid Logic

**1. Dynamic Thresholding (Adaptive Noise Filter)**
Instead of a fixed percentage, we use a **Hybrid Volatility Threshold**:
*   **Short-Term:** 1.25 * SD (Standard Deviation) of the last **20 days**.
*   **Long-Term Floor:** 50% of the 1-Year SD.
*   **Logic:** `Threshold = Max(Short-Term, Long-Term Floor)`
*   *Why?* prevents the threshold from becoming too small in extremely calm markets, reducing false signals (overfitting).

**2. Strict Pattern Recognition**
*   **UP (+)**: Price Change > +Threshold
*   **DOWN (-)**: Price Change < -Threshold
*   **FLAT**: Price Change within ±Threshold
*   *Rule:* A **FLAT** day immediately **breaks** a streak. We only count pure momentum.

---

## 🚀 Usage

### 1. View Report (Single Asset)
Detailed analysis including Master Pattern Stats and Streak Profile.
```bash
python view_report.py [SYMBOL]
# Example: python view_report.py ADVANC
```

### 2. Batch Processing (All Assets)
Process all 255+ assets and generate `Master_Pattern_Stats.csv` and `Streak_Profile.csv`.
```bash
python batch_processor.py
```

### 3. Check Gold/Silver Intraday
```bash
python scripts/check_gold_silver.py
```

---

## 📊 Output Example (view_report.py)

```text
===============================================================
=================
📄 PART 1: MASTER PATTERN STATS (Tomorrow's Forecast) [Threshold: ±1.40%]
===============================================================
=================
Pattern    Category   Chance     Prob   Stats           Avg_Ret
--------------------------------------------------------------------------------
+-+        Reversal   🔴 DOWN    57%    4/7 (5000)      -0.5%
...

===============================================================
=================
📄 PART 2: STREAK PROFILE (Momentum)
===============================================================
=================
Type   Day         Stats               Prob
---------------------------------------------------------------
UP     1         465/582     🔴 REV. (79.9%)        
UP     2          90/117     🔴 REV. (76.9%)        
```

---

## 📈 Changelog

### v3.1 (2026-01-21)
- **Strict Logic:** FLAT days break streaks.
- **Hybrid Threshold:** `Max(20d SD, 0.5 * 1y SD)`.
- **Prob Fix:** Exclude FLAT from Prob denominator.
- **UI:** Merged "Continued/Reached" columns in Streak Profile.

### v2.0 (2026-01-21)
- **New Assets:** China Tech & Economy ADRs.
- **Dynamic Reporting:** Grouped tables.
- **Optimization:** SD 1.25 & 5000 Bars history.

---

*Developed for Quantitative Trading Research*
