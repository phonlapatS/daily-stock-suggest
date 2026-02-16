"""
scripts/forward_testing_report.py
=================================
Forward Testing Report (Human-friendly)

What it does:
- Reads forward-test log from `logs/performance_log.csv` (created/managed by `core/performance.py`)
- Optionally verifies PENDING rows (pulls latest close from TradingView)
- Prints a clear summary + top winners/losers

Usage:
  python scripts/forward_testing_report.py
  python scripts/forward_testing_report.py --verify
  python scripts/forward_testing_report.py --days 30
  python scripts/forward_testing_report.py --verify --days 60 --export data/forward_report.csv
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta

import pandas as pd

# Add project root to sys.path so `core.*` imports work when running from /scripts
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.performance import LOG_FILE, verify_forecast


def _load_log() -> pd.DataFrame:
    if not os.path.exists(LOG_FILE):
        raise FileNotFoundError(f"Forward log not found: {LOG_FILE}")
    df = pd.read_csv(LOG_FILE)
    if df.empty:
        return df
    # Normalize types (best-effort)
    for c in ("scan_date", "target_date"):
        if c in df.columns:
            df[c] = df[c].astype(str)
    for c in ("prob", "stats", "price_at_scan", "price_actual", "correct"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _filter_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    if df.empty:
        return df
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    if "scan_date" not in df.columns:
        return df
    return df[df["scan_date"] >= cutoff].copy()


def _summary_table(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total": 0,
            "verified": 0,
            "pending": 0,
            "correct": 0,
            "accuracy": 0.0,
        }

    pending = df[df["actual"] == "PENDING"] if "actual" in df.columns else pd.DataFrame()
    verified = df[df["actual"] != "PENDING"] if "actual" in df.columns else df
    verified = verified[verified["correct"].notna()] if "correct" in verified.columns else verified

    total_verified = len(verified)
    correct = int(verified["correct"].sum()) if (total_verified and "correct" in verified.columns) else 0
    accuracy = (correct / total_verified * 100.0) if total_verified else 0.0

    return {
        "total": len(df),
        "verified": total_verified,
        "pending": len(pending),
        "correct": correct,
        "accuracy": round(accuracy, 1),
    }


def _print_report(df: pd.DataFrame, days: int) -> None:
    s = _summary_table(df)

    print("=" * 80)
    print("FORWARD TESTING REPORT")
    print("=" * 80)
    print(f"Log file: {LOG_FILE}")
    print(f"Window: last {days} day(s)")
    print("-" * 80)
    print(f"Total rows:    {s['total']}")
    print(f"Verified rows: {s['verified']}")
    print(f"Pending rows:  {s['pending']}")
    if s["verified"] > 0:
        print(f"Accuracy:      {s['accuracy']}%  ({s['correct']}/{s['verified']})")
    else:
        print("Accuracy:      n/a (no verified rows yet)")

    if df.empty:
        print("-" * 80)
        print("No data.")
        print("=" * 80)
        return

    if "actual" not in df.columns or "correct" not in df.columns:
        print("-" * 80)
        print("Log columns missing; cannot compute forward results.")
        print("=" * 80)
        return

    verified = df[(df["actual"] != "PENDING") & (df["correct"].notna())].copy()
    if verified.empty:
        print("-" * 80)
        print("No verified rows in selected window yet.")
        print("=" * 80)
        return

    # By market/exchange
    if "exchange" in verified.columns:
        by_ex = (
            verified.groupby("exchange")["correct"]
            .agg(["count", "sum"])
            .rename(columns={"count": "n", "sum": "correct"})
            .reset_index()
        )
        by_ex["accuracy"] = (by_ex["correct"] / by_ex["n"] * 100.0).round(1)
        by_ex = by_ex.sort_values(["n", "accuracy"], ascending=[False, False])

        print("\nBy Exchange:")
        print(by_ex.to_string(index=False))

    # By direction
    if "forecast" in verified.columns:
        by_dir = (
            verified.groupby("forecast")["correct"]
            .agg(["count", "sum"])
            .rename(columns={"count": "n", "sum": "correct"})
            .reset_index()
        )
        by_dir["accuracy"] = (by_dir["correct"] / by_dir["n"] * 100.0).round(1)
        print("\nBy Forecast Direction:")
        print(by_dir.to_string(index=False))

    # Biggest moves
    if "pnl_pct" in verified.columns:
        pass  # Not in this log format (kept for compatibility)
    if "price_actual" in verified.columns and "price_at_scan" in verified.columns:
        verified["move_pct"] = (verified["price_actual"] - verified["price_at_scan"]) / verified["price_at_scan"] * 100.0
        top = verified.sort_values("move_pct", ascending=False).head(10)[
            ["scan_date", "symbol", "exchange", "forecast", "actual", "move_pct", "prob", "stats", "pattern", "correct"]
        ]
        bot = verified.sort_values("move_pct", ascending=True).head(10)[
            ["scan_date", "symbol", "exchange", "forecast", "actual", "move_pct", "prob", "stats", "pattern", "correct"]
        ]
        print("\nTop 10 Move% (Actual):")
        print(top.to_string(index=False, formatters={"move_pct": "{:.2f}%".format}))
        print("\nBottom 10 Move% (Actual):")
        print(bot.to_string(index=False, formatters={"move_pct": "{:.2f}%".format}))

    print("=" * 80)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="Verify any PENDING rows before reporting (requires TradingView access).")
    ap.add_argument("--days", type=int, default=30, help="Report window size in days (default: 30).")
    ap.add_argument("--export", type=str, default="", help="Optional CSV export path for the filtered window.")
    args = ap.parse_args()

    if args.verify:
        print("Running verify_forecast() ...")
        verify_forecast(tv=None)

    df = _load_log()
    dfw = _filter_days(df, args.days)

    if args.export:
        os.makedirs(os.path.dirname(args.export) or ".", exist_ok=True)
        dfw.to_csv(args.export, index=False, encoding="utf-8-sig")
        print(f"Exported window to: {args.export}")

    _print_report(dfw, args.days)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


