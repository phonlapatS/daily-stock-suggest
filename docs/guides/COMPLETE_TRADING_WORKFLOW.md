# Complete Trading Workflow: จากข้อมูล → การตัดสินใจ

## 🎯 ภาพรวม

ระบบนี้ไม่ใช่แค่ "ดึงข้อมูล" แล้วจบ แต่เป็น **Daily Trading Decision System**

---

## 📅 Daily Workflow (ทุกวันหลังตลาดปิด)

### **17:00 - Update Data**
```bash
python pipeline/data_updater.py
```
**ได้:**
- ข้อมูลล่าสุด (วันนี้)
- Parquet files updated

---

### **17:05 - Run Analysis**
```bash
python scripts/scanner.py
```
**ได้:**
- รายงาน 51 หุ้น
- Probability สำหรับพรุ่งนี้ (N+1)

**ตัวอย่าง Output:**
```
Symbol  Price   Change  Streak       WinRate  AvgRet  MaxRisk  Events
PTT     ฿32.75  +3.15%  Up 3 Days    43.0%    +0.13%  -9.43%   272
SCC     ฿206    +4.39%  Up 1 Days    65.0%    +0.80%  -3.20%   150
ADVANC  ฿339    +1.81%  Up 1 Days    38.0%    -0.10%  -5.58%   269
```

---

### **17:10 - Filter & Rank**
```bash
python scripts/view_scanner.py streaks
```

**ดู:**
- Active streaks only
- เรียงตาม WinRate

**Filter Criteria (ตัวอย่าง):**
```python
# หุ้นที่สนใจ
good_stocks = df[
    (df['Events'] >= 50) &      # ข้อมูลเพียงพอ
    (df['WinRate'] >= 55) &     # มี edge
    (df['AvgRet'] >= 0.3) &     # คุ้มค่า
    (df['MaxRisk'] >= -5)       # Risk ไม่สูงเกิน
]
```

**ผลลัพธ์:**
```
Symbol  WinRate  AvgRet  MaxRisk  Events  Score
SCC     65.0%    +0.80%  -3.20%   150     ⭐⭐⭐⭐⭐
```

---

### **17:30 - Make Decisions**

#### **Option 1: Manual Review**
```
ดู SCC:
- WinRate 65% → ดี!
- AvgRet +0.80% → คุ้มค่า
- Events 150 → ข้อมูลเพียงพอ
- MaxRisk -3.20% → ยอมรับได้

✅ ตัดสินใจ: ซื้อ SCC พรุ่งนี้
```

#### **Option 2: Automated Signal**
```python
# สร้าง trading signals
def generate_signals(df):
    signals = []
    
    for _, row in df.iterrows():
        if (row['WinRate'] >= 60 and 
            row['AvgRet'] >= 0.5 and 
            row['Events'] >= 50):
            
            signals.append({
                'symbol': row['Symbol'],
                'action': 'BUY',
                'confidence': row['WinRate'],
                'target': row['AvgRet'],
                'stop_loss': row['MaxRisk']
            })
    
    return signals
```

**Output:**
```json
{
  "symbol": "SCC",
  "action": "BUY",
  "confidence": 65.0,
  "target": 0.80,
  "stop_loss": -3.20
}
```

---

### **17:45 - Position Sizing**

```python
def calculate_position(
    capital=100000,      # เงินทุน
    risk_per_trade=0.02, # เสี่ยง 2% ต่อรอบ
    max_risk=-3.20       # MaxRisk จาก scanner
):
    # คำนวณจำนวนหุ้นที่ซื้อได้
    risk_amount = capital * risk_per_trade  # 2,000 บาท
    
    # ถ้า MaxRisk -3.20% = เสี่ยงขาดทุน 3.20%
    # จำนวนเงินที่ลงได้ = risk_amount / |max_risk|
    position_value = risk_amount / abs(max_risk/100)
    
    return position_value
```

**ตัวอย่าง:**
```
เงินทุน: 100,000 บาท
Risk: 2% = 2,000 บาท
MaxRisk: -3.20%

Position = 2,000 / 0.032 = 62,500 บาท

SCC ราคา 206 บาท
จำนวน = 62,500 / 206 = 303 หุ้น
```

---

### **18:00 - Plan for Tomorrow**

**สร้าง Trading Plan:**
```
Date: 16 Jan 2026
Action: BUY

Symbol: SCC
Price: ~206 (ประมาณ)
Quantity: 303 shares
Entry: Market Open or Limit 205-207

Take Profit: 206 + (206 × 0.80%) = 207.65
Stop Loss: 206 - (206 × 3.20%) = 199.41

Expected:
- Win Rate: 65%
- Target: +0.80% (+1,648 บาท)
- Max Loss: -3.20% (-2,000 บาท)
```

---

## 🔄 Next Day (วันพรุ่งนี้)

### **09:00 - Execute**
```
1. เปิดโบรกเกอร์
2. ซื้อ SCC 303 หุ้น @ 206
3. ตั้ง Stop Loss @ 199.41
4. ตั้ง Take Profit @ 207.65
```

### **16:30 - Review Result**
```
Scenario 1: Win (+0.75%)
→ ขาย @ 207.55
→ กำไร +1,623 บาท ✅

Scenario 2: Loss (-3.10%)
→ Stop Loss @ 199.50
→ ขาดทุน -1,968 บาท ❌

Scenario 3: Break Even
→ ตลาดไม่เคลื่อนไหว
```

### **17:00 - Repeat Cycle**
```bash
# Update data ใหม่
python pipeline/data_updater.py

# Scan ใหม่สำหรับวันรุ่งขึ้น (N+2)
python scripts/scanner.py
```

---

## 📊 Long-term: Backtesting

### **ทดสอบว่าระบบทำงานจริงไหม**

```python
# backtest.py
def backtest_strategy(historical_data, strategy):
    """
    ทดสอบกลับหลัง 1 ปี
    """
    results = []
    capital = 100000
    
    for day in historical_data:
        # 1. Run scanner
        signals = scanner.analyze(day)
        
        # 2. Filter
        good_signals = filter_signals(signals)
        
        # 3. Execute
        for signal in good_signals:
            result = execute_trade(signal, day+1)
            results.append(result)
            capital += result['profit']
    
    return results
```

**ผลลัพธ์:**
```
Backtest Results (365 days):
- Total Trades: 120
- Wins: 72 (60%)
- Losses: 48 (40%)
- Total Return: +15.2%
- Sharpe Ratio: 1.8
- Max Drawdown: -8.5%
```

---

## 🎯 Real-world Applications

### **1. Day Trading**
```
Daily:
- ดู scanner ทุกวัน
- เลือกหุ้น high WinRate
- Trade วันเดียว
```

### **2. Swing Trading**
```
Weekly:
- ดู streak ที่แข็งแรง
- Hold 3-5 วัน
- Take profit ตาม AvgRet
```

### **3. Portfolio Screening**
```
Monthly:
- ดูหุ้นที่มี pattern ดี
- สร้าง watchlist
- ติดตามต่อเนื่อง
```

---

## 🚀 Next Level: Automation

### **สร้าง Trading Bot**

```python
# trading_bot.py
import schedule

def daily_analysis():
    # 1. Update data
    os.system('python pipeline/data_updater.py')
    
    # 2. Run scanner
    df = run_scanner()
    
    # 3. Generate signals
    signals = generate_signals(df)
    
    # 4. Send notification
    send_line_notify(signals)
    
    # 5. (Optional) Auto-trade via API
    # execute_orders(signals)

# Run every day at 17:00
schedule.every().day.at("17:00").do(daily_analysis)
```

**Output (LINE Notify):**
```
📊 Daily Trading Signals (16 Jan 2026)

🟢 BUY Signals:
1. SCC: WinRate 65%, Target +0.80%
2. PTT: WinRate 58%, Target +0.40%

⚠️ High Risk:
3. DELTA: WinRate 52%, MaxRisk -12%

Total: 3 signals
```

---

## 📈 Performance Tracking

### **สร้าง Performance Dashboard**

```python
# performance.py
def track_performance():
    """
    ติดตาม Performance ของ strategy
    """
    trades = load_trade_history()
    
    metrics = {
        'win_rate': calculate_win_rate(trades),
        'avg_return': calculate_avg_return(trades),
        'sharpe': calculate_sharpe(trades),
        'max_dd': calculate_max_drawdown(trades)
    }
    
    plot_performance(trades, metrics)
```

**Dashboard:**
```
=== Strategy Performance ===
Period: Jan - Dec 2026
Total Trades: 250
Win Rate: 62%
Avg Return: +0.45%
Total Return: +18.5%
Sharpe Ratio: 2.1
Max Drawdown: -6.2%
==========================
```

---

## ✅ สรุป Complete Workflow

```
Day 1 (Today):
1. 17:00 → Update data
2. 17:05 → Run scanner
3. 17:10 → Filter signals
4. 17:30 → Make decisions
5. 17:45 → Calculate positions
6. 18:00 → Plan for tomorrow

Day 2 (Tomorrow):
1. 09:00 → Execute trades (N+1)
2. 16:30 → Close/Monitor positions
3. 17:00 → Update & Scan (for N+2)

Repeat Every Day → N+3, N+4, N+5...

Long-term:
- Backtest strategy
- Track performance
- Optimize parameters
- Automate execution
```

---

## 🎯 Key Takeaways

1. **Scanner = Screening Tool**
   - ให้ Probability ไม่ใช่คำสั่ง

2. **Must Have Strategy**
   - Filter criteria
   - Position sizing
   - Risk management

3. **Daily Process**
   - Update → Analyze → Decide → Execute

4. **Continuous Improvement**
   - Backtest
   - Track
   - Refine

**ระบบนี้เป็น "เครื่องมือ" ไม่ใช่ "คำตอบ"**
**ต้องมี Strategy + Discipline = ได้ผล!** 💪📊
