# 📋 คำสั่ง Backtest แต่ละประเทศ (ค่าเดิม)

## 🇺🇸 US STOCK
```bash
python scripts/backtest.py --full --group US --atr_tp_mult 5.0 --trail_activate 1.5 --max_hold 5 --fast
```

**ค่าเดิม:**
- TP: 5.0x ATR
- Trailing: 1.5%
- Max Hold: 5 days

---

## 🇨🇳 CHINA/HK STOCK
```bash
python scripts/backtest.py --full --group CHINA --atr_tp_mult 5.0 --trail_activate 1.0 --max_hold 3 --fast
```

**ค่าเดิม:**
- TP: 5.0x ATR
- Trailing: 1.0%
- Max Hold: 3 days

---

## 🇹🇼 TAIWAN STOCK
```bash
python scripts/backtest.py --full --group TAIWAN --atr_tp_mult 6.5 --trail_activate 1.0 --max_hold 10 --fast
```

**ค่าเดิม:**
- TP: 6.5x ATR
- Trailing: 1.0%
- Max Hold: 10 days

---

## 🇹🇭 THAI STOCK
```bash
python scripts/backtest.py --full --group THAI --atr_tp_mult 3.5 --trail_activate 1.5 --max_hold 5 --fast
```

**ค่าเดิม:**
- TP: 3.5x ATR
- Trailing: 1.5%
- Max Hold: 5 days

---

## 📊 สรุป

| Market | TP | Trailing | Max Hold | คำสั่ง |
|--------|----|----------|----------|--------|
| **US** | 5.0x | 1.5% | 5 days | `--group US --atr_tp_mult 5.0 --trail_activate 1.5 --max_hold 5` |
| **CHINA** | 5.0x | 1.0% | 3 days | `--group CHINA --atr_tp_mult 5.0 --trail_activate 1.0 --max_hold 3` |
| **TAIWAN** | 6.5x | 1.0% | 10 days | `--group TAIWAN --atr_tp_mult 6.5 --trail_activate 1.0 --max_hold 10` |
| **THAI** | 3.5x | 1.5% | 5 days | `--group THAI --atr_tp_mult 3.5 --trail_activate 1.5 --max_hold 5` |

---

## 🧹 ลบ Cache

```bash
python scripts/clear_cache.py
```

---

## 📈 ตรวจสอบผลลัพธ์

```bash
python scripts/compare_before_after_tp_adjustment.py
```


