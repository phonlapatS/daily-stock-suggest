import pandas as pd

def verify():
    # Load Data
    try:
        master = pd.read_csv('data/Master_Pattern_Stats.csv')
        streak = pd.read_csv('data/Streak_Profile.csv')
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    print(f"\n🧪 Consistency Check (Master Stats vs Streak Profile)")
    print("=" * 80)
    print(f"{'Symbol':<10} {'Pattern(+) Dir':<15} {'Streak(UP-1) Survival':<20} {'Implied Dir':<15} {'Match?'}")
    print("-" * 80)

    # Check top 10 stocks
    symbols = master['Symbol'].unique()[:10]
    
    match_count = 0
    total_checked = 0

    for sym in symbols:
        # Get Master Stats for Pattern '+' (1 Day Up)
        m_row = master[(master['Symbol'] == sym) & (master['Pattern'] == '+')]
        if m_row.empty: continue
        
        master_chance = m_row.iloc[0]['Chance'] # "🟢 UP" or "🔴 DOWN"
        
        # Get Streak Profile for Streak Type 'UP', Day 1
        s_row = streak[(streak['Symbol'] == sym) & 
                       (streak['Streak_Type'] == 'UP') & 
                       (streak['Day_Count_n'] == 1)]
        if s_row.empty: continue

        survival_prob = s_row.iloc[0]['Next_Day_Prob_Percent']
        
        # Determine Implied Direction from Streak
        # If Survival > 50% => UP (Continue)
        # If Survival < 50% => DOWN (Reverse)
        if survival_prob >= 50:
            implied_dir = "🟢 UP"
        else:
            implied_dir = "🔴 DOWN"

        # Compare
        is_match = (master_chance == implied_dir)
        match_str = "✅ YES" if is_match else "❌ NO"
        
        if is_match: match_count += 1
        total_checked += 1

        print(f"{sym:<10} {master_chance:<15} {survival_prob:>18.1f}% {implied_dir:<15} {match_str}")

    print("-" * 80)
    print(f"Total Matches: {match_count}/{total_checked}")

if __name__ == "__main__":
    verify()
