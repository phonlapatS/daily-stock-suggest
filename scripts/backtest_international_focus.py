#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backtest_international_focus.py - Focus Backtest: US, Taiwan, China/HK
================================================================================
ทดสอบ 3 ตลาดต่างประเทศด้วย Risk Management V7.0
- US: Hybrid Volatility (HIGH_VOL → REVERSION, LOW_VOL → TREND)
- Taiwan: Regime-Aware (BULL → TREND, BEAR/SIDEWAYS → REVERSION)
- China/HK: Mean Reversion (เหมือนไทย)
"""

import sys
import os
import time
import pandas as pd
import numpy as np

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tvDatafeed import TvDatafeed, Interval
from core.data_cache import get_data_with_cache

# Direct import of backtest function (avoid double-wrapping stdout)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backtest.py'), encoding='utf-8').read().split('def main')[0])

# =========================================================================
# Test stocks for each market
# =========================================================================
INTERNATIONAL_STOCKS = {
    'US': {
        'label': '🇺🇸 US Market (NASDAQ/NYSE)',
        'stocks': [
            ('NVDA', 'NASDAQ'),
            ('AAPL', 'NASDAQ'),
            ('MSFT', 'NASDAQ'),
            ('GOOGL', 'NASDAQ'),
            ('AMZN', 'NASDAQ'),
            ('TSLA', 'NASDAQ'),
            ('META', 'NASDAQ'),
        ]
    },
    'TW': {
        'label': '🇹🇼 Taiwan Market (TWSE)',
        'stocks': [
            ('2330', 'TWSE'),   # TSMC
            ('2454', 'TWSE'),   # MediaTek
            ('2317', 'TWSE'),   # Hon Hai (Foxconn)
            ('2303', 'TWSE'),   # UMC
            ('2308', 'TWSE'),   # Delta Electronics
        ]
    },
    'CN': {
        'label': '🇨🇳 China/HK Market (HKEX)',
        'stocks': [
            ('700', 'HKEX'),    # Tencent
            ('9988', 'HKEX'),   # Alibaba
            ('3690', 'HKEX'),   # Meituan
            ('1810', 'HKEX'),   # Xiaomi
            ('1211', 'HKEX'),   # BYD
        ]
    }
}

def main():
    n_bars = 2000
    
    print("\n" + "="*120)
    print("🌍 International Markets Focused Backtest (V7.0 Risk Management)")
    print("="*120)
    print(f"📋 Risk Management: SL 2% / TP 4% / Max Hold 5 days")
    print(f"📊 Test Bars: {n_bars}")
    print("="*120)
    
    tv = TvDatafeed()
    
    market_results = {}
    
    for market_code, market_info in INTERNATIONAL_STOCKS.items():
        print(f"\n{'='*120}")
        print(f"{market_info['label']}")
        print(f"{'='*120}")
        
        market_results[market_code] = {
            'label': market_info['label'],
            'results': [],
            'all_predictions': []
        }
        
        for symbol, exchange in market_info['stocks']:
            print(f"\n   [{symbol}]...", end=" ")
            
            try:
                result = backtest_single(
                    tv, symbol, exchange, 
                    n_bars=n_bars,
                    verbose=False,
                    use_risk_mgmt=True,
                    stop_loss=2.0,
                    take_profit=4.0,
                    max_hold=5
                )
                
                if result and result.get('total', 0) > 0:
                    result['group'] = market_code
                    market_results[market_code]['results'].append(result)
                    
                    total_ret = sum(p['trader_return'] for p in result.get('detailed_predictions', []))
                    print(f"✅ {result['total']} trades, Acc: {result['accuracy']:.1f}%, RRR: {result['risk_reward']:.2f}, Return: {total_ret:.1f}%")
                    
                    # Collect predictions
                    for p in result.get('detailed_predictions', []):
                        p['symbol'] = symbol
                        p['exchange'] = exchange
                        p['market'] = market_code
                        market_results[market_code]['all_predictions'].append(p)
                else:
                    print(f"❌ No signals")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1.5)
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*120)
    print("📊 INTERNATIONAL MARKETS SUMMARY")
    print("="*120)
    print(f"📋 Risk Management: SL 2% / TP 4% / Max Hold 5 days")
    print("="*120)
    
    # Per-stock table
    print(f"\n{'Symbol':<10} {'Market':<6} {'Trades':<8} {'Win':<6} {'Accuracy':<10} {'AvgWin%':<10} {'AvgLoss%':<10} {'RRR':<8} {'Return%':<10}")
    print("-"*90)
    
    grand_total = 0
    grand_correct = 0
    grand_return = 0
    
    for market_code, mdata in market_results.items():
        for r in mdata['results']:
            total_ret = sum(p['trader_return'] for p in r.get('detailed_predictions', []))
            print(f"{r['symbol']:<10} {market_code:<6} {r['total']:<8} {r['correct']:<6} {r['accuracy']:.1f}%      {r['avg_win']:<10.2f} {r['avg_loss']:<10.2f} {r['risk_reward']:<8.2f} {total_ret:<10.2f}")
            grand_total += r['total']
            grand_correct += r['correct']
            grand_return += total_ret
    
    print("-"*90)
    grand_acc = (grand_correct / grand_total * 100) if grand_total > 0 else 0
    print(f"{'TOTAL':<10} {'ALL':<6} {grand_total:<8} {grand_correct:<6} {grand_acc:.1f}%      {'':10} {'':10} {'':8} {grand_return:<10.2f}")
    
    # Per-market summary
    print(f"\n{'='*120}")
    print(f"📊 PER-MARKET ANALYSIS")
    print(f"{'='*120}")
    
    for market_code, mdata in market_results.items():
        preds = mdata['all_predictions']
        if not preds:
            continue
        
        total = len(preds)
        wins = [p for p in preds if p['correct'] == 1]
        losses = [p for p in preds if p['correct'] == 0]
        accuracy = len(wins) / total * 100
        
        avg_win = np.mean([abs(p['trader_return']) for p in wins]) if wins else 0
        avg_loss = np.mean([abs(p['trader_return']) for p in losses]) if losses else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        total_return = sum(p['trader_return'] for p in preds)
        
        # Exit reason breakdown
        exit_reasons = {}
        for p in preds:
            reason = p.get('exit_reason', '1DAY')
            if reason not in exit_reasons:
                exit_reasons[reason] = {'count': 0, 'wins': 0, 'return': 0}
            exit_reasons[reason]['count'] += 1
            exit_reasons[reason]['wins'] += 1 if p['correct'] == 1 else 0
            exit_reasons[reason]['return'] += p['trader_return']
        
        # Strategy breakdown
        strategies = {}
        for p in preds:
            strat = p.get('strategy', 'UNKNOWN')
            if strat not in strategies:
                strategies[strat] = {'count': 0, 'wins': 0, 'return': 0}
            strategies[strat]['count'] += 1
            strategies[strat]['wins'] += 1 if p['correct'] == 1 else 0
            strategies[strat]['return'] += p['trader_return']
        
        print(f"\n{mdata['label']}:")
        print(f"   Trades: {total}, Accuracy: {accuracy:.2f}%")
        print(f"   AvgWin: {avg_win:.2f}%, AvgLoss: {avg_loss:.2f}%, RRR: {rrr:.2f}")
        print(f"   Total Return: {total_return:.2f}%")
        
        print(f"\n   Exit Reasons:")
        print(f"   {'Reason':<15} {'Count':<8} {'Win%':<10} {'Avg Ret%':<10}")
        print(f"   {'-'*45}")
        for reason in ['TAKE_PROFIT', 'MAX_HOLD', 'STOP_LOSS']:
            if reason in exit_reasons:
                data = exit_reasons[reason]
                win_pct = data['wins'] / data['count'] * 100 if data['count'] > 0 else 0
                avg_ret = data['return'] / data['count'] if data['count'] > 0 else 0
                print(f"   {reason:<15} {data['count']:<8} {win_pct:<10.1f} {avg_ret:<10.4f}")
        
        if len(strategies) > 1:
            print(f"\n   Strategy Breakdown:")
            for strat, data in strategies.items():
                win_pct = data['wins'] / data['count'] * 100 if data['count'] > 0 else 0
                avg_ret = data['return'] / data['count'] if data['count'] > 0 else 0
                print(f"   {strat:<20} {data['count']:<8} Win%: {win_pct:<8.1f} AvgRet: {avg_ret:<10.4f}")
    
    # Recommendations
    print(f"\n{'='*120}")
    print(f"💡 RECOMMENDATIONS")
    print(f"{'='*120}")
    
    for market_code, mdata in market_results.items():
        preds = mdata['all_predictions']
        if not preds:
            continue
        
        total = len(preds)
        wins = [p for p in preds if p['correct'] == 1]
        accuracy = len(wins) / total * 100
        avg_win = np.mean([abs(p['trader_return']) for p in wins]) if wins else 0
        avg_loss_list = [p for p in preds if p['correct'] == 0]
        avg_loss = np.mean([abs(p['trader_return']) for p in avg_loss_list]) if avg_loss_list else 0
        rrr = avg_win / avg_loss if avg_loss > 0 else 0
        total_return = sum(p['trader_return'] for p in preds)
        
        status = "✅" if total_return > 0 and rrr >= 1.5 else "⚠️" if total_return > 0 else "❌"
        
        print(f"\n   {status} {mdata['label']}:")
        print(f"      Accuracy: {accuracy:.1f}%, RRR: {rrr:.2f}, Return: {total_return:.1f}%")
        
        if rrr >= 1.5 and total_return > 0:
            print(f"      → ดีแล้ว! RRR >= 1.5 และกำไร")
        elif total_return > 0:
            print(f"      → กำไร แต่ RRR ยังต่ำ ควรปรับ SL/TP")
        else:
            print(f"      → ขาดทุน ต้องปรับ Strategy/Parameters")
        
        # Specific advice
        # Check TP hit rate
        tp_count = sum(1 for p in preds if p.get('exit_reason') == 'TAKE_PROFIT')
        sl_count = sum(1 for p in preds if p.get('exit_reason') == 'STOP_LOSS')
        tp_ratio = tp_count / (tp_count + sl_count) * 100 if (tp_count + sl_count) > 0 else 0
        
        print(f"      TP/SL Ratio: {tp_count} TP vs {sl_count} SL ({tp_ratio:.1f}% TP)")
        
        if tp_ratio < 40:
            print(f"      ⚠️  SL โดนบ่อย → ควรขยาย SL หรือลด TP")
        elif tp_ratio > 60:
            print(f"      ✅ TP โดนบ่อย → Strategy ดี")
    
    print(f"\n{'='*120}")

if __name__ == "__main__":
    main()

