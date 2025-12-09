# 📊 Strategy Backtesting Guide

## Quick Start

Test your 8-layer filtering strategy on historical data before going live!

---

## 🚀 Basic Usage

### Test First 10 Stocks (Fast - ~2 minutes)
```bash
python backtest_strategy.py
```

### Test Specific Stocks
```bash
python backtest_strategy.py --symbols RELIANCE TCS INFY HDFCBANK
```

### Test All 49 NIFTY 50 Stocks (Complete - ~10 minutes)
```bash
python backtest_strategy.py --all
```

### Test Different Time Periods
```bash
# Last 7 days
python backtest_strategy.py --days 7

# Last 60 days
python backtest_strategy.py --days 60

# Last 3 months
python backtest_strategy.py --days 90
```

---

## 📋 What It Tests

### Your 8-Layer Filtering System:
1. ✅ **Trend Direction** - EMA50 crossover
2. ✅ **RSI Extremes** - Oversold (30) / Overbought (70)
3. ✅ **VWAP Mean Reversion** - Price vs VWAP
4. ✅ **Candle Reversal** - Bullish/Bearish patterns
5. ✅ **Volume Confirmation** - 1.2x average volume
6. ✅ **MACD Momentum** - Trend strength validation
7. ✅ **Trend Strength** - EMA20-EMA50 separation ≥0.5%
8. ✅ **Candle Range** - Minimum 0.15% range

---

## 📊 Output Format

### Console Output:
```
================================================================================
                        STARTING STRATEGY BACKTEST
================================================================================
Symbols: 10
Period: Last 30 days
Strategy: 8-Layer Filtering System
================================================================================

[1/10] Testing RELIANCE...
============================================================
Backtesting RELIANCE
============================================================
Fetching RELIANCE data from 2025-11-09 to 2025-12-09
Fetched 2500 candles for RELIANCE

📊 Results for RELIANCE:
  Data points: 2500
  Total signals: 5
  BUY signals: 3
  SELL signals: 2

  Signal Details:
  [1] BUY Signal
      Time: 2025-11-15 10:45:00
      Price: ₹2450.75
      Strength: 85.0%
      Stop Loss: ₹2425.50
      Target: ₹2500.25
      Reason: EMA50 bullish + RSI oversold (28.5) + VWAP below + Volume 1.3x...

  [2] SELL Signal
      Time: 2025-11-20 14:15:00
      Price: ₹2510.30
      Strength: 78.5%
      Stop Loss: ₹2535.50
      Target: ₹2460.20
      Reason: EMA50 bearish + RSI overbought (72.1) + VWAP above + Volume 1.5x...

[continues for all symbols...]

================================================================================
                            BACKTEST SUMMARY
================================================================================
Symbols Tested: 10
Symbols with Signals: 8
Total Signals Generated: 42
  - BUY Signals: 24
  - SELL Signals: 18
Average Signals per Symbol: 4.20
Test Period: 30 days
================================================================================

✅ Results saved to: backtest_results_20251209_143022.json
```

### JSON Output File:
```json
{
  "timestamp": "20251209_143022",
  "summary": {
    "total_symbols_tested": 10,
    "symbols_with_signals": 8,
    "total_signals": 42,
    "total_buy_signals": 24,
    "total_sell_signals": 18,
    "avg_signals_per_symbol": 4.2,
    "test_period_days": 30
  },
  "results": [
    {
      "symbol": "RELIANCE",
      "total_signals": 5,
      "buy_signals": 3,
      "sell_signals": 2,
      "data_points": 2500,
      "date_range": "2025-11-09 to 2025-12-09",
      "signals_detail": [
        {
          "timestamp": "2025-11-15 10:45:00",
          "type": "BUY",
          "price": 2450.75,
          "strength": 0.85,
          "reason": "EMA50 bullish + RSI oversold..."
        }
      ]
    }
  ]
}
```

---

## 📈 Understanding Results

### Key Metrics:

**Total Signals**
- How many trading opportunities were identified
- More signals = More active strategy
- Fewer signals = More selective/conservative

**BUY vs SELL Ratio**
- Should be roughly balanced in ranging markets
- More BUY in uptrends, more SELL in downtrends

**Signals per Symbol**
- Average: 2-5 signals per 30 days = Good
- < 1 signal = Too strict (consider adjusting filters)
- > 10 signals = Too loose (may generate false signals)

**Signal Strength**
- 60-75% = Moderate confidence
- 75-85% = Good confidence
- > 85% = High confidence (rare, best quality)

---

## 🎯 What to Look For

### Good Signs ✅
- ✅ Multiple signals across different stocks
- ✅ Signal strength consistently > 70%
- ✅ Clear entry/exit reasons logged
- ✅ Balanced BUY/SELL distribution
- ✅ Signals match known market conditions

### Warning Signs ⚠️
- ⚠️ Very few signals (< 1 per symbol in 30 days)
- ⚠️ Too many signals (> 10 per symbol)
- ⚠️ All BUY or all SELL signals
- ⚠️ Low signal strength (< 60%)
- ⚠️ No signals at all for multiple stocks

---

## 🔍 Example Analysis Workflow

### Step 1: Quick Test (First 10 stocks)
```bash
python backtest_strategy.py --days 30
```
**Review:** Are signals being generated? What's the quality?

### Step 2: Analyze Specific Stock
```bash
python backtest_strategy.py --symbols RELIANCE --days 60
```
**Review:** Check signal details, timing, and conditions

### Step 3: Full Test (All 49 stocks)
```bash
python backtest_strategy.py --all --days 30
```
**Review:** Overall strategy performance across market

### Step 4: Different Market Conditions
```bash
# Recent volatile period
python backtest_strategy.py --all --days 7

# Longer trending period
python backtest_strategy.py --all --days 90
```

---

## 📝 Interpreting Results

### Example 1: Good Strategy Performance
```
Symbols Tested: 49
Symbols with Signals: 35
Total Signals: 156
  - BUY: 82
  - SELL: 74
Avg Signals per Symbol: 3.18
```
**Analysis:** 
- ✅ 71% of stocks generated signals (good coverage)
- ✅ ~3 signals per stock in 30 days (reasonable frequency)
- ✅ Balanced BUY/SELL (healthy market participation)

### Example 2: Too Strict
```
Symbols Tested: 49
Symbols with Signals: 8
Total Signals: 12
  - BUY: 7
  - SELL: 5
Avg Signals per Symbol: 0.24
```
**Analysis:**
- ⚠️ Only 16% of stocks generated signals (too selective)
- ⚠️ 0.24 signals per stock (strategy too strict)
- 💡 Consider: Relaxing some filter thresholds

### Example 3: Too Loose
```
Symbols Tested: 49
Symbols with Signals: 48
Total Signals: 850
  - BUY: 420
  - SELL: 430
Avg Signals per Symbol: 17.35
```
**Analysis:**
- ⚠️ 17 signals per stock in 30 days (too many)
- ⚠️ Likely generating false signals
- 💡 Consider: Tightening filter conditions

---

## 🛠️ Advanced Usage

### Test Multiple Time Periods
```bash
# Test different timeframes
python backtest_strategy.py --days 7
python backtest_strategy.py --days 30
python backtest_strategy.py --days 60
python backtest_strategy.py --days 90
```

### Compare Specific Stocks
```bash
# Large caps
python backtest_strategy.py --symbols RELIANCE TCS INFY HDFCBANK --days 30

# Mid caps
python backtest_strategy.py --symbols ADANIPORTS TATAMOTORS SUNPHARMA --days 30

# Bank stocks
python backtest_strategy.py --symbols HDFCBANK ICICIBANK SBIN AXISBANK --days 30
```

### Export and Analyze
```bash
# Run backtest and save results
python backtest_strategy.py --all --days 30

# Results saved to: backtest_results_20251209_143022.json
# Open in Excel/Python for detailed analysis
```

---

## 🎓 Tips for Effective Backtesting

### 1. Start Small
Test with 10 stocks first to verify everything works

### 2. Test Different Market Conditions
- Trending market (last 7 days if market trending)
- Ranging market (stable 30-day period)
- Volatile market (high volume days)

### 3. Review Signal Quality
- Check signal reasons make sense
- Verify entry prices are realistic
- Confirm stop-loss and targets are appropriate

### 4. Compare to Live Data
- Run backtest on recent data
- Compare with live signals you've seen
- Validate strategy logic

### 5. Document Your Findings
- Note which stocks generate best signals
- Identify which filters are most effective
- Adjust thresholds if needed

---

## ⚙️ Adjusting Strategy Based on Results

### If Too Few Signals:
Edit `src/strategies/intraday_strategy.py`:
- Reduce `rsi_oversold` from 30 → 35
- Reduce `rsi_overbought` from 70 → 65
- Reduce `trend_strength_threshold` from 0.005 → 0.003
- Reduce `min_candle_range` from 0.0015 → 0.001

### If Too Many Signals:
- Increase RSI thresholds (make more extreme)
- Increase trend strength requirement
- Add volume multiplier requirement

### If Poor Quality Signals:
- Review signal reasons in detail
- Check which filters are passing
- Consider adding additional confirmation

---

## 📞 Need Help?

### Common Issues:

**"No data available"**
- Check Zerodha access token is valid
- Verify market was open during test period
- Try shorter time period (--days 7)

**"Too many requests"**
- Testing 49 stocks = many API calls
- Use --symbols to test fewer at once
- Rate limiter handles this automatically

**"No signals found"**
- Normal if market was stable/sideways
- Try different time period
- Check strategy filters aren't too strict

---

## 📊 Next Steps After Backtesting

1. ✅ Review backtest results
2. ✅ Adjust strategy if needed
3. ✅ Re-test with new settings
4. ✅ When satisfied, go live with WebSocket dashboard
5. ✅ Monitor live signals vs backtest expectations

---

## 🎯 Remember

**Backtesting shows what WOULD have happened**
- Past performance ≠ future results
- Use as validation tool, not guarantee
- Always start with paper trading
- Monitor live performance carefully

**Your strategy is designed for:**
- Intraday trading (5-minute candles)
- NIFTY 50 liquid stocks
- Trending + mean-reversion opportunities
- Multiple confirmation layers for quality

---

**Happy Backtesting! 🚀**

*Test thoroughly before live trading!*
