#!/usr/bin/env python
"""
Test China Min Prob in Gatekeeper - ทดสอบค่า min_prob ที่เหมาะสม
เพื่อให้ Prob% ที่แสดง realistic มากขึ้น
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_min_prob():
    """ทดสอบค่า min_prob ต่างๆ"""
    
    print("="*100)
    print("Test China Min Prob in Gatekeeper - หาค่า min_prob ที่เหมาะสม")
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
    
    # Test different min_prob values
    min_prob_options = [51.0, 52.0, 53.0, 54.0, 55.0]
    
    print("="*100)
    print("Testing Different Min Prob in Gatekeeper")
    print("="*100)
    print(f"{'Min Prob':<15} {'Total Trades':<15} {'Passed Trades':<15} {'Pass Rate':<15} {'Avg Prob%':<15} {'Avg RRR':<15}")
    print("-" * 100)
    
    results = []
    
    for min_prob in min_prob_options:
        # Filter trades by min_prob (simulate gatekeeper)
        filtered_trades = df[df['prob'] >= min_prob].copy()
        
        if filtered_trades.empty:
            print(f"{min_prob:<15.1f} {'0':<15} {'0':<15} {'0.0%':<15} {'N/A':<15} {'N/A':<15}")
            continue
        
        total_trades = len(df)
        passed_trades = len(filtered_trades)
        pass_rate = (passed_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate Raw Prob% from filtered trades
        raw_wins = int(filtered_trades['correct'].sum())
        raw_prob = (raw_wins / passed_trades * 100) if passed_trades > 0 else 0
        
        # Calculate RRR from filtered trades
        if 'forecast' in filtered_trades.columns and 'actual' in filtered_trades.columns:
            filtered_trades['pnl'] = filtered_trades.apply(
                lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
                axis=1
            )
        else:
            filtered_trades['pnl'] = filtered_trades['actual_return']
        
        wins = filtered_trades[filtered_trades['pnl'] > 0]['pnl'].abs()
        losses = filtered_trades[filtered_trades['pnl'] <= 0]['pnl'].abs()
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        results.append({
            'min_prob': min_prob,
            'total_trades': total_trades,
            'passed_trades': passed_trades,
            'pass_rate': pass_rate,
            'avg_prob': raw_prob,
            'avg_rrr': rrr
        })
        
        print(f"{min_prob:<15.1f} {total_trades:<15} {passed_trades:<15} {pass_rate:<15.1f} {raw_prob:<15.1f} {rrr:<15.2f}")
    
    print()
    print("="*100)
    print("💡 Recommendation:")
    print("="*100)
    print()
    
    if results:
        # Find min_prob that gives realistic Prob% (55-65%)
        best = None
        for r in results:
            if 55.0 <= r['avg_prob'] <= 65.0:
                if best is None or abs(r['avg_prob'] - 60.0) < abs(best['avg_prob'] - 60.0):
                    best = r
        
        if best:
            print(f"✅ Recommended Min Prob: {best['min_prob']:.1f}%")
            print(f"   Total Trades: {best['total_trades']}")
            print(f"   Passed Trades: {best['passed_trades']} ({best['pass_rate']:.1f}%)")
            print(f"   Avg Prob%: {best['avg_prob']:.1f}% (realistic)")
            print(f"   Avg RRR: {best['avg_rrr']:.2f}")
        else:
            # Fallback: use min_prob that gives lowest Prob% but still has good RRR
            best = None
            for r in sorted(results, key=lambda x: x['avg_prob']):
                if r['avg_rrr'] >= 1.2 and r['pass_rate'] >= 50.0:
                    best = r
                    break
            
            if best:
                print(f"⚠️  Best Available Min Prob: {best['min_prob']:.1f}%")
                print(f"   Total Trades: {best['total_trades']}")
                print(f"   Passed Trades: {best['passed_trades']} ({best['pass_rate']:.1f}%)")
                print(f"   Avg Prob%: {best['avg_prob']:.1f}% (ยังสูงอยู่)")
                print(f"   Avg RRR: {best['avg_rrr']:.2f}")
            else:
                print(f"⚠️  ไม่พบค่า min_prob ที่เหมาะสม")
                print(f"   → Prob% จะสูงอยู่ (เพราะเป็น Raw Prob% ของหุ้นที่ผ่านเกณฑ์แล้ว)")
                print(f"   → อาจจะต้องยอมรับว่า Prob% จะสูงอยู่ หรือปรับ display criteria")

if __name__ == "__main__":
    test_min_prob()

