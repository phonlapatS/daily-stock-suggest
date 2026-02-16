
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import sys

# ตั้งค่าให้กราฟเหมือนเดิมทุกครั้ง
np.random.seed(42)
random.seed(42)

# ==================== ข้อมูล (Data) ====================
# US Market
us_data = {
    'VRTX': [90, 73.3, 1.35, 1.05],   # [Count, WinRate, AvgWin, AvgLoss]
    'ODFL': [80, 62.5, 2.22, 1.47],
    'CHTR': [94, 61.7, 1.70, 1.38],
    'ENPH': [98, 57.1, 3.60, 2.69],
    'TEAM': [102, 56.9, 3.62, 2.44]
}
# China Market
cn_data = { 'XIAOMI': [72, 59.7, 2.28, 1.44] }
# Taiwan Market
tw_data = { 'ADVANTECH': [512, 58.8, 1.24, 0.98] }

markets = [
    ("US Market (NASDAQ)", us_data, 'tab:blue'),
    ("China & HK Market (HKEX)", cn_data, 'tab:red'),
    ("Taiwan Market (TWSE)", tw_data, 'tab:green')
]

# ==================== คำนวณและวาดกราฟ ====================
fig, axes = plt.subplots(3, 1, figsize=(12, 18))
plt.subplots_adjust(hspace=0.4)

def simulate_equity(count, win_rate, avg_win, avg_loss):
    n_wins = int(count * (win_rate/100))
    n_losses = count - n_wins
    outcomes = [avg_win]*n_wins + [-avg_loss]*n_losses
    random.shuffle(outcomes)
    return np.insert(np.cumsum(outcomes), 0, 0)

# ตั้งค่าฟอนต์ให้อ่านภาษาไทยได้ (สำหรับ Windows)
plt.rcParams['font.family'] = 'Tahoma'

for i, (mkt_name, data, color_theme) in enumerate(markets):
    ax = axes[i]
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5) # เส้นทุน
    
    max_x = 0
    for stock, stats in data.items():
        equity = simulate_equity(*stats)
        ax.plot(equity, label=f"{stock} (Win {stats[1]}%)", linewidth=2)
        max_x = max(max_x, len(equity))
    
    ax.set_title(f"Market: {mkt_name}", fontsize=14, fontweight='bold', color='darkblue')
    # Try multiple fonts for Thai support on Windows
    thai_font = "Tahoma" if "win" in sys.platform else "DejaVu Sans"
    ax.set_ylabel("กำไรสะสม (%)", fontname=thai_font)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

plt.xlabel("Number of Trades")

# Output to artifacts directory as requested
output_path = r'C:\Users\manda\.gemini\antigravity\brain\a4ef2fa5-d372-4c88-a413-c56fa035f128\simulated_equity_curves.png'
plt.savefig(output_path, bbox_inches='tight', dpi=100)
print(f"✅ Image saved to: {output_path}")
plt.close()
