"""
Visualizer Module - สร้างกราฟแสดงผลสถิติ
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from config import PLOTS_DIR
import os


class StatsVisualizer:
    """
    Class สำหรับสร้าง visualization จากสถิติ
    """
    
    def __init__(self, output_dir=PLOTS_DIR):
        """
        Args:
            output_dir: directory สำหรับบันทึกกราฟ
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # ตั้งค่า style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_distribution(self, df, symbol, save=True):
        """
        แสดงการกระจายของ % changes
        
        Args:
            df: DataFrame with pct_change column
            symbol: ชื่อหุ้น
            save: บันทึกกราฟหรือไม่
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        axes[0].hist(df['pct_change'].dropna(), bins=50, edgecolor='black', alpha=0.7)
        axes[0].axvline(x=1, color='green', linestyle='--', label='±1% threshold')
        axes[0].axvline(x=-1, color='red', linestyle='--')
        axes[0].set_xlabel('% Change')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title(f'{symbol} - Distribution of Daily Returns')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Box plot
        axes[1].boxplot(df['pct_change'].dropna(), vert=True)
        axes[1].set_ylabel('% Change')
        axes[1].set_title(f'{symbol} - Returns Box Plot')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, f'{symbol}_distribution.png')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"✅ Saved: {filepath}")
        
        plt.close()
    
    def plot_next_day_outcomes(self, stats, symbol, save=True):
        """
        Bar chart แสดงผลลัพธ์วันถัดไป
        
        Args:
            stats: dict จาก stats_analyzer
            symbol: ชื่อหุ้น
            save: บันทึกหรือไม่
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # After Positive Days
        ap = stats['next_day_stats']['after_positive']
        categories = ['Up', 'Down', 'Sideways']
        values = [ap['up'], ap['down'], ap['sideways']]
        colors = ['green', 'red', 'gray']
        
        axes[0].bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        axes[0].set_ylabel('Count')
        axes[0].set_title(f'{symbol} - Next Day After Positive Move (+{stats["threshold"]}%)')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # เพิ่ม labels บนแท่ง
        for i, v in enumerate(values):
            axes[0].text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        # After Negative Days
        an = stats['next_day_stats']['after_negative']
        values = [an['up'], an['down'], an['sideways']]
        
        axes[1].bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        axes[1].set_ylabel('Count')
        axes[1].set_title(f'{symbol} - Next Day After Negative Move (-{stats["threshold"]}%)')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        for i, v in enumerate(values):
            axes[1].text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, f'{symbol}_next_day_outcomes.png')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"✅ Saved: {filepath}")
        
        plt.close()
    
    def plot_probability_matrix(self, probs, symbol, save=True):
        """
        Heatmap แสดงความน่าจะเป็น
        
        Args:
            probs: dict ของ probabilities
            symbol: ชื่อหุ้น
            save: บันทึกหรือไม่
        """
        # สร้าง matrix
        data = []
        labels_row = []
        labels_col = ['Up', 'Down', 'Sideways']
        
        # After Positive
        if 'up_after_positive' in probs:
            data.append([
                probs.get('up_after_positive', 0),
                probs.get('down_after_positive', 0),
                probs.get('sideways_after_positive', 0)
            ])
            labels_row.append('After +ve')
        
        # After Negative
        if 'up_after_negative' in probs:
            data.append([
                probs.get('up_after_negative', 0),
                probs.get('down_after_negative', 0),
                probs.get('sideways_after_negative', 0)
            ])
            labels_row.append('After -ve')
        
        if not data:
            print("⚠️ No probability data to plot")
            return
        
        # สร้าง heatmap
        fig, ax = plt.subplots(figsize=(10, 4))
        
        im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        
        # ตั้งค่า ticks
        ax.set_xticks(np.arange(len(labels_col)))
        ax.set_yticks(np.arange(len(labels_row)))
        ax.set_xticklabels(labels_col)
        ax.set_yticklabels(labels_row)
        
        # เพิ่มค่าในแต่ละช่อง
        for i in range(len(labels_row)):
            for j in range(len(labels_col)):
                text = ax.text(j, i, f'{data[i][j]:.1f}%',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title(f'{symbol} - Probability Matrix (Next Day Outcome)')
        fig.colorbar(im, ax=ax, label='Probability (%)')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, f'{symbol}_probability_matrix.png')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"✅ Saved: {filepath}")
        
        plt.close()
    
    def plot_streak_analysis(self, streaks, symbol, save=True):
        """
        แสดงผลการวิเคราะห์ streaks
        
        Args:
            streaks: list of streak dicts
            symbol: ชื่อหุ้น
            save: บันทึกหรือไม่
        """
        if not streaks:
            print("⚠️ No streaks to plot")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))
        
        # 1. Streak lengths distribution
        lengths = [s['length'] for s in streaks]
        axes[0].hist(lengths, bins=range(min(lengths), max(lengths) + 2), 
                    edgecolor='black', alpha=0.7, color='steelblue')
        axes[0].set_xlabel('Streak Length (days)')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title(f'{symbol} - Streak Length Distribution')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # 2. Next day change after streak ends
        next_changes = [s['next_day_change'] for s in streaks if s['next_day_change'] is not None]
        
        if next_changes:
            axes[1].hist(next_changes, bins=30, edgecolor='black', alpha=0.7, color='coral')
            axes[1].axvline(x=0, color='black', linestyle='--', linewidth=2)
            axes[1].set_xlabel('Next Day % Change After Streak Ends')
            axes[1].set_ylabel('Frequency')
            axes[1].set_title(f'{symbol} - What Happens After Streak Ends?')
            axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, f'{symbol}_streak_analysis.png')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"✅ Saved: {filepath}")
        
        plt.close()
    
    def create_full_report_plots(self, df, stats, symbol):
        """
        สร้างกราฟทั้งหมดในครั้งเดียว
        
        Args:
            df: DataFrame
            stats: statistics dict
            symbol: ชื่อหุ้น
        """
        print(f"\n📊 Creating visualizations for {symbol}...")
        
        self.plot_distribution(df, symbol)
        self.plot_next_day_outcomes(stats, symbol)
        self.plot_probability_matrix(stats['probabilities'], symbol)
        self.plot_streak_analysis(stats['streaks'], symbol)
        
        print(f"✅ All plots saved to {self.output_dir}")


# Example usage
if __name__ == "__main__":
    from data_fetcher import StockDataFetcher
    from stats_analyzer import StatsAnalyzer
    
    # Fetch data
    fetcher = StockDataFetcher()
    df = fetcher.fetch_daily_data('PTT', 'SET', n_bars=2000)
    
    if df is not None:
        # Analyze
        analyzer = StatsAnalyzer(threshold=1.0)
        stats = analyzer.generate_full_report(df)
        
        # Visualize
        visualizer = StatsVisualizer()
        visualizer.create_full_report_plots(df, stats, 'PTT')
