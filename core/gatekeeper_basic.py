"""
Basic Gatekeeper - เกณฑ์การตัดสินใจแบบเรียบง่าย
==============================================
ใช้เกณฑ์: Prob > 60%, match_count >= Nmin
"""


class BasicGatekeeper:
    """
    Gatekeeper แบบเรียบง่าย
    - Prob > threshold (เกณฑ์หลัก)
    - match_count >= min_stats (เกณฑ์รอง)
    - RRR เป็น metric เท่านั้น (ไม่ใช่ filter)
    """
    
    def __init__(self, prob_threshold=55.0, min_stats=25):
        """
        Args:
            prob_threshold: Prob% ขั้นต่ำ (default: 55.0)
            min_stats: จำนวน match ขั้นต่ำ (default: 25)
        """
        self.prob_threshold = prob_threshold
        self.min_stats = min_stats
    
    def check_prob(self, prob):
        """
        ตรวจสอบว่า Prob >= threshold หรือไม่
        
        Args:
            prob: Prob% (float) - Win Rate จาก historical matches
        
        Returns:
            bool: True ถ้า Prob >= threshold
        """
        return prob >= self.prob_threshold
    
    def check_match_count(self, match_count):
        """
        ตรวจสอบว่า match_count >= min_stats หรือไม่
        
        Args:
            match_count: จำนวน match (int)
        
        Returns:
            bool: True ถ้า match_count >= min_stats
        """
        return match_count >= self.min_stats
    
    def decide_signal(self, prob, match_count, direction, rrr=None):
        """
        ตัดสินใจสัญญาณ: BUY/SELL/NO-TRADE
        
        Args:
            prob: Prob% (float)
            match_count: จำนวน match (int)
            direction: "LONG" หรือ "SHORT"
            rrr: Risk-Reward Ratio (optional)
        
        Returns:
            dict: {
                'signal': str,      # "BUY", "SELL", "NO-TRADE"
                'reason': str,       # เหตุผล
                'passed': bool       # ผ่านเกณฑ์หรือไม่
            }
        """
        # Check criteria (Prob และ Match Count เท่านั้น)
        prob_ok = self.check_prob(prob)
        count_ok = self.check_match_count(match_count)
        
        # All criteria must pass
        if prob_ok and count_ok:
            signal = "BUY" if direction == "LONG" else "SELL"
            reason = f"Prob {prob:.1f}% >= {self.prob_threshold}%, match_count {match_count} >= {self.min_stats}"
            return {
                'signal': signal,
                'reason': reason,
                'passed': True
            }
        else:
            # Find which criteria failed
            reasons = []
            if not prob_ok:
                reasons.append(f"Prob {prob:.1f}% <= {self.prob_threshold}%")
            if not count_ok:
                reasons.append(f"match_count {match_count} < {self.min_stats}")
            
            return {
                'signal': "NO-TRADE",
                'reason': " | ".join(reasons),
                'passed': False
            }
    
    def get_tag(self, prob, match_count, rrr=None):
        """
        กำหนด tag: STRONG / WEAK / NO-TRADE
        
        Args:
            prob: Prob% (float)
            match_count: จำนวน match (int)
            rrr: Risk-Reward Ratio (optional, สำหรับแสดงผลเท่านั้น)
        
        Returns:
            str: "STRONG", "WEAK", หรือ "NO-TRADE"
        """
        if self.decide_signal(prob, match_count, "LONG", rrr)['passed']:
            if prob >= 65.0:
                return "STRONG"
            else:
                return "WEAK"
        else:
            return "NO-TRADE"

