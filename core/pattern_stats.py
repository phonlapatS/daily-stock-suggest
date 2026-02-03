import pandas as pd
import numpy as np
import os
import datetime

class PatternStatsManager:
    """
    Manages incremental updates for Master Pattern Stats.
    Instead of recalculating stats from scratch every day (expensive),
    it loads existing stats and adds only the new data points.
    """
    
    def __init__(self, stats_path='data/Master_Pattern_Stats.csv'):
        self.stats_path = stats_path
        self.stats_df = None
        self.last_update = None
        
        # Load existing stats if available
        self._load_stats()
        
    def _load_stats(self):
        """Load stats CSV and metadata"""
        if os.path.exists(self.stats_path):
            try:
                self.stats_df = pd.read_csv(self.stats_path)
                # Check for metadata in the file or companion file
                # For simplicity, we'll infer last update from the data or a separate state file
                # But for V3.3, let's look for a 'last_update' column or similar if we decide to store it there.
                # Actually, strictly keeping it in a separate state file is cleaner for CSV structure.
                self.load_state()
            except Exception as e:
                print(f"⚠️ Failed to load stats: {e}")
                self.stats_df = pd.DataFrame()
        else:
            self.stats_df = pd.DataFrame()

    def load_state(self):
        """Load the last update date from state file"""
        state_path = self.stats_path.replace('.csv', '_state.json')
        if os.path.exists(state_path):
            try:
                import json
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    self.last_update = pd.to_datetime(state.get('last_update'))
            except:
                self.last_update = None
        else:
            self.last_update = None

    def save_state(self, last_date):
        """Save the last update date"""
        state_path = self.stats_path.replace('.csv', '_state.json')
        import json
        with open(state_path, 'w') as f:
            json.dump({'last_update': str(last_date.date())}, f)
        self.last_update = last_date

    def _commit_updates(self, updates, symbol):
        """
        Merge memory updates into the main DataFrame (Incremental Commit).
        
        Args:
            updates (dict): New stats {pattern: {'up': count, 'down': count, 'returns': [list]}}
            symbol (str): The symbol being updated (e.g., 'PTT')
        """
        if not updates: return
        
        for pat, data in updates.items():
            # Find row for (Symbol, Pattern)
            mask = (self.stats_df['Symbol'] == symbol) & (self.stats_df['Pattern'] == pat)
            
            if not mask.any():
                # Note: New patterns encountered incrementally are currently ignored 
                # to maintain the integrity of the original Master Stats structure.
                continue
                
            idx = self.stats_df[mask].index[0]
            
            # 1. Parse existing Stats "Wins/Total"
            stats_str = str(self.stats_df.at[idx, 'Stats']) # e.g., "342/637"
            
            try:
                clean_stats = stats_str.split(' ')[0] # Remove any suffix
                wins_old, total_old = map(int, clean_stats.split('/'))
            except:
                wins_old, total_old = 0, 0
                
            # 2. Determine Wins vs Losses based on Forecast Direction
            # If Forecast is UP, then 'up' count = Win.
            # If Forecast is DOWN, then 'down' count = Win.
            forecast = self.stats_df.at[idx, 'Chance'] # "🔴 DOWN" or "🟢 UP"
            is_forecast_up = 'UP' in str(forecast)
            
            new_wins = data['up'] if is_forecast_up else data['down']
            new_total = data['up'] + data['down']
            
            total_final = total_old + new_total
            wins_final = wins_old + new_wins
            
            # 3. Update Stats String
            self.stats_df.at[idx, 'Stats'] = f"{wins_final}/{total_final}"
            
            # 4. Update Probability %
            if total_final > 0:
                prob = (wins_final / total_final) * 100
                self.stats_df.at[idx, 'Prob'] = f"{int(prob)}%"
                
            # 5. Update Avg Return (Weighted Average)
            # Weighted formula: ((Old_Avg * Old_Count) + Sum_New_Returns) / New_Total
            old_avg = float(self.stats_df.at[idx, 'avg_return'])
            sum_old = old_avg * total_old
            
            # Note: new_data_df returns were raw (e.g., 0.05), but Stats file stores % (e.g., 5.0)
            # So we multiply new sum by 100.
            sum_new = sum(data['returns']) * 100 
            
            avg_final = (sum_old + sum_new) / total_final
            self.stats_df.at[idx, 'avg_return'] = round(avg_final, 2)
            
        # Verify save persistence
        self.stats_df.to_csv(self.stats_path, index=False)

        
    def get_stats(self):
        return self.stats_df
