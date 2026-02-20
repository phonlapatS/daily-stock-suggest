#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
recover_missing_forecasts.py - Recover forecast data for specific dates
=============================================================
Recovers forecast data for dates 12, 13, 16, 17 February 2026
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import processor
from core.data_cache import get_data_with_cache, has_cache, is_cache_fresh
from core.performance import log_forecast
import config

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Target dates to recover
TARGET_DATES = [
    "2026-02-12",
    "2026-02-13", 
    "2026-02-16",
    "2026-02-17"
]

def get_market_data_for_date(symbol, exchange, target_date):
    """Get market data for a specific date from cache"""
    try:
        # Try to get cached data
        cache_key = f"{exchange}_{symbol}"
        cache_file = f"data/cache/{cache_key}.csv"
        
        if os.path.exists(cache_file):
            df = pd.read_csv(cache_file)
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                # Filter data around the target date
                target_dt = pd.to_datetime(target_date)
                start_date = target_dt - timedelta(days=5)
                end_date = target_dt + timedelta(days=2)
                
                filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
                if not filtered_df.empty:
                    return filtered_df
        return None
    except Exception as e:
        print(f"Error getting data for {symbol}: {e}")
        return None

def process_symbol_for_date(symbol, exchange, target_date):
    """Process a single symbol for a specific date"""
    try:
        # Get market data
        data = get_market_data_for_date(symbol, exchange, target_date)
        if data is None or len(data) < 50:
            return None
            
        # Process using the same logic as main.py
        results = processor.process_symbol(symbol, exchange, data, target_date)
        return results
    except Exception as e:
        print(f"Error processing {symbol} for {target_date}: {e}")
        return None

def recover_forecasts_for_date(target_date):
    """Recover all forecasts for a specific date"""
    print(f"\n🔄 Recovering forecasts for {target_date}...")
    
    # Define markets and symbols (same as main.py)
    markets = {
        "THAI": {
            "symbols": [
                "ADVANC", "AOT", "AP", "AWC", "BAM", "BANPU", "BBL", "BCH", "BCP", "BCPG",
                "BDMS", "BEM", "BGRIM", "BH", "BJC", "BPP", "BTS", "BYD", "CBG", "CENTEL",
                "CHG", "CK", "CKP", "COM7", "CPALL", "CPF", "CPN", "CRC", "DELTA", "DOHOME",
                "EA", "EGCO", "EPG", "ERW", "FORTH", "GFPT", "GLOBAL", "GPSC", "GULF", "GUNKUL",
                "HANA", "HMPRO", "ICHI", "IVL", "JMART", "JMT", "JTS", "KBANK", "KCE", "KKP",
                "KTB", "KTC", "LANNA", "LH", "MAJOR", "MEGA", "MINT", "MTC", "NEX", "ONEE",
                "OR", "ORI", "OSP", "PLANB", "PR9", "PSL", "PTG", "PTT", "PTTEP", "PTTGC",
                "QH", "RATCH", "RCL", "SABUY", "SAWAD", "SCB", "SCC", "SCGP", "SINGER", "SIRI",
                "SISB", "SJWD", "SNNP", "SPALI", "SPRC", "SSP", "STA", "STGT", "SUPER", "TASCO",
                "TCAP", "THANI", "THG", "TIDLOR", "TIPH", "TISCO", "TKN", "TKS", "TLI", "TOA",
                "TOP", "TPIPL", "TPIPP", "TQM", "TRUE", "TTB", "TU", "VGI", "WHA", "WHAUP"
            ],
            "exchange": "SET"
        },
        "US": {
            "symbols": [
                "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD", "AMGN",
                "AMZN", "ASML", "AVGO", "BIDU", "BIIB", "BKNG", "BKR", "CDNS", "CHTR", "CMCSA",
                "COST", "CPRT", "CRWD", "CSCO", "CSX", "CTAS", "DDOG", "DLTR", "DXCM", "ENPH",
                "EXC", "FANG", "FAST", "FISV", "FTNT", "GFS", "GILD", "GOOG", "GOOGL", "HON",
                "HTHT", "IDXX", "ILMN", "INTC", "INTU", "ISRG", "JD", "KDP", "KHC", "KLAC",
                "LCID", "LRCX", "LULU", "MAR", "MCHP", "MDLZ", "MELI", "META", "MNST", "MRNA",
                "MRVL", "MSFT", "MU", "NFLX", "NTES", "NVDA", "NXPI", "ODFL", "ORLY", "PANW",
                "PAYX", "PCAR", "PDD", "PEP", "PYPL", "QCOM", "REGN", "RIVN", "ROKU", "ROST",
                "SBUX", "SIRI", "SNPS", "TCOM", "TEAM", "TMUS", "TSLA", "TXN", "VRSK", "VRTX",
                "WBD", "XEL", "ZM", "ZS"
            ],
            "exchange": "NASDAQ"
        },
        "TAIWAN": {
            "symbols": [
                "2303", "2308", "2317", "2330", "2357", "2382", "2395", "2454", "3008", "3711"
            ],
            "exchange": "TWSE"
        },
        "CHINA": {
            "symbols": [
                "700", "1810", "2015", "3690", "9866", "9868", "9888", "9988", "1211", "9618"
            ],
            "exchange": "HKEX"
        }
    }
    
    all_results = []
    processed_count = 0
    
    for market_name, market_info in markets.items():
        print(f"\n📂 Processing {market_name} Market...")
        symbols = market_info["symbols"]
        exchange = market_info["exchange"]
        
        for i, symbol in enumerate(symbols, 1):
            print(f"   [{i}/{len(symbols)}] Processing {symbol}...", end='\r')
            
            try:
                results = process_symbol_for_date(symbol, exchange, target_date)
                if results:
                    all_results.extend(results)
                    processed_count += 1
            except Exception as e:
                print(f"\n⚠️ Error processing {symbol}: {e}")
    
    print(f"\n✅ Processed {processed_count} symbols for {target_date}")
    return all_results

def save_forecasts_to_csv(forecasts, target_date):
    """Save forecasts to a CSV file for the specific date"""
    if not forecasts:
        print(f"No forecasts to save for {target_date}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = "data/recovered_forecasts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(forecasts)
    
    # Save to CSV
    filename = f"{output_dir}/forecast_{target_date}.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Saved {len(forecasts)} forecasts to {filename}")
    
    # Also log to performance log
    try:
        for forecast in forecasts:
            if forecast.get('is_tradeable', False):
                log_forecast(
                    scan_date=target_date,
                    target_date=(pd.to_datetime(target_date) + timedelta(days=1)).strftime('%Y-%m-%d'),
                    symbol=forecast['symbol'],
                    exchange=forecast['exchange'],
                    pattern=forecast['pattern'],
                    forecast=forecast['forecast_label'],
                    prob=forecast['_sort_prob'],
                    stats=f"{forecast['matches']}/{forecast['total_bars']} ({forecast['total_bars']})",
                    price_at_scan=forecast['price'],
                    change_pct=forecast['change_pct'],
                    threshold=forecast['threshold'],
                    avg_return=forecast['avg_return'],
                    total_bars=forecast['total_bars']
                )
        print(f"📝 Logged {len([f for f in forecasts if f.get('is_tradeable', False)])} tradeable forecasts to performance log")
    except Exception as e:
        print(f"⚠️ Error logging to performance log: {e}")

def main():
    print("🔄 Starting Forecast Recovery for Missing Dates...")
    print(f"Target dates: {', '.join(TARGET_DATES)}")
    
    total_recovered = 0
    
    for target_date in TARGET_DATES:
        try:
            forecasts = recover_forecasts_for_date(target_date)
            save_forecasts_to_csv(forecasts, target_date)
            total_recovered += len(forecasts)
        except Exception as e:
            print(f"❌ Error recovering forecasts for {target_date}: {e}")
    
    print(f"\n✅ Recovery complete! Total forecasts recovered: {total_recovered}")
    print("📁 Check data/recovered_forecasts/ for recovered forecast files")

if __name__ == "__main__":
    main()
