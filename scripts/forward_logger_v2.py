#!/usr/bin/env python
"""
forward_logger_v2.py - Enhanced Forward Testing Logger
=======================================================
Improved version with better tracking and statistics.
"""
import pandas as pd
import os
from datetime import datetime

class ForwardLogger:
    """Enhanced forward testing logger with comprehensive tracking."""
    
    def __init__(self, log_path='logs/forward_test_v2.csv'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(log_path):
            log_path = os.path.join(base_dir, log_path)
        
        self.log_path = log_path
        self.columns = [
            'Date', 'Symbol', 'Exchange', 'Pattern', 'Forecast',
            'Confidence', 'Expected_RR', 'Sample_Size', 'Entry_Price', 
            'Target_Price', 'Stop_Loss', 'Actual_Close', 'Actual_Return', 
            'Win_Loss', 'Table', 'Notes'
        ]
        
        # Create directory if doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Create file if doesn't exist
        if not os.path.exists(self.log_path):
            pd.DataFrame(columns=self.columns).to_csv(self.log_path, index=False)
            print(f"✅ Created forward test log: {self.log_path}")
    
    def log_signal(self, symbol, exchange, pattern, forecast, confidence, 
                   expected_rr, sample_size, entry_price, avg_win_pct, 
                   avg_loss_pct, table='Unknown'):
        """
        Log a new trading signal.
        
        Args:
            table: 'Thai Strict', 'Thai Balanced', 'Global Winners', etc.
        """
        # Calculate target and stop
        if forecast == 'UP':
            target = entry_price * (1 + avg_win_pct / 100)
            stop = entry_price * (1 - avg_loss_pct / 100)
        else:  # DOWN
            target = entry_price * (1 - avg_win_pct / 100)
            stop = entry_price * (1 + avg_loss_pct / 100)
        
        new_row = {
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Symbol': symbol,
            'Exchange': exchange,
            'Pattern': pattern,
            'Forecast': forecast,
            'Confidence': round(confidence, 1),
            'Expected_RR': round(expected_rr, 2),
            'Sample_Size': sample_size,
            'Entry_Price': round(entry_price, 2),
            'Target_Price': round(target, 2),
            'Stop_Loss': round(stop, 2),
            'Actual_Close': None,
            'Actual_Return': None,
            'Win_Loss': 'PENDING',
            'Table': table,
            'Notes': ''
        }
        
        df = pd.read_csv(self.log_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.log_path, index=False)
        
        print(f"✅ [{table}] {symbol} {forecast} @ {entry_price:.2f} (Conf: {confidence:.1f}%, RR: {expected_rr:.2f}, N={sample_size})")
    
    def update_result(self, symbol, date, actual_close, notes=''):
        """Update with actual result."""
        df = pd.read_csv(self.log_path)
        
        # Find the pending trade
        mask = (df['Symbol'] == symbol) & (df['Date'] == date) & (df['Win_Loss'] == 'PENDING')
        
        if not mask.any():
            print(f"❌ No pending trade found for {symbol} on {date}")
            print(f"   Available pending trades:")
            pending = df[df['Win_Loss'] == 'PENDING']
            for _, row in pending.iterrows():
                print(f"   - {row['Date']} {row['Symbol']}")
            return
        
        idx = df[mask].index[0]
        entry = df.loc[idx, 'Entry_Price']
        forecast = df.loc[idx, 'Forecast']
        
        # Calculate return
        actual_return = ((actual_close - entry) / entry) * 100
        
        # Determine win/loss
        if forecast == 'UP':
            win_loss = 'WIN' if actual_return > 0 else 'LOSS'
        else:  # DOWN
            win_loss = 'WIN' if actual_return < 0 else 'LOSS'
            actual_return = -actual_return  # Flip for short
        
        # Update row
        df.loc[idx, 'Actual_Close'] = round(actual_close, 2)
        df.loc[idx, 'Actual_Return'] = round(actual_return, 2)
        df.loc[idx, 'Win_Loss'] = win_loss
        df.loc[idx, 'Notes'] = notes
        
        df.to_csv(self.log_path, index=False)
        
        icon = "✅" if win_loss == 'WIN' else "❌"
        print(f"{icon} Updated: {symbol} {win_loss} ({actual_return:+.2f}%)")
    
    def get_stats(self, by_table=True):
        """Calculate statistics."""
        df = pd.read_csv(self.log_path)
        completed = df[df['Win_Loss'].isin(['WIN', 'LOSS'])]
        
        if len(completed) == 0:
            print("⚠️ No completed trades yet.")
            return
        
        total = len(completed)
        wins = len(completed[completed['Win_Loss'] == 'WIN'])
        win_rate = (wins / total) * 100
        
        avg_return = completed['Actual_Return'].mean()
        total_return = completed['Actual_Return'].sum()
        
        print("\n" + "=" * 70)
        print("📊 FORWARD TEST STATISTICS")
        print("=" * 70)
        print(f"Total Trades: {total}")
        print(f"Wins: {wins}")
        print(f"Losses: {total - wins}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Avg Return per Trade: {avg_return:+.2f}%")
        print(f"Cumulative Return: {total_return:+.2f}%")
        
        if by_table and 'Table' in completed.columns:
            print(f"\n📈 By Table:")
            print("-" * 70)
            
            by_table_stats = completed.groupby('Table').agg({
                'Win_Loss': lambda x: (x == 'WIN').sum() / len(x) * 100,
                'Actual_Return': ['mean', 'sum', 'count']
            }).round(2)
            
            for table in by_table_stats.index:
                trades = int(by_table_stats.loc[table, ('Actual_Return', 'count')])
                wr = by_table_stats.loc[table, ('Win_Loss', '<lambda>')]
                avg_ret = by_table_stats.loc[table, ('Actual_Return', 'mean')]
                tot_ret = by_table_stats.loc[table, ('Actual_Return', 'sum')]
                
                print(f"{table:<20} | Trades: {trades:<4} | WR: {wr:<6.1f}% | Avg: {avg_ret:+6.2f}% | Total: {tot_ret:+7.2f}%")
        
        print("=" * 70)
    
    def get_pending(self):
        """Show pending trades."""
        df = pd.read_csv(self.log_path)
        pending = df[df['Win_Loss'] == 'PENDING']
        
        if len(pending) == 0:
            print("✅ No pending trades.")
            return
        
        print(f"\n⏳ PENDING TRADES ({len(pending)})")
        print("=" * 70)
        
        for _, row in pending.iterrows():
            print(f"{row['Date']} | {row['Symbol']} {row['Forecast']} @ {row['Entry_Price']:.2f}")
            print(f"   Table: {row['Table']} | Pattern: {row['Pattern']}")
            print(f"   Conf: {row['Confidence']:.1f}% | RR: {row['Expected_RR']:.2f} | N={row['Sample_Size']}")
            print(f"   Target: {row['Target_Price']:.2f} | Stop: {row['Stop_Loss']:.2f}")
            print()

if __name__ == "__main__":
    import sys
    
    logger = ForwardLogger()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'stats':
            logger.get_stats()
        
        elif command == 'pending':
            logger.get_pending()
        
        elif command == 'update':
            if len(sys.argv) < 5:
                print("Usage: python forward_logger_v2.py update SYMBOL DATE PRICE [NOTES]")
                sys.exit(1)
            
            symbol = sys.argv[2]
            date = sys.argv[3]
            price = float(sys.argv[4])
            notes = sys.argv[5] if len(sys.argv) > 5 else ''
            
            logger.update_result(symbol, date, price, notes)
            logger.get_stats()
        
        else:
            print("Unknown command. Available: stats, pending, update")
    
    else:
        print("\n📋 Forward Test Logger V2")
        print("=" * 50)
        print("Commands:")
        print("  python forward_logger_v2.py stats     - Show statistics")
        print("  python forward_logger_v2.py pending   - Show pending trades")
        print("  python forward_logger_v2.py update SYMBOL DATE PRICE [NOTES]")
        print("\nExample:")
        print("  python forward_logger_v2.py update PTT 2026-02-10 125.50")
