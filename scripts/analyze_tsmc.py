#!/usr/bin/env python
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv('logs/trade_history_TAIWAN.csv', on_bad_lines='skip', engine='python')
tsmc = df[df['symbol']=='2330']

print("=" * 80)
print("TSMC (2330) - Detailed Analysis")
print("=" * 80)

print(f"\nTotal Trades: {len(tsmc)}")
print(f"Raw Count: 426 (from symbol_performance.csv)")

if len(tsmc) > 0:
    print(f"\n{'='*80}")
    print("Win/Loss Breakdown (All Trades):")
    print(f"{'='*80}")
    wins = tsmc[tsmc['actual_return'] > 0]
    losses = tsmc[tsmc['actual_return'] <= 0]
    zeros = tsmc[tsmc['actual_return'] == 0]
    
    total = len(tsmc)
    print(f"Wins: {len(wins)} ({len(wins)/total*100:.1f}%)")
    print(f"Losses: {len(losses)} ({len(losses)/total*100:.1f}%)")
    print(f"Zeros: {len(zeros)} ({len(zeros)/total*100:.1f}%)")
    
    if len(wins) > 0:
        print(f"\nAvgWin: {wins['actual_return'].abs().mean():.2f}%")
        print(f"MaxWin: {wins['actual_return'].abs().max():.2f}%")
    else:
        print("\n[WARNING] NO WINS RECORDED!")
    
    if len(losses) > 0:
        print(f"\nAvgLoss: {losses['actual_return'].abs().mean():.2f}%")
        print(f"MaxLoss: {losses['actual_return'].abs().max():.2f}%")
    
    print(f"\n{'='*80}")
    print("Prob% vs Actual Win Rate Comparison:")
    print(f"{'='*80}")
    
    if 'prob' in tsmc.columns:
        tsmc['prob_num'] = pd.to_numeric(tsmc['prob'], errors='coerce')
        
        # Calculate actual win rate
        if 'correct' in tsmc.columns:
            tsmc['correct'] = pd.to_numeric(tsmc['correct'], errors='coerce')
            actual_wins = tsmc['correct'].sum()
            actual_win_rate = (actual_wins / len(tsmc)) * 100
        else:
            # Fallback: use actual_return > 0
            actual_wins = (tsmc['actual_return'] > 0).sum()
            actual_win_rate = (actual_wins / len(tsmc)) * 100
        
        # Average Prob% (predicted win rate)
        avg_prob = tsmc['prob_num'].mean()
        
        print(f"[INFO] Predicted Win Rate (Avg Prob%): {avg_prob:.2f}%")
        print(f"[INFO] Actual Win Rate: {actual_win_rate:.2f}%")
        print(f"[INFO] Difference: {abs(avg_prob - actual_win_rate):.2f}%")
        
        if abs(avg_prob - actual_win_rate) < 5:
            print("[OK] Pattern matching is ACCURATE (difference < 5%)")
        else:
            print("[WARNING] Pattern matching is INACCURATE (difference >= 5%)")
        
        print(f"\n{'='*80}")
        print("Elite Trades Analysis (Prob >= 60%):")
        print(f"{'='*80}")
        print("[IMPORTANT] Elite Filter = Historical Probability Filter")
        print("   NOT a filter for winning trades!")
        print(f"{'='*80}")
        
        elite = tsmc[tsmc['prob_num'] >= 60]
        print(f"Elite Trades (Prob >= 60%): {len(elite)}")
        
        if len(elite) > 0:
            # Elite actual win rate
            if 'correct' in elite.columns:
                elite['correct'] = pd.to_numeric(elite['correct'], errors='coerce')
                elite_wins = elite['correct'].sum()
                elite_win_rate = (elite_wins / len(elite)) * 100
            else:
                elite_wins = (elite['actual_return'] > 0).sum()
                elite_win_rate = (elite_wins / len(elite)) * 100
            
            elite_avg_prob = elite['prob_num'].mean()
            
            print(f"\nElite Predicted Win Rate (Avg Prob%): {elite_avg_prob:.2f}%")
            print(f"Elite Actual Win Rate: {elite_win_rate:.2f}%")
            print(f"Elite Difference: {abs(elite_avg_prob - elite_win_rate):.2f}%")
            
            elite_wins_trades = elite[elite['actual_return'] > 0]
            elite_losses_trades = elite[elite['actual_return'] <= 0]
            print(f"\nElite Wins: {len(elite_wins_trades)}")
            print(f"Elite Losses: {len(elite_losses_trades)}")
            
            if len(elite_wins_trades) > 0:
                print(f"Elite AvgWin: {elite_wins_trades['actual_return'].abs().mean():.2f}%")
            if len(elite_losses_trades) > 0:
                print(f"Elite AvgLoss: {elite_losses_trades['actual_return'].abs().mean():.2f}%")
            
            # Calculate RRR for elite trades
            if len(elite_wins_trades) > 0 and len(elite_losses_trades) > 0:
                elite_avg_win = elite_wins_trades['actual_return'].abs().mean()
                elite_avg_loss = elite_losses_trades['actual_return'].abs().mean()
                elite_rrr = elite_avg_win / elite_avg_loss if elite_avg_loss > 0 else 0
                print(f"Elite RRR: {elite_rrr:.2f}")
            elif len(elite_wins_trades) > 0:
                print("Elite RRR: ∞ (no losses)")
            else:
                print("Elite RRR: 0.00 (no wins)")
            
            print(f"\n{'='*80}")
            print("Sample Elite Trades (Prob >= 60%):")
            print(f"{'='*80}")
            display_cols = ['date', 'forecast', 'actual', 'actual_return', 'prob']
            if 'correct' in elite.columns:
                display_cols.append('correct')
            print(elite[display_cols].head(10).to_string(index=False))
        else:
            print("[WARNING] No elite trades found!")
        
        print(f"\n{'='*80}")
        print("Prob% Distribution:")
        print(f"{'='*80}")
        print(f"Min Prob%: {tsmc['prob_num'].min():.2f}%")
        print(f"Max Prob%: {tsmc['prob_num'].max():.2f}%")
        print(f"Avg Prob%: {tsmc['prob_num'].mean():.2f}%")
        print(f"Median Prob%: {tsmc['prob_num'].median():.2f}%")
        print(f"\nProb% >= 60%: {len(tsmc[tsmc['prob_num'] >= 60])} trades")
        print(f"Prob% >= 55%: {len(tsmc[tsmc['prob_num'] >= 55])} trades")
        print(f"Prob% >= 52%: {len(tsmc[tsmc['prob_num'] >= 52])} trades")
        
        print(f"\nTop 10 Prob% Values:")
        print(tsmc['prob_num'].value_counts().sort_index(ascending=False).head(10))
    else:
        print("[WARNING] No 'prob' column found")
    
    print(f"\n{'='*80}")
    print("Return Distribution:")
    print(f"{'='*80}")
    print(f"Min: {tsmc['actual_return'].min():.4f}%")
    print(f"Max: {tsmc['actual_return'].max():.4f}%")
    print(f"Mean: {tsmc['actual_return'].mean():.4f}%")
    print(f"Median: {tsmc['actual_return'].median():.4f}%")
    print(f"Std: {tsmc['actual_return'].std():.4f}%")
else:
    print("[WARNING] No TSMC trades found in trade_history_TAIWAN.csv")
    print("This might be because:")
    print("1. TSMC trades were filtered out before saving")
    print("2. TSMC didn't pass the gatekeeper (Prob >= 52%, Expectancy > 0)")

print(f"\n{'='*80}")
print("Why TSMC Doesn't Pass Criteria:")
print(f"{'='*80}")
print("From symbol_performance.csv:")
print("1. Prob%: 58.0% (may be below 52% requirement for Taiwan)")
print("2. RRR: 0.00 (no wins in elite trades OR elite trade loss)")
print("3. Count: 426 > 150 (too high - over-trading)")
print("4. Elite Count: 1 (only 1 trade passes elite filter Prob >= 60%)")
print("5. Elite trade loss -> RRR = 0")

print(f"\n{'='*80}")
print("Key Issue:")
print(f"{'='*80}")
print("TSMC มี trades 426 ตัว แต่:")
print("- มีแค่ 1 ตัวที่ผ่าน elite filter (Prob >= 60%)")
print("- Elite trade ตัวนั้น loss -> RRR = 0")
print("- Raw Prob% = 58.0% (อาจจะต่ำกว่า 52% requirement)")
print("- Count สูงเกินไป (426 > 150) -> over-trading")

print(f"\n{'='*80}")
print("Can We Use TSMC in Real Trading?")
print(f"{'='*80}")
print("[X] NO - ไม่สามารถใช้ได้!")
print("\nReasons:")
print("1. Elite Count = 1 (น้อยเกินไป - ไม่มีข้อมูลเพียงพอ)")
print("2. RRR = 0.00 (ไม่คุ้มเสี่ยง - elite trade loss)")
print("3. Prob% ต่ำ (58.0% - pattern matching ไม่แม่น)")
print("4. Count สูงเกินไป (426 > 150 - over-trading)")
print("\nConclusion:")
print("TSMC ไม่เหมาะกับระบบนี้ เพราะ:")
print("- Volatility ต่ำ -> Pattern matching ยาก")
print("- Prob% ต่ำ -> ไม่แม่น")
print("- Elite trade loss -> RRR = 0")

print(f"\n{'='*80}")
print("Recommendations:")
print(f"{'='*80}")
print("1. ตรวจสอบว่าทำไม TSMC มี Prob% ต่ำ (58.0%)")
print("   - อาจจะต้องปรับ threshold หรือ logic สำหรับ TSMC")
print("   - หรือ skip TSMC เพราะไม่เหมาะกับระบบ")
print("2. ตรวจสอบ elite trade ตัวเดียวว่าทำไม loss")
print("   - Elite Prob% = 100% แต่ loss -> over-confident หรือมีปัญหา")
print("3. ควรลด Count requirement หรือ cap สำหรับหุ้นที่มี trades เยอะ")
print("4. หรือใช้ Raw Prob% (58.0%) แทน Elite Prob% ถ้า Elite Count < 5")
print("5. **Skip TSMC** - Focus on stocks that pass criteria (Prob >= 52%, RRR >= 1.3, Count 25-150)")

