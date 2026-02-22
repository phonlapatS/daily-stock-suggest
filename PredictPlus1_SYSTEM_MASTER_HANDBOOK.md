# PredictPlus1 V4.4.7 — SYSTEM MASTER HANDBOOK 📘
**A Technical Reference for the Fractal Pattern Detection & Risk Management System**

---

## 📑 สารบัญ (Table of Contents)
1.  [ภาพรวมและปรัชญาระบบ (Executive Summary)](#1-ภาพรวมและปรัชญาระบบ)
2.  [เทคโนโลยีหลัก: Aggregate Voting V4.4 (Core Technology)](#2-เทคโนโลยีหลัก-aggregate-voting-v44)
3.  [ตรรกะการวิเคราะห์รายตลาด (Market Strategy Matrix)](#3-ตรรกะการวิเคราะห์รายตลาด)
4.  [ระบบบริหารความเสี่ยง (Risk Management Framework)](#4-ระบบบริหารความเสี่ยง)
5.  [คู่มือปฏิบัติการและการรันระบบ (Operational Guide)](#5-คู่มือปฏิบัติการและการรันระบบ)
    *   [Operational Commands Manual (Detailed)](file:///e:/PredictPlus1/PredictPlus1_OPERATIONAL_MANUAL.md)
6.  [ประวัติการพัฒนาและวิวัฒนาการ (System Evolution History)](#6-ประวัติการพัฒนาและวิวัฒนาการ)
    *   [Phase 1: Foundation (V1.0 - V2.0)](#phase-1-foundation)
    *   [Phase 2: Statistical Rigor (V3.0 - V3.4)](#phase-2-statistical-rigor)
    *   [Phase 3: Market Tailoring (V10 - V13)](#phase-3-market-tailoring)
    *   [Phase 4: Synthesis & Consensus (V4.4.7)](#phase-4-synthesis--consensus)
7.  [โครงสร้างข้อมูลและระบบหน่วยความจำ (Data & Cache System)](#7-โครงสร้างข้อมูลและระบบหน่วยความจำ)
8.  [การแก้ไขปัญหาพื้นฐาน (Troubleshooting)](#8-การแก้ไขปัญหาพื้นฐาน)

---

## 1. ภาพรวมและปรัชญาระบบ
PredictPlus1 คือระบบทำนายทิศทางราคาสินทรัพย์ล่วงหน้า 1 วัน (N+1) โดยเน้นผลลัพธ์ทางสถิติที่เกิดจาก **Pattern Recognition** แทนการใช้ Indicator ทางเทคนิคแบบดั้งเดิม

### 🔑 ปรัชญาการออกแบบ (Design Philosophy)
*   **Pure Statistics:** ระบบเชื่อว่าพฤติกรรมราคาในอดีต (History) คือหลักฐานที่เชื่อถือได้ที่สุด
*   **Fractal Patterns:** การใช้ชุดข้อมูลสัญญาณ (+, -, .) มาเรียงต่อกันเพื่อหาโอกาสการเกิดซ้ำ
*   **Adaptive Intelligence:** ระบบปรับเปลี่ยนขอบเขตการมอง (Lookback) และความผันผวน (Threshold) ตามสภาวะตลาดจริงของหุ้นแต่ละตัว

---

## 2. เทคโนโลยีหลัก: Aggregate Voting V4.4
ในเวอร์ชันล่าสุด (V4.4.7) ระบบได้ข้ามผ่านการเลือก Pattern เพียงอันเดียว (Best Fit) มาสู่ระบบ **"โหวตแบบรวมกลุ่ม"**

### 2.1 Dynamic Streak Extraction
ระบบจะไม่จำกัดจำนวนวันย้อนหลังที่ตายตัว (เช่น ไม่ใช่แค่ 4 วันเสมอไป) แต่จะสแกนย้อนหลังจากวันนี้จนกว่าจะเจอวัน **Neutral (.)** เพื่อหา "รอบราคา" (Streak) ที่แท้จริง

### 2.2 Suffix Level Voting
เมื่อได้ Pattern (เช่น `++-`) ระบบจะแตกย่อยออกเป็น Suffixes:
1.  **Suffix 3:** `++-` (ความสัมพันธ์ 3 วันล่าสุด)
2.  **Suffix 2:** `+-` (ความสัมพันธ์ 2 วันล่าสุด)
3.  **Suffix 1:** `-` (แนวโน้ม 1 วันล่าสุด)

### 2.3 ตรรกะแก่นกลาง: Weighted Consensus V4.5 (Core Philosophy)
ส่วนนี้คือ "หัวใจ" ของ PredictPlus1 ที่ใช้ตัดสินทิศทางและความมั่นใจ โดยเน้นการวัดผลจาก "หลักฐานที่แข็งแกร่งที่สุด" (Strongest Evidence) เท่านั้น

#### 🏁 ลำดับการประมวลผล (Execution Flow)

1.  **Pattern Dissection (Suffixing):** ระบบนำ Active Pattern ล่าสุดมาแตกกิ่งย่อย (Suffixes) จากยาวที่สุดไปหาท่อนท้ายสุด (เช่น `-++` ➔ `-++`, `++`, `+`)
2.  **The 30-Sample Gatekeeper (Filtering):** ทุกกิ่งต้องถูกตรวจสอบ Sample Size ในประวัติศาสตร์
    *   **Count ≥ 30:** ถือว่าเป็น **"Strong Pattern"** ➔ ได้สิทธิ์ไปต่อในรอบตัดสิน
    *   **Count < 30:** ถือว่าเป็น **"Weak Pattern"** ➔ **ถูกตัดออกจากการคำนวณโดยสิ้นเชิง** (ป้องกัน Error จากตัวอย่างที่น้อยเกินไป)
3.  **Local Winner Selection (Winner-Takes-All per Suffix):** ในแต่ละกิ่งที่ "Strong" ระบบจะดูว่าฝั่ง UP หรือ DOWN มีจำนวนครั้ง (Occurrence) มากกว่ากัน
    *   ฝั่งที่ชนะ ➔ ส่งจำนวนครั้งที่ชนะไปเป็น **"Vote Weight"** (น้ำหนักโหวต)
    *   ฝั่งที่แพ้ ➔ คะแนนในกิ่งนั้นจะกลายเป็น **0** ทันที (ไม่นำมาช่วยดึงคะแนนให้ฝั่งตัวเอง)
4.  **Consensus Aggregation:** ระบบรวมน้ำหนักโหวตจากทุกกิ่งที่ Strong
    *   `Total_UP_Weight` = ผลรวมของคะแนนโหวตจากกิ่งที่ UP ชนะ
    *   `Total_DOWN_Weight` = ผลรวมของคะแนนโหวตจากกิ่งที่ DOWN ชนะ
5.  **Final Results Formulation:**
    *   **ทิศทาง (Direction):** เลือกฝั่งที่มี `Total Weight` สูงกว่า
    *   **ความน่าเชื่อถือ (Prob%):** คำนวณจาก `Weight_Winner / Denominator_Base`
    *   **ฐานตัวหาร (Denominator Base):** คือผลรวมของ Occurrence ทั้งหมด (ทั้งฝั่งที่ชนะและแพ้) **เฉพาะจากกิ่งที่ Strong เท่านั้น**

---

#### 💡 กรณีศึกษา: เจาะลึกการคำนวณ (Case Study - ADVANTECH 2395)
เพื่อให้เห็นภาพความต่างระหว่าง **"น้ำหนักโหวต"** และ **"ฐานตัวหาร"**

| Suffix กิ่งย่อย | UP (+) | DOWN (-) | สถานะ (Status) | ผลต่อ Vote Weight | ผลต่อ Base (ตัวหาร) |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **กิ่ง A:** `-++` | 0 | 1 | **Weak** (Count < 30) | ไม่นับ (0) | ไม่นับ (0) |
| **กิ่ง B:** `++` | 3 | 3 | **Tie/Weak** | ไม่นับ (0) | ไม่นับ (0) |
| **กิ่ง C:** `+` | 19 | **28** | **Strong & DOWN Win** | **DOWN +28** | **47** (19+28) |

**สรุปผลลัพธ์ของเคสนี้:**
*   **Vote Weight (DOWN):** **28**  *(มาจากกิ่ง C ที่ชนะ)*
*   **Vote Weight (UP):** **0** *(เพราะกิ่ง A, B ถูกตัด และกิ่ง C แพ้)*
*   **Denominator (Base):** **47** *(เอาทุกอย่างในกิ่ง C มาเป็นฐาน ไม่ว่าจะขึ้นหรือลง)*
*   **ผลการทำนาย:** **🔴 DOWN** ที่ความมั่นใจ **59.6%** (มาจาก `28 / 47`)

---

#### ⚠️ หมายเหตุสำคัญ (Crucial Notes)
*   **ยอดฝั่งที่แพ้ไม่หายไปไหน:** "ไม่นับเป็นน้ำหนักโหวต" หมายถึงมันช่วยให้กิ่งนั้นชนะไม่ได้ แต่ "ยังต้องนับเป็นฐาน (Base)" เสมอ เพื่อให้ Prob% ไม่เว่อร์เกินจริง (ถ้าไม่หารด้วยยอดที่แพ้ ผลจะกลายเป็น 100% ซึ่งเป็น Logical Fallacy)
*   **ความโปร่งใส (Transparency):** แม้ Weak Pattern จะไม่ถูกคำนวณ แต่ต้องแสดงใน Report เพื่อให้ User เห็น "หลักฐานที่ระบบคัดทิ้ง" เสมอ
*   **พฤติกรรม Consensus:** ระบบนี้เน้นเลือกทิศทางที่มี "หมัดหนักจริง" (Strong Patterns) มาชกกันเท่านั้น กิ่งที่มีตัวอย่างแค่ 1-2 ครั้งจะม่สีสิทธิ์โหวตแม้แต่คะแนนเดียว

---

## 3. ตรรกะการวิเคราะห์รายตลาด
ระบบรองรับ 6 ตลาดหลัก โดยแบ่งการใช้งานตามพฤติกรรมราคาเฉพาะถิ่น

| ตลาด | ทฤษฎีหลัก (Strategy) | การทายผล (Direction) | Threshold Multiplier |
| :--- | :--- | :--- | :--- |
| 🇹🇭 **THAI (SET)** | **Mean Reversion** | สวนทาง (Contrarian) | 1.0x (Seek Alpha) |
| 🇺🇸 **US (NASDAQ)** | **Trend Following** | ตามเทรนด์ (Momentum) | 0.6x (Sensitive) |
| 🇨🇳 **CHINA (HKEX)** | **Mean Reversion** | สวนทาง | 0.8x (Reversion) |
| 🇹🇼 **TAIWAN (TWSE)** | **Regime-Aware** | ผสม (Trend + Reversion) | 0.9x (Balanced) |
| 🥇 **GOLD (Spot)** | **Trend / Breakout** | ตามความแรง | 0.3-0.6% (Fixed) |

---

## 4. ระบบบริหารความเสี่ยง (Risk Management)
V4.4.7 ยกระดับจากการทำนายทิศทาง (Direction) มาเป็นการจัดการแผนการเข้าเทรด (Trade Management)

### 4.1 Exit Strategies
*   **Stop Loss (SL):** ตัดขาดทุนทันทีเมื่อราคาผิดทาง (เน้นความปลอดภัย)
*   **Take Profit (TP):** ขายทำกำไรเมื่อถึงรอบ (คำนวณจาก ATR ของหุ้นแต่ละตัว)
*   **Trailing Stop:** กระโดดล้อไปตามกำไร (Lock Profit) โดยจะเริ่มทำงานเมื่อกำไรถึง +1.5%

### 4.2 Production Mode (ความสมจริง)
*   **Next Bar Open Entry:** จำลองการเข้าซื้อในราคาเปิดวันถัดไป (สะท้อนการเทรดจริง)
*   **Friction Cost:** หักค่าคอมมิชชั่นและค่าส่วนต่างราคา (Slippage) ออกจากผลกำไรทันที
*   **Gap Risk Factor:** เผื่อความเสี่ยงกรณีราคาเปิดกระโดดข้ามจุดตัดขาดทุน

---

## 5. คู่มือปฏิบัติการและการรันระบบ

### 🌅 กิจวัตรประจำวัน (Daily Routine)
1.  `python main.py`: สแกนหุ้นและสร้างคำทำนาย (รันหลังตลาดปิด)
2.  `python scripts/core_reports/view_report.py ALL`: ดูรายงาน Consensus (±Threshold, Prob%, Exp.Ret)
3.  `python scripts/core_reports/check_forward_testing.py --verify`: ตรวจคะแนนย้อนหลัง (Verify)

### 🔧 การบำรุงรักษา (Maintenance)
*   `python scripts/backfill/generate_master_stats.py`: รันเพื่อสร้างฐานข้อมูล Pattern ใหม่ (นาน 20-30 นาที)
*   `python scripts/maintenance/clear_cache.py`: ล้างข้อมูลราคาเก่ากรณีราคาเพี้ยน

> [!TIP]
> สำหรับรายละเอียดคำสั่งทั้งหมด (Arguments, Options) และการทำ Backfill ย้อนหลัง สามารถดูได้ที่:
> 👉 **[PredictPlus1_OPERATIONAL_MANUAL.md](file:///e:/PredictPlus1/PredictPlus1_OPERATIONAL_MANUAL.md)**

---

## 6. ประวัติการพัฒนาและวิวัฒนาการ (Detailed History)

### Phase 1: Foundation (V1.0 - V2.0)
*   **V1.0:** จุดเริ่มต้นของการใช้ Binary Signal (+/-) เพื่อทำนายวันถัดไป
*   **V2.0:** ขยายขอบเขตจากหุ้นรายตัวเป็นรายตลาด (Multi-Market)

### Phase 2: Statistical Rigor (V3.0 - V3.4)
*   **V3.1 (Strict Logic):** เปลี่ยนจากการข้ามวันนิ่ง (.) มาเป็นการตัด Streak ทันทีเพื่อความแม่นยำ
*   **V3.3 (The 4-Table Strategy):** เริ่มแบ่งหุ้นตามคุณภาพ (Strict, Balanced, Observation, Sensitivity)
*   **V3.4 (Adaptive Engine):** ระบบสแกนหา Pattern ความยาว 3-8 วันโดยอัตโนมัติเป็นครั้งแรก

### Phase 3: Market Tailoring (V10 - V13)
ในช่วงนี้ระบบเน้นการ "ปรับจูน" (Optimization) รายประเทศ:
*   **V10 & V11 (Thai Balancing):** ปรับลดค่า Threshold ของหุ้นไทยลงมาเท่ากับตลาดสากล เพื่อเพิ่มจำนวนสัญญาณเทรด (10-13x Increase)
*   **V12 (Taiwan Quality Focus):** แยก Logic ไต้หวันออกมา และปรับเกณฑ์ RRR ให้เข้มงวด (Min RRR 1.25) เพื่อชดเชยค่าคอมมิชชั่นที่สูง
*   **V13 (China Realistic Entry):** ปรับลดความต้องการ Prob% และ Count ลง เพื่อให้สามารถเทรดหุ้นจีนกลุ่ม Tech ได้ทั่วถึงขึ้น

### Phase 4: Synthesis & Consensus (V4.4.7)
*   **V4.4 (Current):** ยกเลิกการเลือก "Pattern ที่ดีที่สุด" เพียงอันเดียว เพราะเสี่ยงต่อการเกิด Overfitting
*   **Aggregate Voting:** นำข้อดีของทุก Version เดิมมาผสมผสานกันผ่านการโหวตแบบ Consensus เพื่อความเสถียรสูงสุดในสภาวะตลาดผันผวน

---

## 7. โครงสร้างข้อมูลและระบบหน่วยความจำ
*   **Smart Cache:** ระบบจะดึงข้อมูลเฉพาะส่วนต่าง (Delta) 50 วันล่าสุดมาต่อเข้ากับไฟล์เดิม ช่วยประหยัดเวลา API ลง 99%
*   **Master_Pattern_Stats_NewLogic.csv:** คือ "คลังความรู้" ของระบบที่บรรจุความจำของหุ้น 200+ ตัว ย้อนหลัง 20 ปี

---

## 8. การแก้ไขปัญหาพื้นฐาน
*   **FileNotFound `performance_log.csv`:** ให้รัน `main.py` ครั้งแรก ระบบจะสร้างไฟล์ให้เอง
*   **API Connection Error:** ตรวจสอบไฟล์ `.env` และความเสถียรของอินเทอร์เน็ต
*   **No Patterns Found:** หุ้นที่เข้าใหม่อาจมี Bars ไม่ถึง 300 วัน หรือหุ้นนิ่งเกินไปจนไม่เกิดสัญญาณ

---
*PredictPlus1 Manual V4.4.7 — Updated 2026-02-22*
