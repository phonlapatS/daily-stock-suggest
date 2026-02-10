"""
sector_rotation.py - Sector Strength Filter
============================================
Filter Logic: Only trade stocks in sectors outperforming SPY.
Returns: True (Strong Sector) or False (Weak Sector)
"""

import pandas as pd

# Mapping of stocks to their sectors (simplified for US stocks)
SECTOR_MAP = {
    # Technology (XLK)
    'AAPL': 'XLK', 'MSFT': 'XLK', 'NVDA': 'XLK', 'GOOGL': 'XLK', 'GOOG': 'XLK',
    'META': 'XLK', 'AVGO': 'XLK', 'ADBE': 'XLK', 'CRM': 'XLK', 'CSCO': 'XLK',
    'ACN': 'XLK', 'ORCL': 'XLK', 'INTC': 'XLK', 'AMD': 'XLK', 'QCOM': 'XLK',
    'TXN': 'XLK', 'AMAT': 'XLK', 'MU': 'XLK', 'LRCX': 'XLK', 'KLAC': 'XLK',
    
    # Healthcare (XLV)
    'UNH': 'XLV', 'JNJ': 'XLV', 'LLY': 'XLV', 'PFE': 'XLV', 'ABBV': 'XLV',
    'MRK': 'XLV', 'TMO': 'XLV', 'ABT': 'XLV', 'DHR': 'XLV', 'BMY': 'XLV',
    'AMGN': 'XLV', 'GILD': 'XLV', 'VRTX': 'XLV', 'REGN': 'XLV', 'BIIB': 'XLV',
    
    # Financial (XLF)
    'BRK.B': 'XLF', 'JPM': 'XLF', 'V': 'XLF', 'MA': 'XLF', 'BAC': 'XLF',
    'WFC': 'XLF', 'GS': 'XLF', 'MS': 'XLF', 'AXP': 'XLF', 'C': 'XLF',
    'PYPL': 'XLF', 'BLK': 'XLF', 'SCHW': 'XLF', 'CME': 'XLF',
    
    # Consumer Discretionary (XLY)
    'AMZN': 'XLY', 'TSLA': 'XLY', 'HD': 'XLY', 'NKE': 'XLY', 'MCD': 'XLY',
    'LOW': 'XLY', 'SBUX': 'XLY', 'TGT': 'XLY', 'BKNG': 'XLY', 'TJX': 'XLY',
    
    # Consumer Staples (XLP)
    'PG': 'XLP', 'KO': 'XLP', 'PEP': 'XLP', 'COST': 'XLP', 'WMT': 'XLP',
    'PM': 'XLP', 'MDLZ': 'XLP', 'MO': 'XLP', 'CL': 'XLP', 'KHC': 'XLP',
    
    # Energy (XLE)
    'XOM': 'XLE', 'CVX': 'XLE', 'COP': 'XLE', 'SLB': 'XLE', 'EOG': 'XLE',
    'MPC': 'XLE', 'PSX': 'XLE', 'VLO': 'XLE', 'OXY': 'XLE', 'KMI': 'XLE',
    
    # Communication (XLC)
    'NFLX': 'XLC', 'DIS': 'XLC', 'CMCSA': 'XLC', 'VZ': 'XLC', 'T': 'XLC',
    'ATVI': 'XLC', 'EA': 'XLC', 'TMUS': 'XLC',
    
    # Industrials (XLI)
    'UPS': 'XLI', 'HON': 'XLI', 'UNP': 'XLI', 'BA': 'XLI', 'CAT': 'XLI',
    'RTX': 'XLI', 'DE': 'XLI', 'LMT': 'XLI', 'GE': 'XLI', 'MMM': 'XLI',
    
    # Utilities (XLU)
    'NEE': 'XLU', 'DUK': 'XLU', 'SO': 'XLU', 'D': 'XLU', 'AEP': 'XLU',
    
    # Real Estate (XLRE)
    'AMT': 'XLRE', 'PLD': 'XLRE', 'CCI': 'XLRE', 'EQIX': 'XLRE', 'SPG': 'XLRE',
    
    # Materials (XLB)
    'LIN': 'XLB', 'APD': 'XLB', 'SHW': 'XLB', 'ECL': 'XLB', 'NEM': 'XLB',
}

# Sector ETF symbols
SECTOR_ETFS = ['XLK', 'XLV', 'XLF', 'XLY', 'XLP', 'XLE', 'XLC', 'XLI', 'XLU', 'XLRE', 'XLB']

def get_sector_for_symbol(symbol):
    """Get sector ETF for a given stock symbol."""
    return SECTOR_MAP.get(symbol, None)

def calculate_return(df, lookback=60):
    """Calculate return over lookback period (default 60 days = ~3 months)."""
    if len(df) < lookback:
        return 0.0
    start_price = df['close'].iloc[-lookback]
    end_price = df['close'].iloc[-1]
    return (end_price - start_price) / start_price * 100

def is_sector_strong(symbol, sector_df, spy_df, lookback=60):
    """
    Check if the stock's sector is outperforming SPY.
    
    Args:
        symbol: Stock symbol
        sector_df: DataFrame for the sector ETF
        spy_df: DataFrame for SPY
        lookback: Period to measure relative strength
    
    Returns:
        bool: True if sector is stronger than SPY
    """
    sector_return = calculate_return(sector_df, lookback)
    spy_return = calculate_return(spy_df, lookback)
    
    return sector_return > spy_return

def get_all_sector_strength(sector_data, spy_df, lookback=60):
    """
    Get relative strength of all sectors vs SPY.
    
    Args:
        sector_data: Dict of {sector_etf: DataFrame}
        spy_df: DataFrame for SPY
        lookback: Period to measure
    
    Returns:
        dict: {sector_etf: relative_strength_value}
    """
    spy_return = calculate_return(spy_df, lookback)
    
    strengths = {}
    for sector, df in sector_data.items():
        sector_return = calculate_return(df, lookback)
        strengths[sector] = sector_return - spy_return  # Relative to SPY
    
    return strengths

def get_top_sectors(sector_data, spy_df, top_n=3, lookback=60):
    """Get the top N performing sectors."""
    strengths = get_all_sector_strength(sector_data, spy_df, lookback)
    sorted_sectors = sorted(strengths.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_sectors[:top_n]]
