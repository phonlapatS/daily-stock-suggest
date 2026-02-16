# 📊 China/HK Stocks List

**วันที่:** 2026-02-13  
**เป้าหมาย:** รายการหุ้นจีน/ฮ่องกงทั้งหมดในระบบ

---

## 🇨🇳 China/HK Stocks ในระบบ

### **1. HKEX (Hong Kong Exchange) - 10 หุ้น**

**GROUP_C_CHINA_HK:**
| # | Symbol | Name | Exchange |
|---|--------|------|----------|
| 1 | **700** | TENCENT | HKEX |
| 2 | **9988** | ALIBABA | HKEX |
| 3 | **3690** | MEITUAN | HKEX |
| 4 | **1810** | XIAOMI | HKEX |
| 5 | **9888** | BAIDU | HKEX |
| 6 | **9618** | JD-COM | HKEX |
| 7 | **1211** | BYD | HKEX |
| 8 | **2015** | LI-AUTO | HKEX |
| 9 | **9868** | XPENG | HKEX |
| 10 | **9866** | NIO | HKEX |

**รวม:** 10 หุ้น (HKEX)

---

### **2. US Market (ADR) - 13 หุ้น**

**CHINA_ADR_STOCKS:**
| # | Symbol | Name | Exchange |
|---|--------|------|----------|
| 1 | **BABA** | ALIBABA | NYSE |
| 2 | **JD** | JD-COM | NASDAQ |
| 3 | **PDD** | PINDUODUO | NASDAQ |
| 4 | **BIDU** | BAIDU | NASDAQ |
| 5 | **NIO** | NIO | NYSE |
| 6 | **XPEV** | XPENG | NYSE |
| 7 | **LI** | LI-AUTO | NASDAQ |
| 8 | **BILI** | BILIBILI | NASDAQ |
| 9 | **TCOM** | TRIP-COM | NASDAQ |
| 10 | **IQ** | IQIYI | NASDAQ |
| 11 | **ZTO** | ZTO-EXP | NYSE |
| 12 | **BEKE** | KE-HOLDINGS | NYSE |
| 13 | **TCEHY** | TENCENT-ADR | OTC |

**รวม:** 13 หุ้น (US ADR)

---

### **3. US Market (Economy) - 5 หุ้น**

**CHINA_ECONOMY_STOCKS:**
| # | Symbol | Name | Exchange |
|---|--------|------|----------|
| 1 | **YUMC** | Yum China | NYSE |
| 2 | **HTHT** | H World Group | NASDAQ |
| 3 | **EDU** | New Oriental Education | NYSE |
| 4 | **TAL** | TAL Education | NYSE |
| 5 | **ZTO** | ZTO Express | NYSE |

**รวม:** 5 หุ้น (US Economy)

---

## 📊 สรุป

### **หุ้นจีน/ฮ่องกงทั้งหมด:**
- **HKEX:** 10 หุ้น (เทรดในฮ่องกง)
- **US ADR:** 13 หุ้น (เทรดใน US)
- **US Economy:** 5 หุ้น (เทรดใน US)
- **รวม:** 28 หุ้น

### **หุ้นที่ใช้ใน Basic System:**
- **HKEX:** 10 หุ้น (GROUP_C_CHINA_HK)
- **US ADR:** ไม่ได้ใช้ (อยู่ใน US group)
- **US Economy:** ไม่ได้ใช้ (อยู่ใน US group)

---

## 🔍 หมายเหตุ

### **ทำไมมีแค่ 10 หุ้นใน HKEX?**

**เหตุผล:**
1. **Focus ที่หุ้นใหญ่:** เลือกหุ้นใหญ่ที่มี liquidity สูง
2. **Tech-focused:** เน้นหุ้น Tech (TENCENT, ALIBABA, MEITUAN, XIAOMI, etc.)
3. **Data availability:** หุ้นที่ TradingView มีข้อมูลครบ

### **หุ้นจีนที่เทรดใน US:**
- **ADR (American Depositary Receipts):** หุ้นจีนที่เทรดใน US
- **อยู่ใน US group:** ไม่ได้อยู่ใน CHINA group
- **รวม:** 13 + 5 = 18 หุ้น

---

## 💡 คำแนะนำ

### **ถ้าต้องการเพิ่มหุ้นจีน/ฮ่องกง:**

1. **เพิ่มใน HKEX:**
   - เพิ่มใน `GROUP_C_CHINA_HK` ใน `config.py`
   - ตัวอย่าง: `{'symbol': 'XXXX', 'exchange': 'HKEX', 'name': 'COMPANY_NAME'}`

2. **เพิ่มหุ้นใหญ่:**
   - ตรวจสอบว่า TradingView มีข้อมูล
   - ตรวจสอบว่าเป็นหุ้นใหญ่ (liquidity สูง)

---

## 🔗 Related Documents

- [CHINA_HK_OPTIMIZATION_PLAN.md](CHINA_HK_OPTIMIZATION_PLAN.md) - แผนการปรับปรุง
- [CHINA_HK_THRESHOLD_ANALYSIS.md](CHINA_HK_THRESHOLD_ANALYSIS.md) - วิเคราะห์ threshold

