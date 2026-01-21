
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def main():
    print("=" * 60)
    print("🚀 FRACTAL PREDICTION SYSTEM - ASSET COUNT CHECKER")
    print("=" * 60)
    
    total_assets = 0
    
    print(f"{'Group':<25} {'Description':<30} {'Count':>5}")
    print("-" * 60)
    
    for group_name, settings in config.ASSET_GROUPS.items():
        count = len(settings['assets'])
        print(f"{group_name:<25} {settings['description']:<30} {count:>5}")
        total_assets += count
        
    print("-" * 60)
    print(f"{'TOTAL':<55} {total_assets:>5}")
    print("=" * 60)

if __name__ == "__main__":
    main()
