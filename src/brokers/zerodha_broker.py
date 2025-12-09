"""
Zerodha Kite API Integration
Handles connection to Zerodha broker for live trading
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd

try:
    from kiteconnect import KiteConnect
    KITE_AVAILABLE = True
except ImportError:
    KITE_AVAILABLE = False
    logging.warning("kiteconnect not installed. Install with: pip install kiteconnect")

class ZerodhaBroker:
    """
    Zerodha broker integration for live trading
    
    Setup Instructions:
    1. Create Zerodha account and get API key from https://kite.trade/
    2. Install kiteconnect: pip install kiteconnect
    3. Set environment variables:
       - ZERODHA_API_KEY
       - ZERODHA_API_SECRET
       - ZERODHA_ACCESS_TOKEN (after first login)
    """
    
    def __init__(self, api_key: str, api_secret: str = None, access_token: str = None):
        """
        Initialize Zerodha broker connection
        
        Args:
            api_key: Zerodha API key
            api_secret: Zerodha API secret (for login)
            access_token: Previously generated access token
        """
        if not KITE_AVAILABLE:
            raise ImportError("kiteconnect library not installed. Run: pip install kiteconnect")
        
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        
        # Initialize KiteConnect
        self.kite = KiteConnect(api_key=api_key)
        
        if access_token:
            self.kite.set_access_token(access_token)
            self.logger.info("Zerodha connection initialized with access token")
        else:
            self.logger.warning("No access token provided. Need to complete login flow.")
    
    def login(self, request_token: str) -> str:
        """
        Complete login flow and generate access token
        
        Args:
            request_token: Request token from redirect URL after login
            
        Returns:
            Access token for future sessions
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            
            self.logger.info("Login successful. Access token generated.")
            self.logger.info(f"Save this token: {self.access_token}")
            
            return self.access_token
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise
    
    def get_login_url(self) -> str:
        """Get login URL for authorization"""
        return self.kite.login_url()
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        try:
            return self.kite.profile()
        except Exception as e:
            self.logger.error(f"Failed to get profile: {e}")
            return {}
    
    def get_margins(self) -> Dict:
        """Get account margins"""
        try:
            margins = self.kite.margins()
            return margins
        except Exception as e:
            self.logger.error(f"Failed to get margins: {e}")
            return {}
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return positions
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return {'net': [], 'day': []}
    
    def get_orders(self) -> List[Dict]:
        """Get all orders"""
        try:
            orders = self.kite.orders()
            return orders
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []
    
    def get_historical_data(
        self, 
        instrument_token: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "5minute"
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data
        
        Args:
            instrument_token: NSE instrument token (e.g., "NSE:RELIANCE")
            from_date: Start date
            to_date: End date
            interval: Candle interval (minute, 3minute, 5minute, 15minute, day)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Get instrument token
            instruments = self.kite.instruments("NSE")
            token = None
            
            # Extract symbol from instrument_token (remove .NS suffix)
            symbol = instrument_token.replace('.NS', '')
            
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    token = inst['instrument_token']
                    break
            
            if not token:
                self.logger.error(f"Instrument token not found for {symbol}")
                return pd.DataFrame()
            
            # Fetch historical data
            data = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.rename(columns={
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                }, inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data: {e}")
            return pd.DataFrame()
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Trading symbol (e.g., "RELIANCE")
            
        Returns:
            Quote data dictionary
        """
        try:
            # Format symbol for Kite API
            instrument = f"NSE:{symbol.replace('.NS', '')}"
            quote = self.kite.quote(instrument)
            return quote.get(instrument, {})
            
        except Exception as e:
            self.logger.error(f"Failed to get quote for {symbol}: {e}")
            return {}
    
    def place_order(
        self,
        symbol: str,
        transaction_type: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "MIS",
        price: float = None,
        trigger_price: float = None,
        validity: str = "DAY"
    ) -> Optional[str]:
        """
        Place an order
        
        Args:
            symbol: Trading symbol (without .NS)
            transaction_type: BUY or SELL
            quantity: Order quantity
            order_type: MARKET, LIMIT, SL, SL-M
            product: CNC (delivery), MIS (intraday), NRML (normal)
            price: Limit price (for LIMIT orders)
            trigger_price: Trigger price (for SL orders)
            validity: DAY or IOC
            
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            symbol = symbol.replace('.NS', '')
            
            order_params = {
                'tradingsymbol': symbol,
                'exchange': 'NSE',
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type,
                'product': product,
                'validity': validity
            }
            
            if price:
                order_params['price'] = price
            if trigger_price:
                order_params['trigger_price'] = trigger_price
            
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                **order_params
            )
            
            self.logger.info(f"Order placed successfully: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
    
    def modify_order(
        self,
        order_id: str,
        quantity: int = None,
        price: float = None,
        trigger_price: float = None,
        order_type: str = None
    ) -> bool:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity
            price: New price
            trigger_price: New trigger price
            order_type: New order type
            
        Returns:
            True if successful
        """
        try:
            order_params = {}
            if quantity:
                order_params['quantity'] = quantity
            if price:
                order_params['price'] = price
            if trigger_price:
                order_params['trigger_price'] = trigger_price
            if order_type:
                order_params['order_type'] = order_type
            
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                **order_params
            )
            
            self.logger.info(f"Order {order_id} modified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to modify order {order_id}: {e}")
            return False
    
    def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            variety: Order variety (regular, amo, etc.)
            
        Returns:
            True if successful
        """
        try:
            self.kite.cancel_order(
                variety=variety,
                order_id=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def get_nifty50_instruments(self) -> List[str]:
        """
        Get list of NIFTY 50 instrument tokens
        
        Returns:
            List of tradingsymbols
        """
        nifty50_symbols = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
            'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'HCLTECH',
            'BAJFINANCE', 'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND',
            'WIPRO', 'ONGC', 'NTPC', 'POWERGRID', 'TECHM',
            'M&M', 'TATAMOTORS', 'TATASTEEL', 'INDUSINDBK', 'BAJAJFINSV',
            'ADANIENT', 'COALINDIA', 'DRREDDY', 'GRASIM', 'HINDALCO',
            'DIVISLAB', 'CIPLA', 'EICHERMOT', 'SHREECEM', 'APOLLOHOSP',
            'BPCL', 'JSWSTEEL', 'HEROMOTOCO', 'BRITANNIA', 'TATACONSUM',
            'SBILIFE', 'ADANIPORTS', 'UPL', 'BAJAJ-AUTO', 'HDFCLIFE'
        ]
        return nifty50_symbols
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        
        # NSE timings: 9:15 AM to 3:30 PM IST, Monday to Friday
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        return market_open <= now <= market_close


# Mock broker for testing without Zerodha API
class MockZerodhaBroker(ZerodhaBroker):
    """Mock broker for paper trading and testing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Using Mock Zerodha Broker (Paper Trading Mode)")
        self.orders = []
        self.positions = []
    
    def get_profile(self) -> Dict:
        return {
            'user_id': 'MOCK_USER',
            'user_name': 'Paper Trading User',
            'email': 'paper@trading.com'
        }
    
    def get_margins(self) -> Dict:
        return {
            'equity': {
                'available': {
                    'cash': 100000.0,
                    'live_balance': 100000.0
                }
            }
        }
    
    def place_order(self, symbol: str, transaction_type: str, quantity: int, **kwargs) -> str:
        order_id = f"MOCK_{len(self.orders) + 1}"
        self.orders.append({
            'order_id': order_id,
            'symbol': symbol,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'status': 'COMPLETE'
        })
        self.logger.info(f"[PAPER TRADE] {transaction_type} {quantity} {symbol}")
        return order_id
    
    def get_orders(self) -> List[Dict]:
        return self.orders
    
    def get_positions(self) -> Dict:
        return {'net': self.positions, 'day': self.positions}
