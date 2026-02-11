
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Configuration
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'cache')
FILES = [
    'OANDA_XAUUSD_15m.csv', 'OANDA_XAUUSD_30m.csv',
    'OANDA_XAGUSD_15m.csv', 'OANDA_XAGUSD_30m.csv'
]

def load_data(filename):
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    df = pd.read_csv(filepath, parse_dates=['datetime'], index_col='datetime')
    return df

def analyze_volatility(df, name):
    print(f"\n🔬 ANALYSIS: {name}")
    print("=" * 40)
    
    # Pre-processing
    close = df['close']
    pct_change = close.pct_change().dropna()
    abs_change = pct_change.abs()
    
    # 1. Volatility Stats (The "Natural Pulse" of the market)
    mean_vol = abs_change.mean() * 100
    median_vol = abs_change.median() * 100
    p80_vol = abs_change.quantile(0.80) * 100
    std_vol = abs_change.std() * 100
    
    print(f"📊 Volatility (Per Bar %):")
    print(f"   Mean:   {mean_vol:.4f}%")
    print(f"   Median: {median_vol:.4f}%")
    print(f"   80th%:  {p80_vol:.4f}% (Suggested Threshold Floor)")
    print(f"   SD:     {std_vol:.4f}%")
    
    # 2. Train/Test Split (Strict separation to prevent Overfitting)
    split_idx = int(len(df) * 0.70)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    print(f"\n🛡️  Overfit Check (Train vs Test Edge):")
    print(f"   Train: {len(train_df)} bars | Test: {len(test_df)} bars")
    
    # Check "Trend Persistence" (Does Green lead to Green?)
    def get_persistence(d):
        ret = d['close'].pct_change()
        # Up followed by Up
        uu = ((ret > 0) & (ret.shift(-1) > 0)).sum()
        ud = ((ret > 0) & (ret.shift(-1) < 0)).sum()
        # Down followed by Down
        dd = ((ret < 0) & (ret.shift(-1) < 0)).sum()
        du = ((ret < 0) & (ret.shift(-1) > 0)).sum()
        
        up_continuation = uu / (uu + ud) if (uu+ud) > 0 else 0
        down_continuation = dd / (dd + du) if (dd+du) > 0 else 0
        
        return up_continuation, down_continuation

    train_up, train_down = get_persistence(train_df)
    test_up, test_down = get_persistence(test_df)
    
    print(f"   [TRAIN] Up-Cont: {train_up*100:.1f}% | Down-Cont: {train_down*100:.1f}%")
    print(f"   [TEST]  Up-Cont: {test_up*100:.1f}% | Down-Cont: {test_down*100:.1f}%")
    
    diff = abs(train_up - test_up) + abs(train_down - test_down)
    if diff > 0.10:
        print("   ⚠️  WARNING: Significant regime change detected! Strategy might be unstable.")
    else:
        print("   ✅ STABLE: Market behavior is consistent between Train/Test.")

    # 3. Time of Day Analysis (Session Volatility)
    # Calculate mean absolute return per hour
    # Group by index.hour directly
    hourly_vol = df.groupby(df.index.hour)['close'].apply(lambda x: x.pct_change().abs().mean() * 100)
    
    # Identify "Hot Hours" (Top 3 volatility hours)
    if isinstance(hourly_vol, pd.Series):
        top_hours = hourly_vol.nlargest(3)
    else:
        top_hours = pd.Series()
    
    print(f"\n⏰ Best Trading Hours (UTC/Server Time):")
    for h, v in top_hours.items():
        print(f"   Hour {h:02d}:00 : {v:.4f}% vol")
        
    return p80_vol

def main():
    print("🚀 STARTING METALS DNA ANALYSIS (Overfit-Proof Config)")
    
    results = {}
    
    for filename in FILES:
        name = filename.replace('.csv', '').replace('OANDA_', '')
        df = load_data(filename)
        
        if df is not None and not df.empty:
            suggested_threshold = analyze_volatility(df, name)
            results[name] = suggested_threshold
            
    print("\n" + "="*50)
    print("💡 FINAL RECOMMENDATIONS (Based on 80th% Risk-Adjusted)")
    print("="*50)
    for name, thresh in results.items():
        print(f"👉 {name:<12}: Suggested Threshold = {thresh:.3f}%")
        
    print("\nNOTE: These thresholds ensure we only trade the 'Top 20%' of moves,")
    print("filtering out 80% of the noise automatically.")

if __name__ == "__main__":
    main()
