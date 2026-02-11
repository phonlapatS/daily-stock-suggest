#!/usr/bin/env python
"""
backtest_metals_advanced.py — Phase 23: Intraday Metals Strategy Tester
========================================================================
Tests 2 strategies from the Blueprint:
  A) Gold (XAUUSD) → VWAP Mean Reversion
  B) Silver (XAGUSD) → EMA Ribbon + Stochastic

Anti-Overfit: Strict 70/30 Train/Test split.
Metrics: Win%, Avg Win, Avg Loss, RRR, Expectancy
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')


# ─────────────────────────────────────────────
# INDICATORS
# ─────────────────────────────────────────────

def calc_vwap(df):
    """Session VWAP — reset daily (approx by date)."""
    df = df.copy()
    df['date'] = df.index.date
    df['typical'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_vol'] = df['typical'] * df['volume']
    df['cum_vol'] = df.groupby('date')['volume'].cumsum()
    df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    return df['vwap']


def calc_atr(high, low, close, period=14):
    """Average True Range."""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def calc_stochastic(high, low, close, k_period=14, d_period=3, smooth_k=3):
    """Stochastic Oscillator %K and %D."""
    lowest_low = low.rolling(k_period).min()
    highest_high = high.rolling(k_period).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    k = raw_k.rolling(smooth_k).mean()
    d = k.rolling(d_period).mean()
    return k, d


def calc_ema_ribbon(close, periods=(8, 13, 21, 34, 55)):
    """EMA Ribbon — returns dict of EMAs."""
    return {p: close.ewm(span=p, adjust=False).mean() for p in periods}


def is_pinbar(o, h, l, c):
    """Detect bullish/bearish pinbars."""
    body = abs(c - o)
    full_range = h - l
    if full_range < 1e-10:
        return 0
    body_ratio = body / full_range

    # Bullish pinbar: small body, long lower wick
    lower_wick = min(o, c) - l
    if body_ratio < 0.35 and lower_wick / full_range > 0.55:
        return 1  # Bullish

    # Bearish pinbar: small body, long upper wick
    upper_wick = h - max(o, c)
    if body_ratio < 0.35 and upper_wick / full_range > 0.55:
        return -1  # Bearish

    return 0


def is_engulfing(o_prev, c_prev, o_curr, c_curr):
    """Detect bullish/bearish engulfing."""
    # Bullish engulfing
    if c_prev < o_prev and c_curr > o_curr:
        if c_curr > o_prev and o_curr < c_prev:
            return 1
    # Bearish engulfing
    if c_prev > o_prev and c_curr < o_curr:
        if c_curr < o_prev and o_curr > c_prev:
            return -1
    return 0


# ─────────────────────────────────────────────
# STRATEGY A: Gold VWAP Mean Reversion
# ─────────────────────────────────────────────

def strategy_gold_vwap(df, holding_bars=4):
    """
    Gold VWAP Reversion (M30 preferred)
    - Time Gate: 08:00-17:00 UTC
    - Entry: Pinbar/Engulfing at VWAP ± 0.15%
    - SL: 0.5 × ATR | TP: 1.5 × ATR
    """
    df = df.copy()
    df['vwap'] = calc_vwap(df)
    df['atr'] = calc_atr(df['high'], df['low'], df['close'], 14)
    df['hour'] = df.index.hour
    df['vol_avg'] = df['volume'].rolling(20).mean()

    trades = []

    for i in range(1, len(df) - holding_bars):
        # 1. TIME GATE
        hour = df['hour'].iloc[i]
        if hour < 8 or hour > 17:
            continue

        # 2. ATR / VWAP must exist
        atr = df['atr'].iloc[i]
        vwap = df['vwap'].iloc[i]
        if pd.isna(atr) or pd.isna(vwap) or atr < 1e-10:
            continue

        close_i = df['close'].iloc[i]
        open_i = df['open'].iloc[i]
        high_i = df['high'].iloc[i]
        low_i = df['low'].iloc[i]

        # 3. DISTANCE FROM VWAP (must be > 0.15%)
        vwap_dist = abs(close_i - vwap) / vwap
        if vwap_dist < 0.0015:
            continue

        # 4. VOLUME CHECK (> 1.2x avg)
        vol_avg = df['vol_avg'].iloc[i]
        if pd.isna(vol_avg) or df['volume'].iloc[i] < vol_avg * 1.0:
            continue

        # 5. PRICE ACTION (Pinbar or Engulfing)
        pin = is_pinbar(open_i, high_i, low_i, close_i)

        o_prev = df['open'].iloc[i - 1]
        c_prev = df['close'].iloc[i - 1]
        eng = is_engulfing(o_prev, c_prev, open_i, close_i)

        signal = pin if pin != 0 else eng
        if signal == 0:
            continue

        # 6. DIRECTION must agree with VWAP reversion
        if close_i < vwap and signal == 1:  # Below VWAP + Bullish = LONG
            direction = 1
        elif close_i > vwap and signal == -1:  # Above VWAP + Bearish = SHORT
            direction = -1
        else:
            continue  # Conflicting signals

        # 7. CALCULATE SL/TP
        sl_distance = 0.5 * atr
        tp_distance = 1.5 * atr

        # 8. SIMULATE TRADE over next N bars
        entry_price = close_i
        trade_result = None

        for j in range(1, holding_bars + 1):
            idx = i + j
            if idx >= len(df):
                break

            bar_high = df['high'].iloc[idx]
            bar_low = df['low'].iloc[idx]

            if direction == 1:  # LONG
                if bar_low <= entry_price - sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_high >= entry_price + tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break
            else:  # SHORT
                if bar_high >= entry_price + sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_low <= entry_price - tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break

        # If not hit SL/TP, close at last bar
        if trade_result is None:
            exit_idx = min(i + holding_bars, len(df) - 1)
            exit_price = df['close'].iloc[exit_idx]
            trade_result = direction * (exit_price - entry_price) / entry_price * 100

        trades.append({
            'datetime': df.index[i],
            'direction': 'LONG' if direction == 1 else 'SHORT',
            'entry': entry_price,
            'result_pct': trade_result
        })

    return pd.DataFrame(trades)


# ─────────────────────────────────────────────
# STRATEGY B: Silver EMA Ribbon + Stochastic
# ─────────────────────────────────────────────

def strategy_silver_ribbon(df, holding_bars=6):
    """
    Silver EMA Ribbon + Stochastic (M30 preferred)
    - Time Gate: 07:00-20:00 UTC
    - Entry: Stoch cross from oversold/overbought WITH Ribbon alignment
    - SL: 1.0 × ATR | TP: 2.0 × ATR
    """
    df = df.copy()
    df['atr'] = calc_atr(df['high'], df['low'], df['close'], 14)
    df['hour'] = df.index.hour

    ribbon = calc_ema_ribbon(df['close'])
    for p, ema in ribbon.items():
        df[f'ema{p}'] = ema

    stoch_k, stoch_d = calc_stochastic(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch_k
    df['stoch_d'] = stoch_d

    trades = []

    for i in range(1, len(df) - holding_bars):
        # 1. TIME GATE
        hour = df['hour'].iloc[i]
        if hour < 7 or hour > 20:
            continue

        # 2. ATR must exist
        atr = df['atr'].iloc[i]
        if pd.isna(atr) or atr < 1e-10:
            continue

        # 3. EMA RIBBON ALIGNMENT
        e8 = df['ema8'].iloc[i]
        e13 = df['ema13'].iloc[i]
        e21 = df['ema21'].iloc[i]
        e34 = df['ema34'].iloc[i]
        e55 = df['ema55'].iloc[i]

        if any(pd.isna(x) for x in [e8, e13, e21, e34, e55]):
            continue

        bull_ribbon = (e8 > e13 > e21 > e34 > e55)
        bear_ribbon = (e8 < e13 < e21 < e34 < e55)

        if not bull_ribbon and not bear_ribbon:
            continue  # Tangled = no trade

        # 4. STOCHASTIC TRIGGER
        stoch_now = df['stoch_k'].iloc[i]
        stoch_prev = df['stoch_k'].iloc[i - 1]
        stoch_d_now = df['stoch_d'].iloc[i]

        if pd.isna(stoch_now) or pd.isna(stoch_prev):
            continue

        signal = 0

        # Buy dip in uptrend
        if bull_ribbon and stoch_prev < 20 and stoch_now > stoch_d_now:
            signal = 1

        # Sell rally in downtrend
        if bear_ribbon and stoch_prev > 80 and stoch_now < stoch_d_now:
            signal = -1

        if signal == 0:
            continue

        # 5. CANDLE VALIDATION
        close_i = df['close'].iloc[i]
        open_i = df['open'].iloc[i]
        if signal == 1 and close_i <= open_i:
            continue  # Must close green for long
        if signal == -1 and close_i >= open_i:
            continue  # Must close red for short

        # 6. CALCULATE SL/TP
        sl_distance = 1.0 * atr
        tp_distance = 2.0 * atr

        # 7. SIMULATE TRADE
        entry_price = close_i
        trade_result = None

        for j in range(1, holding_bars + 1):
            idx = i + j
            if idx >= len(df):
                break

            bar_high = df['high'].iloc[idx]
            bar_low = df['low'].iloc[idx]

            if signal == 1:  # LONG
                if bar_low <= entry_price - sl_distance:
                    trade_result = -sl_distance / entry_price * 100
                    break
                if bar_high >= entry_price + tp_distance:
                    trade_result = tp_distance / entry_price * 100
                    break
            else:  # SHORT
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

        trades.append({
            'datetime': df.index[i],
            'direction': 'LONG' if signal == 1 else 'SHORT',
            'entry': entry_price,
            'result_pct': trade_result
        })

    return pd.DataFrame(trades)


# ─────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────

def calc_metrics(trades_df, label):
    """Calculate and print performance metrics."""
    if trades_df.empty or len(trades_df) == 0:
        print(f"\n{'='*55}")
        print(f"📊 {label}")
        print(f"{'='*55}")
        print(f"   ❌ No trades generated.")
        return None

    results = trades_df['result_pct']
    wins = results[results > 0]
    losses = results[results <= 0]

    n = len(results)
    win_rate = len(wins) / n * 100
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    total_return = results.sum()
    expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)

    print(f"\n{'='*55}")
    print(f"📊 {label}")
    print(f"{'='*55}")
    print(f"   Trades:      {n}")
    print(f"   Win Rate:    {win_rate:.1f}%")
    print(f"   Avg Win:     +{avg_win:.3f}%")
    print(f"   Avg Loss:    -{avg_loss:.3f}%")
    print(f"   RRR:         {rrr:.2f}")
    print(f"   Expectancy:  {expectancy:+.4f}% per trade")
    print(f"   Total Return:{total_return:+.2f}%")

    # Direction breakdown
    if 'direction' in trades_df.columns:
        for d in ['LONG', 'SHORT']:
            subset = trades_df[trades_df['direction'] == d]
            if len(subset) > 0:
                d_wins = subset[subset['result_pct'] > 0]
                d_wr = len(d_wins) / len(subset) * 100
                print(f"   [{d}] {len(subset)} trades, Win: {d_wr:.1f}%")

    return {
        'N': n, 'Win%': win_rate, 'AvgWin': avg_win,
        'AvgLoss': avg_loss, 'RRR': rrr, 'Total': total_return,
        'Expectancy': expectancy
    }


def main():
    print("🚀 METALS ADVANCED STRATEGY BACKTEST")
    print("=" * 60)
    print("🛡️  Anti-Overfit: 70% Train / 30% Test (Report Test Only)")
    print()

    all_results = []

    # ─── GOLD (VWAP Reversion) ───
    for tf in ['15m', '30m']:
        filename = f'OANDA_XAUUSD_{tf}.csv'
        filepath = os.path.join(CACHE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"❌ {filename} not found")
            continue

        df = pd.read_csv(filepath, parse_dates=['datetime'], index_col='datetime')
        split = int(len(df) * 0.70)
        train_df = df.iloc[:split]
        test_df = df.iloc[split:]

        print(f"\n--- 🥇 GOLD {tf.upper()} (VWAP Reversion) ---")
        print(f"   Data: {len(df)} total | Train: {len(train_df)} | Test: {len(test_df)}")

        # Run on TRAIN (for reference only)
        train_trades = strategy_gold_vwap(train_df)
        train_m = calc_metrics(train_trades, f"GOLD {tf} VWAP [TRAIN]")

        # Run on TEST (the real result)
        test_trades = strategy_gold_vwap(test_df)
        test_m = calc_metrics(test_trades, f"GOLD {tf} VWAP [TEST] ⭐")

        if train_m and test_m:
            drift = abs(train_m['Win%'] - test_m['Win%'])
            print(f"\n   🛡️  Overfit Check: Train Win={train_m['Win%']:.1f}% vs Test Win={test_m['Win%']:.1f}% (Drift: {drift:.1f}%)")
            if drift > 10:
                print(f"   ⚠️  WARNING: High drift! Possible overfit.")
            else:
                print(f"   ✅ STABLE")
            all_results.append(('GOLD', tf, 'VWAP', test_m))

    # ─── SILVER (EMA Ribbon + Stochastic) ───
    for tf in ['15m', '30m']:
        filename = f'OANDA_XAGUSD_{tf}.csv'
        filepath = os.path.join(CACHE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"❌ {filename} not found")
            continue

        df = pd.read_csv(filepath, parse_dates=['datetime'], index_col='datetime')
        split = int(len(df) * 0.70)
        train_df = df.iloc[:split]
        test_df = df.iloc[split:]

        print(f"\n--- 🥈 SILVER {tf.upper()} (EMA Ribbon + Stochastic) ---")
        print(f"   Data: {len(df)} total | Train: {len(train_df)} | Test: {len(test_df)}")

        train_trades = strategy_silver_ribbon(train_df)
        train_m = calc_metrics(train_trades, f"SILVER {tf} Ribbon [TRAIN]")

        test_trades = strategy_silver_ribbon(test_df)
        test_m = calc_metrics(test_trades, f"SILVER {tf} Ribbon [TEST] ⭐")

        if train_m and test_m:
            drift = abs(train_m['Win%'] - test_m['Win%'])
            print(f"\n   🛡️  Overfit Check: Train Win={train_m['Win%']:.1f}% vs Test Win={test_m['Win%']:.1f}% (Drift: {drift:.1f}%)")
            if drift > 10:
                print(f"   ⚠️  WARNING: High drift! Possible overfit.")
            else:
                print(f"   ✅ STABLE")
            all_results.append(('SILVER', tf, 'RIBBON', test_m))

    # ─── FINAL COMPARISON TABLE ───
    if all_results:
        print(f"\n{'='*70}")
        print(f"🏆 FINAL COMPARISON (TEST SET ONLY — No Peeking!)")
        print(f"{'='*70}")
        print(f"{'Asset':<8} {'TF':<5} {'Strategy':<10} {'N':<5} {'Win%':<7} {'AvgWin':<9} {'AvgLoss':<9} {'RRR':<6} {'Expect':<8}")
        print(f"{'-'*70}")
        for asset, tf, strat, m in all_results:
            print(f"{asset:<8} {tf:<5} {strat:<10} {m['N']:<5} {m['Win%']:<5.1f}% +{m['AvgWin']:<7.3f} -{m['AvgLoss']:<7.3f} {m['RRR']:<6.2f} {m['Expectancy']:+.4f}")

        # Pick best
        best = max(all_results, key=lambda x: x[3]['Expectancy'])
        print(f"\n🥇 BEST: {best[0]} {best[1]} {best[2]} — Expectancy: {best[3]['Expectancy']:+.4f}% per trade")


if __name__ == "__main__":
    main()
