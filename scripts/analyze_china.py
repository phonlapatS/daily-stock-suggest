"""
analyze_china.py - Deep Analysis of China/HK Market Trades
==========================================================
Analyzes the raw trade data to determine optimal strategy for China market.
Tests: Trend Following vs Mean Reversion vs Stat Follow
"""
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze():
    path = os.path.join('logs', 'trade_history_CHINA.csv')
    if not os.path.exists(path):
        print("❌ No China trade log found.")
        return

    df = pd.read_csv(path)
    print(f"📊 Loaded {len(df)} China/HK trades")
    print(f"   Symbols: {df['symbol'].nunique()}")
    print(f"   Strategies: {df['strategy'].unique()}")
    print()

    # Convert numeric columns
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce')
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce')
    df['correct'] = pd.to_numeric(df['correct'], errors='coerce')
    
    # Extract last character of pattern to determine trend direction
    df['last_char'] = df['pattern'].apply(lambda x: str(x)[-1] if pd.notna(x) and len(str(x)) > 0 else '.')
    df['actual_dir'] = df['actual_return'].apply(lambda x: 'UP' if x > 0 else 'DOWN')
    
    # =============================================
    # TEST 1: Current Strategy (STAT_FOLLOW)
    # =============================================
    print("=" * 70)
    print("📈 TEST 1: Current Strategy (STAT_FOLLOW)")
    print("=" * 70)
    
    for sym, grp in df.groupby('symbol'):
        wins = grp[grp['correct'] == 1]
        losses = grp[grp['correct'] == 0]
        win_rate = len(wins) / len(grp) * 100 if len(grp) > 0 else 0
        avg_win = abs(grp[grp['trader_return'] > 0]['trader_return'].mean()) if len(wins) > 0 else 0
        avg_loss = abs(grp[grp['trader_return'] <= 0]['trader_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"   {sym:<8} Count={len(grp):<5} WinRate={win_rate:5.1f}%  AvgWin={avg_win:5.2f}%  AvgLoss={avg_loss:5.2f}%  RRR={rrr:.2f}")
    
    # =============================================
    # TEST 2: Simulated MEAN REVERSION (Fade)
    # =============================================
    print()
    print("=" * 70)
    print("📉 TEST 2: Simulated MEAN REVERSION (Fade last candle)")
    print("   Logic: If pattern ends '+', bet DOWN. If '-', bet UP.")
    print("=" * 70)
    
    # Only use patterns ending in + or -
    df_directional = df[df['last_char'].isin(['+', '-'])].copy()
    
    # Reversion: flip the direction
    df_directional['reversion_dir'] = df_directional['last_char'].apply(lambda x: 'DOWN' if x == '+' else 'UP')
    df_directional['reversion_correct'] = (df_directional['reversion_dir'] == df_directional['actual_dir']).astype(int)
    df_directional['reversion_return'] = df_directional.apply(
        lambda row: abs(row['actual_return']) if row['reversion_correct'] == 1 else -abs(row['actual_return']),
        axis=1
    )
    
    for sym, grp in df_directional.groupby('symbol'):
        wins = grp[grp['reversion_correct'] == 1]
        losses = grp[grp['reversion_correct'] == 0]
        win_rate = len(wins) / len(grp) * 100 if len(grp) > 0 else 0
        avg_win = abs(grp[grp['reversion_return'] > 0]['reversion_return'].mean()) if len(wins) > 0 else 0
        avg_loss = abs(grp[grp['reversion_return'] <= 0]['reversion_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"   {sym:<8} Count={len(grp):<5} WinRate={win_rate:5.1f}%  AvgWin={avg_win:5.2f}%  AvgLoss={avg_loss:5.2f}%  RRR={rrr:.2f}")
    
    # =============================================
    # TEST 3: Simulated TREND FOLLOWING
    # =============================================
    print()
    print("=" * 70)
    print("📈 TEST 3: Simulated TREND FOLLOWING (Follow last candle)")  
    print("   Logic: If pattern ends '+', bet UP. If '-', bet DOWN.")
    print("=" * 70)
    
    df_directional['trend_dir'] = df_directional['last_char'].apply(lambda x: 'UP' if x == '+' else 'DOWN')
    df_directional['trend_correct'] = (df_directional['trend_dir'] == df_directional['actual_dir']).astype(int)
    df_directional['trend_return'] = df_directional.apply(
        lambda row: abs(row['actual_return']) if row['trend_correct'] == 1 else -abs(row['actual_return']),
        axis=1
    )
    
    for sym, grp in df_directional.groupby('symbol'):
        wins = grp[grp['trend_correct'] == 1]
        losses = grp[grp['trend_correct'] == 0]
        win_rate = len(wins) / len(grp) * 100 if len(grp) > 0 else 0
        avg_win = abs(grp[grp['trend_return'] > 0]['trend_return'].mean()) if len(wins) > 0 else 0
        avg_loss = abs(grp[grp['trend_return'] <= 0]['trend_return'].mean()) if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"   {sym:<8} Count={len(grp):<5} WinRate={win_rate:5.1f}%  AvgWin={avg_win:5.2f}%  AvgLoss={avg_loss:5.2f}%  RRR={rrr:.2f}")

    # =============================================
    # TEST 4: Strategy Comparison Summary
    # =============================================
    print()
    print("=" * 70)
    print("🏆 STRATEGY COMPARISON (Overall)")
    print("=" * 70)
    
    # Overall Stats
    stat_wins = df['correct'].sum()
    stat_total = len(df)
    stat_wr = stat_wins / stat_total * 100 if stat_total > 0 else 0
    
    rev_wins = df_directional['reversion_correct'].sum()
    rev_total = len(df_directional)
    rev_wr = rev_wins / rev_total * 100 if rev_total > 0 else 0
    
    trend_wins = df_directional['trend_correct'].sum()
    trend_total = len(df_directional)
    trend_wr = trend_wins / trend_total * 100 if trend_total > 0 else 0
    
    # RRR
    stat_avg_w = abs(df[df['trader_return'] > 0]['trader_return'].mean())
    stat_avg_l = abs(df[df['trader_return'] <= 0]['trader_return'].mean())
    stat_rrr = stat_avg_w / stat_avg_l if stat_avg_l > 0 else 0
    
    rev_avg_w = abs(df_directional[df_directional['reversion_return'] > 0]['reversion_return'].mean())
    rev_avg_l = abs(df_directional[df_directional['reversion_return'] <= 0]['reversion_return'].mean())
    rev_rrr = rev_avg_w / rev_avg_l if rev_avg_l > 0 else 0
    
    trend_avg_w = abs(df_directional[df_directional['trend_return'] > 0]['trend_return'].mean())
    trend_avg_l = abs(df_directional[df_directional['trend_return'] <= 0]['trend_return'].mean())
    trend_rrr = trend_avg_w / trend_avg_l if trend_avg_l > 0 else 0
    
    print(f"   {'Strategy':<20} {'Count':<8} {'WinRate':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<6}")
    print(f"   {'-'*64}")
    print(f"   {'STAT_FOLLOW':<20} {stat_total:<8} {stat_wr:>6.1f}%   {stat_avg_w:>6.2f}%   {stat_avg_l:>6.2f}%   {stat_rrr:.2f}")
    print(f"   {'MEAN_REVERSION':<20} {rev_total:<8} {rev_wr:>6.1f}%   {rev_avg_w:>6.2f}%   {rev_avg_l:>6.2f}%   {rev_rrr:.2f}")
    print(f"   {'TREND_FOLLOW':<20} {trend_total:<8} {trend_wr:>6.1f}%   {trend_avg_w:>6.2f}%   {trend_avg_l:>6.2f}%   {trend_rrr:.2f}")
    
    # =============================================
    # TEST 5: High Prob Only (>55%)
    # =============================================
    print()
    print("=" * 70)
    print("🔎 TEST 5: Confidence Filter (Only Prob > 55%)")
    print("=" * 70)
    
    df_high = df[df['prob'] > 55].copy()
    print(f"   Trades with Prob > 55%: {len(df_high)} / {len(df)} ({len(df_high)/len(df)*100:.1f}%)")
    
    if len(df_high) > 0:
        # STAT_FOLLOW with high prob
        high_wins = df_high['correct'].sum()
        high_wr = high_wins / len(df_high) * 100
        high_avg_w = abs(df_high[df_high['trader_return'] > 0]['trader_return'].mean())
        high_avg_l = abs(df_high[df_high['trader_return'] <= 0]['trader_return'].mean())
        high_rrr = high_avg_w / high_avg_l if high_avg_l > 0 else 0
        print(f"   STAT_FOLLOW (>55%): WinRate={high_wr:.1f}%  AvgWin={high_avg_w:.2f}%  AvgLoss={high_avg_l:.2f}%  RRR={high_rrr:.2f}")
        
        # Per Symbol
        print(f"\n   Per Symbol (Prob > 55%):")
        for sym, grp in df_high.groupby('symbol'):
            if len(grp) < 10: continue
            w = grp['correct'].sum()
            wr = w / len(grp) * 100
            aw = abs(grp[grp['trader_return'] > 0]['trader_return'].mean()) if w > 0 else 0
            al = abs(grp[grp['trader_return'] <= 0]['trader_return'].mean()) if (len(grp) - w) > 0 else 0
            r = aw / al if al > 0 else 0
            print(f"   {sym:<8} Count={len(grp):<5} WinRate={wr:5.1f}%  RRR={r:.2f}")
    
    # =============================================
    # TEST 6: Mean Reversion + High Prob Filter
    # =============================================
    print()
    print("=" * 70)
    print("🔎 TEST 6: MEAN REVERSION + Confidence Filter (Prob > 55%)")
    print("=" * 70)
    
    df_rev_high = df_directional[df_directional['prob'] > 55].copy()
    if len(df_rev_high) > 0:
        rev_h_wins = df_rev_high['reversion_correct'].sum()
        rev_h_wr = rev_h_wins / len(df_rev_high) * 100
        rev_h_aw = abs(df_rev_high[df_rev_high['reversion_return'] > 0]['reversion_return'].mean())
        rev_h_al = abs(df_rev_high[df_rev_high['reversion_return'] <= 0]['reversion_return'].mean())
        rev_h_rrr = rev_h_aw / rev_h_al if rev_h_al > 0 else 0
        print(f"   MEAN_REVERSION (>55%): Count={len(df_rev_high)}  WinRate={rev_h_wr:.1f}%  RRR={rev_h_rrr:.2f}")
        
        for sym, grp in df_rev_high.groupby('symbol'):
            if len(grp) < 10: continue
            w = grp['reversion_correct'].sum()
            wr = w / len(grp) * 100
            aw = abs(grp[grp['reversion_return'] > 0]['reversion_return'].mean()) if w > 0 else 0
            al = abs(grp[grp['reversion_return'] <= 0]['reversion_return'].mean()) if (len(grp) - w) > 0 else 0
            r = aw / al if al > 0 else 0
            print(f"   {sym:<8} Count={len(grp):<5} WinRate={wr:5.1f}%  RRR={r:.2f}")

if __name__ == "__main__":
    analyze()
