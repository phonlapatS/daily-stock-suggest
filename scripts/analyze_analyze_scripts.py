#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_analyze_scripts.py - วิเคราะห์ analyze scripts แต่ละไฟล์ว่ายังใช้อยู่หรือไม่
====================================================================================
"""

import os
import sys
import ast
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Analyze scripts ที่ต้องตรวจสอบ
ANALYZE_SCRIPTS = [
    'scripts/analyze_china.py',
    'scripts/analyze_china_turnover.py',
    'scripts/analyze_us_paradox.py',
    'scripts/analyze_backtest_results.py',
    'scripts/analyze_count_impact.py',
    'scripts/analyze_display_improvements.py',
    'scripts/analyze_logic_engine_comprehensive.py',
    'scripts/analyze_mentor_comments_status.py',
    'scripts/analyze_stock_counts_by_country.py',
    'scripts/analyze_trade_direction.py',
    'scripts/analyze_rrr_calculation.py',
    'scripts/analyze_rrr_potential.py',
    'scripts/analyze_honest_timestop.py',
    'scripts/analyze_metals_volatility.py',
    'scripts/analyze_market_specific_logic.py',
    'scripts/debug_china_stats.py',
    'scripts/deep_analysis_international.py',
    'scripts/diagnose_market_loss.py',
    'scripts/quick_intl_analysis.py',
]

def check_file_imported(file_path, all_files):
    """ตรวจสอบว่าไฟล์ถูก import หรือไม่"""
    file_name = os.path.basename(file_path)
    file_stem = os.path.splitext(file_name)[0]
    
    for other_file in all_files:
        if other_file == file_path:
            continue
        
        full_path = os.path.join(BASE_DIR, other_file)
        if not os.path.exists(full_path):
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # เช็ค import
            if file_stem in content or file_name in content:
                # เช็คว่าเป็น import จริงๆ หรือไม่
                import_patterns = [
                    f'import {file_stem}',
                    f'from {file_stem}',
                    f'import.*{file_stem}',
                    f'from.*{file_stem}',
                ]
                
                for pattern in import_patterns:
                    if re.search(pattern, content):
                        return True, other_file
        except:
            pass
    
    return False, None

def analyze_script_purpose(file_path):
    """วิเคราะห์จุดประสงค์ของ script"""
    full_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(full_path):
        return None, None
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # อ่าน docstring หรือ comment แรก
        lines = content.split('\n')
        purpose = []
        for i, line in enumerate(lines[:50]):  # อ่าน 50 บรรทัดแรก
            if '"""' in line or "'''" in line:
                # Docstring
                continue
            if line.strip().startswith('#'):
                purpose.append(line.strip())
            if len(purpose) >= 5:
                break
        
        # หา main function หรือ entry point
        has_main = 'if __name__' in content or 'def main(' in content
        
        return '\n'.join(purpose[:3]), has_main
    except:
        return None, None

def main():
    print("\n" + "="*120)
    print("📊 วิเคราะห์ Analyze Scripts แต่ละไฟล์")
    print("="*120)
    
    # หาไฟล์ .py ทั้งหมด
    all_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                all_files.append(rel_path.replace('\\', '/'))
    
    results = []
    
    for file_path in ANALYZE_SCRIPTS:
        full_path = os.path.join(BASE_DIR, file_path)
        
        if not os.path.exists(full_path):
            results.append({
                'file': file_path,
                'exists': False,
                'imported': False,
                'purpose': None,
                'has_main': False,
                'recommendation': '❌ ไม่พบไฟล์'
            })
            continue
        
        # ตรวจสอบว่าไฟล์ถูก import หรือไม่
        imported, imported_by = check_file_imported(file_path, all_files)
        
        # วิเคราะห์จุดประสงค์
        purpose, has_main = analyze_script_purpose(file_path)
        
        # แนะนำ
        if imported:
            recommendation = f'✅ ยังใช้อยู่ (imported by {imported_by})'
        elif has_main:
            recommendation = '⚠️  Standalone script - ตรวจสอบว่ายังใช้อยู่หรือไม่'
        else:
            recommendation = '❌ ไม่ได้ใช้แล้ว - ควรลบ'
        
        results.append({
            'file': file_path,
            'exists': True,
            'imported': imported,
            'imported_by': imported_by,
            'purpose': purpose,
            'has_main': has_main,
            'recommendation': recommendation
        })
    
    # แสดงผลลัพธ์
    print("\n" + "="*120)
    print("📋 ผลการวิเคราะห์")
    print("="*120)
    
    for result in results:
        print(f"\n📄 {result['file']}")
        print(f"   สถานะ: {'✅ พบไฟล์' if result['exists'] else '❌ ไม่พบไฟล์'}")
        if result['exists']:
            print(f"   Imported: {'✅ ใช่' if result['imported'] else '❌ ไม่ใช่'}")
            if result['imported']:
                print(f"      → Imported by: {result['imported_by']}")
            print(f"   Has Main: {'✅ ใช่' if result['has_main'] else '❌ ไม่ใช่'}")
            if result['purpose']:
                print(f"   Purpose: {result['purpose'][:100]}...")
            print(f"   💡 แนะนำ: {result['recommendation']}")
    
    # สรุป
    print("\n" + "="*120)
    print("📊 สรุป")
    print("="*120)
    
    imported_count = sum(1 for r in results if r['imported'])
    standalone_count = sum(1 for r in results if r['exists'] and r['has_main'] and not r['imported'])
    unused_count = sum(1 for r in results if r['exists'] and not r['imported'] and not r['has_main'])
    
    print(f"\n✅ ยังใช้อยู่ (imported): {imported_count} ไฟล์")
    print(f"⚠️  Standalone (ต้องตรวจสอบ): {standalone_count} ไฟล์")
    print(f"❌ ไม่ได้ใช้แล้ว (ควรลบ): {unused_count} ไฟล์")
    
    # แสดงไฟล์ที่ควรลบ
    if unused_count > 0:
        print("\n" + "="*120)
        print("🗑️  ไฟล์ที่ควรลบ:")
        print("="*120)
        for result in results:
            if result['exists'] and not result['imported'] and not result['has_main']:
                print(f"   - {result['file']}")
    
    print("\n" + "="*120)

if __name__ == "__main__":
    main()

