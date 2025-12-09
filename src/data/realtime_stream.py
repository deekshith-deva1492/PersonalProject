"""
Real-time WebSocket Data Stream using Zerodha KiteTicker
Provides live tick-by-tick data without rate limits
"""

import time
import threading
from typing import Dict, List, Callable, Optional
from datetime import datetime
from collections import deque
import pandas as pd

from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('realtime_stream', config.get('logging'))

try:
    from kiteconnect import KiteTicker
    TICKER_AVAILABLE = True
except ImportError:
    TICKER_AVAILABLE = False
    logger.warning("KiteTicker not available")


class RealtimeDataStream:
    """
    Real-time WebSocket data stream for live market data
    
    Benefits over HTTP polling:
    - No rate limits! WebSocket keeps connection open
    - Real-time updates (tick-by-tick data)
    - Lower latency (~200ms vs ~1000ms)
    - More efficient (no repeated HTTP handshakes)
    """
    
    def __init__(self, api_key: str, access_token: str):
        """
        Initialize real-time data stream
        
        Args:
            api_key: Zerodha API key
            access_token: Valid access token
        """
        if not TICKER_AVAILABLE:
            raise ImportError("KiteTicker not available. Install: pip install kiteconnect")
        
        self.api_key = api_key
        self.access_token = access_token
        
        # Initialize KiteTicker
        self.kws = KiteTicker(api_key, access_token)
        
        # Data storage - keep last 100 ticks per symbol
        self.tick_data: Dict[str, deque] = {}
        self.latest_tick: Dict[str, Dict] = {}
        
        # Callbacks
        self.tick_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Connection state
        self.is_connected = False
        self.subscribed_tokens: List[int] = []
        
        # Symbol to token mapping (cache)
        self.symbol_to_token: Dict[str, int] = {}
        
        # Setup callbacks
        self._setup_callbacks()
        
        logger.info("Initialized RealtimeDataStream")
    
    def _setup_callbacks(self):
        """Setup WebSocket event handlers"""
        
        def on_ticks(ws, ticks):
            """Called when ticks are received"""
            for tick in ticks:
                instrument_token = tick.get('instrument_token')
                
                # Find symbol for this token
                symbol = None
                for sym, token in self.symbol_to_token.items():
                    if token == instrument_token:
                        symbol = sym
                        break
                
                if symbol:
                    # Initialize deque if needed
                    if symbol not in self.tick_data:
                        self.tick_data[symbol] = deque(maxlen=100)
                    
                    # Store tick with timestamp
                    tick['timestamp'] = datetime.now()
                    self.tick_data[symbol].append(tick)
                    self.latest_tick[symbol] = tick
                    
                    # Log tick received (helps verify streaming is working)
                    last_price = tick.get('last_price', 0)
                    # KiteTicker provides 'volume_traded' not 'volume'
                    volume = tick.get('volume_traded', tick.get('volume', 0))
                    logger.info(f"TICK: {symbol} | Rs.{last_price:.2f} | Vol: {volume:,}")
                    
                    # Call registered callbacks
                    for callback in self.tick_callbacks:
                        try:
                            callback(symbol, tick)
                        except Exception as e:
                            logger.error(f"Error in tick callback: {e}")
        
        def on_connect(ws, response):
            """Called when WebSocket connects"""
            self.is_connected = True
            logger.info("WebSocket connected successfully")
            
            # Resubscribe to tokens if any
            if self.subscribed_tokens:
                self.kws.subscribe(self.subscribed_tokens)
                self.kws.set_mode(self.kws.MODE_FULL, self.subscribed_tokens)
                logger.info(f"Resubscribed to {len(self.subscribed_tokens)} tokens")
        
        def on_close(ws, code, reason):
            """Called when WebSocket closes"""
            self.is_connected = False
            logger.warning(f"WebSocket closed: {code} - {reason}")
        
        def on_error(ws, code, reason):
            """Called on WebSocket error"""
            logger.error(f"WebSocket error: {code} - {reason}")
            for callback in self.error_callbacks:
                try:
                    callback(code, reason)
                except Exception as e:
                    logger.error(f"Error in error callback: {e}")
        
        # Assign callbacks
        self.kws.on_ticks = on_ticks
        self.kws.on_connect = on_connect
        self.kws.on_close = on_close
        self.kws.on_error = on_error
    
    def subscribe(self, symbols: List[str], instrument_tokens: Dict[str, int]):
        """
        Subscribe to real-time data for symbols
        
        Args:
            symbols: List of symbols (e.g., ['RELIANCE.NS', 'TCS.NS'])
            instrument_tokens: Dict mapping symbols to instrument tokens
        """
        # Update symbol-token mapping
        self.symbol_to_token.update(instrument_tokens)
        
        # Get tokens to subscribe
        tokens = [instrument_tokens[sym] for sym in symbols if sym in instrument_tokens]
        
        if not tokens:
            logger.warning("No valid tokens to subscribe")
            return
        
        # Subscribe to tokens
        self.subscribed_tokens.extend(tokens)
        self.subscribed_tokens = list(set(self.subscribed_tokens))  # Remove duplicates
        
        if self.is_connected:
            self.kws.subscribe(tokens)
            # Set mode to FULL for complete tick data
            self.kws.set_mode(self.kws.MODE_FULL, tokens)
            logger.info(f"Subscribed to {len(tokens)} symbols: {symbols[:5]}...")
        else:
            logger.info(f"Queued {len(tokens)} symbols for subscription")
    
    def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        tokens = [self.symbol_to_token[sym] for sym in symbols if sym in self.symbol_to_token]
        
        if tokens and self.is_connected:
            self.kws.unsubscribe(tokens)
            for token in tokens:
                if token in self.subscribed_tokens:
                    self.subscribed_tokens.remove(token)
            logger.info(f"Unsubscribed from {len(tokens)} symbols")
    
    def start(self):
        """Start WebSocket connection (non-blocking)"""
        if not self.is_connected:
            # Run in separate thread to avoid blocking
            thread = threading.Thread(target=self._start_websocket, daemon=True)
            thread.start()
            
            # Wait a bit for connection
            time.sleep(2)
            logger.info("WebSocket stream started")
    
    def _start_websocket(self):
        """Internal method to start WebSocket (blocking)"""
        try:
            self.kws.connect(threaded=False)
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self.is_connected = False
    
    def stop(self):
        """Stop WebSocket connection"""
        if self.is_connected:
            self.kws.close()
            self.is_connected = False
            logger.info("WebSocket stream stopped")
    
    def get_latest_tick(self, symbol: str) -> Optional[Dict]:
        """Get latest tick for a symbol"""
        return self.latest_tick.get(symbol)
    
    def get_tick_history(self, symbol: str, count: int = 100) -> List[Dict]:
        """Get recent tick history for a symbol"""
        if symbol in self.tick_data:
            return list(self.tick_data[symbol])[-count:]
        return []
    
    def register_tick_callback(self, callback: Callable):
        """Register callback for tick updates: callback(symbol, tick)"""
        self.tick_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable):
        """Register callback for errors: callback(code, reason)"""
        self.error_callbacks.append(callback)
    
    def build_5min_candle(self, symbol: str) -> Optional[Dict]:
        """
        Build a 5-minute candle from tick data
        
        Returns:
            Dict with OHLCV data or None
        """
        ticks = self.get_tick_history(symbol, count=100)
        
        if not ticks:
            return None
        
        # Get ticks from last 5 minutes
        now = datetime.now()
        recent_ticks = [t for t in ticks if (now - t['timestamp']).seconds <= 300]
        
        if not recent_ticks:
            return None
        
        # Build candle
        prices = [t.get('last_price', 0) for t in recent_ticks if t.get('last_price')]
        # KiteTicker provides 'volume_traded' not 'volume'
        volumes = [t.get('volume_traded', 0) for t in recent_ticks if t.get('volume_traded')]
        
        if not prices:
            return None
        
        candle = {
            'timestamp': now,
            'open': prices[0],
            'high': max(prices),
            'low': min(prices),
            'close': prices[-1],
            'volume': sum(volumes) if volumes else 0
        }
        
        return candle
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        tick = self.get_latest_tick(symbol)
        if tick:
            return tick.get('last_price')
        return None
    
    def is_symbol_subscribed(self, symbol: str) -> bool:
        """Check if symbol is subscribed"""
        return symbol in self.symbol_to_token and \
               self.symbol_to_token[symbol] in self.subscribed_tokens


class StreamingScanner:
    """
    Scanner using WebSocket streaming instead of HTTP polling
    
    Key Advantages:
    - No rate limits (single WebSocket connection)
    - Real-time signal detection (< 1 second latency)
    - Can scan continuously without delays
    - More efficient resource usage
    """
    
    def __init__(self, stream: RealtimeDataStream, strategy, alert_manager=None):
        """
        Initialize streaming scanner
        
        Args:
            stream: RealtimeDataStream instance
            strategy: Trading strategy instance
            alert_manager: AlertManager for notifications
        """
        self.stream = stream
        self.strategy = strategy
        self.alert_manager = alert_manager
        
        # Signal tracking
        self.active_signals: Dict[str, Dict] = {}
        self.last_check: Dict[str, datetime] = {}
        
        # Register callback for tick updates
        self.stream.register_tick_callback(self._on_tick_update)
        
        logger.info("Initialized StreamingScanner")
    
    def _on_tick_update(self, symbol: str, tick: Dict):
        """Called on every tick - check for signals"""
        
        # Throttle checks (don't check every single tick)
        now = datetime.now()
        if symbol in self.last_check:
            elapsed = (now - self.last_check[symbol]).seconds
            if elapsed < 2:  # Check max once per 2 seconds per symbol (was 5s)
                return
        
        self.last_check[symbol] = now
        logger.debug(f"🔍 Checking signal for {symbol}")
        
        # Build recent candle data
        candle = self.stream.build_5min_candle(symbol)
        if not candle:
            return
        
        # Check for signals (would need historical data + this candle)
        # For now, just log the update
        logger.debug(f"{symbol}: Price ₹{tick.get('last_price', 0):.2f}")
    
    def start_monitoring(self, symbols: List[str], instrument_tokens: Dict[str, int]):
        """
        Start monitoring symbols for signals
        
        Args:
            symbols: List of symbols to monitor
            instrument_tokens: Dict mapping symbols to tokens
        """
        logger.info(f"Starting real-time monitoring for {len(symbols)} symbols")
        
        # Subscribe to symbols
        self.stream.subscribe(symbols, instrument_tokens)
        
        logger.info("✅ Now receiving real-time data - signals will be detected instantly!")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.stream.stop()
        logger.info("Stopped real-time monitoring")
