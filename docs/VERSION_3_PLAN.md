# Version 3: Batch Pattern Statistical Calculator (Planning)

> [!IMPORTANT]
> This document outlines the planned architecture for **PredictPlus V3.0**.
> **Goal:** Shift from "On-Demand Calculation" to "Pre-Calculated Lookup Tables".
> **Benefit:** Allows instant queries, historical tracking of pattern reliability, and prevents "re-calculating" the same history every day.

---

## 🏗️ System Architecture

### Core Logic: "Complete Coverage"
Unlike V2 which only cares about the *current* pattern, V3 acts as a massive statistical engine.
It must calculate the stats for **Every Pattern** for **Every Stock**, even if that pattern didn't happen today.

### The Nested Loop Requirement
To guarantee consistency, we use a strict nested loop:
1.  **Outer Loop:** Iterate through every Stock in the universe (SET100, NASDAQ, etc.).
2.  **Inner Loop:** Iterate through a fixed list of **30 Standard Patterns**.

---

## 🐍 Proposed Python Implementation

```python
import pandas as pd
import numpy as np

# ==============================================================================
# 1. Standardized Pattern Definitions (The "Fixed 30")
# ==============================================================================
def get_standard_patterns():
    """
    Returns the strict list of 30 patterns to be calculated for EVERY stock.
    This ensures the output CSV has a consistent shape.
    """
    patterns = [
        # --- 1-Day Patterns (2) ---
        "+", "-",
        
        # --- 2-Day Patterns (4) ---
        "++", "+-", "-+", "--",
        
        # --- 3-Day Patterns (8) ---
        "+++", "++-", "+-+", "+--", 
        "-++", "-+-", "--+", "---",
        
        # --- 4-Day Patterns (16) ---
        "++++", "+++-", "++-+", "++--", "+-++", "+-+-", "+--+", "+---",
        "-+++", "-++-", "-+-+", "-+--", "--++", "--+-", "---++", "----"
    ]
    # Total = 2 + 4 + 8 + 16 = 30 Patterns
    return patterns 

# ==============================================================================
# 2. The Core Batch Calculator
# ==============================================================================
def calculate_batch_statistics(stock_universe_data):
    """
    Calculates stats for ALL 30 patterns for ALL stocks.
    
    Args:
        stock_universe_data (dict): { 'SYMBOL': df_history, ... }
    
    Returns:
        pd.DataFrame: The master lookup table.
    """
    standard_patterns = get_standard_patterns()
    master_records = []
    
    print(f"🚀 Starting Batch Calculation for {len(stock_universe_data)} stocks x {len(standard_patterns)} patterns...")

    # --- OUTER LOOP: Iterate Every Stock ---
    for symbol, df in stock_universe_data.items():
        if df is None or len(df) < 100:
            continue
            
        print(f"  >> Processing {symbol}...")
        
        # (Pre-calculation of daily signals happens here to speed up inner loop)
        # e.g., finding all HAMMER indices, all "++++" indices first.
        # precalc_signals = scan_all_signals(df) 
        
        # --- INNER LOOP: Iterate Every Standard Pattern ---
        for pattern_name in standard_patterns:
            
            # 1. Identify all historical occurrences of this SPECIFIC pattern
            # (Logic depends on the pattern type: string vs candlestick)
            occurrences = find_pattern_occurrences(df, pattern_name)
            
            # 2. Calculate Stats if occurrences > 0
            if len(occurrences) > 0:
                # Calculate next-day returns for these occurrences
                next_day_returns = get_next_day_returns(df, occurrences)
                
                total_events = len(next_day_returns)
                wins = sum(1 for r in next_day_returns if r > 0)
                win_rate = (wins / total_events * 100) if total_events > 0 else 0
                exp_move = np.mean(next_day_returns) * 100
            else:
                # Default values for "Never Happened" -> Crucial to keep the row!
                total_events = 0
                win_rate = 0.0
                exp_move = 0.0

            # 3. Append to Master Record
            master_records.append({
                'Symbol': symbol,
                'Pattern_Name': pattern_name,
                'Total_Events': total_events,
                'Win_Rate': round(win_rate, 2),
                'Exp_Move': round(exp_move, 2),
                'Last_Updated': pd.Timestamp.now().strftime('%Y-%m-%d')
            })

    # --- Final Output Generation ---
    df_results = pd.DataFrame(master_records)
    
    # Save to CSV (The Lookup Table)
    output_path = 'data/pattern_stats_lookup.csv'
    df_results.to_csv(output_path, index=False)
    print(f"✅ Batch Complete. Saved {len(df_results)} rows to {output_path}")
    
    return df_results

# ==============================================================================
# Helper Functions (Placeholders for logic)
# ==============================================================================
def find_pattern_occurrences(df, pattern_name):
    """
    Returns list of indices where the pattern occurred.
    This is where the 'Fractal' or 'Candlestick' detection logic lives.
    """
    # ... Implementation details ...
    return []

def get_next_day_returns(df, indices):
    # ... Implementation details ...
    return []
```

## 📊 Data Structure (CSV Output)

The final `pattern_stats_lookup.csv` will look like this:

| Symbol | Pattern_Name | Total_Events | Win_Rate | Exp_Move | Last_Updated |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PTT | ++++ | 120 | 55.0 | 0.85 | 2026-01-22 |
| PTT | ++-- | 45 | 42.0 | -0.50 | 2026-01-22 |
| PTT | HAMMER | 12 | 70.0 | 1.25 | 2026-01-22 |
| ... | ... | ... | ... | ... | ... |
| GULF | ++++ | 98 | 60.0 | 1.10 | 2026-01-22 |

*(Total Rows = Number of Stocks × 30)*

## 🧠 Why This Design?

1.  **O(1) Lookup Speed:** When the market closes, we don't calculate anything. We just identify today's pattern (e.g., "HAMMER") and instantly fetch the row `WHERE Symbol='PTT' AND Pattern='HAMMER'` from our CSV.
2.  **Global Heatmap:** We can easily pivot this CSV to see which patterns are performing best across the *entire market*.
3.  **Consistency:** By forcing the loop over all 30 patterns (even those with 0 events), we ensure our dataset is perfectly rectangular and ready for Machine Learning or Matrix operations later.
