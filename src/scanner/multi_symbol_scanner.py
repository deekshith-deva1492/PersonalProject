"""
Multi-Symbol Scanner - Scans all NIFTY 50 stocks continuously
Finds trading opportunities in real-time
"""

import time
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from src.data.data_fetcher import DataFetcher
from src.data.data_processor import DataProcessor
from src.strategies.intraday_strategy import IntradayStrategy
from src.strategies.base_strategy import Signal
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('multi_symbol_scanner', config.get('logging'))


class RateLimiter:
    """Rate limiter for API calls - respects Zerodha's 3 requests/second limit"""
    
    def __init__(self, max_calls: int = 3, time_window: float = 1.0):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            
            # Remove calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # If at limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0]) + 0.1  # Add 100ms buffer
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    # Remove expired calls after waiting
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # Record this call
            self.calls.append(time.time())


class MultiSymbolScanner:
    """Continuously scan multiple symbols for trading signals"""
    
    def __init__(self, symbols: Optional[List[str]] = None, alert_manager=None):
        """
        Initialize multi-symbol scanner
        
        Args:
            symbols: List of symbols to scan (defaults to config symbols)
            alert_manager: AlertManager instance for sending notifications
        """
        self.symbols = symbols or config.get_symbols()
        self.data_fetcher = DataFetcher(provider="zerodha")
        self.data_processor = DataProcessor()
        self.strategy = IntradayStrategy()
        self.alert_manager = alert_manager
        
        # Rate limiter for Zerodha API (3 requests per second)
        self.rate_limiter = RateLimiter(max_calls=3, time_window=1.0)
        
        # Scanner state
        self.is_running = False
        self.signals: List[Signal] = []
        self.last_scan_time: Dict[str, datetime] = {}
        self.scan_interval = 60  # Scan every 60 seconds
        
        # Performance tracking
        self.symbols_scanned = 0
        self.signals_generated = 0
        
        logger.info(f"Initialized MultiSymbolScanner with {len(self.symbols)} symbols")
        logger.info("Rate limiter: 3 requests/second (Zerodha API limit)")
    
    def scan_single_symbol(self, symbol: str) -> List[Signal]:
        """
        Scan a single symbol for signals
        
        Args:
            symbol: Stock symbol to scan
            
        Returns:
            List of signals found
        """
        try:
            # Wait if needed to respect rate limits
            self.rate_limiter.wait_if_needed()
            
            # Fetch recent data (last 5 days)
            df = self.data_fetcher.get_historical_data(
                symbol=symbol,
                interval="5minute",
                days=5
            )
            
            if df.empty:
                logger.warning(f"No data for {symbol}")
                return []
            
            # Process data and add indicators
            df = self.data_processor.clean_data(df)
            df = self.strategy.indicators.calculate_all_indicators(df)
            
            # Generate signals
            signals = self.strategy.generate_signals(df, symbol)
            
            # Update scan time
            self.last_scan_time[symbol] = datetime.now()
            
            return signals
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return []
    
    def scan_all_symbols(self) -> List[Signal]:
        """
        Scan all symbols in parallel
        
        Returns:
            List of all signals found
        """
        all_signals = []
        start_time = time.time()
        
        logger.info(f"Starting scan of {len(self.symbols)} symbols...")
        
        # Use ThreadPoolExecutor for parallel scanning
        # Reduced to 2 workers to respect Zerodha rate limits (3 req/sec)
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit all scan tasks
            future_to_symbol = {
                executor.submit(self.scan_single_symbol, symbol): symbol
                for symbol in self.symbols
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    signals = future.result()
                    if signals:
                        all_signals.extend(signals)
                        logger.info(f"✅ {symbol}: Found {len(signals)} signal(s)")
                    
                    self.symbols_scanned += 1
                    
                except Exception as e:
                    logger.error(f"❌ {symbol} failed: {e}")
        
        elapsed = time.time() - start_time
        self.signals_generated += len(all_signals)
        
        logger.info(f"Scan complete: {len(all_signals)} signals in {elapsed:.1f}s")
        
        # Send alerts if signals found and alert manager is configured
        if all_signals and self.alert_manager:
            if len(all_signals) == 1:
                self.alert_manager.send_signal_alert(all_signals[0])
            else:
                self.alert_manager.send_multiple_signals_alert(all_signals)
        
        return all_signals
    
    def start_continuous_scan(self, callback=None):
        """
        Start continuous scanning
        
        Args:
            callback: Optional callback function called with signals: callback(signals)
        """
        self.is_running = True
        logger.info("🔍 Starting continuous scanner...")
        
        while self.is_running:
            try:
                # Check if market is open
                if not self._is_market_hours():
                    logger.info("Market closed. Waiting...")
                    time.sleep(300)  # Check every 5 minutes
                    continue
                
                # Scan all symbols
                signals = self.scan_all_symbols()
                
                # Store signals
                if signals:
                    self.signals.extend(signals)
                    
                    # Call callback if provided
                    if callback:
                        callback(signals)
                    
                    # Log new signals
                    for signal in signals:
                        logger.info(f"📊 NEW SIGNAL: {signal}")
                        logger.info(signal.get_detailed_explanation())
                
                # Wait before next scan
                logger.info(f"Waiting {self.scan_interval}s before next scan...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Scanner stopped by user")
                self.is_running = False
                break
            
            except Exception as e:
                logger.error(f"Error in continuous scan: {e}")
                time.sleep(self.scan_interval)
    
    def stop(self):
        """Stop the scanner"""
        self.is_running = False
        logger.info("Scanner stopped")
    
    def _is_market_hours(self) -> bool:
        """Check if market is currently open"""
        try:
            trading_config = config.get_trading_config()
            market_open = trading_config.get('market_open', '09:15')
            market_close = trading_config.get('market_close', '15:30')
            
            # Parse times
            now = datetime.now()
            open_time = datetime.strptime(market_open, '%H:%M').time()
            close_time = datetime.strptime(market_close, '%H:%M').time()
            current_time = now.time()
            
            # Check if weekday
            if now.weekday() >= 5:  # Saturday=5, Sunday=6
                return False
            
            # Check if within market hours
            return open_time <= current_time <= close_time
            
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return True  # Assume market is open if check fails
    
    def get_recent_signals(self, minutes: int = 60) -> List[Signal]:
        """
        Get signals from the last N minutes
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            List of recent signals
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            signal for signal in self.signals
            if signal.timestamp >= cutoff_time
        ]
    
    def get_statistics(self) -> Dict:
        """Get scanner statistics"""
        return {
            'is_running': self.is_running,
            'symbols_count': len(self.symbols),
            'symbols_scanned': self.symbols_scanned,
            'signals_generated': self.signals_generated,
            'signals_in_memory': len(self.signals),
            'last_scan_times': self.last_scan_time
        }
    
    def clear_old_signals(self, hours: int = 24):
        """
        Remove signals older than specified hours
        
        Args:
            hours: Age threshold in hours
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        original_count = len(self.signals)
        
        self.signals = [
            signal for signal in self.signals
            if signal.timestamp >= cutoff_time
        ]
        
        removed = original_count - len(self.signals)
        if removed > 0:
            logger.info(f"Cleared {removed} old signals")
