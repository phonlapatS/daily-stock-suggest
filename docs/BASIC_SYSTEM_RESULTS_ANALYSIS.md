# 📊 Basic System Results Analysis

**วันที่:** 2026-02-13  
**Test:** `python scripts/backtest_basic.py --full --bars 2500`

---

## 📈 สรุปผลลัพธ์

### **Overall Results:**
- ✅ **Passed:** 2 หุ้น (0.9%)
- ❌ **No-Trade:** 145 หุ้น (63.3%)
- ⏭️ **No Pattern Found:** 82 หุ้น (35.8%)
- **Total:** 229 หุ้น

### **Passed Stats:**
- **Avg Prob%:** 67.0%
- **Avg RRR:** 3.71
- **Avg Match Count:** 32

---

## 🎯 หุ้นที่ผ่านเกณฑ์ (2 หุ้น)

| Symbol | Country | Signal | Prob% | RRR | Matches |
|--------|---------|--------|-------|-----|---------|
| **CBG** | TH | BUY | 60.6% | 6.24 | 33 |
| **NFLX** | US | SELL | 73.3% | 1.18 | 30 |

**ข้อสังเกต:**
- ✅ Prob% สูง (60.6%, 73.3%)
- ✅ RRR ดี (6.24, 1.18)
- ✅ Match Count เพียงพอ (33, 30)

---

## ❌ หุ้นที่ No-Trade (145 หุ้น)

### **สาเหตุหลัก:**
1. **Prob < 60%** → ส่วนใหญ่ Prob อยู่ที่ 40-58%
2. **Match Count >= 30** → มี match_count เพียงพอ แต่ Prob ต่ำ

### **ตัวอย่าง:**
- ADVANC: Prob 49.5%, RRR 1.24, Matches 2168
- AOT: Prob 43.4%, RRR 1.49, Matches 2832
- BBL: Prob 55.5%, RRR 1.30, Matches 146
- META: Prob 58.3%, RRR 1.12, Matches 834

**ข้อสังเกต:**
- มี match_count สูงมาก (100-3000) แต่ Prob ต่ำ
- RRR ส่วนใหญ่ 0.8-2.0 (ไม่สูงมาก)
- Prob ส่วนใหญ่ 40-58% (ต่ำกว่า 60%)

---

## ⏭️ หุ้นที่ No Pattern Found (82 หุ้น)

### **สาเหตุ:**
- Last pattern (วันนี้) ไม่มีใน `pattern_stats` (training data)
- หรือ pattern ที่ match มี match_count < 30

**ตัวอย่าง:**
- AWC, BEM, BGRIM, BH, BTS, CENTEL, COM7, CPALL, CRC, GPSC, GULF, KTC, MTC, OR, OSP, TRUE, AP, BAM, BCH, BCPG, BPP, BYD, DOHOME, HANA, JMT, KCE, NEX, ONEE, ORI, PR9, PSL, SABUY, SINGER, SISB, SJWD, SNNP, SPALI, SPRC, SSP, STA, SUPER, THANI, THG, TIPH, TKN, TKS, TLI, TOA, TPIPP, TQM, WHAUP

**ข้อสังเกต:**
- ส่วนใหญ่เป็นหุ้นเล็ก/ไม่ค่อยมี pattern
- หรือ threshold สูงเกินไป → ไม่มี pattern match

---

## 🔍 วิเคราะห์ปัญหา

### **1. Prob Threshold 60% สูงเกินไป?**

**ผลลัพธ์:**
- มีหุ้นจำนวนมากที่ Prob 50-58% แต่ไม่ผ่าน
- ได้สัญญาณแค่ 2 หุ้น (0.9%)

**คำถาม:**
- Prob 60% สูงเกินไปหรือไม่?
- ควรลดเป็น 55% หรือ 58% หรือไม่?

### **2. Match Count >= 30 เพียงพอหรือไม่?**

**ผลลัพธ์:**
- หุ้นที่ No-Trade มี match_count สูงมาก (100-3000)
- แต่ Prob ต่ำ (40-58%)

**ข้อสังเกต:**
- Match count สูง ≠ Prob สูง
- อาจต้องปรับ min_stats ตามประเทศ

### **3. "No Pattern Found" มากเกินไป?**

**ผลลัพธ์:**
- 82 หุ้น (35.8%) ไม่มี pattern
- อาจเป็นเพราะ:
  - Last pattern ไม่มีใน training data
  - Threshold สูงเกินไป → ไม่มี pattern match

---

## 💡 คำแนะนำ

### **Option 1: ลด Prob Threshold**
```python
# จาก 60% → 55% หรือ 58%
prob_threshold = 55.0  # หรือ 58.0
```

**ผลลัพธ์ที่คาดหวัง:**
- ได้สัญญาณมากขึ้น
- แต่ Prob ต่ำกว่า (55-58%)

### **Option 2: ปรับ min_stats ตามประเทศ**
```python
# THAI: 30 → 25
# US: 30 → 20
# CHINA/TAIWAN: 30 → 25
```

**ผลลัพธ์ที่คาดหวัง:**
- ได้ pattern มากขึ้น
- แต่ match_count ต่ำกว่า

### **Option 3: ใช้ Prob 55% + RRR > 1.5**
```python
# Prob >= 55% และ RRR >= 1.5
```

**ผลลัพธ์ที่คาดหวัง:**
- ได้สัญญาณมากขึ้น
- แต่คุณภาพดี (RRR > 1.5)

---

## 📊 เปรียบเทียบ: Current vs Basic

| Aspect | Current System | Basic System |
|--------|----------------|--------------|
| **Prob Threshold** | 50-60% (ตามประเทศ) | 60% (ทุกประเทศ) |
| **Min Stats** | 15-30 (ตามประเทศ) | 30 (ทุกประเทศ) |
| **RRR Filter** | 1.2-1.5 (gatekeeper) | ไม่มี (secondary) |
| **Passed Rate** | ~5-10% | 0.9% (2/229) |

**ข้อสังเกต:**
- Basic System เข้มงวดกว่า (Prob 60%, min_stats 30)
- ได้สัญญาณน้อยมาก (0.9%)
- แต่คุณภาพสูง (Prob 67%, RRR 3.71)

---

## 🎯 สรุป

### **✅ ข้อดี:**
1. **คุณภาพสูง:** Prob 67%, RRR 3.71
2. **เข้มงวด:** กรองหุ้นที่ไม่ดีออก
3. **เรียบง่าย:** Logic แยกชัดเจน

### **⚠️ ข้อควรระวัง:**
1. **สัญญาณน้อย:** แค่ 2 หุ้น (0.9%)
2. **Prob 60% สูง:** อาจได้สัญญาณน้อยเกินไป
3. **No Pattern Found มาก:** 82 หุ้น (35.8%)

### **💡 คำแนะนำ:**
- **ถ้าต้องการ Quality:** เก็บ Prob 60% ไว้ (ได้สัญญาณน้อยแต่คุณภาพสูง)
- **ถ้าต้องการ Quantity:** ลด Prob เป็น 55-58% (ได้สัญญาณมากขึ้น)
- **ถ้าต้องการ Balance:** Prob 55% + RRR > 1.5 (สมดุลระหว่างคุณภาพและจำนวน)

---

## 🔗 Related Documents

- [BACK_TO_BASIC_ANALYSIS.md](BACK_TO_BASIC_ANALYSIS.md) - แนวทาง Back to Basic
- [BASIC_SYSTEM_ARCHITECTURE.md](BASIC_SYSTEM_ARCHITECTURE.md) - Architecture

