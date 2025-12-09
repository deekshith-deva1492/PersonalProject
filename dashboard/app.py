"""
Trading Dashboard
Streamlit dashboard for monitoring the trading bot
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from src.data.data_fetcher import DataFetcher
from src.data.data_processor import DataProcessor
from src.indicators.technical_indicators import TechnicalIndicators
from src.strategies.intraday_strategy import IntradayStrategy
from src.risk.risk_manager import RiskManager
from src.utils.config import config

# Page configuration
st.set_page_config(
    page_title="Intraday Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize trading components with Zerodha"""
    data_fetcher = DataFetcher(provider="zerodha")  # Use Zerodha API
    data_processor = DataProcessor()
    indicators = TechnicalIndicators()
    strategy = IntradayStrategy()
    risk_manager = RiskManager()
    
    return data_fetcher, data_processor, indicators, strategy, risk_manager

data_fetcher, data_processor, indicators, strategy, risk_manager = initialize_components()

# Sidebar
st.sidebar.title("⚙️ Settings")

# Symbol selection
trading_config = config.get_trading_config()
symbols = trading_config.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
selected_symbol = st.sidebar.selectbox("Select Symbol", symbols)

# Timeframe selection
data_config = config.get_data_config()
interval = st.sidebar.selectbox(
    "Interval",
    ["minute", "3minute", "5minute", "15minute", "30minute", "60minute"],
    index=2  # Default to 5minute
)

days = st.sidebar.slider("Days to Load", 1, 30, 5)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Market status
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Market Status")
market_open = data_fetcher.is_market_open()
status_color = "🟢" if market_open else "🔴"
status_text = "OPEN" if market_open else "CLOSED"
st.sidebar.markdown(f"{status_color} **{status_text}**")

# Main content
st.title("📈 Intraday Trading Dashboard")
st.markdown(f"**Symbol:** {selected_symbol} | **Interval:** {interval} | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Fetch data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_data(symbol, interval, days):
    """Fetch and process data"""
    df = data_fetcher.get_historical_data(symbol, interval, days)
    if not df.empty:
        # Ensure datetime is a column (Zerodha returns it as index)
        if 'datetime' not in df.columns and df.index.name is not None:
            df.reset_index(inplace=True)
            if df.columns[0] != 'datetime':
                df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
        
        df = data_processor.clean_data(df)
        df = indicators.calculate_all_indicators(df)
    return df

df = get_data(selected_symbol, interval, days)

if df.empty:
    st.error(f"No data available for {selected_symbol}")
    st.stop()

# Get current quote
quote = data_fetcher.get_real_time_quote(selected_symbol)

# Metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    current_price = quote.get('price', df.iloc[-1]['close'])
    st.metric("Current Price", f"₹{current_price:.2f}")

with col2:
    change = quote.get('change', 0)
    change_pct = quote.get('change_percent', 0)
    st.metric("Change", f"₹{change:.2f}", f"{change_pct:.2f}%")

with col3:
    volume = quote.get('volume', df.iloc[-1]['volume'])
    st.metric("Volume", f"{volume:,.0f}")

with col4:
    rsi = df.iloc[-1]['rsi']
    rsi_color = "🔴" if rsi > 70 else "🟢" if rsi < 30 else "⚪"
    st.metric("RSI", f"{rsi:.2f} {rsi_color}")

with col5:
    macd = df.iloc[-1]['macd']
    macd_signal = df.iloc[-1]['macd_signal']
    macd_trend = "📈" if macd > macd_signal else "📉"
    st.metric("MACD", f"{macd:.4f} {macd_trend}")

# Generate signals
signals = strategy.generate_signals(df, selected_symbol)

# Signals section
st.markdown("---")
col_signal, col_strength = st.columns(2)

with col_signal:
    st.subheader("🎯 Trading Signals")
    if signals:
        latest_signal = signals[0]
        signal_type = latest_signal.signal_type.value
        signal_color = "green" if signal_type == "BUY" else "red" if signal_type == "SELL" else "gray"
        
        st.markdown(f"**Signal:** :{signal_color}[{signal_type}]")
        st.markdown(f"**Price:** ₹{latest_signal.price:.2f}")
        st.markdown(f"**Strength:** {latest_signal.strength*100:.1f}%")
        st.markdown(f"**Reason:** {latest_signal.reason}")
        st.markdown(f"**Time:** {latest_signal.timestamp}")
    else:
        st.info("No active signals")

with col_strength:
    st.subheader("📊 Signal History")
    if signals:
        signal_df = pd.DataFrame([s.to_dict() for s in signals])
        st.dataframe(signal_df, use_container_width=True, hide_index=True)
    else:
        st.info("No signal history")

# Price chart
st.markdown("---")
st.subheader("📉 Price Chart with Indicators")

# Create subplots
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.5, 0.25, 0.25],
    subplot_titles=("Price & Moving Averages", "RSI", "MACD")
)

# Candlestick chart
fig.add_trace(
    go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price"
    ),
    row=1, col=1
)

# Moving averages
if 'sma_20' in df.columns:
    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df['sma_20'], name="SMA 20", line=dict(color='orange', width=1)),
        row=1, col=1
    )

if 'sma_50' in df.columns:
    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df['sma_50'], name="SMA 50", line=dict(color='blue', width=1)),
        row=1, col=1
    )

# Bollinger Bands
if 'bb_upper' in df.columns:
    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df['bb_upper'], name="BB Upper", 
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['datetime'], y=df['bb_lower'], name="BB Lower",
                  line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )

# RSI
fig.add_trace(
    go.Scatter(x=df['datetime'], y=df['rsi'], name="RSI", line=dict(color='purple', width=2)),
    row=2, col=1
)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# MACD
fig.add_trace(
    go.Scatter(x=df['datetime'], y=df['macd'], name="MACD", line=dict(color='blue', width=1)),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=df['datetime'], y=df['macd_signal'], name="Signal", line=dict(color='red', width=1)),
    row=3, col=1
)
fig.add_trace(
    go.Bar(x=df['datetime'], y=df['macd_histogram'], name="Histogram", marker_color='gray'),
    row=3, col=1
)

# Update layout
fig.update_layout(
    height=900,
    showlegend=True,
    xaxis_rangeslider_visible=False,
    hovermode='x unified'
)

fig.update_xaxes(title_text="Date", row=3, col=1)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="RSI", row=2, col=1)
fig.update_yaxes(title_text="MACD", row=3, col=1)

st.plotly_chart(fig, use_container_width=True)

# Portfolio section
st.markdown("---")
st.subheader("💼 Portfolio Summary")

portfolio = risk_manager.get_portfolio_summary()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Value", f"₹{portfolio['total_value']:,.2f}")

with col2:
    st.metric("Cash", f"₹{portfolio['cash']:,.2f}")

with col3:
    st.metric("Positions Value", f"₹{portfolio['positions_value']:,.2f}")

with col4:
    return_pct = portfolio['total_return_percent']
    st.metric("Total Return", f"{return_pct:.2f}%", delta=f"{return_pct:.2f}%")

# Open positions
if portfolio['positions']:
    st.subheader("📌 Open Positions")
    positions_data = []
    for symbol, pos in portfolio['positions'].items():
        positions_data.append({
            'Symbol': symbol,
            'Quantity': pos['quantity'],
            'Entry Price': f"₹{pos['entry_price']:.2f}",
            'Current Price': f"₹{pos['current_price']:.2f}",
            'P&L': f"₹{pos['unrealized_pnl']:.2f}",
            'P&L %': f"{pos['unrealized_pnl_percent']:.2f}%"
        })
    
    st.dataframe(pd.DataFrame(positions_data), use_container_width=True, hide_index=True)
else:
    st.info("No open positions")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center'>"
    "<p>Built with ❤️ using Python, Streamlit, and yfinance</p>"
    "<p>⚠️ For educational purposes only. Not financial advice.</p>"
    "</div>",
    unsafe_allow_html=True
)
