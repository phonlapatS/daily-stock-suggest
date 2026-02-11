#!/usr/bin/env python
"""
backtest.py - Backtest Pattern Accuracy
========================================
ทดสอบ accuracy ของ pattern matching ด้วย historical data
ไม่ต้องรอผลจริง - ใช้ข้อมูลในอดีตมาทดสอบทันที

Usage:
    python scripts/backtest.py                    # ทุกหุ้น (จาก config.py)
    python scripts/backtest.py PTT SET            # หุ้นเดียว
    python scripts/backtest.py NVDA NASDAQ 300    # ระบุ test bars
    python scripts/backtest.py --quick            # ทดสอบ 4 หุ้นหลัก
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import config
from core.data_cache import get_data_with_cache

# Load environment variables
load_dotenv()


def backtest_single(tv, symbol, exchange, n_bars=200, threshold_multiplier=1.25, min_stats=30, verbose=True, **kwargs):
    """
    Backtest หุ้นเดียว พร้อมแสดงช่วงวันที่
    
    Returns:
        dict: ผล backtest รวมถึง date_from, date_to
    """
    if verbose:
        print(f"\n🔬 BACKTEST: {symbol} ({exchange})")
        print("=" * 50)
    
    max_retries = 3
    df = None
    
    for attempt in range(max_retries):
        try:
            df = get_data_with_cache(
                tv=tv,
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                full_bars=5000,
                delta_bars=50
            )
            if df is not None and len(df) >= 250:
                break
        except Exception as e:
            if verbose: print(f"⚠️ Attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(2)
    
    if df is None or len(df) < 250:
        if verbose:
            print(f"❌ Not enough data for {symbol}")
        return None
    
    # Get date range
    total_bars = len(df)
    
    # --- DYNAMIC SPLIT STRATEGY (V3.4 Adaptive Logic) ---
    MIN_TRAIN_BARS = 200    
    MIN_TEST_BARS = 20      
    
    if total_bars < (MIN_TRAIN_BARS + MIN_TEST_BARS):
        if verbose:
            print(f"❌ Insufficient data ({total_bars} bars).")
        return None

    if total_bars >= 1000:
        final_test_bars = n_bars
        if final_test_bars > total_bars * 0.5:
            final_test_bars = int(total_bars * 0.5) 
    else:
        final_test_bars = int(total_bars * 0.20)
        final_test_bars = max(MIN_TEST_BARS, final_test_bars)
    
    n_bars = final_test_bars
    train_end = total_bars - n_bars
    
    test_date_from = df.index[train_end].strftime('%Y-%m-%d')
    test_date_to = df.index[-1].strftime('%Y-%m-%d')
    train_date_from = df.index[0].strftime('%Y-%m-%d')
    train_date_to = df.index[train_end-1].strftime('%Y-%m-%d')
    
    if verbose:
        print(f"📊 Total: {len(df)} bars")
        print(f"   Train: {train_date_from} → {train_date_to} ({train_end} bars)")
        print(f"   Test:  {test_date_from} → {test_date_to} ({n_bars} bars)")
    
    # Calculate Returns and Threshold
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    pct_change = close.pct_change()
    
    # NEW: Calculate Indicators for filtering (V4.3)
    from core.indicators import calculate_adx, calculate_volume_adv, calculate_rsi
    adx = calculate_adx(high, low, close)
    vol_adv = calculate_volume_adv(volume)
    rsi = calculate_rsi(close)
    sma50 = close.rolling(50).mean()
    
    # V4.4: Volume Ratio for China FOMO Filter
    vol_avg_20 = volume.rolling(20).mean()
    volume_ratio = volume / vol_avg_20  # VR > 3.0 = FOMO, VR < 0.5 = Dead
    
    # V4.2 Threshold Logic (Static Floors + Dynamic Base)
    is_us_market = any(ex in exchange.upper() for ex in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX'])
    is_thai_market = any(ex in exchange.upper() for ex in ['SET', 'MAI', 'TH'])
    is_china_market = any(ex in exchange.upper() for ex in ['HKEX', 'SHSE', 'SZSE'])
    
    # Define Floor based on market philosophy (V4.2)
    current_floor = 0
    if is_us_market: current_floor = 0.006     # 0.6%
    elif is_thai_market: current_floor = 0.01  # 1.0%
    
    if 'fixed_threshold' in kwargs and kwargs['fixed_threshold'] is not None:
         fixed_val = float(kwargs['fixed_threshold']) / 100.0
         threshold = pd.Series(fixed_val, index=pct_change.index)
    else:
        short_std = pct_change.rolling(window=20).std()
        long_std = pct_change.rolling(window=252).std()
        
        # V4.2: Max(20d SD, 252d SD, Market Floor)
        effective_std = np.maximum(short_std, long_std.fillna(0))
        effective_std = np.maximum(effective_std, current_floor)
        
        threshold = effective_std * threshold_multiplier
    
    # Convert to +/- pattern
    patterns = []
    for i in range(len(pct_change)):
        if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
            patterns.append('.') # Use '.' for neutral instead of empty
        elif pct_change.iloc[i] > threshold.iloc[i]:
            patterns.append('+')
        elif pct_change.iloc[i] < -threshold.iloc[i]:
            patterns.append('-')
        else:
            patterns.append('.')
    
    pattern_stats = {}
    MIN_LEN = 3
    MAX_LEN = 8
    
    # ... (Rest of pattern extraction remains similar, but using '.' instead of '') ...
    # Skip to loop and direction logic
    
    # 1. TRAINING PHASE
    for i in range(MAX_LEN, train_end - 1):
        next_ret = pct_change.iloc[i+1]
        if pd.isna(next_ret): continue

        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0: continue
            sub_pat_list = patterns[i-length+1 : i+1]
            pat = ''.join(sub_pat_list)
            if len(pat) < MIN_LEN: continue
            
            if pat not in pattern_stats:
                pattern_stats[pat] = []
            pattern_stats[pat].append(next_ret)
    
    if verbose:
        print(f"   Patterns found (Dynamic 3-{MAX_LEN}): {len(pattern_stats)}")
    
    # 2. TESTING PHASE
    total_predictions = 0
    correct_predictions = 0
    predictions = []
    
    for i in range(train_end, len(df) - 1):
        # ADX Filter (V4.4)
        min_adx = kwargs.get('min_adx')
        if min_adx is not None:
             if adx.iloc[i] < min_adx:
                 continue

        next_ret = pct_change.iloc[i+1]
        if pd.isna(next_ret):
            continue
        
        candidate_pats = []
        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0:
                continue
            sub_pat_list = patterns[i-length+1 : i+1]
            pat = ''.join(sub_pat_list)
            if len(pat) < MIN_LEN:
                continue
            
            if pat in pattern_stats:
                hist_returns = pattern_stats[pat]
                total = len(hist_returns)
                if total < min_stats:
                    continue
                
                # Base probabilities from historical returns
                bull_count = sum(1 for r in hist_returns if r > 0)
                bull_prob = (bull_count / total) * 100
                bear_prob = 100 - bull_prob
                
                # Default statistical winner (used for non-US markets)
                if bull_prob > bear_prob:
                    cand_dir, cand_prob = 1, bull_prob
                else:
                    cand_dir, cand_prob = -1, bear_prob
                
                # Calculate RR and expectancy for this candidate pattern
                if cand_dir == 1:
                    wins = [abs(r) for r in hist_returns if r > 0]
                    losses = [abs(r) for r in hist_returns if r <= 0]
                else:
                    wins = [abs(r) for r in hist_returns if r < 0]
                    losses = [abs(r) for r in hist_returns if r >= 0]
                
                avg_win = np.mean(wins) if wins else 0
                avg_loss = np.mean(losses) if losses else 0
                rr = avg_win / avg_loss if avg_loss > 0 else 0
                p_win = len(wins) / total if total > 0 else 0
                expectancy = p_win * avg_win - (1 - p_win) * avg_loss

                # 🔒 US MARKET QUALITY FILTER (Long-only, High-Edge Patterns)
                if is_us_market:
                    # Long-only: always evaluate from bull side
                    cand_dir = 1
                    cand_prob = bull_prob
                    wins = [abs(r) for r in hist_returns if r > 0]
                    losses = [abs(r) for r in hist_returns if r <= 0]
                    avg_win = np.mean(wins) if wins else 0
                    avg_loss = np.mean(losses) if losses else 0
                    rr = avg_win / avg_loss if avg_loss > 0 else 0
                    p_win = len(wins) / total if total > 0 else 0
                    expectancy = p_win * avg_win - (1 - p_win) * avg_loss

                    # Gatekeeper: keep only high-quality, profitable patterns
                    if cand_prob < 60.0 or rr < 1.5 or expectancy <= 0:
                        continue
                
                candidate_pats.append({
                    'length': length,
                    'pattern': pat,
                    'prob': cand_prob,
                    'dir': cand_dir,
                    'rr': rr,
                    'exp': expectancy,
                    'p_win': p_win,
                })
        
        if not candidate_pats:
            continue
            
        # Pick the best match prioritizing expectancy, then probability and length
        best_match = sorted(
            candidate_pats,
            key=lambda x: (x['exp'], x['prob'], x['length']),
            reverse=True
        )[0]
        
        last_char = best_match['pattern'][-1]
        
        # Determine Direction based on market philosophy
        if is_us_market:
            # US: Long-only trend following, direction already enforced as +1
            direction = 1
            strategy = "US_LONG_TREND"
        elif is_thai_market or is_china_market:
            # Thai & China/HK: Mean Reversion (fade last candle)
            if last_char == '+':
                direction = -1
            elif last_char == '-':
                direction = 1
            else:
                continue  # Pattern doesn't imply direction
            strategy = "MEAN_REVERSION"
            
            # V4.4: China FOMO Volume Filter
            if is_china_market:
                current_vr = volume_ratio.iloc[i] if not pd.isna(volume_ratio.iloc[i]) else 1.0
                if current_vr < 0.5:
                    continue  # Dead Zone (47.8% WR) → Skip
                elif current_vr > 3.0:
                    strategy = "FOMO_REVERSION"  # Tag for tracking
            
            # ====== PILLAR 1: Market Regime Filter ======
            # Skip LONG trades when price < SMA50 (bearish regime)
            if is_china_market and direction == 1:  # LONG only
                current_sma50 = sma50.iloc[i]
                if not pd.isna(current_sma50) and close.iloc[i] < current_sma50:
                    continue  # Bearish regime → skip longs
        else:
            # Default to historical winner if unknown market
            direction = best_match['dir']
            strategy = "STAT_FOLLOW"

        final_dir = direction
        final_forecast = "UP" if final_dir == 1 else "DOWN"
        
        # Confidence calculation for the chosen direction
        if is_us_market:
            confidence = best_match['prob']
        else:
            hist_returns = pattern_stats[best_match['pattern']]
            total_hist = len(hist_returns)
            bull_count = sum(1 for r in hist_returns if r > 0)
            confidence = (bull_count / total_hist) * 100 if final_dir == 1 else ((total_hist - bull_count) / total_hist) * 100
        
        # ====== Time Stop Analysis ======
        # NOTE: "Best-of-3" approach was REMOVED (look-ahead bias, inflated WR by +18%)
        # Testing showed: Day-1=49.8%, TP/SL=50.7%, Best-of-3=68.6%(BIASED)
        # Using honest Day-1 return. Market Regime + Vol Targeting are the real edge.
        trade_ret = next_ret  # Honest: next-day return only
        
        # Actual outcome
        actual_dir = 1 if trade_ret > 0 else -1
        actual_label = 'UP' if trade_ret > 0 else 'DOWN'
        is_correct = 1 if final_dir == actual_dir else 0
        
        # ====== PILLAR 2: Volatility Targeting ======
        raw_return_pct = trade_ret * 100 * final_dir
        if is_china_market:
            # Risk-adjusted: scale return by 2% target / actual SD
            stock_sd = pct_change.iloc[max(0,i-20):i].std()
            if not pd.isna(stock_sd) and stock_sd > 0:
                vol_scalar = min(0.02 / stock_sd, 2.0)  # Cap at 2x
            else:
                vol_scalar = 1.0
            trader_return_pct = raw_return_pct * vol_scalar
        else:
            trader_return_pct = raw_return_pct

        total_predictions += 1
        correct_predictions += is_correct

        predictions.append({
            'date': df.index[i],
            'pattern': best_match['pattern'],
            'forecast': final_forecast,
            'prob': confidence,
            'actual': actual_label,
            'actual_return': next_ret * 100,
            'trader_return': trader_return_pct,
            'correct': is_correct,
            'strategy': strategy
        })
    
    if total_predictions == 0:
        if verbose:
            print("❌ No signals passed strict filters (Acc > 60%, RR > 2.0)")
        return {
            'symbol': symbol, 
            'exchange': exchange, 
            'total': 0, 
            'correct': 0, 
            'accuracy': 0, 
            'avg_win': 0,
            'avg_loss': 0,
            'risk_reward': 0,
            'test_date_from': test_date_from,
            'test_date_to': test_date_to
        }
    
    accuracy = (correct_predictions / total_predictions) * 100
    
    result = {
        'symbol': symbol,
        'exchange': exchange,
        'total': total_predictions,
        'correct': correct_predictions,
        'accuracy': round(accuracy, 1),
        'detailed_predictions': predictions, # Ensure logs can be saved
        'test_date_from': test_date_from,
        'test_date_to': test_date_to,
    }
    
    # Calculate RR for all predictions
    wins = [abs(p['trader_return']) for p in predictions if p['correct'] == 1]
    losses = [abs(p['trader_return']) for p in predictions if p['correct'] == 0]
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    result.update({'avg_win': round(avg_win, 5), 'avg_loss': round(avg_loss, 5), 'risk_reward': round(rrr, 2)})
    return result


def save_trade_logs(trades, filename='trade_history.csv'):
    """
    Save list of trade dictionaries to CSV.
    
    Args:
        trades (list): List of trade result dictionaries.
        filename (str): Output filename.
    """
    if not trades:
        return

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, filename)
    
    df_trades = pd.DataFrame(trades)
    
    # Ensure columns exist and order them
    # Ensure columns exist and order them
    cols = ['date', 'symbol', 'exchange', 'group', 'pattern', 'forecast', 'prob', 'actual', 'actual_return', 'trader_return', 'correct', 'strategy']
    
    # Filter only existing columns to avoid errors if some keys are missing
    # Add missing columns with None
    for c in cols:
        if c not in df_trades.columns:
            df_trades[c] = None
            
    df_trades = df_trades[cols]
    
    # Append mode with header only if file does not exist
    header = not os.path.exists(log_path)
    df_trades.to_csv(log_path, mode='a', index=False, header=header)
    print(f"\n💾 Saved Trade Logs: {log_path} ({len(df_trades)} trades)")


def backtest_all(n_bars=200, skip_intraday=True, full_scan=False, target_group=None, threshold_multiplier=1.25):
    """
    Backtest ทุกหุ้นจาก config.py
    
    Args:
        n_bars: จำนวน test bars
        skip_intraday: ข้าม intraday (Gold/Silver) ไหม
        full_scan: If True, test ALL assets (no limit)
    """
    print("\n" + "=" * 70)
    print("🔬 BACKTEST ALL STOCKS")
    print("=" * 70)
    print(f"Test Period: {n_bars} bars ล่าสุด")
    print(f"Mode: {'FULL SCAN (200+ Assets)' if full_scan else 'SAMPLE SCAN (10 per group)'}")
    print("=" * 70)
    
    tv = TvDatafeed()
    
    # Results storage
    all_results = []
    all_trades = [] # Initialize logs list
    
    output_file = 'data/full_backtest_results.csv'
    processed_symbols = set()

    # When running a broad market scan (no group filter), we skip symbols that
    # already have results in full_backtest_results.csv to save time.
    # But for targeted scans (e.g. --group US) we always recompute.
    if not target_group and os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file)
            if 'symbol' in df_existing.columns:
                processed_symbols = set(df_existing['symbol'].tolist())
                print(f"📦 Found {len(processed_symbols)} existing results. Skipping...")
        except Exception:
            pass
    
    # Failure counter for connection issues
    consecutive_failures = 0
    
    for group_name, group_config in config.ASSET_GROUPS.items():
        # Filter by group if requested
        if target_group and target_group.upper() not in group_name.upper():
            continue
            
        # Skip intraday
        if skip_intraday and 'METALS' in group_name:
            print(f"\n⏭️ Skipping {group_name} (intraday)")
            continue
        
        print(f"\n📂 {group_config['description']}")
        print("-" * 50)
        
        assets = group_config['assets']
        
        # Deduplicate assets by symbol
        seen_assets = set()
        unique_assets = []
        for a in assets:
            sym = a.get('symbol')
            if sym and sym not in seen_assets:
                unique_assets.append(a)
                seen_assets.add(sym)
        
        # SAMPLE vs FULL scan selection
        if full_scan:
            target_assets = unique_assets
        else:
            # Limit to first 10 unique symbols for speed (sample scan)
            target_assets = unique_assets[:10]

        for i, asset in enumerate(target_assets):
            symbol = asset['symbol']
            exchange = asset['exchange']
            
            if symbol in processed_symbols:
                continue

            print(f"   [{i+1}/{len(target_assets)}] {symbol}...", end=" ")
            
            # Retry Logic with Exponential Backoff
            max_retries = 5 
            result = None
            success = False
            
            for attempt in range(max_retries):
                try:
                    fixed_thresh = group_config.get('fixed_threshold')
                    inverse_log = group_config.get('inverse_logic', False)
                    min_adx_val = group_config.get('min_adx')
                    result = backtest_single(tv, symbol, exchange, n_bars=n_bars, verbose=False, fixed_threshold=fixed_thresh, inverse_logic=inverse_log, threshold_multiplier=threshold_multiplier, min_adx=min_adx_val)
                    
                    if result:
                        success = True
                        consecutive_failures = 0
                        break
                    else:
                        break 
                except Exception as e:
                    errMsg = str(e).lower()
                    is_timeout = "connection" in errMsg or "timeout" in errMsg or "no data" in errMsg
                    
                    if is_timeout:
                        wait_time = (2 ** attempt) * 5
                        print(f"⚠️ Timeout. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(wait_time)
                        try:
                            tv = TvDatafeed()
                        except: pass
                    else:
                        print(f"❌ Error: {e}")
                        break
            
            if success and result:
                result['group'] = group_name
                all_results.append(result)
                if result.get('total', 0) > 0:
                    print(f"✅ {result['accuracy']:.1f}% ({result['total']} Trades)")
                else:
                    print("✅ 0 Trades found")
                
                # Incremental Save
                df_current = pd.DataFrame([result])
                if 'detailed_predictions' in df_current.columns:
                    df_current = df_current.drop(columns=['detailed_predictions'])
                
                df_current.to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))

                if 'detailed_predictions' in result:
                    trade_logs = []
                    for trade in result['detailed_predictions']:
                        trade['symbol'] = symbol
                        trade['exchange'] = exchange
                        trade['group'] = group_name
                        trade_logs.append(trade)
                    
                    # Log File per Group (Cleaner)
                    group_clean = group_name.replace(" ", "_").upper()
                    if 'US' in group_clean: file_suffix = 'US'
                    elif 'THAI' in group_clean: file_suffix = 'THAI'
                    elif 'CHINA' in group_clean or 'HK' in group_clean: file_suffix = 'CHINA'
                    elif 'TAIWAN' in group_clean: file_suffix = 'TAIWAN'
                    elif 'GOLD' in group_clean or 'SILVER' in group_clean: file_suffix = 'METALS'
                    else: file_suffix = 'OTHER'
                    
                    log_file = f'logs/trade_history_{file_suffix}.csv'
                    save_trade_logs(trade_logs, filename=os.path.basename(log_file))
            else:
                consecutive_failures += 1
                if not result: print("❌ (No Data)")
                else: print("❌")

            # Cool-down if too many failures in a row
            if consecutive_failures >= 3:
                print(f"🛑 {consecutive_failures} consecutive failures. Entering Cool-down (60s)...")
                time.sleep(60)
                consecutive_failures = 0 # Reset
                tv = TvDatafeed() # Fresh connection
            
            # Market-Specific Delays
            is_china = any(ex in exchange.upper() for ex in ['SHSE', 'SZSE', 'CHINA'])
            base_delay = 3.0 if is_china else 1.0
            time.sleep(base_delay)
            
    # Save Trade Logs using helper
    save_trade_logs(all_trades)
    
    # Summary
    if all_results:
        print("\n" + "=" * 70)
        print("📊 BACKTEST SUMMARY")
        print("=" * 70)
        
        df = pd.DataFrame(all_results)
        
        # Date range
        date_from = df['test_date_from'].min() if 'test_date_from' in df.columns else "N/A"
        date_to = df['test_date_to'].max() if 'test_date_to' in df.columns else "N/A"
        print(f"\n📅 Test Period: {date_from} → {date_to}")
        print(f"   ({n_bars} bars per stock)")
        
        # Overall Metrics
        total_preds = df['total'].sum()
        total_correct = df['correct'].sum()
        avg_acc = (total_correct / total_preds * 100) if total_preds > 0 else 0
        
        # Weighted RRR / Expectancy
        total_win_sum = (df['avg_win'] * (df['total'] * df['accuracy']/100)).sum()
        total_loss_sum = (df['avg_loss'] * (df['total'] * (1 - df['accuracy']/100))).sum()
        market_rrr = total_win_sum / total_loss_sum if total_loss_sum > 0 else 0
        
        print(f"\n🎯 Overall Market Stats:")
        print(f"   Accuracy: {avg_acc:.1f}%")
        print(f"   Market RRR: {market_rrr:.2f}")
        print(f"   Total Signals: {total_preds}")
        
        # Best & Worst RRR (Risk-Reward focus)
        print(f"\n🏆 Top 5 Best Risk-Reward (RRR):")
        top_rrr = df[df['total'] >= 5].nlargest(5, 'risk_reward')
        for _, r in top_rrr.iterrows():
            print(f"   {r['symbol']:<10} RRR: {r['risk_reward']:<6.2f} (Win: {r['avg_win']:.2f}%, Loss: {r['avg_loss']:.2f}%, Acc: {r['accuracy']:.1f}%)")
        
        # Group Analysis
        print(f"\n📂 Sector Analysis (Risk/Reward Floor):")
        sector_stats = df.groupby('group').agg({
            'accuracy': 'mean',
            'risk_reward': 'mean',
            'total': 'sum'
        })
        for grp, r in sector_stats.iterrows():
             print(f"   {grp:<25} Avg RRR: {r['risk_reward']:<5.2f} Avg Acc: {r['accuracy']:>5.1f}% (Signals: {int(r['total'])})")
        
        return df
        
        return df
    
    return None


def main():
    import argparse
    
    print("\n" + "=" * 70)
    print("🔬 PATTERN MATCHING BACKTEST")
    print("=" * 70)
    print("ทดสอบ accuracy ด้วย historical data (ไม่ต้องรอผลจริง)")
    print("=" * 70)
    
    parser = argparse.ArgumentParser(description="Backtest Pattern Recognition System")
    parser.add_argument('symbol', nargs='?', help='Stock Symbol (e.g. PTT)')
    parser.add_argument('exchange', nargs='?', default='SET', help='Exchange (e.g. SET, NASDAQ)')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--quick', action='store_true', help='Run quick test on 4 main stocks')
    group.add_argument('--all', action='store_true', help='Run on all stocks (Sample 10)')
    group.add_argument('--full', action='store_true', help='Run FULL scan on entire market')
    
    parser.add_argument('--bars', type=int, default=200, help='Number of bars to test (default: 200)')
    parser.add_argument('--group', type=str, help='Filter by group name (e.g. US, THAI)')
    
    parser.add_argument('--multiplier', type=float, default=1.25, help='Threshold multiplier (default: 1.25)')
    
    args = parser.parse_args()
    
    n_bars = args.bars
    threshold_multiplier = args.multiplier
    
    if args.full:
        # Full Scan Mode
        print(f"🚀 Running FULL SCAN on market (Bars: {n_bars}, Group: {args.group})")
        backtest_all(n_bars=n_bars, full_scan=True, target_group=args.group, threshold_multiplier=threshold_multiplier)
        
    elif args.all:
        # Sample Scan Mode
        print(f"🚀 Running SAMPLE SCAN on all stocks (Bars: {n_bars}, Group: {args.group})")
        backtest_all(n_bars=n_bars, full_scan=False, target_group=args.group, threshold_multiplier=threshold_multiplier)
        
    elif args.quick:
        # Quick Test Mode
        default_stocks = [
            ('PTT', 'SET'),
            ('ADVANC', 'SET'),
            ('NVDA', 'NASDAQ'),
            ('AAPL', 'NASDAQ'),
        ]
        
        print(f"\n🚀 Quick test: {len(default_stocks)} stocks, {n_bars} test bars each")
        
        # Connect TV with Credentials
        tv_user = os.environ.get('TV_USERNAME', '')
        tv_pass = os.environ.get('TV_PASSWORD', '')
        if tv_user and tv_pass:
            print(f"🔑 Authenticated for Quick Test: {tv_user}")
            tv = TvDatafeed(username=tv_user, password=tv_pass)
        else:
            tv = TvDatafeed()
            
        results = []
        all_trades = []
        
        for symbol, exchange in default_stocks:
            result = backtest_single(tv, symbol, exchange, n_bars=n_bars, threshold_multiplier=threshold_multiplier)
            if result:
                results.append(result)
                if 'detailed_predictions' in result:
                    for trade in result['detailed_predictions']:
                        trade['symbol'] = symbol
                        trade['exchange'] = exchange
                        trade['group'] = 'QUICK_TEST'
                        all_trades.append(trade)
        
        # Save Trade Logs
        save_trade_logs(all_trades)
            
        if results:
            print("\n" + "=" * 60)
            print("📊 SUMMARY")
            print("=" * 60)
            
            print(f"\n📅 Test Period: {results[0]['test_date_from']} → {results[0]['test_date_to']}")
            
            total_preds = sum(r['total'] for r in results)
            total_correct = sum(r['correct'] for r in results)
            avg_accuracy = total_correct / total_preds * 100 if total_preds > 0 else 0
            
            print(f"\n{'Symbol':<12} {'Exchange':<10} {'Total':<8} {'Correct':<8} {'Accuracy':<10} {'Avg Win%':<10} {'Avg Loss%':<10} {'RRR':<6}")
            print("-" * 85)
            for r in results:
                print(f"{r['symbol']:<12} {r['exchange']:<10} {r['total']:<8} {r['correct']:<8} {r['accuracy']:.1f}%      {r['avg_win']:<10.2f} {r['avg_loss']:<10.2f} {r['risk_reward']:<6.2f}")
            print("-" * 85)
            
            total_avg_win = sum(r['avg_win'] for r in results) / len(results) if results else 0
            total_avg_loss = sum(r['avg_loss'] for r in results) / len(results) if results else 0
            total_rrr = total_avg_win / total_avg_loss if total_avg_loss > 0 else 0
            
            print(f"{'TOTAL':<12} {'':<10} {total_preds:<8} {total_correct:<8} {avg_accuracy:.1f}%      {total_avg_win:<10.2f} {total_avg_loss:<10.2f} {total_rrr:<6.2f}")

    elif args.symbol:
        
        # Auto-detect config settings (fixed_threshold)
        fixed_thresh = None
        
        for group_name, group_config in config.ASSET_GROUPS.items():
            for asset in group_config['assets']:
                if asset['symbol'] == args.symbol:
                     fixed_thresh = group_config.get('fixed_threshold')
                     break
            if fixed_thresh is not None: break
            
        print(f"   Config Detected: Fixed Threshold={fixed_thresh}")
        
        # Connect TV with Credentials
        tv_user = os.environ.get('TV_USERNAME', '')
        tv_pass = os.environ.get('TV_PASSWORD', '')
        if tv_user and tv_pass:
            tv = TvDatafeed(username=tv_user, password=tv_pass)
        else:
            tv = TvDatafeed()
            
        result = backtest_single(tv, args.symbol, args.exchange, n_bars=n_bars, fixed_threshold=fixed_thresh, threshold_multiplier=threshold_multiplier)
        
        if result and 'detailed_predictions' in result:
            for p in result['detailed_predictions']:
                p['symbol'] = args.symbol
                p['exchange'] = args.exchange
                p['group'] = 'SINGLE_TEST'
            save_trade_logs(result['detailed_predictions'])
        
    else:
        parser.print_help()

    print("\n" + "=" * 70)
    print("✅ Backtest Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
