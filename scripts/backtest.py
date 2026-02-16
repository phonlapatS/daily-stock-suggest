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

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
import config
from core.data_cache import get_data_with_cache
# REMOVED: BasePatternEngine import (V6.1 - No longer using Trailing Stop)

# Load environment variables
load_dotenv()


# ====================================================================
# V11.0: PRODUCTION-REALISTIC PARAMETERS
# ====================================================================
# These parameters simulate real-world trading friction that backtests
# typically ignore. Enable with --production flag.
#
# Without these: Backtest shows IDEAL performance
# With these:    Backtest shows REALISTIC performance
# ====================================================================

# Slippage: % of price lost due to bid-ask spread + market impact
# - Thai SET: wider spreads, less liquid
# - US: tight spreads on large-cap, wider on small-cap
# - Taiwan/China: moderate
SLIPPAGE_PCT = {
    'THAI': 0.10,       # 0.10% per trade (each way)
    'US': 0.05,         # 0.05% per trade
    'TAIWAN': 0.07,     # 0.07% per trade
    'CHINA': 0.08,      # 0.08% per trade
    'DEFAULT': 0.05
}

# Commission: round-trip (buy + sell) brokerage fee
# - Thai SET: ~0.157% (online broker) each way = ~0.314% round-trip
# - US: ~$0 commission but SEC fee → ~0.01% effective
# - Taiwan: 0.1425% + tax 0.3% sell = ~0.44% round-trip
# - China/HK: stamp 0.1% + commission 0.05% each way = ~0.30% round-trip
COMMISSION_PCT = {
    'THAI': 0.32,       # 0.16% x 2 = 0.32% round-trip
    'US': 0.02,         # Near-zero commission era (SEC fee only)
    'TAIWAN': 0.44,     # Tax + commission
    'CHINA': 0.30,      # Stamp duty + commission
    'DEFAULT': 0.10
}

# Minimum daily volume (shares) to consider a stock tradeable
MIN_VOLUME = {
    'THAI': 500_000,    # 500K shares/day minimum
    'US': 100_000,      # 100K shares/day minimum  
    'TAIWAN': 200_000,  # 200K shares/day minimum
    'CHINA': 200_000,   # 200K shares/day minimum
    'DEFAULT': 100_000
}

# Gap Risk Factor: How much worse SL can be due to gaps
# e.g. 1.3 means SL of 1.5% could become 1.95% after gap
GAP_RISK_FACTOR = {
    'THAI': 1.20,       # Thai has daily limit ±30%, gaps are moderate
    'US': 1.30,         # US can gap significantly on news
    'TAIWAN': 1.25,     # Taiwan moderate gaps
    'CHINA': 1.35,      # China/HK can have large gaps
    'DEFAULT': 1.25
}


def get_market_key(exchange):
    """Get market key from exchange name for production parameters"""
    ex = exchange.upper()
    if any(x in ex for x in ['SET', 'MAI', 'TH']): return 'THAI'
    if any(x in ex for x in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX']): return 'US'
    if any(x in ex for x in ['TWSE', 'TW']): return 'TAIWAN'
    if any(x in ex for x in ['HKEX', 'SHSE', 'SZSE']): return 'CHINA'
    return 'DEFAULT'


def calc_atr(high, low, close, period=14):
    """Calculate Average True Range - ใช้สำหรับ ATR-based SL/TP"""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def simulate_trade_with_rm(df, entry_idx, direction, stop_loss_pct=2.0, take_profit_pct=4.0, max_hold_days=5,
                           atr_series=None, atr_sl_mult=None, atr_tp_mult=None,
                           use_trailing_stop=False, trail_activation_pct=1.5, trail_distance_pct=50.0,
                           production_mode=False, slippage_pct=0.0, commission_pct=0.0, gap_risk=1.0):
    """
    Simulate a trade with Risk Management (Stop Loss / Take Profit / Multi-day hold)
    
    V11.0 PRODUCTION-REALISTIC:
    - Entry at NEXT BAR OPEN (not current close) when production_mode=True
    - Slippage applied to entry and exit prices
    - Commission deducted from final return (round-trip)
    - Gap risk: SL can be worse than target if price gaps through
    - Trailing stop exit uses conservative fill (not exact level)
    
    Args:
        df: DataFrame with OHLCV data
        entry_idx: Index of entry bar (signal generated at close of this bar)
        direction: 1 = LONG, -1 = SHORT
        stop_loss_pct: Fixed stop loss %
        take_profit_pct: Fixed take profit %
        max_hold_days: Maximum hold days
        atr_series: Pre-calculated ATR series (optional)
        atr_sl_mult: ATR multiplier for SL
        atr_tp_mult: ATR multiplier for TP
        use_trailing_stop: Enable trailing stop
        trail_activation_pct: Profit % to activate trailing stop
        trail_distance_pct: Trail distance as % of peak profit
        production_mode: Enable production-realistic friction
        slippage_pct: Slippage % per trade (each way)
        commission_pct: Commission % round-trip (buy + sell)
        gap_risk: Factor for gap risk on SL (e.g. 1.3 = 30% worse)
    
    Returns:
        dict: {'return_pct': float, 'exit_reason': str, 'hold_days': int, 'sl_used': float}
    """
    close = df['close']
    high = df['high']
    low = df['low']
    has_open = 'open' in df.columns
    
    # V11.0: Entry price logic
    if production_mode and has_open and entry_idx + 1 < len(df):
        # PRODUCTION: Enter at NEXT bar's OPEN (realistic: signal at close, execute next morning)
        entry_price = df['open'].iloc[entry_idx + 1]
        # Apply entry slippage (LONG pays more, SHORT gets less)
        if direction == 1:
            entry_price *= (1 + slippage_pct / 100)  # Worse fill for buy
        else:
            entry_price *= (1 - slippage_pct / 100)  # Worse fill for sell
    else:
        # BACKTEST (ideal): Enter at current close
        entry_price = close.iloc[entry_idx]
    
    # Determine actual SL/TP percentages
    if atr_series is not None and atr_sl_mult is not None and atr_tp_mult is not None:
        atr_val = atr_series.iloc[entry_idx]
        if pd.isna(atr_val) or atr_val <= 0:
            # Fallback: ใช้ค่า ATR ที่คำนวณจาก volatility จริง (ไม่ lock ที่ 2%)
            # คำนวณจาก rolling std ของ price change (20 days)
            if entry_idx >= 20:
                price_changes = df['close'].pct_change().iloc[max(0, entry_idx-20):entry_idx+1]
                price_changes = price_changes.dropna()  # Remove NaN values
                if len(price_changes) > 0:
                    std_val = price_changes.std()
                    if not pd.isna(std_val) and std_val > 0:
                        atr_val = entry_price * std_val * 1.5  # 1.5x std as ATR estimate
                    else:
                        atr_val = entry_price * 0.015  # Fallback 1.5%
                else:
                    atr_val = entry_price * 0.015  # Fallback 1.5%
            else:
                atr_val = entry_price * 0.015  # Fallback 1.5% (ลดจาก 2% → 1.5%)
            
            # Final check: ensure atr_val is valid
            if pd.isna(atr_val) or atr_val <= 0:
                atr_val = entry_price * 0.015  # Final fallback 1.5%
        actual_sl_pct = (atr_val * atr_sl_mult / entry_price) * 100
        actual_tp_pct = (atr_val * atr_tp_mult / entry_price) * 100
        # V9.0: Cap ATR-based SL/TP to prevent wild swings
        # Updated: เพิ่ม cap เพื่อให้ยืดหยุ่นขึ้น (AvgLoss% ไม่ lock)
        actual_sl_pct = min(actual_sl_pct, 7.0)   # Max 7% SL (เพิ่มจาก 5% → 7% เพื่อให้ยืดหยุ่นขึ้น)
        actual_tp_pct = min(actual_tp_pct, 15.0)  # Max 15% TP (เพิ่มจาก 12% → 15% เพื่อให้ยืดหยุ่นขึ้น)
    else:
        actual_sl_pct = stop_loss_pct
        actual_tp_pct = take_profit_pct
    
    # V11.0: Production adjustments for SL
    # In real trading, SL can be worse than target due to gaps
    effective_gap_sl = actual_sl_pct * gap_risk if production_mode else actual_sl_pct
    # Exit slippage: when exiting, you get slightly worse price
    exit_slip = slippage_pct if production_mode else 0.0
    # Total friction: commission is deducted from every trade's return
    total_commission = commission_pct if production_mode else 0.0
    
    # V9.0: Trailing Stop state
    peak_profit_pct = 0.0
    trailing_active = False
    trailing_stop_level = -actual_sl_pct  # Start at SL level
    
    # V11.0: Production mode starts holding from day 1 (after entry at next open)
    # In ideal mode, entry is at close of signal day, hold starts next day
    start_day = 1
    if production_mode and has_open:
        start_day = 2  # Signal at close of entry_idx, enter at open of entry_idx+1, first full day is entry_idx+2
    
    for day in range(start_day, start_day + max_hold_days):
        if entry_idx + day >= len(df):
            last_idx = min(entry_idx + day - 1, len(df) - 1)
            exit_price = close.iloc[last_idx]
            ret_pct = (exit_price / entry_price - 1) * 100 * direction
            ret_pct -= (exit_slip + total_commission)  # V11.0: Deduct friction
            return {'return_pct': ret_pct, 'exit_reason': 'END_DATA', 'hold_days': day - start_day, 'sl_used': actual_sl_pct}
        
        current_high = high.iloc[entry_idx + day]
        current_low = low.iloc[entry_idx + day]
        current_close = close.iloc[entry_idx + day]
        
        if direction == 1:  # LONG
            intraday_worst_pct = (current_low / entry_price - 1) * 100
            intraday_best_pct = (current_high / entry_price - 1) * 100
            close_pct = (current_close / entry_price - 1) * 100
        else:  # SHORT
            intraday_worst_pct = -(current_high / entry_price - 1) * 100
            intraday_best_pct = -(current_low / entry_price - 1) * 100
            close_pct = -(current_close / entry_price - 1) * 100
        
        # Update peak profit
        peak_profit_pct = max(peak_profit_pct, intraday_best_pct)
        
        # Check SL hit (or trailing stop)
        if use_trailing_stop and peak_profit_pct >= trail_activation_pct:
            # Trailing stop activated
            trailing_active = True
            # Trail at X% below peak (e.g. 50% of peak → if peak=4%, trail stop at 2%)
            trailing_stop_level = peak_profit_pct * (1 - trail_distance_pct / 100)
            # At minimum, break-even once trailing is activated
            trailing_stop_level = max(trailing_stop_level, 0.0)
            
            if intraday_worst_pct <= trailing_stop_level:
                # V11.0: Production → exit slightly below trail level (slippage)
                exit_pct = max(trailing_stop_level - exit_slip, 0.0)
                exit_pct -= total_commission  # Deduct commission
                return {'return_pct': exit_pct, 'exit_reason': 'TRAILING_STOP', 'hold_days': day - start_day + 1, 'sl_used': actual_sl_pct}
        
        # Regular SL check (only if trailing not active or price below activation)
        if not trailing_active:
            if actual_sl_pct and intraday_worst_pct <= -actual_sl_pct:
                # V11.0: Production → SL can be worse due to gap (gap_risk factor)
                sl_fill = -effective_gap_sl - exit_slip - total_commission
                return {'return_pct': sl_fill, 'exit_reason': 'STOP_LOSS', 'hold_days': day - start_day + 1, 'sl_used': actual_sl_pct}
        
        # TP check
        if actual_tp_pct and intraday_best_pct >= actual_tp_pct:
            # V11.0: Production → TP might fill slightly below target (slippage)
            tp_fill = actual_tp_pct - exit_slip - total_commission
            return {'return_pct': tp_fill, 'exit_reason': 'TAKE_PROFIT', 'hold_days': day - start_day + 1, 'sl_used': actual_sl_pct}
        
        # Last day: exit at close
        if day == start_day + max_hold_days - 1:
            ret_pct = close_pct
            # If trailing was active and close is below trail level, use trail level
            if trailing_active and ret_pct < trailing_stop_level:
                ret_pct = max(trailing_stop_level - exit_slip, 0.0)
                ret_pct -= total_commission
                return {'return_pct': ret_pct, 'exit_reason': 'TRAILING_STOP', 'hold_days': day - start_day + 1, 'sl_used': actual_sl_pct}
            ret_pct -= (exit_slip + total_commission)  # V11.0: Deduct friction
            return {'return_pct': ret_pct, 'exit_reason': 'MAX_HOLD', 'hold_days': day - start_day + 1, 'sl_used': actual_sl_pct}
    
    # Fallback
    return {'return_pct': 0 - total_commission, 'exit_reason': 'UNKNOWN', 'hold_days': 0, 'sl_used': actual_sl_pct}


def backtest_single(tv, symbol, exchange, n_bars=200, threshold_multiplier=None, min_stats=None, verbose=True, **kwargs):
    """
    Backtest หุ้นเดียว พร้อมแสดงช่วงวันที่
    
    Risk Management (V7.0):
    - Stop Loss: 2% (ตัดขาดทุนไว)
    - Take Profit: 4% (ปล่อยกำไรวิ่ง)
    - Max Hold: 5 days (ไม่ถือนานเกิน)
    - RRR Target: 2.0 (TP/SL = 4/2)
    
    Returns:
        dict: ผล backtest รวมถึง date_from, date_to
    """
    if verbose:
        print(f"\n🔬 BACKTEST: {symbol} ({exchange})")
        print("=" * 50)
    
    max_retries = 3
    df = None
    
    # Get interval from kwargs (for intraday support)
    interval = kwargs.get('interval', Interval.in_daily)
    
    for attempt in range(max_retries):
        try:
            df = get_data_with_cache(
                tv=tv,
                symbol=symbol,
                exchange=exchange,
                interval=interval,
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
    
    # REMOVED: Indicators (V6.1 - Back to simple system)
    # System should be simple: just history pattern matching, no indicators
    
    # V4.2 Threshold Logic (Static Floors + Dynamic Base)
    is_us_market = any(ex in exchange.upper() for ex in ['NASDAQ', 'NYSE', 'US', 'CME', 'COMEX', 'NYMEX'])
    is_thai_market = any(ex in exchange.upper() for ex in ['SET', 'MAI', 'TH'])
    is_china_market = any(ex in exchange.upper() for ex in ['HKEX', 'SHSE', 'SZSE'])
    is_tw_market_early = any(ex in exchange.upper() for ex in ['TWSE', 'TW'])
    
    # ====== V10.0: BALANCED MARKET-SPECIFIC PARAMETERS ======
    # Optimized from grid search across 10 parameter combos per market
    # Key insight: thresh 0.9 + lower prob → 10-13x more trades, minimal acc loss
    # ====== V10.1: ALL MARKETS BALANCED ======
    # Thai updated: align with international V10.0 optimization
    # Key change: Thai thresh 1.25→1.0, floor 1.0%→0.7%, prob 55→53%, trailing ON
    # ====== V12.0: TAIWAN-SPECIFIC OPTIMIZATION ======
    # Taiwan separated from China/US for easier maintenance
    # Key changes: Lower threshold (0.85) and min_stats (20) to increase signals
    # ============================================================================
    # CHINA MARKET LOGIC - Separated for clarity and maintainability
    # ============================================================================
    if threshold_multiplier is None:
        if is_thai_market:
            threshold_multiplier = 1.0     # Thai V10.1: ลดจาก 1.25 → 1.0 (เพิ่มสัญญาณ)
        elif is_us_market:
            threshold_multiplier = 0.9     # US: sweet spot
        elif is_tw_market_early:
            threshold_multiplier = 0.9    # Taiwan V12.1: เพิ่มจาก 0.85 → 0.9 (ลดสัญญาณ, เพิ่มคุณภาพ)
        elif is_china_market:
            # China Market: Default threshold (can be overridden via kwargs)
            threshold_multiplier = kwargs.get('threshold_multiplier', 0.9)  # CN: sweet spot
        else:
            threshold_multiplier = 0.9     # Default fallback
    
    # Detect intraday timeframe (Metals: Gold/Silver 30min/15min) - MUST BE BEFORE min_stats check
    is_intraday = any(x in symbol.upper() for x in ['XAUUSD', 'XAGUSD', 'GOLD', 'SILVER']) or \
                  any(x in exchange.upper() for x in ['OANDA', 'FOREX'])
    
    if min_stats is None:
        if is_intraday:
            # Intraday 24h: เพิ่ม min_stats เพื่อเพิ่มความน่าเชื่อถือของ pattern (สมดุลระหว่าง Prob%, RRR และ Count)
            # แยก logic สำหรับ 15min และ 30min
            is_15min = kwargs.get('interval') == Interval.in_15_minute
            if is_15min:
                # สำหรับ Silver 15min ใช้ min_stats เพื่อเพิ่ม Prob%
                is_silver_15m = any(x in symbol.upper() for x in ['XAGUSD', 'SILVER'])
                if is_silver_15m:
                    min_stats = kwargs.get('min_stats', 40)  # Silver 15min: 40 (เพิ่มจาก 38 → 40 เพื่อลด Count และ balance กับ Gold)
                else:
                    min_stats = kwargs.get('min_stats', 32)  # Gold 15min: 32 (คงค่าเดิม)
            else:
                min_stats = kwargs.get('min_stats', 35)  # 30min: 35 (คงค่าเดิม)
        elif is_thai_market:
            min_stats = 25                 # Thai V10.1: ลดจาก 30 → 25
        elif is_us_market:
            min_stats = 20                 # US: relaxed
        elif is_tw_market_early:
            min_stats = 25                 # Taiwan V12.1: เพิ่มจาก 20 → 25 (ลด patterns, เพิ่มคุณภาพ)
        elif is_china_market:
            # China Market: Default min_stats (can be overridden via kwargs)
            # V13.7: เพิ่มจาก 25 → 30 (เพิ่มคุณภาพ, RRR 1.40)
            min_stats = kwargs.get('min_stats', 30)  # CN V13.7: เพิ่มจาก 25 → 30
        else:
            min_stats = 25                 # Default fallback
    
    # Define Floor based on market philosophy (V4.2 + V10.1 + V12.0)
    # Updated to match STRATEGY_TABLE_BY_COUNTRY.md (2026-02-13)
    current_floor = 0
    if is_intraday:
        # Intraday 24h: ใช้ floor ต่ำกว่า daily (0.1% สำหรับ Metals)
        current_floor = 0.001  # 0.1% (intraday มี volatility ต่ำกว่า daily)
    elif is_us_market: 
        current_floor = 0.006  # 0.6% (US)
    elif is_thai_market: 
        current_floor = 0.007  # 0.7% (THAI)
    elif is_tw_market_early: 
        current_floor = 0.005  # 0.5% (TAIWAN - Fixed to match documentation)
    elif is_china_market: 
        current_floor = 0.005  # 0.5% (CHINA/HK)
    
    # Calculate effective_std with appropriate rolling windows
    # For intraday 24h: ใช้ rolling window ที่เหมาะสมกับ intraday
    # แยก logic สำหรับ 15min และ 30min
    if is_intraday:
        # แยก logic สำหรับ 15min และ 30min
        is_15min = kwargs.get('interval') == Interval.in_15_minute
        if is_15min:
            # Intraday 15min: 96 bars/day, 672 bars/week (7 days * 96)
            # Short window: 96 bars (1 วัน) - ใช้ 1 วันสำหรับ short-term volatility
            # Long window: 672 bars (1 สัปดาห์) - ใช้ 1 สัปดาห์สำหรับ long-term volatility
            short_window = 96   # 1 วัน (24 ชั่วโมง / 15 นาที)
            long_window = 672   # 1 สัปดาห์ (7 วัน * 96 bars/day)
            if verbose:
                print(f"   📊 Intraday 15min: short_window={short_window}, long_window={long_window}")
        else:
            # Intraday 30min: 48 bars/day, 336 bars/week (7 days * 48)
            # Short window: 48 bars (1 วัน) - ใช้ 1 วันสำหรับ short-term volatility
            # Long window: 336 bars (1 สัปดาห์) - ใช้ 1 สัปดาห์สำหรับ long-term volatility
            short_window = 48   # 1 วัน (24 ชั่วโมง / 30 นาที)
            long_window = 336   # 1 สัปดาห์ (7 วัน * 48 bars/day)
            if verbose:
                print(f"   📊 Intraday 30min: short_window={short_window}, long_window={long_window}")
    else:
        # Daily: ใช้ rolling window แบบเดิม
        short_window = 20   # 20 วัน
        long_window = 252   # 252 วัน (~1 ปี)
    
    # Always calculate effective_std (needed for Hybrid Volatility strategy)
    short_std = pct_change.rolling(window=short_window).std()
    long_std = pct_change.rolling(window=long_window).std()
    effective_std = np.maximum(short_std, long_std.fillna(0))
    effective_std = np.maximum(effective_std, current_floor)
    
    if 'fixed_threshold' in kwargs and kwargs['fixed_threshold'] is not None:
         fixed_val = float(kwargs['fixed_threshold']) / 100.0
         threshold = pd.Series(fixed_val, index=pct_change.index)
         if verbose:
             print(f"   🔧 Using fixed_threshold: {kwargs['fixed_threshold']}% (={fixed_val})")
    else:
        # V4.2: Max(20d SD, 252d SD, Market Floor)
        threshold = effective_std * threshold_multiplier
        if verbose:
            print(f"   🔧 Using dynamic threshold (SD-based): multiplier={threshold_multiplier}")
            print(f"   ⚠️ WARNING: No fixed_threshold provided! Using dynamic threshold instead.")
    
    # Convert to +/- pattern (Base strings for window-based extraction)
    # Note: We keep the full list including None to maintain time-alignment
    raw_patterns = []
    for i in range(len(pct_change)):
        if pd.isna(pct_change.iloc[i]) or pd.isna(threshold.iloc[i]):
            raw_patterns.append(None)
        elif pct_change.iloc[i] > threshold.iloc[i]:
            raw_patterns.append('+')
        elif pct_change.iloc[i] < -threshold.iloc[i]:
            raw_patterns.append('-')
        else:
            raw_patterns.append(None)
    
    pattern_stats = {}
    MIN_LEN = 3 
    MAX_LEN = 8 # REVERTED: 14 was over-fitting. 8 is standard for high accuracy.
    
    # 1. TRAINING PHASE
    for i in range(MAX_LEN, train_end - 1):
        next_ret = pct_change.iloc[i+1]
        if pd.isna(next_ret): continue

        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0: continue
            
            # Optimized Window-based Pattern Extraction
            window_slice = raw_patterns[i-length+1 : i+1]
            pat = ''.join([p for p in window_slice if p is not None])
            
            if not pat: continue
            
            if pat not in pattern_stats:
                pattern_stats[pat] = []
            pattern_stats[pat].append(next_ret)
    
    # ====== V10.0: BALANCED SWEET SPOT PARAMETERS ======
    # Key Changes from V9.0:
    #   ✅ threshold_multiplier: 0.9 for international (was 1.25) → 10-13x more trades
    #   ✅ min_stats: 20 (US), 25 (TW/CN), 30 (Thai) → more patterns qualify
    #   ✅ Prob filter: 52% (US), 53% (TW/CN), 55% (Thai) → balanced accuracy
    #   ✅ Floor: 0.5% for TW/CN (was missing)
    #   ✅ All RM features kept: Trailing Stop, ATR, Position Sizing
    
    is_tw_market = any(ex in exchange.upper() for ex in ['TWSE', 'TW'])
    
    # Calculate ATR for all markets (needed for ATR-based RM)
    atr_series = calc_atr(high, low, close, period=14)
    
    # V9.0: Position Sizing - Risk 2% per trade
    RISK_PER_TRADE = kwargs.get('risk_per_trade', 0.02)  # 2% of capital
    
    # Market-specific RM parameters
    if is_tw_market:
        # ========================================================================
        # TAIWAN MARKET RISK MANAGEMENT - Separated for clarity and testing
        # ========================================================================
        # Taiwan: ATR-based SL/TP for Flexibility (Auto System)
        # - ATR-based SL/TP: ยืดหยุ่นตาม volatility ของแต่ละหุ้น
        #   - ATR SL 1.0x: หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ
        #   - ATR TP 3.5x: เป้าหมาย RRR 3.5 (ปรับจาก 6.5x → 3.5x - ให้ถึง TP ได้มากขึ้น)
        # - Max Hold: 10 days (ให้มีเวลาไปถึง TP)
        # - Trailing: Activate 2.0%, Distance 40% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        # - Target: RRR >= 1.2, Prob% >= 51%
        # - Updated to match STRATEGY_TABLE_BY_COUNTRY.md (2026-02-13)
        # 
        # ข้อดีของ ATR-based:
        #   ✅ ยืดหยุ่นตาม volatility (ไม่ lock AvgLoss% ไว้ที่ 1.0%)
        #   ✅ เอาไปใช้จริงง่าย (auto system)
        #   ✅ Realistic: ใช้ความผันผวนจริงของหุ้น
        # 
        # All parameters can be overridden via kwargs for testing:
        #   - atr_sl_mult: Override ATR SL multiplier
        #   - atr_tp_mult: Override ATR TP multiplier
        #   - max_hold: Override max hold days
        #   - trail_activate: Override trailing stop activation %
        #   - trail_distance: Override trailing stop distance %
        # ========================================================================
        RM_STOP_LOSS = None  # V12.5: Use ATR instead of fixed SL
        RM_TAKE_PROFIT = None  # V12.5: Use ATR instead of fixed TP
        RM_MAX_HOLD = kwargs.get('max_hold', 5)            # Revert: 5 days (ค่าที่เสถียร)
        RM_ATR_SL = kwargs.get('atr_sl_mult', 1.0)       # V12.5: ATR multiplier for SL (flexible)
        RM_ATR_TP = kwargs.get('atr_tp_mult', 3.5)       # ปรับจาก 6.5 → 3.5 (ให้ถึง TP ได้มากขึ้น - based on actual data: TP exits 0.1%)
        RM_USE_ATR = True  # V12.5: Enable ATR-based SL/TP
        RM_USE_TRAILING = True
        RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 2.0)   # ปรับจาก 1.0% → 2.0% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)  # ปรับจาก 30% → 40% (trail แน่นขึ้น - lock กำไรดีขึ้น)
    elif is_china_market:
        # ========================================================================
        # CHINA MARKET RISK MANAGEMENT - Separated for clarity and testing
        # ========================================================================
        # China/HK: ATR-based SL/TP for Flexibility (Auto System)
        # - ATR-based SL/TP: ยืดหยุ่นตาม volatility ของแต่ละหุ้น
        #   - ATR SL 1.0x: หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ
        #   - ATR TP 3.5x: เป้าหมาย RRR 3.5 (ปรับจาก 5.0x → 3.5x - ให้ถึง TP ได้มากขึ้น)
        # - Min Prob: 54.0% (Gatekeeper - คุณภาพสูง)
        # - Max Hold: 8 days (ให้มีเวลาไปถึง TP)
        # - Trailing: Activate 2.0%, Distance 40% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        # - Target: RRR >= 1.2, Prob% >= 54%
        # - Updated to match STRATEGY_TABLE_BY_COUNTRY.md (2026-02-13)
        # 
        # ข้อดีของ ATR-based:
        #   ✅ ยืดหยุ่นตาม volatility (ไม่ lock AvgLoss% ไว้ที่ 1.0%)
        #   ✅ เอาไปใช้จริงง่าย (auto system)
        #   ✅ Realistic: ใช้ความผันผวนจริงของหุ้น
        # 
        # All parameters can be overridden via kwargs for testing:
        #   - atr_sl_mult: Override ATR SL multiplier
        #   - atr_tp_mult: Override ATR TP multiplier
        #   - max_hold: Override max hold days
        #   - trail_activate: Override trailing stop activation %
        #   - trail_distance: Override trailing stop distance %
        # ========================================================================
        RM_STOP_LOSS = None  # V13.5: Use ATR instead of fixed SL
        RM_TAKE_PROFIT = None  # V13.5: Use ATR instead of fixed TP
        RM_MAX_HOLD = kwargs.get('max_hold', 5)            # Revert: 5 days (ค่าที่เสถียร)
        RM_ATR_SL = kwargs.get('atr_sl_mult', 1.0)       # V13.5: ATR multiplier for SL (flexible)
        RM_ATR_TP = kwargs.get('atr_tp_mult', 3.5)       # ปรับจาก 5.0x → 3.5x (ให้ถึง TP ได้มากขึ้น - based on actual data: TP exits 0.0%)
        RM_USE_ATR = True  # V13.5: Enable ATR-based SL/TP
        RM_USE_TRAILING = True
        RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 2.0)   # ปรับจาก 1.0% → 2.0% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)  # V13.5: Keep at 40% (let profits run)
    elif is_us_market:
        # ========================================================================
        # US MARKET RISK MANAGEMENT - Separated for clarity and testing
        # ========================================================================
        # US: ATR-based SL/TP for Flexibility (Auto System)
        # - ATR-based SL/TP: ยืดหยุ่นตาม volatility ของแต่ละหุ้น
        #   - ATR SL 1.0x: หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ
        #   - ATR TP 3.5x: เป้าหมาย RRR 3.5 (ปรับจาก 5.0x → 3.5x - ให้ถึง TP ได้มากขึ้น)
        # - Max Hold: 7 days (เพิ่มจาก 5 → 7 days - ให้มีเวลาไปถึง TP)
        # - Trailing: Activate 2.0%, Distance 40% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        # - Target: RRR >= 1.2, Prob% >= 52%, AvgWin > AvgLoss (Quality Filter)
        # - Updated to match STRATEGY_TABLE_BY_COUNTRY.md (2026-02-13)
        # 
        # ข้อดีของ ATR-based:
        #   ✅ ยืดหยุ่นตาม volatility (ไม่ lock AvgLoss% ไว้ที่ 1.5%)
        #   ✅ เอาไปใช้จริงง่าย (auto system)
        #   ✅ Realistic: ใช้ความผันผวนจริงของหุ้น
        # 
        # All parameters can be overridden via kwargs for testing:
        #   - atr_sl_mult: Override ATR SL multiplier
        #   - atr_tp_mult: Override ATR TP multiplier
        #   - max_hold: Override max hold days
        #   - trail_activate: Override trailing stop activation %
        #   - trail_distance: Override trailing stop distance %
        # ========================================================================
        RM_STOP_LOSS = None  # V10.1: Use ATR instead of fixed SL
        RM_TAKE_PROFIT = None  # V10.1: Use ATR instead of fixed TP
        RM_MAX_HOLD = kwargs.get('max_hold', 5)            # Revert: 5 days (ค่าที่เสถียร)
        RM_ATR_SL = kwargs.get('atr_sl_mult', 1.0)       # V10.1: ATR multiplier for SL (flexible)
        RM_ATR_TP = kwargs.get('atr_tp_mult', 3.5)       # ปรับจาก 5.0x → 3.5x (ให้ถึง TP ได้มากขึ้น - based on actual data: TP exits 0.0%)
        RM_USE_ATR = True  # V10.1: Enable ATR-based SL/TP
        RM_USE_TRAILING = True
        RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 2.0)   # ปรับจาก 1.5% → 2.0% (activate ช้าลง - ให้มีเวลาไปถึง TP)
        RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 40.0)  # ปรับจาก 50% → 40% (trail แน่นขึ้น - lock กำไรดีขึ้น)
    else:
        # ========================================================================
        # THAI MARKET RISK MANAGEMENT - Separated for clarity and testing
        # ========================================================================
        # Thai: ATR-based SL/TP for Flexibility (Auto System)
        # - ATR-based SL/TP: ยืดหยุ่นตาม volatility ของแต่ละหุ้น
        #   - ATR SL 1.0x: หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ
        #   - ATR TP 3.5x: เป้าหมาย RRR 3.5 (เหมือนเดิม - theoretical RRR 3.5)
        # - Max Hold: 5 days (คงเดิม)
        # - Trailing: Activate 1.5%, Distance 50% (lock กำไร)
        # - Target: RRR >= 1.2, Prob% >= 53%
        # - Updated: เปลี่ยนจาก Fixed SL/TP → ATR-based เพื่อให้ AvgLoss% ยืดหยุ่นขึ้น
        # 
        # ข้อดีของ ATR-based:
        #   ✅ ยืดหยุ่นตาม volatility (ไม่ lock AvgLoss% ไว้ที่ 1.5%)
        #   ✅ เอาไปใช้จริงง่าย (auto system)
        #   ✅ Realistic: ใช้ความผันผวนจริงของหุ้น
        # 
        # All parameters can be overridden via kwargs for testing:
        #   - atr_sl_mult: Override ATR SL multiplier
        #   - atr_tp_mult: Override ATR TP multiplier
        #   - max_hold: Override max hold days
        #   - trail_activate: Override trailing stop activation %
        #   - trail_distance: Override trailing stop distance %
        # ========================================================================
        # Intraday: ใช้ max_hold เป็น bars แทน days (30min: 48 bars/day, 15min: 96 bars/day)
        # แยก logic สำหรับ 15min และ 30min
        if is_intraday:
            # แยก logic สำหรับ 15min และ 30min
            is_15min = kwargs.get('interval') == Interval.in_15_minute
            if is_15min:
                # Intraday 15min: 96 bars = 1 วัน (24 ชั่วโมง / 15 นาที)
                # แต่สำหรับ intraday ควร hold น้อยกว่า (1 วัน = 96 bars)
                RM_MAX_HOLD = kwargs.get('max_hold', 96)  # Intraday 15min: 96 bars (1 วัน)
                if verbose:
                    print(f"   🔧 Intraday 15min: RM_MAX_HOLD={RM_MAX_HOLD} bars (1 วัน)")
            else:
                # Intraday 30min: 48 bars = 1 วัน (24 ชั่วโมง / 30 นาที)
                # แต่สำหรับ intraday ควร hold น้อยกว่า (1 วัน = 48 bars)
                RM_MAX_HOLD = kwargs.get('max_hold', 48)  # Intraday 30min: 48 bars (1 วัน)
                if verbose:
                    print(f"   🔧 Intraday 30min: RM_MAX_HOLD={RM_MAX_HOLD} bars (1 วัน)")
        else:
            RM_MAX_HOLD = kwargs.get('max_hold', 5)  # Daily: 5 days
        
        RM_STOP_LOSS = None  # Use ATR instead of fixed SL
        RM_TAKE_PROFIT = None  # Use ATR instead of fixed TP
        RM_ATR_SL = kwargs.get('atr_sl_mult', 1.0)       # ATR multiplier for SL (flexible)
        
        # Gold 15min: เพิ่ม ATR TP multiplier เพื่อเพิ่ม RRR ใกล้ 1.5
        if is_intraday and kwargs.get('interval') == Interval.in_15_minute:
            is_gold_15m = any(x in symbol.upper() for x in ['XAUUSD', 'GOLD'])
            if is_gold_15m:
                RM_ATR_TP = kwargs.get('atr_tp_mult', 4.5)  # Gold 15min: 4.5 (เพิ่มจาก 3.5 → 4.5 เพื่อเพิ่ม RRR ใกล้ 1.5)
                if verbose:
                    print(f"   🔧 Gold 15min: RM_ATR_TP={RM_ATR_TP} (เพิ่ม RRR)")
            else:
                RM_ATR_TP = kwargs.get('atr_tp_mult', 3.5)  # Silver 15min: 3.5 (คงค่าเดิม)
        else:
            RM_ATR_TP = kwargs.get('atr_tp_mult', 3.5)  # Default: 3.5
        
        RM_USE_ATR = True  # Enable ATR-based SL/TP
        RM_USE_TRAILING = True
        RM_TRAIL_ACTIVATE = kwargs.get('trail_activate', 1.5)   # Activate at 1.5%
        RM_TRAIL_DISTANCE = kwargs.get('trail_distance', 50.0)  # Distance 50%
    
    use_risk_mgmt = kwargs.get('use_risk_mgmt', True)
    
    # ====== V11.0: PRODUCTION MODE ======
    production_mode = kwargs.get('production', False)
    market_key = get_market_key(exchange)
    prod_slippage = SLIPPAGE_PCT.get(market_key, SLIPPAGE_PCT['DEFAULT']) if production_mode else 0.0
    prod_commission = COMMISSION_PCT.get(market_key, COMMISSION_PCT['DEFAULT']) if production_mode else 0.0
    prod_gap_risk = GAP_RISK_FACTOR.get(market_key, GAP_RISK_FACTOR['DEFAULT']) if production_mode else 1.0
    prod_min_volume = MIN_VOLUME.get(market_key, MIN_VOLUME['DEFAULT']) if production_mode else 0
    
    if verbose and production_mode:
        print(f"\n   [PRODUCTION MODE] Slippage: {prod_slippage}% | Commission: {prod_commission}% | Gap Risk: {prod_gap_risk}x | Min Volume: {prod_min_volume:,}")
    
    # Pre-calculate average volume for liquidity filter
    avg_volume = volume.rolling(20).mean() if production_mode else None
    
    # SMA for Regime-Aware Direction (Hybrid Strategy)
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    
    # 2. TESTING PHASE
    total_predictions = 0
    correct_predictions = 0
    predictions = []
    skipped_low_volume = 0
    
    # Set min_prob ก่อน loop เพื่อหลีกเลี่ยงการ set ซ้ำๆ (แก้บัค debug print ซ้ำ)
    # Intraday 24h: เพิ่ม min_prob เพื่อเน้น Prob% และ RRR (สมดุลกับ Count)
    # แยก logic สำหรับ 15min และ 30min
    if is_intraday:
        is_15min = kwargs.get('interval') == Interval.in_15_minute
        if is_15min:
            # สำหรับ Silver 15min ใช้ min_prob สูงขึ้นเพื่อเพิ่ม Prob%
            is_silver_15m = any(x in symbol.upper() for x in ['XAGUSD', 'SILVER'])
            if is_silver_15m:
                min_prob = kwargs.get('min_prob', 60.0)  # Silver 15min: 60% (เพิ่มจาก 58% → 60% เพื่อลด Count และ balance กับ Gold)
                if verbose:
                    print(f"   🔧 Silver 15min: min_prob={min_prob}%, min_stats={min_stats}")
            else:
                min_prob = kwargs.get('min_prob', 50.0)  # Gold 15min: 50% (ลดจาก 53% → 50% เพื่อให้มี trades)
                if verbose:
                    print(f"   🔧 Gold 15min: min_prob={min_prob}%, min_stats={min_stats}")
        else:
            # 30min: ใช้ค่าเดิม (ไม่แก้ไข)
            min_prob = kwargs.get('min_prob', 58.0)  # 30min: 58% (คงค่าเดิม)
            if verbose:
                print(f"   🔧 Intraday 30min: min_prob={min_prob}%, min_stats={min_stats}")
    elif is_us_market:
        min_prob = 52.0
    elif is_tw_market:
        min_prob = 51.0  # Taiwan V12.4: ลดจาก 51.5% → 51.0%
    elif is_china_market:
        min_prob = kwargs.get('min_prob', 54.0)  # V13.9: 54.0%
    else:  # Thai
        min_prob = 53.0
    
    for i in range(train_end, len(df) - RM_MAX_HOLD - 1):
        
        # V11.0: Liquidity filter - skip low-volume days in production mode
        if production_mode and avg_volume is not None:
            vol_at_signal = avg_volume.iloc[i]
            if not pd.isna(vol_at_signal) and vol_at_signal < prod_min_volume:
                skipped_low_volume += 1
                continue
        
        # Determine Potential Direction upfront (Pillar 0)
        # V7.0: Hybrid Strategy based on market type
        intended_dir = 0
        
        # Get last pattern
        window_slice = raw_patterns[i-MAX_LEN+1 : i+1] if i-MAX_LEN+1 >= 0 else raw_patterns[:i+1]
        last_pats = [p for p in window_slice if p is not None]
        
        if not last_pats:
            continue
        
        last_directional = last_pats[-1]
        
        if is_thai_market or is_china_market:
            # Mean Reversion Logic (เหมือนเดิม - ดีอยู่แล้ว)
            if last_directional == '+': intended_dir = -1
            elif last_directional == '-': intended_dir = 1
        
        elif is_us_market:
            # V7.0 Hybrid Volatility Strategy for US
            # HIGH_VOL → REVERSION (fade the spike)
            # LOW_VOL → TREND (ride momentum)
            avg_vol = effective_std.iloc[max(0, i-20):i+1].mean()
            current_vol = effective_std.iloc[i]
            
            if current_vol > avg_vol * 1.2:  # HIGH_VOL
                if last_directional == '+': intended_dir = -1
                elif last_directional == '-': intended_dir = 1
            else:  # LOW_VOL → TREND
                if last_directional == '+': intended_dir = 1
                elif last_directional == '-': intended_dir = -1
        
        elif is_tw_market:
            # Taiwan: Regime-Aware (BULL → TREND, BEAR/SIDEWAYS → REVERSION)
            c_sma50 = sma50.iloc[i]
            c_sma200 = sma200.iloc[i] if not pd.isna(sma200.iloc[i]) else close.iloc[i]
            
            if not pd.isna(c_sma50) and close.iloc[i] > c_sma50 and c_sma50 > c_sma200:
                # BULL → TREND
                if last_directional == '+': intended_dir = 1
                elif last_directional == '-': intended_dir = -1
            else:
                # BEAR/SIDEWAYS → REVERSION
                if last_directional == '+': intended_dir = -1
                elif last_directional == '-': intended_dir = 1
        
        elif is_intraday:
            # Intraday Metals: แยก logic ตาม engine จาก config
            # Gold: TREND_FOLLOWING (Breakout ตาม Session - Flow เงินเข้าชัดเจนช่วงเปิดตลาด)
            # Silver: MEAN_REVERSION (Fakeout - High Volatility, False Break บ่อย)
            engine = kwargs.get('engine', 'MEAN_REVERSION')
            if engine == "TREND_FOLLOWING":
                # Gold: Breakout Logic - ตาม momentum (เหมาะกับพฤติกรรมของทอง)
                if last_directional == '+': intended_dir = 1
                elif last_directional == '-': intended_dir = -1
            else:
                # Silver: Mean Reversion/Fakeout - สวนเทรนด์เมื่อหมดแรง (เหมาะกับพฤติกรรมของเงิน)
                if last_directional == '+': intended_dir = -1
                elif last_directional == '-': intended_dir = 1
        else:
            # Default: Mean Reversion
            if last_directional == '+': intended_dir = -1
            elif last_directional == '-': intended_dir = 1
        
        if intended_dir == 0: continue

        candidate_pats = []
        for length in range(MIN_LEN, MAX_LEN + 1):
            if i - length + 1 < 0: continue
            
            window_slice = raw_patterns[i-length+1 : i+1]
            pat = ''.join([p for p in window_slice if p is not None])
            if not pat or pat not in pattern_stats: continue
            
            hist_returns = pattern_stats[pat]
            total = len(hist_returns)
            if total < min_stats: continue
            
            # Calculate stats for the TRADED direction specifically
            if intended_dir == 1:
                wins = [abs(r) for r in hist_returns if r > 0]
                losses = [abs(r) for r in hist_returns if r <= 0]
            else: # intended_dir == -1
                wins = [abs(r) for r in hist_returns if r < 0]
                losses = [abs(r) for r in hist_returns if r >= 0]
            
            win_count = len(wins)
            cand_prob = (win_count / total) * 100
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            rr = avg_win / avg_loss if avg_loss > 0 else 0
            p_win = win_count / total
            expectancy = p_win * avg_win - (1 - p_win) * avg_loss

            # 🔒 V10.1 BALANCED GATEKEEPER (All Markets Aligned)
            # Thai: Prob >= 53% (V10.1: ลดจาก 55% → 53% เพิ่มสัญญาณ)
            # US:   Prob >= 52% + Quality filter
            # TW:   Prob >= 51% (V12.0: ลดจาก 53% → 51% เพิ่มสัญญาณ)
            # CN:   Prob >= 53%
            # Intraday: Prob >= 50% (ต่ำกว่า daily เพราะ intraday มี noise มากกว่า)
            # All:  Expectancy > 0 (must be +EV)
            # Note: min_prob ถูก set แล้วก่อน loop (บรรทัด 743-770) ไม่ต้อง set ใหม่ใน loop นี้
            
            if cand_prob < min_prob or expectancy <= 0:
                continue
            
            # US Quality Filter: AvgWin must be > AvgLoss (key differentiator)
            if is_us_market and avg_win <= avg_loss:
                continue
            
            candidate_pats.append({
                'length': length,
                'pattern': pat,
                'prob': cand_prob,
                'dir': intended_dir,
                'rr': rr,
                'exp': expectancy
            })
        
        if not candidate_pats:
            continue
            
        # Pick the best match prioritizing PROBABILITY (Win Rate)
        best_match = sorted(
            candidate_pats,
            key=lambda x: (x['prob'], x['exp'], x['length']),
            reverse=True
        )[0]
        
        final_dir = best_match['dir']
        final_forecast = "UP" if final_dir == 1 else "DOWN"
        confidence = best_match['prob']
        
        if is_us_market:
            strategy = "US_HYBRID_VOL"
        elif is_thai_market or is_china_market:
            strategy = "MEAN_REVERSION"
        else:
            strategy = "REGIME_AWARE"

        # ====== V9.0: Balanced Risk-Managed Exit ======
        # All markets: Trailing Stop + Position Sizing
        # Taiwan: ATR 1.0x SL / 6.5x TP (V12.5: flexible, auto system) + Trailing
        # China/HK: ATR 1.0x SL / 4.0x TP (V13.5: flexible, auto system) + Trailing
        # US: ATR 1.0x SL / 5.0x TP (V10.1: flexible, auto system) + Trailing + Quality filter
        # Thai: Fixed SL 1.5% / TP 3.5% + Trailing
        
        if use_risk_mgmt:
            # V11.0: Common production parameters for all RM calls
            prod_params = dict(
                production_mode=production_mode,
                slippage_pct=prod_slippage,
                commission_pct=prod_commission,
                gap_risk=prod_gap_risk
            )
            
            # Debug: Check ATR availability for Thai market
            if is_thai_market and verbose and i == train_end:
                print(f"   [DEBUG] RM_USE_ATR: {RM_USE_ATR}, atr_series is not None: {atr_series is not None}")
                if atr_series is not None:
                    print(f"   [DEBUG] ATR series length: {len(atr_series)}, non-null count: {atr_series.notna().sum()}")
                    if i < len(atr_series):
                        print(f"   [DEBUG] ATR at index {i}: {atr_series.iloc[i] if not pd.isna(atr_series.iloc[i]) else 'NaN'}")
            
            if RM_USE_ATR and atr_series is not None:
                trade_result = simulate_trade_with_rm(
                    df, i, final_dir,
                    max_hold_days=RM_MAX_HOLD,
                    atr_series=atr_series,
                    atr_sl_mult=RM_ATR_SL,
                    atr_tp_mult=RM_ATR_TP,
                    use_trailing_stop=RM_USE_TRAILING,
                    trail_activation_pct=RM_TRAIL_ACTIVATE,
                    trail_distance_pct=RM_TRAIL_DISTANCE,
                    **prod_params
                )
            else:
                # Fallback to fixed SL/TP if ATR not available or RM_USE_ATR is False
                if RM_USE_ATR and (atr_series is None or RM_STOP_LOSS is None):
                    # ATR-based requested but ATR not available or RM_STOP_LOSS is None - use fallback fixed values
                    if is_thai_market:
                        # Use original fixed values as fallback for Thai market
                        fallback_sl = 1.5
                        fallback_tp = 3.5
                    else:
                        fallback_sl = 1.5
                        fallback_tp = 3.5
                else:
                    # Use provided fixed values
                    fallback_sl = RM_STOP_LOSS if RM_STOP_LOSS is not None else 1.5
                    fallback_tp = RM_TAKE_PROFIT if RM_TAKE_PROFIT is not None else 3.5
                
                trade_result = simulate_trade_with_rm(
                    df, i, final_dir,
                    stop_loss_pct=fallback_sl,
                    take_profit_pct=fallback_tp,
                    max_hold_days=RM_MAX_HOLD,
                    use_trailing_stop=RM_USE_TRAILING,
                    trail_activation_pct=RM_TRAIL_ACTIVATE,
                    trail_distance_pct=RM_TRAIL_DISTANCE,
                    **prod_params
                )
            
            raw_return_pct = trade_result['return_pct']
            # V13.5: For ATR-based, sl_used is the actual SL% calculated from ATR
            sl_used = trade_result.get('sl_used', RM_STOP_LOSS if RM_STOP_LOSS is not None else 1.0)
            exit_reason = trade_result['exit_reason']
            hold_days = trade_result['hold_days']
            
            # V9.0: Position Sizing - Scale return by position size
            # Risk 2% of capital per trade → position_pct = risk / SL
            if sl_used > 0:
                position_pct = min(RISK_PER_TRADE / (sl_used / 100), 1.0)
            else:
                position_pct = 1.0
            trader_return_pct = raw_return_pct * position_pct
        else:
            # Fallback: simple 1-day exit
            next_ret = pct_change.iloc[i+1] if i+1 < len(df) else 0
            trader_return_pct = next_ret * 100 * final_dir
            exit_reason = '1DAY'
            hold_days = 1
            position_pct = 1.0
            raw_return_pct = trader_return_pct
        
        # Determine correctness based on return
        is_correct = 1 if trader_return_pct > 0 else 0
        actual_label = 'UP' if trader_return_pct > 0 else 'DOWN'

        total_predictions += 1
        correct_predictions += is_correct

        predictions.append({
            'date': df.index[i],
            'pattern': best_match['pattern'],
            'forecast': final_forecast,
            'prob': confidence,
            'actual': actual_label,
            'actual_return': raw_return_pct,        # Raw trade return (before sizing)
            'trader_return': trader_return_pct,      # Position-sized return
            'correct': is_correct,
            'strategy': strategy,
            'exit_reason': exit_reason,
            'hold_days': hold_days,
            'position_pct': round(position_pct * 100, 1)  # V9.0: Position size %
        })
    
    if verbose and production_mode and skipped_low_volume > 0:
        print(f"   [PRODUCTION] Skipped {skipped_low_volume} signals due to low volume")
    
    if total_predictions == 0:
        if verbose:
            print(f"❌ No signals passed filters (Prob >= {min_prob}%, Expectancy > 0)")
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
            'test_date_to': test_date_to,
            'production_mode': production_mode
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
    
    result.update({
        'avg_win': round(avg_win, 5), 
        'avg_loss': round(avg_loss, 5), 
        'risk_reward': round(rrr, 2),
        'production_mode': production_mode,
        'skipped_low_volume': skipped_low_volume if production_mode else 0
    })
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
    cols = ['date', 'symbol', 'exchange', 'group', 'pattern', 'forecast', 'prob', 'actual', 'actual_return', 'trader_return', 'correct', 'strategy', 'exit_reason', 'hold_days', 'position_pct']
    
    # Filter only existing columns to avoid errors if some keys are missing
    # Add missing columns with None
    for c in cols:
        if c not in df_trades.columns:
            df_trades[c] = None
            
    df_trades = df_trades[cols]
    
    # Overwrite mode for specific files (Metals 15min/30min) to avoid duplicate data
    # Append mode for other files (to accumulate all trades)
    is_metals_file = 'METALS' in filename.upper() and ('15M' in filename.upper() or '30M' in filename.upper())
    
    if is_metals_file:
        # Overwrite mode for Metals files (to avoid duplicate data when re-running backtest)
        df_trades.to_csv(log_path, mode='w', index=False, header=True)
        print(f"\n💾 Saved Trade Logs (OVERWRITE): {log_path} ({len(df_trades)} trades)")
    else:
    # Append mode with header only if file does not exist
    header = not os.path.exists(log_path)
    df_trades.to_csv(log_path, mode='a', index=False, header=header)
        print(f"\n💾 Saved Trade Logs (APPEND): {log_path} ({len(df_trades)} trades)")


def backtest_all(n_bars=200, skip_intraday=True, full_scan=False, target_group=None, threshold_multiplier=None, production=False, fast_mode=False, **kwargs):
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

    # Load existing results to skip already-processed symbols (works for both --group and no --group)
    # This saves time by not re-running backtests for symbols that already have results
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file, on_bad_lines='skip', engine='python')
            if 'symbol' in df_existing.columns:
                # If target_group is specified, only skip symbols from that group
                if target_group:
                    # Filter by group if available
                    if 'group' in df_existing.columns:
                        group_filter = df_existing['group'].str.upper().str.contains(target_group.upper(), na=False)
                        processed_symbols = set(df_existing[group_filter]['symbol'].tolist())
                    else:
                        # No group column, skip all existing symbols (conservative)
                        processed_symbols = set(df_existing['symbol'].tolist())
                else:
                    # No target_group, skip all existing symbols
                    processed_symbols = set(df_existing['symbol'].tolist())
                
                if processed_symbols:
                    print(f"📦 Found {len(processed_symbols)} existing results. Will skip these symbols...")
        except Exception as e:
            print(f"⚠️ Warning: Could not load existing results: {e}")
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

        # Filter out already processed symbols
        new_assets = [a for a in target_assets if a['symbol'] not in processed_symbols]
        skipped_count = len(target_assets) - len(new_assets)
        
        if skipped_count > 0:
            print(f"   ⏭️ Skipping {skipped_count} already processed symbols")
        
        if not new_assets:
            print(f"   ✅ All symbols already processed. No new symbols to test.")
            continue

        print(f"   📊 Processing {len(new_assets)} new symbols...")
        
        for i, asset in enumerate(new_assets):
            symbol = asset['symbol']
            exchange = asset['exchange']
            
            print(f"   [{i+1}/{len(new_assets)}] {symbol}...", end=" ")
            
            # Retry Logic with Exponential Backoff
            max_retries = 5 
            result = None
            success = False
            
            for attempt in range(max_retries):
                try:
                    fixed_thresh = group_config.get('fixed_threshold')
                    inverse_log = group_config.get('inverse_logic', False)
                    min_adx_val = group_config.get('min_adx')
                    # Pass all kwargs through (for China market testing: stop_loss, take_profit, max_hold, etc.)
                    result = backtest_single(tv, symbol, exchange, n_bars=n_bars, verbose=False, fixed_threshold=fixed_thresh, inverse_logic=inverse_log, threshold_multiplier=threshold_multiplier, min_adx=min_adx_val, production=production, **kwargs)
                    
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
                    # Also check group_config description for better matching
                    group_desc = group_config.get('description', '').upper()
                    if 'US' in group_clean or 'US' in group_desc: file_suffix = 'US'
                    elif 'THAI' in group_clean or 'THAI' in group_desc: file_suffix = 'THAI'
                    elif 'CHINA' in group_clean or 'HK' in group_clean or 'CHINA' in group_desc or 'HK' in group_desc: file_suffix = 'CHINA'
                    elif 'TAIWAN' in group_clean or 'TAIWAN' in group_desc: file_suffix = 'TAIWAN'
                    elif 'GOLD' in group_clean or 'SILVER' in group_clean or 'METAL' in group_clean: file_suffix = 'METALS'
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
            
            # Market-Specific Delays (reduced in fast mode)
            is_china = any(ex in exchange.upper() for ex in ['SHSE', 'SZSE', 'CHINA'])
            if fast_mode:
                base_delay = 0.3 if is_china else 0.2  # Much faster in fast mode
            else:
                base_delay = 3.0 if is_china else 1.0  # Normal delays
            time.sleep(base_delay)
    
    # Summary
    print("\n" + "=" * 70)
    if all_results:
        # Save Trade Logs using helper
        save_trade_logs(all_trades)
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
    
    parser.add_argument('--multiplier', type=float, default=None, help='Threshold multiplier (default: auto per market)')
    parser.add_argument('--production', action='store_true', 
                        help='Enable PRODUCTION mode: adds slippage, commission, gap risk, volume filter, entry at open')
    parser.add_argument('--fast', action='store_true',
                        help='Fast mode: reduce delays between requests (may risk rate limiting)')
    
    # China Market Testing Parameters
    parser.add_argument('--stop_loss', type=float, default=None, help='Override stop loss percent for testing')
    parser.add_argument('--take_profit', type=float, default=None, help='Override take profit percent for testing')
    parser.add_argument('--max_hold', type=int, default=None, help='Override max hold days for testing')
    parser.add_argument('--trail_activate', type=float, default=None, help='Override trailing stop activation percent for testing')
    parser.add_argument('--trail_distance', type=float, default=None, help='Override trailing stop distance percent for testing')
    parser.add_argument('--min_prob', type=float, default=None, help='Override min_prob percent for gatekeeper for testing')
    parser.add_argument('--min_stats', type=int, default=None, help='Override min_stats minimum pattern occurrences for testing')
    parser.add_argument('--atr_tp_mult', type=float, default=None, help='Override ATR TP multiplier for testing')
    parser.add_argument('--atr_sl_mult', type=float, default=None, help='Override ATR SL multiplier for testing')
    
    args = parser.parse_args()
    
    n_bars = args.bars
    threshold_multiplier = args.multiplier
    production_mode = args.production
    
    if production_mode:
        print("\n" + "!" * 70)
        print("  PRODUCTION MODE ENABLED - Realistic trading friction applied")
        print("  Slippage + Commission + Gap Risk + Volume Filter + Entry at Open")
        print("!" * 70)
    
    fast_mode = args.fast
    
    # Build kwargs for China market testing
    test_kwargs = {}
    if args.stop_loss is not None:
        test_kwargs['stop_loss'] = args.stop_loss
    if args.take_profit is not None:
        test_kwargs['take_profit'] = args.take_profit
    if args.max_hold is not None:
        test_kwargs['max_hold'] = args.max_hold
    if args.trail_activate is not None:
        test_kwargs['trail_activate'] = args.trail_activate
    if args.trail_distance is not None:
        test_kwargs['trail_distance'] = args.trail_distance
    if args.min_prob is not None:
        test_kwargs['min_prob'] = args.min_prob
    if args.min_stats is not None:
        test_kwargs['min_stats'] = args.min_stats
    if args.atr_tp_mult is not None:
        test_kwargs['atr_tp_mult'] = args.atr_tp_mult
    if args.atr_sl_mult is not None:
        test_kwargs['atr_sl_mult'] = args.atr_sl_mult
    if args.multiplier is not None:
        test_kwargs['threshold_multiplier'] = args.multiplier
        # Don't pass threshold_multiplier separately if it's in test_kwargs to avoid duplicate
        threshold_multiplier = None
    
    if args.full:
        # Full Scan Mode
        print(f"🚀 Running FULL SCAN on market (Bars: {n_bars}, Group: {args.group})")
        if fast_mode:
            print("⚡ FAST MODE: Reduced delays (may risk rate limiting)")
        if test_kwargs:
            print(f"🔧 Custom Parameters: {test_kwargs}")
        # Remove threshold_multiplier from test_kwargs if it exists to avoid duplicate
        call_kwargs = test_kwargs.copy()
        if 'threshold_multiplier' in call_kwargs:
            call_kwargs.pop('threshold_multiplier')
        all_results = backtest_all(n_bars=n_bars, full_scan=True, target_group=args.group, threshold_multiplier=test_kwargs.get('threshold_multiplier', threshold_multiplier), production=production_mode, fast_mode=fast_mode, **call_kwargs)
        
    elif args.all:
        # Sample Scan Mode
        print(f"🚀 Running SAMPLE SCAN on all stocks (Bars: {n_bars}, Group: {args.group})")
        if fast_mode:
            print("⚡ FAST MODE: Reduced delays (may risk rate limiting)")
        if test_kwargs:
            print(f"🔧 Custom Parameters: {test_kwargs}")
        # Remove threshold_multiplier from test_kwargs if it exists to avoid duplicate
        call_kwargs = test_kwargs.copy()
        if 'threshold_multiplier' in call_kwargs:
            call_kwargs.pop('threshold_multiplier')
        all_results = backtest_all(n_bars=n_bars, full_scan=False, target_group=args.group, threshold_multiplier=test_kwargs.get('threshold_multiplier', threshold_multiplier), production=production_mode, fast_mode=fast_mode, **call_kwargs)
        
    elif args.quick:
        # Quick Test Mode
        default_stocks = [
            ('PTT', 'SET'),
            ('ADVANC', 'SET'),
            ('NVDA', 'NASDAQ'),
            ('AAPL', 'NASDAQ'),
            ('2330', 'TWSE'),    # TSMC (Taiwan)
            ('700', 'HKEX'),     # Tencent (China/HK)
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
            result = backtest_single(tv, symbol, exchange, n_bars=n_bars, threshold_multiplier=threshold_multiplier, production=production_mode, **test_kwargs)
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
            print(f"📋 Risk Management: Market-Specific V8.0")
            print(f"   🇺🇸 US: SL 1.5% / TP 4.5% + Quality Filter (AvgWin > AvgLoss)")
            print(f"   🇹🇼 Taiwan: ATR 1.5x SL / 3x TP (dynamic)")
            print(f"   🇨🇳 China/HK: SL 1% / TP 3% (tight cut)")
            print(f"   🇹🇭 Thai: SL 2% / TP 4% (standard)")
            
            total_preds = sum(r['total'] for r in results)
            total_correct = sum(r['correct'] for r in results)
            avg_accuracy = total_correct / total_preds * 100 if total_preds > 0 else 0
            
            print(f"\n{'Symbol':<12} {'Exchange':<10} {'Total':<8} {'Win':<8} {'Accuracy':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<8} {'Return%':<10}")
            print("-" * 100)
            for r in results:
                total_ret = sum(p['trader_return'] for p in r.get('detailed_predictions', [])) if 'detailed_predictions' in r else 0
                print(f"{r['symbol']:<12} {r['exchange']:<10} {r['total']:<8} {r['correct']:<8} {r['accuracy']:.1f}%      {r['avg_win']:<10.2f} {r['avg_loss']:<10.2f} {r['risk_reward']:<8.2f} {total_ret:<10.2f}")
            print("-" * 100)
            
            total_avg_win = sum(r['avg_win'] for r in results) / len(results) if results else 0
            total_avg_loss = sum(r['avg_loss'] for r in results) / len(results) if results else 0
            total_rrr = total_avg_win / total_avg_loss if total_avg_loss > 0 else 0
            total_return = sum(sum(p['trader_return'] for p in r.get('detailed_predictions', [])) for r in results if 'detailed_predictions' in r)
            
            print(f"{'TOTAL':<12} {'':<10} {total_preds:<8} {total_correct:<8} {avg_accuracy:.1f}%      {total_avg_win:<10.2f} {total_avg_loss:<10.2f} {total_rrr:<8.2f} {total_return:<10.2f}")
            
            # Exit Reason Breakdown
            all_preds = []
            for r in results:
                if 'detailed_predictions' in r:
                    all_preds.extend(r['detailed_predictions'])
            
            if all_preds:
                exit_reasons = {}
                for p in all_preds:
                    reason = p.get('exit_reason', '1DAY')
                    if reason not in exit_reasons:
                        exit_reasons[reason] = {'count': 0, 'wins': 0, 'total_return': 0}
                    exit_reasons[reason]['count'] += 1
                    exit_reasons[reason]['wins'] += 1 if p['correct'] == 1 else 0
                    exit_reasons[reason]['total_return'] += p['trader_return']
                
                print(f"\n📊 Exit Reason Breakdown:")
                print(f"   {'Reason':<15} {'Count':<8} {'Win%':<10} {'Avg Return%':<12}")
                print(f"   {'-'*50}")
                for reason, data in sorted(exit_reasons.items()):
                    win_pct = (data['wins'] / data['count'] * 100) if data['count'] > 0 else 0
                    avg_ret = data['total_return'] / data['count'] if data['count'] > 0 else 0
                    print(f"   {reason:<15} {data['count']:<8} {win_pct:<10.1f} {avg_ret:<12.4f}")

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
            
        result = backtest_single(tv, args.symbol, args.exchange, n_bars=n_bars, fixed_threshold=fixed_thresh, threshold_multiplier=threshold_multiplier, production=production_mode, **test_kwargs)
        
        if result and 'detailed_predictions' in result:
            for p in result['detailed_predictions']:
                p['symbol'] = args.symbol
                p['exchange'] = args.exchange
                p['group'] = 'SINGLE_TEST'
            save_trade_logs(result['detailed_predictions'])
        
    else:
        parser.print_help()

    print("\n" + "=" * 70)
    # Check if all_results was defined (from backtest_all call)
    # backtest_all() returns DataFrame or None
    try:
        if 'all_results' in locals():
            if all_results is not None and isinstance(all_results, pd.DataFrame) and not all_results.empty:
                print("✅ Backtest Complete")
            elif all_results is not None and isinstance(all_results, list) and len(all_results) > 0:
                print("✅ Backtest Complete")
            else:
                print("ℹ️  All symbols already processed. No new results generated.")
        else:
            print("✅ Backtest Complete")
    except NameError:
        print("✅ Backtest Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
