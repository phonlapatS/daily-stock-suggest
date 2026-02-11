"""
analyze_china_turnover.py - Volume Ratio / Turnover Rate Analysis for China
============================================================================
Tests the hypothesis that Volume Ratio (VR) zones create better trade quality
than ADX filtering for China/HK market.

Uses raw OHLCV data to calculate Volume Ratio and segment historical trades
into VR zones, measuring Win Rate and RRR for each.
"""
import pandas as pd
import numpy as np
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fetch_data_for_symbol(symbol, exchange, n_bars=5000):
    """Fetch OHLCV data from tvDatafeed."""
    from tvDatafeed import TvDatafeed, Interval
    tv = TvDatafeed()
    time.sleep(2)
    
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
        if df is not None and len(df) > 100:
            return df
    except Exception as e:
        print(f"   ❌ Error fetching {symbol}: {e}")
    return None

def calculate_volume_metrics(df):
    """Calculate Volume Ratio and related metrics."""
    volume = df['volume']
    close = df['close']
    
    # Volume Ratio (VR) = Today's Volume / 20-day Average Volume
    vol_avg_20 = volume.rolling(20).mean()
    df['volume_ratio'] = volume / vol_avg_20
    
    # 5-day Average VR (for accumulation detection)
    df['vr_5d'] = df['volume_ratio'].rolling(5).mean()
    
    # Turnover Rate Proxy (relative volume intensity)
    df['pct_change'] = close.pct_change()
    
    # Volume-Price Divergence (price up but volume dropping = smart money)
    df['price_dir'] = np.where(df['pct_change'] > 0, 1, -1)
    df['vol_change'] = volume.pct_change()
    
    return df

def classify_vr_zone(vr):
    """Classify Volume Ratio into zones."""
    if pd.isna(vr):
        return "UNKNOWN"
    elif vr < 0.5:
        return "DEAD (VR<0.5)"
    elif vr < 1.0:
        return "QUIET (0.5-1.0)"
    elif vr < 1.5:
        return "NORMAL (1.0-1.5)"
    elif vr < 2.0:
        return "ELEVATED (1.5-2.0)"
    elif vr < 3.0:
        return "HIGH (2.0-3.0)"
    else:
        return "FOMO (VR>3.0)"

def analyze_symbol(df, symbol):
    """Analyze a single symbol's Volume Ratio vs Returns relationship."""
    df = calculate_volume_metrics(df)
    
    close = df['close']
    pct_change = df['pct_change']
    
    # Pattern detection (simplified 3-day)
    results = []
    
    for i in range(25, len(df) - 1):  # Start after 20-day vol avg stabilizes
        if pd.isna(df['volume_ratio'].iloc[i]):
            continue
            
        # Get current VR metrics
        current_vr = df['volume_ratio'].iloc[i]
        vr_5d = df['vr_5d'].iloc[i] if not pd.isna(df['vr_5d'].iloc[i]) else current_vr
        vr_zone = classify_vr_zone(current_vr)
        
        # Next day return (what we're trying to predict)
        next_return = pct_change.iloc[i + 1]
        if pd.isna(next_return):
            continue
        
        # 3-day pattern (simplified)
        if i < 3:
            continue
        pat_chars = []
        for j in range(i-2, i+1):
            ret = pct_change.iloc[j]
            if pd.isna(ret):
                break
            if ret > 0:
                pat_chars.append('+')
            elif ret < 0:
                pat_chars.append('-')
            else:
                pat_chars.append('.')
        
        if len(pat_chars) != 3:
            continue
        
        pattern = ''.join(pat_chars)
        last_char = pattern[-1]
        
        # Mean Reversion bet direction
        if last_char == '+':
            mr_dir = 'DOWN'
        elif last_char == '-':
            mr_dir = 'UP'
        else:
            continue  # Skip flat patterns
        
        actual_dir = 'UP' if next_return > 0 else 'DOWN'
        mr_correct = 1 if mr_dir == actual_dir else 0
        
        results.append({
            'symbol': symbol,
            'date': df.index[i],
            'pattern': pattern,
            'vr': current_vr,
            'vr_5d': vr_5d,
            'vr_zone': vr_zone,
            'mr_direction': mr_dir,
            'actual_direction': actual_dir,
            'actual_return': next_return * 100,
            'mr_correct': mr_correct,
            'mr_return': abs(next_return * 100) if mr_correct else -abs(next_return * 100)
        })
    
    return pd.DataFrame(results)

def main():
    # China/HK symbols from config
    symbols = [
        ('700', 'HKEX', 'TENCENT'),
        ('9988', 'HKEX', 'ALIBABA'),
        ('3690', 'HKEX', 'MEITUAN'),
        ('1810', 'HKEX', 'XIAOMI'),
        ('9888', 'HKEX', 'BAIDU'),
        ('9618', 'HKEX', 'JD-COM'),
        ('1211', 'HKEX', 'BYD'),
        ('2015', 'HKEX', 'LI-AUTO'),
        ('9868', 'HKEX', 'XPENG'),
        ('9866', 'HKEX', 'NIO'),
    ]
    
    all_results = []
    
    print("=" * 80)
    print("🇨🇳 CHINA/HK VOLUME RATIO ANALYSIS")
    print("=" * 80)
    print("Testing: Does Volume Ratio create a better edge than ADX?")
    print()
    
    for sym, exch, name in symbols:
        print(f"   📈 Fetching {name} ({sym})...", end=" ")
        df = fetch_data_for_symbol(sym, exch)
        
        if df is None or len(df) < 100:
            print("❌ No data")
            continue
        
        results = analyze_symbol(df, name)
        print(f"✅ {len(results)} patterns analyzed")
        all_results.append(results)
        time.sleep(3)  # Rate limit
    
    if not all_results:
        print("❌ No data collected!")
        return
    
    combined = pd.concat(all_results, ignore_index=True)
    
    # =============================================
    # ANALYSIS 1: Win Rate by VR Zone (Overall)
    # =============================================
    print()
    print("=" * 80)
    print("📊 ANALYSIS 1: Mean Reversion Win Rate by Volume Ratio Zone")
    print("=" * 80)
    
    zone_order = ["DEAD (VR<0.5)", "QUIET (0.5-1.0)", "NORMAL (1.0-1.5)", 
                  "ELEVATED (1.5-2.0)", "HIGH (2.0-3.0)", "FOMO (VR>3.0)"]
    
    print(f"\n   {'VR Zone':<22} {'Count':<8} {'WinRate':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6} {'Expectancy':<10}")
    print(f"   {'-'*76}")
    
    for zone in zone_order:
        grp = combined[combined['vr_zone'] == zone]
        if len(grp) < 10:
            print(f"   {zone:<22} {len(grp):<8} (insufficient data)")
            continue
        
        wins = grp[grp['mr_correct'] == 1]
        losses = grp[grp['mr_correct'] == 0]
        wr = len(wins) / len(grp) * 100
        avg_w = abs(grp[grp['mr_return'] > 0]['mr_return'].mean())
        avg_l = abs(grp[grp['mr_return'] <= 0]['mr_return'].mean())
        rrr = avg_w / avg_l if avg_l > 0 else 0
        expectancy = (wr/100 * avg_w) - ((100-wr)/100 * avg_l)
        
        marker = " ⭐" if wr > 52 and rrr > 1.0 else " ❌" if wr < 48 else ""
        print(f"   {zone:<22} {len(grp):<8} {wr:>6.1f}%   {avg_w:>6.2f}%   {avg_l:>6.2f}%   {rrr:.2f}   {expectancy:>+6.3f}%{marker}")

    # =============================================
    # ANALYSIS 2: Smart Money Zone Detection
    # =============================================
    print()
    print("=" * 80)
    print("📊 ANALYSIS 2: Smart Money Zone (Low 5d VR < 0.8 → Current VR 0.8-2.0)")
    print("=" * 80)
    
    smart_zone = combined[(combined['vr_5d'] < 0.8) & (combined['vr'].between(0.8, 2.0))]
    normal_zone = combined[(combined['vr'].between(0.5, 1.5))]
    fomo_zone = combined[combined['vr'] > 3.0]
    
    for label, grp in [("Smart Money Zone", smart_zone), ("Normal Zone", normal_zone), ("FOMO Zone", fomo_zone)]:
        if len(grp) < 10:
            print(f"   {label}: Insufficient data ({len(grp)} trades)")
            continue
        
        wins = grp[grp['mr_correct'] == 1]
        losses = grp[grp['mr_correct'] == 0]
        wr = len(wins) / len(grp) * 100
        avg_w = abs(grp[grp['mr_return'] > 0]['mr_return'].mean())
        avg_l = abs(grp[grp['mr_return'] <= 0]['mr_return'].mean())
        rrr = avg_w / avg_l if avg_l > 0 else 0
        expectancy = (wr/100 * avg_w) - ((100-wr)/100 * avg_l)
        
        print(f"   {label:<25} Count={len(grp):<6} WR={wr:5.1f}%  AvgWin={avg_w:.2f}%  AvgLoss={avg_l:.2f}%  RRR={rrr:.2f}  E={expectancy:+.3f}%")
    
    # =============================================
    # ANALYSIS 3: Per-Symbol Best Zone
    # =============================================
    print()
    print("=" * 80)
    print("📊 ANALYSIS 3: Per-Symbol Win Rate (Normal VR Zone 0.5-1.5 only)")
    print("=" * 80)
    
    normal = combined[combined['vr'].between(0.5, 1.5)]
    
    print(f"\n   {'Symbol':<12} {'Count':<8} {'WinRate':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6}")
    print(f"   {'-'*56}")
    
    for sym, grp in normal.groupby('symbol'):
        if len(grp) < 20:
            continue
        wins = grp[grp['mr_correct'] == 1]
        losses = grp[grp['mr_correct'] == 0]
        wr = len(wins) / len(grp) * 100
        avg_w = abs(grp[grp['mr_return'] > 0]['mr_return'].mean()) if len(wins) > 0 else 0
        avg_l = abs(grp[grp['mr_return'] <= 0]['mr_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_w / avg_l if avg_l > 0 else 0
        
        marker = " ⭐" if wr > 52 and rrr > 1.0 else ""
        print(f"   {sym:<12} {len(grp):<8} {wr:>6.1f}%   {avg_w:>6.2f}%   {avg_l:>6.2f}%   {rrr:.2f}{marker}")

    # =============================================
    # ANALYSIS 4: Strategy Comparison (Full Picture)
    # =============================================
    print()
    print("=" * 80)
    print("🏆 FINAL COMPARISON: ALL STRATEGIES FOR CHINA")
    print("=" * 80)
    
    # 1. Raw Mean Reversion (no filter)
    all_wr = combined['mr_correct'].mean() * 100
    all_aw = abs(combined[combined['mr_return'] > 0]['mr_return'].mean())
    all_al = abs(combined[combined['mr_return'] <= 0]['mr_return'].mean())
    all_rrr = all_aw / all_al if all_al > 0 else 0
    all_exp = (all_wr/100 * all_aw) - ((100-all_wr)/100 * all_al)
    
    # 2. VR Filtered (0.5-1.5)
    filtered = combined[combined['vr'].between(0.5, 1.5)]
    f_wr = filtered['mr_correct'].mean() * 100
    f_aw = abs(filtered[filtered['mr_return'] > 0]['mr_return'].mean())
    f_al = abs(filtered[filtered['mr_return'] <= 0]['mr_return'].mean())
    f_rrr = f_aw / f_al if f_al > 0 else 0
    f_exp = (f_wr/100 * f_aw) - ((100-f_wr)/100 * f_al)
    
    # 3. Smart Money (vr_5d < 0.8, vr 0.8-2.0)
    sm = combined[(combined['vr_5d'] < 0.8) & (combined['vr'].between(0.8, 2.0))]
    if len(sm) > 10:
        sm_wr = sm['mr_correct'].mean() * 100
        sm_aw = abs(sm[sm['mr_return'] > 0]['mr_return'].mean())
        sm_al = abs(sm[sm['mr_return'] <= 0]['mr_return'].mean())
        sm_rrr = sm_aw / sm_al if sm_al > 0 else 0
        sm_exp = (sm_wr/100 * sm_aw) - ((100-sm_wr)/100 * sm_al)
    else:
        sm_wr = sm_rrr = sm_exp = 0
        sm_aw = sm_al = 0
    
    # 4. Exclude FOMO only (VR < 3.0)
    no_fomo = combined[combined['vr'] < 3.0]
    nf_wr = no_fomo['mr_correct'].mean() * 100
    nf_aw = abs(no_fomo[no_fomo['mr_return'] > 0]['mr_return'].mean())
    nf_al = abs(no_fomo[no_fomo['mr_return'] <= 0]['mr_return'].mean())
    nf_rrr = nf_aw / nf_al if nf_al > 0 else 0
    nf_exp = (nf_wr/100 * nf_aw) - ((100-nf_wr)/100 * nf_al)
    
    print(f"\n   {'Strategy':<35} {'Count':<8} {'WinRate':<10} {'RRR':<6} {'Expectancy':<10}")
    print(f"   {'-'*69}")
    print(f"   {'Mean Rev (No Filter)':<35} {len(combined):<8} {all_wr:>6.1f}%   {all_rrr:.2f}   {all_exp:>+7.3f}%")
    print(f"   {'Mean Rev (Exclude FOMO >3.0)':<35} {len(no_fomo):<8} {nf_wr:>6.1f}%   {nf_rrr:.2f}   {nf_exp:>+7.3f}%")
    print(f"   {'Mean Rev (Normal VR 0.5-1.5)':<35} {len(filtered):<8} {f_wr:>6.1f}%   {f_rrr:.2f}   {f_exp:>+7.3f}%")
    if len(sm) > 10:
        print(f"   {'Smart Money Zone':<35} {len(sm):<8} {sm_wr:>6.1f}%   {sm_rrr:.2f}   {sm_exp:>+7.3f}%")
    
    print()
    print("=" * 80)
    print("✅ Analysis Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
