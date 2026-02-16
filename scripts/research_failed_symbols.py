#!/usr/bin/env python
"""
research_failed_symbols.py - Research and document reasons for failed symbols
================================================================================
ตรวจสอบและบันทึกเหตุผลที่หุ้นดึงข้อมูลไม่ได้ เช่น:
- ออกจากตลาด (Delisted)
- ล้มละลาย (Bankruptcy)
- ถูกควบรวม (Merged/Acquired)
- เปลี่ยนชื่อ/รหัส (Name/Symbol Change)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import time
from datetime import datetime

# หุ้นที่ต้องตรวจสอบ
FAILED_SYMBOLS = {
    'INTUCH': {'exchange': 'SET', 'market': 'Thailand', 'name': 'Intouch Holdings'},
    'ESSO': {'exchange': 'SET', 'market': 'Thailand', 'name': 'Esso (Thailand)'},
    'STARK': {'exchange': 'SET', 'market': 'Thailand', 'name': 'Stark Corporation'},
    'STEC': {'exchange': 'SET', 'market': 'Thailand', 'name': 'Sino-Thai Engineering'},
    'AZN': {'exchange': 'NASDAQ', 'market': 'US', 'name': 'AstraZeneca'},
    'SGEN': {'exchange': 'NASDAQ', 'market': 'US', 'name': 'Seagen'},
    'WBA': {'exchange': 'NASDAQ', 'market': 'US', 'name': 'Walgreens Boots Alliance'},
    '0981': {'exchange': 'HKEX', 'market': 'Hong Kong', 'name': 'SMIC (Semiconductor Manufacturing)'},
}

def check_symbol_status(tv, symbol, info):
    """
    ตรวจสอบสถานะหุ้นและหาสาเหตุที่ดึงข้อมูลไม่ได้
    
    Returns:
        dict: ข้อมูลสถานะและเหตุผล
    """
    result = {
        'symbol': symbol,
        'exchange': info['exchange'],
        'market': info['market'],
        'name': info['name'],
        'status': 'unknown',
        'reason': '',
        'details': '',
        'last_trade_date': None,
        'data_available': False
    }
    
    print(f"\n{'='*80}")
    print(f"Researching: {symbol} ({info['name']}) - {info['market']}")
    print(f"{'='*80}")
    
    # ลองดึงข้อมูลหลายวิธี
    attempts = [
        {'n_bars': 10, 'description': 'Recent data (10 bars)'},
        {'n_bars': 100, 'description': 'Medium history (100 bars)'},
        {'n_bars': 1, 'description': 'Latest bar only'},
    ]
    
    for attempt in attempts:
        try:
            print(f"  Trying: {attempt['description']}...", end=' ', flush=True)
            df = tv.get_hist(
                symbol=symbol,
                exchange=info['exchange'],
                interval=Interval.in_daily,
                n_bars=attempt['n_bars']
            )
            
            if df is not None and not df.empty:
                result['data_available'] = True
                result['last_trade_date'] = str(df.index[-1]) if len(df) > 0 else None
                print(f"[OK] Found {len(df)} bars, last date: {result['last_trade_date']}")
                break
            else:
                print("[FAIL] Empty data")
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[FAIL] {error_msg[:60]}")
            
            # วิเคราะห์ error message เพื่อหาสาเหตุ
            if 'no data' in error_msg or 'not found' in error_msg:
                result['reason'] = 'Symbol not found in database'
            elif 'timeout' in error_msg:
                result['reason'] = 'Connection timeout (may be temporary)'
            elif 'delisted' in error_msg or 'suspended' in error_msg:
                result['reason'] = 'Delisted or Suspended'
            else:
                result['reason'] = f'Error: {error_msg[:50]}'
        
        time.sleep(0.3)
    
    # วิเคราะห์สถานะ
    if not result['data_available']:
        # กำหนดสถานะตาม market และ error
        if result['exchange'] == 'SET':
            result['status'] = 'Likely Delisted'
            result['details'] = 'Thai stock - May have been delisted from SET. Check SET delisted securities list.'
        elif result['exchange'] == 'NASDAQ':
            if symbol == 'AZN':
                result['status'] = 'Wrong Exchange'
                result['details'] = 'AstraZeneca (AZN) trades on LSE (London Stock Exchange) as AZN.L, not NASDAQ'
            elif symbol == 'SGEN':
                result['status'] = 'Acquired/Delisted'
                result['details'] = 'Seagen (SGEN) was acquired by Pfizer in December 2023 and delisted from NASDAQ'
            elif symbol == 'WBA':
                result['status'] = 'May be Valid'
                result['details'] = 'Walgreens Boots Alliance (WBA) should be valid on NASDAQ. May be temporary issue or symbol format issue.'
            else:
                result['status'] = 'Unknown Issue'
        elif result['exchange'] == 'HKEX':
            if symbol == '0981':
                result['status'] = 'Symbol Format Issue'
                result['details'] = 'HKEX symbols may need different format. Try without leading zero: 981'
            else:
                result['status'] = 'Unknown Issue'
    
    return result

def generate_report(results):
    """
    สร้างรายงานสรุปเหตุผล
    """
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("RESEARCH REPORT: Failed Stock Symbols")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("="*80)
    report_lines.append("")
    
    # จัดกลุ่มตามสถานะ
    by_status = {}
    for r in results:
        status = r['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(r)
    
    for status, symbols in by_status.items():
        report_lines.append(f"\n{'='*80}")
        report_lines.append(f"STATUS: {status}")
        report_lines.append(f"{'='*80}")
        
        for r in symbols:
            report_lines.append(f"\nSymbol: {r['symbol']}")
            report_lines.append(f"  Name: {r['name']}")
            report_lines.append(f"  Exchange: {r['exchange']}")
            report_lines.append(f"  Market: {r['market']}")
            report_lines.append(f"  Reason: {r['reason']}")
            report_lines.append(f"  Details: {r['details']}")
            if r['last_trade_date']:
                report_lines.append(f"  Last Trade Date: {r['last_trade_date']}")
    
    report_lines.append("\n" + "="*80)
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("="*80)
    
    # สรุปคำแนะนำ
    delisted = [r for r in results if 'Delisted' in r['status'] or 'Acquired' in r['status']]
    wrong_exchange = [r for r in results if 'Wrong Exchange' in r['status']]
    format_issue = [r for r in results if 'Format' in r['status']]
    
    if delisted:
        report_lines.append("\n1. DELISTED/ACQUIRED SYMBOLS (Should be removed):")
        for r in delisted:
            report_lines.append(f"   - {r['symbol']}: {r['details']}")
    
    if wrong_exchange:
        report_lines.append("\n2. WRONG EXCHANGE (Need correction):")
        for r in wrong_exchange:
            report_lines.append(f"   - {r['symbol']}: {r['details']}")
    
    if format_issue:
        report_lines.append("\n3. FORMAT ISSUES (May need symbol correction):")
        for r in format_issue:
            report_lines.append(f"   - {r['symbol']}: {r['details']}")
    
    report_lines.append("\n" + "="*80)
    
    return "\n".join(report_lines)

def main():
    print("="*80)
    print("RESEARCHING FAILED SYMBOLS")
    print("="*80)
    print(f"Checking {len(FAILED_SYMBOLS)} symbols...\n")
    
    # Connect to TradingView
    print("Connecting to TradingView...")
    try:
        tv = TvDatafeed()
        print("Connected!\n")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return
    
    results = []
    
    for symbol, info in FAILED_SYMBOLS.items():
        result = check_symbol_status(tv, symbol, info)
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Generate report
    report = generate_report(results)
    
    # Print to console
    print("\n" + report)
    
    # Save to file
    report_file = "data/failed_symbols_research_report.txt"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    main()

