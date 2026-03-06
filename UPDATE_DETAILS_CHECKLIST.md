# ✅ Update Details Checklist — Predict N+1

**Author:** Rocket (phonlapatS)  
**Period:** December 2025 — March 6, 2026  
**Project:** [daily-stock-suggest](https://github.com/phonlapatS/daily-stock-suggest)

---

## Phase 1: Foundation (V1.0 — Dec 2025)
- [x] สร้างระบบ Pattern Matching พื้นฐาน
- [x] ทำนายทิศทางราคาหุ้นวันถัดไป (N+1) จาก Historical Data
- [x] รองรับตลาดไทย (SET) เป็นตลาดแรก
- [x] แนวคิด "History Repeat Itself" — ถ้า Pattern เคยเกิดซ้ำ → ทายว่าวันถัดไปจะเป็นยังไง

---

## Phase 2: Multi-Market & Enhancement (V2.0 — Jan 2026)
- [x] ขยายรองรับหลายตลาด (SET, NASDAQ)
- [x] เพิ่ม Multi-timeframe Support
- [x] สร้าง Scanner สำหรับค้นหาสัญญาณ (scanner.py, scanner_v2.py)
- [x] สร้าง Batch Processing Pipeline (pipeline/)

---

## Phase 3: Statistical Engine (V3.0–V3.4 — Jan–Feb 2026)

### V3.0 — Statistical Filtering
- [x] เพิ่มการกรองด้วยสถิติ (Statistical Filtering)
- [x] ใช้ Dynamic Threshold แทน Fixed Threshold

### V3.1 — Strict Logic
- [x] Strict Logic — วันไหนไม่เกิน threshold → streak ขาดทันที (ไม่ข้าม FLAT)
- [x] แก้ Probability Calculation: `Prob = dominant / (up + down)` ไม่รวม FLAT
- [x] เพิ่ม Avg_Return metric
- [x] เพิ่ม Avg_Intensity metric
- [x] สร้าง Unified Report Tool

### V3.2 — Confidence & Risk Scoring
- [x] เพิ่มระบบให้คะแนนความเชื่อมั่น (Confidence Score)
- [x] เพิ่มระบบให้คะแนนความเสี่ยง (Risk Score)

### V3.3 — Performance Logging
- [x] สร้าง Performance Logging System (`performance_log.csv`)
- [x] 4-Table Report System:
  - [x] Table 1: Thai Strict (Prob > 60%, RR > 2.0)
  - [x] Table 2: Thai Balanced (Prob > 60%, 1.5 < RR ≤ 2.0)
  - [x] Table 3: International Observation (Prob > 55%, RR > 1.1)
  - [x] Table 4: International Sensitivity (Prob > 50%, 0.5 < RR ≤ 1.1)

### V3.4 — Dynamic Pattern + Cache
- [x] Dynamic Pattern Detection — Scan pattern lengths 1–8 days (แทน Fixed 4 days)
- [x] Smart Cache System — ลด API calls 99% (5000 bars → 50 bars incremental)
- [x] CSV-based caching (data/cache/) — portable, debug ง่าย
- [x] Adaptive Split สำหรับหุ้นใหม่ (IPO)

---

## Phase 4: Production & Consensus (V4.0–V4.5 — Feb 2026)

### V4.0 — Real-time Alert
- [x] วางแผนระบบ Real-time Alert

### V4.1 — Production-Ready
- [x] Production Mode — Entry at next bar's OPEN (realistic, not current close)
- [x] Slippage (market-specific)
- [x] Commission (market-specific)
- [x] Gap Risk (Stop Loss can be worse due to gap)
- [x] Liquidity Filter (skip low-volume days)
- [x] Display Enhancement — Count prominent (Width 12, Comma formatting)
- [x] Display Enhancement — All passing stocks displayed (ไม่มี .head() limit)
- [x] Display Enhancement — Sorting by Prob% (Descending)
- [x] Statistical Reliability — Count ≥ 30 for Thai (Central Limit Theorem)
- [x] Statistical Reliability — Count ≥ 15 for US/China/Taiwan

### V4.1 — Intraday Metals
- [x] Gold 30min (OANDA) — TREND_FOLLOWING engine (Breakout Logic)
- [x] Gold 15min (OANDA) — TREND_FOLLOWING engine
- [x] Silver 30min (OANDA) — MEAN_REVERSION engine (Fakeout Logic)
- [x] Silver 15min (OANDA) — MEAN_REVERSION engine
- [x] Separated rolling windows สำหรับ 15min and 30min
- [x] Separated max_hold สำหรับ 15min and 30min
- [x] Market-specific min_prob, min_stats, fixed_threshold สำหรับ Metals
- [x] Separate display criteria สำหรับ 15min and 30min

### V4.4 — Aggregate Voting
- [x] Consensus Voting — รวมผลจาก sub-patterns ทั้งหมด
- [x] Dynamic Streak Extraction (Overlapping Sliding Window)
- [x] Gatekeeper Filter — Count ≥ 30, Prob ≥ 50%
- [x] Winner-Takes-All logic — ฝั่งที่ชนะมากกว่าเป็นผลลัพธ์

### V4.5 — Market-Specific Thresholds
- [x] Thai: 1.0% threshold (Mean Reversion)
- [x] US: 0.6% threshold (Trend Following)
- [x] China: 0.5% threshold (ลดจาก 1.2% → Early Entry)
- [x] Taiwan: 0.5% threshold (ลดจาก 1.0% → Accumulation)
- [x] China: SMA50 + FOMO Filter (Volume Ratio < 3.0)
- [x] Taiwan: ADX > 20
- [x] US: ADX > 20 + Quality Gate (Prob ≥ 60%)

---

## Phase 5: Philosophy Shift — Pure Statistics (V6.0–V6.1 — Feb 2026)

### V6.0 — Indicator-based (ทดลอง)
- [x] ทดลอง ADX Filter (ADX ≥ 20)
- [x] ทดลอง SMA50 Filter (Price > SMA50)
- [x] ทดลอง Volume Ratio Filter (VR > 0.5)
- [x] เพิ่ม Trailing Stop Loss
- [x] เพิ่ม Take Profit
- [x] สรุป: กรองได้ดีจริง แต่ **ซับซ้อนเกินไป + ไม่ตรงกับแนวคิดเดิม**

### V6.1 — Simplified (ตัดสินใจ)
- [x] ลบ ADX Filter
- [x] ลบ SMA50 Filter
- [x] ลบ Volume Ratio Filter
- [x] ลบ RSI
- [x] ลบ Trailing Stop Loss
- [x] ลบ Take Profit
- [x] ลบ ATR Multiplier
- [x] ลบ Max Hold Days
- [x] กลับสู่ Pattern Matching จาก History Statistics
- [x] กลับสู่ 1-Day Exit (N+1)
- [x] Gatekeeper: Prob > 60% และ RRR > 1.2

---

## Phase 6: Risk Management & Balance (V10.0–V10.1 — Feb 2026)

### V10.0 — Balanced Markets
- [x] Threshold multiplier: 0.9 for International (was 1.25)
- [x] ผลลัพธ์: 10–13x more trades with minimal accuracy loss
- [x] Trailing Stop enabled
- [x] Stop Loss (market-specific)
- [x] Take Profit (market-specific)

### V10.1 — All Markets Balanced
- [x] Thai threshold_multiplier: 1.25 → 1.0
- [x] Thai floor: 1.0% → 0.7%
- [x] Thai min_stats: 30 → 25
- [x] Thai gatekeeper Prob: 55% → 53%
- [x] Thai RM SL: 2.0% → 1.5%
- [x] Thai RM TP: 4.0% → 3.5%
- [x] Trailing Stop: Enabled for all markets
- [x] All Markets Aligned — ใช้ Logic เดียวกัน

---

## Phase 7: International Market Optimization (V12.0–V13.2 — Feb 2026)

### V12.0 — Taiwan Optimization
- [x] แยก Logic ไต้หวัน (`is_tw_market_early`, `is_tw_market`)
- [x] threshold_multiplier: 0.9 → 0.85
- [x] min_stats: 25 → 20
- [x] floor: 0.5% → 0.4%
- [x] prob filter: 53% → 51%
- [x] TP: 3.5% → 4.0% (RRR 2.67)
- [x] เกณฑ์: Prob ≥ 50%, RRR ≥ 1.05, Count ≥ 15
- [x] ผลลัพธ์: 4 stocks passing (DELTA, LARGAN, MEDIATEK, QUANTA)

### V12.1 — Taiwan Quality
- [x] SL: 1.5% → 1.2% (tight SL)
- [x] TP: 4.0% → 5.0% (RRR 4.17)
- [x] Max Hold: 5 → 7 วัน
- [x] Trail Activate: 1.5% → 1.0%
- [x] Trail Distance: 50% → 40%
- [x] threshold_multiplier: 0.85 → 0.9
- [x] min_stats: 20 → 25
- [x] prob filter: 51% → 53%
- [x] เกณฑ์: Prob ≥ 53%, RRR ≥ 1.3, Count 25–150
- [x] ผลลัพธ์: MEDIATEK (Prob 62.5%, RRR 1.45, Count 40)

### V12.2 — RRR Optimization
- [x] SL: 1.2% → 1.0% (tighter)
- [x] TP: 5.0% → 6.5% (wider)
- [x] Max Hold: 7 → 10 วัน
- [x] Trail Distance: 40% → 30% (let profits run)
- [x] Prob Filter: 53% → 52%
- [x] ผลลัพธ์: 2 stocks (MEDIATEK RRR 1.76, HON-HAI RRR 1.42)

### V12.3 — Count Optimization
- [x] min_prob: 52.0% → 51.5%
- [x] n_bars: 2000 → 2500 (เพิ่ม historical data)
- [x] ผลลัพธ์: DELTA (Prob 70.9%, RRR 1.89, Count 55)

### V12.4 — Taiwan Real-World Ready
- [x] min_prob: 51.5% → 51.0%
- [x] RRR Requirement: 1.3 → 1.25
- [x] n_bars: 2500 (คงเดิม)
- [x] ทดสอบ Option 3 (RRR 1.15, Count 300): ❌ ไม่เพิ่มหุ้น
- [x] ทดสอบ Option B (RRR 1.25, Count 400): ⚠️ over-trading risk
- [x] เลือก Option A (RRR 1.25, Count 150) — Best for real trading
- [x] ผลลัพธ์: DELTA (Prob 71.4%, RRR 1.95) + QUANTA (Prob 62.5%, RRR 1.41)
- [x] Avg Prob%: 66.95%, Avg RRR: 1.68, Total Trades: 131

### V13.0 — China Market Focus
- [x] Prob Requirement: 55% → 53%
- [x] RRR Requirement: 1.2 → 1.0
- [x] Count Requirement: ≥ 15 (คงเดิม)
- [x] ผลลัพธ์: 3 stocks (MEITUAN 76.9%, BYD 59.1%, JD-COM 54.2%)

### V13.1 — China Increase Stocks
- [x] RRR ≥ 1.0 → 0.95
- [x] Count ≥ 15 → 10
- [x] TP: 3.5% → 4.5%
- [x] Max Hold: 5 → 6 days
- [x] Gatekeeper min_prob: 53.0% → 51.0%
- [x] ผลลัพธ์: 4 stocks (+ LI-AUTO Prob 80.0%)

### V13.2 — China RM Optimization
- [x] SL: 1.5% → 1.2% (tighter)
- [x] TP: 4.5% → 5.5% (higher)
- [x] RRR: 3.0 → 4.58 (theoretical)
- [x] Max Hold: 6 → 8 days
- [x] Trail Activate: 1.5% → 1.0%
- [x] Trail Distance: 50% → 40%
- [x] Target RRR actual: 1.11 → 1.5+

---

## Phase 8: Final Production (V5.0–V5.0.1 — Feb–Mar 2026)
- [x] แก้ Probability Overflow (ค่าเกิน 100%) — Cap at 100%
- [x] เปลี่ยน Probability Calculation จาก Average Consensus → Total Weighted Probability
  - [x] เดิม: `np.mean` ของ individual sub-pattern win rates
  - [x] ใหม่: `sum(winning_counts) / sum(total_events)` จาก winning-side patterns
- [x] แก้ Engine Key Mismatch — Gold: `TREND_FOLLOWING` → `TREND_MOMENTUM` ใน config.py
- [x] แก้ Engine Key Mismatch — Gold: `TREND_FOLLOWING` → `TREND_MOMENTUM` ใน backtest.py
- [x] แก้ Backtest Engine Pass-through — เพิ่ม `engine` kwarg ใน `backtest_all()`
- [x] Full Data Reconstruction — Backfill ข้อมูลทั้งหมดตั้งแต่ 2 ก.พ.
- [x] Realized P/L Synchronization — ใช้ `realized_change` (Scan Price → Target Price) เป็นมาตรฐาน
- [x] Standardized Filters — บังคับ Stats ≥ 30, Prob ≥ 50% ทุก Dashboard และ Script
- [x] Pattern Length — อัพเดทเอกสาร 3–8 → 1–8 days ให้ตรงกับ `min_len=1`
- [x] Market Group Count — อัพเดทเอกสาร "5 market groups" → "8 asset groups covering 5 markets"

---

## Phase 9: Codebase Cleanup & Documentation (Mar 2026)

### Code Cleanup
- [x] ลบ 11 old core modules (predictor.py, data_fetcher.py, stats_analyzer.py, scoring.py, indicators.py, visualizer.py, data_utils.py, pattern_stats.py, market_classifier.py, core/config.py, core/utils.py)
- [x] ลบ 5 unused engine logic files (thai/us/china/hk/taiwan_logic_threshold_only.py)
- [x] ลบ pipeline/ directory (batch_processor, bulk_data_loader, data_cache, data_cleaner, data_updater)
- [x] ลบ utils/ directory (cache_manager)
- [x] ลบ scripts/filters/ directory (market_regime, momentum, multi_timeframe, sector_rotation)
- [x] ลบ scripts/analysis/ directory (calculate_performance, forward_testing_report, market_sentiment, mock_enhanced_report, optimal_filtering_logic, validate_global_strategy, verify_history_detail, view_accuracy)
- [x] ลบ 4 shim scripts (scripts/check_forward_testing.py, daily_forecast_dashboard.py, view_report.py, calculate_performance.py)
- [x] ลบ debug/temp scripts (debug_pnl.py, market_regime.py, simulate_equity_curves.py)
- [x] Inline `calculate_adx()` ใน trend_engine.py หลังลบ core/indicators.py

### Data Cleanup
- [x] ลบ data/stocks/ (200+ old parquet files)
- [x] ลบ data/plots/ (17 old PNG charts)
- [x] ลบ data/logs/ (individual stock logs)
- [x] ลบ data/recovered_forecasts/ (12 recovery files)
- [x] ลบ 25+ old analysis CSVs (Master_Pattern_Stats*, backtest_results, stock_stats, optimization_results, etc.)
- [x] ลบ 13+ old analysis MDs (country_thresholds, data_flow_analysis, gatekeeper_comparison, thai_market_analysis, etc.)
- [x] ลบ 4 old PNGs from data/ (equity_curve_verification, market_equity_curves, etc.)
- [x] ลบ old data text files (test_write.txt, system_assessment_v11.txt, all_thai_stocks.txt)

### Logs & Config Cleanup
- [x] ลบ 12 old log files (threshold_analysis, trade_history backups, dashboard dumps, etc.)
- [x] ลบ backup_20260218_200031/ directory
- [x] ลบ results/ directory (old scanner JSON reports)
- [x] ลบ output/ directory (old equity charts)
- [x] ลบ plots/ directory (old metrics charts)
- [x] ลบ cache/ directory (root-level, ไม่ใช่ data/cache/)
- [x] ลบ .vscode/ directory
- [x] ลบ temp_dash2.txt, temp_dashboard.txt

### Security
- [x] ลบ credentials จริง (email + password) ออกจาก .env
- [x] แทนด้วย placeholder values
- [x] ตรวจสอบแล้ว .env ไม่เคยถูก commit ลง git history
- [x] อัพเดท .gitignore ให้ครอบคลุม (data/cache/, logs/*.csv, .env, IDE files)

### Dependencies
- [x] ลบ matplotlib (ไม่มี import ในโค้ด)
- [x] ลบ seaborn (ไม่มี import ในโค้ด)
- [x] ลบ beautifulsoup4 (ไม่มี import ในโค้ด)
- [x] ลบ python-dateutil (ไม่มี import ในโค้ด)
- [x] ลบ websocket-client (ไม่มี import ในโค้ด — เป็น dependency ของ tvDatafeed)
- [x] อัพเดท requirements.txt เหลือ 7 libraries ที่ใช้จริง (pandas, numpy, tvDatafeed, python-dotenv, requests, tabulate, pytz)

### Documentation
- [x] เขียน README ใหม่ทั้งหมด (~350 บรรทัด)
  - [x] Overview & Supported Markets
  - [x] Project Structure tree
  - [x] Installation (4 steps)
  - [x] Configuration parameters
  - [x] Daily Usage guide
  - [x] CLI Command Reference (Main, Reports, Backtest, Backfill, Maintenance)
  - [x] Core Engines explanation (MeanReversion vs TrendMomentum)
  - [x] System Architecture ASCII diagram
  - [x] Libraries & Dependencies table (7 libraries)
  - [x] Technical Documentation links
- [x] อัพเดท README ลบ reference ไฟล์ที่ถูกลบ (distribution_analysis.py, probability_threshold_analysis.py)
- [x] SCRIPTS_FINAL_AUDIT_V4.4.md ลบ (outdated)

### Verification
- [x] All 11 core modules import OK
- [x] All 14 scripts syntax check passed
- [x] All README .py references point to existing files
- [x] All 8 engine mappings correct (MEAN_REVERSION × 6, TREND_MOMENTUM × 2)
- [x] .env contains placeholder only (no real credentials)
- [x] .gitignore covers all sensitive files

### Git
- [x] Commit: V5.0.1 Major codebase cleanup
- [x] Commit: chore: Clean dependencies
- [x] Commit: docs: Update Details Checklist
- [x] Force push จาก version-5 branch → main
- [x] GitHub main synced กับ local ตรงกัน

---

## 📊 Final Statistics

| Metric | Value |
|:--|:--|
| Total Forecasts | **6,689** |
| Unique Symbols | **227** |
| Trading Days | **43** (Jan 2 – Mar 6, 2026) |
| Markets | **5** (SET, NASDAQ, HKEX, TWSE, OANDA) |
| Asset Groups | **8** |
| Git Commits | **77** |
| Python Files (Final) | **18** |
| Engines | **2** (MeanReversion, TrendMomentum) |
| Libraries | **7** (pandas, numpy, tvDatafeed, dotenv, requests, tabulate, pytz) |

---

## 💡 Key Lessons Learned

1. **Pure Statistics > Indicators** — ทดลอง ADX, SMA50, Volume แล้วไม่เพิ่มคุณภาพ แต่เพิ่มความซับซ้อน
2. **Balance is Key** — เข้มงวดเกินไป = สัญญาณน้อย, หลวมเกินไป = noise เยอะ
3. **Production Realism** — Backtest ที่ไม่รวม Slippage/Commission ให้ตัวเลขสวยแต่ไม่จริง
4. **Cache = Speed** — Smart Cache ลดเวลารันจาก 30 นาทีเหลือ 19 วินาที
5. **Clean Code Matters** — ลบไฟล์ที่ไม่ใช้, แยก Engine ชัดเจน, README ที่ดี ทำให้ maintain ง่าย
6. **Systematic Version Control** — แยก version ชัดเจน, เก็บประวัติทุก iteration ช่วยย้อนกลับได้
7. **Market-Specific Tuning** — แต่ละตลาดมี characteristics ต่างกัน ใช้ parameter ชุดเดียวไม่ได้

---

**Last Updated:** March 6, 2026  
**Final Version:** V5.0.1  
**Status:** ✅ Production-Ready — Clean & Documented
