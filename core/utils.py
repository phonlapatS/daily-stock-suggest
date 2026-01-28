"""
core/utils.py - Shared Logic Functions (V3.2 Standard)
=======================================================
Central repository for calculation logic to ensure consistency
across processor.py and batch_processor.py.
"""

import pandas as pd
import numpy as np

# ============================================================
# VOLATILITY THRESHOLD (Hybrid Logic)
# ============================================================
def calculate_hybrid_threshold(pct_change: pd.Series, 
                                short_window: int = 20,
                                long_window: int = 252,
                                multiplier: float = 1.25) -> pd.Series:
    """
    Calculate Hybrid Volatility Threshold.
    
    Logic:
    - Short-term: Rolling SD of last `short_window` days × multiplier
    - Long-term Floor: 50% of Rolling SD of last `long_window` days × multiplier
    - Effective Threshold = Max(Short-term, Long-term Floor)
    
    Args:
        pct_change: Series of percentage changes (decimal form)
        short_window: Days for short-term volatility (default 20)
        long_window: Days for long-term volatility (default 252, ~1 year)
        multiplier: SD multiplier (default 1.25)
    
    Returns:
        Series of threshold values (decimal form, NOT percentage)
    """
    short_term_std = pct_change.rolling(window=short_window).std()
    long_term_std = pct_change.rolling(window=long_window).std()
    
    # Long-term floor = 50% of 1-year SD
    long_term_floor = long_term_std * 0.50
    
    # Effective threshold = Max(Short, Floor)
    effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
    effective_std = effective_std.fillna(short_term_std)
    
    # Apply multiplier
    threshold = effective_std * multiplier
    
    return threshold


def get_current_threshold(pct_change: pd.Series, 
                           short_window: int = 20,
                           long_window: int = 252,
                           multiplier: float = 1.25) -> float:
    """
    Get the current (latest) threshold value as a single float.
    
    Returns:
        Threshold value (decimal form). Returns 0 if invalid.
    """
    threshold_series = calculate_hybrid_threshold(
        pct_change, short_window, long_window, multiplier
    )
    
    current = threshold_series.iloc[-1]
    
    if pd.isna(current) or current == 0:
        return 0.0
    
    return float(current)


# ============================================================
# SAMPLE SIZE VALIDATION
# ============================================================
MIN_SAMPLE_THRESHOLD = 5

def is_statistically_significant(sample_count: int, 
                                  min_threshold: int = MIN_SAMPLE_THRESHOLD) -> bool:
    """
    Check if sample size is sufficient for statistical analysis.
    
    Args:
        sample_count: Number of occurrences
        min_threshold: Minimum required samples (default 5)
    
    Returns:
        True if sample size >= min_threshold
    """
    return sample_count >= min_threshold
