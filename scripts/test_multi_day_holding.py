#!/usr/bin/env python
"""
test_multi_day_holding.py
=========================
Experimental script to evaluate a "hold until forecast flips" strategy
using existing 1-day forecasts in logs/trade_history.csv.

Logic per symbol:
  - We iterate trades ordered by date.
  - Open a LONG position when forecast == 'UP' and there is no open trade.
  - While in a trade, we accumulate raw actual_return each day.
  - We exit the trade on the first day where forecast == 'DOWN'
    (after adding that day's actual_return).

This approximates the behavior:
  pattern today => forecast UP
  tomorrow => if forecast still UP, continue holding (+n2, +n3, ...)
  if forecast turns DOWN, close the streak.

We then compute:
  - Win rate (trade_return > 0)
  - AvgWin, AvgLoss
  - RRR = AvgWin / AvgLoss

The goal is to compare Thai vs US behavior under this multi-day holding
to see if RRR/Prob improve relative to the 1-day trades.
"""

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADE_FILE = os.path.join(BASE_DIR, "logs", "trade_history.csv")


def compute_multi_day_trades(df_symbol: pd.DataFrame) -> pd.DataFrame:
    """
    Build multi-day trades for a single symbol based on forecast sequence.

    Args:
        df_symbol: trades for one symbol, must have columns:
                   ['date', 'forecast', 'actual_return']

    Returns:
        DataFrame with one row per multi-day trade and columns:
        ['entry_date', 'exit_date', 'bars', 'trade_return']
    """
    df = df_symbol.sort_values("date").reset_index(drop=True)

    trades = []
    in_trade = False
    cum_ret = 0.0
    bars = 0
    entry_date = None

    for _, row in df.iterrows():
        forecast = str(row.get("forecast", "")).upper()
        actual_ret = float(row.get("actual_return", 0.0))
        date = row["date"]

        if not in_trade:
            # Open trade only on UP forecast
            if forecast == "UP":
                in_trade = True
                cum_ret = actual_ret
                bars = 1
                entry_date = date
        else:
            # Already in trade: accumulate return
            cum_ret += actual_ret
            bars += 1

            # Exit on DOWN forecast
            if forecast == "DOWN":
                trades.append(
                    {
                        "entry_date": entry_date,
                        "exit_date": date,
                        "bars": bars,
                        "trade_return": cum_ret,
                    }
                )
                in_trade = False
                cum_ret = 0.0
                bars = 0
                entry_date = None

    # If a trade is still open at the end, we close it at last bar
    if in_trade and bars > 0:
        last_date = df.iloc[-1]["date"]
        trades.append(
            {
                "entry_date": entry_date,
                "exit_date": last_date,
                "bars": bars,
                "trade_return": cum_ret,
            }
        )

    return pd.DataFrame(trades)


def summarize_trades(trades: pd.DataFrame) -> dict:
    """
    Compute Prob, AvgWin, AvgLoss, RRR for a set of trades.
    """
    if trades.empty:
        return {
            "trades": 0,
            "prob": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "rrr": 0.0,
        }

    rets = trades["trade_return"].astype(float)
    wins = rets[rets > 0]
    losses = rets[rets <= 0]

    trades_count = len(rets)
    prob = len(wins) / trades_count * 100 if trades_count > 0 else 0.0
    avg_win = wins.mean() if not wins.empty else 0.0
    avg_loss = abs(losses.mean()) if not losses.empty else 0.0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0.0

    return {
        "trades": trades_count,
        "prob": prob,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "rrr": rrr,
    }


def print_market_summary(df: pd.DataFrame, group_name: str, title: str, top_n: int = 20):
    """
    Print summary table for a given market group.
    """
    df_group = df[df["group"] == group_name].copy()
    if df_group.empty:
        print(f"\n{title}")
        print("=" * 100)
        print("No trades found for this group.")
        return

    df_group["date"] = pd.to_datetime(df_group["date"])

    rows = []
    for symbol, g in df_group.groupby("symbol"):
        multi_trades = compute_multi_day_trades(g)
        stats = summarize_trades(multi_trades)
        if stats["trades"] == 0:
            continue
        rows.append(
            {
                "symbol": symbol,
                "Count": stats["trades"],
                "Prob%": stats["prob"],
                "AvgWin%": stats["avg_win"],
                "AvgLoss%": stats["avg_loss"],
                "RRR": stats["rrr"],
            }
        )

    if not rows:
        print(f"\n{title}")
        print("=" * 100)
        print("No valid multi-day trades after filtering.")
        return

    df_stats = pd.DataFrame(rows)
    df_stats = df_stats.sort_values(by=["Prob%", "RRR"], ascending=[False, False]).head(top_n)

    print(f"\n{title}")
    print("=" * 100)
    print(f"{'Symbol':<10} {'Count':>8} {'Prob%':>8} {'AvgWin%':>10} {'AvgLoss%':>10} {'RRR':>6}")
    print("-" * 100)
    for _, row in df_stats.iterrows():
        print(
            f"{row['symbol']:<10} {int(row['Count']):>8d} "
            f"{row['Prob%']:>7.1f}% {row['AvgWin%']:>9.2f}% "
            f"{row['AvgLoss%']:>9.2f}% {row['RRR']:>6.2f}"
        )
    print("-" * 100)


def main():
    if not os.path.exists(TRADE_FILE):
        print(f"❌ Trade log not found: {TRADE_FILE}")
        sys.exit(1)

    print(f"📊 Loading trade history from: {TRADE_FILE}")
    df = pd.read_csv(TRADE_FILE, engine="python", on_bad_lines="skip")

    # Basic sanity check
    required_cols = {"date", "symbol", "group", "forecast", "actual_return"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"❌ Missing required columns in trade history: {missing}")
        sys.exit(1)

    print("\n🔬 MULTI-DAY HOLDING BACKTEST (Hold until forecast flips DOWN)")

    # Thai Market
    print_market_summary(df, "GROUP_A_THAI", "🇹🇭 THAI MARKET (Multi-day Holding)")

    # US Market
    print_market_summary(df, "GROUP_B_US", "🇺🇸 US MARKET (Multi-day Holding)")


if __name__ == "__main__":
    main()


