"""
Risk Manager
Manages position sizing, stop losses, and portfolio risk
"""

from typing import Dict, Optional
from dataclasses import dataclass

from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('risk_manager', config.get('logging'))


@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    
    @property
    def market_value(self) -> float:
        """Current market value of position"""
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """Unrealized profit/loss percentage"""
        return (self.current_price - self.entry_price) / self.entry_price
    
    def update_price(self, price: float):
        """Update current price"""
        self.current_price = price


class RiskManager:
    """Manage trading risk and position sizing"""
    
    def __init__(self):
        """Initialize risk manager"""
        self.risk_config = config.get_risk_config()
        self.portfolio_value = self.risk_config.get('initial_capital', 100000)
        self.initial_capital = self.portfolio_value
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = 0.0
        
        logger.info(f"Initialized RiskManager with capital: Rs.{self.portfolio_value:,.2f}")
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: float,
        signal_strength: float = 1.0
    ) -> int:
        """
        Calculate position size based on risk parameters
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            stop_loss_price: Stop loss price
            signal_strength: Signal strength (0-1)
            
        Returns:
            Number of shares to buy
        """
        # Maximum risk per trade
        max_risk_per_trade = self.risk_config.get('max_portfolio_risk', 0.02)
        risk_amount = self.portfolio_value * max_risk_per_trade * signal_strength
        
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            logger.warning("Risk per share is zero, using default position size")
            risk_per_share = entry_price * 0.01  # Default 1% risk
        
        # Calculate shares
        shares = int(risk_amount / risk_per_share)
        
        # Apply maximum position size constraint
        max_position_size = self.risk_config.get('max_position_size', 0.1)
        max_shares = int((self.portfolio_value * max_position_size) / entry_price)
        
        shares = min(shares, max_shares)
        
        # Ensure at least 1 share if we have enough capital
        if shares == 0 and self.portfolio_value > entry_price:
            shares = 1
        
        logger.info(f"Calculated position size for {symbol}: {shares} shares at ${entry_price:.2f}")
        return shares
    
    def can_open_position(self, symbol: str, estimated_cost: float) -> bool:
        """
        Check if we can open a new position
        
        Args:
            symbol: Stock symbol
            estimated_cost: Estimated cost of position
            
        Returns:
            True if position can be opened
        """
        # Check maximum open positions
        max_positions = self.risk_config.get('max_open_positions', 5)
        if len(self.positions) >= max_positions:
            logger.warning(f"Maximum positions ({max_positions}) reached")
            return False
        
        # Check if we already have a position in this symbol
        if symbol in self.positions:
            logger.warning(f"Already have position in {symbol}")
            return False
        
        # Check if we have enough capital
        if estimated_cost > self.portfolio_value * 0.95:  # Keep 5% cash buffer
            logger.warning(f"Insufficient capital for {symbol}")
            return False
        
        # Check daily loss limit
        max_daily_loss = self.risk_config.get('max_daily_loss', 0.05)
        daily_loss_limit = self.initial_capital * max_daily_loss
        
        if self.daily_pnl < -daily_loss_limit:
            logger.warning(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        return True
    
    def add_position(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ):
        """
        Add a new position to portfolio
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.positions[symbol] = position
        self.portfolio_value -= (quantity * entry_price)
        
        logger.info(f"Added position: {symbol} x{quantity} @ ${entry_price:.2f}")
        logger.info(f"Remaining capital: ${self.portfolio_value:.2f}")
    
    def remove_position(self, symbol: str, exit_price: float) -> Optional[Position]:
        """
        Remove a position from portfolio
        
        Args:
            symbol: Stock symbol
            exit_price: Exit price
            
        Returns:
            Removed position or None
        """
        if symbol not in self.positions:
            logger.warning(f"No position found for {symbol}")
            return None
        
        position = self.positions[symbol]
        position.update_price(exit_price)
        
        # Update portfolio value
        proceeds = position.quantity * exit_price
        self.portfolio_value += proceeds
        
        # Update daily P&L
        self.daily_pnl += position.unrealized_pnl
        
        # Remove position
        del self.positions[symbol]
        
        logger.info(
            f"Closed position: {symbol} x{position.quantity} @ ${exit_price:.2f} "
            f"| P&L: ${position.unrealized_pnl:.2f} ({position.unrealized_pnl_percent*100:.2f}%)"
        )
        
        return position
    
    def update_position_prices(self, prices: Dict[str, float]):
        """
        Update current prices for all positions
        
        Args:
            prices: Dictionary of symbol -> current_price
        """
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)
    
    def check_stop_loss(self, symbol: str) -> bool:
        """
        Check if stop loss triggered for a position
        
        Args:
            symbol: Stock symbol
            
        Returns:
            True if stop loss triggered
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position.current_price <= position.stop_loss:
            logger.warning(
                f"Stop loss triggered for {symbol}: "
                f"${position.current_price:.2f} <= ${position.stop_loss:.2f}"
            )
            return True
        
        return False
    
    def check_take_profit(self, symbol: str) -> bool:
        """
        Check if take profit triggered for a position
        
        Args:
            symbol: Stock symbol
            
        Returns:
            True if take profit triggered
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position.current_price >= position.take_profit:
            logger.info(
                f"Take profit triggered for {symbol}: "
                f"${position.current_price:.2f} >= ${position.take_profit:.2f}"
            )
            return True
        
        return False
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary
        
        Returns:
            Dictionary with portfolio metrics
        """
        total_unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )
        
        total_market_value = sum(
            pos.market_value for pos in self.positions.values()
        )
        
        total_value = self.portfolio_value + total_market_value
        total_return = (total_value - self.initial_capital) / self.initial_capital
        
        return {
            'cash': self.portfolio_value,
            'positions_value': total_market_value,
            'total_value': total_value,
            'unrealized_pnl': total_unrealized_pnl,
            'daily_pnl': self.daily_pnl,
            'total_return_percent': total_return * 100,
            'num_positions': len(self.positions),
            'positions': {
                symbol: {
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'unrealized_pnl_percent': pos.unrealized_pnl_percent * 100
                }
                for symbol, pos in self.positions.items()
            }
        }
    
    def reset_daily_pnl(self):
        """Reset daily P&L counter (call at start of each trading day)"""
        self.daily_pnl = 0.0
        logger.info("Daily P&L reset")
