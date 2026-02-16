#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_gatekeeper_comparison.py - ทดสอบและเปรียบเทียบ Gatekeeper เดิม vs ใหม่
================================================================================
ทดสอบ:
1. Gatekeeper เดิม (Prob >= 55%)
2. Gatekeeper ปัจจุบัน (Prob >= 53%)
3. Gatekeeper สูง (Prob >= 60%)

และสร้างตารางเปรียบเทียบ
"""

import pandas as pd
import os
import sys
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
THAI_LOG = os.path.join(LOGS_DIR, "trade_history_THAI.csv")
METRICS_FILE = os.path.join(DATA_DIR, "symbol_performance.csv")

def simulate_gatekeeper(df, min_prob):
    """จำลอง gatekeeper ด้วย min_prob"""
    if 'prob' not in df.columns:
        return None
    
    df = df.copy()
    df['prob'] = pd.to_numeric(df['prob'], errors='coerce')
    
    # กรองด้วย gatekeeper
    filtered = df[df['prob'] >= min_prob].copy()
    
    return filtered

def calculate_metrics_for_gatekeeper(df_filtered, gatekeeper_name, min_prob):
    """คำนวณ metrics สำหรับ gatekeeper"""
    if df_filtered.empty:
        return {
            'gatekeeper': gatekeeper_name,
            'min_prob': min_prob,
            'total_trades': 0,
            'elite_trades': 0,
            'elite_prob': 0.0,
            'raw_prob': 0.0,
            'raw_avgwin': 0.0,
            'raw_avgloss': 0.0,
            'raw_rrr': 0.0,
            'elite_avgwin': 0.0,
            'elite_avgloss': 0.0,
            'elite_rrr': 0.0,
            'symbols': 0,
            'symbols_passing': 0
        }
    
    df_filtered = df_filtered.copy()
    
    # วิเคราะห์ Elite Filter (Prob >= 60%)
    elite_trades = df_filtered[df_filtered['prob'] >= 60.0].copy()
    
    # คำนวณ Raw Prob%
    if 'correct' in df_filtered.columns:
        df_filtered.loc[:, 'correct'] = pd.to_numeric(df_filtered['correct'], errors='coerce').fillna(0)
        raw_correct = int(df_filtered['correct'].sum())
        raw_prob = (raw_correct / len(df_filtered) * 100) if len(df_filtered) > 0 else 0.0
    else:
        raw_prob = 0.0
    
    # คำนวณ Raw AvgWin%, AvgLoss%, RRR
    if 'trader_return' in df_filtered.columns:
        df_filtered.loc[:, 'trader_return'] = pd.to_numeric(df_filtered['trader_return'], errors='coerce').fillna(0)
        raw_wins = df_filtered[df_filtered['trader_return'] > 0]['trader_return'].abs()
        raw_losses = df_filtered[df_filtered['trader_return'] <= 0]['trader_return'].abs()
        raw_avgwin = raw_wins.mean() if len(raw_wins) > 0 else 0.0
        raw_avgloss = raw_losses.mean() if len(raw_losses) > 0 else 0.0
        raw_rrr = raw_avgwin / raw_avgloss if raw_avgloss > 0 else 0.0
    else:
        raw_avgwin = 0.0
        raw_avgloss = 0.0
        raw_rrr = 0.0
    
    # คำนวณ Elite Prob%
    if not elite_trades.empty and 'correct' in elite_trades.columns:
        elite_trades.loc[:, 'correct'] = pd.to_numeric(elite_trades['correct'], errors='coerce').fillna(0)
        elite_correct = int(elite_trades['correct'].sum())
        elite_prob = (elite_correct / len(elite_trades) * 100) if len(elite_trades) > 0 else 0.0
    else:
        elite_prob = 0.0
    
    # คำนวณ Elite AvgWin%, AvgLoss%, RRR
    if not elite_trades.empty and 'trader_return' in elite_trades.columns:
        elite_trades.loc[:, 'trader_return'] = pd.to_numeric(elite_trades['trader_return'], errors='coerce').fillna(0)
        elite_wins = elite_trades[elite_trades['trader_return'] > 0]['trader_return'].abs()
        elite_losses = elite_trades[elite_trades['trader_return'] <= 0]['trader_return'].abs()
        elite_avgwin = elite_wins.mean() if len(elite_wins) > 0 else 0.0
        elite_avgloss = elite_losses.mean() if len(elite_losses) > 0 else 0.0
        elite_rrr = elite_avgwin / elite_avgloss if elite_avgloss > 0 else 0.0
    else:
        elite_avgwin = 0.0
        elite_avgloss = 0.0
        elite_rrr = 0.0
    
    # วิเคราะห์ตาม symbol
    symbols = df_filtered['symbol'].unique()
    
    # ตรวจสอบหุ้นที่ผ่านเกณฑ์ THAI MARKET (Prob >= 60% | RRR >= 1.2 | Count >= 30)
    symbols_passing = []
    for symbol in symbols:
        symbol_trades = df_filtered[df_filtered['symbol'] == symbol].copy()
        
        if len(symbol_trades) < 30:  # Count < 30
            continue
        
        # คำนวณ Prob%
        if 'correct' in symbol_trades.columns:
            symbol_trades.loc[:, 'correct'] = pd.to_numeric(symbol_trades['correct'], errors='coerce').fillna(0)
            symbol_correct = int(symbol_trades['correct'].sum())
            symbol_prob = (symbol_correct / len(symbol_trades) * 100) if len(symbol_trades) > 0 else 0.0
        else:
            symbol_prob = 0.0
        
        # ใช้ Elite Prob% ถ้ามี Elite Trades >= 5
        symbol_elite = symbol_trades[symbol_trades['prob'] >= 60.0].copy()
        if len(symbol_elite) >= 5:
            if 'correct' in symbol_elite.columns:
                symbol_elite.loc[:, 'correct'] = pd.to_numeric(symbol_elite['correct'], errors='coerce').fillna(0)
                symbol_elite_correct = int(symbol_elite['correct'].sum())
                symbol_prob = (symbol_elite_correct / len(symbol_elite) * 100) if len(symbol_elite) > 0 else symbol_prob
        
        # คำนวณ RRR
        if 'trader_return' in symbol_trades.columns:
            symbol_trades.loc[:, 'trader_return'] = pd.to_numeric(symbol_trades['trader_return'], errors='coerce').fillna(0)
            wins = symbol_trades[symbol_trades['trader_return'] > 0]['trader_return'].abs()
            losses = symbol_trades[symbol_trades['trader_return'] <= 0]['trader_return'].abs()
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = losses.mean() if len(losses) > 0 else 0
            rrr = avg_win / avg_loss if avg_loss > 0 else 0
        else:
            rrr = 0
        
        # ตรวจสอบว่าผ่านเกณฑ์หรือไม่
        if symbol_prob >= 60.0 and rrr >= 1.2 and len(symbol_trades) >= 30:
            symbols_passing.append({
                'symbol': symbol,
                'prob': symbol_prob,
                'rrr': rrr,
                'count': len(symbol_trades)
            })
    
        return {
        'gatekeeper': gatekeeper_name,
        'min_prob': min_prob,
        'total_trades': len(df_filtered),
        'elite_trades': len(elite_trades),
        'elite_prob': elite_prob,
        'raw_prob': raw_prob,
        'raw_avgwin': raw_avgwin,
        'raw_avgloss': raw_avgloss,
        'raw_rrr': raw_rrr,
        'elite_avgwin': elite_avgwin,
        'elite_avgloss': elite_avgloss,
        'elite_rrr': elite_rrr,
        'symbols': len(symbols),
        'symbols_passing': len(symbols_passing),
        'symbols_passing_list': symbols_passing
    }

def analyze_symbol_performance(df_filtered, symbol):
    """วิเคราะห์ performance ของหุ้นตัวเดียว"""
    symbol_trades = df_filtered[df_filtered['symbol'] == symbol].copy()
    
    if symbol_trades.empty:
        return None
    
    # คำนวณ Prob%
    if 'correct' in symbol_trades.columns:
        symbol_trades.loc[:, 'correct'] = pd.to_numeric(symbol_trades['correct'], errors='coerce').fillna(0)
        raw_correct = int(symbol_trades['correct'].sum())
        raw_prob = (raw_correct / len(symbol_trades) * 100) if len(symbol_trades) > 0 else 0.0
    else:
        raw_prob = 0.0
    
    # Elite Trades
    elite_trades = symbol_trades[symbol_trades['prob'] >= 60.0].copy()
    elite_count = len(elite_trades)
    
    if elite_count >= 5 and 'correct' in elite_trades.columns:
        elite_trades.loc[:, 'correct'] = pd.to_numeric(elite_trades['correct'], errors='coerce').fillna(0)
        elite_correct = int(elite_trades['correct'].sum())
        elite_prob = (elite_correct / elite_count * 100) if elite_count > 0 else 0.0
    else:
        elite_prob = 0.0
    
    # ใช้ Elite Prob% ถ้า Elite Count >= 5
    final_prob = elite_prob if elite_count >= 5 else raw_prob
    
    # คำนวณ RRR, AvgWin%, AvgLoss%
    if 'trader_return' in symbol_trades.columns:
        symbol_trades.loc[:, 'trader_return'] = pd.to_numeric(symbol_trades['trader_return'], errors='coerce').fillna(0)
        wins = symbol_trades[symbol_trades['trader_return'] > 0]['trader_return'].abs()
        losses = symbol_trades[symbol_trades['trader_return'] <= 0]['trader_return'].abs()
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        trader_returns = symbol_trades['trader_return'].tolist()
    else:
        rrr = 0
        trader_returns = []
    
    return {
        'symbol': symbol,
        'count': len(symbol_trades),
        'raw_prob': raw_prob,
        'elite_count': elite_count,
        'elite_prob': elite_prob,
        'final_prob': final_prob,
        'rrr': rrr,
        'trader_return': trader_returns,
        'passes_criteria': final_prob >= 60.0 and rrr >= 1.2 and len(symbol_trades) >= 30
    }

def main():
    print("\n" + "="*100)
    print("[GATEKEEPER COMPARISON] ทดสอบและเปรียบเทียบ Gatekeeper เดิม vs ใหม่")
    print("="*100)
    
    # โหลดข้อมูล
    if not os.path.exists(THAI_LOG):
        print(f"\n❌ ไม่พบไฟล์: {THAI_LOG}")
        return
    
    print(f"\n📊 โหลดข้อมูลจาก: {THAI_LOG}")
    df = pd.read_csv(THAI_LOG)
    
    if df.empty:
        print("❌ ไม่มีข้อมูล")
        return
    
    print(f"   โหลด {len(df)} trades ทั้งหมด")
    
    # ทดสอบ gatekeeper ต่างๆ
    gatekeepers = [
        (55.0, "เดิม (Prob >= 55%)"),
        (53.0, "ปัจจุบัน (Prob >= 53%)"),
        (60.0, "สูง (Prob >= 60%)")
    ]
    
    results = []
    symbol_details = {}
    
    for min_prob, name in gatekeepers:
        print(f"\n🔬 ทดสอบ Gatekeeper: {name}")
        print("-" * 80)
        
        # จำลอง gatekeeper
        filtered = simulate_gatekeeper(df, min_prob)
        
        if filtered is None or filtered.empty:
            print(f"   ❌ ไม่มี trades ที่ผ่าน gatekeeper")
            continue
        
        print(f"   ✅ Trades ที่ผ่าน: {len(filtered)} trades")
        
        # คำนวณ metrics
        metrics = calculate_metrics_for_gatekeeper(filtered, name, min_prob)
        results.append(metrics)
        
        print(f"   Elite Trades (Prob >= 60%): {metrics['elite_trades']}")
        print(f"   Raw Prob%: {metrics['raw_prob']:.1f}%")
        print(f"   Raw AvgWin%: {metrics['raw_avgwin']:.2f}%")
        print(f"   Raw AvgLoss%: {metrics['raw_avgloss']:.2f}%")
        print(f"   Raw RRR: {metrics['raw_rrr']:.2f}")
        print(f"   Elite Prob%: {metrics['elite_prob']:.1f}%")
        print(f"   Elite AvgWin%: {metrics['elite_avgwin']:.2f}%")
        print(f"   Elite AvgLoss%: {metrics['elite_avgloss']:.2f}%")
        print(f"   Elite RRR: {metrics['elite_rrr']:.2f}")
        print(f"   Symbols: {metrics['symbols']}")
        print(f"   Symbols ผ่านเกณฑ์: {metrics['symbols_passing']}")
        
        # เก็บรายละเอียดหุ้นสำคัญ
        important_symbols = ['TPIPP', 'SUPER', 'SSP', 'BTS', 'MINT', 'BYD']
        for symbol in important_symbols:
            if symbol not in symbol_details:
                symbol_details[symbol] = {}
            symbol_details[symbol][name] = analyze_symbol_performance(filtered, symbol)
    
    # สร้างตารางเปรียบเทียบ
    print("\n" + "="*100)
    print("[COMPARISON TABLE] ตารางเปรียบเทียบ Gatekeeper")
    print("="*100)
    
    # ตารางสรุป
    print(f"\n{'Gatekeeper':<25} {'Trades':<8} {'Elite':<8} {'Raw Prob%':<10} {'Raw RRR':<10} {'Elite Prob%':<12} {'Elite RRR':<12} {'Symbols':<8} {'ผ่านเกณฑ์':<10}")
    print("-" * 120)
    
    for r in results:
        print(f"{r['gatekeeper']:<25} {r['total_trades']:<8} {r['elite_trades']:<8} {r['raw_prob']:<10.1f} {r['raw_rrr']:<10.2f} {r['elite_prob']:<12.1f} {r['elite_rrr']:<12.2f} {r['symbols']:<8} {r['symbols_passing']:<10}")
    
    # ตารางเปรียบเทียบ Raw vs Elite Metrics
    print("\n" + "="*100)
    print("[METRICS COMPARISON] เปรียบเทียบ Raw vs Elite Metrics")
    print("="*100)
    
    print(f"\n{'Gatekeeper':<25} {'Type':<8} {'Prob%':<10} {'AvgWin%':<12} {'AvgLoss%':<12} {'RRR':<10}")
    print("-" * 100)
    
    for r in results:
        print(f"{r['gatekeeper']:<25} {'Raw':<8} {r['raw_prob']:<10.1f} {r['raw_avgwin']:<12.2f} {r['raw_avgloss']:<12.2f} {r['raw_rrr']:<10.2f}")
        print(f"{'':<25} {'Elite':<8} {r['elite_prob']:<10.1f} {r['elite_avgwin']:<12.2f} {r['elite_avgloss']:<12.2f} {r['elite_rrr']:<10.2f}")
        print("-" * 100)
    
    # ตารางเปรียบเทียบหุ้นสำคัญ
    print("\n" + "="*100)
    print("[SYMBOL COMPARISON] เปรียบเทียบหุ้นสำคัญ")
    print("="*100)
    
    for symbol in important_symbols:
        if symbol not in symbol_details:
            continue
        
        print(f"\n📊 {symbol}:")
        print(f"{'Gatekeeper':<25} {'Count':<8} {'Prob%':<10} {'AvgWin%':<12} {'AvgLoss%':<12} {'RRR':<10} {'ผ่านเกณฑ์':<10}")
        print("-" * 100)
        
        for name in [g[1] for g in gatekeepers]:
            detail = symbol_details[symbol].get(name)
            if detail is None:
                print(f"{name:<25} {'N/A':<8} {'N/A':<10} {'N/A':<12} {'N/A':<12} {'N/A':<10} {'N/A':<10}")
            else:
                passes = "✅" if detail['passes_criteria'] else "❌"
                # คำนวณ AvgWin% และ AvgLoss%
                if 'trader_return' in detail:
                    wins = [r for r in detail['trader_return'] if r > 0]
                    losses = [abs(r) for r in detail['trader_return'] if r <= 0]
                    avgwin = sum(wins) / len(wins) if wins else 0.0
                    avgloss = sum(losses) / len(losses) if losses else 0.0
                else:
                    avgwin = 0.0
                    avgloss = 0.0
                
                print(f"{name:<25} {detail['count']:<8} {detail['final_prob']:<10.1f} {avgwin:<12.2f} {avgloss:<12.2f} {detail['rrr']:<10.2f} {passes:<10}")
    
    # สรุปหุ้นที่ผ่านเกณฑ์
    print("\n" + "="*100)
    print("[PASSING SYMBOLS] หุ้นที่ผ่านเกณฑ์ THAI MARKET (Prob >= 60% | RRR >= 1.2 | Count >= 30)")
    print("="*100)
    
    for r in results:
        print(f"\n📊 {r['gatekeeper']}: {r['symbols_passing']} symbols")
        if r['symbols_passing_list']:
            print(f"{'Symbol':<12} {'Prob%':<10} {'RRR':<8} {'Count':<8}")
            print("-" * 40)
            for s in sorted(r['symbols_passing_list'], key=lambda x: x['prob'], reverse=True)[:10]:
                print(f"{s['symbol']:<12} {s['prob']:<10.1f} {s['rrr']:<8.2f} {s['count']:<8}")
            if len(r['symbols_passing_list']) > 10:
                print(f"... และอีก {len(r['symbols_passing_list']) - 10} symbols")
    
    # สรุปและคำแนะนำ
    print("\n" + "="*100)
    print("[CONCLUSION] สรุปและคำแนะนำ")
    print("="*100)
    
    # หา gatekeeper ที่ดีที่สุด
    best_gatekeeper = max(results, key=lambda x: x['symbols_passing'])
    
    print(f"\n🏆 Gatekeeper ที่ดีที่สุด: {best_gatekeeper['gatekeeper']}")
    print(f"   Symbols ผ่านเกณฑ์: {best_gatekeeper['symbols_passing']}")
    print(f"   Elite Trades: {best_gatekeeper['elite_trades']}")
    print(f"   Elite Prob%: {best_gatekeeper['elite_prob']:.1f}%")
    
    print(f"\n💡 วิเคราะห์:")
    for r in results:
        print(f"   {r['gatekeeper']}:")
        print(f"      ✅ Symbols ผ่านเกณฑ์: {r['symbols_passing']}")
        print(f"      {'✅' if r['elite_trades'] > 0 else '❌'} Elite Trades: {r['elite_trades']} ({r['elite_prob']:.1f}%)")
        print(f"      {'✅' if r['raw_prob'] >= 50 else '❌'} Raw Prob%: {r['raw_prob']:.1f}%")
    
    print(f"\n🎯 คำแนะนำ:")
    if best_gatekeeper['min_prob'] == 55.0:
        print(f"   ✅ ใช้ Gatekeeper เดิม (Prob >= 55%)")
        print(f"      - Symbols ผ่านเกณฑ์มากที่สุด")
        print(f"      - Elite Trades เพียงพอ")
    elif best_gatekeeper['min_prob'] == 60.0:
        print(f"   ✅ ใช้ Gatekeeper สูง (Prob >= 60%)")
        print(f"      - Symbols ผ่านเกณฑ์มากที่สุด")
        print(f"      - Elite Trades สูงสุด")
    else:
        print(f"   ⚠️ Gatekeeper ปัจจุบัน (Prob >= 53%) ไม่ดีที่สุด")
        print(f"   💡 แนะนำ: เปลี่ยนเป็น Prob >= 55% หรือ 60%")
    
    # บันทึกผลลัพธ์
    output_file = os.path.join(DATA_DIR, "gatekeeper_comparison_results.csv")
    comparison_df = pd.DataFrame(results)
    comparison_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 บันทึกผลลัพธ์: {output_file}")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    main()

