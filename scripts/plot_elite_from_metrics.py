#!/usr/bin/env python
"""
plot_elite_from_metrics.py
==========================

Plot multi-panel equity curves similar to the reference image:
- Top Performing Elite Stocks: Thai Market (SET)
- US Market (NASDAQ)
- China/HK Market (HKEX)
- Taiwan Market (TWSE)

Source data:
- Aggregated metrics: data/symbol_performance.csv (from calculate_metrics.py)
- Raw trades: logs/trade_history.csv

Usage:
    python scripts/plot_elite_from_metrics.py
"""

import os
from typing import Dict, List

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

    # Ensure required columns exist
    needed = {"symbol", "Country", "Count", "Prob%", "RR_Ratio", "AvgWin%", "AvgLoss%"}
    missing = needed - set(df.columns)
    if missing:
        print(f"⚠️ Metrics missing columns {missing} — some values will be zero.")
        for col in missing:
            df[col] = 0.0

    # Normalize symbol as string
    df["symbol"] = df["symbol"].astype(str)
    return df


def load_trades(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Trade history not found: {path}")
        return pd.DataFrame()

    # Use python engine & skip bad lines to handle legacy rows
    df = pd.read_csv(path, engine="python", on_bad_lines="skip")
    if df.empty:
        print("⚠️ Trade history is empty.")
        return pd.DataFrame()

    if "date" not in df.columns or "symbol" not in df.columns:
        print("❌ trade_history.csv does not have expected 'date'/'symbol' columns.")
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    df["symbol"] = df["symbol"].astype(str)

    # Ensure trader_return exists; if not, derive from forecast + actual_return
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


def select_elite_symbols(df_metrics: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Pick top symbols per market based purely on ranking (no hard filters).
    This is meant for visualization only (see full landscape), not for
    enforcing live-trading thresholds.
    """
    selections: Dict[str, List[str]] = {}

    # Market configs: how many lines to show per market
    configs = {
        "TH": {"top_n": 5},
        "US": {"top_n": 5},
        "CN": {"top_n": 5},
        "TW": {"top_n": 5},
    }

    for ctry, cfg in configs.items():
        sub = df_metrics[df_metrics["Country"] == ctry].copy()
        if sub.empty:
            selections[ctry] = []
            continue

        # Sort by Prob, then RRR, then Count (all descending)
        sub = sub.sort_values(["Prob%", "RR_Ratio", "Count"], ascending=[False, False, False])
        selections[ctry] = sub["symbol"].head(cfg["top_n"]).tolist()

    return selections


def plot_elite_equity(
    df_trades: pd.DataFrame,
    elite: Dict[str, List[str]],
    output_path: str = os.path.join(DATA_DIR, "elite_stocks_from_metrics.png"),
) -> None:
    market_meta = {
        "TH": {"title": "Top Performing Elite Stocks: Thai Market (SET)"},
        "US": {"title": "Top Performing Elite Stocks: US Market (NASDAQ)"},
        "CN": {"title": "Top Performing Elite Stocks: China/HK Market (HKEX)"},
        "TW": {"title": "Top Performing Elite Stocks: Taiwan Market (TWSE)"},
    }

    n_markets = len(market_meta)
    fig, axes = plt.subplots(n_markets, 1, figsize=(10, 3.5 * n_markets), dpi=120)
    if n_markets == 1:
        axes = [axes]

    # We assume group names in trade history reflect markets, but we primarily
    # filter by symbol lists from metrics.
    df_trades = df_trades.sort_values("date")

    for idx, (ctry, meta) in enumerate(market_meta.items()):
        ax = axes[idx]
        symbols = elite.get(ctry, [])
        if not symbols:
            ax.text(0.5, 0.5, "No symbols passing elite filter", ha="center", va="center", fontsize=11)
            ax.set_title(meta["title"], fontsize=10, fontweight="bold")
            ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
            ax.grid(True, alpha=0.2)
            continue

        for sym in symbols:
            sdf = df_trades[df_trades["symbol"] == sym].copy()
            if sdf.empty:
                continue

            sdf = sdf.sort_values("date")
            sdf["cum"] = sdf["trader_return"].cumsum()
            ax.plot(sdf["date"], sdf["cum"], linewidth=1.3, label=f"{sym} (N={len(sdf)})")

        ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_title(meta["title"], fontsize=10, fontweight="bold")
        ax.set_ylabel("Individual Cumulative Return (%)")
        ax.grid(True, linestyle=":", alpha=0.3)
        ax.legend(loc="upper left", fontsize=7, ncol=2)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    print(f"✅ Saved elite equity plot to: {output_path}")


def main() -> None:
    metrics_path = os.path.join(DATA_DIR, "symbol_performance.csv")
    trades_path = os.path.join(LOG_DIR, "trade_history.csv")

    df_metrics = load_metrics(metrics_path)
    if df_metrics.empty:
        return

    df_trades = load_trades(trades_path)
    if df_trades.empty:
        return

    elite = select_elite_symbols(df_metrics)
    print("🎯 Elite selections from metrics:")
    for ctry, syms in elite.items():
        print(f"  {ctry}: {syms}")

    plot_elite_equity(df_trades, elite)


if __name__ == "__main__":
    main()


