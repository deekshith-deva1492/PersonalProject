"""
Scanner Dashboard - View all signals from all NIFTY 50 stocks
Shows real-time signals, detailed explanations, and allows signal execution
Supports both HTTP polling and WebSocket streaming modes
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv

from src.scanner.multi_symbol_scanner import MultiSymbolScanner
from src.execution.auto_executor import AutoTradeExecutor
from src.brokers.zerodha_broker import ZerodhaBroker
from src.risk.risk_manager import RiskManager
from src.utils.config import config
from src.utils.alerting import AlertManager
from src.data.realtime_stream import RealtimeDataStream, StreamingScanner
from src.utils.market_hours import check_market_hours, get_market_status_detailed

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="NIFTY 50 Scanner",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .signal-card {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin: 10px 0;
    }
    .buy-signal {
        background-color: #d4edda;
        border-color: #28a745;
    }
    .sell-signal {
        background-color: #f8d7da;
        border-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'scanner' not in st.session_state:
    st.session_state.scanner = MultiSymbolScanner()
    st.session_state.scanner_running = False
    st.session_state.last_scan_time = None
    st.session_state.signals = []
    st.session_state.previous_signal_count = 0
    st.session_state.scan_mode = "WebSocket"  # DEFAULT: WebSocket for real-time streaming
    st.session_state.websocket_stream = None
    st.session_state.streaming_scanner = None
    st.session_state.websocket_connected = False

if 'alert_manager' not in st.session_state:
    # Initialize alert manager with default settings (desktop + sound enabled)
    st.session_state.alert_manager = AlertManager({
        'desktop_alerts': True,
        'sound_alerts': True,
        'email_alerts': False,
        'telegram_alerts': False
    })

if 'executor' not in st.session_state:
    # Initialize Zerodha broker
    api_key = os.getenv('ZERODHA_API_KEY')
    api_secret = os.getenv('ZERODHA_API_SECRET')
    access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
    
    if all([api_key, api_secret, access_token]):
        broker = ZerodhaBroker(api_key, api_secret, access_token)
        risk_manager = RiskManager()
        st.session_state.executor = AutoTradeExecutor(broker, risk_manager, dry_run=True)
    else:
        st.session_state.executor = None


# Title
st.title("🔍 NIFTY 50 Multi-Symbol Scanner")
st.markdown("Real-time scanning of all 50 NIFTY stocks for trading opportunities")

# Market Hours Check - Display prominent warning if market is closed
is_market_open, market_message = check_market_hours()
if not is_market_open:
    st.error(market_message)
    market_status = get_market_status_detailed()
    st.warning(f"📅 {market_status['current_day']} {market_status['current_time']} | {market_status['next_event']}")
    st.info(f"ℹ️ Market Hours: {market_status['market_hours']}")
else:
    st.success(market_message)

# Sidebar controls
st.sidebar.header("Scanner Controls")

# Manual scan button REMOVED - WebSocket is always live streaming
# No need for manual "Scan All Symbols" button anymore
# Signals are detected automatically in real-time

# Old HTTP polling scan button (removed):
# if st.sidebar.button("🔍 Scan All Symbols", use_container_width=True):
#     with st.spinner("Scanning all NIFTY 50 stocks..."):
#         signals = st.session_state.scanner.scan_all_symbols()
#         ...

st.sidebar.info("🔴 **LIVE STREAMING**\n\nWebSocket automatically scans all 49 NIFTY 50 stocks in real-time. Signals appear instantly when conditions are met.")

# WebSocket is the ONLY mode now - no mode selector
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Data Mode")
st.sidebar.info("🔴 LIVE - WebSocket Streaming Active")
st.sidebar.caption("Real-time tick updates (<1 second latency)")

# Force WebSocket mode (no HTTP option)
st.session_state.scan_mode = "WebSocket"
auto_scan = False  # No auto-scan needed - WebSocket is always live

# HTTP Polling mode REMOVED - WebSocket only
# Old HTTP polling code commented out below:
# st.sidebar.markdown("---")
# if st.session_state.scan_mode == "HTTP":
#     auto_scan = st.sidebar.checkbox("Enable Auto-Scan (every 60s)")
# else:
#     auto_scan = False
#     st.sidebar.info("🔴 LIVE - WebSocket streaming active")

# Alert settings
st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Alert Settings")

desktop_alerts = st.sidebar.checkbox("Desktop Notifications", value=True)
sound_alerts = st.sidebar.checkbox("Sound Alerts", value=True)

# Update alert manager settings
st.session_state.alert_manager.desktop_enabled = desktop_alerts
st.session_state.alert_manager.sound_enabled = sound_alerts

# Test alerts button
if st.sidebar.button("🧪 Test Alerts"):
    st.session_state.alert_manager.test_alerts()
    st.sidebar.success("Alert test sent!")

# WebSocket status (if in WebSocket mode)
if st.session_state.scan_mode == "WebSocket":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔴 WebSocket Status")
    
    if st.session_state.websocket_connected:
        st.sidebar.success("Connected & Streaming")
        st.sidebar.metric("Mode", "Real-Time")
        st.sidebar.metric("Latency", "< 1 second")
    else:
        st.sidebar.warning("Initializing...")
        if st.sidebar.button("🔄 Reconnect WebSocket"):
            if st.session_state.websocket_stream:
                st.session_state.websocket_stream.stop()
            st.session_state.websocket_stream = None
            st.rerun()

# Scanner statistics - WebSocket only
st.sidebar.markdown("---")
st.sidebar.subheader("Scanner Stats")

# Only WebSocket stats (HTTP mode removed)
st.sidebar.metric("Mode", "WebSocket Streaming")
st.sidebar.metric("Symbols", "49 NIFTY 50")
st.sidebar.metric("Updates", "Real-Time (<1s)")
if st.session_state.signals:
    st.sidebar.metric("Active Signals", len(st.session_state.signals))

# Auto-trading controls
st.sidebar.markdown("---")
st.sidebar.subheader("Auto-Trading")

if st.session_state.executor:
    if st.sidebar.button("🟢 Activate Auto-Trading", use_container_width=True):
        st.session_state.executor.activate()
        st.sidebar.success("Auto-trading ACTIVATED!")
    
    if st.sidebar.button("🔴 Deactivate Auto-Trading", use_container_width=True):
        st.session_state.executor.deactivate()
        st.sidebar.warning("Auto-trading DEACTIVATED")
    
    exec_stats = st.session_state.executor.get_statistics()
    st.sidebar.metric("Auto-Trade Status", "🟢 ACTIVE" if exec_stats['is_active'] else "🔴 INACTIVE")
    st.sidebar.metric("Trades Today", f"{exec_stats['trades_today']}/{exec_stats['max_trades_per_day']}")
else:
    st.sidebar.warning("Executor not initialized. Check .env credentials.")

# Main content
if st.session_state.last_scan_time:
    st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Display signals
if st.session_state.signals:
    st.header(f"📊 Active Signals ({len(st.session_state.signals)})")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    buy_signals = [s for s in st.session_state.signals if s.signal_type.value == 'BUY']
    sell_signals = [s for s in st.session_state.signals if s.signal_type.value == 'SELL']
    avg_strength = sum(s.strength for s in st.session_state.signals) / len(st.session_state.signals)
    
    # Count signals by quality
    high_prob_count = 0
    strong_count = 0
    valid_count = 0
    for signal in st.session_state.signals:
        if signal.reason and '[' in signal.reason:
            if 'HIGH-PROB' in signal.reason:
                high_prob_count += 1
            elif 'STRONG' in signal.reason:
                strong_count += 1
            elif 'VALID' in signal.reason:
                valid_count += 1
    
    col1.metric("Total Signals", len(st.session_state.signals))
    col2.metric("BUY Signals", len(buy_signals), delta_color="normal")
    col3.metric("SELL Signals", len(sell_signals), delta_color="inverse")
    col4.metric("Avg Strength", f"{avg_strength:.1%}")
    col5.metric("HIGH-PROB (5+)", high_prob_count, delta_color="normal")
    
    st.markdown("---")
    
    # Display each signal
    for idx, signal in enumerate(st.session_state.signals):
        signal_dict = signal.to_dict()
        
        # Signal card
        card_class = "buy-signal" if signal.signal_type.value == 'BUY' else "sell-signal"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Extract score from reason (format: "BUY [QUALITY SCORE/8]: ...")
            score_text = ""
            quality_text = ""
            if signal.reason and '[' in signal.reason and ']' in signal.reason:
                try:
                    # Extract text between brackets: "[HIGH-PROB 5/8]"
                    bracket_content = signal.reason.split('[')[1].split(']')[0]
                    # Split into quality and score: "HIGH-PROB 5/8"
                    parts = bracket_content.rsplit(' ', 1)
                    if len(parts) == 2:
                        quality_text = parts[0]  # "HIGH-PROB"
                        score_text = parts[1]     # "5/8"
                except:
                    pass
            
            # Title with score badge
            if score_text:
                # Color code based on quality
                if "HIGH-PROB" in quality_text:
                    badge_color = "#28a745"  # Green
                elif "STRONG" in quality_text:
                    badge_color = "#ffc107"  # Yellow
                else:
                    badge_color = "#6c757d"  # Gray
                
                st.markdown(f"""
                ### {signal.symbol} - {signal.signal_type.value} 
                <span style="background-color: {badge_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold; margin-left: 10px;">
                    {quality_text} {score_text}
                </span>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"### {signal.symbol} - {signal.signal_type.value}")
            
            st.markdown(f"**Price:** ₹{signal.price:.2f} | **Strength:** {signal.strength:.1%}")
            st.markdown(f"**Time:** {signal.timestamp}")
            
            # Expandable detailed explanation
            with st.expander(f"📖 View Detailed Explanation"):
                st.markdown(f"```\n{signal.get_detailed_explanation()}\n```")
            
            # Conditions met
            if signal.conditions_met:
                st.markdown("**Conditions Met:**")
                for condition in signal.conditions_met:
                    st.markdown(f"- {condition}")
        
        with col2:
            # Trade setup
            if signal.stop_loss and signal.take_profit:
                st.markdown("**Trade Setup:**")
                st.metric("Entry", f"₹{signal.price:.2f}")
                st.metric("Stop Loss", f"₹{signal.stop_loss:.2f}")
                st.metric("Take Profit", f"₹{signal.take_profit:.2f}")
                
                rr_ratio = signal.get_risk_reward_ratio()
                if rr_ratio:
                    st.metric("R:R Ratio", f"1:{rr_ratio:.2f}")
            
            # Execute button
            if st.session_state.executor:
                if st.button(f"⚡ Execute Trade", key=f"exec_{idx}"):
                    with st.spinner("Executing trade..."):
                        result = st.session_state.executor.execute_signal(signal)
                        if result:
                            st.success(f"✅ Order placed! ID: {result.get('order_id', 'N/A')}")
                        else:
                            st.error("❌ Failed to place order")
        
        st.markdown("---")
    
    # Download signals as CSV
    if st.button("📥 Download Signals as CSV"):
        df_data = []
        for signal in st.session_state.signals:
            # Extract score from reason
            score_text = ""
            quality_text = ""
            if signal.reason and '[' in signal.reason and ']' in signal.reason:
                try:
                    bracket_content = signal.reason.split('[')[1].split(']')[0]
                    parts = bracket_content.rsplit(' ', 1)
                    if len(parts) == 2:
                        quality_text = parts[0]
                        score_text = parts[1]
                except:
                    pass
            
            df_data.append({
                'Symbol': signal.symbol,
                'Signal': signal.signal_type.value,
                'Quality': quality_text if quality_text else 'N/A',
                'Score': score_text if score_text else 'N/A',
                'Price': signal.price,
                'Strength': signal.strength,
                'Stop Loss': signal.stop_loss,
                'Take Profit': signal.take_profit,
                'R:R Ratio': signal.get_risk_reward_ratio(),
                'Reason': signal.reason,
                'Timestamp': signal.timestamp
            })
        
        df = pd.DataFrame(df_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    st.info("👆 Click 'Scan All Symbols' to start scanning for signals")
    
    # Show sample of symbols being monitored
    symbols = config.get_symbols()
    st.subheader("Monitored Symbols")
    
    # Display in columns
    cols = st.columns(5)
    for idx, symbol in enumerate(symbols):
        cols[idx % 5].markdown(f"- {symbol}")

# Footer
st.markdown("---")
st.markdown("**Note:** This scanner continuously monitors all NIFTY 50 stocks. Signals are generated based on technical analysis and should be verified before trading.")

# Initialize and run WebSocket streaming if in WebSocket mode
if st.session_state.scan_mode == "WebSocket":
    # Initialize WebSocket stream if not already done
    if st.session_state.websocket_stream is None:
        try:
            # Load instrument tokens
            if os.path.exists('instrument_tokens.json'):
                with open('instrument_tokens.json', 'r') as f:
                    tokens_data = json.load(f)
                
                # Get API credentials
                api_key = os.getenv('ZERODHA_API_KEY')
                access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
                
                if api_key and access_token:
                    # tokens_data is already a dict: {'SYMBOL.NS': token_int}
                    symbols = list(tokens_data.keys())
                    
                    st.info(f"🔄 Initializing WebSocket for {len(symbols)} symbols...")
                    
                    # Create WebSocket stream first
                    stream = RealtimeDataStream(
                        api_key=api_key,
                        access_token=access_token
                    )
                    
                    # Get strategy from the HTTP scanner
                    strategy = st.session_state.scanner.strategy
                    
                    # Create streaming scanner
                    streaming_scanner = StreamingScanner(
                        stream=stream,
                        strategy=strategy,
                        alert_manager=st.session_state.alert_manager
                    )
                    
                    # Subscribe to all symbols (pass dict, not separate lists!)
                    stream.subscribe(symbols, tokens_data)
                    
                    # START the WebSocket connection (this is crucial!)
                    stream.start()
                    
                    # Store in session state
                    st.session_state.websocket_stream = stream
                    st.session_state.streaming_scanner = streaming_scanner
                    st.session_state.websocket_connected = True
                    
                    st.success("✅ WebSocket connected! Streaming real-time data...")
                    st.toast("🔴 LIVE - Real-time streaming active!", icon="🚀")
                    st.rerun()
                else:
                    st.error("❌ Missing Zerodha API credentials in .env file")
            else:
                st.error("❌ instrument_tokens.json not found. Run: python get_instruments.py")
        except Exception as e:
            st.error(f"❌ WebSocket initialization failed: {str(e)}")
            st.session_state.scan_mode = "HTTP"  # Fall back to HTTP
    
    # WebSocket is running - just refresh UI periodically
    if st.session_state.websocket_connected:
        import time
        time.sleep(2)  # Refresh UI every 2 seconds
        st.rerun()

# HTTP auto-scan logic REMOVED - WebSocket only now
# Old HTTP polling auto-refresh code (commented out):
# elif auto_scan:
#     # Check if enough time has passed since last scan
#     should_scan = False
#     if st.session_state.last_scan_time is None:
#         should_scan = True
#     else:
#         time_since_scan = (datetime.now() - st.session_state.last_scan_time).total_seconds()
#         should_scan = time_since_scan >= 60  # 60 seconds interval
#     if should_scan:
#         # Automatically trigger scan
#         ...
# WebSocket mode handles everything automatically - no manual refresh needed
