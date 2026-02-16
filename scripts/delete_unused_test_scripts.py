#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
delete_unused_test_scripts.py - ลบ test scripts ที่ไม่เกี่ยวกับโปรเจ็ค
=====================================================================
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test scripts ที่ควรลบ (ไม่เกี่ยวกับโปรเจ็ค - เอาไว้เช็คเฉยๆ)
TEST_SCRIPTS_TO_DELETE = [
    # Old Threshold Testing
    'scripts/test_old_threshold_simple.py',
    'scripts/test_old_threshold_thai.py',
    'scripts/test_thai_old_threshold.py',
    'scripts/backtest_old_threshold_separate.py',
    'scripts/backtest_thai_with_old_threshold.py',
    'scripts/run_old_threshold_backtest.py',
    
    # Hybrid Backtest Testing
    'scripts/test_hybrid_backtest.py',
    'scripts/test_hybrid_backtest_v2.py',
    'scripts/test_hybrid_backtest_v3.py',
    'scripts/test_hybrid_backtest_v4.py',
    'scripts/test_hybrid_backtest_v5.py',
    
    # Comparison Scripts
    'scripts/compare_old_new_results.py',
    'scripts/compare_old_vs_new_results.py',
    'scripts/compare_threshold_results.py',
    'scripts/create_comparison_table.py',
    'scripts/create_full_comparison_table.py',
    'scripts/create_threshold_comparison_table.py',
    
    # Other Test Scripts
    'scripts/test_all_filters.py',
    'scripts/test_comprehensive_v6.py',
    'scripts/test_filter_variants.py',
    'scripts/test_global_optimization.py',
    'scripts/test_improved_strategies.py',
    'scripts/test_international_markets.py',
    'scripts/test_inverse_logic.py',
    'scripts/test_multi_day_holding.py',
    'scripts/test_optimized_classifier.py',
    'scripts/test_shadow_mode.py',
    'scripts/test_simplified_system.py',
    'scripts/test_trailing_stop_rrr.py',
    'scripts/test_us_long_only.py',
    
    # Analysis Scripts (Old Criteria)
    'scripts/analyze_old_vs_new_criteria.py',
    'scripts/analyze_thai_market_changes.py',
    'scripts/analyze_data_flow.py',
    'scripts/explain_tpipp_mystery.py',
    'scripts/check_super.py',
]

def delete_files(file_list):
    """ลบไฟล์"""
    deleted = []
    not_found = []
    errors = []
    
    for file_path in file_list:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                deleted.append(file_path)
                print(f"✅ ลบแล้ว: {file_path}")
            except Exception as e:
                errors.append((file_path, str(e)))
                print(f"❌ ไม่สามารถลบได้: {file_path} - {e}")
        else:
            not_found.append(file_path)
            print(f"⚠️  ไม่พบไฟล์: {file_path}")
    
    return deleted, not_found, errors

def main():
    print("\n" + "="*120)
    print("🗑️  ลบ Test Scripts ที่ไม่เกี่ยวกับโปรเจ็ค")
    print("="*120)
    
    print(f"\n📋 ไฟล์ที่จะลบ: {len(TEST_SCRIPTS_TO_DELETE)} ไฟล์\n")
    
    # แสดงรายการไฟล์ที่จะลบ
    for i, file_path in enumerate(TEST_SCRIPTS_TO_DELETE, 1):
        print(f"   {i:2d}. {file_path}")
    
    # Auto-delete (no confirmation needed - these are test scripts)
    print("\n" + "="*120)
    print("⚠️  กำลังลบไฟล์ (Auto-delete mode)")
    print("="*120)
    
    # ลบไฟล์
    print("\n" + "="*120)
    print("🗑️  กำลังลบไฟล์...")
    print("="*120)
    
    deleted, not_found, errors = delete_files(TEST_SCRIPTS_TO_DELETE)
    
    # สรุปผล
    print("\n" + "="*120)
    print("📊 สรุปผลการลบ")
    print("="*120)
    
    print(f"\n✅ ลบสำเร็จ: {len(deleted)} ไฟล์")
    if deleted:
        for file_path in deleted:
            print(f"   - {file_path}")
    
    print(f"\n⚠️  ไม่พบไฟล์: {len(not_found)} ไฟล์")
    if not_found:
        for file_path in not_found:
            print(f"   - {file_path}")
    
    print(f"\n❌ เกิดข้อผิดพลาด: {len(errors)} ไฟล์")
    if errors:
        for file_path, error in errors:
            print(f"   - {file_path}: {error}")
    
    print("\n" + "="*120)
    print("✅ เสร็จสิ้น")
    print("="*120)

if __name__ == "__main__":
    main()

