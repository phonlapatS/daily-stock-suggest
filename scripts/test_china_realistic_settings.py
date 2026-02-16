#!/usr/bin/env python
"""
Test China Market - Adjust Multiplier to Lower Prob & Increase RRR

User Feedback:
- prob ยังสูงเกินไป (ในเทรดจริงโอกาสชนะอาจไม่ถึง 70%)
- RRR น้อย

ทดสอบ threshold_multiplier และ min_prob:
- threshold_multiplier: เพิ่มจาก 0.9 → 1.0, 1.1, 1.2 (จับ pattern ยากขึ้น → prob ลดลง)
- min_prob: เพิ่มจาก 54.0% → 55.0%, 56.0%, 57.0% (กรองหุ้นมากขึ้น → prob ลดลง, RRR เพิ่ม)

เป้าหมาย:
- Average Prob < 65% (realistic - ไม่สูงเกินไป)
- RRR >= 1.4 (สูงขึ้น)
- Win Rate: 60-70% (realistic - ไม่สูงเกินไป)
- Total Trades >= 10 (ต้องมี trades)
"""

import sys
import os
import pandas as pd
import subprocess
import time
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test Parameters - ปรับ multiplier เพื่อลด prob และเพิ่ม RRR
# User feedback: prob ยังสูงเกินไป, RRR น้อย, ในเทรดจริงโอกาสชนะอาจไม่ถึง 70%
THRESHOLD_MULTIPLIER_OPTIONS = [0.9, 1.0]  # ทดสอบทั้ง 0.9 และ 1.0
MIN_PROB_OPTIONS = [52.0, 53.0, 54.0]  # ลด min_prob เพื่อให้มี trades (52.0, 53.0, 54.0)
ATR_TP_MULT_OPTIONS = [5.0, 6.0, 7.0]  # ทดสอบ ATR TP 3 ค่าเพื่อเพิ่ม RRR (5.0, 6.0, 7.0)

def run_backtest(threshold_multiplier, min_prob, atr_tp_mult, n_bars=2000, verbose=True):
    """Run backtest with specific parameters"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    backtest_results_file = 'data/full_backtest_results.csv'
    
    # Clean old results
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # ลบ CN results จาก performance file
    if os.path.exists(perf_file):
        try:
            df = pd.read_csv(perf_file)
            # ลบ CN results ทั้งหมดเพื่อให้ backtest รันใหม่
            df = df[df['Country'] != 'CN']
            df.to_csv(perf_file, index=False)
            if verbose:
                print(f"Cleaned CN results from {perf_file}")
        except Exception as e:
            if verbose:
                print(f"Warning: Could not clean {perf_file}: {e}")
            pass
    
    # ลบ CN results จาก backtest results file เพื่อให้ backtest รันใหม่
    if os.path.exists(backtest_results_file):
        try:
            df = pd.read_csv(backtest_results_file)
            # ลบ CN results ทั้งหมด (เช็คจาก group หรือ country)
            if 'group' in df.columns:
                df = df[~df['group'].str.contains('CHINA', case=False, na=False)]
            elif 'Country' in df.columns:
                df = df[df['Country'] != 'CN']
            df.to_csv(backtest_results_file, index=False)
            if verbose:
                print(f"Cleaned CN results from {backtest_results_file}")
        except Exception as e:
            if verbose:
                print(f"Warning: Could not clean {backtest_results_file}: {e}")
            pass
    
    # Run backtest
    cmd = [
        'python', 'scripts/backtest.py',
        '--full',
        '--bars', str(n_bars),
        '--group', 'CHINA',
        '--fast',
        '--multiplier', str(threshold_multiplier),
        '--min_prob', str(min_prob),
        '--atr_tp_mult', str(atr_tp_mult)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        if verbose:
            print(f"Backtest error: {result.stderr[:500]}")
        return False
    
    # Calculate metrics
    subprocess.run(['python', 'scripts/calculate_metrics.py'], capture_output=True)
    time.sleep(2)
    return True

def analyze_results(threshold_multiplier, min_prob, atr_tp_mult):
    """Analyze results for specific parameters"""
    log_file = 'logs/trade_history_CHINA.csv'
    perf_file = 'data/symbol_performance.csv'
    
    if not os.path.exists(log_file):
        return None
    
    df = pd.read_csv(log_file, on_bad_lines='skip', engine='python')
    
    if len(df) == 0:
        return None
    
    # Convert to numeric
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce')
    df['hold_days'] = pd.to_numeric(df['hold_days'], errors='coerce')
    df = df.dropna(subset=['actual_return', 'hold_days'])
    
    if len(df) == 0:
        return None
    
    # Calculate metrics
    wins = df[df['actual_return'] > 0]
    losses = df[df['actual_return'] <= 0]
    
    total_trades = len(df)
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
    avg_return = df['actual_return'].mean()
    avg_win = wins['actual_return'].mean() if len(wins) > 0 else 0
    avg_loss = losses['actual_return'].abs().mean() if len(losses) > 0 else 0
    rrr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Hold days analysis
    avg_hold_days = df['hold_days'].mean()
    max_hold_days = df['hold_days'].max()
    hold_over_7 = len(df[df['hold_days'] > 7])
    hold_over_7_pct = (hold_over_7 / total_trades) * 100 if total_trades > 0 else 0
    
    # Exit reasons
    if 'exit_reason' in df.columns:
        tp_hits = len(df[df['exit_reason'] == 'TAKE_PROFIT'])
        sl_hits = len(df[df['exit_reason'] == 'STOP_LOSS'])
        max_hold_exits = len(df[df['exit_reason'] == 'MAX_HOLD'])
        
        tp_rate = (tp_hits / total_trades) * 100 if total_trades > 0 else 0
        sl_rate = (sl_hits / total_trades) * 100 if total_trades > 0 else 0
        max_hold_rate = (max_hold_exits / total_trades) * 100 if total_trades > 0 else 0
        
        # MAX_HOLD exits return
        max_hold_df = df[df['exit_reason'] == 'MAX_HOLD']
        max_hold_return = max_hold_df['actual_return'].mean() if len(max_hold_df) > 0 else 0
    else:
        tp_rate = 0
        sl_rate = 0
        max_hold_rate = 0
        max_hold_return = 0
    
    # Stocks passing
    stocks_passing = 0
    if os.path.exists(perf_file):
        try:
            df_perf = pd.read_csv(perf_file)
            stocks_passing = len(df_perf[df_perf['Country'] == 'CN'])
        except:
            pass
    
    # Calculate average prob from trades (if available)
    avg_prob = 0
    if 'prob' in df.columns:
        prob_series = pd.to_numeric(df['prob'], errors='coerce')
        avg_prob = prob_series.mean()
        if pd.isna(avg_prob):
            avg_prob = 0
    
    # Score calculation - ปรับให้เน้น prob ต่ำและ RRR สูง
    score = 0
    
    # Average Prob (ต่ำกว่า = ดีกว่า - realistic)
    if avg_prob < 60:
        score += 3
    elif avg_prob < 65:
        score += 2
    elif avg_prob < 70:
        score += 1
    
    # RRR (สูงกว่า = ดีกว่า)
    if rrr >= 1.5:
        score += 4
    elif rrr >= 1.4:
        score += 3
    elif rrr >= 1.3:
        score += 2
    elif rrr >= 1.2:
        score += 1
    
    # Win Rate (realistic - ไม่สูงเกินไป)
    if 60 <= win_rate <= 70:
        score += 3
    elif 55 <= win_rate < 60 or 70 < win_rate <= 75:
        score += 2
    elif 50 <= win_rate < 55 or 75 < win_rate <= 80:
        score += 1
    
    # Total Trades (ต้องมี trades)
    if total_trades >= 20:
        score += 2
    elif total_trades >= 10:
        score += 1
    
    # Stocks Passing
    if stocks_passing >= 4:
        score += 2
    elif stocks_passing >= 2:
        score += 1
    
    return {
        'threshold_multiplier': threshold_multiplier,
        'min_prob': min_prob,
        'atr_tp_mult': atr_tp_mult,
        'stocks_passing': stocks_passing,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'rrr': rrr,
        'expectancy': avg_return,
        'avg_prob': avg_prob,
        'tp_rate': tp_rate,
        'sl_rate': sl_rate,
        'max_hold_rate': max_hold_rate,
        'max_hold_return': max_hold_return,
        'avg_hold_days': avg_hold_days,
        'max_hold_days': max_hold_days,
        'hold_over_7_pct': hold_over_7_pct,
        'score': score
    }

def main():
    """Main function"""
    print("="*100)
    print("China Market - Adjust Multiplier Testing")
    print("="*100)
    print(f"\nTesting Parameters:")
    print(f"  Threshold Multiplier Options: {THRESHOLD_MULTIPLIER_OPTIONS}")
    print(f"  Min Prob Options: {MIN_PROB_OPTIONS}%")
    print(f"  ATR TP Multiplier Options: {ATR_TP_MULT_OPTIONS}")
    print(f"  Total Tests: {len(THRESHOLD_MULTIPLIER_OPTIONS) * len(MIN_PROB_OPTIONS) * len(ATR_TP_MULT_OPTIONS)}")
    
    print(f"\nTarget Criteria (User Feedback):")
    print(f"  Average Prob: < 65% (realistic - ไม่สูงเกินไป)")
    print(f"  RRR: >= 1.4 (สูงขึ้น)")
    print(f"  Win Rate: 60-70% (realistic - ไม่สูงเกินไป)")
    print(f"  Total Trades: >= 10 (ต้องมี trades)")
    print(f"  Stocks Passing: >= 2")
    
    results = []
    
    # Test all combinations
    for threshold_multiplier in THRESHOLD_MULTIPLIER_OPTIONS:
        for min_prob in MIN_PROB_OPTIONS:
            for atr_tp_mult in ATR_TP_MULT_OPTIONS:
                print(f"\n{'='*100}")
                print(f"Test {len(results)+1}/{len(THRESHOLD_MULTIPLIER_OPTIONS)*len(MIN_PROB_OPTIONS)*len(ATR_TP_MULT_OPTIONS)}: Multiplier={threshold_multiplier}, Min Prob={min_prob}%, ATR TP={atr_tp_mult}x")
                print(f"{'='*100}")
                
                if run_backtest(threshold_multiplier, min_prob, atr_tp_mult, verbose=True):
                    result = analyze_results(threshold_multiplier, min_prob, atr_tp_mult)
                if result:
                    results.append(result)
                    print(f"✅ Results:")
                    print(f"   Stocks: {result['stocks_passing']}, Trades: {result['total_trades']}")
                    print(f"   Avg Prob: {result['avg_prob']:.1f}%, Win Rate: {result['win_rate']:.1f}%, RRR: {result['rrr']:.2f}")
                    print(f"   TP Rate: {result['tp_rate']:.1f}%, MAX_HOLD Rate: {result['max_hold_rate']:.1f}%")
                    print(f"   Avg Hold: {result['avg_hold_days']:.1f} days, Score: {result['score']}")
                else:
                    print(f"⚠️  No results")
            else:
                print(f"❌ Backtest failed")
            
            time.sleep(1)
    
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('score', ascending=False)
        results_df.to_csv('data/china_multiplier_test_results.csv', index=False)
        
        print(f"\n{'='*100}")
        print("COMPARISON TABLE - Sorted by Score (Best First)")
        print(f"{'='*100}")
        print(f"\n{'Mult':<6} {'Min Prob':<10} {'ATR TP':<8} {'Stocks':<8} {'Trades':<8} {'Avg Prob':<10} {'Win Rate':<10} {'RRR':<8} {'TP Rate':<10} {'MAX_HOLD':<12} {'Score':<8}")
        print("-" * 100)
        for _, row in results_df.iterrows():
            print(f"{row['threshold_multiplier']:<6.1f} {row['min_prob']:<10.1f} {row['atr_tp_mult']:<8.1f} {row['stocks_passing']:<8} {row['total_trades']:<8} {row['avg_prob']:>8.1f}%     {row['win_rate']:>6.1f}%     {row['rrr']:>6.2f}   {row['tp_rate']:>6.1f}%     {row['max_hold_rate']:>10.1f}%     {row['score']:<8}")
        
        # Best combination
        best = results_df.iloc[0]
        print(f"\n{'='*100}")
        print("BEST COMBINATION (Realistic Prob & Higher RRR)")
        print(f"{'='*100}")
        print(f"  Threshold Multiplier: {best['threshold_multiplier']}")
        print(f"  Min Prob: {best['min_prob']:.1f}%")
        print(f"  ATR TP Multiplier: {best['atr_tp_mult']:.1f}x")
        print(f"  Stocks Passing: {best['stocks_passing']}")
        print(f"  Total Trades: {best['total_trades']}")
        print(f"  Average Prob: {best['avg_prob']:.1f}% {'✅' if best['avg_prob'] < 65 else '⚠️'}")
        print(f"  Win Rate: {best['win_rate']:.1f}% {'✅' if 60 <= best['win_rate'] <= 70 else '⚠️'}")
        print(f"  RRR: {best['rrr']:.2f} {'✅' if best['rrr'] >= 1.4 else '⚠️'}")
        print(f"  TP Hit Rate: {best['tp_rate']:.1f}%")
        print(f"  MAX_HOLD Rate: {best['max_hold_rate']:.1f}%")
        print(f"  Avg Hold Days: {best['avg_hold_days']:.1f} days")
        print(f"  Score: {best['score']}/14")
        
        # Assessment
        print(f"\n{'='*100}")
        print("ASSESSMENT")
        print(f"{'='*100}")
        
        acceptable = True
        issues = []
        
        if best['avg_prob'] >= 65:
            acceptable = False
            issues.append(f"Average Prob สูงเกินไป ({best['avg_prob']:.1f}%) - ควร < 65%")
        
        if best['rrr'] < 1.4:
            acceptable = False
            issues.append(f"RRR ต่ำ ({best['rrr']:.2f}) - ควร >= 1.4")
        
        if not (60 <= best['win_rate'] <= 70):
            issues.append(f"Win Rate อาจไม่ realistic ({best['win_rate']:.1f}%) - ควร 60-70%")
        
        if best['total_trades'] < 10:
            acceptable = False
            issues.append(f"Total Trades น้อยเกินไป ({best['total_trades']}) - ควร >= 10")
        
        if best['stocks_passing'] < 2:
            acceptable = False
            issues.append(f"Stocks Passing น้อยเกินไป ({best['stocks_passing']}) - ควร >= 2")
        
        if acceptable:
            print(f"  ✅ ✅ ✅ ACCEPTABLE - ผลลัพธ์พอรับได้!")
            print(f"  💡 แนะนำ: ใช้ threshold_multiplier={best['threshold_multiplier']}, min_prob={best['min_prob']:.1f}%, atr_tp_mult={best['atr_tp_mult']:.1f}x")
        else:
            print(f"  ⚠️  มีปัญหา:")
            for issue in issues:
                print(f"    - {issue}")
            print(f"  💡 พิจารณา: ปรับ parameters หรือทดสอบเพิ่มเติม")
        
        print(f"\n✅ Results saved to: data/china_multiplier_test_results.csv")
    else:
        print(f"\n⚠️  No results to display")
    
    print(f"\n{'='*100}")
    print("Testing Complete!")
    print(f"{'='*100}")

if __name__ == '__main__':
    main()

