#!/usr/bin/env python
"""
Test China Prob% Threshold - ทดสอบค่า Prob% threshold ที่เหมาะสม
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

def test_prob_thresholds():
    """ทดสอบค่า Prob% threshold ต่างๆ"""
    
    print("="*100)
    print("Test China Prob% Threshold - หาค่า Prob% threshold ที่เหมาะสม")
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
    df['trader_return'] = pd.to_numeric(df['trader_return'], errors='coerce').fillna(0)
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce').fillna(0)
    
    # Test different Prob% thresholds
    prob_thresholds = [50.0, 55.0, 60.0, 65.0]
    
    print("="*100)
    print("Testing Different Prob% Thresholds in Display Criteria")
    print("="*100)
    print(f"{'Prob% Threshold':<20} {'Stocks':<10} {'Avg Prob%':<15} {'Avg RRR':<15} {'Avg Count':<15} {'Min Prob%':<15}")
    print("-" * 100)
    
    results = []
    
    for prob_threshold in prob_thresholds:
        # Filter by symbol
        symbol_stats = []
        
        for symbol in df['symbol'].unique():
            symbol_trades = df[df['symbol'].astype(str) == str(symbol)].copy()
            
            if symbol_trades.empty:
                continue
            
            # Calculate Raw Prob%
            raw_count = len(symbol_trades)
            raw_wins = int(symbol_trades['correct'].sum())
            raw_prob = (raw_wins / raw_count * 100) if raw_count > 0 else 0
            
            # Calculate RRR (use actual_return for consistency with calculate_metrics)
            if 'actual_return' in symbol_trades.columns:
                symbol_trades['actual_return'] = pd.to_numeric(symbol_trades['actual_return'], errors='coerce').fillna(0)
                # Calculate PnL based on forecast direction
                if 'forecast' in symbol_trades.columns and 'actual' in symbol_trades.columns:
                    symbol_trades['pnl'] = symbol_trades.apply(
                        lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
                        axis=1
                    )
                else:
                    symbol_trades['pnl'] = symbol_trades['actual_return']
                wins = symbol_trades[symbol_trades['pnl'] > 0]['pnl'].abs()
                losses = symbol_trades[symbol_trades['pnl'] <= 0]['pnl'].abs()
            else:
                wins = symbol_trades[symbol_trades['trader_return'] > 0]['trader_return'].abs()
                losses = symbol_trades[symbol_trades['trader_return'] <= 0]['trader_return'].abs()
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = losses.mean() if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
            
            # Apply filters
            if raw_prob >= prob_threshold and rrr >= 1.0 and raw_count >= 20:
                symbol_stats.append({
                    'symbol': symbol,
                    'prob': raw_prob,
                    'rrr': rrr,
                    'count': raw_count
                })
        
        if symbol_stats:
            stats_df = pd.DataFrame(symbol_stats)
            avg_prob = stats_df['prob'].mean()
            avg_rrr = stats_df['rrr'].mean()
            avg_count = stats_df['count'].mean()
            min_prob = stats_df['prob'].min()
            num_stocks = len(stats_df)
            
            results.append({
                'prob_threshold': prob_threshold,
                'num_stocks': num_stocks,
                'avg_prob': avg_prob,
                'avg_rrr': avg_rrr,
                'avg_count': avg_count,
                'min_prob': min_prob
            })
            
            print(f"{prob_threshold:<20.1f} {num_stocks:<10} {avg_prob:<15.1f} {avg_rrr:<15.2f} {avg_count:<15.0f} {min_prob:<15.1f}")
        else:
            print(f"{prob_threshold:<20.1f} {'0':<10} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15}")
    
    print()
    print("="*100)
    print("💡 Recommendation:")
    print("="*100)
    print()
    
    if results:
        # Find threshold that gives realistic Prob% (55-65%)
        best = None
        for r in results:
            if 55.0 <= r['avg_prob'] <= 65.0:
                if best is None or abs(r['avg_prob'] - 60.0) < abs(best['avg_prob'] - 60.0):
                    best = r
        
        if best:
            print(f"✅ Recommended Prob% Threshold: {best['prob_threshold']:.1f}%")
            print(f"   Stocks: {best['num_stocks']}")
            print(f"   Avg Prob%: {best['avg_prob']:.1f}% (realistic)")
            print(f"   Avg RRR: {best['avg_rrr']:.2f}")
            print(f"   Avg Count: {best['avg_count']:.0f}")
            print(f"   Min Prob%: {best['min_prob']:.1f}%")
        else:
            # Fallback: use threshold that gives lowest Prob%
            best = min(results, key=lambda x: x['avg_prob'])
            print(f"⚠️  Best Available Prob% Threshold: {best['prob_threshold']:.1f}%")
            print(f"   Stocks: {best['num_stocks']}")
            print(f"   Avg Prob%: {best['avg_prob']:.1f}% (ยังสูงอยู่)")
            print(f"   Avg RRR: {best['avg_rrr']:.2f}")
            print(f"   Avg Count: {best['avg_count']:.0f}")
            print(f"   Min Prob%: {best['min_prob']:.1f}%")
            print()
            print(f"   💡 อาจจะต้อง:")
            print(f"      1. เพิ่ม min_prob ใน gatekeeper (51.0% → 52.0% หรือ 53.0%)")
            print(f"      2. หรือยอมรับว่า Prob% จะสูงอยู่ (เพราะเป็น Raw Prob% ของหุ้นที่ผ่านเกณฑ์แล้ว)")

if __name__ == "__main__":
    test_prob_thresholds()

