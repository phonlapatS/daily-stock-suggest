import pandas as pd
import sys
import os

def load_data():
    try:
        stats_df = pd.read_csv("data/Master_Pattern_Stats.csv")
        streak_df = pd.read_csv("data/Streak_Profile.csv")
        return stats_df, streak_df
    except FileNotFoundError:
        print("❌ Error: Data files not found. Please run batch_processor.py first.")
        sys.exit(1)

def print_section_header(title):
    print("\n" + "=" * 80)
    print(f"📄 {title}")
    print("=" * 80)

def view_report(symbol=None):
    stats, streaks = load_data()
    
    if symbol:
        symbol = symbol.upper()
        stats = stats[stats['Symbol'] == symbol]
        streaks = streaks[streaks['Symbol'] == symbol]
        print(f"\n🔍 Generating Full Report for: {symbol}")
    else:
        print("\n⚠️  No symbol specified. Showing top 20 rows for overview.")
        stats = stats.head(20)
        streaks = streaks.head(20)
    
    # ---------------------------------------------------------
    # PART 1: Master Pattern Stats
    # ---------------------------------------------------------
    print_section_header("PART 1: MASTER PATTERN STATS (Tomorrow's Forecast)")
    if stats.empty:
        print("   (No Pattern Data found)")
    else:
        # Columns to display
        cols = ['Symbol','Pattern_Name','Category','Chance','Prob','Stats']
        # Check if columns exist (compatibility)
        display_cols = [c for c in cols if c in stats.columns]
        
        # Formatted Print
        print(f"{'Pattern':<25} {'Category':<10} {'Chance':<10} {'Prob':<6} {'Stats':<15}")
        print("-" * 70)
        for _, row in stats.iterrows():
            print(f"{str(row['Pattern_Name']):<25} {str(row['Category']):<10} {str(row['Chance']):<10} {str(row['Prob']):<6} {str(row['Stats']):<15}")

    # ---------------------------------------------------------
    # PART 2: Streak Profile
    # ---------------------------------------------------------
    print_section_header("PART 2: STREAK PROFILE (Momentum Health)")
    if streaks.empty:
        print("   (No Streak Data found)")
    else:
        print(f"{'Type':<6} {'Day':<4} {'Count':>8} {'Cont.':>8} {'Prediction':>18}")
        print("-" * 70)
        for _, row in streaks.iterrows():
            # Reconstruct Visual Logic (Strict Mode)
            current_streak_type = row['Streak_Type']
            
            # Since we are reading from CSV, we might need to recalculate Prob for display if not raw
            # But the CSV usually has 'Next_Day_Prob_Percent'
            if 'Next_Day_Prob_Percent' in row:
                prob = row['Next_Day_Prob_Percent']
                # Cont vs Rev
                # In Strict Mode: Prob is "Chance of Continuation"
                # If Prob < 50 => Reversal likely
                
                survival_prob = prob
                reversal_prob = 100.0 - survival_prob
                
                if survival_prob >= 50: # Simple threshold for display
                     pred_str = f"🟢 CONT. ({survival_prob:.1f}%)"
                else:
                     pred_str = f"🔴 REV. ({reversal_prob:.1f}%)"
            else:
                pred_str = "N/A"

            print(f"{row['Streak_Type']:<6} {row['Day_Count_n']:<4} {row['Reached_Count']:>8} {row['Continued_to_n_plus_1']:>8} {pred_str:>18}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        view_report(sys.argv[1])
    else:
        print("Usage: python view_report.py [SYMBOL]")
        view_report()
