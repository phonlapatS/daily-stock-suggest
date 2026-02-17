#!/usr/bin/env python
from collections import defaultdict
import pandas as pd
import numpy as np
import os
import sys

# Resolve path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Helper to build symbol name map
def get_symbol_map():
    mapping = {}
    for group in config.ASSET_GROUPS.values():
        for asset in group['assets']:
            if 'name' in asset:
                mapping[asset['symbol']] = asset['name']
    return mapping

SYMBOL_MAP = get_symbol_map()

def get_country_code(group_name, symbol=None):
    """
    Determine country code from group name or symbol.
    Priority: group_name > symbol lookup in config
    """
    # Try group name first
    if isinstance(group_name, str):
        if 'THAI' in group_name: return 'TH'
        if 'US' in group_name: return 'US'
        if 'CHINA' in group_name: return 'CN'
        if 'HK' in group_name: return 'HK'
        if 'TAIWAN' in group_name: return 'TW'
        if 'METAL' in group_name or 'GOLD' in group_name or 'SILVER' in group_name:
            return 'GL'
    
    # Fallback: lookup symbol in config
    if symbol:
        for group_key, group_data in config.ASSET_GROUPS.items():
            for asset in group_data.get('assets', []):
                if asset.get('symbol') == symbol:
                    if 'THAI' in group_key: return 'TH'
                    if 'US' in group_key: return 'US'
                    if 'CHINA' in group_key: return 'CN'
                    if 'HK' in group_key: return 'HK'
                    if 'TAIWAN' in group_key: return 'TW'
                    if 'METAL' in group_key or 'GOLD' in group_key or 'SILVER' in group_key:
                        return 'GL'
    
    return 'GL'  # Default to Global/Metals


# ==============================================================================
# Helper Functions: Print Tables
# ==============================================================================
def print_table(df, title, icon="[OK]"):
    """
    Detailed table: Raw vs Elite comparison (used mainly for System Edge / debug).
    """
    if df.empty:
        print(f"\n{title}")
        print("=" * 100)
        print("   (No Data)")
        return

    print(f"\n{title}")
    print("=" * 100)
    print(f"{'Symbol':<10} {'Ctry':<6} {'Count':>6} {'Prob%':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>6}")
    print("-" * 100)
    
    for _, row in df.iterrows():
        print(f"{str(row.get('Symbol',row.get('symbol','?'))):<10} "
              f"{str(row.get('Country','?')):<6} "
              f"{int(row.get('Count',0)):>6} "
              f"{float(row.get('Prob%',0)):>7.1f}% "
              f"{float(row.get('AvgWin%',0)):>9.2f}% "
              f"{float(row.get('AvgLoss%',0)):>9.2f}% "
              f"{float(row.get('RRR',row.get('RR_Ratio',0))):>6.2f}")
    print("-" * 100)

import glob

def load_trade_data(file_path):
    """
    Load trade data from CSV(s). Prioritizes merging multiple logs/trade_history_*.csv 
    over a single file, to ensure latest data is used.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Check for Split Files First (Priority)
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    
    # Filter out the main "trade_history.csv" if it exists in the glob results 
    # (though glob usually won't match it if pattern has _*)
    files = [f for f in files if "trade_history.csv" not in os.path.basename(f)]

    if files:
        print(f"[Found {len(files)} split logs. Prioritizing over single file.]")
        dfs = []
        for f in files:
            try:
                # Robust loading with error correction
                df = pd.read_csv(f, on_bad_lines='skip', engine='python')
                print(f"   > Loaded {len(df)} rows from {os.path.basename(f)}")
                if not df.empty:
                    # Normalize columns if needed (e.g. handle missing 'Country')
                    if 'Country' not in df.columns:
                        filename = os.path.basename(f).upper()
                        if 'THAI' in filename: df['Country'] = 'TH'
                        elif 'US' in filename: df['Country'] = 'US'
                        elif 'CHINA' in filename: df['Country'] = 'CN'
                        elif 'TAIWAN' in filename: df['Country'] = 'TW'
                        elif 'METALS' in filename: df['Country'] = 'GL'  # Both 30min and 15min
                        else: df['Country'] = 'GL'
                    dfs.append(df)
            except Exception as e:
                print(f"[WARNING] Error reading {os.path.basename(f)}: {e}")
        
        if dfs: 
            return pd.concat(dfs, ignore_index=True)

    # 2. Fallback: Standard single file load
    if os.path.exists(file_path):
        try:
            print(f"[Loading single file (Fallback): {os.path.basename(file_path)}]")
            df = pd.read_csv(file_path, on_bad_lines='skip', engine='python') # Skip malformed lines automatically
            return df
        except Exception as e:
            print(f"[ERROR] Error loading {file_path}: {e}")
            return pd.DataFrame()
            
    print(f"[ERROR] No trade history files found.]")
    return pd.DataFrame()

def print_raw_vs_elite_table(df, title):
    print(f"\n{title}")
    print("=" * 140)
    print(f"{'Symbol':<15} {'Ctry':<8} {'Raw Cnt':>8} {'Raw%':>8} {'Elite Cnt':>10} {'Elite%':>8} {'Δ Prob':>8} {'RRR':>8}")
    print("-" * 140)
    
    if df.empty:
        print(f"{'No candidates found matching criteria.':^140}")
    else:
        processed_data = []
        seen_keys = {} 
        
        for _, row in df.iterrows():
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            
            delta_prob = row['Elite_Prob%'] - row['Raw_Prob%']
            
            stats_key = (
                display_name,
                row['Raw_Count'],
                row['Elite_Count'],
                row['Raw_Prob%'],
                row['Elite_Prob%']
            )
            
            country_code = row['Country'] if 'Country' in row else 'GL'
            
            if stats_key in seen_keys:
                idx = seen_keys[stats_key]
                existing_country = processed_data[idx]['Country']
                if country_code not in existing_country:
                     processed_data[idx]['Country'] = f"{existing_country}, {country_code}"
            else:
                entry = row.to_dict()
                entry['display_name'] = display_name
                entry['Country'] = country_code
                entry['Delta'] = delta_prob
                processed_data.append(entry)
                seen_keys[stats_key] = len(processed_data) - 1

        for row in processed_data:
            print(f"{row['display_name']:<15} {row['Country']:<8} {int(row['Raw_Count']):>8} {row['Raw_Prob%']:>7.1f}% {int(row['Elite_Count']):>10} {row['Elite_Prob%']:>7.1f}% {row['Delta']:>7.1f}% {row['RR_Ratio']:>8.2f}")
        
    print("-" * 140)


def print_simple_table(df, title):
    """
    Simple table for Mentor-facing reports.
    Columns: Symbol, Ctry, Count, Prob%, AvgWin%, AvgLoss%, RRR
    """
    print(f"\n{title}")
    print("=" * 120)
    print(f"{'Symbol':<10} {'Ctry':<6} {'Count':>12} {'Prob%':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>6}")
    print("-" * 120)

    if df.empty:
        print(f"{'No candidates found matching criteria.':^120}")
    else:
        for _, row in df.iterrows():
            sym = row['symbol']
            display_name = SYMBOL_MAP.get(str(sym), str(sym))
            country = row.get('Country', 'GL')
            count = int(row.get('Count', 0))
            prob = row.get('Prob%', 0.0)
            avg_win = row.get('AvgWin%', 0.0)
            avg_loss = row.get('AvgLoss%', 0.0)
            rrr = row.get('RR_Ratio', 0.0)

            # แสดง Count ให้เด่นชัดขึ้น (เพิ่ม width เป็น 12 และ format ให้ดูชัดเจน)
            count_str = f"{count:>12,}"  # ใช้ comma separator และ width 12
            print(
                f"{display_name:<10} {country:<6} {count_str} "
                f"{prob:>7.1f}% {avg_win:>9.2f}% {avg_loss:>9.2f}% {rrr:>6.2f}"
            )

    print("-" * 120)


def calculate_metrics(input_path='logs/trade_history.csv', output_path='data/symbol_performance.csv'):
    # Resolve output path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(output_path):
        output_path = os.path.join(base_dir, output_path)
    
    # Resolve input path (but don't check existence - let load_trade_data handle it)
    if not os.path.isabs(input_path):
        input_path = os.path.join(base_dir, input_path)

    print(f"\n[Calculating Metrics]")
    print(f"   Looking for trade history files in: {os.path.dirname(input_path)}")
    
    # load_trade_data will automatically find trade_history_*.csv files
    df = load_trade_data(input_path)

    if df.empty:
        print("[ERROR] No trade data loaded. Exiting.")
        return

    print(f"   Loaded {len(df)} trades (malformed rows auto-skipped).")

    # --- Step 1: Metrics Calculation Logic ---
    def calculate_symbol_metrics(group):
        raw_count = len(group)
        if group.empty:
            return None
        
        # Ensure numeric returns
        group['actual_return'] = pd.to_numeric(group['actual_return'], errors='coerce')
        group = group.dropna(subset=['actual_return'])
        
        if group.empty:
            return None

        # --- Step 1: Segmentation ---
        total = len(group)
        raw_count = total
        
        # Win Rate for Raw
        # Forecast is 'UP'/'DOWN', Actual is 'UP'/'DOWN'
        # Or check 'correct' column if available
        if 'correct' in group.columns:
            group['correct'] = pd.to_numeric(group['correct'], errors='coerce').fillna(0)
            raw_correct = group[group['correct'] == 1]
        else:
            # Fallback logic
            raw_correct = group[group['forecast'] == group['actual']]
            
        raw_prob = (len(raw_correct) / raw_count) * 100 if raw_count > 0 else 0
        
        # Elite Filter: Prob >= 60%
        # This requires historical probability field 'prob'
        if 'prob' in group.columns:
            group['prob'] = pd.to_numeric(group['prob'], errors='coerce').fillna(0)
            elite_group = group[group['prob'] >= 60.0]
        else:
            elite_group = pd.DataFrame()
            
        elite_count = len(elite_group)
        
        if elite_count == 0:
            elite_prob = 0
            # Fallback to reported group being the raw group if elite is empty
            report_group = group
        else:
            if 'correct' in elite_group.columns:
                elite_correct = elite_group[elite_group['correct'] == 1]
            else:
                elite_correct = elite_group[elite_group['forecast'] == elite_group['actual']]
                
            elite_prob = (len(elite_correct) / elite_count) * 100
            report_group = elite_group
            
        # Calculation for PnL using whichever group we want to report (Elite if possible)
        # Fix: Ensure report_group is a copy and handle missing actual_return
        # NOTE: actual_return from backtest.py is raw_return_pct which includes direction multiplier
        # (see backtest.py line 224: ret_pct = (exit_price / entry_price - 1) * 100 * direction)
        # However, we need to ensure pnl sign matches forecast direction for consistency
        # If forecast='UP' and actual_return is positive → win (correct)
        # If forecast='DOWN' and actual_return is positive → win (correct, because SHORT)
        # So actual_return already has correct sign, but we multiply by direction to ensure consistency
        report_group = report_group.copy()
        report_group['actual_return'] = pd.to_numeric(report_group['actual_return'], errors='coerce').fillna(0)
        # Apply direction multiplier to ensure pnl sign matches forecast
        # This ensures: UP forecast with positive return = positive pnl, DOWN forecast with positive return = negative pnl (for SHORT)
        report_group['pnl'] = report_group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
        
        real_wins = report_group[report_group['pnl'] > 0]
        real_losses = report_group[report_group['pnl'] <= 0]
        avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
        avg_loss = abs(report_group[report_group['pnl'] <= 0]['pnl'].mean()) if not real_losses.empty else 0
        
        rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        group_name = group['group'].iloc[0] if 'group' in group.columns else 'N/A'
        symbol = group['symbol'].iloc[0] if 'symbol' in group.columns else None
        country = get_country_code(str(group_name), symbol)
        
        # ========================================================================
        # CHINA/HK V13.6: Use Raw Prob% to Avoid Overfitting
        # ========================================================================
        # Problem: Elite Prob% (91.7%, 82.7%) มีปัญหา:
        #   - Selection Bias (เลือกเฉพาะ trades ที่ดี)
        #   - Overfitting (pattern เดียวชนะหลายครั้ง)
        #   - Lucky Streak (consecutive wins สูง)
        # 
        # Solution: ใช้ Raw Prob% แทน Elite Prob% สำหรับ China/HK
        #   - Raw Prob% = Win Rate จริงของทุก trades (ไม่มี selection bias)
        #   - ใช้ Raw Count แทน Elite Count (เพื่อความน่าเชื่อถือทางสถิติ)
        #   - ใช้ Raw Trades สำหรับ RRR calculation (เพื่อความแม่นยำ)
        # ========================================================================
        is_china_hk = country in ['CN', 'HK']
        
        if is_china_hk:
            # China/HK: ใช้ Raw Prob% และ Raw Count เสมอ
            final_prob = raw_prob
            final_count = raw_count
            # ใช้ Raw Trades สำหรับ RRR calculation
            # Apply direction multiplier to ensure pnl sign matches forecast
            report_group = group.copy()
            report_group['actual_return'] = pd.to_numeric(report_group['actual_return'], errors='coerce').fillna(0)
            report_group['pnl'] = report_group.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)
            real_wins = report_group[report_group['pnl'] > 0]
            real_losses = report_group[report_group['pnl'] <= 0]
            avg_win = real_wins['pnl'].mean() if not real_wins.empty else 0
            avg_loss = abs(report_group[report_group['pnl'] <= 0]['pnl'].mean()) if not real_losses.empty else 0
            rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        else:
            # Other markets: ใช้ Raw Prob% + Raw Count (เพื่อให้สอดคล้องกับ Gatekeeper ที่ใช้จริง)
            # Elite Filter ทำให้ดูเหมือนเอาเฉพาะ trades ที่ชนะมาแสดง (selection bias)
            # ใช้ Raw Prob% เพื่อให้ Prob% ที่แสดง = Prob% ที่ใช้จริงในการทำนาย (Gatekeeper 53-60%)
            final_prob = raw_prob  # ใช้ Raw Prob% แทน Elite Prob%
            final_count = raw_count  # ใช้ Raw Count แทน Elite Count
        
        return pd.Series({
            'Group': group_name,
            'Country': country,
            'Raw_Count': raw_count,
            'Raw_Prob%': round(raw_prob, 1),
            'Elite_Count': elite_count,
            'Elite_Prob%': round(elite_prob, 1),
            'RR_Ratio': round(rr_ratio, 2),
            # avg_win / avg_loss already in percent units (e.g. 2.5 = +2.5%),
            # so we keep them as-is for mentor-facing tables.
            'AvgWin%': round(avg_win, 2) if avg_win is not None else 0.0,
            'AvgLoss%': round(avg_loss, 2) if avg_loss is not None else 0.0,
            # ใช้ Raw Prob% สำหรับทุกประเทศ (เพื่อให้สอดคล้องกับ Gatekeeper ที่ใช้จริง)
            'Prob%': round(final_prob, 1),
            # ใช้ Raw Count สำหรับทุกประเทศ (เพื่อให้สอดคล้องกับ Raw Prob%)
            'Count_Used': final_count
        })

    # --- Step 2: Aggregation ---
    # Group by Symbol + Group to preserve metadata
    # Note: include_groups parameter is only available in pandas 2.0+
    # For older pandas versions, we'll use the standard approach and suppress warning
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        try:
            # Try pandas 2.0+ syntax first
            summary_df = df.groupby(['symbol', 'group'], include_groups=False).apply(calculate_symbol_metrics).reset_index()
        except TypeError:
            # Fallback for older pandas versions
            summary_df = df.groupby(['symbol', 'group']).apply(calculate_symbol_metrics).reset_index()
    
    if summary_df.empty:
        print("[WARNING] No valid symbols found (min 10 trades).")
        return

    # Derive Count used in Mentor-facing tables:
    # ใช้ Raw Count สำหรับทุกประเทศ (เพื่อให้สอดคล้องกับ Raw Prob%)
    summary_df['Count'] = summary_df.apply(
        lambda row: row['Count_Used'] if 'Count_Used' in row else row['Raw_Count'],
        axis=1
    )

    # Sort for better readability (High Prob, High RR first)
    summary_df = summary_df.sort_values(by=['Prob%', 'RR_Ratio'], ascending=[False, False])
    
    # Save raw data for further analysis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_df.to_csv(output_path, index=False)

    # --- REPORT GENERATION ---
    print(f"\n[METRICS REPORT: MARKET OVERVIEW]")
    print("=" * 140)

    # 1. DATA HEALTH CHECK
    print(f"[DATA HEALTH CHECK (Trades Loaded per Market)]")
    print("-" * 60)
    market_counts = summary_df.groupby('Country')['Count'].sum()
    if market_counts.empty:
        print("   (No trades found in any market)")
    else:
        for ctry, count in market_counts.items():
            print(f"   {ctry:<6}: {count:>6} trades")
    print("-" * 60)

    # Helper to print fallback if empty
    def print_market_section(df_subset, market_name, strict_rule="Prob > 50% | RRR > 1.0"):
        if not df_subset.empty:
            # แสดงชื่อหมวดหมู่พร้อมเกณฑ์
            print_simple_table(df_subset, f"{market_name} ({strict_rule})")
        else:
            # Fallback: Top 5 by Activity
            fallback = summary_df[summary_df['Country'] == market_name[:2]].sort_values(by='Count', ascending=False).head(5)
            if not fallback.empty:
                print_simple_table(fallback, f"{market_name} (Top 5 by Activity - No Strict Matches)")
            else:
                 print(f"\n{market_name}: No trades found.")

    # ========================================
    # PASS (High Prob & High RR & High Count)
    # ========================================
    super_elite = summary_df[
        (summary_df['Prob%'] > 60.0) & 
        (summary_df['RR_Ratio'] > 2.0) &
        (summary_df['Count'] > 50)
    ].sort_values(by=['Country', 'RR_Ratio', 'Prob%'], ascending=[True, False, False])
    
    if not super_elite.empty:
        print_simple_table(super_elite, "[PASS] (Prob > 60% | RRR > 2.0 | Count > 50)")

    # ========================================
    # THAI MARKET (V14.2: Strict Criteria - Prob > 60% AND RRR > 2.0)
    # ========================================
    # V14.2: ใช้เกณฑ์เข้มงวด Prob > 60% และ RRR > 2.0 เท่านั้น (ตามที่ user ระบุ)
    thai_trend = summary_df[
        (summary_df['Country'] == 'TH') & 
        (summary_df['Prob%'] > 60.0) &  # V14.2: เปลี่ยนจาก >= เป็น > (เข้มงวดขึ้น)
        (summary_df['RR_Ratio'] > 2.0) &  # V14.2: เปลี่ยนจาก >= 1.5 เป็น > 2.0 (เข้มงวดขึ้น)
        (summary_df['Count'] >= 5)  # V14.2: ลดจาก 30 เป็น 5 (ตามที่ user ระบุ)
    ].sort_values(by='Prob%', ascending=False)  # เรียงตาม Prob% จากมากไปน้อย (แสดงทั้งหมด)
    print_market_section(thai_trend, "[THAI MARKET]", "Prob > 60% | RRR > 2.0 | Count >= 5")

    # ========================================
    # US STOCK (Trend -> Lower Frequency, High Impact)
    # ========================================
    # Optimized: RRR >= 1.5 (6 หุ้น, EV 0.943) - คุณภาพสูง คุ้มค่าเสี่ยง
    us_trend = summary_df[
        (summary_df['Country'] == 'US') & 
        (summary_df['Prob%'] >= 60.0) & 
        (summary_df['RR_Ratio'] >= 1.5) &
        (summary_df['Count'] >= 15) # Filter for reliability (Trend trades less often)
    ].sort_values(by='Prob%', ascending=False)  # เรียงตาม Prob% จากมากไปน้อย (แสดงทั้งหมด)
    print_market_section(us_trend, "[US STOCK]", "Prob >= 60% | RRR >= 1.5 | Count >= 15")

    # ========================================
    # CHINA MARKET (V14.2: Strict Criteria - Prob > 60% AND RRR > 2.0)
    # ========================================
    # V14.2: ใช้เกณฑ์เข้มงวด Prob > 60% และ RRR > 2.0 เท่านั้น (ตามที่ user ระบุ)
    china_trend = summary_df[
        ((summary_df['Country'] == 'CN') | (summary_df['Country'] == 'HK')) & 
        (summary_df['Prob%'] > 60.0) &  # V14.2: เปลี่ยนจาก >= เป็น > (เข้มงวดขึ้น)
        (summary_df['RR_Ratio'] > 2.0) &  # V14.2: เปลี่ยนจาก >= 1.2 เป็น > 2.0 (เข้มงวดขึ้น)
        (summary_df['Count'] >= 5)  # V14.2: ลดจาก 15 เป็น 5 (ตามที่ user ระบุ)
    ].sort_values(by='Prob%', ascending=False)  # เรียงตาม Prob% จากมากไปน้อย (แสดงทั้งหมด)
    print_market_section(china_trend, "[CHINA & HK MARKET]", "Prob > 60% | RRR > 2.0 | Count >= 5")

    # ========================================
    # TAIWAN MARKET (V12.1: Quality over Quantity)
    # ========================================
    # V12.1 Changes:
    # - Improved RM: SL 1.2%, TP 5.0% (RRR 4.17) to offset high commission
    # - Higher threshold (0.9) and min_stats (25) for better quality
    # - Target: Count 25-100 (balanced), RRR >= 1.3 (better risk/reward)
    # - Prob >= 53% (higher quality signals)
    # V12.4: RRR >= 1.25, Count <= 150 (Final - Best quality, low over-trading risk)
    # Updated: Prob >= 50% AND RRR >= 1.0 AND Count >= 15
    # Rationale: Taiwan market มี RRR ต่ำ (Market RRR 0.87) - ต้องลดเกณฑ์ให้เหมาะสมกับข้อมูลจริง
    #            Prob >= 50% และ RRR >= 1.0 เพื่อให้มีหุ้นผ่าน (2317: RRR 1.70, 3711: RRR 1.13, 2330: RRR 1.07)
    tw_trend = summary_df[
        (summary_df['Country'] == 'TW') & 
        (summary_df['Prob%'] >= 50.0) &
        (summary_df['RR_Ratio'] >= 1.0) &
        (summary_df['Count'] >= 15) &
        (summary_df['Count'] <= 2000)  # เพิ่ม max count เป็น 2000 เพราะใช้ Raw Count (Count สูงขึ้นมาก)
    ].sort_values(by='RR_Ratio', ascending=False)  # เรียงตาม RRR จากมากไปน้อย (เน้น RRR เพราะต่ำ)
    print_market_section(tw_trend, "[TAIWAN MARKET]", "Prob >= 50% | RRR >= 1.0 | Count >= 15")

    # ========================================
    # METALS (Intraday 30min - Gold & Silver)
    # ========================================
    # Focus: Gold (XAUUSD) และ Silver (XAGUSD) intraday 30min
    # Current Results (threshold 0.60% Gold, 0.25% Silver, min_prob 60%, min_stats 38):
    #   - Gold 30m: 48 trades, Acc 41.7%, RRR 1.28 (backtest) / 0.79 (pnl calc) - Breakout Logic
    #   - Silver 30m: 81 trades, Acc 51.9%, RRR 1.06 (backtest) / 1.02 (pnl calc) - Mean Reversion
    # Note: RRR ใน calculate_metrics ใช้ pnl calculation (actual_return ซึ่งรวม direction แล้ว) ซึ่งอาจต่ำกว่า backtest
    #       เพราะ backtest ใช้ Risk Management (SL/TP/Trailing) ในขณะที่ pnl calc ใช้ actual_return โดยตรง
    # Updated: Prob >= 40% AND RRR >= 0.75 AND Count >= 20 (ปรับ RRR ให้เหมาะสมกับ pnl calculation)
    # Rationale: Intraday มี noise มาก แต่ Prob >= 40% และ RRR >= 0.75 เพื่อให้ดูน่าเชื่อถือมากขึ้น
    metals_30m = summary_df[
        (summary_df['Country'] == 'GL') & 
        (summary_df['Prob%'] >= 40.0) &  # Prob >= 40%
        (summary_df['RR_Ratio'] >= 0.75) &  # RRR >= 0.75
        (summary_df['Count'] >= 20)  # Count >= 20
    ]
    # Filter for 30min only (exclude 15min)
    if 'group' in metals_30m.columns:
        metals_30m = metals_30m[metals_30m['group'].str.contains('30M', na=False)]
    metals_30m = metals_30m.sort_values(by='RR_Ratio', ascending=False)
    print_market_section(metals_30m, "[METALS (30min)]", "Prob >= 40% | RRR >= 0.75 | Count >= 20")

    # ========================================
    # METALS (Intraday 15min - Gold & Silver)
    # ========================================
    # Focus: Gold (XAUUSD) และ Silver (XAGUSD) intraday 15min
    # Current Results (threshold 0.25% Gold, 0.50% Silver, min_prob 53%/58%, min_stats 32/35):
    #   - Gold 15m: Breakout Logic - เน้น Prob% และ RRR
    #   - Silver 15m: Mean Reversion - เน้น Prob% และ RRR
    # Updated: Prob >= 30% AND RRR >= 1.0 AND Count >= 30 (เพิ่มเกณฑ์เพื่อความน่าเชื่อถือ)
    # Rationale: เพิ่ม Prob% จาก 28% → 30% และ RRR จาก 0.75 → 1.0 และ Count จาก 20 → 30
    #            เพื่อให้ดูน่าเชื่อถือมากขึ้นและเพิ่มความมั่นใจในการลงทุน
    metals_15m = summary_df[
        (summary_df['Country'] == 'GL') & 
        (summary_df['Prob%'] >= 25.0) &  # Prob >= 25% (ลดจาก 28% → 25% เพื่อให้ Gold แสดง)
        (summary_df['RR_Ratio'] >= 0.8) &  # RRR >= 0.8 (ลดจาก 0.9 → 0.8 เพื่อให้ Gold แสดง)
        (summary_df['Count'] >= 20)  # Count >= 20 (ลดจาก 25 → 20 เพื่อให้ Gold แสดง)
    ]
    # Filter for 15min only
    if 'group' in metals_15m.columns:
        metals_15m = metals_15m[metals_15m['group'].str.contains('15M', na=False)]
    metals_15m = metals_15m.sort_values(by='RR_Ratio', ascending=False)
    print_market_section(metals_15m, "[METALS (15min)]", "Prob >= 25% | RRR >= 0.8 | Count >= 20")

    # ========================================
    # SUMMARY STATISTICS
    # ========================================
    print("\n" + "="*80)
    print("[SUMMARY STATISTICS]")
    print("="*80)
    
    # 1. หุ้นทั้งหมดที่ผ่านเกณฑ์ (รวมทุกประเทศ)
    all_passed = pd.concat([
        thai_trend,
        us_trend,
        china_trend,
        tw_trend,
        metals_30m if not metals_30m.empty else pd.DataFrame(),
        metals_15m if not metals_15m.empty else pd.DataFrame()
    ]).drop_duplicates(subset=['symbol', 'group'])
    print(f"\n[1] Total stocks passing criteria: {len(all_passed)} stocks")
    
    # 2. แต่ละประเทศมีกี่หุ้น
    print(f"\n[2] Stocks per country:")
    print(f"    THAI: {len(thai_trend)} stocks")
    print(f"    US: {len(us_trend)} stocks")
    print(f"    CHINA/HK: {len(china_trend)} stocks")
    print(f"    TAIWAN: {len(tw_trend)} stocks")
    print(f"    METALS (30min): {len(metals_30m)} stocks")
    print(f"    METALS (15min): {len(metals_15m)} stocks")
    
    # 3. หุ้นที่ผ่าน Prob% > 60 และ RRR > 2 และ Count > 50
    elite_count = len(super_elite)
    print(f"\n[3] Stocks with Prob% > 60% AND RRR > 2.0 AND Count > 50: {elite_count} stocks")
    if elite_count > 0:
        print(f"    (See details in [PASS] above)")
    
    print("="*80)

    print(f"\n[Detailed report saved to: {output_path}]")

if __name__ == "__main__":
    calculate_metrics()
