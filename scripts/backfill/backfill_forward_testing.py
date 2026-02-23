#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backfill_forward_testing.py — Reconstruct Forward Testing from a Given Date
============================================================================
อ้างอิง Master_Pattern_Stats_NewLogic.csv สำหรับ pattern lookup
ดึงข้อมูลเฉพาะ ~300 bars ต่อ stock (เพียงพอสำหรับ threshold + signal)

วิธีทำงาน:
  1. โหลด Master_Pattern_Stats_NewLogic.csv เป็น pattern database
  2. ดึง ~300 bars ต่อ stock (ใช้ cache)
  3. สำหรับแต่ละ trading day (Feb 12 → yesterday):
     a. คำนวณ threshold (20d SD, 252d SD, floor)
     b. สร้าง active pattern จาก signals ล่าสุด (Dynamic Lookback)
     c. ค้นหา pattern ที่ตรงใน master stats → Best Fit Selection
     d. เช็ค actual N+1 return
     e. เขียนลง performance_log.csv (Anti-Overlapping: 1 result/stock/day)

Usage:
  python scripts/backfill_forward_testing.py
  python scripts/backfill_forward_testing.py --start-date 2026-02-12
"""

import sys
import os
import time
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from tvDatafeed import TvDatafeed, Interval
import config
from core.data_cache import get_data_with_cache

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Performance log
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'performance_log.csv')
MASTER_STATS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'Master_Pattern_Stats_NewLogic.csv')

COLUMNS = [
    'scan_date', 'target_date', 'symbol', 'exchange', 'pattern',
    'forecast', 'prob', 'conf', 'stats', 'price_at_scan',
    'change_pct', 'threshold', 'avg_return', 'total_bars',
    'actual', 'price_actual', 'correct', 'last_update'
]

MIN_MATCHES = config.MIN_MATCHES_THRESHOLD
MIN_PROB = config.MIN_PROB_THRESHOLD

# Market config (same floors as engines)
MARKET_FLOORS = {
    'GROUP_A_THAI':       0.01,
    'GROUP_B_US':         0.006,
    'GROUP_C1_GOLD_30M':  0.003,
    'GROUP_C2_GOLD_15M':  0.003,
    'GROUP_D1_SILVER_30M':0.003,
    'GROUP_D2_SILVER_15M':0.003,
    'GROUP_C_CHINA_HK':   0.008,
    'GROUP_D_TAIWAN':     0.009,
}

# Direction logic per market (same as engines)
# Mean Reversion: pattern ends '+' → forecast DOWN, '-' → UP
# Trend Following: pattern ends '+' → forecast UP, '-' → DOWN
MARKET_DIRECTION = {
    'GROUP_A_THAI':       'reversion',
    'GROUP_B_US':         'trend',
    'GROUP_C1_GOLD_30M':  'reversion',
    'GROUP_C2_GOLD_15M':  'reversion',
    'GROUP_D1_SILVER_30M':'reversion',
    'GROUP_D2_SILVER_15M':'reversion',
    'GROUP_C_CHINA_HK':   'reversion',
    'GROUP_D_TAIWAN':     'trend',
}


def load_master_stats():
    """โหลด Master Stats CSV เป็น lookup dict: {symbol: [{pattern, count, ...}]}"""
    if not os.path.exists(MASTER_STATS):
        print(f"❌ Master stats not found: {MASTER_STATS}")
        sys.exit(1)

    df = pd.read_csv(MASTER_STATS)
    # บังคับ Symbol เป็น string เพื่อป้องกัน Bug เลข 2330 vs '2330'
    df['Symbol'] = df['Symbol'].astype(str)
    print(f"📊 Loaded master stats: {len(df)} rows, {df['Symbol'].nunique()} symbols")

    # Build lookup: symbol → list of {pattern, count, ...}
    lookup = defaultdict(list)
    for _, row in df.iterrows():
        lookup[row['Symbol']].append({
            'pattern': row['Pattern'],
            'count': row['Count'],
            'category': row.get('Category', 'Unknown'),
            'pattern_name': row.get('Pattern_Name', 'Unknown'),
            'bars': row.get('Bars', 0),
            'max_streak_pos': row.get('Max_Streak_Pos', 0),
            'max_streak_neg': row.get('Max_Streak_Neg', 0),
            # New Stats (V8.0 Pure Stats)
            'next_up': row.get('Next_Up', 0),
            'next_down': row.get('Next_Down', 0),
            'next_neutral': row.get('Next_Neutral', 0),
            'reliability': row.get('Reliability', 0.0)
        })

    return lookup


def calculate_threshold(pct_change, floor):
    """Threshold = MAX(20d SD, 252d SD, floor)"""
    short_std = pct_change.rolling(20).std()
    long_std = pct_change.rolling(252).std()
    effective = np.maximum(short_std, long_std.fillna(0))
    effective = np.maximum(effective, floor)
    return effective


def get_active_pattern(pct_change, effective_std, end_idx, max_length=7):
    """
    Dynamic Lookback: scan backward from end_idx
    สร้าง active pattern จาก signals ล่าสุด
    หยุดเมื่อเจอ neutral day
    Anti-Overlapping: ได้ pattern เดียวต่อ stock
    """
    signals = []
    for i in range(end_idx, max(end_idx - max_length - 1, -1), -1):
        if i < 0:
            break
        ret = pct_change.iloc[i]
        thresh = effective_std.iloc[i]

        if pd.isna(ret) or pd.isna(thresh):
            break

        if ret > thresh:
            signals.insert(0, '+')
        elif ret < -thresh:
            signals.insert(0, '-')
        else:
            break  # neutral = จุดตัด

    if not signals:
        return None
    return ''.join(signals)


def select_best_fit(active_pattern, symbol_stats, min_count=3):
    """
    Best Fit Selection (V8.0 — Highest Probability):
    System generates all valid sub-patterns from the active pattern (longest -> shortest).
    It checks Master Stats for each.
    
    Selection Criteria:
    1. Count >= min_count (Screening)
    2. Highest 'Reliability' (Probability)
    3. Tie-breaker: Longest Pattern
    """
    if not active_pattern or not symbol_stats:
        return None

    # Build lookup
    stats_lookup = {s['pattern']: s for s in symbol_stats}
    
    candidates = []

    # Collect all valid candidates
    for length in range(len(active_pattern), 0, -1):
        sub = active_pattern[-length:]
        if sub not in stats_lookup:
            continue
        
        info = stats_lookup[sub]
        
        # 1. Screen by Count
        if info['count'] < min_count:
            continue
            
        # 2. Calculate Reliability (if not present, estimate)
        # Use 'reliability' from CSV if available, else calc from Next_Up/Next_Down
        if 'reliability' in info and info['reliability'] > 0:
            prob = info['reliability']
        else:
            # Fallback calc
            total = info.get('next_up', 0) + info.get('next_down', 0) + info.get('next_neutral', 0)
            if total > 0:
                # Reliability = Max(Up, Down) / Total
                prob = max(info.get('next_up', 0), info.get('next_down', 0)) / total * 100
            else:
                prob = 0
        
        candidates.append({
            'pattern': sub,
            'info': info,
            'prob': prob,
            'length': length
        })
    
    if not candidates:
        return None
        
    # Sort Candidates:
    # 1. Probability (Descending)
    # 2. Length (Descending) - Tie-breaker
    candidates.sort(key=lambda x: (-x['prob'], -x['length']))
    
    # Return best candidate's stats
    return candidates[0]['info']


def determine_forecast(pattern_stats):
    """
    Determine direction from Master Stats (Pure Stats Logic)
    Case 1: Up > Down -> Forecast UP
    Case 2: Down > Up -> Forecast DOWN
    Case 3: Equal -> NEUTRAL (No trade)
    """
    if not pattern_stats:
        return None

    n_up = pattern_stats.get('next_up', 0)
    n_down = pattern_stats.get('next_down', 0)
    
    # Simple Majority Vote
    if n_up > n_down:
        return 'UP'
    elif n_down > n_up:
        return 'DOWN'
    
    return None # Neutral or Zero


def main():
    parser = argparse.ArgumentParser(description='Backfill forward testing data')
    parser.add_argument('--start-date', type=str, default='2026-02-12',
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='End date (YYYY-MM-DD), default: yesterday')
    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("=" * 80)
    print("🔄 BACKFILL FORWARD TESTING (Using Master Stats)")
    print(f"   📅 Range: {start_date} → {end_date}")
    print(f"   📊 Reference: Master_Pattern_Stats_NewLogic.csv")
    print(f"   🧩 Anti-Overlapping: 1 pattern per stock per day")
    print("=" * 80)

    # Load master stats
    master_stats = load_master_stats()

    # Init TvDatafeed
    tv_user = os.getenv("TV_USERNAME", "")
    tv_pass = os.getenv("TV_PASSWORD", "")
    try:
        tv = TvDatafeed(tv_user, tv_pass)
    except Exception:
        tv = TvDatafeed()

    os.makedirs(LOG_DIR, exist_ok=True)

    all_records = []
    stats = {'predictions': 0, 'verified': 0, 'correct': 0, 'incorrect': 0}
    total_assets = sum(len(g.get('assets', [])) for g in config.ASSET_GROUPS.values())
    asset_count = 0

    for group_key, group_cfg in config.ASSET_GROUPS.items():
        floor = MARKET_FLOORS.get(group_key, 0.01)
        direction_logic = MARKET_DIRECTION.get(group_key, 'reversion')
        assets = group_cfg.get('assets', [])
        interval = group_cfg.get('interval', Interval.in_daily)
        description = group_cfg.get('description', group_key)

        print(f"\n{'─' * 60}")
        print(f"🏷️  {description} | {direction_logic.upper()} | Floor: {floor*100:.1f}%")
        print(f"{'─' * 60}")

        for asset in assets:
            symbol = asset['symbol']
            exchange = asset['exchange']
            display_name = asset.get('name', symbol)
            asset_count += 1

            # ตรวจว่า symbol อยู่ใน master stats ไหม
            symbol_stats = master_stats.get(display_name, [])
            if not symbol_stats:
                # ลอง symbol ด้วย
                symbol_stats = master_stats.get(symbol, [])
            if not symbol_stats:
                print(f"  ⏭️  [{asset_count}/{total_assets}] {display_name}: not in master stats")
                continue

            try:
                # เพิ่มเป็น 1000 bars เพื่อให้วอร์มอัพ 252d SD ได้แน่นอน
                df = get_data_with_cache(
                    tv=tv,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    full_bars=1000,
                    delta_bars=100
                )

                if df is None or df.empty or len(df) < 300:
                    print(f"  ⏭️  [{asset_count}/{total_assets}] {display_name}: insufficient data ({len(df) if df is not None else 0} bars)")
                    continue

                pct_change = df['close'].pct_change()
                effective_std = calculate_threshold(pct_change, floor)

                # หา trading days ในช่วงที่ต้องการ
                dates = df.index.normalize().unique().sort_values()
                mask = (dates >= pd.Timestamp(start_date)) & (dates <= pd.Timestamp(end_date))
                trading_days = dates[mask].tolist()

                if not trading_days:
                    print(f"  ⏭️  [{asset_count}/{total_assets}] {display_name}: no trading days in range")
                    continue

                symbol_predictions = 0

                for scan_day in trading_days:
                    # หา index ของ scan_day ใน df
                    scan_mask = df.index.normalize() == scan_day
                    scan_indices = df.index[scan_mask]
                    if len(scan_indices) == 0:
                        continue

                    scan_idx = df.index.get_loc(scan_indices[-1])
                    if isinstance(scan_idx, slice):
                        scan_idx = scan_idx.stop - 1

                    if scan_idx < 252:
                        continue  # ต้อง warmup

                    scan_date_str = scan_day.strftime('%Y-%m-%d')
                    
                    # 1. สร้าง active pattern (Dynamic Lookback)
                    active_pattern = get_active_pattern(pct_change, effective_std, scan_idx)

                    if not active_pattern:
                        continue  # วันนี้ neutral → ไม่มี pattern

                    # === FINAL LOGIC — AVERAGE OF WINNING PATTERNS ===
                    
                    # 2. สร้าง Suffixes ทั้งหมด (จากยาวไปสั้น)
                    suffixes = []
                    for i in range(len(active_pattern)):
                        sub = active_pattern[i:]
                        if sub:
                            suffixes.append(sub)

                    # 2. ค้นหาผู้ชนะราย Pattern (Pattern-Level Decision)
                    pattern_stats_map = {s['pattern']: s for s in symbol_stats}
                    p_winners = []
                    n_winners = []
                    
                    for sub_pat in suffixes:
                        if sub_pat not in pattern_stats_map:
                            continue
                            
                        info = pattern_stats_map[sub_pat]
                        if info['count'] < MIN_MATCHES:
                            continue
                            
                        p_win_i = info.get('next_up', 0)
                        n_win_i = info.get('next_down', 0)
                        
                        # Rule: เสมอ หรือไม่มีข้อมูลฝั่งชนะ -> ข้าม
                        if p_win_i > n_win_i:
                            p_winners.append({'count': p_win_i, 'total': info.get('bars', 0), 'pattern': sub_pat})
                        elif n_win_i > p_win_i:
                            n_winners.append({'count': n_win_i, 'total': info.get('bars', 0), 'pattern': sub_pat})

                    if not p_winners and not n_winners:
                        continue

                    # 3. รวมค่าพลังโหวต (Aggregation based on winners)
                    total_up_win = sum(d['count'] for d in p_winners)
                    total_down_win = sum(d['count'] for d in n_winners)

                    # 4. ตัดสินฝั่งชนะของวันนี้
                    if total_up_win > total_down_win:
                        winning_side = 'P'
                        winning_patterns = p_winners
                        forecast = 'UP'
                    elif total_down_win > total_up_win:
                        winning_side = 'N'
                        winning_patterns = n_winners
                        forecast = 'DOWN'
                    else:
                        continue # Tie = Skip
                    
                    # Probability Calculation: Average of Individual Probabilities (Consensus)
                    pattern_probs = []
                    for d in winning_patterns:
                        # d contains: 'count' (win count), 'total' (total bars), 'pattern'
                        # To find the true probability of this pattern we need its original up/down splits.
                        info_d = pattern_stats_map[d['pattern']]
                        total_events_i = info_d.get('next_up', 0) + info_d.get('next_down', 0)
                        p_i = (d['count'] / total_events_i * 100) if total_events_i > 0 else 0
                        pattern_probs.append(p_i)
                    
                    avg_prob = np.mean(pattern_probs) if pattern_probs else 0.0
                    final_prob = avg_prob

                    # บันทึกค่า
                    prob = round(final_prob, 1)
                    best_fit_pattern = suffixes[0]
                    count = int(max(total_up_win, total_down_win))

                    # 5. หา target_date (N+1)
                    all_dates = dates.tolist()
                    try:
                        scan_day_idx = all_dates.index(scan_day)
                    except ValueError:
                        continue

                    if scan_day_idx + 1 >= len(all_dates):
                        continue

                    target_day = all_dates[scan_day_idx + 1]
                    target_date_str = target_day.strftime('%Y-%m-%d')

                    # 6. หาผลจริง (actual)
                    target_mask = df.index.normalize() == target_day
                    target_data = df[target_mask]
                    if target_data.empty:
                        actual, price_actual = 'PENDING', None
                    else:
                        price_actual = target_data['close'].iloc[-1]
                        price_scan = df['close'].iloc[scan_idx]
                        actual_change = (price_actual - price_scan) / price_scan * 100

                        thresh_pct = effective_std.iloc[scan_idx] * 100
                        if actual_change > thresh_pct:
                            actual = 'UP'
                        elif actual_change < -thresh_pct:
                            actual = 'DOWN'
                        else:
                            actual = 'NEUTRAL'

                    # 7. เช็ค correct/incorrect
                    correct = None
                    if actual not in ('PENDING',):
                        if actual == 'NEUTRAL':
                            correct = 0  # Rule 4: NEUTRAL = LOSS
                        elif actual == forecast:
                            correct = 1
                        else:
                            correct = 0

                    # Price & threshold info
                    price_scan = df['close'].iloc[scan_idx]
                    change_pct = pct_change.iloc[scan_idx] * 100 if not pd.isna(pct_change.iloc[scan_idx]) else 0
                    threshold_pct = effective_std.iloc[scan_idx] * 100

                    record = {
                        'scan_date': scan_date_str,
                        'target_date': target_date_str,
                        'symbol': display_name,
                        'exchange': exchange,
                        'pattern': best_fit_pattern,
                        'forecast': forecast,
                        'prob': prob, # ค่า SCORE (Average)
                        'conf': prob, # โชว์ SCORE ซ้ำในช่อง CONF
                        'stats': count,
                        'price_at_scan': round(price_scan, 2),
                        'change_pct': round(change_pct, 2),
                        'threshold': round(threshold_pct, 2),
                        'avg_return': round(change_pct, 2),
                        'total_bars': int(np.mean([d['bars'] for d in pattern_decisions if d['side'] == winning_side])),
                        'actual': actual,
                        'price_actual': round(price_actual, 2) if price_actual else None,
                        'correct': correct,
                        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    all_records.append(record)
                    stats['predictions'] += 1
                    symbol_predictions += 1

                    if correct is not None:
                        stats['verified'] += 1
                        if correct == 1:
                            stats['correct'] += 1
                        else:
                            stats['incorrect'] += 1

                if symbol_predictions > 0:
                    print(f"  ✅ [{asset_count}/{total_assets}] {display_name:<12} | {symbol_predictions} predictions | {len(trading_days)} days")
                else:
                    sys.stdout.write(f"\r  ⏭️  [{asset_count}/{total_assets}] {display_name:<12} | no signal in range   ")
                    sys.stdout.flush()

            except Exception as e:
                print(f"  ❌ [{asset_count}/{total_assets}] {display_name}: {e}")

            time.sleep(0.2)

    # ==========================================
    # Save to performance_log.csv
    # ==========================================
    if all_records:
        df_new = pd.DataFrame(all_records, columns=COLUMNS)

        # Anti-overlapping: 1 record per (scan_date, symbol)
        # ถ้ามีหลาย pattern ใน 1 วัน → เลือก count สูงสุด
        df_new = df_new.sort_values('stats', ascending=False).drop_duplicates(
            subset=['scan_date', 'symbol'], keep='first'
        )

        # Merge with existing log
        if os.path.exists(LOG_FILE):
            df_existing = pd.read_csv(LOG_FILE)
            if not df_existing.empty:
                merge_cols = ['scan_date', 'symbol', 'pattern', 'target_date']
                existing_keys = set(df_existing[merge_cols].apply(tuple, axis=1))
                new_keys = df_new[merge_cols].apply(tuple, axis=1)
                df_new = df_new[~new_keys.isin(existing_keys)]
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
        else:
            df_combined = df_new

        df_combined = df_combined.sort_values(['scan_date', 'symbol']).reset_index(drop=True)
        df_combined.to_csv(LOG_FILE, index=False, encoding='utf-8-sig')

        accuracy = (stats['correct'] / stats['verified'] * 100) if stats['verified'] > 0 else 0

        print(f"\n\n{'=' * 60}")
        print(f"✅ BACKFILL COMPLETE")
        print(f"{'=' * 60}")
        print(f"   📅 Range: {start_date} → {end_date}")
        print(f"   📊 Total predictions: {stats['predictions']}")
        print(f"   ✅ Verified: {stats['verified']}")
        print(f"       ✅ Correct: {stats['correct']}")
        print(f"       ❌ Incorrect: {stats['incorrect']}")
        print(f"   📈 Accuracy: {accuracy:.1f}%")
        print(f"   💾 Saved: {LOG_FILE}")
        print(f"   📝 Total log records: {len(df_combined)}")

        # Summary by date
        print(f"\n{'─' * 40}")
        print("📆 Summary by Date:")
        for date, grp in df_combined.groupby('scan_date'):
            verified = grp[grp['correct'].notna()]
            correct_n = verified[verified['correct'] == 1].shape[0]
            total_v = len(verified)
            acc = (correct_n / total_v * 100) if total_v > 0 else 0
            print(f"  {date} | {len(grp):>3} predictions | {correct_n}/{total_v} correct ({acc:.0f}%)")
    else:
        print("\n⚠️  No predictions generated")


if __name__ == '__main__':
    main()
