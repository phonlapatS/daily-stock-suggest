# 🚀 Quick Start Guide - PredictPlus1

**Version:** V14.3  
**Last Updated:** 2026-01-XX

---

## ⚡ Quick Start (5 นาที)

### 1. Daily Trading (Normal Use)

```bash
# 1. รันระบบหลัก (หลังตลาดปิด)
python main.py

# 2. ตรวจสอบ Forward Testing
python scripts/check_forward_testing.py --verify
```

**เมื่อไหร่ใช้:**
- 🇹🇭 **THAI:** 17:00-18:00 ICT (หลัง SET ปิด)
- 🇺🇸 **US:** 05:00-06:00 ICT (หลัง NASDAQ/NYSE ปิด)
- 🇹🇼 **TAIWAN:** 13:00-14:00 ICT (หลัง TWSE ปิด)
- 🇨🇳 **CHINA/HK:** 15:30-16:30 ICT (หลัง HKEX ปิด)

---

### 2. Backtest & Analysis (Testing/Research)

```bash
# 1. รัน Backtest (เลือกตลาด)
python scripts/run_single_backtest.py

# 2. คำนวณ Metrics
python scripts/calculate_metrics.py

# 3. สร้าง Equity Curves
python scripts/plot_equity_curves.py
```

---

## 📋 คำสั่งที่ใช้บ่อย

### Main System
```bash
python main.py                                    # รันระบบหลัก
python scripts/check_forward_testing.py          # ตรวจสอบ Forward Testing
```

### Backtest
```bash
python scripts/backtest.py --full --bars 2500 --group THAI    # Backtest เฉพาะตลาด
python scripts/run_single_backtest.py                         # Backtest แบบ Interactive
```

### Metrics & Reports
```bash
python scripts/calculate_metrics.py              # คำนวณ Metrics
python scripts/plot_equity_curves.py             # สร้าง Equity Curves
```

### Utilities
```bash
python scripts/clear_cache.py                     # Clear Cache
python scripts/market_sentiment.py               # ดู Market Sentiment
```

---

## 📊 Risk Management Parameters (สรุป)

| Market | ATR TP | ATR SL | Max Hold | Trail Activate | Trail Distance |
|--------|--------|--------|----------|----------------|----------------|
| 🇹🇭 **THAI** | 2.5x | 1.2x | 10 days | 2.0% | 60% |
| 🇺🇸 **US** | 3.5x | 1.0x | 5 days | 2.0% | 40% |
| 🇹🇼 **TAIWAN** | 3.5x | 1.0x | 5 days | 2.0% | 40% |
| 🇨🇳 **CHINA/HK** | 3.0x | 1.0x | 7 days | 2.0% | 50% |

**ดูรายละเอียดเพิ่มเติม:** [RISK_MANAGEMENT_SUMMARY.md](RISK_MANAGEMENT_SUMMARY.md)

---

## 🔍 Filter Criteria (Display)

| Market | Prob% | RRR | Count |
|--------|-------|-----|-------|
| 🇹🇭 **THAI** | > 60% | > 2.0 | >= 5 |
| 🇺🇸 **US** | >= 60% | >= 1.5 | >= 15 |
| 🇹🇼 **TAIWAN** | >= 50% | >= 1.0 | >= 15 |
| 🇨🇳 **CHINA/HK** | > 60% | > 2.0 | >= 5 |

---

## 📚 เอกสารเพิ่มเติม

- **[COMPLETE_SYSTEM_MANUAL.md](COMPLETE_SYSTEM_MANUAL.md)** - ⭐ คู่มือระบบฉบับสมบูรณ์
- **[RISK_MANAGEMENT_SUMMARY.md](RISK_MANAGEMENT_SUMMARY.md)** - Risk Management Parameters
- **[BACKTEST_COMMANDS.md](BACKTEST_COMMANDS.md)** - Backtest Commands

---

**Last Updated:** 2026-01-XX (V14.3)

