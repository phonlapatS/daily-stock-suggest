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

    def _commit_updates(self, updates):
        """Merge memory updates into the main DataFrame"""
        if not updates:
            return

        # Ensure index is Pattern or MultiIndex (Symbol, Pattern)
        # The CSV has multiple symbols, so we need to update rows based on (Symbol, Pattern)
        # But 'updates' dict currently only has Pattern keys?
        # WAIT: The update_stats loop iterated through 'valid_indices' which are Dates.
        # But updates dict is {pattern: stats}. This aggregates ALL symbols together if we aren't careful?
        # The 'patterns_dict' passed to update_stats comes from ONE symbol's data (presumably).
        # We need to know WHICH symbol we are updating.
        # FIX: The update_stats method needs 'symbol' argument. 
        # For now, let's assume 'updates' needs to track (Symbol, Pattern).
        
        pass # Only partial implementation provided in this step to fix the method signature and logic flow first.
        
    def update_stats(self, new_data_df, patterns_dict, symbol):
        """
        Incrementally update stats with new data for a specific symbol.
        """
        if self.stats_df is None or self.stats_df.empty:
            print("   ⚠️ No existing stats found. Please run batch_processor.py first.")
            return

        # ... (Same initialization logic) ...
        # Convert index to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(new_data_df.index):
            new_data_df.index = pd.to_datetime(new_data_df.index)

        # Determine start date
        start_date = self.last_update + datetime.timedelta(days=1) if self.last_update else None
        
        # If no start_date (first run incrementally), normally we might skip or start from a fixed date.
        # But here let's be safe.
        if not start_date:
            return

        new_rows = new_data_df[new_data_df.index >= start_date]
        if new_rows.empty: return

        # updates = {pattern: {'wins': 0, 'total': 0, 'returns': []}}
        updates = {}
        
        # We need access to pct_change
        pct_change = new_data_df['close'].pct_change()
        
        processed_count = 0
        latest_date = self.last_update

        for date in new_rows.index:
            if date not in patterns_dict: continue
            
            # 1. Get Pattern
            pattern = patterns_dict.get(date)
            
            # 2. Get Next Day Return
            try:
                loc = new_data_df.index.get_loc(date)
                if loc >= len(new_data_df) - 1: continue 
                
                next_return = pct_change.iloc[loc + 1]
                if pd.isna(next_return): continue

                # 3. Determine Win/Loss (Based on existing Logic: Up > 0 is Win? Or Pattern specific?)
                # In Master Stats, 'Chance' col says 'UP' or 'DOWN'.
                # The 'Prob' is the probability of THAT chance.
                # So we need to know the 'Forecast' direction for this pattern to know if it's a 'Win'.
                # But Master Stats ALREADY has 'Prob' derived from history.
                # Here we are UPDATING history. So we just need to count UP outcomes and DOWN outcomes.
                
                if pattern not in updates:
                    updates[pattern] = {'up': 0, 'down': 0, 'returns': []}
                
                if next_return > 0:
                    updates[pattern]['up'] += 1
                else:
                    updates[pattern]['down'] += 1
                    
                updates[pattern]['returns'].append(next_return)
                
                processed_count += 1
                latest_date = date

            except:
                continue

        self._commit_updates(updates, symbol)
        
        if latest_date:
            self.save_state(latest_date)

    def _commit_updates(self, updates, symbol):
        """Merge updates for a specific symbol"""
        if not updates: return
        
        for pat, data in updates.items():
            # Find row for (Symbol, Pattern)
            mask = (self.stats_df['Symbol'] == symbol) & (self.stats_df['Pattern'] == pat)
            
            if not mask.any():
                # New pattern for this symbol? Append?
                # Complex to add new row with all cols. Skip for now or simpler logic.
                continue
                
            idx = self.stats_df[mask].index[0]
            
            # Parse existing Stats "342/637"
            stats_str = str(self.stats_df.at[idx, 'Stats']) # "342/637 (5000)" or just "342/637"
            
            try:
                # Remove (N) suffix if exists
                clean_stats = stats_str.split(' ')[0]
                wins_old, total_old = map(int, clean_stats.split('/'))
            except:
                wins_old, total_old = 0, 0
                
            # Update Counts (Up is Win? NO. Depends on Forecast.)
            # We strictly count occurrences of UP and DOWN.
            # But the stats file stores "Wins / Total". "Win" means match forecast?
            # Or is it "Up / Total"?
            # Looking at 'Chance' col: if Chance=DOWN, Prob=53%. This means 53% chance of DOWN.
            # So Wins = Count(DOWN).
            # We need to check 'Chance' column.
            
            forecast = self.stats_df.at[idx, 'Chance'] # "🔴 DOWN" or "🟢 UP"
            is_forecast_up = 'UP' in str(forecast)
            
            new_wins = data['up'] if is_forecast_up else data['down']
            new_total = data['up'] + data['down']
            
            total_final = total_old + new_total
            wins_final = wins_old + new_wins
            
            # Update Stats String
            self.stats_df.at[idx, 'Stats'] = f"{wins_final}/{total_final}"
            
            # Update Prob %
            if total_final > 0:
                prob = (wins_final / total_final) * 100
                self.stats_df.at[idx, 'Prob'] = f"{int(prob)}%"
                
            # Update Avg Return (Weighted)
            # data['returns'] is list of floats.
            # current avg is self.stats_df.at[idx, 'avg_return']
            # We need a weighted average update.
            old_avg = float(self.stats_df.at[idx, 'avg_return'])
            sum_old = old_avg * total_old
            sum_new = sum(data['returns']) * 100 # Convert to %? Check CSV. 
            # CSV example: -0.0433... This looks like raw decimal? OR percent?
            # 1_Days_Up return 0.22... likely 0.22%?
            # If standard pct_change is 0.01 (1%), let's assume CSV is % value.
            # If CSV is 0.22, that is 0.22%.
            # pct_change sum needs * 100.
            
            avg_final = (sum_old + (sum_new)) / total_final
            self.stats_df.at[idx, 'avg_return'] = avg_final
            
        # Save happens in the caller or explicit save
        self.stats_df.to_csv(self.stats_path, index=False)

        
    def get_stats(self):
        return self.stats_df
