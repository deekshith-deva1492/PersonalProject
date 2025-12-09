"""
Data Fetcher
Fetches real-time and historical market data from Zerodha
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import pytz
import os
from dotenv import load_dotenv

from src.utils.logger import get_logger
from src.utils.config import config

# Load environment variables
load_dotenv()

logger = get_logger('data_fetcher', config.get('logging'))

# Import Zerodha broker
try:
    from src.brokers.zerodha_broker import ZerodhaBroker
    ZERODHA_AVAILABLE = True
except ImportError:
    ZERODHA_AVAILABLE = False
    logger.warning("Zerodha broker not available")


class DataFetcher:
    """Fetch market data from Zerodha"""
    
    def __init__(self, provider: str = "zerodha"):
        """
        Initialize data fetcher with Zerodha
        
        Args:
            provider: Data provider (zerodha)
        """
        self.provider = provider
        self.data_config = config.get_data_config()
        
        # Initialize Zerodha connection
        if provider == "zerodha" and ZERODHA_AVAILABLE:
            api_key = os.getenv('ZERODHA_API_KEY')
            api_secret = os.getenv('ZERODHA_API_SECRET')
            access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
            
            if api_key and access_token:
                try:
                    self.broker = ZerodhaBroker(api_key, api_secret, access_token)
                    logger.info("Initialized DataFetcher with Zerodha API")
                except Exception as e:
                    logger.error(f"Failed to initialize Zerodha: {e}")
                    logger.info("Falling back to paper trading mode")
                    from src.brokers.zerodha_broker import MockZerodhaBroker
                    self.broker = MockZerodhaBroker()
            else:
                logger.warning("Zerodha credentials not found, using mock broker")
                from src.brokers.zerodha_broker import MockZerodhaBroker
                self.broker = MockZerodhaBroker()
        else:
            logger.warning("Zerodha not available, using mock broker")
            from src.brokers.zerodha_broker import MockZerodhaBroker
            self.broker = MockZerodhaBroker()
    
    def get_historical_data(
        self,
        symbol: str,
        interval: str = "5min",
        days: int = 5
    ) -> pd.DataFrame:
        """
        Get historical data for a symbol from Zerodha
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS')
            interval: Data interval (minute, 3minute, 5minute, 15minute, 30minute, 60minute, day)
            days: Number of days to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching {days} days of {interval} data for {symbol}")
            
            if self.provider == "zerodha":
                return self._fetch_zerodha(symbol, interval, days)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()
    
    def _fetch_zerodha(
        self,
        symbol: str,
        interval: str,
        days: int
    ) -> pd.DataFrame:
        """Fetch data using Zerodha Kite API"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data from Zerodha
            df = self.broker.get_historical_data(
                instrument_token=symbol,
                from_date=start_date,
                to_date=end_date,
                interval=interval
            )
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return df
            
            # Data is already in correct format from broker
            # Index is already datetime
            # Columns are: open, high, low, close, volume
            
            logger.info(f"Fetched {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Zerodha data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_real_time_quote(self, symbol: str) -> dict:
        """
        Get real-time quote for a symbol from Zerodha
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            
        Returns:
            Dictionary with current price, volume, etc.
        """
        try:
            # Get quote from Zerodha
            quote_data = self.broker.get_quote(symbol)
            
            if not quote_data:
                logger.warning(f"No quote data for {symbol}")
                return {}
            
            # Extract relevant fields from Zerodha quote
            ohlc = quote_data.get('ohlc', {})
            quote = {
                'symbol': symbol,
                'price': quote_data.get('last_price', 0),
                'open': ohlc.get('open', 0),
                'high': ohlc.get('high', 0),
                'low': ohlc.get('low', 0),
                'close': ohlc.get('close', 0),
                'change': quote_data.get('change', 0),
                'change_percent': quote_data.get('change_percent', 0),
                'volume': quote_data.get('volume', 0),
                'timestamp': datetime.now()
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return {}
    
    def get_multiple_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            DataFrame with quotes for all symbols
        """
        quotes = []
        for symbol in symbols:
            quote = self.get_real_time_quote(symbol)
            if quote:
                quotes.append(quote)
        
        return pd.DataFrame(quotes)
    
    def is_market_open(self) -> bool:
        """
        Check if the market is currently open
        
        Returns:
            True if market is open, False otherwise
        """
        trading_config = config.get_trading_config()
        timezone = pytz.timezone(trading_config.get('timezone', 'America/New_York'))
        
        now = datetime.now(timezone)
        current_time = now.time()
        
        # Get market hours
        market_open = datetime.strptime(trading_config.get('market_open', '09:30'), '%H:%M').time()
        market_close = datetime.strptime(trading_config.get('market_close', '16:00'), '%H:%M').time()
        
        # Check if it's a weekday
        is_weekday = now.weekday() < 5
        
        # Check if current time is within market hours
        is_open = is_weekday and market_open <= current_time <= market_close
        
        return is_open
