import pandas as pd
import os

def check_china():
    path = 'logs/trade_history_CHINA.csv'
    if not os.path.exists(path):
        print("No log file found.")
        return

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} trades.")

    # Convert numeric columns
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['forecast'] = df['forecast'].astype(str)
    
    # Calculate PnL
    df['pnl'] = df.apply(lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), axis=1)

    # Group by Symbol
    stats = []
    for sym, group in df.groupby('symbol'):
        total = len(group)
        wins = group[group['pnl'] > 0]
        losses = group[group['pnl'] <= 0]
        
        avg_win = wins['pnl'].mean() if not wins.empty else 0
        avg_loss = abs(losses['pnl'].mean()) if not losses.empty else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        win_rate = (len(wins) / total) * 100
        
        stats.append({
            'symbol': sym,
            'count': total,
            'win_rate': round(win_rate, 2),
            'rrr': round(rrr, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2)
        })
    
    # Sort by Win Rate
    stats_df = pd.DataFrame(stats).sort_values(by='win_rate', ascending=False)
    print(stats_df.to_string(index=False))

if __name__ == "__main__":
    check_china()
