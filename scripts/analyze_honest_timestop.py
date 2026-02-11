"""
analyze_honest_timestop.py - Compare Time Stop Strategies WITHOUT Look-Ahead Bias
==================================================================================
Tests 3 realistic holding period strategies for China/HK Mean Reversion:

1. DAY-1: Original 1-day return (current baseline)
2. DAY-3 FIXED: Always hold exactly 3 days, take whatever return you get
3. TAKE-PROFIT STOP: Set 2% target + 2% stop-loss, exit whichever hits first (max 3 days)
4. BEST-OF-3 (BIASED): The current "cheating" approach — for comparison only

This script proves which approach is honest AND profitable.
"""
import pandas as pd
import numpy as np
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fetch_data(symbol, exchange, n_bars=5000):
    from tvDatafeed import TvDatafeed, Interval
    tv = TvDatafeed()
    time.sleep(2)
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
        if df is not None and len(df) > 100:
            return df
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return None

def test_strategies(df, symbol):
    """Test all time-stop strategies on one stock."""
    close = df['close']
    high = df['high']
    low = df['low']
    pct_change = close.pct_change()
    sma50 = close.rolling(50).mean()
    volume = df['volume']
    vol_avg_20 = volume.rolling(20).mean()
    volume_ratio = volume / vol_avg_20
    
    # Build patterns
    patterns = []
    for ret in pct_change:
        if pd.isna(ret):
            patterns.append('.')
        elif ret > 0:
            patterns.append('+')
        elif ret < 0:
            patterns.append('-')
        else:
            patterns.append('.')
    
    # Training phase (first 70%)
    train_end = int(len(df) * 0.7)
    pattern_stats = {}
    for i in range(3, train_end - 1):
        next_ret = pct_change.iloc[i+1]
        if pd.isna(next_ret): continue
        for length in range(3, 6):
            if i - length + 1 < 0: continue
            pat = ''.join(patterns[i-length+1:i+1])
            if len(pat) < 3: continue
            if pat not in pattern_stats:
                pattern_stats[pat] = []
            pattern_stats[pat].append(next_ret)
    
    results = {
        'day1': [], 'day3_fixed': [], 'tp_stop': [], 'best3': []
    }
    
    # Testing phase
    for i in range(train_end, len(df) - 4):  # Need 3 days forward
        # Find matching pattern
        best_pat = None
        best_count = 0
        for length in range(3, 6):
            if i - length + 1 < 0: continue
            pat = ''.join(patterns[i-length+1:i+1])
            if pat in pattern_stats and len(pattern_stats[pat]) >= 30:
                if len(pattern_stats[pat]) > best_count:
                    best_pat = pat
                    best_count = len(pattern_stats[pat])
        
        if best_pat is None:
            continue
        
        last_char = best_pat[-1]
        
        # Mean Reversion direction
        if last_char == '+':
            direction = -1  # SHORT (fade up)
        elif last_char == '-':
            direction = 1   # LONG (fade down)
        else:
            continue
        
        # PILLAR 1: Market Regime Filter
        if direction == 1:  # LONG only
            if not pd.isna(sma50.iloc[i]) and close.iloc[i] < sma50.iloc[i]:
                continue
        
        # FOMO / Dead filter
        vr = volume_ratio.iloc[i] if not pd.isna(volume_ratio.iloc[i]) else 1.0
        if vr < 0.5:
            continue
        
        # ========================================
        # STRATEGY 1: Day-1 Return (Baseline)
        # ========================================
        ret_day1 = pct_change.iloc[i+1]
        if pd.isna(ret_day1): continue
        
        actual_d1 = ret_day1 * direction
        correct_d1 = 1 if actual_d1 > 0 else 0
        results['day1'].append({
            'symbol': symbol, 'correct': correct_d1, 
            'return': actual_d1 * 100, 'abs_return': abs(actual_d1 * 100)
        })
        
        # ========================================
        # STRATEGY 2: Fixed Day-3 Hold
        # ========================================
        ret_day3 = (close.iloc[i+3] - close.iloc[i]) / close.iloc[i]
        actual_d3 = ret_day3 * direction
        correct_d3 = 1 if actual_d3 > 0 else 0
        results['day3_fixed'].append({
            'symbol': symbol, 'correct': correct_d3,
            'return': actual_d3 * 100, 'abs_return': abs(actual_d3 * 100)
        })
        
        # ========================================
        # STRATEGY 3: Take-Profit / Stop-Loss (2%/2%, max 3 days)
        # ========================================
        tp_pct = 0.02   # 2% take profit
        sl_pct = -0.02   # 2% stop loss
        final_ret = None
        
        for day in range(1, 4):  # Day 1, 2, 3
            idx = i + day
            if idx >= len(close): break
            
            # Intraday check using high/low
            day_high_ret = (high.iloc[idx] - close.iloc[i]) / close.iloc[i] * direction
            day_low_ret = (low.iloc[idx] - close.iloc[i]) / close.iloc[i] * direction
            
            # For LONG: high is favorable, low is adverse
            # For SHORT: low is favorable, high is adverse  
            if direction == 1:
                favorable = day_high_ret
                adverse = day_low_ret
            else:
                favorable = -day_low_ret  # Most negative price = most favorable for short
                adverse = -day_high_ret
            
            # Check stop-loss first (conservative assumption)
            day_ret_close = (close.iloc[idx] - close.iloc[i]) / close.iloc[i] * direction
            
            if day_ret_close <= sl_pct:
                final_ret = sl_pct  # Stopped out
                break
            elif day_ret_close >= tp_pct:
                final_ret = tp_pct  # Take profit hit
                break
        
        if final_ret is None:
            # Day 3 close (time stop)
            final_ret = (close.iloc[i+3] - close.iloc[i]) / close.iloc[i] * direction
        
        correct_tp = 1 if final_ret > 0 else 0
        results['tp_stop'].append({
            'symbol': symbol, 'correct': correct_tp,
            'return': final_ret * 100, 'abs_return': abs(final_ret * 100)
        })
        
        # ========================================
        # STRATEGY 4: Best-of-3 (BIASED — for comparison)
        # ========================================
        best_ret = ret_day1
        for day_offset in range(2, 4):
            multi_ret = (close.iloc[i+day_offset] - close.iloc[i]) / close.iloc[i]
            if direction == 1 and multi_ret > best_ret:
                best_ret = multi_ret
            elif direction == -1 and multi_ret < best_ret:
                best_ret = multi_ret
        
        actual_best = best_ret * direction
        correct_best = 1 if actual_best > 0 else 0
        results['best3'].append({
            'symbol': symbol, 'correct': correct_best,
            'return': actual_best * 100, 'abs_return': abs(actual_best * 100)
        })
    
    return results

def main():
    symbols = [
        ('700', 'HKEX', 'TENCENT'),
        ('9988', 'HKEX', 'ALIBABA'),
        ('3690', 'HKEX', 'MEITUAN'),
        ('1810', 'HKEX', 'XIAOMI'),
        ('9618', 'HKEX', 'JD-COM'),
        ('1211', 'HKEX', 'BYD'),
        ('9868', 'HKEX', 'XPENG'),
        ('9866', 'HKEX', 'NIO'),
    ]
    
    all_results = {'day1': [], 'day3_fixed': [], 'tp_stop': [], 'best3': []}
    
    print("=" * 85)
    print("🔬 HONEST TIME STOP COMPARISON — No Look-Ahead Bias")
    print("=" * 85)
    print("Testing 4 strategies with Market Regime Filter active:\n")
    
    for sym, exch, name in symbols:
        print(f"   📈 {name} ({sym})...", end=" ")
        df = fetch_data(sym, exch)
        if df is None or len(df) < 200:
            print("❌ No data")
            continue
        
        res = test_strategies(df, name)
        for k in all_results:
            all_results[k].extend(res[k])
        
        # Per-symbol summary
        if res['day1']:
            d1_wr = sum(r['correct'] for r in res['day1']) / len(res['day1']) * 100
            d3_wr = sum(r['correct'] for r in res['day3_fixed']) / len(res['day3_fixed']) * 100
            tp_wr = sum(r['correct'] for r in res['tp_stop']) / len(res['tp_stop']) * 100
            b3_wr = sum(r['correct'] for r in res['best3']) / len(res['best3']) * 100
            print(f"✅ {len(res['day1'])} trades | D1:{d1_wr:.0f}% D3:{d3_wr:.0f}% TP:{tp_wr:.0f}% Best3:{b3_wr:.0f}%")
        else:
            print("✅ 0 trades")
        time.sleep(3)
    
    # ==========================================
    # OVERALL COMPARISON
    # ==========================================
    print()
    print("=" * 85)
    print("🏆 OVERALL COMPARISON — ALL CHINA/HK STOCKS")
    print("=" * 85)
    
    strategies = [
        ("Day-1 (Baseline)", 'day1'),
        ("Day-3 Fixed Hold", 'day3_fixed'),
        ("TP/SL 2%/2% (Max 3d)", 'tp_stop'),
        ("Best-of-3 ⚠️ BIASED", 'best3'),
    ]
    
    print(f"\n   {'Strategy':<30} {'Count':<8} {'WinRate':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6} {'Expectancy':<10}")
    print(f"   {'-'*84}")
    
    for label, key in strategies:
        data = all_results[key]
        if not data:
            continue
        
        df_s = pd.DataFrame(data)
        wr = df_s['correct'].mean() * 100
        wins = df_s[df_s['correct']==1]['abs_return']
        losses = df_s[df_s['correct']==0]['abs_return']
        avg_w = wins.mean() if len(wins) > 0 else 0
        avg_l = losses.mean() if len(losses) > 0 else 0
        rrr = avg_w / avg_l if avg_l > 0 else 0
        exp = (wr/100 * avg_w) - ((100-wr)/100 * avg_l)
        
        bias_marker = " ⚠️" if "BIASED" in label else ""
        best_marker = " ⭐" if exp > 0 and "BIASED" not in label else ""
        print(f"   {label:<30} {len(data):<8} {wr:>6.1f}%   {avg_w:>6.2f}%   {avg_l:>6.2f}%   {rrr:.2f}   {exp:>+7.3f}%{best_marker}{bias_marker}")
    
    # ==========================================
    # PER-SYMBOL BREAKDOWN (Best honest strategy)
    # ==========================================
    print()
    print("=" * 85)
    print("📊 PER-SYMBOL: Day-3 Fixed Hold vs TP/SL Stop")
    print("=" * 85)
    
    for key_label, key in [("Day-3 Fixed", 'day3_fixed'), ("TP/SL 2%/2%", 'tp_stop')]:
        print(f"\n   --- {key_label} ---")
        print(f"   {'Symbol':<12} {'Count':<8} {'WinRate':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6}")
        print(f"   {'-'*56}")
        
        df_s = pd.DataFrame(all_results[key])
        for sym, grp in df_s.groupby('symbol'):
            if len(grp) < 10:
                continue
            wr = grp['correct'].mean() * 100
            wins = grp[grp['correct']==1]['abs_return']
            losses = grp[grp['correct']==0]['abs_return']
            avg_w = wins.mean() if len(wins) > 0 else 0
            avg_l = losses.mean() if len(losses) > 0 else 0
            rrr = avg_w / avg_l if avg_l > 0 else 0
            marker = " ⭐" if wr > 55 and rrr > 1.0 else ""
            print(f"   {sym:<12} {len(grp):<8} {wr:>6.1f}%   {avg_w:>6.2f}%   {avg_l:>6.2f}%   {rrr:.2f}{marker}")
    
    print()
    print("=" * 85)
    print("✅ Analysis Complete — Use HONEST strategies (Day-3 Fixed or TP/SL)")
    print("   ⚠️  Best-of-3 is shown for reference only — DO NOT use in production")
    print("=" * 85)

if __name__ == "__main__":
    main()
