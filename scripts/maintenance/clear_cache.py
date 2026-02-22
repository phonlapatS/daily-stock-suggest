#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ลบ cache ทั้งหมด
"""
import os
import sys
import glob

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")

def clear_cache():
    """ลบ cache ทั้งหมด"""
    if not os.path.exists(CACHE_DIR):
        print("ℹ️  ไม่พบ cache directory")
        return
    
    cache_files = glob.glob(os.path.join(CACHE_DIR, "*.csv")) + glob.glob(os.path.join(CACHE_DIR, "*.pkl"))
    
    if not cache_files:
        print("ℹ️  ไม่พบไฟล์ cache")
        return
    
    deleted_count = 0
    for file_path in cache_files:
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            print(f"⚠️  ไม่สามารถลบ {os.path.basename(file_path)}: {e}")
    
    if deleted_count > 0:
        print(f"🗑️  ลบ cache แล้ว ({deleted_count} ไฟล์)")
    else:
        print("ℹ️  ไม่พบไฟล์ cache ที่ต้องลบ")

if __name__ == "__main__":
    clear_cache()
