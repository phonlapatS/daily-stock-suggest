#!/usr/bin/env python
"""
Analyze China V13.9 Results - วิเคราะห์ผลลัพธ์ V13.9
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_v13_9_results():
    """วิเคราะห์ผลลัพธ์ V13.9"""
    
    print("="*100)
    print("Analyze China V13.9 Results - วิเคราะห์ผลลัพธ์ V13.9")
    print("="*100)
    print()
    
    # Load trade history
    trade_file = 'logs/trade_history_CHINA.csv'
    if not os.path.exists(trade_file):
        print(f"❌ File not found: {trade_file}")
        return
    
    df = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    print(f"✅ Loaded {len(df)} trades from {trade_file}")
    print()
    
    # Convert to numeric
    df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0)
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
    df['actual_return'] = pd.to_numeric(df['actual_return'], errors='coerce').fillna(0)
    
    # Calculate metrics per symbol
    print("="*100)
    print("China/HK Stocks Analysis (V13.9)")
    print("="*100)
    print(f"{'Symbol':<12} {'Count':<10} {'Prob%':<10} {'AvgWin%':<12} {'AvgLoss%':<12} {'RRR':<10} {'Status':<20}")
    print("-" * 100)
    
    results = []
    symbols = df['symbol'].unique()
    
    for symbol in symbols:
        sym_df = df[df['symbol'] == symbol].copy()
        
        if len(sym_df) < 20:  # Skip if count < 20
            continue
        
        # Calculate Raw Prob%
        wins = int(sym_df['correct'].sum())
        total = len(sym_df)
        raw_prob = (wins / total * 100) if total > 0 else 0
        
        # Calculate RRR
        if 'forecast' in sym_df.columns and 'actual' in sym_df.columns:
            sym_df['pnl'] = sym_df.apply(
                lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
                axis=1
            )
        else:
            sym_df['pnl'] = sym_df['actual_return']
        
        wins_pnl = sym_df[sym_df['pnl'] > 0]['pnl'].abs()
        losses_pnl = sym_df[sym_df['pnl'] <= 0]['pnl'].abs()
        avg_win = wins_pnl.mean() if len(wins_pnl) > 0 else 0
        avg_loss = losses_pnl.mean() if len(losses_pnl) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Status
        status = []
        if raw_prob >= 60.0:
            status.append("✅ Prob")
        else:
            status.append("⚠️ Prob")
        
        if rrr >= 1.40:
            status.append("✅ RRR")
        elif rrr >= 1.0:
            status.append("⚠️ RRR")
        else:
            status.append("❌ RRR")
        
        if total >= 20:
            status.append("✅ Count")
        else:
            status.append("⚠️ Count")
        
        status_str = ", ".join(status)
        
        results.append({
            'symbol': symbol,
            'count': total,
            'prob': raw_prob,
            'avgwin': avg_win,
            'avgloss': avg_loss,
            'rrr': rrr,
            'status': status_str
        })
        
        print(f"{symbol:<12} {total:<10} {raw_prob:<10.1f} {avg_win:<12.2f} {avg_loss:<12.2f} {rrr:<10.2f} {status_str:<20}")
    
    print()
    print("="*100)
    print("Summary Statistics")
    print("="*100)
    
    if results:
        # Filter by display criteria (Prob >= 60%, RRR >= 1.0, Count >= 20)
        passing = [r for r in results if r['prob'] >= 60.0 and r['rrr'] >= 1.0 and r['count'] >= 20]
        
        print(f"Total Stocks Analyzed: {len(results)}")
        print(f"Passing Stocks (Prob >= 60%, RRR >= 1.0, Count >= 20): {len(passing)}")
        print()
        
        if passing:
            avg_prob = sum(r['prob'] for r in passing) / len(passing)
            avg_rrr = sum(r['rrr'] for r in passing) / len(passing)
            avg_win = sum(r['avgwin'] for r in passing) / len(passing)
            avg_loss = sum(r['avgloss'] for r in passing) / len(passing)
            avg_count = sum(r['count'] for r in passing) / len(passing)
            min_rrr = min(r['rrr'] for r in passing)
            max_rrr = max(r['rrr'] for r in passing)
            
            print("Passing Stocks Statistics:")
            print(f"  Avg Prob%: {avg_prob:.1f}%")
            print(f"  Avg RRR: {avg_rrr:.2f}")
            print(f"  Min RRR: {min_rrr:.2f}")
            print(f"  Max RRR: {max_rrr:.2f}")
            print(f"  Avg Win%: {avg_win:.2f}%")
            print(f"  Avg Loss%: {avg_loss:.2f}%")
            print(f"  Avg Count: {avg_count:.0f}")
            print()
            
            # Check targets
            print("="*100)
            print("Target Achievement")
            print("="*100)
            
            rrr_ok = sum(1 for r in passing if r['rrr'] >= 1.40)
            prob_ok = sum(1 for r in passing if r['prob'] >= 60.0)
            count_ok = sum(1 for r in passing if r['count'] >= 20)
            
            print(f"✅ RRR >= 1.40: {rrr_ok}/{len(passing)} stocks ({rrr_ok/len(passing)*100:.1f}%)")
            print(f"✅ Prob% >= 60%: {prob_ok}/{len(passing)} stocks ({prob_ok/len(passing)*100:.1f}%)")
            print(f"✅ Count >= 20: {count_ok}/{len(passing)} stocks ({count_ok/len(passing)*100:.1f}%)")
            print(f"✅ Stocks >= 4: {len(passing)} >= 4 {'✅' if len(passing) >= 4 else '❌'}")
            print()
            
            # Overall assessment
            print("="*100)
            print("Overall Assessment")
            print("="*100)
            
            if avg_rrr >= 1.40 and avg_prob >= 60.0 and len(passing) >= 4:
                print("✅ EXCELLENT: All targets achieved!")
                print(f"   - Avg RRR: {avg_rrr:.2f} >= 1.40 ✅")
                print(f"   - Avg Prob%: {avg_prob:.1f}% >= 60% ✅")
                print(f"   - Stocks: {len(passing)} >= 4 ✅")
            elif avg_rrr >= 1.30 and avg_prob >= 60.0 and len(passing) >= 4:
                print("⚠️ GOOD: Most targets achieved, but RRR could be higher")
                print(f"   - Avg RRR: {avg_rrr:.2f} (target: >= 1.40)")
                print(f"   - Avg Prob%: {avg_prob:.1f}% >= 60% ✅")
                print(f"   - Stocks: {len(passing)} >= 4 ✅")
            else:
                print("⚠️ NEEDS IMPROVEMENT: Some targets not met")
                print(f"   - Avg RRR: {avg_rrr:.2f} (target: >= 1.40)")
                print(f"   - Avg Prob%: {avg_prob:.1f}% (target: >= 60%)")
                print(f"   - Stocks: {len(passing)} (target: >= 4)")
        else:
            print("❌ No stocks passing the display criteria")
            print("   (Prob >= 60%, RRR >= 1.0, Count >= 20)")
    
    print()
    print("="*100)
    print("Comparison: V13.8 vs V13.9")
    print("="*100)
    print()
    print("V13.8 (ATR TP 4.5x):")
    print("  - Avg RRR: 1.40")
    print("  - Avg Prob%: 72.4%")
    print("  - Stocks: 5")
    print("  - RRR >= 1.40: 2/5 (40%)")
    print()
    if results and passing:
        print("V13.9 (ATR TP 5.0x):")
        print(f"  - Avg RRR: {avg_rrr:.2f}")
        print(f"  - Avg Prob%: {avg_prob:.1f}%")
        print(f"  - Stocks: {len(passing)}")
        print(f"  - RRR >= 1.40: {rrr_ok}/{len(passing)} ({rrr_ok/len(passing)*100:.1f}%)")
        print()
        if avg_rrr >= 1.40:
            print("✅ V13.9 is BETTER: RRR improved!")
        elif len(passing) > 5:
            print("✅ V13.9 is BETTER: More stocks passing!")
        else:
            print("⚠️ V13.9 needs further tuning")

if __name__ == "__main__":
    analyze_v13_9_results()

