#!/usr/bin/env python3
import sys
import os
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Configure paths to project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import config
from core.data_cache import get_data_with_cache
from processor import analyze_asset

def print_header(text):
    print("\n" + "=" * 80)
    print(f"📄 {text}")
    print("=" * 80)

def view_report(symbol):
    print(f"🚀 Generating Deep Dive Report for: {symbol} ...")
    
    # 1. Find Asset Config
    asset_info = None
    for group in config.ASSET_GROUPS.values():
        for asset in group['assets']:
            if asset['symbol'] == symbol:
                asset_info = asset
                break
        if asset_info: break
    
    if not asset_info:
        # Fallback for manual symbol
        print(f"⚠️ Symbol {symbol} not found in config. Using defaults (SET).")
        asset_info = {'symbol': symbol, 'exchange': 'SET'}
        interval = Interval.in_daily
    else:
        # Find interval from group
        for group in config.ASSET_GROUPS.values():
            if asset_info in group['assets']:
                interval = group['interval']
                break

    # 2. Fetch Data
    tv = TvDatafeed()
    df = get_data_with_cache(tv, asset_info['symbol'], asset_info['exchange'], interval, 5000, 50)
    
    if df is None or df.empty:
        print("❌ Error: No data found.")
        return

    # 3. Analyze Patterns
    # We use processor.py to get the BEST pattern
    results = analyze_asset(df, symbol=symbol)
    
    if not results:
        print("❌ No clear pattern found (Noise/Flat).")
        # Debug: Check volatility
        close = df['close']
        change = close.pct_change().iloc[-1] * 100
        
        # Recalculate threshold to see why it failed
        pct_change = close.pct_change()
        short_term_std = pct_change.rolling(window=20).std()
        long_term_std = pct_change.rolling(window=252).std()
        long_term_floor = long_term_std * 0.50
        effective_std = np.maximum(short_term_std, long_term_floor.fillna(0))
        threshold = effective_std.iloc[-1] * 1.25 * 100
        
        print(f"   Last Change: {change:.2f}%")
        print(f"   Threshold:   ±{threshold:.2f}% (Price change must exceed this)")
        return

    # 4. Display Report
    # Sort results by probability (prob or acc_score)
    results.sort(key=lambda x: x.get('prob', x.get('acc_score', 0)), reverse=True)
    
    print_header(f"PART 1: MASTER PATTERN STATS (V4.4 Consensus) - {symbol}")
    print(f"Price: {df['close'].iloc[-1]:.2f}  |  Threshold: ±{results[0].get('threshold', 0):.2f}%")
    print("-" * 120)
    print(f"{'Symbol':<10} {'Predict':^10} {'Exp.Ret':>8} {'Prob%':>9} {'Samples':>12}")
    print("-" * 75)
    
    for res in results:
        # 1. Prepare Data
        pattern_str = res.get('pattern', '')
        forecast_label = res.get('forecast', '')
        direction_sym = "🟢 UP" if forecast_label == "UP" else "🔴 DOWN"
        exp_ret = f"{res.get('avg_return', 0.0):+.2f}%"
        
        # Consistent key for probability/score
        prob_val = res.get('prob', res.get('acc_score', 0.0))
        prob_str = f"{prob_val:.1f}%"
        
        samples = int(res.get('winning_count', res.get('total_events', 0)))
        
        print(f"{symbol:<11} {direction_sym:<11} {exp_ret:>8} {prob_str:>9} {samples:>12}")

    print("-" * 75)
    
    # 4b. Show Detailed Consensus Breakdown (New V4.4.7 Feature - Table View)
    if 'breakdown' in results[0] and results[0]['breakdown']:
        print("\n🔍 CONSENSUS BREAKDOWN (Raw Voting Weights):")
        print("-" * 80)
        print(f"{'Suffix Pattern':<18} | {'UP (+)':>10} | {'DOWN (-)':>10} | {'Winner':^10}")
        print("-" * 80)
        
        parts = results[0]['breakdown'].split('; ')
        for part in parts:
            # Format -> Suffix:Win/Other(Tag)
            try:
                pattern_part = part.split(':')[0]
                numbers_part = part.split(':')[1] # "50/30(P)"
                counts_str = numbers_part.split('(')[0] # "50/30"
                tag = numbers_part.split('(')[1].replace(')', '') # "P", "N", or "T"
                
                v1, v2 = map(int, counts_str.split('/'))
                
                is_weak = "W" in tag
                w_label = " (Weak)" if is_weak else ""
                
                if tag.startswith('P'):
                    up_c, down_c = v1, v2
                    winner_label = f"🟢 UP{w_label}"
                elif tag.startswith('N'):
                    up_c, down_c = v2, v1
                    winner_label = f"🔴 DOWN{w_label}"
                else:
                    up_c, down_c = v1, v2
                    winner_label = f"⚪ TIE{w_label}"
                
                print(f"{pattern_part:<18} | {up_c:>10} | {down_c:>10} | {winner_label:^10}")
            except Exception as e:
                print(f"  {part}")
        print("-" * 80)
    
    # 5. Streak Profile (Simplified for V3.4)
    print_header("PART 2: STREAK PROFILE (Momentum)")
    # Calculate current streak
    closes = df['close'].values
    streak_type = "UP" if closes[-1] > closes[-2] else "DOWN"
    streak_len = 0
    for i in range(len(closes)-1, 0, -1):
        if (closes[i] > closes[i-1] and streak_type == "UP") or \
           (closes[i] < closes[i-1] and streak_type == "DOWN"):
            streak_len += 1
        else:
            break
            
    print(f"Current Streak: {streak_type} x {streak_len} Days")
    print("(Note: Full historical streak stats integration coming in V3.5)")
    
    # 6. Show the Math (Verification)
    if 'breakdown' in results[0] and results[0]['breakdown']:
        print("\n🎯 FINAL DECISION MATH:")
        parts = results[0]['breakdown'].split('; ')
        up_wins = []
        down_wins = []
        for part in parts:
            try:
                # Suffix:Win/Other(Tag)
                counts = part.split(':')[1].split('(')[0]
                tag = part.split('(')[1].replace(')', '')
                
                # Rule: Skip Weak (W) and Ties (T)
                if 'W' in tag or 'T' in tag:
                    continue
                    
                win_c, other_c = map(int, counts.split('/'))
                if tag == 'P': up_wins.append((win_c, other_c))
                elif tag == 'N': down_wins.append((win_c, other_c))
            except: continue
        
        sum_up = sum(w[0] for w in up_wins)
        sum_down = sum(w[0] for w in down_wins)
        
        if results[0]['forecast_label'] == 'UP':
            vote_weight = sum_up
            if not down_wins:
                # Single side: Base = All events in winning patterns
                denominator = sum(w[0] + w[1] for w in up_wins)
                calc_str = f"{vote_weight} / {denominator} (Total Samples)"
            else:
                # Multi side: Base = Sum of winning weights from both sides
                denominator = sum_up + sum_down
                calc_str = f"{sum_up} / ({sum_up} + {sum_down})"
        else:
            vote_weight = sum_down
            if not up_wins:
                denominator = sum(w[0] + w[1] for w in down_wins)
                calc_str = f"{vote_weight} / {denominator} (Total Samples)"
            else:
                denominator = sum_up + sum_down
                calc_str = f"{sum_down} / ({sum_up} + {sum_down})"
        
        print(f"   Vote Weight (UP)    : {sum_up}")
        print(f"   Vote Weight (DOWN)  : {sum_down}")
        print(f"   Denominator (Base)  : {denominator}")
        print(f"   Calculation         : {calc_str} = {results[0]['acc_score']:.1f}% Prob%")
        print("-" * 50)
        print("💡 Note: Losing side occurrences are included in Denominator base")
        print("   to ensure realistic probability (Weight != Occurrences)")

def view_all_report():
    file_path = 'data/forecast_tomorrow.csv'
    if not os.path.exists(file_path):
        print("❌ No daily report data found. Please run 'python3 main.py' first.")
        return

    df = pd.read_csv(file_path)
    if df.empty:
        print("❌ No patterns found in the latest run.")
        return

    # Sort by Probability (acc_score)
    df = df.sort_values(by=['acc_score', 'total_events'], ascending=[False, False])

    print_header("DAILY V4.4 CONSENSUS REPORT (ALL SYMBOLS)")
    print(f"{'Symbol':<10} {'Chg%':>8} {'Thresh%':>10} {'Forecast':^10} {'Exp.Ret':>8} {'Score':>7} {'Weight(P/N)'}")
    print("-" * 85)

    for _, row in df.iterrows():
        # Prepare Data
        sym = row['symbol']
        price = row['price']
        chg = f"{row['change_pct']:>7.2f}%"
        thresh = f"±{row['threshold']:.2f}%"
        
        # Construct symbolic forecast (🟢 / 🔴)
        forecast_label = row['forecast_label']
        direction_sym = "🟢 UP" if forecast_label == "UP" else "🔴 DOWN"
        
        exp_ret = f"{row.get('avg_return', 0.0):+.2f}%"
        prob = row['acc_score']
        
        total_p = int(row.get('total_p', 0))
        total_n = int(row.get('total_n', 0))
        stats = f"{total_p}/{total_n}"

        print(f"{sym:<11} {chg:>8} {thresh:>10} {direction_sym:>10} {exp_ret:>8} {prob:>7.1f} {stats:>20}")
    
    print("-" * 85)
    print(f"Total: {len(df)} symbols")

    # ==========================================
    # SECTION 2: DETAILED PATTERN BREAKDOWN (Per Symbol)
    # ==========================================
    print("\n\n" + "=" * 80)
    print("📄 SECTION 2: DETAILED PATTERN BREAKDOWN (Per Symbol)")
    print("=" * 80)
    
    # Sort data correctly to align with summary
    df = df.reset_index(drop=True)
    
    for idx, row in df.iterrows():
        sym = row['symbol']
        breakdown_str = row.get('breakdown', '')
        
        if pd.isna(breakdown_str) or not breakdown_str:
            continue
            
        parts = breakdown_str.split('; ')
        pattern_data = []
        
        for part in parts:
            try:
                pattern_part = part.split(':')[0]
                display_pat = pattern_part.replace('+', 'P').replace('-', 'N')
                
                numbers_part = part.split(':')[1]
                stats = numbers_part.split('(')[0]
                winner_tag = numbers_part.split('(')[1].replace(')', '')
                
                p_wins, n_wins = map(int, stats.split('/'))
                pattern_data.append({
                    'pat': display_pat,
                    'p': p_wins,
                    'n': n_wins,
                    'winner': winner_tag
                })
            except Exception:
                continue
                
        if not pattern_data:
            continue
            
        print(f"\n[ {idx+1}. {sym} ]")
        
        # Build Headers
        header_row = f"{'Pattern Suffix':<16} : "
        for pdct in pattern_data:
            header_row += f"{pdct['pat']:<13}"
        header_row += "| SUMMARY"
        
        print(header_row)
        print("-" * len(header_row))
        
        num_patterns = len(pattern_data)
        
        # Build UP row
        line_p = f"{'🟢 UP Votes':<16} : "
        sum_p_actual = 0
        for pdct in pattern_data:
            if num_patterns == 1 or pdct['winner'] == 'P':
                sum_p_actual += pdct['p']
                val_str = f"*{pdct['p']}*" if pdct['winner'] == 'P' else f"{pdct['p']}"
            else:
                val_str = f"{pdct['p']} (0)"
            line_p += f"{val_str:<13}"
        line_p += f"| = {sum_p_actual}"
        
        # Build DOWN row
        line_n = f"{'🔴 DOWN Votes':<16} : "
        sum_n_actual = 0
        for pdct in pattern_data:
            if num_patterns == 1 or pdct['winner'] == 'N':
                sum_n_actual += pdct['n']
                val_str = f"*{pdct['n']}*" if pdct['winner'] == 'N' else f"{pdct['n']}"
            else:
                val_str = f"{pdct['n']} (0)"
            line_n += f"{val_str:<13}"
        line_n += f"| = {sum_n_actual}"
        
        print(line_p)
        print(line_n)
        print("-" * len(header_row))
        
        # Final calculation (Supervisor True Winner Counting vs Single-Pattern Fallback)
        if num_patterns == 1:
            p_val = pattern_data[0]['p']
            n_val = pattern_data[0]['n']
            total = p_val + n_val
            
            if p_val >= n_val:
                final_dir = "🟢 UP"
                winner_wr = (p_val / total * 100) if total > 0 else 0
            else:
                final_dir = "🔴 DOWN"
                winner_wr = (n_val / total * 100) if total > 0 else 0
                
            formula_str = f"({winner_wr:.1f}%)"
            print(f"🎯 Final Result: {final_dir} | Calculation: {formula_str} / 1 = {winner_wr:.1f}% Prob%")
        else:
            # Multi-pattern weighted consensus (TOTAL_UP_WIN vs TOTAL_DOWN_WIN)
            sum_p_win = sum(pdct['p'] for pdct in pattern_data if pdct['winner'] == 'P')
            sum_n_win = sum(pdct['n'] for pdct in pattern_data if pdct['winner'] == 'N')
            
            if sum_p_win > sum_n_win:
                final_dir = "🟢 UP"
                final_prob = (sum_p_win / (sum_p_win + sum_n_win) * 100) if (sum_p_win + sum_n_win) > 0 else 0
                calc_str = f"{sum_p_win} / ({sum_p_win} + {sum_n_win})"
            elif sum_n_win > sum_p_win:
                final_dir = "🔴 DOWN"
                final_prob = (sum_n_win / (sum_p_win + sum_n_win) * 100) if (sum_p_win + sum_n_win) > 0 else 0
                calc_str = f"{sum_n_win} / ({sum_p_win} + {sum_n_win})"
            else:
                print("🎯 Final Result: ⚪ NEUTRAL (Tie)")
                return
                
            print(f"🎯 Final Result: {final_dir} | Calculation: {calc_str} = {final_prob:.1f}% Prob%")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].upper() == 'ALL':
        view_all_report()
    else:
        view_report(sys.argv[1])
