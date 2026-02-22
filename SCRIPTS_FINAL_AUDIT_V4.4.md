เช# Final Scripts Audit: PredictPlus1 V4.4.7 🔍

Based on your request, I have audited the remaining **30 files** in the `scripts/` folder. Here is the classification into **Essential**, **Backfill**, and **Redundant**.

## ✅ Group A: Core Predict N+1 (KEEP)
*Essential for daily operation and viewing results.*

| File Name | Description |
| :--- | :--- |
| `daily_forecast_dashboard.py` | The main executive dashboard. |
| `view_report.py` | Detailed consensus report (Main tool). |
| `check_forward_testing.py` | Verifies predictions against actual close prices. |
| `calculate_performance.py` | Calculates win-rate, RRR, and accuracy stats. |
| `forward_testing_report.py` | Detailed move analysis and accuracy breakdown. |
| `market_sentiment.py` | Shows overall market bias (Bullish/Bearish). |
| `view_log.py` | Quick tool to check the contents of the performance log. |

## 🔄 Group B: Backfill & Maintenance (KEEP - As Requested)
*Tools to repair logs, manage cache, and regenerate history.*

| File Name | Description |
| :--- | :--- |
| **`backfill_forward_testing.py`** | **The main backfill engine (Requested).** |
| **`backfill_performance_log.py`** | Auxiliary backfill tool for specific logs. |
| `generate_master_stats.py` | **Crucial:** Regenerates the Pattern Database. |
| `clear_cache.py` | Clears all cached price data (Manual refresh). |
| `clean_all_cache.py` | Batch clearing of different market caches. |
| `cleanup_duplicate_forecasts.py` | Fixes potential data entry errors in logs. |
| `restore_logs.py` | Used if `performance_log.csv` gets corrupted. |

## 🧪 Group C: Advanced Research (OPTIONAL - Keep?)
*Specialized tools used for fine-tuning specific market behaviors.*

| File Name | Description | Rationale |
| :--- | :--- | :--- |
| `backtest.py` | The base backtest logic. | Used internally for research. |
| `market_regime.py` | SMA-based regime detection. | Core dependency for Taiwan logic. |
| `optimal_filtering_logic.py` | Logic experiments. | Defines high-level filtering rules. |
| `simulate_equity_curves.py` | Monte Carlo simulations. | Useful for risk assessment. |

## 🔴 Group D: Redundant / Obsolete (DELETE)
*Experimental scripts from V12/V13 that are no longer part of the V4.4.7 core.*

| File Name | Description |
| :--- | :--- |
| `fix_test_china.py` | One-off fix for old China tests. |
| `quick_china_adjustment.py` | Manual tuning for V13.0 (Now in config). |
| `quick_china_test_table.py` | V13 validation tool. |
| `quick_test_taiwan_params.py` | V12 validation tool. |
| `full_threshold_analysis.py` | Superseded by `view_report.py`. |
| `filter_signals.py` | Logic is now integrated into `main.py`. |
| `threshold_comparison.py` | Manual comparison tool for early V4 tests. |
| `clean_china_cache.py` | Redundant (use `clean_all_cache.py`). |
| `clean_taiwan_cache.py` | Redundant (use `clean_all_cache.py`). |
| `clean_china_results.py` | Obsolete results cleaner. |
| `split_trade_history_by_market.py`| Fixed in `calculate_performance.py`. |
| `diagnose_market_loss.py` | diagnostic tool for V4.1. |

---

### 💡 ประเมินความจำเป็น:
ผมแนะนำให้เก็บ **Group A, B, และ C** ไว้ครับ เพราะเป็นหัวใจของระบบ N+1 และตัว Backfill/Maintenance ที่คุณต้องการ

ส่วน **Group D (12 ไฟล์)** คือสคริปต์ที่ใช้ "ทดลอง" ปรับจูนตลาดไต้หวันและจีนในช่วงสัปดาห์ที่ผ่านมา ซึ่งตอนนี้ logic เหล่านั้นถูกฝังลงใน `config.py` และ `base_engine.py` หมดแล้วครับ การลบ Group นี้จะช่วยให้โฟลเดอร์ `scripts/` เหลือเพียงเครื่องมือที่ใช้งานจริงประมาณ 18-20 ไฟล์ครับ

**คุณต้องการให้ผมลบ Group D เลยไหมครับ? หรืออยากให้เก็บตัวไหนไว้เป็นพิเศษไหม?**
