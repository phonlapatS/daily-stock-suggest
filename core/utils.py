"""
Utility functions for Stock Statistics Extraction System
"""

import json
import os
from datetime import datetime
import pandas as pd
import numpy as np


def calculate_percent_change(price_old, price_new):
    """
    คำนวณ % การเปลี่ยนแปลงของราคา
    
    Args:
        price_old: ราคาเก่า
        price_new: ราคาใหม่
    
    Returns:
        float: % change
    """
    if price_old == 0:
        return 0.0
    return ((price_new - price_old) / price_old) * 100


def add_percent_change_column(df):
    """
    เพิ่ม column % change ใน DataFrame
    
    Args:
        df: DataFrame with 'close' column
    
    Returns:
        DataFrame: with added 'pct_change' column
    """
    df = df.copy()
    df['pct_change'] = df['close'].pct_change() * 100
    return df


def classify_direction(pct_change, sideways_threshold=0.5):
    """
    จัดประเภททิศทางของการเคลื่อนไหว
    
    Args:
        pct_change: % การเปลี่ยนแปลง
        sideways_threshold: threshold สำหรับการถือว่า sideways
    
    Returns:
        str: 'up', 'down', หรือ 'sideways'
    """
    if pct_change > sideways_threshold:
        return 'up'
    elif pct_change < -sideways_threshold:
        return 'down'
    else:
        return 'sideways'


def save_to_json(data, filepath):
    """
    บันทึกข้อมูลเป็น JSON file
    
    Args:
        data: dict ที่จะบันทึก
        filepath: path ของไฟล์
    """
    # สร้าง directory ถ้ายังไม่มี
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {filepath}")


def load_from_json(filepath):
    """
    โหลดข้อมูลจาก JSON file
    
    Args:
        filepath: path ของไฟล์
    
    Returns:
        dict: ข้อมูลที่โหลดมา
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_stats_report(stats):
    """
    สร้าง text report สวยๆ จาก statistics
    
    Args:
        stats: dict ของ statistics
    
    Returns:
        str: formatted report
    """
    report = []
    report.append("=" * 60)
    report.append("STOCK STATISTICS REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Basic stats
    report.append(f"Total significant days (±{stats.get('threshold', 1)}%): {stats.get('total_significant_days', 0)}")
    report.append(f"  - Positive moves: {stats.get('positive_moves', 0)}")
    report.append(f"  - Negative moves: {stats.get('negative_moves', 0)}")
    report.append("")
    
    # Next day statistics
    if 'next_day_stats' in stats:
        report.append("NEXT DAY BEHAVIOR:")
        report.append("-" * 60)
        
        if 'after_positive' in stats['next_day_stats']:
            ap = stats['next_day_stats']['after_positive']
            report.append(f"After positive days:")
            report.append(f"  Up: {ap.get('up', 0)}, Down: {ap.get('down', 0)}, Sideways: {ap.get('sideways', 0)}")
            report.append(f"  Average change: {ap.get('avg_change', 0):.2f}%")
        
        if 'after_negative' in stats['next_day_stats']:
            an = stats['next_day_stats']['after_negative']
            report.append(f"After negative days:")
            report.append(f"  Up: {an.get('up', 0)}, Down: {an.get('down', 0)}, Sideways: {an.get('sideways', 0)}")
            report.append(f"  Average change: {an.get('avg_change', 0):.2f}%")
        report.append("")
    
    # Probabilities
    if 'probabilities' in stats:
        report.append("PROBABILITIES:")
        report.append("-" * 60)
        probs = stats['probabilities']
        for key, value in probs.items():
            report.append(f"  {key}: {value:.1f}%")
        report.append("")
    
    # Risk metrics
    if 'risk' in stats:
        report.append("RISK METRICS:")
        report.append("-" * 60)
        risk = stats['risk']
        for key, value in risk.items():
            report.append(f"  {key}: {value:.2f}%")
        report.append("")
    
    report.append("=" * 60)
    
    return "\n".join(report)


def ensure_directories():
    """
    สร้าง directories ที่จำเป็นถ้ายังไม่มี
    """
    from config import DATA_DIR, RESULTS_DIR, PLOTS_DIR
    
    for directory in [DATA_DIR, RESULTS_DIR, PLOTS_DIR]:
        os.makedirs(directory, exist_ok=True)
        # สร้าง .gitkeep
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            open(gitkeep_path, 'w').close()
    
    print("✅ Directories created/verified")
