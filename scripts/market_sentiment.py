import pandas as pd
import sys
import os

def analyze_sentiment():
    file_path = 'data/pattern_results.csv'
    
    if not os.path.exists(file_path):
        print("❌ Data not found. Please run 'python3 main.py' first.")
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    if df.empty:
        print("❌ No signals found in data.")
        return

    # Filter only relevant signals (Optional: Filter by Prob > 50%)
    # df = df[df['bull_prob'] > 50] # Example

    total = len(df)
    
    # Simple logic: If avg_return > 0 -> UP, else DOWN
    # Or use strict probability
    up_count = len(df[df['avg_return'] > 0])
    down_count = len(df[df['avg_return'] < 0])
    sideways = total - up_count - down_count

    percent_up = (up_count / total) * 100
    percent_down = (down_count / total) * 100

    print("\n🌍 GLOBAL MARKET SENTIMENT (Tomorrow Forecast)")
    print("==================================================")
    print(f"📡 Total Signals Scanned: {total}")
    print(f"🟢 Bullish (UP):    {up_count} ({percent_up:.1f}%)")
    print(f"🔴 Bearish (DOWN):  {down_count} ({percent_down:.1f}%)")
    
    sentiment_score = percent_up - percent_down
    
    print("\n🧭 DASHBOARD INDICATOR:")
    if sentiment_score > 20:
        print("   🚀 STRONG BULLISH (ตลาดกระทิงดุ)")
    elif sentiment_score > 5:
        print("   📈 MILD BULLISH (แนวโน้มขาขึ้น)")
    elif sentiment_score < -20:
        print("   🩸 STRONG BEARISH (ตลาดเลือดสาด)")
    elif sentiment_score < -5:
        print("   📉 MILD BEARISH (แนวโน้มขาลง)")
    else:
        print("   ⚖️ NEUTRAL / MIXED (ตลาดเลือกทาง/ไซด์เวย์)")
    print("==================================================")

    # Breakdown by Group (if 'group' column exists)
    if 'group' in df.columns:
        print("\n📂 BREAKDOWN BY SECTOR:")
        groups = df['group'].unique()
        for g in groups:
            gdf = df[df['group'] == g]
            g_up = len(gdf[gdf['avg_return'] > 0])
            g_total = len(gdf)
            if g_total > 0:
                g_pct = (g_up / g_total) * 100
                bar = "🟩" * int(g_pct // 10) + "🟥" * (10 - int(g_pct // 10))
                print(f"   {g:<20} : {bar} {g_pct:.0f}% Bullish ({g_up}/{g_total})")

if __name__ == "__main__":
    analyze_sentiment()
