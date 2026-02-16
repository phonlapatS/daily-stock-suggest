#!/usr/bin/env python
"""
plot_markets_from_metrics.py
============================

Plot cumulative return curves for ALL symbols that pass the same
criteria used in `calculate_metrics.py` tables, separated by market.

This lets you see, for each stock that passes the filter:
- How cumulative return has evolved through time
- Whether there were long drawdown periods

Sources:
- Aggregated metrics: data/symbol_performance.csv
- Raw trades: logs/trade_history.csv

Usage:
    python scripts/plot_markets_from_metrics.py
"""

import os
from typing import Dict, List, Set

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")


def load_metrics(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Metrics file not found: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        print("⚠️ Metrics file is empty.")
        return pd.DataFrame()

    df["symbol"] = df["symbol"].astype(str)
    return df


def load_trades(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Trade history not found: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path, engine="python", on_bad_lines="skip")
    if df.empty:
        print("⚠️ Trade history is empty.")
        return pd.DataFrame()

    # Handle mixed schemas: ensure these exist
    if "date" not in df.columns:
        print("❌ trade_history.csv has no 'date' column.")
        return pd.DataFrame()
    if "symbol" not in df.columns:
        print("❌ trade_history.csv has no 'symbol' column.")
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    df["symbol"] = df["symbol"].astype(str)

    # trader_return already includes direction & threshold logic from backtest;
    # if missing, derive from forecast + actual_return.
    if "trader_return" not in df.columns:
        if {"forecast", "actual_return"}.issubset(df.columns):
            df["actual_return"] = pd.to_numeric(df["actual_return"], errors="coerce").fillna(0.0)
            df["trader_return"] = df.apply(
                lambda row: row["actual_return"] if str(row["forecast"]).upper() == "UP" else -row["actual_return"],
                axis=1,
            )
        else:
            print("❌ Cannot derive trader_return — missing forecast/actual_return.")
            return pd.DataFrame()

    return df


def select_symbols_by_market(df_metrics: pd.DataFrame) -> Dict[str, Set[str]]:
    """
    Reproduce the same filters used in calculate_metrics.py tables.
    Returns a dict of Country -> set(symbols).
    """
    selected: Dict[str, Set[str]] = {"TH": set(), "US": set(), "CN": set(), "TW": set(), "GL": set()}

    # THAI ELITE (TABLE 1): Prob > 55% AND RR > 1.2
    th_elite = df_metrics[
        (df_metrics["Country"] == "TH") & (df_metrics["Prob%"] > 55.0) & (df_metrics["RR_Ratio"] > 1.2)
    ]
    selected["TH"].update(th_elite["symbol"].tolist())

    # THAI BALANCED (TABLE 2): Prob > 60% AND 1.5 < RR <= 2.0
    th_bal = df_metrics[
        (df_metrics["Country"] == "TH")
        & (df_metrics["Prob%"] > 60.0)
        & (df_metrics["RR_Ratio"] > 1.5)
        & (df_metrics["RR_Ratio"] <= 2.0)
    ]
    selected["TH"].update(th_bal["symbol"].tolist())

    # US MARKET (TABLE 3B): Prob > 50% | RRR > 1.0
    us = df_metrics[(df_metrics["Country"] == "US") & (df_metrics["Prob%"] > 50.0) & (df_metrics["RR_Ratio"] > 1.0)]
    selected["US"].update(us["symbol"].tolist())

    # CHINA MARKET (TABLE 4): Prob > 50% | RRR > 1.0
    cn = df_metrics[(df_metrics["Country"] == "CN") & (df_metrics["Prob%"] > 50.0) & (df_metrics["RR_Ratio"] > 1.0)]
    selected["CN"].update(cn["symbol"].tolist())

    # TAIWAN MARKET (TABLE 6): Prob > 50% | RRR > 1.0
    tw = df_metrics[(df_metrics["Country"] == "TW") & (df_metrics["Prob%"] > 50.0) & (df_metrics["RR_Ratio"] > 1.0)]
    selected["TW"].update(tw["symbol"].tolist())

    # METALS (TABLE 7): Prob > 50% | RRR > 1.0
    gl = df_metrics[(df_metrics["Country"] == "GL") & (df_metrics["Prob%"] > 50.0) & (df_metrics["RR_Ratio"] > 1.0)]
    selected["GL"].update(gl["symbol"].tolist())

    return selected


def plot_market_panels(
    trades: pd.DataFrame,
    symbols_by_market: Dict[str, Set[str]],
    output_path: str = os.path.join(DATA_DIR, "market_equity_from_metrics.png"),
) -> None:
    market_defs = [
        ("TH", "Top Performing Elite Stocks: Thai Market (SET)"),
        ("US", "Top Performing Elite Stocks: US Market (NASDAQ)"),
        ("CN", "Top Performing Elite Stocks: China/HK Market (HKEX)"),
        ("TW", "Top Performing Elite Stocks: Taiwan Market (TWSE)"),
    ]

    fig, axes = plt.subplots(len(market_defs), 1, figsize=(10, 3.5 * len(market_defs)), dpi=120)
    if len(market_defs) == 1:
        axes = [axes]

    for idx, (code, title) in enumerate(market_defs):
        ax = axes[idx]
        syms = symbols_by_market.get(code, set())
        if not syms:
            ax.text(0.5, 0.5, "No symbols from metrics filter", ha="center", va="center", fontsize=11)
            ax.set_title(title, fontsize=10, fontweight="bold")
            ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
            ax.grid(True, alpha=0.2)
            continue

        # For each symbol, plot cumulative trader_return over time
        for sym in sorted(syms):
            sdf = trades[trades["symbol"] == sym].copy()
            if sdf.empty:
                continue

            sdf = sdf.sort_values("date")
            sdf["cum"] = sdf["trader_return"].cumsum()
            ax.plot(sdf["date"], sdf["cum"], linewidth=1.2, label=f"{sym} (N={len(sdf)})")

        ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel("Individual Cumulative Return (%)")
        ax.grid(True, linestyle=":", alpha=0.3)
        if ax.has_data():
            ax.legend(loc="upper left", fontsize=6, ncol=2)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    print(f"✅ Saved market equity plot to: {output_path}")


def main() -> None:
    metrics_path = os.path.join(DATA_DIR, "symbol_performance.csv")
    trades_path = os.path.join(LOG_DIR, "trade_history.csv")

    df_metrics = load_metrics(metrics_path)
    if df_metrics.empty:
        return

    df_trades = load_trades(trades_path)
    if df_trades.empty:
        return

    symbols_by_market = select_symbols_by_market(df_metrics)
    print("🎯 Symbols per market from metrics filters:")
    for k, v in symbols_by_market.items():
        print(f"  {k}: {sorted(v)}")

    plot_market_panels(df_trades, symbols_by_market)


if __name__ == "__main__":
    main()


