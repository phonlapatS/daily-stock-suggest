import pandas as pd
import numpy as np
import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pattern_stats import PatternStatsManager


# Create dummy stats file
test_stats_path = 'data/test_stats.csv'
test_state_path = 'data/test_stats_state.json'
df_stats = pd.DataFrame([
    {'Symbol': 'TEST', 'Pattern': '+', 'Stats': '10/20', 'Chance': '🟢 UP', 'Prob': '50%', 'avg_return': 0.1},
    {'Symbol': 'TEST', 'Pattern': '-', 'Stats': '5/10', 'Chance': '🔴 DOWN', 'Prob': '50%', 'avg_return': -0.1}
])
df_stats.to_csv(test_stats_path, index=False)

# Create dummy price data (Dates 1-5)
dates = pd.date_range(start='2024-01-01', periods=5)
df_data = pd.DataFrame({
    'close': [100, 101, 102, 100, 103], # Returns: +, +, -, +
}, index=dates)

# Init Manager with TEST path
manager = PatternStatsManager(stats_path=test_stats_path)
print("Initial Stats:")
print(manager.get_stats())

# Manually set state to Day 3 (2024-01-03)
manager.last_update = pd.to_datetime('2024-01-03')
manager.save_state(manager.last_update)

# Run Update with FULL Data (Should only pick up Day 4+)
# Day 1: 100 None
# Day 2: 101 (+1%) -> Pattern + (Outcome: Day 3 +)
# Day 3: 102 (+1%) -> Pattern + (Outcome: Day 4 -)
# Day 4: 100 (-2%) -> Pattern - (Outcome: Day 5 +)
# Day 5: 103 (+3%)

# Patterns Dict (Simulating detection)
patterns = {
    pd.to_datetime('2024-01-02'): '+',
    pd.to_datetime('2024-01-03'): '+',
    pd.to_datetime('2024-01-04'): '-', # New Data
}

# Mock the 'updates' dictionary that would come from the scanner logic
updates_payload = {
    '-': {'up': 1, 'down': 0, 'returns': [0.03]} # Day 4 outcome was UP (+3%), existing prediction was DOWN.
}

print(f"\nPerforming Update from {manager.last_update}...")
# Call the internal commit method directly for testing
manager._commit_updates(updates_payload, symbol='TEST')

# Verify
print("\nUpdated Stats:")
df_updated = pd.read_csv(test_stats_path)
print(df_updated)

# Check Logic
# New data after 2024-01-03 is 2024-01-04.
# Day 4 (2024-01-04): Pattern '-', Next Return (Day 5) is +3% (UP).
# Existing Pattern '-' was 5/10 (Down forecast).
# New outcome is UP (LOSS for Down forecast).
# Win should NOT increase. Total +1.
# Stats should become 5/11.

row = df_updated[df_updated['Pattern'] == '-'].iloc[0]
print(f"\nPattern '-' Stats: {row['Stats']} (Expected 5/11)")

# Cleanup
os.remove(test_stats_path)
os.remove(test_state_path)
