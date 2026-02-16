# 🎯 Version 4 - Stable Settings (สำหรับ GitHub)

**วันที่:** 2026-02-13  
**Version:** V4.1 (Production-Ready)  
**Status:** ✅ **STABLE** - Ready for GitHub

---

## 📊 สรุป Settings ที่เสถียรที่สุด

### **Core Settings (ทุกประเทศ):**
- ✅ **Max Hold:** 5 วัน (ค่าที่เสถียร - revert จาก 7-10 วัน)
- ✅ **ATR SL:** 1.0x (ยืดหยุ่นตาม volatility)
- ✅ **ATR TP:** 3.5x (ให้ถึง TP ได้มากขึ้น)
- ✅ **ATR Cap:** SL ≤ 7%, TP ≤ 15% (ป้องกัน wild swings)

---

## 🌍 Market-Specific Settings

### **1. THAI MARKET**
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Strategy** | Mean Reversion | Fade the move |
| **Threshold** | 1.0x SD, Floor 0.7% | Dynamic threshold |
| **Min Stats** | 25 | Pattern occurrences |
| **Gatekeeper** | Prob >= 53% | Quality filter |
| **Max Hold** | **5 วัน** ✅ | Stable value |
| **ATR SL** | 1.0x | Flexible |
| **ATR TP** | 3.5x | RRR 3.5 |
| **Trailing** | Activate 1.5%, Distance 50% | Lock profits |

---

### **2. US MARKET**
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Strategy** | Trend Following | Follow momentum |
| **Threshold** | 0.9x SD, Floor 0.6% | Dynamic threshold |
| **Min Stats** | 20 | Pattern occurrences |
| **Gatekeeper** | Prob >= 52% + Quality Filter | AvgWin > AvgLoss |
| **Max Hold** | **5 วัน** ✅ | Stable value (revert from 7) |
| **ATR SL** | 1.0x | Flexible |
| **ATR TP** | 3.5x | RRR 3.5 |
| **Trailing** | Activate 2.0%, Distance 40% | Lock profits |

---

### **3. CHINA/HK MARKET**
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Strategy** | Mean Reversion | Fade the move |
| **Threshold** | 0.9x SD, Floor 0.5% | Dynamic threshold |
| **Min Stats** | 30 | Pattern occurrences |
| **Gatekeeper** | Prob >= 54% | Quality filter |
| **Max Hold** | **5 วัน** ✅ | Stable value (revert from 8) |
| **ATR SL** | 1.0x | Flexible |
| **ATR TP** | 3.5x | RRR 3.5 |
| **Trailing** | Activate 2.0%, Distance 40% | Lock profits |

---

### **4. TAIWAN MARKET**
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Strategy** | Trend Following | Follow momentum |
| **Threshold** | 0.9x SD, Floor 0.5% | Dynamic threshold |
| **Min Stats** | 25 | Pattern occurrences |
| **Gatekeeper** | Prob >= 51% | Quality filter |
| **Max Hold** | **5 วัน** ✅ | Stable value (revert from 10) |
| **ATR SL** | 1.0x | Flexible |
| **ATR TP** | 3.5x | RRR 3.5 |
| **Trailing** | Activate 2.0%, Distance 40% | Lock profits |

---

## 🔄 การเปลี่ยนแปลงสำคัญ

### **Max Hold Days:**
- ✅ **ทุกประเทศ:** Revert กลับมาเป็น **5 วัน** (ค่าที่เสถียร)
- **เดิม:** US 7 วัน, CHINA/HK 8 วัน, TAIWAN 10 วัน
- **ใหม่:** ทุกประเทศ 5 วัน (ลดความเสี่ยง, ใช้ค่าที่เสถียร)

### **ATR TP Multiplier:**
- ✅ **ทุกประเทศ:** **3.5x** (ให้ถึง TP ได้มากขึ้น)
- **เดิม:** US/CHINA 5.0x, TAIWAN 6.5x
- **ใหม่:** ทุกประเทศ 3.5x (based on actual data: TP exits 0.0-0.5%)

### **Trailing Stop:**
- ✅ **US/CHINA/TAIWAN:** Activate 2.0%, Distance 40%
- **เดิม:** Activate 1.0-1.5%, Distance 30-50%
- **ใหม่:** Activate 2.0% (activate ช้าลง - ให้มีเวลาไปถึง TP), Distance 40% (trail แน่นขึ้น)

---

## 📈 Production Mode Settings

### **Slippage:**
- THAI: 0.1%
- US: 0.05%
- TAIWAN: 0.08%
- CHINA/HK: 0.1%
- DEFAULT: 0.05%

### **Commission:**
- THAI: 0.32% (round-trip)
- US: 0.02% (SEC fee only)
- TAIWAN: 0.44% (tax + commission)
- CHINA/HK: 0.30% (stamp duty + commission)
- DEFAULT: 0.10%

### **Gap Risk:**
- THAI: 1.20x
- US: 1.30x
- TAIWAN: 1.25x
- CHINA/HK: 1.35x
- DEFAULT: 1.25x

### **Min Volume:**
- THAI: 500,000 shares/day
- US: 100,000 shares/day
- TAIWAN: 200,000 shares/day
- CHINA/HK: 200,000 shares/day
- DEFAULT: 100,000 shares/day

---

## ✅ ข้อดีของ Settings นี้

### **1. เสถียร (Stable):**
- ✅ Max Hold 5 วันทุกประเทศ → ใช้ค่าที่เสถียร
- ✅ ATR-based SL/TP → ยืดหยุ่นตาม volatility
- ✅ Trailing Stop → Lock กำไร

### **2. Production-Ready:**
- ✅ Production Mode → Slippage, Commission, Gap Risk
- ✅ Entry at Next Bar Open → Realistic
- ✅ Liquidity Filter → Skip low-volume days

### **3. Balance:**
- ✅ มีสัญญาณเพียงพอ (ไม่เข้มงวดเกินไป)
- ✅ คุณภาพดี (Prob >= 51-54%)
- ✅ RRR คุ้มค่า (RRR >= 1.2)

### **4. ตรงกับแนวคิดระบบ:**
- ✅ Pure Statistics (Pattern Matching + History Statistics)
- ✅ ไม่ใช้ Indicator (ไม่ซับซ้อน)
- ✅ Risk Management ครบถ้วน

---

## 📋 Display Criteria (สำหรับ calculate_metrics.py)

### **THAI:**
- Prob >= 60%, RRR >= 1.2, Count >= 30

### **US:**
- Prob >= 55%, RRR >= 1.2, Count >= 15

### **CHINA/HK:**
- Prob >= 55%, RRR >= 1.2, Count >= 15

### **TAIWAN:**
- Prob >= 51%, RRR >= 1.2, Count >= 15

---

## 🔗 Related Documents

- [REVERT_TO_STABLE_SETTINGS.md](REVERT_TO_STABLE_SETTINGS.md) - รายละเอียดการ revert
- [STRATEGY_TABLE_BY_COUNTRY.md](STRATEGY_TABLE_BY_COUNTRY.md) - ตารางกลยุทธ์
- [VERSION_HISTORY.md](VERSION_HISTORY.md) - ประวัติ version
- [MAX_HOLD_EXIT_LOGIC.md](MAX_HOLD_EXIT_LOGIC.md) - Logic การ exit

---

## 🎯 สรุป

**Version 4 ที่เสถียรที่สุด:**
- ✅ **Max Hold:** 5 วันทุกประเทศ (ค่าที่เสถียร)
- ✅ **ATR SL:** 1.0x (ยืดหยุ่น)
- ✅ **ATR TP:** 3.5x (ให้ถึง TP ได้มากขึ้น)
- ✅ **Trailing Stop:** ตามประเทศ (lock กำไร)
- ✅ **Production Mode:** พร้อมใช้งานจริง

**พร้อมสำหรับ GitHub Version 4!** 🚀

