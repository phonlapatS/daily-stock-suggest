#!/usr/bin/env python
"""
view_results.py - Scanner Result Viewer
=======================================
Reads data/scan_results.csv and displays it in a beautiful table.
Supports sorting and filtering.
"""

import pandas as pd
import os
from tabulate import tabulate

RESULTS_FILE = "data/scan_results.csv"

def clean_percentage(x):
    if isinstance(x, str):
        return float(x.replace('%', ''))
    return x

def main():
    if not os.path.exists(RESULTS_FILE):
        print(f"❌ No results found at {RESULTS_FILE}")
        return

    try:
        # Read CSV
        df = pd.read_csv(RESULTS_FILE)
        
        if df.empty:
            print("⚠️ Log file is empty.")
            return

        # Clean data for sorting (keep original for display if preferred, but cleaning makes it easier)
        # We will create temporary columns for sorting
        df['WinRate_Val'] = df['WinRate'].apply(clean_percentage)
        df['Pearson_Val'] = df['PearsonScore']

        # Sort by Date (descending) and WinRate (descending)
        df = df.sort_values(by=['Timestamp', 'WinRate_Val'], ascending=[False, False])
        
        # Select columns to display
        display_cols = ['Timestamp', 'Asset', 'Price', 'Change', 'Signal', 'WinRate', 'AvgRet', 'Events', 'PearsonScore']
        
        print("\n" + "="*80)
        print(f"📊 SCAN RESULTS (Total: {len(df)})")
        print("="*80)
        
        # Display using tabulate
        print(tabulate(df[display_cols], headers='keys', tablefmt='psql', showindex=False))
        
        print("\n💡 Tip: Run 'python scripts/stateless_scanner.py' to update results.")

    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    main()
