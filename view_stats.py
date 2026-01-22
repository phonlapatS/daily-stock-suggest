#!/usr/bin/env python
"""
view_stats.py - Quick View Master Pattern Stats (Formatted)
============================================================
Displays the Master_Pattern_Stats.csv in a nicely formatted table.
"""

import pandas as pd
import sys

def print_formatted_table(df: pd.DataFrame, max_rows: int = 50, symbol_filter: str = None):
    """
    Print DataFrame as a nicely formatted table.
    """
    print("\n" + "=" * 120)
    print("📊 MASTER PATTERN STATS")
    print("=" * 120)
    
    # Header
    # Header
    header = f"{'Symbol':<10} {'Threshold':>10} {'MaxUp':>6} {'MaxDown':>8} {'Pattern':^8} {'Pattern_Name':<20} {'Category':<10} {'Chance':<8} {'Prob':>6} {'Stats':>18}"
    print("-" * 120)
    print(header)
    print("-" * 120)
    
    # Filter by symbol if provided
    if symbol_filter:
        df = df[df['Symbol'] == symbol_filter.upper()]
        print(f"🔍 Filtering for: {symbol_filter}")

    # Rows
    for idx, row in df.head(max_rows).iterrows():
        symbol = str(row['Symbol'])[:10]
        threshold = str(row['Threshold'])
        # Handle cases where these columns might be missing if reading older CSV
        max_up = int(row.get('Max_Streak_Pos', 0))
        max_down = int(row.get('Max_Streak_Neg', 0))
        
        pattern = str(row['Pattern'])
        pattern_name = str(row['Pattern_Name'])[:20]
        category = str(row['Category'])[:10]
        chance = str(row.get('Chance', '-'))[:8]
        prob = str(row['Prob'])
        stats = str(row['Stats'])
        
        print(f"{symbol:<10} {threshold:>10} {max_up:>6} {max_down:>8} {pattern:^8} {pattern_name:<20} {category:<10} {chance:<8} {prob:>6} {stats:>18}")
    
    print("-" * 100)
    
    if len(df) > max_rows:
        print(f"... and {len(df) - max_rows} more rows (total: {len(df)})")
    
    print(f"\n📊 Total rows: {len(df)}")


def main():
    csv_path = "data/Master_Pattern_Stats.csv"
    max_rows = 50
    symbol_filter = None
    
    # Simple argument parsing
    args = sys.argv[1:]
    for arg in args:
        if arg.endswith('.csv'):
            csv_path = arg
        elif arg.isdigit():
            max_rows = int(arg)
        else:
            symbol_filter = arg.upper()
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} rows from {csv_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {csv_path}")
        print("   Run batch_processor.py first to generate the file.")
        return
    
    # Get max rows from command line argument if provided
    max_rows = 50
    if len(sys.argv) > 1:
        try:
            max_rows = int(sys.argv[1])
        except:
            pass
    
    print_formatted_table(df, max_rows=max_rows, symbol_filter=symbol_filter)


if __name__ == "__main__":
    main()
