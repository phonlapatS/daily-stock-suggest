"""
Test Hybrid Pattern Display Logic
===================================
Simulates various market scenarios to verify pattern detection works correctly.
"""
import numpy as np
import pandas as pd
from scipy.stats import zscore

def test_pattern_logic():
    print("=" * 80)
    print("HYBRID PATTERN DISPLAY TEST")
    print("=" * 80)
    
    # Scenario 1: Fresh Breakout from Quiet
    print("\n🧪 Test 1: Fresh Breakout (should show: . → +)")
    returns = [0.001, 0.002, -0.001, 0.03]  # Last day breaks +2SD
    result = simulate_pattern(returns, threshold=0.015)
    print(f"   Result: '{result}'")
    print(f"   Expected: '.→+' or '+' (fresh signal)")
    
    # Scenario 2: Extended Rally
    print("\n🧪 Test 2: Extended Rally (should show: +++++ or similar)")
    returns = [0.03, 0.025, 0.03, 0.028, 0.03]  # 5-day rally
    result = simulate_pattern(returns, threshold=0.015)
    print(f"   Result: '{result}'")
    print(f"   Expected: '+++++' (overbought warning)")
    
    # Scenario 3: Reversal from Crash
    print("\n🧪 Test 3: Reversal (should show: --- → +)")
    returns = [-0.03, -0.025, -0.03, 0.03]  # Crash then bounce
    result = simulate_pattern(returns, threshold=0.015)
    print(f"   Result: '{result}'")
    print(f"   Expected: '---→+' (reversal signal)")
    
    # Scenario 4: Quiet Market
    print("\n🧪 Test 4: Quiet (should show: .)")
    returns = [0.001, 0.002, -0.001, 0.002]  # All within range
    result = simulate_pattern(returns, threshold=0.015)
    print(f"   Result: '{result}'")
    print(f"   Expected: '.' (no pattern)")
    
    # Scenario 5: Stabilization after Crash
    print("\n🧪 Test 5: Stabilization (should show: --- → .)")
    returns = [-0.03, -0.025, -0.03, 0.002]  # Crash then stabilize
    result = simulate_pattern(returns, threshold=0.015)
    print(f"   Result: '{result}'")
    print(f"   Expected: '---→.' (potential floor)")
    
    print("\n" + "=" * 80)
    print("✅ Visual Inspection Complete - Check results above")
    print("=" * 80)

def simulate_pattern(returns_list, threshold):
    """Simulate the hybrid pattern logic"""
    returns = np.array(returns_list)
    thresholds = np.full(len(returns), threshold)
    
    if len(returns) < 2:
        return "."
    
    # Today's state
    today_ret = returns[-1]
    today_thresh = thresholds[-1] * 2.0
    
    if today_ret > today_thresh:
        today_state = '+'
    elif today_ret < -today_thresh:
        today_state = '-'
    else:
        today_state = '.'
    
    # Count current streak
    current_streak = today_state
    if today_state != '.':
        for i in range(2, len(returns) + 1):
            if i > len(returns):
                break
            past_ret = returns[-i]
            past_thresh = thresholds[-i] * 2.0
            
            if today_state == '+' and past_ret > past_thresh:
                current_streak = '+' + current_streak
            elif today_state == '-' and past_ret < -past_thresh:
                current_streak = '-' + current_streak
            else:
                break
    
    # Check previous streak
    prev_streak = ""
    start_idx = len(current_streak) if current_streak != '.' else 1
    
    if start_idx < len(returns):
        prev_ret = returns[-(start_idx + 1)]
        prev_thresh = thresholds[-(start_idx + 1)] * 2.0
        
        if prev_ret > prev_thresh:
            prev_state = '+'
        elif prev_ret < -prev_thresh:
            prev_state = '-'
        else:
            prev_state = '.'
        
        if prev_state != '.':
            prev_streak = prev_state
            for i in range(start_idx + 2, min(start_idx + 6, len(returns) + 1)):
                if i > len(returns):
                    break
                past_ret = returns[-i]
                past_thresh = thresholds[-i] * 2.0
                
                if prev_state == '+' and past_ret > past_thresh:
                    prev_streak = '+' + prev_streak
                elif prev_state == '-' and past_ret < -past_thresh:
                    prev_streak = '-' + prev_streak
                else:
                    break
    
    # Display logic
    if prev_streak and prev_streak[0] != current_streak[0]:
        return f"{prev_streak[:3]}→{current_streak[:3]}"
    else:
        return current_streak[:5] if current_streak != '.' else '.'

if __name__ == "__main__":
    test_pattern_logic()
