#!/usr/bin/env python
"""
plot_metrics.py
===============

Visualize results from calculate_metrics.py so you can see each market clearly.

Reads: data/symbol_performance.csv
Outputs: plots/metrics_by_market.png

Usage:
    python scripts/plot_metrics.py
"""

import os

import matplotlib.pyplot as plt
import pandas as pd


def load_metrics(path: str = "data/symbol_performance.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"❌ Metrics file not found: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        print("⚠️ Metrics file is empty.")
        return pd.DataFrame()

    # Backwards compatibility: if AvgWin% / AvgLoss% missing, fill with 0
    if "AvgWin%" not in df.columns:
        df["AvgWin%"] = 0.0
    if "AvgLoss%" not in df.columns:
        df["AvgLoss%"] = 0.0
    if "Count" not in df.columns:
        # Fallback: use Elite_Count if available, otherwise Raw_Count
        df["Count"] = df.get("Elite_Count", df.get("Raw_Count", 0))

    return df


def plot_by_market(df: pd.DataFrame, output_path: str = "plots/metrics_by_market.png") -> None:
    if df.empty:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Markets we care about in order
    market_order = [
        ("TH", "Thai Stocks"),
        ("US", "US Stocks"),
        ("CN", "China ADR"),
        ("TW", "Taiwan"),
        ("GL", "Metals"),
    ]

    # Create up to 5 subplots horizontally (or fewer if markets missing)
    n_markets = sum((df["Country"] == code).any() for code, _ in market_order)
    if n_markets == 0:
        print("⚠️ No markets found in metrics (Country column is empty).")
        return

    fig, axes = plt.subplots(1, n_markets, figsize=(4 * n_markets + 2, 5), squeeze=False)
    ax_list = axes[0]

    idx = 0
    for code, title in market_order:
        sub = df[df["Country"] == code].copy()
        if sub.empty:
            continue

        ax = ax_list[idx]
        idx += 1

        # X-axis: Prob%, Y-axis: RRR, Bubble size: Count
        x = sub["Prob%"]
        y = sub["RR_Ratio"]
        sizes = sub["Count"].clip(lower=5)  # avoid zero
        sizes = (sizes / sizes.max()) * 300  # scale bubbles

        ax.scatter(x, y, s=sizes, alpha=0.6, edgecolor="k")

        # Annotate top few symbols
        top = sub.sort_values(["Prob%", "RR_Ratio"], ascending=[False, False]).head(7)
        for _, row in top.iterrows():
            ax.annotate(
                str(row["symbol"]),
                (row["Prob%"], row["RR_Ratio"]),
                textcoords="offset points",
                xytext=(3, 3),
                fontsize=8,
            )

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Prob%")
        ax.set_ylabel("RRR")
        ax.grid(True, linestyle=":", alpha=0.4)

        # Reference lines for mentor thresholds
        ax.axvline(60, color="orange", linestyle="--", linewidth=1, alpha=0.7)
        ax.axhline(1.5, color="red", linestyle="--", linewidth=1, alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    print(f"✅ Saved metrics plot to: {output_path}")


def main() -> None:
    df = load_metrics()
    if df.empty:
        return

    plot_by_market(df)


if __name__ == "__main__":
    main()


