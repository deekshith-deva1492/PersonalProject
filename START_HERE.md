# 🎯 START HERE - Complete Guide

## ✅ What You Have

A **complete intraday trading bot** with:
- Real-time data fetching
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Trading strategy with buy/sell signals
- Risk management & position sizing
- Interactive dashboard
- Paper trading mode

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

Open PowerShell and run:

```powershell
pip install pandas numpy yfinance pyyaml python-dotenv streamlit plotly pytz schedule matplotlib requests
```

If you get timeout errors, install one at a time:
```powershell
pip install pandas
pip install numpy
pip install yfinance
pip install streamlit
pip install plotly
pip install pyyaml python-dotenv pytz schedule matplotlib requests
```

### Step 2: Test Everything Works

```powershell
cd e:\TradingBot
python test_functionality.py
```

This will test all components and show you if everything is working.

### Step 3: Run the Bot

**Option A: Run the trading bot**
```powershell
python main.py
```

**Option B: Open the dashboard (recommended to start)**
```powershell
streamlit run dashboard/app.py
```

The dashboard will open in your browser at http://localhost:8501

## 📊 What Each Component Does

### 1. Trading Bot (`main.py`)
- Runs continuously
- Checks market every 5 minutes
- Generates trading signals
- Executes trades (paper mode)
- Logs everything

**Run with:**
```powershell
python main.py --mode paper --interval 5
```

### 2. Dashboard (`dashboard/app.py`)
- Visual interface
- Real-time charts
- Shows signals
- Displays portfolio
- Monitor positions

**Run with:**
```powershell
streamlit run dashboard/app.py
```

### 3. Configuration (`config.yaml`)
- Customize symbols (AAPL, MSFT, etc.)
- Adjust strategy parameters
- Set risk limits
- Configure market hours

## 📁 Key Files

| File | What It Does |
|------|--------------|
| `main.py` | Main trading bot - runs automatically |
| `dashboard/app.py` | Visual dashboard - see everything |
| `config.yaml` | Settings - change symbols, risk limits |
| `test_functionality.py` | Test script - verify it works |
| `requirements.txt` | Dependencies list |
| `PROJECT_SUMMARY.md` | Complete project overview |

## ⚙️ Configuration Quick Guide

Edit `config.yaml` to change:

```yaml
# What stocks to trade
trading:
  symbols:
    - "AAPL"
    - "MSFT"
    - "GOOGL"

# How much risk per trade
risk:
  max_portfolio_risk: 0.02    # 2% per trade
  max_position_size: 0.1      # 10% per position
  initial_capital: 100000     # Starting money

# When to exit
strategy:
  exit:
    profit_target: 0.02       # Sell at 2% profit
    stop_loss: 0.01           # Sell at 1% loss
```

## 🎯 Typical Workflow

### For Beginners:

1. **Start with Dashboard** (visual)
   ```powershell
   streamlit run dashboard/app.py
   ```
   - Select a symbol (AAPL, MSFT, etc.)
   - Watch the charts
   - See when signals appear
   - Understand the indicators

2. **Run the Bot** (automated)
   ```powershell
   python main.py
   ```
   - Let it run
   - Check logs in `logs/` folder
   - See trades being made

### For Advanced Users:

1. Edit `config.yaml` to customize
2. Run `python test_functionality.py` to verify
3. Start bot: `python main.py`
4. Monitor: `streamlit run dashboard/app.py`

## 📈 Understanding the Strategy

### When Does It Buy?

The bot looks for 2 or more of these conditions:
- RSI below 30 (stock oversold)
- Price below lower Bollinger Band
- MACD showing upward momentum
- Price above VWAP with volume

### When Does It Sell?

- Profit target hit (2% gain)
- Stop loss hit (1% loss)
- RSI above 70 (overbought)
- MACD turning negative

## 🔒 Safety First

✅ **Paper Trading**: Bot starts in paper (simulated) mode
✅ **Position Limits**: Maximum 5 positions at once
✅ **Risk Limits**: Only risk 2% per trade
✅ **Stop Loss**: Every position has automatic stop loss
✅ **Daily Limit**: Stops if loses 5% in one day

## 💡 Pro Tips

1. **Start Simple**
   - Run dashboard first to see how it works
   - Watch for a few days before changing settings

2. **Test During Market Hours**
   - Bot works best when US market is open (9:30 AM - 4:00 PM ET)
   - Outside hours, you'll see "Market Closed"

3. **Check Logs**
   - All activity logged in `logs/` folder
   - Review to understand bot behavior

4. **Customize Gradually**
   - Start with default settings
   - Change one thing at a time in `config.yaml`
   - Test after each change

## 🐛 Common Issues & Solutions

### "Module not found" Error
**Solution:** Install the missing package
```powershell
pip install <package-name>
```

### "No data available"
**Solution:** 
- Check internet connection
- Verify symbol is correct (AAPL, not Apple)
- Market might be closed

### Dashboard Won't Start
**Solution:**
```powershell
pip install streamlit
streamlit run dashboard/app.py
```

### Bot Not Making Trades
**Solution:**
- This is normal! Not every period has good setups
- Try different symbols
- Check logs to see what it's evaluating

## 📚 Learn More

- **PROJECT_SUMMARY.md**: Complete project details
- **QUICKSTART.md**: Detailed quick start guide
- **INSTALLATION.md**: Installation troubleshooting
- **README.md**: Full documentation

## 🎓 Next Steps

### Today:
1. ✅ Install dependencies
2. ✅ Run test: `python test_functionality.py`
3. ✅ Open dashboard: `streamlit run dashboard/app.py`
4. ✅ Explore charts and indicators

### This Week:
1. Run bot during market hours
2. Observe signal generation
3. Review logs
4. Understand the strategy

### Later:
1. Customize `config.yaml`
2. Try different symbols
3. Tune parameters
4. Consider adding more features

## ⚠️ IMPORTANT REMINDERS

🔴 **This is PAPER TRADING only**
- No real money at risk
- All trades are simulated
- Perfect for learning

🟡 **Educational Purpose**
- Learn about trading algorithms
- Understand technical indicators
- Practice strategy development

🟢 **Before Live Trading**
- Test for weeks/months
- Understand every parameter
- Know the risks
- Never risk money you can't lose

## 🆘 Need Help?

1. Read error messages carefully
2. Check logs in `logs/` directory
3. Review relevant .md files
4. Run test script: `python test_functionality.py`

## 🎉 You're Ready!

Everything is set up and ready to go. Just:

1. **Install packages** (Step 1 above)
2. **Run dashboard**: `streamlit run dashboard/app.py`
3. **Watch it work!**

**Happy Trading! 📈🚀**

---

*Remember: This is for educational purposes. Always practice with paper trading before considering real money.*
