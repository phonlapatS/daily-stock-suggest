import pandas as pd
import sys

def view_streak_profile(csv_path="data/Streak_Profile.csv", symbol_filter=None):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_path}")
        return

    if symbol_filter:
        df = df[df['Symbol'] == symbol_filter.upper()]
        if df.empty:
            print(f"❌ No streak data found for {symbol_filter}")
            return

    print("\n" + "=" * 80)
    print(f"📊 STREAK PROFILE {'(' + symbol_filter + ')' if symbol_filter else ''}")
    print("=" * 80)
    print(f"{'Symbol':<10} {'Type':<6} {'Day':<4} {'Count':>8} {'Cont.':>8} {'Prob Next Day':>15}")
    print("-" * 80)

    for _, row in df.iterrows():
        # Add visual indicator for probability
        survival_prob = row['Next_Day_Prob_Percent']
        reversal_prob = 100.0 - survival_prob
        
        # Determine Dominant Direction (Prediction)
        if survival_prob >= reversal_prob:
            # Prediction: Trend Continues
            direction_str = "🟢 CONT."
            prob_val = survival_prob
        else:
            # Prediction: Trend Reverses
            direction_str = "🔴 REV."
            prob_val = reversal_prob
            
        prob_vis = f"{direction_str} ({prob_val:.1f}%)"

        print(f"{row['Symbol']:<10} {row['Streak_Type']:<6} {row['Day_Count_n']:<4} {row['Reached_Count']:>8} {row['Continued_to_n_plus_1']:>8} {prob_vis:>15}")
    
    print("-" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        view_streak_profile(symbol_filter=symbol)
    else:
        print("Usage: python view_streak.py <SYMBOL>")
        print("Showing first 20 rows because no symbol specified...")
        # Show sample if no arg
        view_streak_profile()
