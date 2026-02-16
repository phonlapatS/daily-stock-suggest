# China/HK V13.6: Use Raw Prob% to Avoid Overfitting

## 📋 Summary

ปรับปรุง logic สำหรับ China/HK Market ให้ใช้ **Raw Prob%** แทน **Elite Prob%** เพื่อหลีกเลี่ยงปัญหา overfitting และ selection bias

---

## ⚠️ Problem: Elite Prob% มีปัญหา

จากการวิเคราะห์พบว่า Elite Prob% (91.7%, 82.7%) มีปัญหาหลายประการ:

### 1. **Selection Bias**
- Elite Prob% = Win Rate ของ trades ที่มี Historical Prob >= 60%
- แต่ในการเทรดจริง จะไม่รู้ว่า trade ไหนจะเป็น Elite
- Elite Prob% สูงเพราะเลือกเฉพาะ trades ที่ดีมาแสดง

### 2. **Overfitting**
- XIAOMI: Elite Trades 36/36 (100%) มาจาก pattern เดียวกัน ("+---")
- MEITUAN: Elite Trades 156/156 (100%) มาจาก pattern เดียวกัน ("+--")
- → Pattern เดียวชนะหลายครั้ง = overfitting

### 3. **Lucky Streak**
- XIAOMI: Max Consecutive Wins = 24/36 (66.7%)
- MEITUAN: Max Consecutive Wins = 48/156 (30.8%)
- → อาจเป็น lucky streak ไม่ใช่ skill

### 4. **Historical Prob% ไม่แม่น**
- XIAOMI: Historical Prob% (61.5%) vs Actual Win Rate (91.7%) = 30.1% difference
- MEITUAN: Historical Prob% (68.0%) vs Actual Win Rate (82.7%) = 14.7% difference
- → Pattern matching ไม่แม่นสำหรับ Elite Trades

---

## ✅ Solution: Use Raw Prob%

### การเปลี่ยนแปลง:

1. **ใช้ Raw Prob% แทน Elite Prob% สำหรับ China/HK**
   - Raw Prob% = Win Rate จริงของทุก trades (ไม่มี selection bias)
   - ใช้ Raw Count แทน Elite Count (เพื่อความน่าเชื่อถือทางสถิติ)
   - ใช้ Raw Trades สำหรับ RRR calculation (เพื่อความแม่นยำ)

2. **ปรับ Display Criteria**
   - Prob% >= 50.0% (ลดจาก 53% เพราะ Raw Prob% ต่ำกว่า Elite Prob%)
   - RRR >= 1.0 (คงเดิม - ชนะได้กำไรมากกว่าขาดทุน)
   - Count >= 20 (เพิ่มจาก 15 เพื่อความน่าเชื่อถือทางสถิติ)

---

## 📊 Results Comparison

### Before (V13.4 - Elite Prob%):

| Symbol | Elite Prob% | Raw Prob% | RRR | Count |
|--------|-------------|-----------|-----|-------|
| XIAOMI | 91.7% | 67.2% | 1.28 | 36 |
| MEITUAN | 82.7% | 67.8% | 1.79 | 156 |

**ปัญหา:**
- Elite Prob% สูงเกินจริง (overfitting/selection bias)
- Elite Count น้อย (36, 156) → ไม่น่าเชื่อถือทางสถิติ
- ในการเทรดจริง จะไม่รู้ว่า trade ไหนจะเป็น Elite

### After (V13.6 - Raw Prob%):

| Symbol | Prob% (Raw) | RRR | Count (Raw) |
|--------|-------------|-----|-------------|
| XIAOMI | 67.2% | 1.05 | 668 |
| MEITUAN | 67.8% | 1.32 | 1,564 |
| LI-AUTO | 68.9% | 1.04 | 524 |
| BYD | 68.2% | 1.03 | 2,340 |
| TENCENT | 62.2% | 1.13 | 4,349 |

**ข้อดี:**
- ✅ Raw Prob% = Win Rate จริง (ไม่มี selection bias)
- ✅ หลีกเลี่ยง overfitting (ไม่เลือกเฉพาะ pattern ที่ชนะ)
- ✅ ใช้ได้จริง (ไม่มี Elite Filter ใน real trading)
- ✅ RRR > 1.0 (ชนะได้กำไรมากกว่าขาดทุน)
- ✅ Count สูง (524-4,349) → น่าเชื่อถือทางสถิติ

---

## 🔧 Technical Changes

### `scripts/calculate_metrics.py`:

1. **`calculate_symbol_metrics` function:**
   ```python
   # V13.6: China/HK ใช้ Raw Prob% และ Raw Count เสมอ
   is_china_hk = country in ['CN', 'HK']
   
   if is_china_hk:
       final_prob = raw_prob
       final_count = raw_count
       # ใช้ Raw Trades สำหรับ RRR calculation
       report_group = group.copy()
       # ... calculate RRR from Raw Trades
   else:
       # Other markets: ใช้ Elite Prob% ถ้า Elite Count >= 5
       final_prob = elite_prob if elite_count >= 5 else raw_prob
       final_count = elite_count if elite_count >= 5 else raw_count
   ```

2. **Display Criteria (China/HK):**
   ```python
   china_trend = summary_df[
       ((summary_df['Country'] == 'CN') | (summary_df['Country'] == 'HK')) & 
       (summary_df['Prob%'] >= 50.0) &  # ลดจาก 53% → 50%
       (summary_df['RR_Ratio'] >= 1.0) &  # คงเดิม
       (summary_df['Count'] >= 20)  # เพิ่มจาก 15 → 20
   ]
   ```

---

## 📈 Key Metrics

### China/HK Market (V13.6):

| Symbol | Prob% | RRR | AvgWin% | AvgLoss% | Count |
|--------|-------|-----|---------|----------|-------|
| LI-AUTO | 68.9% | 1.04 | 2.10% | 2.01% | 524 |
| BYD | 68.2% | 1.03 | 1.82% | 1.77% | 2,340 |
| MEITUAN | 67.8% | 1.32 | 2.17% | 1.64% | 1,564 |
| XIAOMI | 67.2% | 1.05 | 1.77% | 1.69% | 668 |
| TENCENT | 62.2% | 1.13 | 1.51% | 1.33% | 4,349 |

**สรุป:**
- ✅ Prob% Realistic (62-69%) → ไม่เวอร์เกินจริง
- ✅ RRR > 1.0 (1.03-1.32) → ชนะได้กำไรมากกว่าขาดทุน
- ✅ Count สูง (524-4,349) → น่าเชื่อถือทางสถิติ
- ✅ หลีกเลี่ยง overfitting (ใช้ Raw Prob% ไม่ใช่ Elite Prob%)

---

## 🎯 Target Achieved

1. ✅ **Realistic Win Rate**: Raw Prob% (62-69%) แทน Elite Prob% (91.7%, 82.7%)
2. ✅ **No Selection Bias**: ใช้ทุก trades ไม่ใช่เฉพาะ Elite Trades
3. ✅ **No Overfitting**: ไม่เลือกเฉพาะ pattern ที่ชนะ
4. ✅ **Statistical Reliability**: Count สูง (524-4,349)
5. ✅ **Real-World Usable**: ใช้ได้จริง (ไม่มี Elite Filter ใน real trading)
6. ✅ **RRR > 1.0**: ชนะได้กำไรมากกว่าขาดทุน

---

## 📝 Notes

- **Other Markets (Thai, US, Taiwan)**: ยังใช้ Elite Prob% ตามปกติ (ไม่มีปัญหา)
- **China/HK Only**: ใช้ Raw Prob% เพื่อหลีกเลี่ยง overfitting
- **Display Criteria**: ปรับให้เหมาะสมกับ Raw Prob% (Prob% >= 50%, Count >= 20)

---

## 🔄 Version History

- **V13.4**: ใช้ Elite Prob% (มีปัญหา overfitting)
- **V13.6**: ใช้ Raw Prob% (แก้ปัญหา overfitting) ← **Current**

---

**Date:** 2025-01-XX  
**Status:** ✅ Implemented & Tested

