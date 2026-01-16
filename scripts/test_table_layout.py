
def generate_report(results):
    print("\n" + "="*115)
    print("📊 FRACTAL DNA REPORT (High Confidence Only)")
    print("="*115)
    
    groups = {
        "GROUP_A_THAI": "🇹🇭 THAI MARKET (SET100+)",
    }
    
    for group_key, title in groups.items():

        filtered_data = []
        for r in results:
            # Fake Filter logic for test
            if r['matches'] >= 10 and (r['bull_prob'] >= 60.0 or r['bear_prob'] >= 60.0):
                # Add prob to dict for sorting (Simulated)
                r['_sort_prob'] = max(r['bull_prob'], r['bear_prob'])
                filtered_data.append(r)
        
        print(f"\n{title}")
        
        # Sort by: 1. Probability (Dominant) DESC, 2. Events DESC
        filtered_data.sort(key=lambda x: (x['_sort_prob'], x['matches']), reverse=True)
        
        # 3. Table Layout
        # Columns (Left-to-Right): Symbol, Price, Threshold, Chg%, Pattern(DNA), History, Predict, Prob, Stats, Exp.Move
        header = f"{'Symbol':<10} {'Price':>10} {'Threshold':>12} {'Chg%':>10} {'Pattern (DNA)':^16} {'History':>10} {'Predict':<12} {'Prob.':>8} {'Stats':>12} {'Exp. Move':>12}"
        
        print("-" * 115)
        print(header)
        print("-" * 115)

        for r in filtered_data:
            # Logic: Predict & Prob
            avg_ret = r['avg_return']
            if avg_ret > 0:
                predict = "🟢 UP" 
                prob_val = r['bull_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            elif avg_ret < 0:
                predict = "🔴 DOWN"
                prob_val = r['bear_prob']
                win_count = int(r['matches'] * (prob_val / 100))
            else:
                predict = "⚪ NEUTRAL"
                prob_val = 50.0
                win_count = 0
            
            # Logic: DNA Icon Mapping
            dna_raw = r.get('dna_pattern', '...')
            dna_icon = ""
            for char in dna_raw:
                if char == '+': dna_icon += "🟢"
                elif char == '-': dna_icon += "🔴"
                else: dna_icon += "⚪"
            
             # Formatting
            price_str = f"{r['price']:,.2f}"
            thresh_str = f"±{r['threshold']:.2f}%"  # New Column
            chg_str   = f"{r['change_pct']:+.2f}%"   # New Column
            # Pattern (DNA) is dna_icon
            hist_str  = f"{r['matches']}"
            prob_str  = f"{int(prob_val)}%"
            stats_str = f"{win_count}/{r['matches']}"
            exp_str   = f"{avg_ret:+.2f}%"
            
            # Print Row
            print(f"{r['symbol']:<10} {price_str:>10} {thresh_str:>12} {chg_str:>10} {dna_icon:^14} {hist_str:>10} {predict:<12} {prob_str:>8} {stats_str:>12} {exp_str:>12}")

        print("-" * 115)

# Dummy Data
mock_results = [
    {
        'group': 'GROUP_A_THAI', 'symbol': 'ADVANC', 'price': 215.00, 'matches': 150, 
        'avg_return': 1.5, 'bull_prob': 85.0, 'bear_prob': 15.0, 'dna_pattern': '++-', 'max_risk': -2.0,
        'threshold': 1.5, 'change_pct': 2.0
    },
    {
        'group': 'GROUP_A_THAI', 'symbol': 'PTT', 'price': 32.50, 'matches': 300, 
        'avg_return': -0.8, 'bull_prob': 30.0, 'bear_prob': 70.0, 'dna_pattern': '--+', 'max_risk': -5.0,
        'threshold': 1.0, 'change_pct': -1.2
    },
    {
        'group': 'GROUP_A_THAI', 'symbol': 'KBANK', 'price': 130.00, 'matches': 20, 
        'avg_return': 2.1, 'bull_prob': 65.0, 'bear_prob': 35.0, 'dna_pattern': '..+', 'max_risk': -3.0,
        'threshold': 1.8, 'change_pct': 1.9
    },
    {
        'group': 'GROUP_A_THAI', 'symbol': 'AOT', 'price': 60.25, 'matches': 12, 
        'avg_return': -1.2, 'bull_prob': 40.0, 'bear_prob': 60.0, 'dna_pattern': '...', 'max_risk': -4.0,
        'threshold': 1.2, 'change_pct': 0.5
    },
     {  # Should be filtered out
        'group': 'GROUP_A_THAI', 'symbol': 'SCB', 'price': 105.50, 'matches': 5, 
        'avg_return': 0.0, 'bull_prob': 50.0, 'bear_prob': 50.0, 'dna_pattern': '...', 'max_risk': 0.0,
        'threshold': 1.0, 'change_pct': 0.1
    }
]

if __name__ == "__main__":
    generate_report(mock_results)
