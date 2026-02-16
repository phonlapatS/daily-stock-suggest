#!/usr/bin/env python
"""
Analyze China Win Rate - วิเคราะห์ว่าทำไม Prob% ถึงสูง
และหาวิธีจูน RRR ให้สูงขึ้น
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_china_win_rate():
    """วิเคราะห์ Win Rate และ RRR ของ China stocks"""
    
    print("="*100)
    print("Analyze China Win Rate & RRR - วิเคราะห์ว่าทำไม Prob% ถึงสูงและจูน RRR")
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
    
    # Load symbol performance
    perf_file = 'data/symbol_performance.csv'
    if not os.path.exists(perf_file):
        print(f"❌ File not found: {perf_file}")
        return
    
    perf_df = pd.read_csv(perf_file)
    china_perf = perf_df[((perf_df['Country'] == 'CN') | (perf_df['Country'] == 'HK')) & 
                         (perf_df['Prob%'] >= 60.0) & 
                         (perf_df['RR_Ratio'] >= 1.0) & 
                         (perf_df['Count'] >= 20)]
    
    if china_perf.empty:
        print("❌ No China/HK stocks found")
        return
    
    print("="*100)
    print("Current China/HK Stocks (Prob% >= 60%, RRR >= 1.0, Count >= 20)")
    print("="*100)
    print(f"{'Symbol':<12} {'Prob%':<10} {'RRR':<10} {'AvgWin%':<12} {'AvgLoss%':<12} {'Count':<10} {'Total Trades':<15}")
    print("-" * 100)
    
    for _, row in china_perf.iterrows():
        symbol = str(row['symbol'])
        symbol_trades = df[df['symbol'].astype(str) == symbol].copy()
        
        print(f"{symbol:<12} {row['Prob%']:<10.1f} {row['RR_Ratio']:<10.2f} {row['AvgWin%']:<12.2f} {row['AvgLoss%']:<12.2f} {row['Count']:<10.0f} {len(symbol_trades):<15}")
    
    print()
    print("="*100)
    print("Analysis: ทำไม Prob% ถึงสูง?")
    print("="*100)
    print()
    
    # Overall stats
    total_trades = len(df)
    total_wins = int(df['correct'].sum())
    overall_prob = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"📊 Overall Market Stats:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Total Wins: {total_wins}")
    print(f"   Overall Raw Prob%: {overall_prob:.1f}%")
    print()
    
    # Gatekeeper stats
    print(f"🔍 Gatekeeper Stats:")
    print(f"   Min Prob (Gatekeeper): 51.0% (V13.7)")
    print(f"   Trades with Historical Prob >= 51.0%: {len(df[df['prob'] >= 51.0])} ({len(df[df['prob'] >= 51.0])/total_trades*100:.1f}%)")
    print(f"   Trades with Historical Prob >= 60.0%: {len(df[df['prob'] >= 60.0])} ({len(df[df['prob'] >= 60.0])/total_trades*100:.1f}%)")
    print()
    
    # RRR analysis
    print("="*100)
    print("RRR Analysis: สามารถจูน RRR ขึ้นได้ไหม?")
    print("="*100)
    print()
    
    # Calculate RRR for different Prob% thresholds
    prob_thresholds = [51.0, 52.0, 53.0, 54.0, 55.0]
    
    print(f"{'Min Prob':<15} {'Trades':<15} {'Avg Prob%':<15} {'Avg RRR':<15} {'AvgWin%':<15} {'AvgLoss%':<15}")
    print("-" * 100)
    
    for min_prob in prob_thresholds:
        filtered_trades = df[df['prob'] >= min_prob].copy()
        
        if filtered_trades.empty:
            continue
        
        # Calculate RRR
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
        
        raw_wins = int(filtered_trades['correct'].sum())
        raw_prob = (raw_wins / len(filtered_trades) * 100) if len(filtered_trades) > 0 else 0
        
        print(f"{min_prob:<15.1f} {len(filtered_trades):<15} {raw_prob:<15.1f} {rrr:<15.2f} {avg_win:<15.2f} {avg_loss:<15.2f}")
    
    print()
    print("="*100)
    print("💡 Recommendation: วิธีจูน RRR ให้สูงขึ้น")
    print("="*100)
    print()
    
    print("1. เพิ่ม min_prob ใน gatekeeper:")
    print("   - จาก 51.0% → 52.0% หรือ 53.0%")
    print("   - จะกรอง trades ที่มี Historical Prob% ต่ำกว่า threshold ออกไป")
    print("   - ผลลัพธ์: RRR อาจจะเพิ่มขึ้นเล็กน้อย แต่ Prob% อาจจะไม่ลดลงมาก")
    print()
    
    print("2. เพิ่ม ATR TP multiplier:")
    print("   - จาก 4.0x → 4.5x หรือ 5.0x")
    print("   - จะเพิ่ม Take Profit ทำให้ RRR สูงขึ้น")
    print("   - ผลลัพธ์: RRR จะเพิ่มขึ้น แต่ Prob% อาจจะลดลง (เพราะ TP สูงขึ้น)")
    print()
    
    print("3. ลด ATR SL multiplier:")
    print("   - จาก 1.0x → 0.8x หรือ 0.9x")
    print("   - จะลด Stop Loss ทำให้ RRR สูงขึ้น")
    print("   - ผลลัพธ์: RRR จะเพิ่มขึ้น แต่ Prob% อาจจะลดลง (เพราะ SL แคบขึ้น)")
    print()
    
    print("4. ปรับ threshold_multiplier หรือ min_stats:")
    print("   - threshold_multiplier: จาก 0.9 → 0.95 หรือ 1.0")
    print("   - min_stats: จาก 30 → 35 หรือ 40")
    print("   - จะกรอง pattern ที่มีคุณภาพดีกว่า")
    print("   - ผลลัพธ์: Prob% และ RRR อาจจะเพิ่มขึ้น")
    print()
    
    print("⚠️  ข้อควรระวัง:")
    print("   - Prob% สูงอยู่แล้ว (70-77%) เพราะเป็น Raw Prob% ของหุ้นที่ผ่านเกณฑ์แล้ว")
    print("   - การจูน RRR อาจจะทำให้ Prob% ลดลง (trade-off)")
    print("   - ต้องทดสอบและเปรียบเทียบผลลัพธ์ก่อนใช้จริง")

if __name__ == "__main__":
    analyze_china_win_rate()

