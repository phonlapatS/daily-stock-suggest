import pandas as pd
try:
    df = pd.read_csv('logs/performance_log.csv')
    epg = df[df['symbol'] == 'EPG'][['symbol', 'forecast', 'price_at_scan', 'price_actual', 'change_pct', 'actual', 'correct']]
    print(epg.to_string())
except Exception as e:
    print(f"Error: {e}")
