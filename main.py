#!/usr/bin/env python
"""
main.py - Fractal N+1 Prediction Runner (Categorized Edition)
=============================================================
Orchestrates the entire pipeline: 
Fetch -> Process -> Categorize -> Report -> Forget.
"""
import sys
import time
import os
import pandas as pd
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed
import config
import processor
from core.scoring import calculate_confidence, calculate_risk_from_stats
from core.performance import verify_forecast, log_forecast
from core.data_cache import get_data_with_cache, get_cache_stats

# Load environment variables from .env file
load_dotenv()

# Rate Limiting Config (reduced since cache handles most requests)
REQUEST_DELAY = 0.5  # Reduced delay since cache reduces load
BACKOFF_BASE = 2.0   # Exponential backoff multiplier

def fetch_and_analyze(tv, asset_info, history_bars, interval):
    """
    Fetch data with smart caching and analyze.
    - First run: Fetches 5000 bars, saves to cache
    - Subsequent runs: Fetches ~50 bars delta, merges with cache
    """
    symbol = asset_info['symbol']
    exchange = asset_info['exchange']
    
    # Use cache-aware fetching
    try:
        df = get_data_with_cache(
            tv=tv,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            full_bars=history_bars,
            delta_bars=50  # Only fetch 50 bars when cache exists!
        )
        
        if df is not None and not df.empty:
            results_list = processor.analyze_asset(df)  # Returns list now
            
            # Use readable name if available (e.g., MOUTAI instead of 600519)
            display_name = asset_info.get('name', symbol)
            
            # Add symbol to each result
            for res in results_list:
                res['symbol'] = display_name
            return results_list  # Return all patterns
            
    except Exception as e:
        pass  # Silently fail, cache module handles retries
            
    return []  # Return empty list on failure



def pass_filter(prob, stats, old_pass: bool):
    """
    ตรวจสอบว่า Pattern ผ่านเกณฑ์ Statistical Reliability หรือไม่
    
    Args:
        prob: Probability (%) ของ Pattern
        stats: Sample Size (จำนวนครั้งที่เกิด)
        old_pass: ผลการกรองเดิม (min_matches ตาม pattern length)
    
    Returns:
        bool: True ถ้าผ่านเกณฑ์, False ถ้าไม่ผ่าน
    
    เกณฑ์:
    - Prob ≥ 80% → ต้องมี Stats ≥ 50 (เข้มงวด)
    - Prob ≥ 70% → ต้องมี Stats ≥ 30 (ปานกลาง)
    - Prob < 70% → ใช้เกณฑ์เดิม (10/5/3 ตาม pattern length)
    """
    if prob >= 80:
        return stats >= 50  # High confidence ต้องมีข้อมูลเยอะ (40-60 range → เลือก 50)
    if prob >= 70:
        return stats >= 30  # Medium-high confidence (25-40 range → เลือก 30)
    return old_pass  # Low-medium confidence ใช้เกณฑ์เดิม


def generate_report(results):
    print("=" * 130)
    print(f"📊 PREDICT N+1 REPORT")
    print("=" * 130)
    
    # Sort keys to ensure consistent order (Thai -> US -> Metals -> China -> Indices)
    # Custom sort order: GROUP_A, GROUP_B, GROUP_E, GROUP_C, GROUP_D, GROUP_F
    
    for group_key, settings in config.ASSET_GROUPS.items():
        title = settings['description'].upper()
        
        # Add Emoji based on group key
        if "THAI" in group_key: title = f"🇹🇭 {title}"
        elif "US" in group_key: title = f"🇺🇸 {title}"
        elif "CHINA" in group_key: title = f"🇨🇳 {title}"
        elif "INDICES" in group_key: title = f"🌍 {title}"
        elif "METALS" in group_key: title = f"⚡ {title}"

        # -------------------------------------------------------------
        # 1. Quality Filtering (The Guardrails)
        # -------------------------------------------------------------
        # Rule 1: Minimum Matches >= 10
        # Rule 2: Significance Threshold >= 60% (Prob)
        
        filtered_data = []
        for r in results:
            if r['group'] != group_key: continue
            
            # Calculate probability based on avg_return direction
            avg_ret = r['avg_return']
            if avg_ret > 0: prob = r['bull_prob']
            elif avg_ret < 0: prob = r['bear_prob']
            else: prob = 50.0
            
            # Statistical Reliability Filter
            # Apply probability-based sample size requirements
            stats = r['matches']
            old_pass = True  # processor.py ผ่าน min_matches มาแล้ว
            
            if not pass_filter(prob, stats, old_pass):
                continue  # Skip patterns ที่ไม่ผ่านเกณฑ์ความน่าเชื่อถือ
            
            # Filter: Stats >= 30 (สำหรับความน่าเชื่อถือ)
            if r['matches'] < 30:
                continue
            
            # Add prob to dict for sorting
            r['_sort_prob'] = prob
            filtered_data.append(r)
        
        if not filtered_data:
            print(f"\n{title}")
            print("   (No high-confidence signals found)")
            continue
            
        print(f"\n{title}")
        
        # -------------------------------------------------------------
        # 2. Sorting (Priority 1: Prob%, Priority 2: Matches)
        # -------------------------------------------------------------
        filtered_data.sort(key=lambda x: (-x['_sort_prob'], -x['matches'], x['symbol']))
        
        # -------------------------------------------------------------
        # 3. Deduplication (ลบแถวซ้ำ / บัคแถวซ้ำ - เก็บ Pattern ที่ดีที่สุด 1 อันต่อหุ้น)
        # -------------------------------------------------------------
        seen_symbols = set()
        deduplicated_data = []
        for r in filtered_data:
            if r['symbol'] not in seen_symbols:
                seen_symbols.add(r['symbol'])
                deduplicated_data.append(r)
        
        filtered_data = deduplicated_data
        
        
        # 4. Table Layout
        # Columns: Symbol, Price, Chg%, Threshold, Pattern, Chance, Prob, Conf%, Risk%, Stats, Exp.Move
        header = f"{'Symbol':<10} {'Price':>10} {'Chg%':>10} {'Threshold':>12} {'Pattern':^10} {'Chance':<11} {'Prob.':>6} {'Conf%':>6} {'Risk%':>6} {'Stats':>18} {'Exp.Move':>10}"
        
        print("-" * 130)
        print(header)
        print("-" * 130)

        for r in filtered_data:
            # Filter low stats (< 30 matches)
            if r['matches'] < 30:
                continue

            # Logic: Predict & Prob
            avg_ret = r['avg_return']
            if avg_ret > 0:
                chance = "🟢 UP"
                prob_val = r['bull_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            elif avg_ret < 0:
                chance = "🔴 DOWN"
                prob_val = r['bear_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            else:
                chance = "⚪ SIDE"
                prob_val = 50.0
                win_count = 0
            
            # Get hybrid pattern (context + current)
            pattern = r.get('pattern_display', '.')
            
             # Formatting
            price_str = f"{r['price']:,.2f}"
            thresh_str = f"±{r['threshold']:.2f}%"
            chg_str   = f"{r['change_pct']:+.2f}%"
            prob_str  = f"{int(prob_val)}%"
            
            # Fix stats_str formatting to remove extra spaces and ensure alignment
            # Force integers to avoid any string weirdness
            try:
                m_matches = int(r['matches'])
                m_total = int(r.get('total_bars', 0))
                m_win = win_count # already int
                stats_str = f"{m_win}/{m_matches} ({m_total})"
            except:
                # Fallback if something is wrong
                stats_str = f"{win_count}/{r['matches']} ({r.get('total_bars','?')})"
            
            # Strict Exp. Move Alignment
            exp_str   = f"{avg_ret:+.2f}%"
            
            # Calculate Confidence and Risk
            conf_score = calculate_confidence(prob_val, r['matches'])
            risk_score = calculate_risk_from_stats(r['bear_prob'], avg_ret)
            conf_str = f"{int(conf_score)}%"
            risk_str = f"{int(risk_score)}%"
            
            # Print Row with Conf% and Risk%
            print(f"{r['symbol']:<10} {price_str:>10} {chg_str:>10} {thresh_str:>12} {pattern:^10} {chance:<11} {prob_str:>6} {conf_str:>6} {risk_str:>6} {stats_str:>18} {exp_str:>10}")

        print("-" * 130)


    # Export to DataFrame
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv('data/pattern_results.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved {len(results)} patterns to data/pattern_results.csv")
    print("\n✅ Report Generated.")

def main():
    import time
    import os
    start_time = time.time()
    
    print("🚀 Starting Fractal N+1 Prediction System...")
    
    # Connect TV - Use environment variables for credentials
    try:
        tv_user = os.environ.get('TV_USERNAME', '')
        tv_pass = os.environ.get('TV_PASSWORD', '')
        if tv_user and tv_pass:
            tv = TvDatafeed(username=tv_user, password=tv_pass)
        else:
            tv = TvDatafeed()  # No login (limited access)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    all_results = []
    
    # Fetch Summary Tracking
    fetch_summary = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'failed_symbols': []
    }
    
    # Iterate through Asset Groups
    for group_name, settings in config.ASSET_GROUPS.items():
        print(f"\n📂 Processing {settings['description']}...")
        
        assets = settings['assets']
        interval = settings['interval']
        history = settings['history_bars']
        
        for i, asset in enumerate(assets):
            sys.stdout.write(f"\r   [{i+1}/{len(assets)}] Scanning {asset['symbol']}...")
            sys.stdout.flush()
            
            fetch_summary['total'] += 1
            pattern_results = fetch_and_analyze(tv, asset, history, interval)
            
            # pattern_results is now a list (can be empty or have multiple items)
            if pattern_results:
                fetch_summary['success'] += 1
                for res in pattern_results:
                    res['group'] = group_name
                    res['exchange'] = asset['exchange']  # Add actual exchange for performance logging
                    all_results.append(res)
            else:
                fetch_summary['failed'] += 1
                fetch_summary['failed_symbols'].append(asset['symbol'])
            
            time.sleep(0.5) # Rate Limit
    
    # Print Fetch Summary
    print("\n")
    print("=" * 50)
    print("📊 FETCH SUMMARY")
    print("=" * 50)
    success_rate = (fetch_summary['success'] / fetch_summary['total'] * 100) if fetch_summary['total'] > 0 else 0
    print(f"✅ Success: {fetch_summary['success']}/{fetch_summary['total']} ({success_rate:.1f}%)")
    print(f"❌ Failed:  {fetch_summary['failed']}")
    if fetch_summary['failed_symbols']:
        # Show first 10 failed symbols
        shown = fetch_summary['failed_symbols'][:10]
        print(f"   Failed symbols: {', '.join(shown)}", end='')
        if len(fetch_summary['failed_symbols']) > 10:
            print(f" ... and {len(fetch_summary['failed_symbols']) - 10} more")
        else:
            print()
    print("=" * 50)

    # Final Report
    if all_results:
        generate_report(all_results)
        
        # Performance Logging
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE LOGGING")
        print("=" * 50)
        verify_forecast(tv)  # Verify yesterday's forecasts
        log_forecast(all_results)  # Log today's forecasts
    else:
        print("\n❌ No matching patterns found in any asset.")
    
    # Print execution time
    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"\n⏱️ Total execution time: {minutes}m {seconds}s")

if __name__ == "__main__":
    main()
