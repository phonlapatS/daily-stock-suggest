# คำสั่งรัน Backtest แต่ละประเทศ

> **สำหรับ:** V4.1 Production-Ready System  
> **Last Updated:** 2026-02-XX

---

## 📋 คำสั่งพื้นฐาน

### โครงสร้างคำสั่ง
```bash
python scripts/backtest.py --full --bars <จำนวน bars> --group <ประเทศ>
```

### Parameters สำคัญ
- `--full`: รัน full scan (ทุกหุ้นในกลุ่ม)
- `--bars`: จำนวน bars ที่ใช้ทดสอบ (default: 200, แนะนำ: 5000)
- `--group`: ระบุประเทศ (THAI, US, CHINA, TAIWAN, METALS)
- `--production`: เปิด Production Mode (Slippage, Commission, Gap Risk)
- `--fast`: Fast mode (ลด delay ระหว่าง requests)

---

## 🇹🇭 หุ้นไทย (THAI)

### คำสั่งพื้นฐาน
```bash
python scripts/backtest.py --full --bars 5000 --group THAI
```

### คำสั่งพร้อม Production Mode
```bash
python scripts/backtest.py --full --bars 5000 --group THAI --production
```

### คำสั่ง Fast Mode
```bash
python scripts/backtest.py --full --bars 5000 --group THAI --fast
```

### ข้อมูล
- **Group Name:** `GROUP_A_THAI`
- **Engine:** MEAN_REVERSION
- **Threshold:** Dynamic (Multiplier 1.0, Floor 0.7%)
- **Gatekeeper:** Prob >= 53%, Expectancy > 0
- **Risk Management:** SL 1.5%, TP 3.5%, Trailing Stop ON
- **Output:** `logs/trade_history_THAI.csv`

---

## 🇺🇸 หุ้นอเมริกา (US)

### คำสั่งพื้นฐาน
```bash
python scripts/backtest.py --full --bars 5000 --group US
```

### คำสั่งพร้อม Production Mode
```bash
python scripts/backtest.py --full --bars 5000 --group US --production
```

### คำสั่ง Fast Mode
```bash
python scripts/backtest.py --full --bars 5000 --group US --fast
```

### ข้อมูล
- **Group Name:** `GROUP_B_US`
- **Engine:** TREND_MOMENTUM
- **Threshold:** Dynamic (Multiplier 0.9, Floor 0.6%)
- **Gatekeeper:** Prob >= 52%, Expectancy > 0
- **Risk Management:** SL 1.5%, TP 5.0%, Trailing Stop ON
- **Output:** `logs/trade_history_US.csv`

---

## 🇨🇳 หุ้นจีน/ฮ่องกง (CHINA/HK)

### คำสั่งพื้นฐาน
```bash
python scripts/backtest.py --full --bars 5000 --group CHINA
```

หรือ

```bash
python scripts/backtest.py --full --bars 5000 --group HK
```

### คำสั่งพร้อม Production Mode
```bash
python scripts/backtest.py --full --bars 5000 --group CHINA --production
```

### คำสั่ง Fast Mode
```bash
python scripts/backtest.py --full --bars 5000 --group CHINA --fast
```

### ข้อมูล
- **Group Name:** `GROUP_C_CHINA_HK`
- **Engine:** MEAN_REVERSION
- **Threshold:** Dynamic (Multiplier 0.9, Floor 0.5%)
- **Gatekeeper:** Prob >= 53%, Expectancy > 0
- **Risk Management:** SL 1.5%, TP 3.5%, Trailing Stop ON
- **Output:** `logs/trade_history_CHINA.csv`

---

## 🇹🇼 หุ้นไต้หวัน (TAIWAN)

### คำสั่งพื้นฐาน
```bash
python scripts/backtest.py --full --bars 5000 --group TAIWAN
```

### คำสั่งพร้อม Production Mode
```bash
python scripts/backtest.py --full --bars 5000 --group TAIWAN --production
```

### คำสั่ง Fast Mode
```bash
python scripts/backtest.py --full --bars 5000 --group TAIWAN --fast
```

### ข้อมูล
- **Group Name:** `GROUP_D_TAIWAN`
- **Engine:** TREND_MOMENTUM (Regime-Aware)
- **Threshold:** Dynamic (Multiplier 0.9, Floor 0.5%)
- **Gatekeeper:** Prob >= 53%, Expectancy > 0
- **Risk Management:** SL 1.5%, TP 3.5%, Trailing Stop ON
- **Output:** `logs/trade_history_TAIWAN.csv`

---

## ⚡ โลหะมีค่า (METALS)

### Gold 30min
```bash
python scripts/backtest.py --full --bars 5000 --group GOLD
```

### Silver 30min
```bash
python scripts/backtest.py --full --bars 5000 --group SILVER
```

### ข้อมูล
- **Group Names:** 
  - `GROUP_C1_GOLD_30M` (Gold 30min)
  - `GROUP_C2_GOLD_15M` (Gold 15min)
  - `GROUP_D1_SILVER_30M` (Silver 30min)
  - `GROUP_D2_SILVER_15M` (Silver 15min)
- **Engine:** MEAN_REVERSION
- **Threshold:** Fixed (Gold: 0.10%, Silver: 0.15-0.20%)
- **Output:** `logs/trade_history_METALS.csv`

---

## 🔧 คำสั่งเพิ่มเติม

### รันทุกประเทศ (Full Scan)
```bash
python scripts/backtest.py --full --bars 5000
```

### รัน Sample (ไม่ใช่ Full)
```bash
python scripts/backtest.py --all --bars 5000 --group THAI
```

### Quick Test (4 หุ้นหลัก)
```bash
python scripts/backtest.py --quick --bars 200
```

### Custom Parameters
```bash
python scripts/backtest.py --full --bars 5000 --group THAI \
  --stop_loss 2.0 \
  --take_profit 4.0 \
  --max_hold 5 \
  --min_prob 55
```

---

## 📊 Output Files

หลังรัน backtest จะได้ไฟล์:
- `logs/trade_history_THAI.csv` - หุ้นไทย
- `logs/trade_history_US.csv` - หุ้นอเมริกา
- `logs/trade_history_CHINA.csv` - หุ้นจีน/ฮ่องกง
- `logs/trade_history_TAIWAN.csv` - หุ้นไต้หวัน
- `logs/trade_history_METALS.csv` - โลหะมีค่า

---

## 💡 Tips

1. **ใช้ --bars 5000** สำหรับผลลัพธ์ที่แม่นยำ (ใช้ข้อมูล 5000 bars)
2. **ใช้ --production** ถ้าต้องการผลลัพธ์ที่สะท้อนความเป็นจริง (Slippage, Commission)
3. **ใช้ --fast** ถ้าต้องการรันเร็วขึ้น (แต่อาจเสี่ยง rate limiting)
4. **รันทีละประเทศ** เพื่อให้เห็นผลลัพธ์ชัดเจนขึ้น

---

## ⏱️ เวลาโดยประมาณ

- **THAI (118 หุ้น):** ~30-60 นาที
- **US (98 หุ้น):** ~25-50 นาที
- **CHINA/HK (10 หุ้น):** ~5-10 นาที
- **TAIWAN (10 หุ้น):** ~5-10 นาที
- **METALS (4 assets):** ~2-5 นาที

*หมายเหตุ: เวลาขึ้นอยู่กับความเร็วอินเทอร์เน็ตและ API rate limits*

---

**Last Updated:** 2026-02-XX  
**Version:** 4.1


