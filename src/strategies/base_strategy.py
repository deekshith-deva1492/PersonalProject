"""
Base Strategy Class
Abstract base class for all trading strategies
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Tuple, Optional
from enum import Enum

from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('base_strategy', config.get('logging'))


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal:
    """Trading signal with detailed reasoning"""
    
    def __init__(
        self,
        symbol: str,
        signal_type: SignalType,
        price: float,
        strength: float,
        reason: str,
        timestamp: pd.Timestamp,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        indicators: Optional[Dict] = None,
        conditions_met: Optional[List[str]] = None
    ):
        """
        Initialize signal
        
        Args:
            symbol: Stock symbol
            signal_type: Type of signal (BUY, SELL, HOLD)
            price: Current price
            strength: Signal strength (0-1)
            reason: Short reason for the signal
            timestamp: Time of signal generation
            stop_loss: Recommended stop loss price
            take_profit: Recommended take profit price
            indicators: Dictionary of indicator values at signal time
            conditions_met: List of detailed conditions that triggered the signal
        """
        self.symbol = symbol
        self.signal_type = signal_type
        self.price = price
        self.strength = strength
        self.reason = reason
        self.timestamp = timestamp
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.indicators = indicators or {}
        self.conditions_met = conditions_met or []
    
    def __repr__(self):
        return f"Signal({self.symbol}, {self.signal_type.value}, ₹{self.price:.2f}, strength={self.strength:.2f})"
    
    def to_dict(self) -> Dict:
        """Convert signal to dictionary"""
        return {
            'symbol': self.symbol,
            'signal': self.signal_type.value,
            'price': self.price,
            'strength': self.strength,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward_ratio': self.get_risk_reward_ratio(),
            'indicators': self.indicators,
            'conditions_met': self.conditions_met,
            'detailed_explanation': self.get_detailed_explanation()
        }
    
    def get_risk_reward_ratio(self) -> Optional[float]:
        """Calculate risk/reward ratio"""
        if self.stop_loss and self.take_profit:
            risk = abs(self.price - self.stop_loss)
            reward = abs(self.take_profit - self.price)
            return reward / risk if risk > 0 else None
        return None
    
    def get_detailed_explanation(self) -> str:
        """Generate detailed explanation of why signal was triggered"""
        lines = [
            f"🔔 {self.signal_type.value} SIGNAL for {self.symbol}",
            f"📊 Price: ₹{self.price:.2f}",
            f"💪 Strength: {self.strength:.2%}",
            f"⏰ Time: {self.timestamp}",
            "",
            f"📝 Reason: {self.reason}",
            ""
        ]
        
        if self.conditions_met:
            lines.append("✅ Conditions Met:")
            for condition in self.conditions_met:
                lines.append(f"  • {condition}")
            lines.append("")
        
        if self.indicators:
            lines.append("📈 Indicator Values:")
            for key, value in self.indicators.items():
                if isinstance(value, float):
                    lines.append(f"  • {key}: {value:.2f}")
                else:
                    lines.append(f"  • {key}: {value}")
            lines.append("")
        
        if self.stop_loss and self.take_profit:
            risk = abs(self.price - self.stop_loss)
            reward = abs(self.take_profit - self.price)
            rr_ratio = self.get_risk_reward_ratio()
            
            lines.append("🎯 Trade Setup:")
            lines.append(f"  • Entry: ₹{self.price:.2f}")
            lines.append(f"  • Stop Loss: ₹{self.stop_loss:.2f} (Risk: ₹{risk:.2f} or {risk/self.price:.2%})")
            lines.append(f"  • Take Profit: ₹{self.take_profit:.2f} (Reward: ₹{reward:.2f} or {reward/self.price:.2%})")
            if rr_ratio:
                lines.append(f"  • Risk/Reward: 1:{rr_ratio:.2f}")
        
        return "\n".join(lines)


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.strategy_config = config.get_strategy_config()
        logger.info(f"Initialized strategy: {name}")
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        """
        Generate trading signals from data
        
        Args:
            df: DataFrame with price data and indicators
            symbol: Stock symbol
            
        Returns:
            List of trading signals
        """
        pass
    
    @abstractmethod
    def get_entry_conditions(self, row: pd.Series) -> Tuple[bool, str]:
        """
        Check entry conditions
        
        Args:
            row: Single row of data with indicators
            
        Returns:
            Tuple of (should_enter, reason)
        """
        pass
    
    @abstractmethod
    def get_exit_conditions(
        self,
        row: pd.Series,
        entry_price: float
    ) -> Tuple[bool, str]:
        """
        Check exit conditions
        
        Args:
            row: Single row of data with indicators
            entry_price: Price at entry
            
        Returns:
            Tuple of (should_exit, reason)
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that required columns exist
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return False
        
        return True
    
    def calculate_signal_strength(
        self,
        conditions: Dict[str, bool]
    ) -> float:
        """
        Calculate signal strength based on multiple conditions
        
        Args:
            conditions: Dictionary of condition names and their values
            
        Returns:
            Signal strength (0-1)
        """
        if not conditions:
            return 0.0
        
        true_count = sum(1 for v in conditions.values() if v)
        return true_count / len(conditions)
