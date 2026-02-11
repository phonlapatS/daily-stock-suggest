#!/usr/bin/env python
"""
tune_metals_winrate.py — Find TP/SL that achieves Win% > 60%
=============================================================
Sweep multiple TP multipliers to find the sweet spot.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')


def calc_vwap(df):
    df = df.copy()
    df['date'] = df.index.date
    df['typical'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_vol'] = df['typical'] * df['volume']
    df['cum_vol'] = df.groupby('date')['volume'].cumsum()
    df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    return df['vwap']


def calc_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def calc_stochastic(high, low, close, k_period=14, d_period=3, smooth_k=3):
    lowest_low = low.rolling(k_period).min()
    highest_high = high.rolling(k_period).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    k = raw_k.rolling(smooth_k).mean()
    d = k.rolling(d_period).mean()
    return k, d


def is_pinbar(o, h, l, c):
    body = abs(c - o)
    full_range = h - l
    if full_range < 1e-10:
        return 0
    body_ratio = body / full_range
    lower_wick = min(o, c) - l
    if body_ratio < 0.35 and lower_wick / full_range > 0.55:
        return 1
    upper_wick = h - max(o, c)
    if body_ratio < 0.35 and upper_wick / full_range > 0.55:
        return -1
    return 0


def is_engulfing(o_prev, c_prev, o_curr, c_curr):
    if c_prev < o_prev and c_curr > o_curr:
        if c_curr > o_prev and o_curr < c_prev:
            return 1
    if c_prev > o_prev and c_curr < o_curr:
        if c_curr < o_prev and o_curr > c_prev:
            return -1
    return 0


def run_gold_vwap(df, sl_mult, tp_mult, holding_bars=4):
    """Gold VWAP Reversion with adjustable SL/TP."""
    df = df.copy()
    df['vwap'] = calc_vwap(df)
    df['atr'] = calc_atr(df['high'], df['low'], df['close'], 14)
    df['hour'] = df.index.hour
    df['vol_avg'] = df['volume'].rolling(20).mean()

    trades = []
    for i in range(1, len(df) - holding_bars):
        hour = df['hour'].iloc[i]
        if hour < 8 or hour > 17:
            continue
        atr = df['atr'].iloc[i]
        vwap = df['vwap'].iloc[i]
        if pd.isna(atr) or pd.isna(vwap) or atr < 1e-10:
            continue

        close_i = df['close'].iloc[i]
        open_i = df['open'].iloc[i]
        high_i = df['high'].iloc[i]
        low_i = df['low'].iloc[i]

        vwap_dist = abs(close_i - vwap) / vwap
        if vwap_dist < 0.0015:
            continue

        vol_avg = df['vol_avg'].iloc[i]
        if pd.isna(vol_avg) or df['volume'].iloc[i] < vol_avg * 1.0:
            continue

        pin = is_pinbar(open_i, high_i, low_i, close_i)
        o_prev = df['open'].iloc[i - 1]
        c_prev = df['close'].iloc[i - 1]
        eng = is_engulfing(o_prev, c_prev, open_i, close_i)
        signal = pin if pin != 0 else eng
        if signal == 0:
            continue

        if close_i < vwap and signal == 1:
            direction = 1
        elif close_i > vwap and signal == -1:
            direction = -1
        else:
            continue

        sl_distance = sl_mult * atr
        tp_distance = tp_mult * atr
        entry_price = close_i
        trade_result = None

        for j in range(1, holding_bars + 1):
            idx = i + j
            if idx >= len(df):
                break
            bar_high = df['high'].iloc[idx]
            bar_low = df['low'].iloc[idx]
            if direction == 1:
                if bar_low <= entry_price - sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_high >= entry_price + tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break
            else:
                if bar_high >= entry_price + sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_low <= entry_price - tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break

        if trade_result is None:
            exit_idx = min(i + holding_bars, len(df) - 1)
            exit_price = df['close'].iloc[exit_idx]
            trade_result = direction * (exit_price - entry_price) / entry_price * 100

        trades.append(trade_result)

    return trades


def run_silver_trend(df, sl_mult, tp_mult, holding_bars=6):
    """Silver Trend Following with EMA(21) filter + Stochastic (relaxed)."""
    df = df.copy()
    df['atr'] = calc_atr(df['high'], df['low'], df['close'], 14)
    df['hour'] = df.index.hour
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema55'] = df['close'].ewm(span=55, adjust=False).mean()

    stoch_k, stoch_d = calc_stochastic(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch_k
    df['stoch_d'] = stoch_d

    trades = []
    for i in range(1, len(df) - holding_bars):
        hour = df['hour'].iloc[i]
        if hour < 7 or hour > 20:
            continue

        atr = df['atr'].iloc[i]
        if pd.isna(atr) or atr < 1e-10:
            continue

        e21 = df['ema21'].iloc[i]
        e55 = df['ema55'].iloc[i]
        if pd.isna(e21) or pd.isna(e55):
            continue

        bull_trend = (e21 > e55) and (df['close'].iloc[i] > e21)
        bear_trend = (e21 < e55) and (df['close'].iloc[i] < e21)

        if not bull_trend and not bear_trend:
            continue

        stoch_now = df['stoch_k'].iloc[i]
        stoch_prev = df['stoch_k'].iloc[i - 1]
        stoch_d_now = df['stoch_d'].iloc[i]
        if pd.isna(stoch_now) or pd.isna(stoch_prev):
            continue

        signal = 0
        # Relaxed: Stoch < 30 (was 20) for buy dip
        if bull_trend and stoch_prev < 30 and stoch_now > stoch_d_now:
            signal = 1
        if bear_trend and stoch_prev > 70 and stoch_now < stoch_d_now:
            signal = -1
        if signal == 0:
            continue

        close_i = df['close'].iloc[i]
        open_i = df['open'].iloc[i]
        if signal == 1 and close_i <= open_i:
            continue
        if signal == -1 and close_i >= open_i:
            continue

        sl_distance = sl_mult * atr
        tp_distance = tp_mult * atr
        entry_price = close_i
        trade_result = None

        for j in range(1, holding_bars + 1):
            idx = i + j
            if idx >= len(df):
                break
            bar_high = df['high'].iloc[idx]
            bar_low = df['low'].iloc[idx]
            if signal == 1:
                if bar_low <= entry_price - sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_high >= entry_price + tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break
            else:
                if bar_high >= entry_price + sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_low <= entry_price - tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break

        if trade_result is None:
            exit_idx = min(i + holding_bars, len(df) - 1)
            exit_price = df['close'].iloc[exit_idx]
            trade_result = signal * (exit_price - entry_price) / entry_price * 100

        trades.append(trade_result)

    return trades


def calc_stats(trades):
    if not trades:
        return None
    arr = np.array(trades)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    n = len(arr)
    win_rate = len(wins) / n * 100
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
    return {'N': n, 'Win%': win_rate, 'AvgWin': avg_win, 'AvgLoss': avg_loss, 'RRR': rrr, 'Expect': expectancy}


def main():
    print("🎯 PARAMETER SWEEP: Finding Win% > 60% Sweet Spot")
    print("=" * 75)

    # TP multipliers to test
    tp_values = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5]

    # ─── GOLD 30m (Best from previous test) ───
    gold_file = os.path.join(CACHE_DIR, 'OANDA_XAUUSD_30m.csv')
    if os.path.exists(gold_file):
        df_gold = pd.read_csv(gold_file, parse_dates=['datetime'], index_col='datetime')
        split = int(len(df_gold) * 0.70)
        test_gold = df_gold.iloc[split:]

        print(f"\n🥇 GOLD 30m VWAP — TP Sweep (SL fixed at 0.5×ATR)")
        print(f"{'TP(×ATR)':<10} {'N':<5} {'Win%':<8} {'AvgWin':<10} {'AvgLoss':<10} {'RRR':<6} {'Expect':<10} {'Verdict':<10}")
        print("-" * 75)

        for tp in tp_values:
            trades = run_gold_vwap(test_gold, sl_mult=0.5, tp_mult=tp, holding_bars=4)
            stats = calc_stats(trades)
            if stats:
                verdict = "✅ TARGET" if stats['Win%'] >= 60 else "❌"
                star = " 🏆" if stats['Win%'] >= 60 and stats['RRR'] >= 1.0 else ""
                print(f"{tp:<10.1f} {stats['N']:<5} {stats['Win%']:<6.1f}% +{stats['AvgWin']:<8.3f} -{stats['AvgLoss']:<8.3f} {stats['RRR']:<6.2f} {stats['Expect']:+.4f}%  {verdict}{star}")

    # ─── SILVER 30m (Relaxed Ribbon → Trend + Stoch) ───
    silver_file = os.path.join(CACHE_DIR, 'OANDA_XAGUSD_30m.csv')
    if os.path.exists(silver_file):
        df_silver = pd.read_csv(silver_file, parse_dates=['datetime'], index_col='datetime')
        split = int(len(df_silver) * 0.70)
        test_silver = df_silver.iloc[split:]

        print(f"\n🥈 SILVER 30m Trend+Stoch — TP Sweep (SL fixed at 1.0×ATR)")
        print(f"{'TP(×ATR)':<10} {'N':<5} {'Win%':<8} {'AvgWin':<10} {'AvgLoss':<10} {'RRR':<6} {'Expect':<10} {'Verdict':<10}")
        print("-" * 75)

        for tp in tp_values:
            trades = run_silver_trend(test_silver, sl_mult=1.0, tp_mult=tp, holding_bars=6)
            stats = calc_stats(trades)
            if stats:
                verdict = "✅ TARGET" if stats['Win%'] >= 60 else "❌"
                star = " 🏆" if stats['Win%'] >= 60 and stats['RRR'] >= 1.0 else ""
                print(f"{tp:<10.1f} {stats['N']:<5} {stats['Win%']:<6.1f}% +{stats['AvgWin']:<8.3f} -{stats['AvgLoss']:<8.3f} {stats['RRR']:<6.2f} {stats['Expect']:+.4f}%  {verdict}{star}")

    # ─── SILVER 15m as well ───
    silver_15_file = os.path.join(CACHE_DIR, 'OANDA_XAGUSD_15m.csv')
    if os.path.exists(silver_15_file):
        df_s15 = pd.read_csv(silver_15_file, parse_dates=['datetime'], index_col='datetime')
        split = int(len(df_s15) * 0.70)
        test_s15 = df_s15.iloc[split:]

        print(f"\n🥈 SILVER 15m Trend+Stoch — TP Sweep (SL fixed at 1.0×ATR)")
        print(f"{'TP(×ATR)':<10} {'N':<5} {'Win%':<8} {'AvgWin':<10} {'AvgLoss':<10} {'RRR':<6} {'Expect':<10} {'Verdict':<10}")
        print("-" * 75)

        for tp in tp_values:
            trades = run_silver_trend(test_s15, sl_mult=1.0, tp_mult=tp, holding_bars=6)
            stats = calc_stats(trades)
            if stats:
                verdict = "✅ TARGET" if stats['Win%'] >= 60 else "❌"
                star = " 🏆" if stats['Win%'] >= 60 and stats['RRR'] >= 1.0 else ""
                print(f"{tp:<10.1f} {stats['N']:<5} {stats['Win%']:<6.1f}% +{stats['AvgWin']:<8.3f} -{stats['AvgLoss']:<8.3f} {stats['RRR']:<6.2f} {stats['Expect']:+.4f}%  {verdict}{star}")


if __name__ == "__main__":
    main()
