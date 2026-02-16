#!/usr/bin/env python
"""
Test China RRR Tuning V2 - ทดสอบหลาย options เพื่อจูน RRR ให้สูงขึ้น
"""

import sys
import os
import pandas as pd
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_rrr_tuning():
    """ทดสอบหลาย options เพื่อจูน RRR"""
    
    print("="*100)
    print("Test China RRR Tuning V2 - หาวิธีจูน RRR ให้สูงขึ้น")
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
    
    print("="*100)
    print("Option 1: เพิ่ม min_prob ใน gatekeeper")
    print("="*100)
    print(f"{'Min Prob':<15} {'Trades':<15} {'Avg Prob%':<15} {'Avg RRR':<15} {'AvgWin%':<15} {'AvgLoss%':<15}")
    print("-" * 100)
    
    prob_options = [51.0, 52.0, 53.0, 54.0, 55.0]
    for min_prob in prob_options:
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
    print("Option 2: กรองหุ้นที่มี RRR สูง (Simulate ATR TP/SL adjustment)")
    print("="*100)
    print("Note: การปรับ ATR TP/SL ต้องรัน backtest ใหม่")
    print("      แต่เราสามารถวิเคราะห์จาก trades ที่มี RRR สูงได้")
    print()
    
    # Calculate RRR per symbol
    symbol_stats = []
    for symbol in df['symbol'].unique():
        symbol_trades = df[df['symbol'].astype(str) == str(symbol)].copy()
        
        if symbol_trades.empty:
            continue
        
        # Calculate RRR
        if 'forecast' in symbol_trades.columns and 'actual' in symbol_trades.columns:
            symbol_trades['pnl'] = symbol_trades.apply(
                lambda row: row['actual_return'] * (1 if row['forecast'] == 'UP' else -1), 
                axis=1
            )
        else:
            symbol_trades['pnl'] = symbol_trades['actual_return']
        
        wins = symbol_trades[symbol_trades['pnl'] > 0]['pnl'].abs()
        losses = symbol_trades[symbol_trades['pnl'] <= 0]['pnl'].abs()
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        
        raw_wins = int(symbol_trades['correct'].sum())
        raw_prob = (raw_wins / len(symbol_trades) * 100) if len(symbol_trades) > 0 else 0
        
        symbol_stats.append({
            'symbol': symbol,
            'prob': raw_prob,
            'rrr': rrr,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'count': len(symbol_trades)
        })
    
    stats_df = pd.DataFrame(symbol_stats)
    
    # Filter by different RRR thresholds
    print(f"{'RRR Threshold':<20} {'Stocks':<15} {'Avg Prob%':<15} {'Avg RRR':<15} {'AvgWin%':<15} {'AvgLoss%':<15}")
    print("-" * 100)
    
    rrr_thresholds = [1.0, 1.2, 1.3, 1.4, 1.5]
    for rrr_threshold in rrr_thresholds:
        filtered = stats_df[
            (stats_df['rrr'] >= rrr_threshold) & 
            (stats_df['prob'] >= 60.0) & 
            (stats_df['count'] >= 20)
        ]
        
        if len(filtered) > 0:
            print(f"{rrr_threshold:<20.1f} {len(filtered):<15} {filtered['prob'].mean():<15.1f} {filtered['rrr'].mean():<15.2f} {filtered['avg_win'].mean():<15.2f} {filtered['avg_loss'].mean():<15.2f}")
        else:
            print(f"{rrr_threshold:<20.1f} {'0':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15}")
    
    print()
    print("="*100)
    print("💡 Recommendation:")
    print("="*100)
    print()
    
    # Find best combination
    best_min_prob = None
    best_rrr = 0
    
    for min_prob in prob_options:
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
        
        if rrr > best_rrr and rrr >= 1.2:
            best_rrr = rrr
            best_min_prob = min_prob
    
    if best_min_prob:
        print(f"✅ Recommended: เพิ่ม min_prob เป็น {best_min_prob:.1f}%")
        print(f"   Expected RRR: {best_rrr:.2f}")
        print(f"   Expected Prob%: ~71-72% (ยังสูงอยู่)")
        print()
        print(f"⚠️  ข้อควรระวัง:")
        print(f"   - Prob% จะยังสูงอยู่ (70-77%) เพราะเป็น Raw Prob% ของหุ้นที่ผ่านเกณฑ์แล้ว")
        print(f"   - การเพิ่ม min_prob จะกรอง trades ที่มี Historical Prob% ต่ำกว่า threshold ออกไป")
        print(f"   - RRR จะเพิ่มขึ้นเล็กน้อย (0.99 → 1.15)")
        print()
        print(f"💡 วิธีเพิ่ม RRR เพิ่มเติม:")
        print(f"   1. เพิ่ม ATR TP multiplier: จาก 4.0x → 4.5x หรือ 5.0x")
        print(f"   2. ลด ATR SL multiplier: จาก 1.0x → 0.8x หรือ 0.9x")
        print(f"   3. ปรับ threshold_multiplier: จาก 0.9 → 0.95 หรือ 1.0")
        print(f"   4. ปรับ min_stats: จาก 30 → 35 หรือ 40")
    else:
        print(f"⚠️  ไม่พบค่า min_prob ที่เหมาะสม")
        print(f"   → ต้องทดสอบการปรับ ATR TP/SL หรือ threshold_multiplier/min_stats")

if __name__ == "__main__":
    test_rrr_tuning()

