#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple_recovery.py - Simple forecast recovery using existing system
=============================================================
Uses the existing main.py logic but with modified date handling
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import processor
from core.data_cache import get_data_with_cache
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

def modify_system_date(target_date):
    """Temporarily modify system date for processing"""
    # This is a hack - we'll modify the datetime module
    import datetime as dt_module
    
    original_today = dt_module.datetime.today
    original_now = dt_module.datetime.now
    
    class MockDateTime:
        @classmethod
        def today(cls):
            return dt_module.datetime.strptime(target_date, '%Y-%m-%d')
        
        @classmethod  
        def now(cls):
            return dt_module.datetime.strptime(target_date, '%Y-%m-%d')
    
    # Monkey patch
    dt_module.datetime.today = MockDateTime.today
    dt_module.datetime.now = MockDateTime.now
    
    return original_today, original_now

def restore_system_date(original_today, original_now):
    """Restore original system date"""
    import datetime as dt_module
    dt_module.datetime.today = original_today
    dt_module.datetime.now = original_now

def run_forecast_for_date(target_date):
    """Run forecast generation for a specific date"""
    print(f"\n🔄 Running forecast generation for {target_date}...")
    
    # Backup original date functions
    original_today, original_now = modify_system_date(target_date)
    
    try:
        # Import and run the main processing logic
        # We'll use a simplified version of main.py processing
        
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
        
        for market_name, market_info in markets.items():
            print(f"\n📂 Processing {market_name} Market...")
            symbols = market_info["symbols"]
            exchange = market_info["exchange"]
            
            for i, symbol in enumerate(symbols, 1):
                print(f"   [{i}/{len(symbols)}] Processing {symbol}...", end='\r')
                
                try:
                    # Get data using cache
                    data = get_data_with_cache(symbol, exchange)
                    if data is not None and len(data) > 50:
                        # Process the symbol
                        results = processor.process_symbol(symbol, exchange, data, target_date)
                        if results:
                            all_results.extend(results)
                except Exception as e:
                    print(f"\n⚠️ Error processing {symbol}: {e}")
        
        print(f"\n✅ Generated {len(all_results)} forecasts for {target_date}")
        return all_results
        
    finally:
        # Restore original date functions
        restore_system_date(original_today, original_now)

def save_forecasts(forecasts, target_date):
    """Save forecasts to files"""
    if not forecasts:
        print(f"No forecasts to save for {target_date}")
        return
    
    # Create output directory
    output_dir = "data/recovered_forecasts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    df = pd.DataFrame(forecasts)
    filename = f"{output_dir}/forecast_{target_date}.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Saved {len(forecasts)} forecasts to {filename}")
    
    # Create a summary report
    summary_filename = f"{output_dir}/summary_{target_date}.txt"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(f"Forecast Summary for {target_date}\n")
        f.write("=" * 50 + "\n\n")
        
        # Group by market
        markets = {}
        for forecast in forecasts:
            exchange = forecast['exchange']
            if exchange not in markets:
                markets[exchange] = []
            markets[exchange].append(forecast)
        
        for exchange, market_forecasts in markets.items():
            f.write(f"{exchange} Market:\n")
            f.write("-" * 20 + "\n")
            
            # Filter tradeable forecasts
            tradeable = [f for f in market_forecasts if f.get('is_tradeable', False)]
            f.write(f"Total patterns: {len(market_forecasts)}\n")
            f.write(f"Tradeable signals: {len(tradeable)}\n\n")
            
            if tradeable:
                f.write("Tradeable Signals:\n")
                for forecast in tradeable[:10]:  # Show top 10
                    f.write(f"  {forecast['symbol']}: {forecast['forecast_label']} ({forecast['_sort_prob']:.1f}%)\n")
                if len(tradeable) > 10:
                    f.write(f"  ... and {len(tradeable) - 10} more\n")
            f.write("\n")
    
    print(f"📋 Created summary report: {summary_filename}")

def main():
    print("🔄 Starting Simple Forecast Recovery...")
    print(f"Target dates: {', '.join(TARGET_DATES)}")
    
    total_recovered = 0
    
    for target_date in TARGET_DATES:
        try:
            forecasts = run_forecast_for_date(target_date)
            save_forecasts(forecasts, target_date)
            total_recovered += len(forecasts)
        except Exception as e:
            print(f"❌ Error recovering forecasts for {target_date}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Recovery complete! Total forecasts recovered: {total_recovered}")
    print("📁 Check data/recovered_forecasts/ for recovered forecast files")

if __name__ == "__main__":
    main()
