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
        stats = stats[stats['Symbol'].str.upper() == symbol]
        streaks = streaks[streaks['Symbol'].str.upper() == symbol]
        print(f"\n🔍 Generating Full Report for: {symbol}")
    else:
        print("\n⚠️  No symbol specified. Showing top 20 rows for overview.")
        stats = stats.head(20)
        streaks = streaks.head(20)
    
    # ---------------------------------------------------------
    # PART 1: Master Pattern Stats
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # PART 1: Master Pattern Stats
    # ---------------------------------------------------------
    
    # Prepare Threshold Info
    threshold_info = ""
    if not stats.empty and 'Threshold' in stats.columns:
        threshold_val = stats.iloc[0]['Threshold']
        threshold_info = f" [Threshold: {threshold_val}]"
        
    print_section_header(f"PART 1: MASTER PATTERN STATS (Tomorrow's Forecast){threshold_info}")
    
    if stats.empty:
        print("   (No Pattern Data found)")
    else:
        print(f"{'Threshold':<12} {'Pattern':<10} {'Category':<10} {'Chance':<10} {'Prob':<6} {'Stats':<15} {'Avg_Ret':>8}")
        print("-" * 85)
        for _, row in stats.iterrows():
            avg_ret = row.get('avg_return', 0.0)
            avg_ret_str = f"{avg_ret:+.2f}%"
            threshold_val = str(row.get('Threshold', 'N/A'))
            print(f"{threshold_val:<12} {str(row['Pattern']):<10} {str(row['Category']):<10} {str(row['Chance']):<10} {str(row['Prob']):<6} {str(row['Stats']):<15} {avg_ret_str:>8}")

    # ---------------------------------------------------------
    # PART 2: Streak Profile
    # ---------------------------------------------------------
    print_section_header("PART 2: STREAK PROFILE (Momentum)")
    if streaks.empty:
        print("   (No Streak Data found)")
    else:
        print(f"{'Type':<6} {'Day':<4} {'Stats':>12} {'Prob':>18} {'Avg_Ints':>10}")
        print("-" * 80)
        for _, row in streaks.iterrows():
            if 'Next_Day_Prob_Percent' in row:
                prob = row['Next_Day_Prob_Percent']
                survival_prob = prob
                reversal_prob = 100.0 - survival_prob
                
                if survival_prob >= 50:
                     pred_str = f"🟢 CONT. ({survival_prob:.1f}%)"
                else:
                     pred_str = f"🔴 REV. ({reversal_prob:.1f}%)"
            else:
                pred_str = "N/A"
            
            avg_int = row.get('Avg_Intensity', 0.0)
            avg_int_str = f"{avg_int:+.2f}%"
            
            # Create stats string showing dominant side (like Master Stats)
            reached = row['Reached_Count']
            continued = row['Continued_to_n_plus_1']
            reversed_count = reached - continued
            
            # Show the dominant count (matching Prob logic)
            if survival_prob >= 50:
                # CONT is dominant
                stats_str = f"{continued}/{reached}"
            else:
                # REV is dominant
                stats_str = f"{reversed_count}/{reached}"

            print(f"{row['Streak_Type']:<6} {row['Day_Count_n']:<4} {stats_str:>12} {pred_str:>18} {avg_int_str:>10}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == '--all' or arg == '-a':
            # Load data once to get symbols
            stats, _ = load_data()
            symbols = stats['Symbol'].unique()
            print(f"🚀 Generating Reports for ALL {len(symbols)} Symbols...\n")
            
            for sym in symbols:
                view_report(sym)
                print("\n" + "#" * 80 + "\n")
        else:
            view_report(sys.argv[1])
    else:
        print("Usage: python view_report.py [SYMBOL] or [--all]")
        view_report()
