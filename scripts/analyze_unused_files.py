#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_unused_files.py - วิเคราะห์ไฟล์ .py ที่ไม่ได้ใช้แล้ว
================================================================
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent

# ไฟล์หลักที่ใช้จริง (Core System)
CORE_FILES = {
    'main.py',
    'config.py',
    'processor.py',
    'scripts/backtest.py',
    'scripts/calculate_metrics.py',
    'core/data_cache.py',
    'core/performance.py',
    'core/market_time.py',
    'core/engines/base_engine.py',
    'core/engines/reversion_engine.py',
    'core/engines/trend_engine.py',
    'scripts/stock_logger.py',
    'scripts/intraday_runner.py',
    'scripts/market_sentiment.py',
    'scripts/incremental_update.py',
}

# ไฟล์ที่ใช้เป็นเครื่องมือวิเคราะห์ (Analysis Tools - ยังใช้ได้)
ANALYSIS_TOOLS = {
    'scripts/assess_system_status.py',
    'scripts/analyze_statistical_reliability.py',
    'scripts/analyze_indicator_vs_risk_management.py',
    'scripts/analyze_metrics_by_country.py',
    'scripts/plot_markets_from_metrics.py',
    'scripts/plot_equity.py',
    'scripts/split_trade_history_by_market.py',
}

# ไฟล์ที่ใช้เป็นเครื่องมือทดสอบ (Test Scripts - ยังใช้ได้)
TEST_SCRIPTS = {
    'scripts/test_risk_management.py',
    'scripts/verify_failed_symbols.py',
    'scripts/research_failed_symbols.py',
}

def find_all_py_files():
    """หาไฟล์ .py ทั้งหมด"""
    py_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip __pycache__ and .git
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                py_files.append(rel_path.replace('\\', '/'))
    return sorted(py_files)

def extract_imports(file_path):
    """ดึง imports จากไฟล์"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        imports = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except:
            # Fallback to regex
            import_pattern = r'^(?:from|import)\s+(\w+)'
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    imports.add(match.group(1))
        
        return imports
    except:
        return set()

def check_file_usage(file_path, all_files, imports_map):
    """ตรวจสอบว่าไฟล์ถูกใช้หรือไม่"""
    file_name = os.path.basename(file_path)
    file_stem = os.path.splitext(file_name)[0]
    
    # ตรวจสอบว่าไฟล์ถูก import หรือไม่
    for other_file, imports in imports_map.items():
        if other_file == file_path:
            continue
        
        # เช็ค import โดยตรง
        if file_stem in imports or file_name in imports:
            return True, f"Imported by {other_file}"
        
        # เช็ค import แบบ relative
        rel_path = file_path.replace('\\', '/')
        if rel_path.replace('.py', '') in imports:
            return True, f"Imported by {other_file}"
    
    # เช็คว่าเป็น entry point หรือไม่
    if file_path in CORE_FILES or file_path in ANALYSIS_TOOLS or file_path in TEST_SCRIPTS:
        return True, "Core/Utility file"
    
    # เช็คว่าถูกเรียกใช้ใน main.py หรือไม่
    if file_path == 'main.py':
        return True, "Main entry point"
    
    return False, "Not found"

def categorize_files(py_files):
    """จัดหมวดหมู่ไฟล์"""
    categories = {
        'core_system': [],
        'analysis_tools': [],
        'test_scripts': [],
        'old_test_scripts': [],
        'old_analysis': [],
        'plotting_scripts': [],
        'unused': [],
        'unknown': []
    }
    
    # Patterns สำหรับจัดหมวดหมู่
    old_test_patterns = [
        'test_old_threshold',
        'test_thai_old_threshold',
        'backtest_old_threshold',
        'backtest_thai_with_old_threshold',
        'run_old_threshold',
        'test_hybrid_backtest',
        'test_comprehensive',
        'test_all_filters',
        'test_filter_variants',
        'test_shadow_mode',
        'test_optimized_classifier',
        'test_global_optimization',
        'test_inverse_logic',
        'test_multi_day_holding',
        'test_us_long_only',
        'test_international_markets',
        'test_improved_strategies',
        'test_simplified_system',
        'test_trailing_stop_rrr',
        'compare_old_new_results',
        'compare_old_vs_new_results',
        'create_comparison_table',
        'create_full_comparison_table',
        'create_threshold_comparison_table',
        'compare_threshold_results',
        'analyze_old_vs_new_criteria',
        'analyze_thai_market_changes',
        'analyze_data_flow',
        'explain_tpipp_mystery',
        'check_super',
    ]
    
    old_analysis_patterns = [
        'analyze_china',
        'analyze_china_turnover',
        'analyze_us_paradox',
        'analyze_honest_timestop',
        'analyze_rrr_calculation',
        'analyze_rrr_potential',
        'analyze_trade_direction',
        'analyze_stock_counts_by_country',
        'analyze_market_specific_logic',
        'analyze_logic_engine_comprehensive',
        'analyze_mentor_comments_status',
        'analyze_metals_volatility',
        'analyze_backtest_results',
        'analyze_count_impact',
        'analyze_display_improvements',
        'deep_analysis_international',
        'debug_china_stats',
        'diagnose_market_loss',
        'quick_intl_analysis',
    ]
    
    plotting_patterns = [
        'plot_',
        'visualize_',
        'generate_real_equity_plots',
        'temp_plot_user_request',
    ]
    
    for file in py_files:
        file_lower = file.lower()
        
        if file in CORE_FILES:
            categories['core_system'].append(file)
        elif file in ANALYSIS_TOOLS:
            categories['analysis_tools'].append(file)
        elif file in TEST_SCRIPTS:
            categories['test_scripts'].append(file)
        elif any(pattern in file_lower for pattern in old_test_patterns):
            categories['old_test_scripts'].append(file)
        elif any(pattern in file_lower for pattern in old_analysis_patterns):
            categories['old_analysis'].append(file)
        elif any(pattern in file_lower for pattern in plotting_patterns):
            categories['plotting_scripts'].append(file)
        else:
            categories['unknown'].append(file)
    
    return categories

def main():
    print("\n" + "="*120)
    print("📊 วิเคราะห์ไฟล์ .py ที่ไม่ได้ใช้แล้ว")
    print("="*120)
    
    # 1. หาไฟล์ .py ทั้งหมด
    print("\n🔍 กำลังค้นหาไฟล์ .py ทั้งหมด...")
    py_files = find_all_py_files()
    print(f"   พบ {len(py_files)} ไฟล์")
    
    # 2. จัดหมวดหมู่
    print("\n📂 กำลังจัดหมวดหมู่ไฟล์...")
    categories = categorize_files(py_files)
    
    # 3. ตรวจสอบ imports
    print("\n🔗 กำลังตรวจสอบ imports...")
    imports_map = {}
    for file in py_files:
        full_path = os.path.join(BASE_DIR, file)
        if os.path.exists(full_path):
            imports_map[file] = extract_imports(full_path)
    
    # 4. แสดงผลลัพธ์
    print("\n" + "="*120)
    print("📋 ผลการวิเคราะห์")
    print("="*120)
    
    # Core System
    print("\n✅ Core System (ใช้จริง):")
    for file in sorted(categories['core_system']):
        print(f"   - {file}")
    
    # Analysis Tools
    print("\n🔧 Analysis Tools (ยังใช้ได้):")
    for file in sorted(categories['analysis_tools']):
        print(f"   - {file}")
    
    # Test Scripts
    print("\n🧪 Test Scripts (ยังใช้ได้):")
    for file in sorted(categories['test_scripts']):
        print(f"   - {file}")
    
    # Old Test Scripts (ควรลบ)
    print("\n" + "="*120)
    print("❌ Old Test Scripts (ควรลบ - ไม่ได้ใช้แล้ว):")
    print("="*120)
    for file in sorted(categories['old_test_scripts']):
        used, reason = check_file_usage(file, py_files, imports_map)
        status = "✅ ใช้" if used else "❌ ไม่ใช้"
        print(f"   {status} - {file}")
        if not used:
            print(f"      → {reason}")
    
    # Old Analysis (ควรลบ)
    print("\n" + "="*120)
    print("❌ Old Analysis Scripts (ควรลบ - ไม่ได้ใช้แล้ว):")
    print("="*120)
    for file in sorted(categories['old_analysis']):
        used, reason = check_file_usage(file, py_files, imports_map)
        status = "✅ ใช้" if used else "❌ ไม่ใช้"
        print(f"   {status} - {file}")
        if not used:
            print(f"      → {reason}")
    
    # Plotting Scripts
    print("\n" + "="*120)
    print("📊 Plotting Scripts (ตรวจสอบ):")
    print("="*120)
    for file in sorted(categories['plotting_scripts']):
        used, reason = check_file_usage(file, py_files, imports_map)
        status = "✅ ใช้" if used else "❌ ไม่ใช้"
        print(f"   {status} - {file}")
        if not used:
            print(f"      → {reason}")
    
    # Unknown
    print("\n" + "="*120)
    print("❓ Unknown Files (ตรวจสอบ):")
    print("="*120)
    for file in sorted(categories['unknown']):
        used, reason = check_file_usage(file, py_files, imports_map)
        status = "✅ ใช้" if used else "❌ ไม่ใช้"
        print(f"   {status} - {file}")
        if not used:
            print(f"      → {reason}")
    
    # สรุป
    print("\n" + "="*120)
    print("📊 สรุป")
    print("="*120)
    
    total_old_test = len(categories['old_test_scripts'])
    total_old_analysis = len(categories['old_analysis'])
    total_unknown = len(categories['unknown'])
    
    print(f"\n✅ Core System: {len(categories['core_system'])} ไฟล์")
    print(f"🔧 Analysis Tools: {len(categories['analysis_tools'])} ไฟล์")
    print(f"🧪 Test Scripts: {len(categories['test_scripts'])} ไฟล์")
    print(f"❌ Old Test Scripts: {total_old_test} ไฟล์ (ควรลบ)")
    print(f"❌ Old Analysis: {total_old_analysis} ไฟล์ (ควรลบ)")
    print(f"📊 Plotting Scripts: {len(categories['plotting_scripts'])} ไฟล์")
    print(f"❓ Unknown: {total_unknown} ไฟล์ (ต้องตรวจสอบ)")
    
    # List ไฟล์ที่ควรลบ
    print("\n" + "="*120)
    print("🗑️  ไฟล์ที่ควรลบ (ไม่ใช้แล้วจริงๆ):")
    print("="*120)
    
    files_to_delete = []
    
    # Old Test Scripts
    for file in sorted(categories['old_test_scripts']):
        used, _ = check_file_usage(file, py_files, imports_map)
        if not used:
            files_to_delete.append(file)
    
    # Old Analysis
    for file in sorted(categories['old_analysis']):
        used, _ = check_file_usage(file, py_files, imports_map)
        if not used:
            files_to_delete.append(file)
    
    if files_to_delete:
        print(f"\nพบ {len(files_to_delete)} ไฟล์ที่ควรลบ:\n")
        for file in files_to_delete:
            print(f"   - {file}")
    else:
        print("\n   ไม่พบไฟล์ที่ควรลบ (หรือยังถูกใช้อยู่)")
    
    print("\n" + "="*120)

if __name__ == "__main__":
    main()

