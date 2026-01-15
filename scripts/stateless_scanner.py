#!/usr/bin/env python
"""
stateless_scanner.py - Automated Statistical Anomaly & Pattern Matching (Production V1)
=====================================================================================
Architecture: Stateless Pipeline (Fetch -> Process -> Report -> Forget)
Objective: Identify high-probability setups using historical pattern matching
           without maintaining persistent raw data storage.

Features (Production Grade):
- Robust Retry Logic for API fetching
- Detailed CSV Logging
- Memory Management (gc.collect)
- Progress Tracking
- Error Resilience (continue on failure)

Process:
1. Fetch: Get 15 years data to RAM (tvDatafeed)
2. Process:
   - Volatility Filter: Current Move > 2SD (20-day rolling)
   - Pattern Match: Top 10 matches (Pearson > 0.8) for last 14 days
3. Report: WinRate > 70%
4. Forget: Clear RAM

Author: Stock Analysis System
Date: 2026-01-16
"""

import sys
import os
import time
import gc
import pandas as pd
import numpy as np
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# Configuration
WATCHLIST_FILE = "data/all_thai_stocks.txt"
RESULTS_LOG = "data/scan_results.csv"
ERROR_LOG = "data/scan_errors.log"

# Analysis Params
HISTORY_BARS = 3500  # ~14 years
SEQ_LEN = 14         # Pattern length (days)
SD_WINDOW = 20       # Volatility window
SD_MULTIPLIER = 2.0  # Threshold multiplier
MIN_CORR = 0.80      # Min correlation for match
TOP_N = 10           # Top matches to analyze
WIN_RATE_THRESHOLD = 70.0 # Report criteria

# System Params
MAX_RETRIES = 3      # Max API retries
RETRY_DELAY = 2      # Seconds between retries
RATE_LIMIT = 0.5     # Min seconds between requests

def setup_logs():
    """Initialize log files if not exist"""
    if not os.path.exists(RESULTS_LOG):
        with open(RESULTS_LOG, 'w') as f:
            f.write("Timestamp,Asset,Price,Change,Threshold,Signal,WinRate,AvgRet,Events,PearsonScore\n")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(RESULTS_LOG), exist_ok=True)

def fetch_data_memory(tv, symbol, exchange='SET'):
    """Step 1: Fetch Data into RAM with Retry Logic"""
    for attempt in range(MAX_RETRIES):
        try:
            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=HISTORY_BARS
            )
            
            # Validation
            if df is None or df.empty:
                raise ValueError("Empty data returned")
            
            if len(df) < 200:
                raise ValueError(f"Insufficient data: {len(df)} bars")
                
            return df
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                # Log final failure
                with open(ERROR_LOG, 'a') as f:
                    f.write(f"{datetime.now()},{symbol},Fetch Error,{str(e)}\n")
                return None
    return None

def process_statistical_analysis(df):
    """Step 2: Process (Volatility + Pattern)"""
    try:
        # 2.0 Prepare Data
        close = df['close']
        pct_change = close.pct_change()
        
        # ----------------------------------------
        # 2.1 Dynamic Volatility Filtering
        # ----------------------------------------
        rolling_sd = pct_change.rolling(window=SD_WINDOW).std()
        
        # Handle NaN at start
        if rolling_sd.iloc[-1] is np.nan:
            return None
            
        threshold = rolling_sd * SD_MULTIPLIER
        
        current_change = pct_change.iloc[-1]
        current_threshold = threshold.iloc[-1]
        
        # Logic: If <= 2SD, it's Noise -> Terminate
        if abs(current_change) <= current_threshold:
            return None  # Terminate (Noise)
        
        # ----------------------------------------
        # 2.2 Historical Pattern Matching
        # ----------------------------------------
        # Extract current sequence (last 14 days)
        # Normalize sequence (Z-Score standardization)
        current_seq = close.iloc[-SEQ_LEN:].values
        if len(current_seq) < SEQ_LEN: return None
        
        curr_mean = np.mean(current_seq)
        curr_std = np.std(current_seq)
        
        if curr_std == 0: return None
        current_seq_norm = (current_seq - curr_mean) / curr_std
        
        # Sliding Window over history
        history = close.values[:-1] # Exclude today
        
        if len(history) < SEQ_LEN + 1:
            return None
            
        # Create windows
        windows = np.lib.stride_tricks.sliding_window_view(history, SEQ_LEN)
        
        # Vectorized Correlation Calculation
        w_mean = np.mean(windows, axis=1, keepdims=True)
        w_std = np.std(windows, axis=1, keepdims=True)
        
        # Avoid div by zero
        valid_mask = w_std.flatten() > 0
        windows = windows[valid_mask]
        w_mean = w_mean[valid_mask]
        w_std = w_std[valid_mask]
        indices = np.arange(len(history) - SEQ_LEN + 1)[valid_mask]
        
        # Normalize windows
        windows_norm = (windows - w_mean) / w_std
        
        # Calculate Correlation
        corr = np.dot(windows_norm, current_seq_norm) / SEQ_LEN
        
        # Filter matches
        match_mask = corr >= MIN_CORR
        match_indices = indices[match_mask]
        match_scores = corr[match_mask]
        
        if len(match_indices) == 0:
            return None
            
        # Get Top N matches
        sorted_idx_locs = np.argsort(match_scores)[::-1][:TOP_N]
        top_indices = match_indices[sorted_idx_locs]
        top_scores = match_scores[sorted_idx_locs]
        
        # ----------------------------------------
        # 2.3 Probability Calculation
        # ----------------------------------------
        future_returns = []
        
        for idx in top_indices:
            next_day_idx = idx + SEQ_LEN
            if next_day_idx < len(history):
                # Use pre-computed pct_change array
                # Need to align index carefully. pct_change likely matches history length roughly
                # safer to calculate manually from price to match indices
                # price_after = history[next_day_idx]
                # price_end_match = history[next_day_idx - 1]
                # ret = (price_after - price_end_match) / price_end_match
                
                # Check bounds for pct_change
                if next_day_idx < len(pct_change):
                    ret = pct_change.values[next_day_idx] * 100 # Convert to %
                    # Handle NaN
                    if not np.isnan(ret):
                        future_returns.append(ret)
                
        if not future_returns:
            return None
            
        avg_return = np.mean(future_returns)
        
        # Win Rate Analysis
        trend_direction = 1 if current_change > 0 else -1
        wins = sum(1 for r in future_returns if (r * trend_direction) > 0)
        win_rate = (wins / len(future_returns)) * 100
        
        return {
            'price': close.iloc[-1],
            'change': current_change * 100,
            'threshold': current_threshold * 100,
            'matches': len(match_indices),
            'top_score': top_scores[0],
            'win_rate': win_rate,
            'avg_return': avg_return,
            'samples': len(future_returns)
        }
        
    except Exception as e:
        # Silent fail on calculation error, log if needed
        return None

def log_result(symbol, signal, res):
    """Step 4: Forget (Log & Clear)"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # CSV Format: Timestamp,Asset,Price,Change,Threshold,Signal,WinRate,AvgRet,Events,PearsonScore
    row = f"{timestamp},{symbol},{res['price']:.2f},{res['change']:.2f}%,{res['threshold']:.2f}%,{signal},{res['win_rate']:.1f}%,{res['avg_return']:.2f}%,{res['samples']},{res['top_score']:.4f}\n"
    
    with open(RESULTS_LOG, 'a') as f:
        f.write(row)
    
    # Also print to console
    print(f"\n⚡ MATCH: {symbol} | WinRate: {res['win_rate']:.1f}% | Events: {res['samples']}")

def main():
    print("\n" + "="*80)
    print("🚀 STATELESS STATISTICAL SCANNER (PRODUCTION V1)")
    print("="*80)
    print(f"🎯 Logic: 2SD Volatility + Pearson Correlation (>0.8)")
    print(f"📡 Data: RAM Only (Fetch > Process > Report > Forget)")
    print(f"💾 Log:  {RESULTS_LOG}")
    print("="*80)
    
    setup_logs()
    
    # Load Watchlist
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            watchlist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print("⚠️ Watchlist not found, using default test set")
        watchlist = ['PTT', 'KBANK', 'AOT', 'DELTA', 'SCB', 'GULF', 'CPALL', 'ADVANC']
        
    # Connect
    print("🔌 Connecting to TradingView...")
    tv = TvDatafeed()
    
    print(f"🔍 Scanning {len(watchlist)} assets...")
    start_time = time.time()
    
    for i, symbol in enumerate(watchlist):
        try:
            # Progress Bar
            sys.stdout.write(f"\r[{i+1}/{len(watchlist)}] Parsing {symbol:<8} ")
            sys.stdout.flush()
            
            # Step 1: Fetch
            df = fetch_data_memory(tv, symbol)
            
            if df is None:
                continue
                
            # Step 2: Process
            res = process_statistical_analysis(df)
            
            # Step 3: Report
            if res:
                if res['win_rate'] >= WIN_RATE_THRESHOLD:
                    direction = "BUY/FOLLOW" if res['change'] > 0 else "SELL/FOLLOW"
                    log_result(symbol, direction, res)
            
            # Step 4: Forget
            del df
            
            # Force Garbage Collection periodically
            if i % 50 == 0:
                gc.collect()
            
            # Rate Limit
            time.sleep(RATE_LIMIT)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Scan interrupted by user.")
            break
        except Exception as e:
            # Global error handler to keep loop running
            with open(ERROR_LOG, 'a') as f:
                f.write(f"{datetime.now()},{symbol},System Error,{str(e)}\n")
            continue
            
    elapsed = time.time() - start_time
    print(f"\n\n✅ Scan Complete in {elapsed/60:.2f} minutes.")
    print(f"📄 Results saved to: {RESULTS_LOG}")

if __name__ == "__main__":
    main()
