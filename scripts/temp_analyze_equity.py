import pandas as pd
import numpy as np

# Load Taiwan data
df = pd.read_csv('logs/trade_history_TAIWAN.csv', on_bad_lines='skip')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce').fillna(0)
df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)

print('='*70)
print('TAIWAN TRADE HISTORY - Deep Dive')
print('='*70)

print(f'\nTotal trades: {len(df):,}')
print(f'Date range: {df.date.min()} to {df.date.max()}')
print(f'Unique symbols: {df.symbol.nunique()}')
print(f'Unique dates: {df.date.dt.date.nunique()}')

# Basic stats
print(f'\n--- Return Stats ---')
print(f'Mean trader_return: {df.trader_return.mean():.4f}%')
print(f'Median trader_return: {df.trader_return.median():.4f}%')
print(f'Std: {df.trader_return.std():.4f}%')

# Win/Loss
wins = df[df['trader_return'] > 0]
losses = df[df['trader_return'] <= 0]
print(f'\n--- Win/Loss ---')
print(f'Wins: {len(wins):,} ({len(wins)/len(df)*100:.1f}%)')
print(f'Losses: {len(losses):,} ({len(losses)/len(df)*100:.1f}%)')
print(f'Avg Win: +{wins.trader_return.mean():.4f}%')
print(f'Avg Loss: {losses.trader_return.mean():.4f}%')
rrr = abs(wins.trader_return.mean() / losses.trader_return.mean()) if losses.trader_return.mean() != 0 else 0
print(f'RRR: {rrr:.4f}')

# Trades per day
daily_count = df.groupby(df['date'].dt.date).size()
print(f'\n--- Trades per Day ---')
print(f'Avg trades/day: {daily_count.mean():.1f}')
print(f'Max trades/day: {daily_count.max()}')
print(f'Total trading days: {len(daily_count):,}')

# Daily avg return
daily_avg = df.groupby(df['date'].dt.date)['trader_return'].mean()
print(f'\n--- Daily Avg Return (Equity Basis) ---')
print(f'Mean daily avg return: {daily_avg.mean():.4f}%')
print(f'Positive days: {(daily_avg > 0).sum()} ({(daily_avg > 0).mean()*100:.1f}%)')
print(f'Negative days: {(daily_avg <= 0).sum()} ({(daily_avg <= 0).mean()*100:.1f}%)')

# Compound effect
equity = (1 + daily_avg / 100).cumprod()
print(f'\nFinal COMPOUNDED equity: {equity.iloc[-1]*100:.1f}')
print(f'Simple SUM of daily avg: {daily_avg.sum():.1f}%')
print(f'Simple SUM of all trades: {df.trader_return.sum():.1f}%')

# Year by year
df['year'] = df['date'].dt.year
print(f'\n--- Year by Year ---')
for year in sorted(df['year'].unique()):
    ydf = df[df['year'] == year]
    wr = ydf['correct'].mean() * 100
    avg_ret = ydf['trader_return'].mean()
    total_ret = ydf['trader_return'].sum()
    print(f'  {year}: {len(ydf):>4} trades | WR: {wr:.1f}% | Avg: {avg_ret:+.3f}% | Sum: {total_ret:+.1f}%')

# ==== US COMPARISON ====
print('\n' + '='*70)
print('US TRADE HISTORY - Comparison')
print('='*70)

df2 = pd.read_csv('logs/trade_history_US.csv', on_bad_lines='skip')
df2['date'] = pd.to_datetime(df2['date'], errors='coerce')
df2 = df2.dropna(subset=['date'])
df2['trader_return'] = pd.to_numeric(df2['trader_return'], errors='coerce').fillna(0)
df2['correct'] = pd.to_numeric(df2['correct'], errors='coerce').fillna(0)

print(f'\nTotal trades: {len(df2):,}')
wins2 = df2[df2['trader_return'] > 0]
losses2 = df2[df2['trader_return'] <= 0]
print(f'Wins: {len(wins2):,} ({len(wins2)/len(df2)*100:.1f}%)')
print(f'Avg Win: +{wins2.trader_return.mean():.4f}%')
print(f'Avg Loss: {losses2.trader_return.mean():.4f}%')
rrr2 = abs(wins2.trader_return.mean() / losses2.trader_return.mean()) if losses2.trader_return.mean() != 0 else 0
print(f'RRR: {rrr2:.4f}')

daily_avg2 = df2.groupby(df2['date'].dt.date)['trader_return'].mean()
print(f'Mean daily avg return: {daily_avg2.mean():.4f}%')
print(f'Trading days: {len(daily_avg2):,}')
equity2 = (1 + daily_avg2 / 100).cumprod()
print(f'Final COMPOUNDED equity: {equity2.iloc[-1]*100:.1f}')
print(f'Simple SUM of daily avg: {daily_avg2.sum():.1f}%')
