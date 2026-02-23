# PredictPlus1 V4.5 — คู่มือการใช้งานคำสั่ง (Operational Commands Manual) 📘

คู่มือนี้รวบรวมคำสั่งพื้นฐานและการใช้งานระบบระดับสูง ทั้งการสแกนรายวัน, การดูรายงาน, และการวัดผลความแม่นยำ

---

## 🚀 1. การรันระบบประจำวัน (Daily Routine)

หากต้องการรันทุกอย่างในขั้นตอนเดียว (สแกน -> ลง Log -> ทำรายงาน -> แดชบอร์ด):
```powershell
python run_daily_routine.py
```

### คำสั่งแยกส่วน (Manual Commands)
*   **เริ่มสแกนทำนาย (Predict N+1):** `python main.py`
    *   ทำนายราคาสำหรับวันพรุ่งนี้ (N+1) โดยใช้เกณฑ์ **30-Match Minimum** และ **Mean Reversion Engine** ในทุกตลาด
*   **ตรวจสอบและ Verify ผล (Verify):** `python scripts/core_reports/check_forward_testing.py --verify`
    *   ดึงราคาปัจจุบันมาเปรียบเทียบกับคำทำนายเมื่อวานเพื่อสรุปผล Correct/Incorrect

---

## 📊 2. การดูรายงานเชิงลึก (Reporting & Analysis)

### 📈 รายงานสรุป Fractal Consensus (Deep Dive)
*   **ดูสรุปทุกตัว:** `python scripts/view_report.py ALL`
*   **ดูเจาะจงรายตัว:** `python scripts/view_report.py PTT`
    *   *ใช้ดูค่า Consensus, Probability %, และการโหวตของแต่ละ Suffix Pattern*
    *   ✨ **V4.4 Logic:** แสดงเฉพาะ Pattern ที่มีข้อมูลย้อนหลัง 30 ครั้งขึ้นไป (ถ้าต่ำกว่าจะเป็น Weak และไม่ถูกนำมาคำนวณ)

### 🏆 แดชบอร์ดภาพรวมผลงาน (Executive Dashboard)
*   **ดู Dashboard สรุป:** `python scripts/daily_forecast_dashboard.py`
    *   แสดงทั้งคำทำนายของวันพรุ่งนี้ และสรุปความแม่นยำ (Winrate/RRR) ย้อนหลังทุกลำดับ

### 🎯 การคำนวณประสิทธิภาพ (Performance Analysis)
*   **สรุป Win-Rate รายตลาด:** `python scripts/analysis/calculate_performance.py`
    *   คำนวณ Win/Loss, Avg Profit, และสร้างไฟล์สรุปใน `data/stats_[market].csv`

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
