#!/usr/bin/env python
"""
Quick Taiwan Parameter Test - Manual Testing Helper
ช่วยบันทึกผลลัพธ์จากการทดสอบแต่ละ combination
"""

import pandas as pd
from datetime import datetime
import os

def record_test_result(test_num, min_prob, n_bars, results_dict):
    """
    Record test result to CSV
    
    Args:
        test_num: Test number (1-12)
        min_prob: min_prob value tested
        n_bars: n_bars value tested
        results_dict: Dictionary with results from calculate_metrics output
    """
    # Read existing results or create new
    results_file = 'docs/TAIWAN_PARAMETER_TEST_RESULTS.csv'
    
    if os.path.exists(results_file):
        df = pd.read_csv(results_file)
    else:
        df = pd.DataFrame(columns=[
            'test_num', 'min_prob', 'n_bars', 'timestamp',
            'passing_stocks', 'passing_symbols',
            'avg_prob', 'avg_rrr', 'avg_count', 'total_trades',
            'best_prob', 'best_rrr', 'best_prob_symbol', 'best_rrr_symbol',
            'details'
        ])
    
    # Parse results from calculate_metrics output
    # Expected format: results_dict from user input or from parsing terminal output
    
    new_row = {
        'test_num': test_num,
        'min_prob': min_prob,
        'n_bars': n_bars,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'passing_stocks': results_dict.get('passing_stocks', 0),
        'passing_symbols': ', '.join(results_dict.get('passing_symbols', [])),
        'avg_prob': results_dict.get('avg_prob', 0),
        'avg_rrr': results_dict.get('avg_rrr', 0),
        'avg_count': results_dict.get('avg_count', 0),
        'total_trades': results_dict.get('total_trades', 0),
        'best_prob': results_dict.get('best_prob', 0),
        'best_rrr': results_dict.get('best_rrr', 0),
        'best_prob_symbol': results_dict.get('best_prob_symbol', ''),
        'best_rrr_symbol': results_dict.get('best_rrr_symbol', ''),
        'details': str(results_dict.get('details', ''))
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(results_file, index=False)
    
    print(f"\n✅ Test #{test_num} recorded!")
    print(f"   min_prob: {min_prob}%, n_bars: {n_bars}")
    print(f"   Passing stocks: {results_dict.get('passing_stocks', 0)}")
    print(f"   Results saved to: {results_file}")

def show_test_matrix():
    """Show test matrix"""
    print("\n" + "="*80)
    print("Taiwan Parameter Test Matrix")
    print("="*80)
    
    tests = [
        (1, 51.0, 2500, "Count (aggressive)"),
        (2, 51.5, 2500, "Baseline (V12.3)"),
        (3, 52.0, 2500, "Quality (V12.2)"),
        (4, 52.5, 2500, "High quality"),
    ]
    
    print(f"\n{'Test':<6} {'min_prob':<10} {'n_bars':<8} {'Focus':<40}")
    print("-" * 80)
    for test_num, min_prob, n_bars, focus in tests:
        print(f"{test_num:<6} {min_prob:<10.1f}% {n_bars:<8} {focus:<40}")
    
    print("\n" + "="*80)

def parse_results_from_terminal():
    """Helper to parse results from terminal output"""
    print("\n" + "="*80)
    print("How to Record Results")
    print("="*80)
    print("\nAfter running backtest and calculate_metrics, copy the Taiwan section:")
    print("\nExample:")
    print("[TAIWAN MARKET] (Matches: Prob >= 53% | RRR >= 1.3 | Count 25-150)")
    print("DELTA      TW               55    70.9%      2.07%      1.09%   1.89")
    print("HON-HAI    TW               96    61.5%      1.56%      1.19%   1.31")
    print("\nThen use record_test_result() function to save.")
    print("="*80)

def main():
    """Main function"""
    show_test_matrix()
    parse_results_from_terminal()
    
    print("\n" + "="*80)
    print("Quick Test Helper")
    print("="*80)
    print("\nTo record a test result, use:")
    print("  record_test_result(test_num, min_prob, n_bars, results_dict)")
    print("\nExample:")
    print("  results = {")
    print("      'passing_stocks': 2,")
    print("      'passing_symbols': ['2308', '2317'],")
    print("      'avg_prob': 66.2,")
    print("      'avg_rrr': 1.60,")
    print("      'avg_count': 75.5,")
    print("      'total_trades': 151,")
    print("      'best_prob': 70.9,")
    print("      'best_rrr': 1.89,")
    print("      'best_prob_symbol': '2308',")
    print("      'best_rrr_symbol': '2308'")
    print("  }")
    print("  record_test_result(4, 51.5, 2000, results)")

if __name__ == '__main__':
    main()

