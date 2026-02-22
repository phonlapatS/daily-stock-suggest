# PredictPlus1 V4.4.7 — คู่มือการใช้งานคำสั่ง (Operational Commands Manual) 📘

คู่มือนี้รวบรวมคำสั่งพื้นฐานและการใช้งานระบบระดับสูง ทั้งการสแกนรายวัน, การดูรายงาน, และการดึงข้อมูลย้อนหลัง (Backfill)

---

## 🚀 1. การรันระบบประจำวัน (Daily Routine)

หากต้องการรันทุกอย่างในขั้นตอนเดียว (สแกน -> คำนวณ -> ทำรายงาน -> แดชบอร์ด):
```powershell
python run_daily_routine.py
```

### คำสั่งแยกส่วน (Manual Commands)
*   **รันหลัก (สแกน + ตรวจการบ้าน):** `python main.py`
    *   ระบบจะดึงราคาเพื่อทำนายใหม่ **และจะตรวจผลของเมื่อวานให้โดยอัตโนมัติ**
*   **ตรวจผลแบบ Manual (ส่องประวัติ):** `python scripts/check_forward_testing.py --verify`
    *   ใช้สำหรับเจาะลึกดูประวัติ หรือบังคับตรวจผลโดยไม่ต้องรันสแกนใหม่

---

## 📊 2. การดูรายงานเชิงลึก (Reporting & Analysis)

### 📈 รายงานสรุป Consensus
*   **ดูสรุปทุกตัว:** `python scripts/core_reports/view_report.py ALL`
*   **ดูเจาะจงรายตัว:** `python scripts/core_reports/view_report.py PTT` (หรือ Ticker อื่นๆ)
    *   *ใช้ดูค่า Consensus, Probability %, และ Weight การโหวตของแต่ละ Pattern*
    *   ✨ **V4.4.7 Feature:** เพิ่มส่วน **CONSENSUS BREAKDOWN** แสดงคะแนนดิบ (Wins/Losses) ของแต่ละ Suffix Pattern เพื่อความโปร่งใสก่อนสรุปผล

### 🏆 รายงานผลตอบแทน (Stat Analytics)
*   **สรุป Win-Rate รายตลาด:** `python scripts/analysis/calculate_performance.py`
    *   คำนวณ Win/Loss, Avg Profit, และสร้างไฟล์สรุปใน `data/stats_[market].csv`
*   **ดูประวัติความแม่นยำ:** `python scripts/analysis/view_accuracy.py`
    *   แสดงความแม่นยำย้อนหลัง 7, 30, 90 วัน แบ่งตาม Ticker

---

## 🔄 3. การดึงข้อมูลย้อนหลัง & ซ่อมประวัติ (Backfill & Data Reconstruction)

ระบบ V4.4.7 มีเครื่องมือประสิทธิภาพสูงในการ "สร้างประวัติการทำนายย้อนหลัง" โดยใช้ข้อมูลราคาในอดีตมาจำลองการทาย

### 🛠️ เครื่องมือ Backfill หลัก (Heavy Reconstruction)
ใช้เมื่อต้องการสร้าง `performance_log.csv` ใหม่ทั้งหมดเพื่อดู Win-rate ย้อนหลังหลายสัปดาห์

*   **รันย้อนหลัง (Default เป็นวันที่ 12 ก.พ.):**
    ```powershell
    python scripts/backfill/backfill_forward_testing.py
    ```
*   **รันย้อนหลังระบุวันที่:**
    ```powershell
    python scripts/backfill/backfill_forward_testing.py --start-date 2026-02-01
    ```
    *   **สิ่งที่เกิดขึ้น:** ระบบจะไปดึงราคาจาก TradingView -> คำนวณ Pattern ณ วันนั้นๆ -> บันทึกลง Log เพื่อให้คุณใช้ `calculate_performance.py` วิเคราะห์ความแม่นยำย้อนหลังได้เสมือนรันระบบจริงมาทุกวัน

### 🧼 เครื่องมือ Sync ข้อมูล (Log Maintenance)
*   **Sync ผลทำนายวันนี้:** `python scripts/backfill/backfill_performance_log.py`
    *   ใช้สำหรับอัปเดตค่า `change_pct` และ `threshold` จากไฟล์รายงานเข้าสู่ Performance Log

---

## 🧪 4. การทดสอบกลยุทธ์ (Backtest & Research)

*   **ทดสอบ Pattern Matching:** `python scripts/backtest/backtest.py PTT SET 1000`
    *   ทดสอบหุ้น PTT ในตลาด SET ย้อนหลัง 1,000 วัน เพื่อดูว่าถ้าใช้ระบบนี้ทายมา 3 ปี จะแม่นแค่ไหน
*   **จำลองเส้นกราฟเงินทุน (Equity Curve):** `python scripts/backtest/simulate_equity_curves.py`
    *   ใช้ประวัติจาก Log มาวาดกราฟว่าพอร์ตจะโตยังไง (ต้องรัน Backfill ก่อน)

---

## 🧹 5. การบำรุงรักษา (Maintenance)

*   **ล้าง Cache ราคาที่ค้าง:** `python scripts/maintenance/clear_cache.py`
    *   ใช้เมื่อข้อมูลราคาใน TradingView ดูผิดเพี้ยน หรือต้องการดึงใหม่จากกราฟจริง
*   **ล้าง Cache ทุกตลาด:** `python scripts/maintenance/clean_all_cache.py`
*   **จัดการข้อมูลซ้ำ:** `python scripts/maintenance/cleanup_duplicate_forecasts.py`
    *   แก้ปัญหาการรันสแกนซ้ำหลายรอบในวันเดียวจน Log บวม

---

## 💡 คำแนะนำเพิ่มเติม (Tips)

1.  **การดึงข้อมูลย้อนหลัง:** แนะนำให้รัน `backfill_forward_testing.py` ก่อนเป็นอันดับแรกหากต้องการทดสอบระบบกับตลาดใหม่ๆ
2.  **การรันรายวัน:** ใช้ `run_daily_routine.py` เป็นหลักเพื่อความสะดวก ระบบจะเชื่อมต่อทุกสคริปต์ให้ทำงานต่อเนื่องกันอัตโนมัติ
3.  **การปรับปรุงระบบ:** หากมีการปรับแก้ `config.py` ควรล้าง Cache ด้วย `clear_cache.py` เพื่อให้ระบบคำนวณใหม่ตาม config ที่เปลี่ยนไป
