"""
core/scoring.py - Confidence & Risk Scoring Module
====================================================
Calculates combined Confidence and Risk scores based on:
1. Pattern Statistics (Prob, Sample Size)
2. Historical Loss Data (Avg Loss %)
"""

import numpy as np
from typing import Dict, List, Optional


def calculate_confidence(prob: float, 
                         sample_size: int,
                         max_sample: int = 100) -> float:
    """
    Calculate Confidence Score (0-100%).
    
    Formula:
    - Confidence = (Prob × 0.5) + (Sample_Quality × 0.5)
    - Sample_Quality = min(sample_size / max_sample, 1.0) × 100
    
    Args:
        prob: Win probability (0-100)
        sample_size: Number of historical occurrences
        max_sample: Sample size that gives 100% quality (default 100)
    
    Returns:
        Confidence score (0-100)
    """
    # Normalize probability to 0-100 range
    prob_normalized = min(max(prob, 0), 100)
    
    # Sample quality: more samples = higher quality (cap at max_sample)
    sample_quality = min(sample_size / max_sample, 1.0) * 100
    
    # Weighted average: 50% Prob + 50% Sample Quality
    confidence = (prob_normalized * 0.5) + (sample_quality * 0.5)
    
    return round(confidence, 1)


def calculate_risk(historical_returns: List[float]) -> float:
    """
    Calculate Risk Score based on historical loss data.
    
    Formula:
    - Risk = Average of negative returns (absolute value)
    - If no negative returns, Risk = 0
    
    Args:
        historical_returns: List of returns (decimal form, e.g., -0.02 = -2%)
    
    Returns:
        Risk score (0-100, representing %)
    """
    if not historical_returns:
        return 0.0
    
    # Get only negative returns
    losses = [abs(r) for r in historical_returns if r < 0]
    
    if not losses:
        return 0.0
    
    # Average loss (convert to percentage)
    avg_loss = np.mean(losses) * 100
    
    return round(avg_loss, 2)


def calculate_risk_from_stats(bear_prob: float, avg_return: float) -> float:
    """
    Calculate Risk Score from existing stats (simpler method).
    
    Formula:
    - Risk = (100 - Dominant Prob) = Chance of being wrong
    - Adjusted by expected loss magnitude
    
    Args:
        bear_prob: Bear probability (0-100)
        avg_return: Average return (%, can be negative)
    
    Returns:
        Risk score (0-100)
    """
    # If avg_return is positive, risk = bear_prob (chance of down)
    # If avg_return is negative, risk = bull_prob (chance of up)
    if avg_return >= 0:
        risk = bear_prob
    else:
        risk = 100 - bear_prob  # bull_prob
    
    return round(risk, 1)


def get_confidence_level(confidence: float) -> str:
    """
    Convert confidence score to human-readable level.
    
    Returns emoji + level string.
    """
    if confidence >= 75:
        return "🔥 HIGH"
    elif confidence >= 60:
        return "⚡ MED"
    elif confidence >= 45:
        return "💧 LOW"
    else:
        return "❄️ VERY LOW"


def get_risk_level(risk: float) -> str:
    """
    Convert risk score to human-readable level.
    """
    if risk >= 45:
        return "🔴 HIGH"
    elif risk >= 35:
        return "🟡 MED"
    else:
        return "🟢 LOW"
