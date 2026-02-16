# Taiwan V12.2 - RRR Optimization

## 🎯 Goal: เพิ่ม RRR ก่อน แล้วค่อยเพิ่ม Count

### V12.2 Changes

| Parameter | V12.1 | V12.2 | Change | Expected Impact |
|-----------|-------|-------|--------|-----------------|
| **Stop Loss** | 1.2% | **1.0%** | ⬇️ -0.2% | Tighter SL → Better RRR |
| **Take Profit** | 5.0% | **6.5%** | ⬆️ +1.5% | Wider TP → Higher RRR |
| **Max Hold** | 7 วัน | **10 วัน** | ⬆️ +3 วัน | More time to reach TP |
| **Trail Distance** | 40% | **30%** | ⬇️ -10% | Let profits run more |
| **Prob Filter** | 53% | **52%** | ⬇️ -1% | Include more high-RRR stocks |

### Theoretical RRR Calculation

**V12.1:** TP 5.0% / SL 1.2% = **RRR 4.17**  
**V12.2:** TP 6.5% / SL 1.0% = **RRR 6.5**

### Expected Results

1. **RRR ดีขึ้น:**
   - Theoretical: 4.17 → 6.5 (+2.33)
   - Actual: ควรได้ RRR > 2.0 (ดีกว่า V12.1 ที่ได้ 1.45-1.51)

2. **หุ้นที่มี RRR ดีขึ้น:**
   - 2308: RRR 1.51 → ควรได้ > 2.0
   - 2454: RRR 1.45 → ควรได้ > 2.0

3. **Count อาจลดลงชั่วคราว:**
   - แต่จะปรับเพิ่มใน V12.3 หลังจาก RRR ดีแล้ว

---

## 📊 Comparison Table

| Version | SL | TP | Theoretical RRR | Actual RRR (Best) | Stocks Passing |
|---------|----|----|------------------|-------------------|----------------|
| V12.0 | 1.5% | 4.0% | 2.67 | 1.36 | 4 |
| V12.1 | 1.2% | 5.0% | 4.17 | 1.51 | 1 |
| **V12.2** | **1.0%** | **6.5%** | **6.5** | **> 2.0 (expected)** | **TBD** |

---

## 🔄 Next Steps

1. **Test V12.2** - Run backtest with new parameters
2. **Verify RRR** - Check if actual RRR > 2.0
3. **V12.3** - If RRR good, then optimize Count (threshold, min_stats)

---

**Last Updated:** 2026-02-13  
**Status:** Ready for Testing

