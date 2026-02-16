#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบ DELTA trades ใน trade_history
"""
import pandas as pd
import glob
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

files = glob.glob(os.path.join(LOGS_DIR, "trade_history_*.csv"))
tw_file = None
for f in files:
    if 'TAIWAN' in f.upper() or 'TW' in f.upper():
        tw_file = f
        break

if tw_file:
    print(f'File: {os.path.basename(tw_file)}')
    df = pd.read_csv(tw_file)
    print(f'Columns: {list(df.columns)}')
    print(f'Total rows: {len(df)}')
    
    if 'symbol' in df.columns:
        print(f'\nUnique symbols (first 30):')
        symbols = df['symbol'].unique()[:30]
        for s in symbols:
            print(f'  - {s}')
        
        # หา DELTA
        delta = df[df['symbol'].astype(str).str.contains('2308|DELTA', case=False, na=False)]
        print(f'\nDELTA trades: {len(delta)}')
        
        if not delta.empty:
            print(f'\nSample DELTA trades:')
            print(delta[['symbol', 'prob', 'correct', 'actual_return']].head(10) if 'prob' in delta.columns else delta.head(10))
            
            # ตรวจสอบ group
            if 'group' in delta.columns:
                print(f'\nGroups: {delta["group"].unique()}')
else:
    print('No Taiwan file found')

