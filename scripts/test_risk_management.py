#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_risk_management.py - วิเคราะห์ Raw Data + ทดสอบ Risk Management
================================================================================
Part 1: วิเคราะห์ว่า Win/Loss เท่ากันจริงหรือไม่ (ดูข้อมูลดิบ)
Part 2: ทดสอบ Stop Loss / Take Profit / Trailing Stop
Part 3: เปรียบเทียบผลลัพธ์
"""

import sys
import os
import pandas as pd
import numpy as np

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache

def load_data(symbol, exchange):
    """Load data"""
    tv = TvDatafeed()
    df = get_data_with_cache(
        tv=tv,
        symbol=symbol,
        exchange=exchange,
        interval=Interval.in_daily,
        full_bars=5000,
        delta_bars=50
    )
    return df

def prepare_signals(df, strategy, floor, multiplier=1.25, n_test_bars=2000):
    """Prepare signals for backtest - return list of entry points with direction"""
    total_bars = len(df)
    train_end = total_bars - n_test_bars
    
    close = df['close']
    pct_change = close.pct_change()
    
    # Calculate threshold
    short_std = pct_change.rolling(window=20).std()
    long_std = pct_change.rolling(window=252).std()
    effective_std = np.maximum(short_std, long_std.fillna(0))
    effective_std = np.maximum(effective_std, floor)
    threshold = effective_std * multiplier
    
    # SMA for regime
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    
    # Extract patterns
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
    
    MAX_LEN = 8
    signals = []
    
    for i in range(train_end, len(df) - 1):
        # Get last pattern
        window_slice = raw_patterns[i-MAX_LEN+1 : i+1] if i-MAX_LEN+1 >= 0 else raw_patterns[:i+1]
        last_pats = [p for p in window_slice if p is not None]
        
        if not last_pats:
            continue
        
        last_directional = last_pats[-1]
        
        # Determine direction
        if strategy == 'HYBRID_VOL':
            avg_vol = effective_std.iloc[max(0, i-20):i+1].mean()
            current_vol = effective_std.iloc[i]
            if current_vol > avg_vol * 1.2:  # HIGH_VOL -> REVERSION
                intended_dir = -1 if last_directional == '+' else 1 if last_directional == '-' else 0
            else:  # LOW_VOL -> TREND
                intended_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
        elif strategy == 'REGIME_AWARE':
            c_price = close.iloc[i]
            c_sma50 = sma50.iloc[i]
            c_sma200 = sma200.iloc[i] if not pd.isna(sma200.iloc[i]) else c_price
            if pd.isna(c_sma50):
                regime = 'SIDEWAYS'
            elif c_price > c_sma50 and c_sma50 > c_sma200:
                regime = 'BULL'
            elif c_price < c_sma50 and c_sma50 < c_sma200:
                regime = 'BEAR'
            else:
                regime = 'SIDEWAYS'
            
            if regime == 'BULL':
                intended_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
            else:
                intended_dir = -1 if last_directional == '+' else 1 if last_directional == '-' else 0
        elif strategy == 'REVERSION':
            intended_dir = -1 if last_directional == '+' else 1 if last_directional == '-' else 0
        else:  # TREND
            intended_dir = 1 if last_directional == '+' else -1 if last_directional == '-' else 0
        
        if intended_dir == 0:
            continue
        
        signals.append({
            'entry_idx': i,
            'intended_dir': intended_dir,
            'pattern': last_directional
        })
    
    return signals

# ============================================================================
# Part 1: Raw Data Analysis
# ============================================================================
def analyze_raw_distribution(df, signals):
    """วิเคราะห์ raw next-day returns ว่า distribution เป็นยังไง"""
    close = df['close']
    pct_change = close.pct_change()
    
    results = []
    for sig in signals:
        i = sig['entry_idx']
        intended_dir = sig['intended_dir']
        
        if i + 1 >= len(df):
            continue
        
        next_ret = pct_change.iloc[i+1]
        if pd.isna(next_ret):
            continue
        
        actual_ret_pct = next_ret * 100
        trader_ret_pct = actual_ret_pct * intended_dir
        is_correct = 1 if ((intended_dir == 1 and next_ret > 0) or (intended_dir == -1 and next_ret < 0)) else 0
        
        results.append({
            'intended_dir': intended_dir,
            'actual_ret_pct': actual_ret_pct,
            'trader_ret_pct': trader_ret_pct,
            'correct': is_correct,
            'abs_ret': abs(actual_ret_pct)
        })
    
    return pd.DataFrame(results)

# ============================================================================
# Part 2: Multi-Day Hold + Stop Loss / Take Profit
# ============================================================================
def backtest_with_risk_mgmt(df, signals, stop_loss_pct=None, take_profit_pct=None, 
                             trailing_stop_pct=None, max_hold_days=1):
    """Backtest with Stop Loss / Take Profit / Trailing Stop"""
    close = df['close']
    high = df['high']
    low = df['low']
    
    results = []
    
    for sig in signals:
        entry_idx = sig['entry_idx']
        intended_dir = sig['intended_dir']
        
        if entry_idx + 1 >= len(df):
            continue
        
        entry_price = close.iloc[entry_idx]
        
        if max_hold_days == 1:
            # Simple 1-day exit
            exit_price = close.iloc[entry_idx + 1]
            pct_return = (exit_price / entry_price - 1) * 100 * intended_dir
            exit_reason = '1DAY'
        else:
            # Multi-day with risk management
            best_price = entry_price
            pct_return = 0
            exit_reason = 'MAX_HOLD'
            
            for day in range(1, max_hold_days + 1):
                if entry_idx + day >= len(df):
                    break
                
                current_close = close.iloc[entry_idx + day]
                current_high = high.iloc[entry_idx + day]
                current_low = low.iloc[entry_idx + day]
                
                # Update best price for trailing stop
                if intended_dir == 1:
                    best_price = max(best_price, current_high)
                    current_return_pct = (current_close / entry_price - 1) * 100
                    intraday_worst = (current_low / entry_price - 1) * 100
                    intraday_best = (current_high / entry_price - 1) * 100
                    trailing_drawdown = (current_low / best_price - 1) * 100
                else:  # SHORT
                    best_price = min(best_price, current_low)
                    current_return_pct = -(current_close / entry_price - 1) * 100
                    intraday_worst = -(current_high / entry_price - 1) * 100
                    intraday_best = -(current_low / entry_price - 1) * 100
                    trailing_drawdown = -(best_price / current_high - 1) * 100
                
                # Check Stop Loss
                if stop_loss_pct is not None and intraday_worst <= -stop_loss_pct:
                    pct_return = -stop_loss_pct
                    exit_reason = 'STOP_LOSS'
                    break
                
                # Check Take Profit
                if take_profit_pct is not None and intraday_best >= take_profit_pct:
                    pct_return = take_profit_pct
                    exit_reason = 'TAKE_PROFIT'
                    break
                
                # Check Trailing Stop
                if trailing_stop_pct is not None and trailing_drawdown <= -trailing_stop_pct:
                    pct_return = current_return_pct  # Exit at close
                    exit_reason = 'TRAILING_STOP'
                    break
                
                # Last day: exit at close
                if day == max_hold_days:
                    pct_return = current_return_pct
                    exit_reason = 'MAX_HOLD'
        
        is_correct = 1 if pct_return > 0 else 0
        
        results.append({
            'intended_dir': intended_dir,
            'trader_return_pct': pct_return,
            'correct': is_correct,
            'exit_reason': exit_reason
        })
    
    return pd.DataFrame(results)

def calculate_stats(df_results, label):
    """Calculate statistics from results"""
    if len(df_results) == 0:
        return None
    
    total = len(df_results)
    correct = df_results['correct'].sum()
    accuracy = (correct / total * 100)
    
    wins = df_results[df_results['correct'] == 1]['trader_return_pct']
    losses = df_results[df_results['correct'] == 0]['trader_return_pct']
    
    avg_win = wins.abs().mean() if len(wins) > 0 else 0
    avg_loss = losses.abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    total_return = df_results['trader_return_pct'].sum()
    
    # Expectancy per trade
    win_rate = correct / total
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    return {
        'label': label,
        'total': total,
        'accuracy': accuracy,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'rrr': rrr,
        'total_return': total_return,
        'expectancy': expectancy
    }

def main():
    """Main function"""
    print("\n" + "="*120)
    print("🔬 Raw Data Analysis + Risk Management Testing")
    print("="*120)
    
    markets = [
        {'symbol': 'NVDA', 'exchange': 'NASDAQ', 'floor': 0.006, 'strategy': 'HYBRID_VOL', 'label': 'US (NVDA)'},
        {'symbol': '2330', 'exchange': 'TWSE', 'floor': 0.005, 'strategy': 'HYBRID_VOL', 'label': 'TW (TSMC)'},
    ]
    
    for market in markets:
        print(f"\n{'='*120}")
        print(f"🔬 {market['label']} - Strategy: {market['strategy']}")
        print(f"{'='*120}")
        
        df = load_data(market['symbol'], market['exchange'])
        if df is None or len(df) < 500:
            print("❌ Not enough data")
            continue
        
        signals = prepare_signals(df, market['strategy'], market['floor'], n_test_bars=2000)
        print(f"📊 Total Signals: {len(signals)}")
        
        # ============================================================================
        # PART 1: Raw Data Analysis
        # ============================================================================
        print(f"\n{'─'*120}")
        print(f"📊 PART 1: Raw Data Analysis (1-Day Exit, ไม่มี filter)")
        print(f"{'─'*120}")
        
        raw_df = analyze_raw_distribution(df, signals)
        
        if len(raw_df) == 0:
            print("❌ No data")
            continue
        
        total = len(raw_df)
        correct = raw_df['correct'].sum()
        incorrect = total - correct
        accuracy = correct / total * 100
        
        print(f"\n   Total Trades: {total}")
        print(f"   Win (ทายถูก): {correct} ({accuracy:.2f}%)")
        print(f"   Loss (ทายผิด): {incorrect} ({100-accuracy:.2f}%)")
        
        wins = raw_df[raw_df['correct'] == 1]
        losses = raw_df[raw_df['correct'] == 0]
        
        avg_win = wins['trader_ret_pct'].abs().mean()
        avg_loss = losses['trader_ret_pct'].abs().mean()
        
        print(f"\n   📈 เมื่อทายถูก (Win):")
        print(f"      Avg Win: {avg_win:.4f}%")
        print(f"      Median Win: {wins['trader_ret_pct'].abs().median():.4f}%")
        
        print(f"\n   📉 เมื่อทายผิด (Loss):")
        print(f"      Avg Loss: {avg_loss:.4f}%")
        print(f"      Median Loss: {losses['trader_ret_pct'].abs().median():.4f}%")
        
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        print(f"\n   💰 RRR: {rrr:.4f}")
        print(f"      AvgWin / AvgLoss = {avg_win:.4f}% / {avg_loss:.4f}%")
        
        # WHY AvgWin ~ AvgLoss?
        print(f"\n   🔍 ทำไม AvgWin ≈ AvgLoss?")
        print(f"      → เพราะเราใช้ 1-Day Exit:")
        print(f"        - ถ้าทายถูก: กำไร = |next day return|")
        print(f"        - ถ้าทายผิด: ขาดทุน = |next day return|")
        print(f"        - ทั้ง Win และ Loss มาจาก distribution เดียวกัน (next-day return)")
        print(f"        - ดังนั้น AvgWin ≈ AvgLoss เสมอ! → RRR ≈ 1.0 เสมอ!")
        
        # Show the distribution of next-day returns
        all_returns = raw_df['abs_ret']
        print(f"\n   📊 Next-Day Return Distribution (ทุก trade):")
        print(f"      Mean: {all_returns.mean():.4f}%")
        print(f"      Median: {all_returns.median():.4f}%")
        print(f"      Std: {all_returns.std():.4f}%")
        
        win_returns = wins['abs_ret']
        loss_returns = losses['abs_ret']
        print(f"\n   📊 เมื่อทายถูก vs ทายผิด (ดู distribution):")
        print(f"      Win Mean: {win_returns.mean():.4f}%, Median: {win_returns.median():.4f}%")
        print(f"      Loss Mean: {loss_returns.mean():.4f}%, Median: {loss_returns.median():.4f}%")
        print(f"      → ถ้า 2 ค่านี้ใกล้กัน = ระบบไม่มี edge ด้าน magnitude")
        print(f"      → Edge อยู่ที่ Direction (Win Rate) เท่านั้น")
        
        # ============================================================================
        # PART 2: Risk Management Testing
        # ============================================================================
        print(f"\n{'─'*120}")
        print(f"📊 PART 2: Risk Management Testing")
        print(f"{'─'*120}")
        
        risk_configs = [
            {'label': 'Baseline (1-Day, No RM)', 'max_hold': 1, 'sl': None, 'tp': None, 'ts': None},
            {'label': '3-Day Hold, No RM', 'max_hold': 3, 'sl': None, 'tp': None, 'ts': None},
            {'label': '5-Day Hold, No RM', 'max_hold': 5, 'sl': None, 'tp': None, 'ts': None},
            {'label': '3-Day + SL 2%', 'max_hold': 3, 'sl': 2.0, 'tp': None, 'ts': None},
            {'label': '3-Day + SL 2% + TP 3%', 'max_hold': 3, 'sl': 2.0, 'tp': 3.0, 'ts': None},
            {'label': '3-Day + SL 2% + TP 4%', 'max_hold': 3, 'sl': 2.0, 'tp': 4.0, 'ts': None},
            {'label': '5-Day + SL 2% + TP 4%', 'max_hold': 5, 'sl': 2.0, 'tp': 4.0, 'ts': None},
            {'label': '5-Day + SL 3% + TP 5%', 'max_hold': 5, 'sl': 3.0, 'tp': 5.0, 'ts': None},
            {'label': '5-Day + TS 2%', 'max_hold': 5, 'sl': None, 'tp': None, 'ts': 2.0},
            {'label': '5-Day + SL 2% + TS 1.5%', 'max_hold': 5, 'sl': 2.0, 'tp': None, 'ts': 1.5},
            {'label': '10-Day + SL 3% + TP 6%', 'max_hold': 10, 'sl': 3.0, 'tp': 6.0, 'ts': None},
            {'label': '10-Day + SL 2% + TS 2%', 'max_hold': 10, 'sl': 2.0, 'tp': None, 'ts': 2.0},
        ]
        
        all_stats = []
        
        for rc in risk_configs:
            bt_results = backtest_with_risk_mgmt(
                df, signals,
                stop_loss_pct=rc['sl'],
                take_profit_pct=rc['tp'],
                trailing_stop_pct=rc['ts'],
                max_hold_days=rc['max_hold']
            )
            
            stats = calculate_stats(bt_results, rc['label'])
            if stats:
                all_stats.append(stats)
                
                # Show exit reason breakdown
                if rc['sl'] or rc['tp'] or rc['ts']:
                    exit_counts = bt_results['exit_reason'].value_counts()
        
        # Display comparison table
        print(f"\n{'Strategy':<35} {'Trades':<8} {'Accuracy':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<8} {'Expect':<10} {'Return%':<10}")
        print("─"*120)
        
        for s in all_stats:
            print(f"{s['label']:<35} {s['total']:<8} {s['accuracy']:<10.2f} {s['avg_win']:<10.4f} {s['avg_loss']:<10.4f} {s['rrr']:<8.2f} {s['expectancy']:<10.4f} {s['total_return']:<10.2f}")
        
        print("─"*120)
        
        # Find best
        best = max(all_stats, key=lambda x: x['expectancy'])
        best_return = max(all_stats, key=lambda x: x['total_return'])
        best_rrr = max(all_stats, key=lambda x: x['rrr'])
        
        print(f"\n   🏆 Best Expectancy: {best['label']}")
        print(f"      Accuracy: {best['accuracy']:.2f}%, RRR: {best['rrr']:.2f}, Return: {best['total_return']:.2f}%")
        
        print(f"\n   🏆 Best Total Return: {best_return['label']}")
        print(f"      Accuracy: {best_return['accuracy']:.2f}%, RRR: {best_return['rrr']:.2f}, Return: {best_return['total_return']:.2f}%")
        
        print(f"\n   🏆 Best RRR: {best_rrr['label']}")
        print(f"      Accuracy: {best_rrr['accuracy']:.2f}%, RRR: {best_rrr['rrr']:.2f}, Return: {best_rrr['total_return']:.2f}%")
        
        # ============================================================================
        # PART 3: Explanation
        # ============================================================================
        print(f"\n{'─'*120}")
        print(f"💡 PART 3: สรุปและอธิบาย")
        print(f"{'─'*120}")
        
        print(f"""
   🔑 ทำไม RRR ≈ 1.0 เมื่อใช้ 1-Day Exit?
   ─────────────────────────────────────────
   เพราะ: Win size ≈ Loss size เสมอ!
   
   ตัวอย่าง: ถ้าพรุ่งนี้หุ้นขึ้น 2%
     - ถ้าเราทาย LONG (ถูก): กำไร = +2%
     - ถ้าเราทาย SHORT (ผิด): ขาดทุน = -2%
   
   ทั้ง Win และ Loss มาจาก |next-day return| ตัวเดียวกัน
   → AvgWin ≈ AvgLoss → RRR ≈ 1.0 เสมอ!
   
   📌 Edge ของระบบอยู่ที่ Direction (Accuracy) เท่านั้น
   → ถ้า Accuracy = 55% กำไรจะมาจาก "ทายถูกบ่อยกว่าทายผิด"
   → ไม่ใช่จาก "ได้กำไรเยอะกว่าขาดทุน"
   
   🔑 จะทำให้ RRR > 1.0 ได้ยังไง?
   ─────────────────────────────────────────
   ต้องให้ Win size > Loss size โดย:
   1. ถือหลายวัน + Stop Loss (ตัด Loss เร็ว)
   2. ถือหลายวัน + Take Profit / Trailing Stop (ปล่อยกำไรวิ่ง)
   3. ใช้ Risk:Reward ratio เช่น SL 2% : TP 4% → RRR = 2.0
        """)
    
    print("\n" + "="*120)

if __name__ == "__main__":
    main()

