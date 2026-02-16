# China Market - Optimization Guide

## 📋 เป้าหมาย

**"เอาให้เสี่ยงน้อยและได้กำไรจริง"**

---

## 🎯 Success Criteria

### Risk Score <= 1 (เสี่ยงน้อย):
- SL Hit Rate <= 20%
- Max Drawdown >= -5%

### Profit Score >= 2 (ได้กำไรจริง):
- Expectancy > 0.5%
- Win Rate > 55% หรือ RRR > 1.5

---

## 🔬 การทดสอบ

### Step 1: รัน Backtest และวิเคราะห์ผลลัพธ์ปัจจุบัน

```bash
python scripts/run_china_analysis.py
```

**สิ่งที่ได้:**
- Overall Performance (Win Rate, RRR, Expectancy)
- Exit Reasons Analysis
- Risk Metrics (SL Rate, Max Drawdown)
- By Symbol Performance
- Assessment & Recommendations

---

### Step 2: ทดสอบหลายค่า (ถ้าจำเป็น)

```bash
python scripts/optimize_china_risk_profit.py
```

**ทดสอบ:**
- Max Hold: 5, 6, 7, 8, 9, 10
- Threshold: 0.8, 0.85, 0.9, 0.95, 1.0

**เป้าหมาย:**
- หาค่าที่ Risk Score <= 1 และ Profit Score >= 2

---

## 📊 การประเมินผลลัพธ์

### Risk Score (ต่ำ = ดี):
- 0-1: ✅ LOW RISK
- 2: ⚠️ MODERATE RISK
- 3-4: ❌ HIGH RISK

### Profit Score (สูง = ดี):
- 3-4: ✅ ✅ ✅ EXCELLENT
- 2-2.5: ✅ ✅ GOOD
- 1-1.5: ⚠️ MODERATE
- 0-0.5: ❌ POOR

### Overall Assessment:
- **Risk Score <= 1 + Profit Score >= 2** = ✅ ✅ ✅ EXCELLENT
- **Risk Score <= 2 + Profit Score >= 1.5** = ✅ ✅ GOOD
- **Risk Score <= 2 + Profit Score >= 1** = ✅ ACCEPTABLE
- **อื่นๆ** = ⚠️ NEEDS IMPROVEMENT

---

## 💡 Recommendations

### ถ้า SL Rate > 30%:
- ลด SL (1.2% → 1.0%)
- หรือเพิ่ม Max Hold (8 → 10 days)

### ถ้า Max Drawdown < -10%:
- ปรับ Risk Management
- ลด Position Size

### ถ้า Expectancy <= 0%:
- ปรับ Strategy
- หรือปรับ RM parameters

### ถ้า Win Rate < 50%:
- เพิ่ม min_prob (51% → 53%)
- หรือปรับ threshold

### ถ้า RRR < 1.2:
- ปรับ TP/SL ratio
- หรือปรับ Trailing Stop

---

## 🚀 Quick Start

1. **รัน Analysis:**
   ```bash
   python scripts/run_china_analysis.py
   ```

2. **ตรวจสอบผลลัพธ์:**
   - ดู Risk Score และ Profit Score
   - ดู Recommendations

3. **ถ้าจำเป็น ใช้ Optimization:**
   ```bash
   python scripts/optimize_china_risk_profit.py
   ```

4. **ปรับ Parameters:**
   - ใช้ค่าที่ดีที่สุดจาก optimization
   - หรือปรับตาม recommendations

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR USE**

