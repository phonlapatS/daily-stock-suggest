# China Market - Max Hold Test Guide

## 📋 Overview

ทดสอบและเปรียบเทียบ Max Hold หลายค่าเพื่อตอบคำถาม:
1. **ถ้าหุ้นผันผวนนิดเดียวไปเรื่อยๆหลายรอบ มันก็ไม่ได้กำไรเหมือนกันรึเปล่า?**
2. **กว่ากำไรจะคุ้มค่ามันก็ต้องถือเกือบ 8 วัน แล้วในระหว่างนั้นจะไม่ชน stop loss ก่อนหรอ?**

---

## 🔬 Step 1: วิเคราะห์ผลลัพธ์ปัจจุบัน (Max Hold = 8)

### Run Analysis Script:

```bash
python scripts/analyze_china_exit_reasons.py
```

**สิ่งที่ได้:**
- Exit reasons distribution
- Hold days distribution
- Win/Loss by exit reason
- หุ้นที่ผันผวนนิดๆไปเรื่อยๆ (MAX_HOLD exits)
- SL hit rate
- TP hit rate

---

## 🔬 Step 2: ทดสอบ Max Hold หลายค่า

### Option A: Manual Testing (แนะนำ)

ทดสอบทีละค่า:

```bash
# Test Max Hold = 5
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 5
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py

# Test Max Hold = 6
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 6
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py

# Test Max Hold = 7
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 7
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py

# Test Max Hold = 8 (current)
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 8
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py

# Test Max Hold = 9
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 9
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py

# Test Max Hold = 10
python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 10
python scripts/calculate_metrics.py
python scripts/analyze_china_exit_reasons.py
```

### Option B: Automated Testing (ใช้เวลานาน)

```bash
python scripts/compare_china_max_hold.py
```

**หมายเหตุ:** Script นี้จะรัน backtest ทีละค่า ซึ่งใช้เวลานานมาก (อาจใช้เวลา 1-2 ชั่วโมง)

---

## 📊 Step 3: เปรียบเทียบผลลัพธ์

### สิ่งที่ต้องดู:

1. **MAX_HOLD Exit Rate:**
   - ถ้า Max Hold = 5: MAX_HOLD rate ควรต่ำ (ถึง TP หรือชน SL ก่อน)
   - ถ้า Max Hold = 8: MAX_HOLD rate อาจสูง (ถือนานแล้วออก)

2. **MAX_HOLD Avg Return:**
   - ถ้า return ติดลบ → Max Hold ยาวเกินไป
   - ถ้า return บวกเล็กน้อย → ได้กำไรแต่ไม่คุ้ม
   - ถ้า return บวกดี → Max Hold นี้เหมาะสม

3. **SL Hit Rate:**
   - ถ้า SL rate สูง → ถือนานแล้วชน SL ก่อนถึง TP
   - ถ้า SL rate ต่ำ → ไม่ค่อยชน SL

4. **TP Hit Rate:**
   - ถ้า TP rate ต่ำ → ไม่ค่อยถึง TP (อาจต้องลด TP หรือเพิ่ม Max Hold)
   - ถ้า TP rate สูง → ถึง TP บ่อย

5. **Win Rate:**
   - ควรสูงกว่า 50%
   - ถ้าต่ำ → อาจมีปัญหา

6. **RRR:**
   - ควรสูงกว่า 1.3
   - ถ้าต่ำ → อาจมีปัญหา

---

## 🎯 Decision Criteria

### ถ้า Max Hold = 8 วันยาวเกินไป:

**Signs:**
- MAX_HOLD exits มี return ติดลบ
- MAX_HOLD win rate < 50%
- SL hit rate > 30%
- TP hit rate < 20%

**Action:**
- ลด Max Hold (5-7 days)
- หรือปรับ SL/TP

### ถ้า Max Hold = 8 วันเหมาะสม:

**Signs:**
- MAX_HOLD exits มี return บวก
- MAX_HOLD win rate > 50%
- SL hit rate < 30%
- TP hit rate > 20%

**Action:**
- ใช้ Max Hold = 8 days

### ถ้า Max Hold = 8 วันสั้นเกินไป:

**Signs:**
- TP hit rate ต่ำมาก (< 10%)
- MAX_HOLD rate สูงมาก (> 50%)
- MAX_HOLD exits มี return บวกดี

**Action:**
- เพิ่ม Max Hold (9-10 days)
- หรือลด TP

---

## 📝 Recording Results

บันทึกผลลัพธ์ในตาราง:

| Max Hold | Total Trades | Win Rate | Avg Return | RRR | SL Rate | TP Rate | MAX_HOLD Rate | MAX_HOLD Avg Return | MAX_HOLD Win Rate |
|----------|--------------|----------|------------|-----|---------|---------|---------------|---------------------|-------------------|
| 5 | | | | | | | | | |
| 6 | | | | | | | | | |
| 7 | | | | | | | | |
| 8 | | | | | | | | |
| 9 | | | | | | | | |
| 10 | | | | | | | | |

---

## 🚀 Quick Start

1. **วิเคราะห์ผลลัพธ์ปัจจุบัน:**
   ```bash
   python scripts/analyze_china_exit_reasons.py
   ```

2. **ทดสอบ Max Hold = 6 (ถ้าต้องการทดสอบ):**
   ```bash
   python scripts/backtest.py --full --bars 2000 --group CHINA --fast --max_hold 6
   python scripts/calculate_metrics.py
   python scripts/analyze_china_exit_reasons.py
   ```

3. **เปรียบเทียบและสรุป**

---

**Last Updated:** 2026-02-13  
**Status:** 📋 **READY FOR TESTING**

