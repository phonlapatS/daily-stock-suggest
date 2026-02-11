"""
plot_fair_comparison.py - Fair Market Comparison (Individual + Combined)
========================================================================
Key Design Decisions for "Fair" Comparison:
1. Use Trustworthy stocks only (from calculate_metrics)
2. Market-appropriate Prob thresholds (TH/US >= 55%, CN/TW >= 50%)
3. Individual plots: All trustworthy stocks per market
4. Combined: Best stock per market, View 1 (time) + View 2 (first 200 trades)
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Market-appropriate probability thresholds
# TH/US have high-probability patterns; CN/TW use lower thresholds
MARKET_FILES = {
    "TH": {"file": "logs/trade_history_THAI.csv", "label": "THAI (SET)", "color": "#2ecc71",
            "trustworthy": ["SUPER","BPP","QH","DOHOME","HANA","LH","RATCH","GUNKUL","TISCO","TTB"],
            "min_prob": 55.0},
    "US": {"file": "logs/trade_history_US.csv", "label": "US (NASDAQ)", "color": "#e74c3c",
            "trustworthy": ["VRTX","ODFL","CHTR","ENPH","TEAM"],
            "min_prob": 55.0},
    "CN": {"file": "logs/trade_history_CHINA.csv", "label": "CHINA/HK (HKEX)", "color": "#3498db",
            "trustworthy": ["1810"],
            "min_prob": 0.0},  # All trades (filtered by calculate_metrics already)
    "TW": {"file": "logs/trade_history_TAIWAN.csv", "label": "TAIWAN (TWSE)", "color": "#9b59b6",
            "trustworthy": ["2395"],
            "min_prob": 50.0}
}

SYMBOL_NAMES = {}
for gk, gd in config.ASSET_GROUPS.items():
    for a in gd.get('assets', []):
        SYMBOL_NAMES[str(a['symbol'])] = a.get('name', a['symbol'])

all_data = {}

print("=" * 60)
print("STEP 1: DATA ANALYSIS")
print("=" * 60)

for mc, cfg in MARKET_FILES.items():
    fp = os.path.join(BASE_DIR, cfg['file'])
    if not os.path.exists(fp):
        continue
    df = pd.read_csv(fp)
    df['date'] = pd.to_datetime(df['date'])
    df['symbol'] = df['symbol'].astype(str)
    
    # Filter: trustworthy symbols + market-appropriate prob threshold
    dft = df[(df['symbol'].isin(cfg['trustworthy'])) & (df['prob'] >= cfg['min_prob'])].copy()
    
    wr = dft.correct.mean()*100 if len(dft) > 0 else 0
    print(f"  {cfg['label']}: Raw={len(df):,} | Filtered={len(dft):,} (Prob>={cfg['min_prob']}%) | WR={wr:.1f}%")
    
    # Per-symbol breakdown
    for sym in sorted(dft.symbol.unique()):
        sdf = dft[dft.symbol == sym]
        name = SYMBOL_NAMES.get(sym, sym)
        print(f"    {name} ({sym}): N={len(sdf)}, WR={sdf.correct.mean()*100:.1f}%, Cum={sdf.trader_return.sum():.1f}%")
    
    all_data[mc] = {'raw': df, 'filtered': dft, 'cfg': cfg}

# =====================================================================
# STEP 2: Individual Market Plots (4 subplots)
# =====================================================================
print(f"\n{'='*60}\nSTEP 2: INDIVIDUAL MARKET PLOTS\n{'='*60}")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, (mc, d) in enumerate(all_data.items()):
    ax = axes[idx]
    cfg = d['cfg']
    dft = d['filtered']
    
    if len(dft) == 0:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=14)
        ax.set_title(cfg['label'])
        continue
    
    for sym in sorted(dft.symbol.unique()):
        sdf = dft[dft.symbol == sym].sort_values('date').copy()
        sdf['cum'] = sdf['trader_return'].cumsum()
        name = SYMBOL_NAMES.get(sym, sym)
        ax.plot(sdf['date'], sdf['cum'], linewidth=1.2, alpha=0.85, 
                label=f"{name} (N={len(sdf)}, WR={sdf.correct.mean()*100:.0f}%)")
    
    # Portfolio avg line
    port = dft.groupby('date')['trader_return'].mean().reset_index().sort_values('date')
    port['cum'] = port['trader_return'].cumsum()
    ax.plot(port['date'], port['cum'], color='black', linewidth=2.5, linestyle='--', 
            label="Portfolio Avg", alpha=0.7)
    
    ax.axhline(0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.set_title(f"{cfg['label']} — Trustworthy Stocks", fontsize=11, fontweight='bold')
    ax.set_ylabel("Cumulative Return (%)")
    ax.legend(loc='upper left', fontsize=5.5, ncol=2)
    ax.grid(True, alpha=0.15)

plt.suptitle("PredictPlus V4.5: Individual Market Performance (Trustworthy Only)", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])
p1 = os.path.join(OUT_DIR, "individual_market_performance.png")
plt.savefig(p1, dpi=150)
plt.close()
print(f"  ✅ Saved: {p1}")

# =====================================================================
# STEP 3: Fair Combined Comparison
# =====================================================================
print(f"\n{'='*60}\nSTEP 3: FAIR COMBINED COMPARISON\n{'='*60}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

best = {}
for mc, d in all_data.items():
    cfg = d['cfg']
    dft = d['filtered']
    if len(dft) == 0:
        continue
    
    # Pick stock with highest WR among trustworthy
    best_sym, best_wr = None, -1
    for sym in dft.symbol.unique():
        wr = dft[dft.symbol == sym].correct.mean()
        if wr > best_wr:
            best_wr = wr
            best_sym = sym
    
    sdf = dft[dft.symbol == best_sym].sort_values('date').copy()
    name = SYMBOL_NAMES.get(best_sym, best_sym)
    best[mc] = {'sym': best_sym, 'name': name, 'data': sdf, 'color': cfg['color'], 'label': cfg['label']}
    print(f"  {mc}: {name} — N={len(sdf)}, WR={sdf.correct.mean()*100:.1f}%, Cum={sdf.trader_return.sum():.1f}%")

# View 1: Time-Based (full history)
for mc, info in best.items():
    sdf = info['data'].copy()
    sdf['cum'] = sdf['trader_return'].cumsum()
    lbl = f"{info['name']} | {info['label']} (N={len(sdf)})"
    ax1.plot(sdf['date'], sdf['cum'], color=info['color'], linewidth=1.8, label=lbl)
    ax1.annotate(f" {info['name']}: {sdf['cum'].iloc[-1]:.0f}%",
                 xy=(sdf['date'].iloc[-1], sdf['cum'].iloc[-1]),
                 fontsize=9, fontweight='bold', color=info['color'])

ax1.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax1.set_title("View 1: Growth over Time (Best Trustworthy Stock per Market)", fontsize=12, fontweight='bold')
ax1.set_ylabel("Cumulative Return (%)")
ax1.legend(loc='upper left', fontsize='small')
ax1.grid(True, alpha=0.2)

# View 2: Fair Trade-Count Based (cap at N trades)
# Use the smallest N among all markets for TRUE fairness
min_n = min(len(info['data']) for info in best.values())
CAP = min(200, min_n)
print(f"\n  Fair cap for View 2: {CAP} trades (smallest market has {min_n})")

for mc, info in best.items():
    sdf = info['data'].head(CAP).copy().reset_index(drop=True)
    sdf['cum'] = sdf['trader_return'].cumsum()
    lbl = f"{info['name']} | {info['label']}"
    ax2.plot(sdf.index, sdf['cum'], color=info['color'], linewidth=1.8, label=lbl)
    ax2.annotate(f" {info['name']}: {sdf['cum'].iloc[-1]:.0f}%",
                 xy=(sdf.index[-1], sdf['cum'].iloc[-1]),
                 fontsize=9, fontweight='bold', color=info['color'])

ax2.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax2.set_title(f"View 2: First {CAP} Trades — Fair Head-to-Head Comparison", fontsize=12, fontweight='bold')
ax2.set_xlabel("Trade Number")
ax2.set_ylabel("Cumulative Return (%)")
ax2.legend(loc='upper left', fontsize='small')
ax2.grid(True, alpha=0.2)

plt.suptitle("PredictPlus V4.5: Fair Market Comparison (Best Stock per Market)", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])
p2 = os.path.join(OUT_DIR, "fair_market_comparison.png")
plt.savefig(p2, dpi=150)
plt.close()
print(f"  ✅ Saved: {p2}")

print(f"\n✅ DONE! All plots saved to: {OUT_DIR}")
