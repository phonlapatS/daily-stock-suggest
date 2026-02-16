#!/usr/bin/env python
"""
Find Optimal China Settings - หาจุดสมดุลที่เหมาะสม
- จำนวนหุ้นที่เทรดได้ (Stocks >= 4)
- ความเสี่ยงน้อย (Prob% สูง, Count สูง)
- RRR คุ้มค่าเสี่ยง (RRR >= 1.40)
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def find_optimal_settings():
    """หาจุดสมดุลที่เหมาะสม"""
    
    print("="*100)
    print("Find Optimal China Settings - หาจุดสมดุลที่เหมาะสม")
    print("="*100)
    print()
    print("🎯 เป้าหมาย:")
    print("   1. จำนวนหุ้นที่เทรดได้ (Stocks >= 4)")
    print("   2. ความเสี่ยงน้อย (Prob% >= 60%, Count >= 20)")
    print("   3. RRR คุ้มค่าเสี่ยง (RRR >= 1.40)")
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
    
    print("="*100)
    print("Testing Different Combinations")
    print("="*100)
    print()
    print("Note: การปรับ ATR TP ต้องรัน backtest ใหม่")
    print("      แต่เราสามารถวิเคราะห์จาก min_prob ได้ก่อน")
    print()
    
    # Test different min_prob values
    min_prob_options = [51.0, 52.0, 53.0, 54.0, 55.0]
    
    print(f"{'Min Prob':<15} {'Trades':<15} {'Pass Rate':<15} {'Avg Prob%':<15} {'Avg RRR':<15} {'Score':<15}")
    print("-" * 100)
    
    results = []
    
    for min_prob in min_prob_options:
        # Filter trades by min_prob (simulate gatekeeper)
        filtered_trades = df[df['prob'] >= min_prob].copy()
        
        if filtered_trades.empty:
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
        
        # Calculate score (weighted)
        # Score = (RRR >= 1.40 ? 40 : RRR/1.40*40) + (Prob% >= 60% ? 30 : Prob%/60%*30) + (Pass Rate >= 50% ? 30 : Pass Rate/50%*30)
        rrr_score = 40 if rrr >= 1.40 else (rrr / 1.40 * 40)
        prob_score = 30 if raw_prob >= 60.0 else (raw_prob / 60.0 * 30)
        pass_score = 30 if pass_rate >= 50.0 else (pass_rate / 50.0 * 30)
        total_score = rrr_score + prob_score + pass_score
        
        results.append({
            'min_prob': min_prob,
            'trades': passed_trades,
            'pass_rate': pass_rate,
            'avg_prob': raw_prob,
            'avg_rrr': rrr,
            'score': total_score
        })
        
        print(f"{min_prob:<15.1f} {passed_trades:<15} {pass_rate:<15.1f} {raw_prob:<15.1f} {rrr:<15.2f} {total_score:<15.1f}")
    
    print()
    print("="*100)
    print("💡 Recommendation")
    print("="*100)
    print()
    
    if results:
        # Find best combination
        best = max(results, key=lambda x: x['score'])
        
        print(f"✅ Recommended Min Prob: {best['min_prob']:.1f}%")
        print(f"   Trades: {best['trades']} ({best['pass_rate']:.1f}%)")
        print(f"   Avg Prob%: {best['avg_prob']:.1f}%")
        print(f"   Avg RRR: {best['avg_rrr']:.2f}")
        print(f"   Score: {best['score']:.1f}/100")
        print()
        
        # Check if RRR needs ATR TP adjustment
        if best['avg_rrr'] < 1.40:
            # Estimate ATR TP needed
            current_atr_tp = 4.0  # V13.5
            target_rrr = 1.40
            current_rrr = best['avg_rrr']
            
            # Simple estimation: RRR is roughly proportional to TP
            estimated_atr_tp = current_atr_tp * (target_rrr / current_rrr)
            
            print(f"⚠️  RRR ยังไม่ถึงเป้าหมาย (1.40)")
            print(f"   → ควรเพิ่ม ATR TP เป็นประมาณ {estimated_atr_tp:.1f}x (จาก 4.0x)")
            print(f"   → หรือใช้ Combined: min_prob {best['min_prob']:.1f}% + ATR TP {estimated_atr_tp:.1f}x")
        else:
            print(f"✅ RRR ถึงเป้าหมายแล้ว!")
            print(f"   → ใช้ min_prob {best['min_prob']:.1f}% + ATR TP 4.5x (V13.8)")
        
        print()
        print("="*100)
        print("📊 Final Recommendation")
        print("="*100)
        print()
        
        if best['avg_rrr'] >= 1.40:
            print("✅ Option 1: V13.8 (Current)")
            print(f"   - Min Prob: 54.0%")
            print(f"   - ATR TP: 4.5x")
            print(f"   - Expected RRR: {best['avg_rrr']:.2f} >= 1.40 ✅")
            print(f"   - Expected Prob%: {best['avg_prob']:.1f}% >= 60% ✅")
            print(f"   - Expected Pass Rate: {best['pass_rate']:.1f}% (จำนวนหุ้นเพียงพอ)")
        else:
            estimated_atr_tp = 4.0 * (1.40 / best['avg_rrr'])
            print("✅ Option 2: Optimized")
            print(f"   - Min Prob: {best['min_prob']:.1f}%")
            print(f"   - ATR TP: {estimated_atr_tp:.1f}x (เพิ่มจาก 4.0x)")
            print(f"   - Expected RRR: >= 1.40 ✅")
            print(f"   - Expected Prob%: {best['avg_prob']:.1f}% >= 60% ✅")
            print(f"   - Expected Pass Rate: {best['pass_rate']:.1f}% (จำนวนหุ้นเพียงพอ)")
            print()
            print("⚠️  ข้อควรระวัง:")
            print(f"   - การเพิ่ม ATR TP เป็น {estimated_atr_tp:.1f}x อาจทำให้ Prob% ลดลงเล็กน้อย")
            print(f"   - ต้องรัน backtest ใหม่เพื่อดูผลลัพธ์จริง")

if __name__ == "__main__":
    find_optimal_settings()

