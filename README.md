# Intraday Trading Bot

A Python-based intraday trading application with real-time data analysis, technical indicators, and automated trading signals.

## Features

- **Real-time Market Data**: Fetch live stock/crypto prices
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands
- **Trading Signals**: Automated buy/sell signal generation
- **Risk Management**: Stop-loss, position sizing, risk-reward ratios
- **Backtesting**: Test strategies on historical data
- **Dashboard**: Real-time monitoring and visualization
- **Paper Trading**: Test strategies without real money

## Project Structure

```
TradingBot/
├── src/
│   ├── data/
│   │   ├── data_fetcher.py      # Fetch market data
│   │   └── data_processor.py    # Process and clean data
│   ├── indicators/
│   │   └── technical_indicators.py  # Calculate technical indicators
│   ├── strategies/
│   │   ├── base_strategy.py     # Base strategy class
│   │   └── intraday_strategy.py # Intraday trading strategies
│   ├── trading/
│   │   ├── order_manager.py     # Manage orders
│   │   └── position_manager.py  # Track positions
│   ├── risk/
│   │   └── risk_manager.py      # Risk management
│   ├── backtesting/
│   │   └── backtest_engine.py   # Backtesting engine
│   └── utils/
│       ├── config.py             # Configuration
│       └── logger.py             # Logging utilities
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── tests/
├── data/                         # Store historical data
├── logs/                         # Application logs
├── config.yaml                   # Configuration file
├── requirements.txt              # Python dependencies
└── main.py                       # Main application entry point
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config.yaml`

## Usage

### Run the Trading Bot
```bash
python main.py
```

### Run the Dashboard
```bash
streamlit run dashboard/app.py
```

### Backtest a Strategy
```bash
python main.py --backtest --symbol AAPL --days 30
```

## Configuration

Edit `config.yaml` to customize:
- Trading symbols
- Strategy parameters
- Risk management settings
- API credentials

## Disclaimer

This software is for educational purposes only. Use at your own risk. Always test strategies thoroughly before using real money.

## License

MIT License
