#!/usr/bin/env python
"""
scripts/run_market_groups.py
=============================
Wrapper script สำหรับรัน main.py แยกตาม market groups

Usage:
    python scripts/run_market_groups.py GROUP_A_THAI
    python scripts/run_market_groups.py GROUP_C_CHINA_HK
    python scripts/run_market_groups.py GROUP_D_TAIWAN
    python scripts/run_market_groups.py GROUP_B_US
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config

def filter_asset_groups(target_groups):
    """Filter ASSET_GROUPS ตาม target_groups"""
    if not target_groups:
        return config.ASSET_GROUPS
    
    filtered = {}
    for group_name in target_groups:
        if group_name in config.ASSET_GROUPS:
            filtered[group_name] = config.ASSET_GROUPS[group_name]
        else:
            print(f"⚠️ Warning: Group '{group_name}' not found in ASSET_GROUPS")
    
    return filtered

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_market_groups.py <GROUP_NAME> [GROUP_NAME2] ...")
        print("\nAvailable groups:")
        for name, settings in config.ASSET_GROUPS.items():
            print(f"  - {name}: {settings['description']}")
        return
    
    target_groups = sys.argv[1:]
    
    # Temporarily replace ASSET_GROUPS with filtered version
    original_groups = config.ASSET_GROUPS
    config.ASSET_GROUPS = filter_asset_groups(target_groups)
    
    if not config.ASSET_GROUPS:
        print("❌ No valid groups found")
        config.ASSET_GROUPS = original_groups
        return
    
    print(f"📂 Running groups: {', '.join(target_groups)}")
    print("="*80)
    
    # Import and run main
    os.chdir(PROJECT_ROOT)
    from main import main as main_func
    main_func()
    
    # Restore original groups
    config.ASSET_GROUPS = original_groups

if __name__ == "__main__":
    main()

