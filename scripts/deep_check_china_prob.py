#!/usr/bin/env python
"""
Deep Check China Prob% - ตรวจสอบ Prob% แบบละเอียด
ตรวจสอบว่า Prob% 91.7% และ 82.7% มันจริงหรือไม่ หรือมี bias
"""

import sys
import os
import pandas as pd
import numpy as np
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def deep_check_prob():
    """ตรวจสอบ Prob% แบบละเอียด"""
    
    print("="*100)
    print("Deep Check: China Prob% Reliability")
    print("="*100)
    print()
    print("⚠️ User Concern: Prob% 91.7% และ 82.7% ดูเวอร์ไป")
    print("   → ในการเทรดจริงมันไม่มีทาง win rate สูงขนาดนี้")
    print("   → มันต้องชนะปนกับแพ้อยู่แล้ว")
    print()
    
    # Load trade history
    trade_file = 'logs/trade_history_CHINA.csv'
    if not os.path.exists(trade_file):
        print(f"❌ File not found: {trade_file}")
        return
    
    df = pd.read_csv(trade_file, on_bad_lines='skip', engine='python')
    print(f"✅ Loaded {len(df)} trades from {trade_file}")
    print()
    
    symbols_to_check = ['1810', '3690']  # XIAOMI, MEITUAN
    
    for symbol in symbols_to_check:
        symbol_trades = df[df['symbol'].astype(str) == str(symbol)].copy()
        
        if symbol_trades.empty:
            continue
        
        print("="*100)
        print(f"Deep Analysis: {symbol}")
        print("="*100)
        
        # Convert to numeric
        symbol_trades['prob'] = pd.to_numeric(symbol_trades['prob'], errors='coerce').fillna(0)
        symbol_trades['correct'] = pd.to_numeric(symbol_trades['correct'], errors='coerce').fillna(0)
        symbol_trades['actual_return'] = pd.to_numeric(symbol_trades['actual_return'], errors='coerce').fillna(0)
        symbol_trades['trader_return'] = pd.to_numeric(symbol_trades['trader_return'], errors='coerce').fillna(0)
        
        # ====== 1. Raw Metrics ======
        raw_count = len(symbol_trades)
        raw_wins = int(symbol_trades['correct'].sum())
        raw_prob = (raw_wins / raw_count * 100) if raw_count > 0 else 0
        
        print(f"\n📊 1. Raw Metrics (All Trades):")
        print(f"   Total Trades: {raw_count}")
        print(f"   Wins: {raw_wins}")
        print(f"   Losses: {raw_count - raw_wins}")
        print(f"   Raw Win Rate: {raw_prob:.1f}%")
        print(f"   → นี่คือ Win Rate จริงของทุก trades")
        
        # ====== 2. Elite Metrics ======
        elite_trades = symbol_trades[symbol_trades['prob'] >= 60.0].copy()
        elite_count = len(elite_trades)
        
        if elite_count > 0:
            elite_wins = int(elite_trades['correct'].sum())
            elite_prob = (elite_wins / elite_count * 100) if elite_count > 0 else 0
            
            print(f"\n⭐ 2. Elite Metrics (Historical Prob >= 60%):")
            print(f"   Elite Count: {elite_count} ({elite_count/raw_count*100:.1f}% of total)")
            print(f"   Elite Wins: {elite_wins}")
            print(f"   Elite Losses: {elite_count - elite_wins}")
            print(f"   Elite Win Rate: {elite_prob:.1f}%")
            print(f"   → นี่คือ Win Rate ของ trades ที่มี Historical Prob >= 60%")
            
            # ====== 3. Check for Pattern Clustering ======
            print(f"\n🔍 3. Pattern Analysis (Elite Trades):")
            
            if 'pattern' in elite_trades.columns:
                pattern_counts = elite_trades['pattern'].value_counts()
                print(f"   Unique Patterns: {len(pattern_counts)}")
                print(f"   Top 5 Patterns:")
                for pattern, count in pattern_counts.head(5).items():
                    pattern_trades = elite_trades[elite_trades['pattern'] == pattern]
                    pattern_wins = int(pattern_trades['correct'].sum())
                    pattern_win_rate = (pattern_wins / count * 100) if count > 0 else 0
                    print(f"      {pattern}: {count} trades, Win Rate: {pattern_win_rate:.1f}%")
                
                # Check if most trades come from same pattern
                top_pattern_count = pattern_counts.iloc[0] if len(pattern_counts) > 0 else 0
                if top_pattern_count / elite_count > 0.5:
                    print(f"   ⚠️ Warning: {top_pattern_count}/{elite_count} ({top_pattern_count/elite_count*100:.1f}%) มาจาก pattern เดียวกัน")
                    print(f"      → อาจเป็น overfitting (pattern เดียวชนะหลายครั้ง)")
            
            # ====== 4. Time Distribution ======
            print(f"\n📅 4. Time Distribution (Elite Trades):")
            if 'date' in elite_trades.columns:
                elite_trades['date'] = pd.to_datetime(elite_trades['date'], errors='coerce')
                date_range = elite_trades['date'].max() - elite_trades['date'].min()
                print(f"   Date Range: {elite_trades['date'].min()} → {elite_trades['date'].max()}")
                print(f"   Span: {date_range.days} days")
                
                # Check if trades are clustered in time
                elite_trades_sorted = elite_trades.sort_values('date')
                time_gaps = elite_trades_sorted['date'].diff().dt.days
                avg_gap = time_gaps.mean()
                print(f"   Avg Days Between Trades: {avg_gap:.1f} days")
                
                # Check consecutive wins/losses
                elite_trades_sorted = elite_trades_sorted.sort_values('date')
                consecutive_wins = 0
                max_consecutive_wins = 0
                for _, row in elite_trades_sorted.iterrows():
                    if row['correct'] == 1:
                        consecutive_wins += 1
                        max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                    else:
                        consecutive_wins = 0
                
                print(f"   Max Consecutive Wins: {max_consecutive_wins}")
                if max_consecutive_wins > elite_count * 0.3:
                    print(f"   ⚠️ Warning: มี consecutive wins สูง ({max_consecutive_wins}/{elite_count})")
                    print(f"      → อาจเป็น lucky streak หรือ overfitting")
            
            # ====== 5. Return Distribution ======
            print(f"\n💰 5. Return Distribution (Elite Trades):")
            elite_wins_returns = elite_trades[elite_trades['correct'] == 1]['trader_return'].abs()
            elite_losses_returns = elite_trades[elite_trades['correct'] == 0]['trader_return'].abs()
            
            if len(elite_wins_returns) > 0:
                print(f"   Wins: {len(elite_wins_returns)} trades")
                print(f"      Avg Win: {elite_wins_returns.mean():.2f}%")
                print(f"      Min Win: {elite_wins_returns.min():.2f}%")
                print(f"      Max Win: {elite_wins_returns.max():.2f}%")
            
            if len(elite_losses_returns) > 0:
                print(f"   Losses: {len(elite_losses_returns)} trades")
                print(f"      Avg Loss: {elite_losses_returns.mean():.2f}%")
                print(f"      Min Loss: {elite_losses_returns.min():.2f}%")
                print(f"      Max Loss: {elite_losses_returns.max():.2f}%")
            
            if len(elite_wins_returns) > 0 and len(elite_losses_returns) > 0:
                elite_rrr = elite_wins_returns.mean() / elite_losses_returns.mean() if elite_losses_returns.mean() > 0 else 0
                print(f"   RRR: {elite_rrr:.2f}")
                print(f"   → ตรวจสอบ: ชนะได้กำไรมากกว่าขาดทุนหรือไม่?")
            
            # ====== 6. Historical Prob vs Actual Win Rate ======
            print(f"\n🎯 6. Historical Prob% vs Actual Win Rate:")
            print(f"   Historical Prob% (Elite): {elite_trades['prob'].mean():.1f}%")
            print(f"   Actual Win Rate (Elite): {elite_prob:.1f}%")
            print(f"   Difference: {abs(elite_trades['prob'].mean() - elite_prob):.1f}%")
            
            if abs(elite_trades['prob'].mean() - elite_prob) > 15:
                print(f"   ⚠️ Warning: Historical Prob% ไม่สอดคล้องกับ Actual Win Rate")
                print(f"      → Pattern matching อาจไม่แม่น หรือมี bias")
            
            # ====== 7. Check for Selection Bias ======
            print(f"\n🔬 7. Selection Bias Check:")
            print(f"   Elite Count: {elite_count} ({elite_count/raw_count*100:.1f}% of total)")
            print(f"   Elite Win Rate: {elite_prob:.1f}%")
            print(f"   Raw Win Rate: {raw_prob:.1f}%")
            print(f"   Difference: {elite_prob - raw_prob:.1f}%")
            
            if elite_prob - raw_prob > 20:
                print(f"   ⚠️ Warning: Elite Win Rate สูงกว่า Raw Win Rate มาก ({elite_prob - raw_prob:.1f}%)")
                print(f"      → อาจเป็น selection bias (เลือกเฉพาะ trades ที่ดี)")
                print(f"      → ในการเทรดจริง จะไม่รู้ว่า trade ไหนจะเป็น Elite")
            
            # ====== 8. Reality Check ======
            print(f"\n⚠️ 8. Reality Check:")
            print(f"   ❓ Prob% {elite_prob:.1f}% มันจริงหรือไม่?")
            print(f"   → Elite Count: {elite_count} trades")
            print(f"   → Elite Wins: {elite_wins} trades")
            print(f"   → Elite Losses: {elite_count - elite_wins} trades")
            
            if elite_count < 50:
                print(f"   ⚠️ Elite Count น้อย ({elite_count} < 50) → Prob% อาจไม่น่าเชื่อถือ")
            
            if elite_prob > 85:
                print(f"   ⚠️ Elite Prob% สูงมาก ({elite_prob:.1f}% > 85%) → ดูเวอร์ไป")
                print(f"      → ในการเทรดจริง ไม่มีทาง win rate สูงขนาดนี้")
                print(f"      → มันต้องชนะปนกับแพ้อยู่แล้ว")
            
            # ====== 9. Recommendation ======
            print(f"\n💡 9. Recommendation:")
            print(f"   ✅ ควรใช้ Raw Prob% ({raw_prob:.1f}%) เป็นหลัก")
            print(f"   ✅ สิ่งที่สำคัญคือ: RRR > 1 (ชนะได้กำไรมากกว่าขาดทุน)")
            print(f"   ⚠️ Elite Prob% ({elite_prob:.1f}%) อาจสูงเกินจริง (overfitting/selection bias)")
            print(f"   ⚠️ ในการเทรดจริง จะไม่รู้ว่า trade ไหนจะเป็น Elite")
            
        print()
    
    print("="*100)
    print("Summary:")
    print("="*100)
    print("""
🎯 สิ่งที่สำคัญจริงๆ:
1. ✅ RRR > 1 (ชนะได้กำไรมากกว่าขาดทุน)
2. ✅ Raw Win Rate (Win Rate จริงของทุก trades)
3. ⚠️ Elite Prob% อาจสูงเกินจริง (selection bias)

⚠️ ข้อควรระวัง:
- Elite Prob% = Win Rate ของ trades ที่มี Historical Prob >= 60%
- แต่ในการเทรดจริง จะไม่รู้ว่า trade ไหนจะเป็น Elite
- Elite Prob% อาจสูงเกินจริงเพราะ selection bias
- ควรใช้ Raw Prob% เป็นหลัก
    """)

if __name__ == "__main__":
    deep_check_prob()

