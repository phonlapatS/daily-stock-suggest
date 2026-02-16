# รายงานไฟล์ .py ที่ไม่ได้ใช้แล้ว

> **วันที่:** 2026-02-XX  
> **สถานะ:** วิเคราะห์เสร็จสิ้น

---

## 📊 สรุปผลการวิเคราะห์

- **Total Files:** 168 ไฟล์
- **Core System:** 15 ไฟล์ (ใช้จริง)
- **Analysis Tools:** 7 ไฟล์ (ยังใช้ได้)
- **Test Scripts:** 3 ไฟล์ (ยังใช้ได้)
- **ควรลบ:** 54 ไฟล์ (ไม่ใช้แล้วจริงๆ)
- **ต้องตรวจสอบ:** 89 ไฟล์ (Unknown + Plotting)

---

## ✅ ไฟล์ที่ใช้จริง (Core System)

### Main Entry Points
- `main.py` - Main entry point
- `config.py` - Configuration
- `processor.py` - Pattern processor

### Core Modules
- `core/data_cache.py` - Data caching
- `core/performance.py` - Performance logging
- `core/market_time.py` - Market time utilities
- `core/engines/base_engine.py` - Base engine
- `core/engines/reversion_engine.py` - Mean reversion engine
- `core/engines/trend_engine.py` - Trend momentum engine

### Scripts (ใช้งานจริง)
- `scripts/backtest.py` - Backtest engine
- `scripts/calculate_metrics.py` - Calculate metrics
- `scripts/stock_logger.py` - Stock logger
- `scripts/incremental_update.py` - Incremental update
- `scripts/intraday_runner.py` - Intraday runner
- `scripts/market_sentiment.py` - Market sentiment

---

## 🔧 ไฟล์ที่ยังใช้ได้ (Analysis Tools)

- `scripts/assess_system_status.py` - System status assessment
- `scripts/analyze_statistical_reliability.py` - Statistical reliability
- `scripts/analyze_indicator_vs_risk_management.py` - Indicator vs RM comparison
- `scripts/analyze_metrics_by_country.py` - Metrics by country
- `scripts/plot_equity.py` - Equity plotting
- `scripts/plot_markets_from_metrics.py` - Market plotting
- `scripts/split_trade_history_by_market.py` - Split trade history

---

## 🧪 ไฟล์ที่ยังใช้ได้ (Test Scripts)

- `scripts/verify_failed_symbols.py` - Verify failed symbols
- `scripts/research_failed_symbols.py` - Research failed symbols
- `scripts/test_risk_management.py` - Test risk management

---

## ❌ ไฟล์ที่ควรลบ (54 ไฟล์)

### Old Test Scripts (35 ไฟล์)

**Threshold Testing (Old Versions):**
- `scripts/test_old_threshold_simple.py`
- `scripts/test_old_threshold_thai.py`
- `scripts/test_thai_old_threshold.py`
- `scripts/backtest_old_threshold_separate.py`
- `scripts/backtest_thai_with_old_threshold.py`
- `scripts/run_old_threshold_backtest.py`

**Comparison Scripts (Old Results):**
- `scripts/compare_old_new_results.py`
- `scripts/compare_old_vs_new_results.py`
- `scripts/compare_threshold_results.py`
- `scripts/create_comparison_table.py`
- `scripts/create_full_comparison_table.py`
- `scripts/create_threshold_comparison_table.py`

**Analysis Scripts (Old Criteria):**
- `scripts/analyze_old_vs_new_criteria.py`
- `scripts/analyze_thai_market_changes.py`
- `scripts/analyze_data_flow.py`
- `scripts/explain_tpipp_mystery.py`
- `scripts/check_super.py`

**Hybrid Backtest Testing:**
- `scripts/test_hybrid_backtest.py`
- `scripts/test_hybrid_backtest_v2.py`
- `scripts/test_hybrid_backtest_v3.py`
- `scripts/test_hybrid_backtest_v4.py`
- `scripts/test_hybrid_backtest_v5.py`

**Other Test Scripts:**
- `scripts/test_all_filters.py`
- `scripts/test_comprehensive_v6.py`
- `scripts/test_filter_variants.py`
- `scripts/test_global_optimization.py`
- `scripts/test_improved_strategies.py`
- `scripts/test_international_markets.py`
- `scripts/test_inverse_logic.py`
- `scripts/test_multi_day_holding.py`
- `scripts/test_optimized_classifier.py`
- `scripts/test_shadow_mode.py`
- `scripts/test_simplified_system.py`
- `scripts/test_trailing_stop_rrr.py`
- `scripts/test_us_long_only.py`

### Old Analysis Scripts (19 ไฟล์)

**Market Analysis:**
- `scripts/analyze_china.py`
- `scripts/analyze_china_turnover.py`
- `scripts/analyze_us_paradox.py`
- `scripts/analyze_market_specific_logic.py`
- `scripts/deep_analysis_international.py`
- `scripts/quick_intl_analysis.py`

**Metrics Analysis:**
- `scripts/analyze_backtest_results.py`
- `scripts/analyze_count_impact.py`
- `scripts/analyze_display_improvements.py`
- `scripts/analyze_logic_engine_comprehensive.py`
- `scripts/analyze_mentor_comments_status.py`
- `scripts/analyze_stock_counts_by_country.py`
- `scripts/analyze_trade_direction.py`

**RRR Analysis:**
- `scripts/analyze_rrr_calculation.py`
- `scripts/analyze_rrr_potential.py`

**Other Analysis:**
- `scripts/analyze_honest_timestop.py`
- `scripts/analyze_metals_volatility.py`
- `scripts/debug_china_stats.py`
- `scripts/diagnose_market_loss.py`

---

## 📊 ไฟล์ที่ต้องตรวจสอบ (89 ไฟล์)

### Plotting Scripts (9 ไฟล์) - ไม่ได้ใช้แล้ว
- `scripts/generate_real_equity_plots.py`
- `scripts/plot_comparative_equity.py`
- `scripts/plot_elite_from_metrics.py`
- `scripts/plot_fair_comparison.py`
- `scripts/plot_market_comparison.py`
- `scripts/plot_metrics.py`
- `scripts/plot_stock_comparison_detailed.py`
- `scripts/temp_plot_user_request.py`
- `scripts/visualize_equity.py`

### Unknown Files (80 ไฟล์) - ต้องตรวจสอบ

**Core Modules (บางไฟล์ยังใช้):**
- ✅ `core/data_fetcher.py` - ใช้
- ✅ `core/predictor.py` - ใช้
- ✅ `core/stats_analyzer.py` - ใช้
- ✅ `core/utils.py` - ใช้
- ✅ `core/visualizer.py` - ใช้
- ❌ `core/__init__.py` - ไม่ใช้
- ❌ `core/config.py` - ไม่ใช้ (มี config.py ที่ root)
- ❌ `core/dynamic_streak_v2.py` - ไม่ใช้
- ❌ `core/indicators.py` - ไม่ใช้ (V6.1 ลบ indicator)
- ❌ `core/market_classifier.py` - ไม่ใช้
- ❌ `core/pattern_stats.py` - ไม่ใช้
- ❌ `core/scoring.py` - ไม่ใช้

**Pipeline (บางไฟล์ยังใช้):**
- ✅ `pipeline/data_cache.py` - ใช้
- ❌ `pipeline/__init__.py` - ไม่ใช้
- ❌ `pipeline/batch_processor.py` - ไม่ใช้
- ❌ `pipeline/bulk_data_loader.py` - ไม่ใช้
- ❌ `pipeline/data_cleaner.py` - ไม่ใช้
- ❌ `pipeline/data_updater.py` - ไม่ใช้

**Scripts (Unknown):**
- ❌ `compare_sd_thresholds.py` - ไม่ใช้ (root level)
- ❌ `scripts/__init__.py` - ไม่ใช้
- ❌ `scripts/analyze_unused_files.py` - ไม่ใช้ (script นี้เอง)
- ❌ `scripts/backtest_international_focus.py` - ไม่ใช้
- ❌ `scripts/backtest_intl_stocks.py` - ไม่ใช้
- ❌ `scripts/backtest_metals.py` - ไม่ใช้
- ❌ `scripts/backtest_metals_advanced.py` - ไม่ใช้
- ❌ `scripts/backtest_metals_intraday.py` - ไม่ใช้
- ❌ `scripts/backtest_with_trailing_stop.py` - ไม่ใช้
- ❌ `scripts/benchmark_auto_strategy.py` - ไม่ใช้
- ❌ `scripts/benchmark_loader.py` - ไม่ใช้
- ❌ `scripts/benchmark_us_strategy.py` - ไม่ใช้
- ❌ `scripts/calc_debug.py` - ไม่ใช้
- ❌ `scripts/calculate_metrics_streak.py` - ไม่ใช้
- ❌ `scripts/calculate_performance.py` - ไม่ใช้
- ❌ `scripts/check_gold_silver.py` - ไม่ใช้
- ❌ `scripts/compare_filtering_results.py` - ไม่ใช้
- ❌ `scripts/compare_tables.py` - ไม่ใช้
- ❌ `scripts/compare_thresholds.py` - ไม่ใช้
- ❌ `scripts/compare_trailing_stop_results.py` - ไม่ใช้
- ❌ `scripts/compare_us_short_logic.py` - ไม่ใช้
- ❌ `scripts/compare_us_strategy.py` - ไม่ใช้
- ❌ `scripts/fact_check.py` - ไม่ใช้
- ❌ `scripts/fetch_intraday_metals.py` - ไม่ใช้
- ❌ `scripts/fetch_missing_cache.py` - ไม่ใช้
- ❌ `scripts/filter_signals.py` - ไม่ใช้
- ❌ `scripts/forward_logger_v2.py` - ไม่ใช้
- ❌ `scripts/forward_test_logger.py` - ไม่ใช้
- ❌ `scripts/forward_testing_report.py` - ไม่ใช้
- ❌ `scripts/full_threshold_analysis.py` - ไม่ใช้
- ❌ `scripts/health_check.py` - ไม่ใช้
- ❌ `scripts/improve_rrr_with_trailing_stop.py` - ไม่ใช้
- ❌ `scripts/improve_us_market_trend_following.py` - ไม่ใช้
- ❌ `scripts/improved_filtering_logic.py` - ไม่ใช้
- ❌ `scripts/improved_filtering_mentor_approved.py` - ไม่ใช้
- ❌ `scripts/main_stats_extraction.py` - ไม่ใช้
- ❌ `scripts/market_regime.py` - ไม่ใช้
- ✅ `scripts/master_scanner.py` - ใช้
- ❌ `scripts/optimal_filtering_logic.py` - ไม่ใช้
- ❌ `scripts/optimize_trailing_stop_parameters.py` - ไม่ใช้
- ❌ `scripts/optimized_threshold_finder.py` - ไม่ใช้
- ❌ `scripts/run_backtest_analysis.py` - ไม่ใช้
- ❌ `scripts/run_backtest_detailed.py` - ไม่ใช้
- ❌ `scripts/show_backtest_results.py` - ไม่ใช้
- ❌ `scripts/simulate_equity_curves.py` - ไม่ใช้
- ❌ `scripts/stateless_scanner.py` - ไม่ใช้
- ❌ `scripts/test_gatekeeper_comparison.py` - ไม่ใช้
- ❌ `scripts/threshold_comparison.py` - ไม่ใช้
- ❌ `scripts/tune_metals_winrate.py` - ไม่ใช้
- ❌ `scripts/validate_global_strategy.py` - ไม่ใช้
- ❌ `scripts/verify_prediction.py` - ไม่ใช้
- ❌ `scripts/verify_rrr_calculation.py` - ไม่ใช้
- ❌ `scripts/verify_threshold.py` - ไม่ใช้
- ❌ `scripts/view_accuracy.py` - ไม่ใช้
- ❌ `scripts/view_report.py` - ไม่ใช้

**Filters (ไม่ใช้):**
- ❌ `scripts/filters/__init__.py` - ไม่ใช้
- ❌ `scripts/filters/market_regime.py` - ไม่ใช้
- ❌ `scripts/filters/momentum.py` - ไม่ใช้
- ❌ `scripts/filters/multi_timeframe.py` - ไม่ใช้
- ❌ `scripts/filters/sector_rotation.py` - ไม่ใช้

**Utils:**
- ✅ `utils/cache_manager.py` - ใช้
- ❌ `utils/__init__.py` - ไม่ใช้

---

## 🗑️ สรุปไฟล์ที่ควรลบ

### แนวทางที่ 1: ลบไฟล์ที่แน่ใจว่าไม่ใช้แล้ว (54 ไฟล์)

**Old Test Scripts (35 ไฟล์):**
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_old_threshold`
- ทุกไฟล์ที่ขึ้นต้นด้วย `backtest_old_threshold`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_hybrid_backtest`
- ทุกไฟล์ที่ขึ้นต้นด้วย `compare_old`
- ทุกไฟล์ที่ขึ้นต้นด้วย `create_comparison`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_old_vs_new`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_thai_market_changes`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_data_flow`
- ทุกไฟล์ที่ขึ้นต้นด้วย `explain_tpipp`
- ทุกไฟล์ที่ขึ้นต้นด้วย `check_super`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_all_filters`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_comprehensive`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_filter_variants`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_global_optimization`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_improved_strategies`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_international_markets`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_inverse_logic`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_multi_day_holding`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_optimized_classifier`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_shadow_mode`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_simplified_system`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_trailing_stop_rrr`
- ทุกไฟล์ที่ขึ้นต้นด้วย `test_us_long_only`

**Old Analysis Scripts (19 ไฟล์):**
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_china`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_us_paradox`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_backtest_results`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_count_impact`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_display_improvements`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_logic_engine_comprehensive`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_mentor_comments_status`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_stock_counts_by_country`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_trade_direction`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_rrr_calculation`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_rrr_potential`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_honest_timestop`
- ทุกไฟล์ที่ขึ้นต้นด้วย `analyze_metals_volatility`
- ทุกไฟล์ที่ขึ้นต้นด้วย `debug_china_stats`
- ทุกไฟล์ที่ขึ้นต้นด้วย `deep_analysis_international`
- ทุกไฟล์ที่ขึ้นต้นด้วย `diagnose_market_loss`
- ทุกไฟล์ที่ขึ้นต้นด้วย `quick_intl_analysis`

### แนวทางที่ 2: ลบไฟล์ที่ต้องตรวจสอบเพิ่มเติม (89 ไฟล์)

**Plotting Scripts (9 ไฟล์):**
- ทุกไฟล์ที่ขึ้นต้นด้วย `plot_` (ยกเว้น `plot_equity.py` และ `plot_markets_from_metrics.py`)
- `scripts/generate_real_equity_plots.py`
- `scripts/temp_plot_user_request.py`
- `scripts/visualize_equity.py`

**Core Modules (ไม่ใช้):**
- `core/__init__.py`
- `core/config.py` (มี config.py ที่ root แล้ว)
- `core/dynamic_streak_v2.py`
- `core/indicators.py` (V6.1 ลบ indicator แล้ว)
- `core/market_classifier.py`
- `core/pattern_stats.py`
- `core/scoring.py`

**Pipeline (ไม่ใช้):**
- `pipeline/__init__.py`
- `pipeline/batch_processor.py`
- `pipeline/bulk_data_loader.py`
- `pipeline/data_cleaner.py`
- `pipeline/data_updater.py`

**Scripts (Unknown - ไม่ใช้):**
- `compare_sd_thresholds.py` (root level)
- `scripts/__init__.py`
- `scripts/analyze_unused_files.py` (script นี้เอง)
- และอื่นๆ อีก 60+ ไฟล์

---

## 💡 คำแนะนำ

### ขั้นตอนที่ 1: ลบไฟล์ที่แน่ใจว่าไม่ใช้แล้ว (54 ไฟล์)
1. ลบ Old Test Scripts (35 ไฟล์)
2. ลบ Old Analysis Scripts (19 ไฟล์)

### ขั้นตอนที่ 2: ตรวจสอบไฟล์ที่ต้องตรวจสอบเพิ่มเติม (89 ไฟล์)
1. ตรวจสอบ Plotting Scripts (9 ไฟล์) - ถ้าไม่ใช้แล้วให้ลบ
2. ตรวจสอบ Core Modules (7 ไฟล์) - ถ้าไม่ใช้แล้วให้ลบ
3. ตรวจสอบ Pipeline (5 ไฟล์) - ถ้าไม่ใช้แล้วให้ลบ
4. ตรวจสอบ Scripts (68 ไฟล์) - ถ้าไม่ใช้แล้วให้ลบ

### ขั้นตอนที่ 3: จัดแจงไฟล์ให้เรียบร้อย
1. ย้ายไฟล์ที่ยังใช้ไปไว้ในโฟลเดอร์ที่เหมาะสม
2. สร้างโฟลเดอร์ `scripts/archive/` สำหรับไฟล์ที่ยังไม่แน่ใจ
3. สร้างโฟลเดอร์ `scripts/deprecated/` สำหรับไฟล์ที่ deprecated

---

## 📝 หมายเหตุ

- ไฟล์ที่ถูก mark เป็น "ใช้" อาจจะถูก import แบบ indirect (ผ่าน module อื่น)
- ควรตรวจสอบด้วยมือก่อนลบไฟล์ที่สำคัญ
- ควร backup ก่อนลบไฟล์จำนวนมาก

---

**Last Updated:** 2026-02-XX  
**Status:** ✅ Ready for Review

