# Backtesting Quick Reference

## One-Line Commands

```bash
# Basic test (10 stocks, 30 days)
python backtest_strategy.py

# All NIFTY 50 stocks
python backtest_strategy.py --all

# Specific stocks
python backtest_strategy.py --symbols RELIANCE TCS INFY

# Different time periods
python backtest_strategy.py --days 7    # Last week
python backtest_strategy.py --days 60   # 2 months

# Combined
python backtest_strategy.py --all --days 60
```

## What Gets Tested

✅ All 8 filters in your strategy
✅ Real historical NIFTY 50 data from Zerodha
✅ Signal quality, timing, and reasons
✅ Entry/exit prices, stop-loss, targets

## Output Files

- **Console**: Real-time progress + summary
- **JSON**: `backtest_results_YYYYMMDD_HHMMSS.json`

## Good Results

- 2-5 signals per stock (30 days)
- Signal strength > 70%
- Balanced BUY/SELL
- Clear reasons

## Next Steps

1. Run basic test
2. Review results
3. Test all stocks
4. Adjust if needed
5. Go live with dashboard

## Full Guide

See `BACKTESTING_GUIDE.md` for complete documentation.
