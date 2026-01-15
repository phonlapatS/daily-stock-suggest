# Stock Prediction System

📊 **ระบบทำนายหุ้นแบบ Pure Data-Driven - Historical Pattern Matching**

> **🆕 Recent Updates (2026-01-14):**
> - ✅ **Data Pipeline** - `data_updater.py` พร้อม Parquet storage (รองรับ 100+ หุ้น)
> - ✅ **Output** - แสดงสถิติแบบ Range แยก +/- ชัดเจน
> - ✅ **Docs** - Flow diagrams ครบ 3 ไฟล์ (SYSTEM_FLOW, SIMPLE_FLOW, DATA_PIPELINE_GUIDE)

## 💡 โจทย์

**ถ้าวันนี้หุ้นขึ้น/ลง เกิน ±1% → ทายว่าพรุ่งนี้จะเป็นอย่างไร**

Output:
1. ทิศทาง (Up/Down)
2. เปอร์เซ็นต์ (กี่ %)
3. ความน่าจะเป็น (กี่ %)  
4. ความเสี่ยง (Risk metrics)

**วิธีการ:** ใช้ Historical Pattern Matching - ค้นหาว่าเคยมีวันที่ขึ้น/ลงแบบนี้กี่ครั้ง แล้ววันถัดไปเกิดอะไรขึ้น

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### หุ้นไทย (Daily)
```bash
python main_stats_extraction.py --symbol PTT --exchange SET --predict
```

### หุ้นอเมริกา (Daily)
```bash
python main_stats_extraction.py --symbol AAPL --exchange NASDAQ --predict
```

### ทองคำ (Intraday 15min)
```bash
python main_stats_extraction.py --symbol XAUUSD --exchange OANDA --timeframe intraday --interval 15 --predict
```

---

## 🎯 Timeframe ตามประเภทสินทรัพย์

### หุ้นรายตัว → Daily (D)
- 🇹🇭 ไทย: PTT, CPALL, AOT, KBANK
- 🇺🇸 อเมริกา: AAPL, MSFT, GOOGL, TSLA
- 🇨🇳 จีน: BABA, JD

**เหตุผล:** หุ้นได้รับอิทธิพลจากข่าว → daily analysis เหมาะสม

### Gold/Silver → Intraday (15min, 30min)
- 🥇 XAUUSD (Gold)
- 🥈 XAGUSD (Silver)

**เหตุผล:** เทรดสั้นและไว, เน้น scalping

---

## 📊 ข้อมูลต้องมีเท่าไหร่ถึงจะเชื่อถือได้?

### Daily (หุ้น):
- ขั้นต่ำ: 3 ปี (750 bars)
- แนะนำ: **5 ปี** (1,250 bars)
- ดีที่สุด: 10 ปี (2,500 bars)

```bash
python main_stats_extraction.py --symbol PTT --exchange SET --nbars 1250 --predict
```

### Intraday (Gold/Silver):
- 15min: 6-12 เดือน (~17,000-35,000 bars)
- 30min: 6-12 เดือน (~8,500-17,500 bars)

```bash
python main_stats_extraction.py --symbol XAUUSD --exchange OANDA --timeframe intraday --interval 15 --nbars 17000 --predict
```

### จำนวน Similar Patterns:
- < 30 patterns: ⚠️ ไม่เชื่อถือ
- 30-50: 🟡 พอใช้
- 50-100: ✅ ดี
- 100+: ✅✅ ยอดเยี่ยม

---

## 🌍 รองรับหุ้นทุกประเทศ

ระบบไม่ fixed - ใช้ได้กับทุกตลาด:

```bash
# หุ้นจีน
python main_stats_extraction.py --symbol BABA --exchange NYSE --predict

# Crypto
python main_stats_extraction.py --symbol BTCUSD --exchange BINANCE --timeframe intraday --interval 15

# หลายหุ้นพร้อมกัน
python main_stats_extraction.py --market thai --predict
```

**วิธีหา Symbol:** ไป TradingView.com → ค้นหา → ดู Symbol และ Exchange

---

## 📋 Template คำสั่ง

```bash
python main_stats_extraction.py \
  --symbol <SYMBOL> \
  --exchange <EXCHANGE> \
  --timeframe <daily|intraday> \
  --interval <15|30|60> \
  --nbars <จำนวน> \
  --predict
```

---

## 🎯 Features

- ✅ **Pure Statistics** - 100% data-driven, ไม่มี ML model
- ✅ **Multi-Timeframe** - Daily และ Intraday
- ✅ **Multi-Market** - หุ้นทุกประเทศ
- ✅ **Prediction** - ทิศทาง + % + Probability + Risk
- ✅ **Visualization** - 4 กราฟอัตโนมัติ
- ✅ **Streak Detection** - หา patterns ที่เกิดติดต่อกัน

---

## 📊 Output

### 1. Statistics (JSON + Console)
```json
{
  "total_significant_days": 450,
  "probabilities": {
    "up_after_positive": 52.2,
    "down_after_positive": 34.8
  },
  "risk": {
    "max_loss_after_positive": -5.5,
    "avg_error": 1.2
  }
}
```

### 2. Prediction (ถ้าเปิด --predict)
```
🔮 PREDICTION for Tomorrow:
   Direction: UP
   Expected change: +0.85%
   Confidence: 65.2%
   Risk (worst case): -1.2%
   Based on 120 historical patterns
```

### 3. Visualizations
- Distribution plot
- Next-day outcomes bar chart
- Probability heatmap
- Streak analysis

---

## ⚡ Performance Optimization

### ปัญหา: หุ้นเยอะ ดึงช้า
- SET: ~700 ตัว
- NASDAQ: ~3,000 ตัว
- ไม่ optimize = **35+ นาที!** ❌

### Solutions: ✅

#### 1. Data Caching (เร็วขึ้น 30x)
```python
from data_cache import OptimizedDataFetcher

fetcher = OptimizedDataFetcher(use_cache=True)

# ครั้งแรก: ช้า (~3 วินาที)
df = fetcher.fetch_daily_data('PTT', 'SET')

# ครั้งต่อไป: เร็วมาก (~0.1 วินาที) ✅
df = fetcher.fetch_daily_data('PTT', 'SET')  # ใช้ cache
```

#### 2. Batch Processing
```python
from batch_processor import BatchStockProcessor

processor = BatchStockProcessor(use_cache=True)

stocks = [
    {'symbol': 'PTT', 'exchange': 'SET'},
    {'symbol': 'CPALL', 'exchange': 'SET'},
    # ... 698 ตัวอื่น
]

# ประมวลผลทั้งหมด พร้อม progress tracking
results = processor.process_batch(stocks)
```

#### 3. Selective Scanning
```python
# กรองเฉพาะหุ้นที่วันนี้เคลื่อนไหว ±1%
# ลดจาก 700 → ~70 ตัว
```

**ผลลัพธ์:**
- วันแรก: 35 นาที (ครั้งเดียว)
- วันถัดไป: **5-10 นาที** ✅
- เฉพาะที่เคลื่อนไหว: **1-2 นาที** ✅✅

**ดูรายละเอียด:** [PERFORMANCE_OPTIMIZATION.md](file:///Users/rocket/Desktop/Intern/predict/PERFORMANCE_OPTIMIZATION.md)

---

## 📁 Project Structure

```
predict/
├── Core Modules
│   ├── config.py                # Settings
│   ├── utils.py                 # Helper functions
│   ├── data_fetcher.py          # TradingView data
│   ├── stats_analyzer.py        # Statistics
│   ├── predictor.py             # 🔮 Prediction
│   └── visualizer.py            # Plots
├── Optimization
│   ├── data_cache.py            # ⚡ Caching system
│   └── batch_processor.py       # ⚡ Batch processing
├── Scripts
│   ├── main_stats_extraction.py # Main script
│   ├── demo_workflow.py         # Workflow demo
│   └── demo_multi_market.py     # Multi-market demo
├── Documentation
│   ├── README.md                # This file
│   ├── PERFORMANCE_OPTIMIZATION.md # ⚡ Performance guide
│   ├── project_overview.md      # Project overview
│   └── system_design.md         # Technical design
└── requirements.txt             # Dependencies
```


---

## 🎓 Use Cases

### นักลงทุนหุ้นไทย
```bash
# Scan ทุกเช้า
python main_stats_extraction.py --market thai --predict
```

### Day Trader (Gold)
```bash
python main_stats_extraction.py --symbol XAUUSD --exchange OANDA --timeframe intraday --interval 15 --predict
```

### Global Investor
```bash
python demo_multi_market.py
```

---

## ⚙️ Configuration

แก้ไขใน `config.py`:

```python
THRESHOLD_PERCENT = 1.0      # กรองวันที่ ±1%
MIN_STREAK_LENGTH = 4        # streak ขั้นต่ำ
DEFAULT_N_BARS = 5000        # จำนวนข้อมูล
```

เพิ่มหุ้นที่ติดตาม:

```python
DEFAULT_STOCKS = {
    'thai': ['PTT', 'CPALL', 'AOT', 'KBANK'],
    'us': [
        {'symbol': 'AAPL', 'exchange': 'NASDAQ'},
        {'symbol': 'TSLA', 'exchange': 'NASDAQ'}
    ]
}
```

---

## ✨ Example Output

```
🔮 AAPL Prediction (Today: +1.8%)
====================================
Tomorrow: UP (+0.25%)
Confidence: 65.4%
Risk if wrong: -1.2%
Based on 146 historical patterns ✅

📈 Probability:
   Up: 65.4%
   Down: 24.1%
   Sideways: 10.5%
```

---

## 📚 More Documentation

- [project_overview.md](file:///Users/rocket/Desktop/Intern/predict/project_overview.md) - ภาพรวมโปรเจ็ค
- [system_design.md](file:///Users/rocket/Desktop/Intern/predict/system_design.md) - System design
- [walkthrough.md](file:///Users/rocket/Desktop/Intern/predict/walkthrough.md) - ผลการทดสอบ

---

## ⚠️ Important Notes

- ระบบนี้เป็น **statistics** ไม่ใช่ prediction model
- ผลลัพธ์เป็น **descriptive analytics** จากอดีต
- ไม่ใช่คำแนะนำการลงทุน
- ควรใช้ร่วมกับการวิเคราะห์อื่นๆ

---

**ระบบพร้อมใช้งาน - ทดสอบกับหุ้นของคุณได้เลย!** 📈


📊 **ระบบวิเคราะห์สถิติและทำนายหุ้นแบบ Pure Data-Driven**

## 💡 แนวคิดโปรเจ็ค

**โจทย์:** ถ้าวันนี้ราคาหุ้นขึ้น/ลง เกิน ±1% → ระบบจะทายว่า**พรุ่งนี้**หุ้นตัวนั้นจะเป็นยังไง

**Output ที่ต้องการ:**
1. **ทิศทาง:** ขึ้น หรือ ลง
2. **เปอร์เซ็นต์:** จะขึ้น/ลง กี่ %
3. **ความน่าจะเป็น:** มีโอกาสเกิด กี่ %
4. **ความเสี่ยง:** ถ้าผิดทาง จะเสียหายกี่ %

**วิธีการ:** ใช้ **Historical Pattern Matching** ไม่ใช้ ML model
- ค้นหาในอดีตว่า เคยมีวันที่ขึ้น/ลงแบบนี้กี่ครั้ง
- ดูว่าวันถัดไปของครั้งเหล่านั้น เกิดอะไรขึ้น
- สรุปเป็นสถิติและทำนายจากข้อมูลจริง

---

## 🎯 Features

- ✅ **Pure Statistics** - วิเคราะห์จากข้อมูลจริง 100% ไม่มี ML model
- 📈 **Multiple Timeframes** - รองรับทั้ง Daily และ Intraday (15m, 30m, 1h)
- 🇹🇭 **Thai Stocks** - รองรับหุ้นไทย (SET) ผ่าน TradingView
- 🇺🇸 **US Stocks** - รองรับหุ้นสหรัฐ (NASDAQ, NYSE)
- 🔥 **Streak Detection** - ตรวจจับ streak patterns (4+ วันติดต่อกัน)
- 📊 **Visualization** - สร้างกราฟแสดงผลอัตโนมัติ
- 🎲 **Probability Calculation** - คำนวณความน่าจะเป็นจากข้อมูลจริง
- ⚠️ **Risk Metrics** - วัดความเสี่ยงจากสถิติที่เกิดขึ้น

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### วิเคราะห์หุ้นเดียว (Statistics Only)

```bash
# หุ้นไทย (Daily)
python main_stats_extraction.py --symbol PTT --exchange SET

# หุ้นสหรัฐ (Daily)
python main_stats_extraction.py --symbol AAPL --exchange NASDAQ

# Intraday 15 นาที
python main_stats_extraction.py --symbol PTT --exchange SET --timeframe intraday --interval 15

# กำหนด threshold เอง
python main_stats_extraction.py --symbol CPALL --exchange SET --threshold 2.0
```

### ทำนายวันพรุ่งนี้ (Prediction Mode) 🔮

```bash
# เปิด prediction mode ด้วย --predict flag
python main_stats_extraction.py --symbol PTT --exchange SET --predict

# ผลลัพธ์จะแสดง:
# - วิเคราะห์สถิติทั้งหมดตามปกติ
# - ดูการเคลื่อนไหววันล่าสุด (ถ้า >= ±1%)
# - ทำนายว่าพรุ่งนี้จะเป็นอย่างไร
# - บันทึก prediction เป็น JSON

# ตัวอย่าง Output:
# 📊 Latest movement: +1.8%
# 🔮 PREDICTION for Tomorrow:
#    Direction: UP
#    Expected change: +0.85%
#    Confidence: 65.2%
#    Risk (worst case): -1.2%
```


### วิเคราะห์หลายหุ้นพร้อมกัน

```bash
# วิเคราะห์หุ้นไทยทั้งหมดใน config
python main_stats_extraction.py --market thai

# วิเคราะห์หุ้นสหรัฐทั้งหมดใน config
python main_stats_extraction.py --market us
```

### รัน Default

```bash
# รัน default (วิเคราะห์ PTT และ CPALL)
python main_stats_extraction.py
```

## 📊 Output

ระบบจะสร้าง:

1. **JSON Reports** → `results/`
   - สถิติครบถ้วนเป็น JSON format
   
2. **Visualizations** → `plots/`
   - Distribution of returns
   - Next-day outcome charts
   - Probability heatmap
   - Streak analysis

3. **Console Report** → แสดงผลสรุปบน terminal

## 📁 Project Structure

```
predict/
├── config.py                # การตั้งค่าระบบ
├── utils.py                 # Helper functions
├── data_fetcher.py          # ดึงข้อมูลจาก TradingView
├── stats_analyzer.py        # วิเคราะห์สถิติ
├── visualizer.py            # สร้างกราฟ
├── main_stats_extraction.py # Script หลัก
├── requirements.txt         # Dependencies
├── data/                    # ข้อมูลดิบ (ถ้ามี)
├── results/                 # ผลลัพธ์ JSON
└── plots/                   # กราฟ
```

## 📋 Output Format

```json
{
  "threshold": 1.0,
  "total_days": 1500,
  "total_significant_days": 450,
  "positive_moves": 230,
  "negative_moves": 220,
  "next_day_stats": {
    "after_positive": {
      "up": 120,
      "down": 80,
      "sideways": 30,
      "avg_change": 0.45
    },
    "after_negative": { ... }
  },
  "probabilities": {
    "up_after_positive": 52.2,
    "down_after_positive": 34.8,
    ...
  },
  "risk": {
    "avg_error_after_positive": 1.2,
    "max_loss_after_positive": -5.5,
    ...
  },
  "streaks": [ ... ]
}
```

## 🔧 Configuration

แก้ไขใน `config.py`:

```python
THRESHOLD_PERCENT = 1.0      # กรองวันที่ ±1%
MIN_STREAK_LENGTH = 4        # streak ขั้นต่ำ
DEFAULT_N_BARS = 5000        # จำนวนข้อมูลที่ดึง
SIDEWAYS_THRESHOLD = 0.5     # threshold สำหรับ sideways
```

## 🎯 Use Cases

1. **วิจัยตลาด** - ศึกษาพฤติกรรมของหุ้นหลังการเคลื่อนไหวรุนแรง
2. **Backtesting** - ทดสอบกลยุทธ์ที่อิงสถิติจริง
3. **Risk Management** - ประเมินความเสี่ยงจากข้อมูลประวัติศาสตร์
4. **Pattern Recognition** - หา pattern ที่เกิดซ้ำบ่อย

## ⚠️ Important Notes

- ระบบนี้เป็น **pure statistics** ไม่ใช่ prediction model
- ผลลัพธ์เป็น **descriptive analytics** จากอดีต
- ไม่ใช่คำแนะนำการลงทุน
- ควรใช้ร่วมกับการวิเคราะห์อื่นๆ

## 📚 Next Steps (Future Development)

- [ ] Phase 2: เพิ่ม ML model (XGBoost)
- [ ] Phase 3: Web dashboard
- [ ] Phase 4: Telegram/Line notification
- [ ] Phase 5: Real-time monitoring

---

Made with ❤️ for pure data-driven analysis
