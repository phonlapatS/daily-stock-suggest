#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_documentation_status.py - ตรวจสอบสถานะเอกสารระบบ
=======================================================
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def check_version_in_file(file_path, target_version="V4.1"):
    """ตรวจสอบว่าไฟล์มี version ที่ถูกต้องหรือไม่"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # เช็คว่ามี target_version หรือไม่
        has_target = target_version in content or target_version.lower() in content
        
        # เช็คว่ามี V3.4 (เก่า) หรือไม่
        has_old = "V3.4" in content or "v3.4" in content or "Version 3.4" in content
        
        if has_target and not has_old:
            return True, "✅ Updated to V4.1"
        elif has_target and has_old:
            return True, "⚠️  Has V4.1 but also mentions V3.4"
        elif has_old:
            return False, "❌ Still shows V3.4"
        else:
            return None, "❓ No version mentioned"
    except:
        return None, "❌ Error reading file"

def main():
    print("\n" + "="*120)
    print("📚 ตรวจสอบสถานะเอกสารระบบ")
    print("="*120)
    
    # เอกสารหลักที่ต้องตรวจสอบ
    main_docs = {
        'README.md': 'Root README',
        'docs/VERSION_HISTORY.md': 'Version History',
        'docs/V4.1_UPDATE_LOG.md': 'V4.1 Update Log',
        'docs/PROJECT_MASTER_MANUAL.md': 'Project Master Manual',
        'docs/SYSTEM_WORKFLOW.md': 'System Workflow',
    }
    
    print("\n📋 เอกสารหลัก:")
    print("="*120)
    
    all_updated = True
    for file_path, description in main_docs.items():
        full_path = os.path.join(BASE_DIR, file_path)
        status, message = check_version_in_file(full_path)
        
        if status is True:
            print(f"✅ {description:<30} {file_path:<40} {message}")
        elif status is False:
            print(f"❌ {description:<30} {file_path:<40} {message}")
            all_updated = False
        else:
            print(f"❓ {description:<30} {file_path:<40} {message}")
    
    # เอกสารอื่นๆ
    print("\n📋 เอกสารอื่นๆ:")
    print("="*120)
    
    other_docs = [
        'docs/V3.4_ROADMAP.md',
        'docs/V4.5_UPDATE_LOG.md',
        'docs/SIMPLIFIED_SYSTEM_V6.1.md',
        'docs/INDICATOR_FILTERS_ARCHIVE.md',
    ]
    
    for file_path in other_docs:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            status, message = check_version_in_file(full_path)
            file_name = os.path.basename(file_path)
            if status is True:
                print(f"✅ {file_name:<40} {message}")
            elif status is False:
                print(f"⚠️  {file_name:<40} {message} (Historical document)")
            else:
                print(f"❓ {file_name:<40} {message}")
    
    # สรุป
    print("\n" + "="*120)
    print("📊 สรุป")
    print("="*120)
    
    if all_updated:
        print("\n✅ เอกสารหลักทั้งหมดอัปเดตเป็น V4.1 แล้ว")
        print("\n📝 เอกสารที่อัปเดตแล้ว:")
        print("   ✅ README.md")
        print("   ✅ docs/VERSION_HISTORY.md")
        print("   ✅ docs/V4.1_UPDATE_LOG.md")
        print("   ✅ docs/PROJECT_MASTER_MANUAL.md")
        print("   ✅ docs/SYSTEM_WORKFLOW.md")
    else:
        print("\n⚠️  ยังมีเอกสารที่ต้องอัปเดต")
    
    print("\n" + "="*120)

if __name__ == "__main__":
    main()

