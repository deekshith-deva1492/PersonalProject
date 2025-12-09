"""
Auto Trading Executor - Automatically places trades based on signals
Implements bracket orders with stop-loss and take-profit
"""

import time
from typing import Dict, List, Optional
from datetime import datetime

from src.strategies.base_strategy import Signal, SignalType
from src.brokers.zerodha_broker import ZerodhaBroker
from src.risk.risk_manager import RiskManager, Position
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('auto_executor', config.get('logging'))


class AutoTradeExecutor:
    """Automatically execute trades based on signals"""
    
    def __init__(self, broker: ZerodhaBroker, risk_manager: RiskManager, dry_run: bool = False):
        """
        Initialize auto trade executor
        
        Args:
            broker: Broker instance for order placement
            risk_manager: Risk manager for position sizing
            dry_run: If True, simulate trades without actual execution
        """
        self.broker = broker
        self.risk_manager = risk_manager
        self.dry_run = dry_run
        
        # Execution tracking
        self.orders_placed: List[Dict] = []
        self.orders_filled: List[Dict] = []
        self.orders_rejected: List[Dict] = []
        
        # State
        self.is_active = False
        self.max_trades_per_day = 10
        self.trades_today = 0
        
        mode = "DRY RUN" if dry_run else "LIVE"
        logger.info(f"Initialized AutoTradeExecutor in {mode} mode")
    
    def execute_signal(self, signal: Signal) -> Optional[Dict]:
        """
        Execute a trading signal
        
        Args:
            signal: Trading signal to execute
            
        Returns:
            Order details if successful, None otherwise
        """
        if not self.is_active:
            logger.warning("Auto-executor is not active. Ignoring signal.")
            return None
        
        # Check if we can take more trades
        if self.trades_today >= self.max_trades_per_day:
            logger.warning(f"Max trades per day ({self.max_trades_per_day}) reached. Ignoring signal.")
            return None
        
        # Check risk limits
        if not self._check_risk_limits(signal):
            logger.warning(f"Risk limits exceeded. Cannot execute {signal.symbol}")
            return None
        
        try:
            # Log signal details
            logger.info("=" * 80)
            logger.info(f"🎯 EXECUTING SIGNAL:")
            logger.info(signal.get_detailed_explanation())
            logger.info("=" * 80)
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                symbol=signal.symbol,
                entry_price=signal.price,
                stop_loss_price=signal.stop_loss or (signal.price * 0.997),
                signal_strength=signal.strength
            )
            
            if position_size == 0:
                logger.warning(f"Position size is 0 for {signal.symbol}. Cannot execute.")
                return None
            
            logger.info(f"📊 Position size calculated: {position_size} shares")
            
            # Place bracket order
            if signal.signal_type == SignalType.BUY:
                order_result = self._place_buy_bracket_order(signal, position_size)
            elif signal.signal_type == SignalType.SELL:
                order_result = self._place_sell_bracket_order(signal, position_size)
            else:
                logger.warning(f"Unknown signal type: {signal.signal_type}")
                return None
            
            if order_result:
                self.trades_today += 1
                self.orders_placed.append({
                    'signal': signal.to_dict(),
                    'order': order_result,
                    'timestamp': datetime.now()
                })
                
                logger.info(f"✅ Order placed successfully!")
                logger.info(f"Order ID: {order_result.get('order_id')}")
                logger.info(f"Trades today: {self.trades_today}/{self.max_trades_per_day}")
                
                return order_result
            else:
                logger.error(f"❌ Failed to place order for {signal.symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing signal for {signal.symbol}: {e}")
            self.orders_rejected.append({
                'signal': signal.to_dict(),
                'error': str(e),
                'timestamp': datetime.now()
            })
            return None
    
    def _place_buy_bracket_order(self, signal: Signal, quantity: int) -> Optional[Dict]:
        """
        Place a BUY bracket order with stop-loss and take-profit
        
        Args:
            signal: Trading signal
            quantity: Number of shares
            
        Returns:
            Order details if successful
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would place BUY order:")
            logger.info(f"  Symbol: {signal.symbol}")
            logger.info(f"  Quantity: {quantity}")
            logger.info(f"  Entry: ₹{signal.price:.2f}")
            logger.info(f"  Stop Loss: ₹{signal.stop_loss:.2f}")
            logger.info(f"  Take Profit: ₹{signal.take_profit:.2f}")
            
            return {
                'order_id': f"DRY_RUN_{int(time.time())}",
                'symbol': signal.symbol,
                'type': 'BUY',
                'quantity': quantity,
                'price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'status': 'DRY_RUN'
            }
        
        # LIVE EXECUTION
        try:
            # Get trading symbol (remove .NS for Zerodha)
            trading_symbol = signal.symbol.replace('.NS', '')
            
            # Place main order
            main_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='MARKET',
                transaction_type='BUY'
            )
            
            if not main_order:
                return None
            
            order_id = main_order.get('order_id')
            logger.info(f"Main BUY order placed: {order_id}")
            
            # Wait for order to fill
            time.sleep(2)
            
            # Place stop-loss order
            sl_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='SL',
                transaction_type='SELL',
                price=signal.stop_loss,
                trigger_price=signal.stop_loss * 0.999  # Trigger slightly before
            )
            
            logger.info(f"Stop-loss order placed: {sl_order.get('order_id') if sl_order else 'FAILED'}")
            
            # Place take-profit order
            tp_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='LIMIT',
                transaction_type='SELL',
                price=signal.take_profit
            )
            
            logger.info(f"Take-profit order placed: {tp_order.get('order_id') if tp_order else 'FAILED'}")
            
            return {
                'main_order_id': order_id,
                'sl_order_id': sl_order.get('order_id') if sl_order else None,
                'tp_order_id': tp_order.get('order_id') if tp_order else None,
                'symbol': signal.symbol,
                'type': 'BUY',
                'quantity': quantity,
                'entry_price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'status': 'PLACED'
            }
            
        except Exception as e:
            logger.error(f"Error placing buy bracket order: {e}")
            return None
    
    def _place_sell_bracket_order(self, signal: Signal, quantity: int) -> Optional[Dict]:
        """
        Place a SELL/SHORT bracket order with stop-loss and take-profit
        
        Args:
            signal: Trading signal
            quantity: Number of shares
            
        Returns:
            Order details if successful
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would place SELL order:")
            logger.info(f"  Symbol: {signal.symbol}")
            logger.info(f"  Quantity: {quantity}")
            logger.info(f"  Entry: ₹{signal.price:.2f}")
            logger.info(f"  Stop Loss: ₹{signal.stop_loss:.2f}")
            logger.info(f"  Take Profit: ₹{signal.take_profit:.2f}")
            
            return {
                'order_id': f"DRY_RUN_{int(time.time())}",
                'symbol': signal.symbol,
                'type': 'SELL',
                'quantity': quantity,
                'price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'status': 'DRY_RUN'
            }
        
        # LIVE EXECUTION
        try:
            # Get trading symbol (remove .NS for Zerodha)
            trading_symbol = signal.symbol.replace('.NS', '')
            
            # Place main short order
            main_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='MARKET',
                transaction_type='SELL'
            )
            
            if not main_order:
                return None
            
            order_id = main_order.get('order_id')
            logger.info(f"Main SELL order placed: {order_id}")
            
            # Wait for order to fill
            time.sleep(2)
            
            # Place stop-loss order (buy back at higher price)
            sl_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='SL',
                transaction_type='BUY',
                price=signal.stop_loss,
                trigger_price=signal.stop_loss * 1.001  # Trigger slightly before
            )
            
            logger.info(f"Stop-loss order placed: {sl_order.get('order_id') if sl_order else 'FAILED'}")
            
            # Place take-profit order (buy back at lower price)
            tp_order = self.broker.place_order(
                symbol=trading_symbol,
                quantity=quantity,
                order_type='LIMIT',
                transaction_type='BUY',
                price=signal.take_profit
            )
            
            logger.info(f"Take-profit order placed: {tp_order.get('order_id') if tp_order else 'FAILED'}")
            
            return {
                'main_order_id': order_id,
                'sl_order_id': sl_order.get('order_id') if sl_order else None,
                'tp_order_id': tp_order.get('order_id') if tp_order else None,
                'symbol': signal.symbol,
                'type': 'SELL',
                'quantity': quantity,
                'entry_price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'status': 'PLACED'
            }
            
        except Exception as e:
            logger.error(f"Error placing sell bracket order: {e}")
            return None
    
    def _check_risk_limits(self, signal: Signal) -> bool:
        """
        Check if we can take this trade within risk limits
        
        Args:
            signal: Trading signal
            
        Returns:
            True if trade is within limits
        """
        # Check maximum open positions
        current_positions = len(self.risk_manager.positions)
        max_positions = self.risk_manager.risk_config.get('max_open_positions', 5)
        
        if current_positions >= max_positions:
            logger.warning(f"Max positions ({max_positions}) reached")
            return False
        
        # Check daily loss limit
        daily_loss_pct = abs(self.risk_manager.daily_pnl / self.risk_manager.initial_capital)
        max_daily_loss = self.risk_manager.risk_config.get('max_daily_loss', 0.03)
        
        if self.risk_manager.daily_pnl < 0 and daily_loss_pct >= max_daily_loss:
            logger.warning(f"Daily loss limit ({max_daily_loss:.1%}) exceeded")
            return False
        
        return True
    
    def activate(self):
        """Activate auto-trading"""
        self.is_active = True
        logger.info("🟢 Auto-trading ACTIVATED")
    
    def deactivate(self):
        """Deactivate auto-trading"""
        self.is_active = False
        logger.info("🔴 Auto-trading DEACTIVATED")
    
    def get_statistics(self) -> Dict:
        """Get execution statistics"""
        return {
            'is_active': self.is_active,
            'dry_run': self.dry_run,
            'trades_today': self.trades_today,
            'max_trades_per_day': self.max_trades_per_day,
            'orders_placed': len(self.orders_placed),
            'orders_filled': len(self.orders_filled),
            'orders_rejected': len(self.orders_rejected)
        }
    
    def reset_daily_counters(self):
        """Reset daily trade counters (call at market open)"""
        self.trades_today = 0
        logger.info("Daily trade counter reset")
