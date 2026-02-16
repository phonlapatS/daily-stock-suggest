# 🎯 China/HK Optimization Plan

**วันที่:** 2026-02-13  
**เป้าหมาย:** 
- ✅ มีหุ้นให้เทรดเยอะขึ้น
- ✅ Prob% สูงขึ้น
- ✅ เสี่ยงน้อยลง
- ✅ RRR คุ้มค่า
- ✅ Count น่าเชื่อถือ

---

## 📊 สถานะปัจจุบัน

### **หุ้นจีน/ฮ่องกงที่ No-Trade:**
| Symbol | Prob% | RRR | Matches | Reason |
|--------|-------|-----|---------|--------|
| **700** | 51.4% | 1.23 | 891 | Prob < 50% threshold |
| **1211** | 49.7% | 0.90 | 2902 | Prob < 50%, RRR ต่ำ |

### **Threshold ปัจจุบัน:**
- **Pattern Matching:** 0.5% floor, 0.9x multiplier
- **Prob Threshold:** 50%
- **Min Stats:** 20

---

## 🔍 วิเคราะห์ปัญหา

### **1. Prob Threshold 50% ยังสูงเกินไป**
- 700: Prob 51.4% → เกือบผ่าน (ขาด 1.4%)
- 1211: Prob 49.7% → เกือบผ่าน (ขาด 0.3%)

### **2. Pattern Matching Threshold อาจต่ำเกินไป**
- Threshold ต่ำ → จับ pattern มาก → Prob ต่ำ
- Threshold สูง → จับ pattern น้อย → Prob สูง (แต่ match_count ลดลง)

### **3. ต้องสมดุลระหว่าง:**
- Prob% สูง (เสี่ยงน้อย)
- RRR คุ้มค่า
- Count น่าเชื่อถือ

---

## 💡 แผนการปรับปรุง

### **Option 1: ลด Prob Threshold (ง่ายที่สุด)**

**การปรับ:**
```python
# China/HK: Prob >= 48% (ลดจาก 50%)
prob_threshold = 48.0
```

**ผลลัพธ์ที่คาดหวัง:**
- 700: Prob 51.4% → ✅ ผ่าน
- 1211: Prob 49.7% → ✅ ผ่าน
- **Total: ~2 หุ้น**

**ข้อดี:**
- ✅ ได้หุ้นมากขึ้น
- ✅ ง่าย

**ข้อเสีย:**
- ⚠️ Prob ต่ำกว่า (48-51%)

---

### **Option 2: ปรับ Pattern Matching Threshold (เพิ่ม Prob%)**

**การปรับ:**
```python
# China/HK: เพิ่ม threshold เพื่อให้ Prob สูงขึ้น
market_floor = 0.6%  # จาก 0.5% → 0.6%
threshold_multiplier = 1.0  # จาก 0.9x → 1.0x
```

**ผลลัพธ์ที่คาดหวัง:**
- Pattern ชัดเจนขึ้น → Prob สูงขึ้น
- Match Count อาจลดลง

**ข้อดี:**
- ✅ Prob สูงขึ้น
- ✅ Pattern ชัดเจนขึ้น

**ข้อเสีย:**
- ⚠️ Match Count อาจลดลง

---

### **Option 3: Prob 48% + Pattern Threshold สูงขึ้น (สมดุล)**

**การปรับ:**
```python
# Pattern Matching
market_floor = 0.6%  # เพิ่มจาก 0.5%
threshold_multiplier = 1.0  # เพิ่มจาก 0.9x

# Gatekeeper
prob_threshold = 48.0  # ลดจาก 50%
min_stats = 25  # เพิ่มจาก 20 (น่าเชื่อถือขึ้น)
```

**ผลลัพธ์ที่คาดหวัง:**
- Prob สูงขึ้น (threshold สูงขึ้น)
- Match Count น่าเชื่อถือขึ้น (min_stats 25)
- ได้หุ้นมากขึ้น (Prob 48%)

**ข้อดี:**
- ✅ Prob สูงขึ้น
- ✅ Count น่าเชื่อถือขึ้น
- ✅ ได้หุ้นมากขึ้น

**ข้อเสีย:**
- ⚠️ ต้องทดสอบ

---

## 🎯 แนะนำ: Option 3 (สมดุล)

### **การปรับ:**
1. **Pattern Matching Threshold:**
   - Floor: 0.5% → 0.6%
   - Multiplier: 0.9x → 1.0x

2. **Gatekeeper:**
   - Prob Threshold: 50% → 48%
   - Min Stats: 20 → 25

### **เหตุผล:**
- ✅ Prob สูงขึ้น (threshold สูงขึ้น → pattern ชัดเจนขึ้น)
- ✅ Count น่าเชื่อถือขึ้น (min_stats 25)
- ✅ ได้หุ้นมากขึ้น (Prob 48%)
- ✅ RRR คุ้มค่า (ยังคงใช้ RRR เป็น metric)

---

## 📊 ผลลัพธ์ที่คาดหวัง

### **หุ้นที่ควรผ่าน:**
- 700: Prob 51.4% → ✅ ผ่าน (Prob > 48%)
- 1211: Prob 49.7% → ✅ ผ่าน (Prob > 48%)

### **คุณภาพ:**
- Prob%: 48-52% (สูงขึ้นจาก threshold สูงขึ้น)
- RRR: 1.0-1.5 (คุ้มค่า)
- Match Count: 25+ (น่าเชื่อถือ)

---

## 🔗 Related Documents

- [CHINA_HK_THRESHOLD_ANALYSIS.md](CHINA_HK_THRESHOLD_ANALYSIS.md) - วิเคราะห์ threshold
- [BASIC_SYSTEM_COMPARISON.md](BASIC_SYSTEM_COMPARISON.md) - เปรียบเทียบผลลัพธ์

