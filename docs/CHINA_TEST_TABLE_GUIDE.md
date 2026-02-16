# China Market - Test Table Guide

## 📋 Overview

สร้างตารางเปรียบเทียบผลลัพธ์จากการทดสอบหลายค่า

---

## 🚀 Quick Test (แนะนำ - ใช้เวลาน้อย)

```bash
python scripts/quick_china_test_table.py
```

**ทดสอบ:**
- Max Hold: 6, 7, 8, 9
- Threshold: 0.85, 0.9, 0.95
- Total: 12 tests

**ผลลัพธ์:**
- ตารางเปรียบเทียบ
- Best combination
- Saved to: `data/china_quick_test_table.csv`

---

## 🔬 Full Test (ใช้เวลานาน)

```bash
python scripts/create_china_comparison_table.py
```

**ทดสอบ:**
- Max Hold: 5, 6, 7, 8, 9, 10
- Threshold: 0.85, 0.9, 0.95
- Total: 18 tests

**ผลลัพธ์:**
- ตารางเปรียบเทียบแบบละเอียด
- Best combination
- Saved to: `data/china_comparison_table.csv`

---

## 📊 ตารางที่ได้

### Main Metrics:
- Max Hold, Threshold
- Stocks Passing, Total Trades
- Win Rate, RRR, Expectancy
- SL Rate, Max Drawdown
- Risk Score, Profit Score, Total Score

### Sorted by:
- Total Score (Best First)
- Risk Score (Low = Good)
- Profit Score (High = Good)

---

## 🎯 การอ่านตาราง

### Risk Score (ต่ำ = ดี):
- 0-1: ✅ LOW RISK
- 2: ⚠️ MODERATE RISK
- 3-4: ❌ HIGH RISK

### Profit Score (สูง = ดี):
- 3-4: ✅ ✅ ✅ EXCELLENT
- 2-2.5: ✅ ✅ GOOD
- 1-1.5: ⚠️ MODERATE
- 0-0.5: ❌ POOR

### Total Score:
- สูง = ดี (Risk ต่ำ + Profit สูง)

---

## 💡 Recommendations

เลือกค่าที่มี:
- Risk Score <= 1
- Profit Score >= 2
- Total Score สูงสุด

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR USE**

