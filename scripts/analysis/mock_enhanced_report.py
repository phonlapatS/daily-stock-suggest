import pandas as pd
import numpy as np
import os
from datetime import datetime

# Path to log file
LOG_FILE = "logs/performance_log.csv"

def generate_mock_report():
    if not os.path.exists(LOG_FILE):
        print("❌ Error: logs/performance_log.csv not found.")
        return

    # Load data
    df = pd.read_csv(LOG_FILE)
    df.columns = df.columns.str.strip()
    
    # Filter only verified forecasts
    df_ver = df[df['actual'] != 'PENDING'].copy()
    if df_ver.empty:
        print("⚠️ No verified forecasts found in log.")
        return

    # Convert types
    df_ver['realized_change'] = pd.to_numeric(df_ver['realized_change'], errors='coerce')
    df_ver['correct'] = pd.to_numeric(df_ver['correct'], errors='coerce')

    # Group by Symbol, then Pattern
    # Note: Threshold in this mock is taken from the most recent record for each symbol
    
    report_data = []
    
    # Sort symbols for consistency
    symbols = sorted(df_ver['symbol'].unique())
    
    print("\n" + "═"*90)
    print("  STRATEGY INSIGHTS: FORWARD TESTING PERFORMANCE (V4.5)")
    print("═"*90)
    print(f"  Last Update : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Data Range  : {df_ver['scan_date'].min()} to {df_ver['scan_date'].max()}")
    print(f"  Total Sample: {len(df_ver)} Verified Forecasts")
    print("─" * 90)
    
    # Header with cleaner spacing
    header = f"  {'Symbol':<10} {'Thresh':>7}   {'Pattern':<10} {'Predict':<8} {'Prob (Stats)':<15} | {'Wins/Total':>11} {'Win%':>7} {'Avg.Win%':>9} {'Avg.Loss%':>9} {'RRR':>6}"
    print(header)
    print("─" * 120)

    for symbol in symbols:
        df_sym = df_ver[df_ver['symbol'] == symbol]
        current_thresh = df_sym.sort_values('scan_date')['threshold'].iloc[-1]
        
        # Group by pattern AND forecast
        groups = df_sym.groupby(['pattern', 'forecast'])
        
        first_row_for_symbol = True
        for (pat, fcast), df_pat in groups:
            total = len(df_pat)
            wins = int(df_pat['correct'].sum())
            win_rate = (wins / total * 100) if total > 0 else 0
            
            # Use average probability and historical sample size (stats)
            raw_prob = df_pat['prob'].mean()
            # Logic-wise cap (realism) - Ensure we don't display > 100% from legacy logs
            avg_prob = min(raw_prob, 100.0)
            
            avg_stats = int(df_pat['stats'].mean()) if 'stats' in df_pat.columns else 0
            prob_stats_str = f"{avg_prob:>5.1f}% ({avg_stats})"
            
            # Stats calculation - Force Win as Positive and Loss as Negative for intuitive reporting
            avg_win_raw = df_pat[df_pat['correct'] == 1]['realized_change'].mean()
            avg_loss_raw = df_pat[df_pat['correct'] == 0]['realized_change'].mean()
            
            # User requirement: Win must be positive, Loss must be negative
            avg_win = abs(avg_win_raw) if not np.isnan(avg_win_raw) else 0
            avg_loss = -abs(avg_loss_raw) if not np.isnan(avg_loss_raw) else 0
            
            avg_win_str = f"{avg_win:>8.2f}%" if avg_win != 0 else f"{' - ':>9}"
            avg_loss_str = f"{avg_loss:>8.2f}%" if avg_loss != 0 else f"{' - ':>9}"
            
            rrr = abs(avg_win / avg_loss) if not np.isnan(avg_win) and not np.isnan(avg_loss) and avg_loss != 0 else 0.0
            rrr_str = f"{rrr:>6.2f}" if rrr > 0 else f"{' - ':>6}"

            s_display = f"{symbol:<10}" if first_row_for_symbol else f"{'':<10}"
            t_display = f"{current_thresh:>6.2f}%" if first_row_for_symbol else f"{'':>7}"
            # Use colored circles for better visual intuition
            p_icon = "🟢" if fcast == 'UP' else "🔴"
            predict_display = f"{p_icon} {fcast:<5}"
            
            row = f"  {s_display:<10} {t_display:<7}   {pat:<10} {predict_display:<8} {prob_stats_str:<15} | {wins:>3}/{total:<7} {win_rate:>6.1f}% {avg_win_str} {avg_loss_str} {rrr_str}"
            print(row)
            
            # Save for CSV
            report_data.append({
                'Symbol': symbol, 'Threshold': current_thresh, 'Pattern': pat,
                'Predict': fcast, 'Confidence_Prob': round(avg_prob, 2),
                'Wins': wins, 'Total': total, 'WinRate': round(win_rate, 2),
                'AvgWin': round(avg_win, 2) if not np.isnan(avg_win) else 0,
                'AvgLoss': round(avg_loss, 2) if not np.isnan(avg_loss) else 0,
                'RRR': round(rrr, 2)
            })
            first_row_for_symbol = False
            
        print("  " + "-" * 115) # Dashed separator per symbol

    # Export to CSV
    csv_file = "logs/strategy_insight_report.csv"
    pd.DataFrame(report_data).to_csv(csv_file, index=False)
    print(f"\n✅ Insight report (V4.5 Final Mock) exported to: {csv_file}")
    print("💡 Tip: You can open the CSV in Excel for professional charting.")

if __name__ == "__main__":
    generate_mock_report()
