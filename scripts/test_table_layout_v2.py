
from tabulate import tabulate

def generate_report_test():
    print("\n" + "="*95)
    print("📊 FRACTAL PREDICTION REPORT (Layout Test)")
    print("="*95)
    
    # Dummy data simulating processor output
    results = [
        {'symbol': 'AAPL', 'price': 150.00, 'threshold': 1.5, 'change_pct': 1.2, 'pattern_display': '++', 'avg_return': 0.5, 'bull_prob': 65, 'bear_prob': 35, 'matches': 20, 'group': 'TEST'},
        {'symbol': 'GOOGL', 'price': 2800.00, 'threshold': 1.2, 'change_pct': -0.8, 'pattern_display': '-+', 'avg_return': -0.8, 'bull_prob': 40, 'bear_prob': 60, 'matches': 15, 'group': 'TEST'},
        {'symbol': 'MSFT', 'price': 300.00, 'threshold': 1.0, 'change_pct': 0.1, 'pattern_display': '.', 'avg_return': 0.0, 'bull_prob': 50, 'bear_prob': 50, 'matches': 10, 'group': 'TEST'},
        {'symbol': 'HIGH_PROB', 'price': 100.00, 'threshold': 1.0, 'change_pct': 2.0, 'pattern_display': '++', 'avg_return': 2.0, 'bull_prob': 90, 'bear_prob': 10, 'matches': 12, 'group': 'TEST'},
    ]

    # Apply sorting logic used in main.py
    for r in results:
        avg_ret = r['avg_return']
        if avg_ret > 0: r['_sort_prob'] = r['bull_prob']
        elif avg_ret < 0: r['_sort_prob'] = r['bear_prob']
        else: r['_sort_prob'] = 50.0
    
    results.sort(key=lambda x: (-x['_sort_prob'], -x['matches'], x['symbol']))

    
    # 3. Table Layout
    # Columns (Left-to-Right): Symbol, Price, Threshold, Chg%, Pattern, Chance, Prob, Stats, Exp.Move
    header = f"{'Symbol':<10} {'Price':>10} {'Threshold':>12} {'Chg%':>10} {'Pattern':^12} {'Chance':^10} {'Prob.':>8} {'Stats':>12} {'Exp. Move':>12}"
    
    print("-" * 105)
    print(header)
    print("-" * 105)

    for r in results:
        # Logic: Predict & Prob
        avg_ret = r['avg_return']
        if avg_ret > 0:
            chance = "🟢 UP"
            prob_val = r['bull_prob']
            win_count = int(r['matches'] * (prob_val / 100))
        elif avg_ret < 0:
            chance = "🔴 DOWN"
            prob_val = r['bear_prob']
            win_count = int(r['matches'] * (prob_val / 100))
        else:
            chance = "⚪ SIDE"
            prob_val = 50.0
            win_count = 0
        
        # Get hybrid pattern (context + current)
        pattern = r.get('pattern_display', '.')
        
            # Formatting
        price_str = f"{r['price']:,.2f}"
        thresh_str = f"±{r['threshold']:.2f}%"
        chg_str   = f"{r['change_pct']:+.2f}%"
        prob_str  = f"{int(prob_val)}%"
        stats_str = f"{win_count}/{r['matches']}"
        exp_str   = f"{avg_ret:+.2f}%"
        
        # Print Row (Hybrid pattern display)
        print(f"{r['symbol']:<10} {price_str:>10} {thresh_str:>12} {chg_str:>10} {pattern:^12} {chance:^10} {prob_str:>8} {stats_str:>12} {exp_str:>12}")

    print("-" * 105)

if __name__ == "__main__":
    generate_report_test()
