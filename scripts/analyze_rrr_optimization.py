#!/usr/bin/env python
"""
analyze_rrr_optimization.py
============================
วิเคราะห์ trade history เพื่อหา optimal SL/TP parameters ที่ให้:
- RRR >= 1.5
- Prob% ~60%  
- Count มากที่สุด (น่าเชื่อถือ)

สร้างโดย Antigravity สำหรับวิเคราะห์ก่อนปรับ parameters จริง
"""

import sys
import os
import pandas as pd
import numpy as np
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_all_trades():
    """Load all trade history files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(base_dir, "logs", "trade_history_*.csv")
    files = glob.glob(pattern)
    files = [f for f in files if "trade_history.csv" not in os.path.basename(f)]
    
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, on_bad_lines='skip', engine='python')
            if not df.empty:
                if 'Country' not in df.columns:
                    filename = os.path.basename(f).upper()
                    if 'THAI' in filename: df['Country'] = 'TH'
                    elif 'US' in filename: df['Country'] = 'US'
                    elif 'CHINA' in filename: df['Country'] = 'CN'
                    elif 'TAIWAN' in filename: df['Country'] = 'TW'
                    elif 'METALS' in filename and '15M' in filename: df['Country'] = 'GL_15M'
                    elif 'METALS' in filename: df['Country'] = 'GL_30M'
                    else: df['Country'] = 'GL'
                dfs.append(df)
        except Exception as e:
            print(f"Warning: {os.path.basename(f)}: {e}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def analyze_exit_distribution(df, country_label):
    """วิเคราะห์สัดส่วน exit reason"""
    if 'exit_reason' not in df.columns:
        return None
    
    total = len(df)
    exit_counts = df['exit_reason'].value_counts()
    
    print(f"\n{'='*70}")
    print(f"  {country_label} — Exit Distribution ({total} trades)")
    print(f"{'='*70}")
    for reason, count in exit_counts.items():
        pct = count / total * 100
        print(f"  {reason:<20} {count:>6} trades ({pct:>5.1f}%)")
    return exit_counts

def analyze_pnl_by_exit(df, country_label):
    """วิเคราะห์ PnL แยกตาม exit reason"""
    if 'exit_reason' not in df.columns or 'actual_return' not in df.columns:
        return
    
    df = df.copy()
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    
    # Calculate direction-adjusted PnL
    if 'forecast' in df.columns:
        df['pnl'] = df.apply(lambda r: r['actual_return'] * (1 if r['forecast'] == 'UP' else -1), axis=1)
    else:
        df['pnl'] = df['actual_return']
    
    print(f"\n  PnL by Exit Reason:")
    print(f"  {'Reason':<20} {'AvgPnL':>8} {'Wins':>6} {'Losses':>8} {'WinRate':>8}")
    print(f"  {'-'*55}")
    
    for reason in df['exit_reason'].unique():
        subset = df[df['exit_reason'] == reason]
        avg_pnl = subset['pnl'].mean()
        wins = len(subset[subset['pnl'] > 0])
        losses = len(subset[subset['pnl'] <= 0])
        total = wins + losses
        wr = wins / total * 100 if total > 0 else 0
        print(f"  {reason:<20} {avg_pnl:>7.2f}% {wins:>6} {losses:>8} {wr:>7.1f}%")

def analyze_current_rrr(df, country_label):
    """วิเคราะห์ RRR ปัจจุบันแบบละเอียด"""
    df = df.copy()
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df = df.dropna(subset=['actual_return'])
    
    if 'forecast' in df.columns:
        df['pnl'] = df.apply(lambda r: r['actual_return'] * (1 if r['forecast'] == 'UP' else -1), axis=1)
    else:
        df['pnl'] = df['actual_return']
    
    wins = df[df['pnl'] > 0]
    losses = df[df['pnl'] <= 0]
    
    avg_win = wins['pnl'].mean() if not wins.empty else 0
    avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    win_rate = len(wins) / len(df) * 100 if len(df) > 0 else 0
    expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
    
    print(f"\n  Current RRR Analysis:")
    print(f"  Total Trades: {len(df)}")
    print(f"  Win Rate:     {win_rate:.1f}%")
    print(f"  Avg Win:      +{avg_win:.2f}%")
    print(f"  Avg Loss:     -{avg_loss:.2f}%")
    print(f"  RRR:          {rrr:.2f}")
    print(f"  Expectancy:   {expectancy:+.3f}% per trade")
    
    # Win/Loss Distribution
    print(f"\n  Win Distribution (percentiles):")
    if not wins.empty:
        for p in [25, 50, 75, 90, 95]:
            print(f"    P{p}: +{wins['pnl'].quantile(p/100):.2f}%")
    
    print(f"\n  Loss Distribution (percentiles):")
    if not losses.empty:
        for p in [25, 50, 75, 90, 95]:
            print(f"    P{p}: {losses['pnl'].quantile(p/100):.2f}%")
    
    return {
        'count': len(df), 'win_rate': win_rate,
        'avg_win': avg_win, 'avg_loss': avg_loss,
        'rrr': rrr, 'expectancy': expectancy
    }

def simulate_sl_filter(df, country_label, sl_caps, tp_caps):
    """
    จำลองการเปลี่ยน SL/TP cap โดยตัด trades ที่เกิน cap ออก
    (เป็นการประมาณ — ไม่ใช่การ re-simulate จริง)
    """
    df = df.copy()
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df = df.dropna(subset=['actual_return'])
    
    if 'forecast' in df.columns:
        df['pnl'] = df.apply(lambda r: r['actual_return'] * (1 if r['forecast'] == 'UP' else -1), axis=1)
    else:
        df['pnl'] = df['actual_return']
    
    print(f"\n{'='*80}")
    print(f"  {country_label} — RRR Optimization Scenarios")
    print(f"{'='*80}")
    print(f"  {'SL_Cap':>8} {'TP_Cap':>8} {'Count':>7} {'WinRate':>8} {'AvgWin':>8} {'AvgLoss':>9} {'RRR':>6} {'Expect':>8}")
    print(f"  {'-'*70}")
    
    best = None
    
    for sl_cap in sl_caps:
        for tp_cap in tp_caps:
            # Simulate: cap losses at SL, cap wins at TP
            sim = df.copy()
            
            # Cap losses (if loss > sl_cap, cap it at sl_cap)
            sim.loc[sim['pnl'] < -sl_cap, 'pnl'] = -sl_cap
            
            # Cap wins (if win > tp_cap, cap it at tp_cap)
            sim.loc[sim['pnl'] > tp_cap, 'pnl'] = tp_cap
            
            wins = sim[sim['pnl'] > 0]
            losses = sim[sim['pnl'] <= 0]
            
            avg_win = wins['pnl'].mean() if not wins.empty else 0
            avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
            win_rate = len(wins) / len(sim) * 100
            expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
            
            marker = ""
            if rrr >= 1.5 and win_rate >= 55:
                marker = " ★★★"
            elif rrr >= 1.2 and win_rate >= 50:
                marker = " ★★"
            elif rrr >= 1.0:
                marker = " ★"
            
            print(f"  {sl_cap:>7.1f}% {tp_cap:>7.1f}% {len(sim):>7} {win_rate:>7.1f}% {avg_win:>+7.2f}% {avg_loss:>8.2f}% {rrr:>5.2f} {expectancy:>+7.3f}%{marker}")
            
            if best is None or (rrr >= 1.5 and expectancy > best.get('expectancy', -999)):
                if rrr >= 1.5:
                    best = {'sl_cap': sl_cap, 'tp_cap': tp_cap, 'rrr': rrr, 
                            'win_rate': win_rate, 'expectancy': expectancy, 'count': len(sim)}
    
    if best:
        print(f"\n  ✅ Best combo (RRR≥1.5): SL={best['sl_cap']}%, TP={best['tp_cap']}%, "
              f"RRR={best['rrr']:.2f}, WR={best['win_rate']:.1f}%, Expect={best['expectancy']:+.3f}%")
    return best

def analyze_per_symbol_potential(df, country_code, country_label):
    """วิเคราะห์ potential RRR ของแต่ละ symbol"""
    df = df.copy()
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df = df.dropna(subset=['actual_return'])
    
    if 'forecast' in df.columns:
        df['pnl'] = df.apply(lambda r: r['actual_return'] * (1 if r['forecast'] == 'UP' else -1), axis=1)
    else:
        df['pnl'] = df['actual_return']
    
    print(f"\n{'='*90}")
    print(f"  {country_label} — Per-Symbol Analysis (Potential for RRR ≥ 1.5)")
    print(f"{'='*90}")
    print(f"  {'Symbol':<10} {'Count':>7} {'WinRate':>8} {'AvgWin':>8} {'AvgLoss':>9} {'RRR':>6} {'Expect':>8} {'Status':>10}")
    print(f"  {'-'*75}")
    
    symbols_data = []
    
    for sym in df['symbol'].unique():
        sym_df = df[df['symbol'] == sym]
        
        if len(sym_df) < 5:
            continue
        
        wins = sym_df[sym_df['pnl'] > 0]
        losses = sym_df[sym_df['pnl'] <= 0]
        
        avg_win = wins['pnl'].mean() if not wins.empty else 0
        avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        wr = len(wins) / len(sym_df) * 100
        expect = (wr/100 * avg_win) - ((100-wr)/100 * avg_loss)
        
        status = ""
        if rrr >= 2.0 and wr >= 55:
            status = "EXCELLENT"
        elif rrr >= 1.5 and wr >= 50:
            status = "GOOD"
        elif rrr >= 1.0 and wr >= 45:
            status = "OK"
        else:
            status = "WEAK"
        
        symbols_data.append({
            'symbol': sym, 'count': len(sym_df), 'wr': wr,
            'avg_win': avg_win, 'avg_loss': avg_loss, 'rrr': rrr, 
            'expect': expect, 'status': status
        })
    
    # Sort by RRR descending
    symbols_data.sort(key=lambda x: x['rrr'], reverse=True)
    
    for s in symbols_data:
        marker = "★" if s['status'] in ['EXCELLENT', 'GOOD'] else ""
        print(f"  {s['symbol']:<10} {s['count']:>7} {s['wr']:>7.1f}% {s['avg_win']:>+7.2f}% "
              f"{s['avg_loss']:>8.2f}% {s['rrr']:>5.2f} {s['expect']:>+7.3f}% {s['status']:>10} {marker}")
    
    # Count qualifying
    good = [s for s in symbols_data if s['rrr'] >= 1.5 and s['wr'] >= 50]
    total_qualifying_count = sum(s['count'] for s in good)
    print(f"\n  Summary: {len(good)}/{len(symbols_data)} symbols qualify (RRR≥1.5, WR≥50%)")
    print(f"  Total qualifying trades: {total_qualifying_count}")
    
    return symbols_data


def main():
    print("=" * 80)
    print("  RRR OPTIMIZATION ANALYSIS")
    print("  Target: RRR ≥ 1.5 | Prob ~60% | High Count")
    print("=" * 80)
    
    df = load_all_trades()
    if df.empty:
        print("ERROR: No trade data found!")
        return
    
    print(f"\n  Total trades loaded: {len(df)}")
    
    # Determine country from filename-based Country column or group column
    markets = {
        'TH': 'THAI MARKET',
        'US': 'US MARKET', 
        'CN': 'CHINA/HK MARKET',
        'TW': 'TAIWAN MARKET'
    }
    
    # Overall summary first
    print(f"\n{'='*80}")
    print(f"  OVERALL MARKET SUMMARY")
    print(f"{'='*80}")
    
    for code, label in markets.items():
        if 'Country' in df.columns:
            market_df = df[df['Country'] == code]
        elif 'group' in df.columns:
            if code == 'TH':
                market_df = df[df['group'].str.contains('THAI', na=False)]
            elif code == 'US':
                market_df = df[df['group'].str.contains('US|NASDAQ', na=False)]
            elif code == 'CN':
                market_df = df[df['group'].str.contains('CHINA|HK', na=False)]
            elif code == 'TW':
                market_df = df[df['group'].str.contains('TAIWAN', na=False)]
            else:
                market_df = pd.DataFrame()
        else:
            market_df = pd.DataFrame()
        
        if market_df.empty:
            print(f"\n  {label}: No data")
            continue
        
        # 1. Current RRR
        stats = analyze_current_rrr(market_df, label)
        
        # 2. Exit Distribution
        analyze_exit_distribution(market_df, label)
        
        # 3. PnL by Exit
        analyze_pnl_by_exit(market_df, label)
        
        # 4. Per-Symbol Analysis
        analyze_per_symbol_potential(market_df, code, label)
        
        # 5. SL/TP Cap Simulation 
        sl_caps = [1.0, 1.5, 2.0, 2.5, 3.0]
        tp_caps = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
        simulate_sl_filter(market_df, label, sl_caps, tp_caps)


if __name__ == "__main__":
    main()
