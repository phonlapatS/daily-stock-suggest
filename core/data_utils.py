import pandas as pd
import numpy as np

def add_percent_change_column(df):
    """
    Calculate daily percentage change based on 'close' price.
    """
    if df is None or df.empty:
        return df
        
    if 'close' in df.columns:
        df['pct_change'] = df['close'].pct_change()
        # Fill first NaN with 0
        df['pct_change'] = df['pct_change'].fillna(0)
    
    return df
