# Performance Optimization Guide

## ⚡ ปัญหา: หุ้นเยอะ ดึงข้อมูลช้า

### ขนาดของงาน:
- **SET (ไทย):** ~700 หุ้น
- **NASDAQ:** ~3,000 หุ้น
- **ไม่ optimize:** 700 หุ้น × 3 วินาที = **35+ นาที!** ❌

---

## ✅ Solutions

### 1. **Data Caching** (เร็วขึ้น 30x)

```python
from data_cache import OptimizedDataFetcher

# สร้าง fetcher with cache
fetcher = OptimizedDataFetcher(
    use_cache=True,
    cache_max_age_hours=24  # cache อายุ 24 ชม.
)

# ครั้งแรก: ช้า (~3 วินาที)
df = fetcher.fetch_daily_data('PTT', 'SET')

# ครั้งต่อไป: เร็วมาก (~0.1 วินาที) ✅
df = fetcher.fetch_daily_data('PTT', 'SET')  # ใช้ cache
```

**ผลลัพธ์:**
- ✅ เร็วขึ้น **30x** เมื่อใช้ cache
- ✅ ลด API calls
- ✅ ดึงเฉพาะข้อมูลใหม่

---

### 2. **Batch Processing**

```python
from batch_processor import BatchStockProcessor

# สร้าง processor
processor = BatchStockProcessor(
    use_cache=True,
    rate_limit_seconds=0.5  # หน่วงเวลา 0.5 วินาที/หุ้น
)

# รายการหุ้นที่ต้องการวิเคราะห์
stocks = [
    {'symbol': 'PTT', 'exchange': 'SET'},
    {'symbol': 'CPALL', 'exchange': 'SET'},
    # ... อีก 698 ตัว
]

# ประมวลผลทั้งหมด
results = processor.process_batch(stocks, threshold=1.0, n_bars=1250)
```

**Features:**
- ✅ Progress tracking
- ✅ Rate limiting (ไม่โดน ban)
- ✅ Error handling
- ✅ Auto save results

---

### 3. **Selective Scanning** (เร็วที่สุด)

```python
# แทนที่จะวิเคราะห์ทั้ง 700 ตัว
# ให้กรองเฉพาะที่วันนี้เคลื่อนไหว ±1%

from data_cache import OptimizedDataFetcher

fetcher = OptimizedDataFetcher(use_cache=True)

# 1. Quick scan (ใช้ cache)
candidates = []
for stock in all_stocks:
    df = fetcher.fetch_daily_data(stock['symbol'], stock['exchange'], n_bars=2)
    latest_change = df.iloc[-1]['pct_change']
    
    if abs(latest_change) >= 1.0:
        candidates.append(stock)

print(f"พบหุ้นที่เคลื่อนไหว ±1%: {len(candidates)} ตัว")

# 2. วิเคราะห์เฉพาะ candidates
processor.process_batch(candidates)  # ลดจาก 700 → ~70 ตัว!
```

---

## 📊 Optimization Strategies

### Strategy 1: **Daily Update** (แนะนำ)

```
วันแรก (ช้า):
├── ดึงข้อมูลทั้งหมด 700 ตัว × 1,000 bars
├── ใช้เวลา: ~30-60 นาที
└── บันทึก cache

วันถัดไป (เร็วมาก):
├── ใช้ cache (อายุ < 24 ชม.)
├── แค่ดึงข้อมูลใหม่ (1-2 bars)
├── ใช้เวลา: ~3-5 นาที ✅
└── อัพเดท cache
```

### Strategy 2: **Selective + Cache** (เร็วที่สุด)

```python
# Step 1: Quick scan (ดูเฉพาะวันล่าสุด)
candidates = quick_scan_for_threshold(all_stocks, threshold=1.0)
# ผลลัพธ์: ~50-100 ตัว (จาก 700)

# Step 2: Full analysis (deep dive เฉพาะ candidates)
results = processor.process_batch(candidates, n_bars=1250)
```

**เวลา:**
- Quick scan: ~2-3 นาที
- Deep analysis: ~5 นาที
- **รวม: ~7-8 นาที** ✅

---

## ⏱️ Performance Comparison

| วิธี | หุ้น | เวลา | หมายเหตุ |
|------|------|------|----------|
| **ไม่ optimize** | 700 | ~35 นาที | ดึงใหม่ทุกครั้ง ❌ |
| **Cache (วันแรก)** | 700 | ~35 นาที | ดึงครั้งเดียว |
| **Cache (วันถัดไป)** | 700 | ~5 นาที | ใช้ cache ✅ |
| **Selective + Cache** | 100 | ~5-7 นาที | กรองก่อน ✅✅ |
| **Selective only new** | 10-20 | ~1-2 นาที | เฉพาะที่เคลื่อนไหววันนี้ ✅✅✅ |

---

## 🚀 Production Workflow

```python
"""
รันทุกวันเช้า 8:00 AM (Daily Suggest)
"""

# 1. Quick scan หุ้นทั้งหมด (ใช้ cache)
candidates = []
for stock in get_all_stocks():
    df = fetcher.fetch_daily_data(stock, n_bars=5, use_cache=True)
    
    if abs(df.iloc[-1]['pct_change']) >= 1.0:
        candidates.append(stock)

print(f"📊 พบหุ้นที่เคลื่อนไหว ±1%: {len(candidates)} ตัว")

# 2. วิเคราะห์เฉพาะ candidates
processor = BatchStockProcessor(use_cache=True)
results = processor.process_batch(candidates, n_bars=1250)

# 3. ส่ง notifications
for r in results:
    if r['prediction'] and r['prediction']['confidence'] > 60:
        send_notification(r)
```

**เวลารวม:** ~10 นาที สำหรับ 700 หุ้น ✅

---

## 💾 Storage Requirements

### Cache Size:
```
หุ้น 1 ตัว (1,250 bars) = ~200 KB
700 หุ้น = ~140 MB
```
ไม่มีปัญหา! 💪

---

## 🔧 Cache Management

```python
from data_cache import DataCacheManager

cache = DataCacheManager()

# ดู cache info
cache.get_cache_info()

# ลบ cache เก่า
cache.clear_cache()

# บังคับ refresh ข้อมูล
fetcher.fetch_daily_data('PTT', 'SET', force_refresh=True)
```

---

## ✅ สรุป

**ก่อน Optimize:**
- 700 หุ้น = 35 นาที ❌

**หลัง Optimize:**
- วันแรก: 35 นาที (ครั้งเดียว)
- วันถัดไป: **5-10 นาที** ✅
- เฉพาะที่เคลื่อนไหว: **1-2 นาที** ✅✅

**Practical สำหรับ Daily Suggest! 🎉**
