# 📊 Risk Management Parameters โดยประเทศ (V14.3)

## 🇹🇭 **THAI MARKET (SET)**
### Risk Management Parameters
- **ATR SL Multiplier:** `1.2x` (V14.3: เพิ่มจาก 1.0x → 1.2x เพื่อลด SL exits)
- **ATR TP Multiplier:** `2.5x` (V14.3: ลดจาก 3.0x → 2.5x เพื่อเพิ่ม TP exits)
- **Max Hold Days:** `10 days` (V14.3: เพิ่มจาก 7 → 10 ให้มีเวลาไปถึง TP)
- **Trailing Stop Activate:** `2.0%` (V14.3: activate ช้าลง - ให้มีเวลาไปถึง TP)
- **Trailing Stop Distance:** `60%` (V14.3: เพิ่มจาก 50% → 60% ให้กำไร run ได้มากขึ้น)

### Gatekeeper Settings
- **Min Prob:** `48%` (V14.3: ลดจาก 50% เพื่อเพิ่ม Win Rate)
- **Min Stats:** `30` (V14.2: เพิ่มจาก 25)
- **Threshold Multiplier:** `1.1` (V14.0: เพิ่มจาก 1.0)
- **Quality Filter:** `AvgWin > AvgLoss` (V14.1: เพิ่ม quality filter)

### Production Mode (Realistic Trading)
- **Slippage:** `0.10%` per trade (each way)
- **Commission:** `0.32%` round-trip (0.16% x 2)
- **Gap Risk Factor:** `1.20x` (Thai has daily limit ±30%)
- **Min Volume:** `500,000` shares/day

---

## 🇺🇸 **US MARKET (NASDAQ/NYSE)**
### Risk Management Parameters
- **ATR SL Multiplier:** `1.0x`
- **ATR TP Multiplier:** `3.5x` (ปรับจาก 5.0x → 3.5x เพื่อให้ถึง TP ได้มากขึ้น)
- **Max Hold Days:** `5 days` (Revert: ค่าที่เสถียร)
- **Trailing Stop Activate:** `2.0%` (activate ช้าลง - ให้มีเวลาไปถึง TP)
- **Trailing Stop Distance:** `40%` (trail แน่นขึ้น - lock กำไรดีขึ้น)

### Gatekeeper Settings
- **Min Prob:** `52.0%`
- **Min Stats:** `20`
- **Threshold Multiplier:** `0.9`
- **Quality Filter:** `AvgWin >= AvgLoss * 0.9` (US Quality Filter)

### Production Mode (Realistic Trading)
- **Slippage:** `0.05%` per trade (each way)
- **Commission:** `0.02%` round-trip (Near-zero commission era)
- **Gap Risk Factor:** `1.30x` (US can gap significantly on news)
- **Min Volume:** `100,000` shares/day

---

## 🇹🇼 **TAIWAN MARKET (TWSE)**
### Risk Management Parameters
- **ATR SL Multiplier:** `1.0x`
- **ATR TP Multiplier:** `3.5x` (ปรับจาก 6.5x → 3.5x เพื่อให้ถึง TP ได้มากขึ้น)
- **Max Hold Days:** `5 days` (Revert: ค่าที่เสถียร)
- **Trailing Stop Activate:** `2.0%` (activate ช้าลง - ให้มีเวลาไปถึง TP)
- **Trailing Stop Distance:** `40%` (trail แน่นขึ้น - lock กำไรดีขึ้น)

### Gatekeeper Settings
- **Min Prob:** `51.0%`
- **Min Stats:** `25`
- **Threshold Multiplier:** `0.9`
- **Quality Filter:** None

### Production Mode (Realistic Trading)
- **Slippage:** `0.07%` per trade (each way)
- **Commission:** `0.44%` round-trip (Tax + commission)
- **Gap Risk Factor:** `1.25x` (Taiwan moderate gaps)
- **Min Volume:** `200,000` shares/day

---

## 🇨🇳 **CHINA/HK MARKET (HKEX)**
### Risk Management Parameters
- **ATR SL Multiplier:** `1.0x`
- **ATR TP Multiplier:** `3.0x` (V14.1: ลดจาก 4.5x → 3.0x เพื่อให้ถึง TP ได้ง่ายขึ้น)
- **Max Hold Days:** `7 days` (V14.1: คงเดิม)
- **Trailing Stop Activate:** `2.0%` (V14.1: เพิ่มจาก 1.5% → 2.0% activate ช้าลง)
- **Trailing Stop Distance:** `50%` (V14.1: เพิ่มจาก 35% → 50% ให้กำไร run ได้มากขึ้น)

### Gatekeeper Settings
- **Min Prob:** `52.0%` (V14.1: ลดจาก 55% เพื่อเพิ่ม Win Rate)
- **Min Stats:** `35` (V14.0: เพิ่มจาก 30)
- **Threshold Multiplier:** `0.9`
- **Quality Filter:** `AvgWin > AvgLoss` (V14.1: เพิ่ม quality filter)

### Production Mode (Realistic Trading)
- **Slippage:** `0.08%` per trade (each way)
- **Commission:** `0.30%` round-trip (Stamp duty + commission)
- **Gap Risk Factor:** `1.35x` (China/HK can have large gaps)
- **Min Volume:** `200,000` shares/day

---

## 📈 **ATR-Based Risk Management System**

### ข้อดีของ ATR-based SL/TP:
- ✅ **ยืดหยุ่นตาม volatility** - หุ้นผันผวนมาก → SL กว้าง, ผันผวนน้อย → SL แคบ
- ✅ **เอาไปใช้จริงง่าย** - Auto system ไม่ต้องตั้งค่าเอง
- ✅ **Realistic** - ใช้ความผันผวนจริงของหุ้น

### ATR Calculation:
- **Period:** 14 bars
- **Formula:** `ATR = Average(True Range)` where `True Range = max(High-Low, abs(High-PrevClose), abs(Low-PrevClose))`
- **SL/TP Calculation:** 
  - `SL = Entry Price ± (ATR × ATR_SL_Multiplier)`
  - `TP = Entry Price ± (ATR × ATR_TP_Multiplier)`
- **Caps:** 
  - Max SL: `7%` (ป้องกัน SL กว้างเกินไป)
  - Max TP: `15%` (ป้องกัน TP สูงเกินไป)

---

## 🔄 **Trailing Stop System**

### How It Works:
1. **Activation:** เมื่อกำไรถึง `Trail Activate %` (เช่น 2.0%) → trailing stop เริ่มทำงาน
2. **Distance:** Trailing stop จะตามห่างจาก peak profit `Trail Distance %` (เช่น 60% = ถ้า peak profit 10% → trailing stop จะอยู่ที่ 4% จาก entry)
3. **Lock Profit:** เมื่อราคาตกลง → trailing stop จะ lock กำไรไว้

### Example (Thai Market):
- Entry: $100
- Peak Profit: $110 (10% profit)
- Trail Activate: 2.0% ✅ (activated)
- Trail Distance: 60%
- Trailing Stop Level: $100 + (10% × 40%) = $104 (4% profit locked)
- ถ้าราคาตกลงถึง $104 → exit ที่ $104 (lock กำไร 4%)

---

## 📝 **Notes**

### V14.3 Changes (Thai Market):
- ✅ TP 2.5x: ลดจาก 3.0x (เพิ่ม TP exits จาก 0.2%)
- ✅ SL 1.2x: เพิ่มจาก 1.0x (ลด SL exits จาก 30.4%)
- ✅ Trailing 2.0% activate: activate ช้าลง (จาก 1.5%) - ให้มีเวลาไปถึง TP
- ✅ Trailing 60% distance: เพิ่มจาก 50% (ให้กำไร run ได้มากขึ้น)
- ✅ Max Hold 10 days: เพิ่มจาก 7 (ให้มีเวลาไปถึง TP)
- ✅ min_prob 48%: ลดจาก 50% (เพิ่ม Win Rate)

### V14.1 Changes (China/HK Market):
- ✅ TP 3.0x: ลดจาก 4.5x (ให้ถึง TP ได้ง่ายขึ้น, แก้ปัญหา AvgLoss > AvgWin)
- ✅ Trailing 2.0% activate: activate ช้าลง (จาก 1.5%) - ให้มีเวลาไปถึง TP
- ✅ Trailing 50% distance: เพิ่มจาก 35% (ให้กำไร run ได้มากขึ้น)
- ✅ min_prob 52%: ลดจาก 55% (เพิ่ม Win Rate, แก้ปัญหา overfitting)

---

**Last Updated:** 2026-01-XX (V14.3)

