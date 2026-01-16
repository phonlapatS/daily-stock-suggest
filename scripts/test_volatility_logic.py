
import pandas as pd
import numpy as np
import os
import sys

# Define logic functions
def calc_volatility_v4(close_prices):
    """Old Logic: Simple 20-day Rolling SD"""
    returns = close_prices.pct_change()
    rolling_std = returns.rolling(window=20).std()
    return rolling_std * 2.0  # Threshold was roughly 2 SD in concept

def calc_volatility_hybrid(close_prices):
    """New Logic: Adaptive Hybrid (Max of 20d or 50% of 252d)"""
    returns = close_prices.pct_change()
    
    # 1. Short-Term (20d)
    short_term_vol = returns.rolling(window=20).std()
    
    # 2. Long-Term Floor (252d)
    long_term_vol = returns.rolling(window=252).std()
    floor_vol = long_term_vol * 0.50
    
    # 3. Effective Volatility
    effective_vol = np.maximum(short_term_vol, floor_vol)
    
    # 4. Final Threshold (2.0 SD)
    return effective_vol * 2.0

# Generate Synthetic Data for Testing
# Scenario: Sideways (Low Vol) -> Breakout (High Vol) -> Crash -> Stability
np.random.seed(42)
days = 500
price = 100
prices = []

# 1. Sideways (200 days)
for _ in range(200):
    change = np.random.normal(0, 0.005) # 0.5% daily volatility
    price *= (1 + change)
    prices.append(price)

# 2. Breakout (50 days) - Highly volatile
for _ in range(50):
    change = np.random.normal(0.005, 0.02) # 2% daily volatility, trending up
    price *= (1 + change)
    prices.append(price)

# 3. Stability (250 days) - Return to normal
for _ in range(250):
    change = np.random.normal(0, 0.008) # 0.8% daily
    price *= (1 + change)
    prices.append(price)

df = pd.DataFrame({'close': prices})

# Run Calculations
df['Threshold_V4'] = calc_volatility_v4(df['close'])
df['Threshold_Hybrid'] = calc_volatility_hybrid(df['close'])
df['Returns'] = df['close'].pct_change()

# Compare Results
# Count how many days the return exceeds the threshold (False Positives during sideways?)
v4_breaches = df[abs(df['Returns']) > df['Threshold_V4']]
hybrid_breaches = df[abs(df['Returns']) > df['Threshold_Hybrid']]

print("="*60)
print("VOLATILITY LOGIC COMPARISON TEST")
print("="*60)
print(f"Total Data Points: {len(df)}")
print(f"V4 Breaches (Simple 20d): {len(v4_breaches)} signals")
print(f"Hybrid Breaches (Adaptive): {len(hybrid_breaches)} signals")
print("-" * 60)

# Analyzer specific periods
print("\n--- Period Analysis ---")
print("1. Sideways Phase (Low Vol):")
sideways = df.iloc[50:200]
v4_s = len(sideways[abs(sideways['Returns']) > sideways['Threshold_V4']])
hy_s = len(sideways[abs(sideways['Returns']) > sideways['Threshold_Hybrid']])
print(f"   V4 Signals: {v4_s}")
print(f"   Hybrid Signals: {hy_s} (Should be lower/equal)")

print("\n2. Breakout Phase (High Vol):")
breakout = df.iloc[200:250]
v4_b = len(breakout[abs(breakout['Returns']) > breakout['Threshold_V4']])
hy_b = len(breakout[abs(breakout['Returns']) > breakout['Threshold_Hybrid']])
print(f"   V4 Signals: {v4_b}")
print(f"   Hybrid Signals: {hy_b}")

print("\n3. Stability (After Shock):")
stable = df.iloc[250:]
v4_st = len(stable[abs(stable['Returns']) > stable['Threshold_V4']])
hy_st = len(stable[abs(stable['Returns']) > stable['Threshold_Hybrid']])
print(f"   V4 Signals: {v4_st}")
print(f"   Hybrid Signals: {hy_st}")

# Check Average Threshold Levels
print("\n--- Threshold Levels (Avg) ---")
print(f"V4 Avg Threshold: {df['Threshold_V4'].mean()*100:.2f}%")
print(f"Hybrid Avg Threshold: {df['Threshold_Hybrid'].mean()*100:.2f}%")
print("="*60)
