#!/usr/bin/env python
"""
split_trade_history_by_market.py
================================

Utility script to split the unified `logs/trade_history.csv` into
per-market files expected by plotting scripts, e.g.:

- logs/trade_history_THAI.csv
- logs/trade_history_US.csv
- logs/trade_history_CHINA.csv
- logs/trade_history_TAIWAN.csv

Usage:
    python scripts/split_trade_history_by_market.py
"""

import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

INPUT_FILE = os.path.join(LOG_DIR, "trade_history.csv")

OUTPUT_FILES = {
    "THAI": os.path.join(LOG_DIR, "trade_history_THAI.csv"),
    "US": os.path.join(LOG_DIR, "trade_history_US.csv"),
    "CHINA": os.path.join(LOG_DIR, "trade_history_CHINA.csv"),
    "TAIWAN": os.path.join(LOG_DIR, "trade_history_TAIWAN.csv"),
}


def main() -> None:
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input trade history not found: {INPUT_FILE}")
        sys.exit(1)

    df = pd.read_csv(INPUT_FILE)
    if df.empty:
        print("⚠️ trade_history.csv is empty – nothing to split.")
        sys.exit(0)

    if "group" not in df.columns:
        print("❌ trade_history.csv has no 'group' column; cannot split by market.")
        sys.exit(1)

    # Simple mapping by group name and exchange keywords
    def classify_market_row(row) -> str:
        # Primary schema (new rows)
        g1 = str(row.get("group", "")).upper()
        ex1 = str(row.get("exchange", "")).upper()

        # Legacy schema (old rows have market info in the last columns)
        g2 = str(row.get("Unnamed: 14", "")).upper()
        ex2 = str(row.get("Unnamed: 13", "")).upper()

        g = f"{g1} {g2}".upper()
        ex = f"{ex1} {ex2}".upper()

        # Thai SET
        if "GROUP_A_THAI" in g or ex in ("SET", "MAI", "TH"):
            return "THAI"

        # US markets
        if "GROUP_B_US" in g or ex in ("NASDAQ", "NYSE", "US", "CME", "COMEX", "NYMEX"):
            return "US"

        # China / HK
        if (
            "GROUP_E_CHINA_ADR" in g
            or "GROUP_F_CHINA_A" in g
            or "GROUP_G_HK_TECH" in g
            or ex in ("HK", "HKEX", "SH", "SZ", "SHSE", "SZSE")
        ):
            return "CHINA"

        # Taiwan
        if "GROUP_H_TAIWAN" in g or ex in ("TW", "TWSE"):
            return "TAIWAN"

        return ""

    df["market"] = df.apply(classify_market_row, axis=1)

    for market, out_path in OUTPUT_FILES.items():
        sub = df[df["market"] == market].copy()
        if sub.empty:
            print(f"⚠️ No trades found for market: {market}")
            continue

        # Drop helper column
        sub = sub.drop(columns=["market"])
        sub.to_csv(out_path, index=False)
        print(f"💾 Saved {len(sub)} trades to {out_path}")

    print("✅ Split complete.")


if __name__ == "__main__":
    main()


