# Intraday Trading Bot - Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies

Run the setup script:
```powershell
python setup.py
```

Or manually:
```powershell
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `config.yaml` to customize:
- Trading symbols
- Strategy parameters
- Risk management settings

### 3. Run the Application

**Run the Trading Bot:**
```powershell
python main.py
```

**Run in Paper Trading Mode (default):**
```powershell
python main.py --mode paper --interval 5
```

**Run the Dashboard:**
```powershell
streamlit run dashboard/app.py
```

## 📋 Features

### ✅ Implemented
- ✅ Real-time data fetching (yfinance)
- ✅ Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands, ATR, VWAP)
- ✅ Trading signal generation
- ✅ Risk management (position sizing, stop loss, take profit)
- ✅ Paper trading mode
- ✅ Interactive dashboard
- ✅ Configurable strategies
- ✅ Logging system

### 🔧 To Implement (Optional)
- 🔲 Live trading integration (Alpaca, Interactive Brokers, etc.)
- 🔲 Backtesting engine with historical data
- 🔲 Machine learning-based signals
- 🔲 Email/SMS notifications
- 🔲 Database integration for trade history
- 🔲 Multiple strategy support
- 🔲 Advanced order types (trailing stop, OCO, etc.)

## 📊 Dashboard Features

The Streamlit dashboard provides:
- Real-time price charts
- Technical indicators visualization
- Trading signals display
- Portfolio summary
- Open positions tracking
- Market status

## ⚙️ Configuration

### Strategy Parameters (config.yaml)

```yaml
strategy:
  indicators:
    rsi_period: 14
    rsi_oversold: 30
    rsi_overbought: 70
    macd_fast: 12
    macd_slow: 26
    macd_signal: 9
```

### Risk Management

```yaml
risk:
  max_portfolio_risk: 0.02  # 2% risk per trade
  max_position_size: 0.1    # Max 10% per position
  max_open_positions: 5
  initial_capital: 100000
```

## 🔐 Security

- Never commit `.env` file with real API keys
- Use environment variables for sensitive data
- Always test in paper trading mode first

## 📈 Strategy Logic

The intraday strategy combines:
1. **Momentum**: MACD crossovers, MA crossovers
2. **Mean Reversion**: RSI oversold/overbought, Bollinger Bands
3. **Volume Analysis**: Volume confirmation for signals
4. **Support/Resistance**: VWAP, Bollinger Bands

### Entry Conditions (BUY)
- RSI < 30 (oversold) + positive MACD
- Price below lower Bollinger Band + low RSI
- Bullish MA crossover with volume
- Price above VWAP with momentum

### Exit Conditions
- Profit target reached (default 2%)
- Stop loss hit (default 1%)
- RSI extreme reversal
- MACD bearish crossover while in profit

## 🧪 Testing

Test with paper trading first:
```powershell
python main.py --mode paper
```

Monitor via dashboard:
```powershell
streamlit run dashboard/app.py
```

## 📝 Notes

- The bot runs continuously and checks for signals every 5 minutes (configurable)
- Market hours are respected (US market 9:30 AM - 4:00 PM ET by default)
- All trades are logged in `logs/` directory
- Paper trading tracks simulated P&L

## ⚠️ Disclaimer

This software is for **educational purposes only**. Use at your own risk. Always test thoroughly before using real money. The developers are not responsible for any financial losses.

## 🆘 Troubleshooting

**Import errors**: Run `python setup.py` to install all dependencies

**No data fetched**: Check internet connection and symbol validity

**Dashboard not loading**: Ensure Streamlit is installed: `pip install streamlit`

**API errors**: Verify API keys in `.env` file (if using paid data providers)

## 📚 Further Development

To extend the bot:
1. Add new strategies in `src/strategies/`
2. Add new indicators in `src/indicators/`
3. Integrate broker APIs in `src/trading/`
4. Add backtesting in `src/backtesting/`

Enjoy trading! 📈🚀
