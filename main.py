"""
Main Trading Bot Application
Entry point for the intraday trading bot
"""

import argparse
import time
from datetime import datetime
import schedule

from src.data.data_fetcher import DataFetcher
from src.data.data_processor import DataProcessor
from src.strategies.intraday_strategy import IntradayStrategy
from src.risk.risk_manager import RiskManager
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('main', config.get('logging'))


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, mode: str = "paper"):
        """
        Initialize trading bot with Zerodha
        
        Args:
            mode: Trading mode (paper or live)
        """
        self.mode = mode
        self.data_fetcher = DataFetcher(provider="zerodha")  # Use Zerodha
        self.data_processor = DataProcessor()
        self.strategy = IntradayStrategy()
        self.risk_manager = RiskManager()
        
        self.trading_config = config.get_trading_config()
        self.symbols = self.trading_config.get('symbols', [])
        
        logger.info(f"Initialized TradingBot in {mode} mode with Zerodha API")
        logger.info(f"Watching {len(self.symbols)} NIFTY 50 stocks")
    
    def run_trading_cycle(self):
        """Execute one trading cycle"""
        logger.info("=" * 50)
        logger.info(f"Starting trading cycle at {datetime.now()}")
        
        # Check if market is open
        if not self.data_fetcher.is_market_open():
            logger.info("Market is closed. Skipping cycle.")
            return
        
        # Get portfolio summary
        portfolio = self.risk_manager.get_portfolio_summary()
        logger.info(
            f"Portfolio: ${portfolio['total_value']:,.2f} | "
            f"Cash: ${portfolio['cash']:,.2f} | "
            f"Positions: {portfolio['num_positions']} | "
            f"P&L: ${portfolio['unrealized_pnl']:,.2f}"
        )
        
        # Process each symbol
        for symbol in self.symbols:
            try:
                self.process_symbol(symbol)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}", exc_info=True)
        
        logger.info("Trading cycle complete")
    
    def process_symbol(self, symbol: str):
        """
        Process a single symbol
        
        Args:
            symbol: Stock symbol to process
        """
        logger.info(f"Processing {symbol}...")
        
        # Fetch recent data
        data_config = config.get_data_config()
        df = self.data_fetcher.get_historical_data(
            symbol,
            interval=data_config.get('interval', '5min'),
            days=data_config.get('lookback_days', 5)
        )
        
        if df.empty:
            logger.warning(f"No data available for {symbol}")
            return
        
        # Clean and process data
        df = self.data_processor.clean_data(df)
        
        # Generate trading signals
        signals = self.strategy.generate_signals(df, symbol)
        
        if not signals:
            logger.info(f"No signals generated for {symbol}")
            return
        
        # Process the most recent signal
        latest_signal = signals[0]
        logger.info(f"Signal for {symbol}: {latest_signal}")
        
        # Execute trades based on signal
        self.execute_signal(latest_signal)
    
    def execute_signal(self, signal):
        """
        Execute a trading signal
        
        Args:
            signal: Trading signal to execute
        """
        symbol = signal.symbol
        
        # Check if we already have a position
        if symbol in self.risk_manager.positions:
            # Check exit conditions
            position = self.risk_manager.positions[symbol]
            
            # Update position with current price
            position.update_price(signal.price)
            
            # Check stop loss and take profit
            if self.risk_manager.check_stop_loss(symbol):
                logger.info(f"Closing {symbol} due to stop loss")
                self.close_position(symbol, signal.price, "Stop Loss")
                return
            
            if self.risk_manager.check_take_profit(symbol):
                logger.info(f"Closing {symbol} due to take profit")
                self.close_position(symbol, signal.price, "Take Profit")
                return
            
            # Check strategy exit conditions
            latest_data = signal.timestamp
            should_exit, reason = self.strategy.get_exit_conditions(
                latest_data,
                position.entry_price
            )
            
            if should_exit:
                logger.info(f"Closing {symbol}: {reason}")
                self.close_position(symbol, signal.price, reason)
                return
        
        # Open new position on BUY signal
        elif signal.signal_type.value == "BUY":
            self.open_position(signal)
        
        # For SELL signals without existing position (shorting)
        elif signal.signal_type.value == "SELL":
            logger.info(f"SELL signal for {symbol} (no position to close, shorting not implemented)")
    
    def open_position(self, signal):
        """
        Open a new position
        
        Args:
            signal: Buy signal
        """
        symbol = signal.symbol
        entry_price = signal.price
        
        # Calculate stop loss and take profit
        exit_config = self.strategy.strategy_config.get('exit', {})
        stop_loss_pct = exit_config.get('stop_loss', 0.01)
        profit_target_pct = exit_config.get('profit_target', 0.02)
        
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + profit_target_pct)
        
        # Calculate position size
        quantity = self.risk_manager.calculate_position_size(
            symbol,
            entry_price,
            stop_loss,
            signal.strength
        )
        
        if quantity == 0:
            logger.warning(f"Position size is 0 for {symbol}")
            return
        
        # Check if we can open position
        estimated_cost = quantity * entry_price
        if not self.risk_manager.can_open_position(symbol, estimated_cost):
            logger.warning(f"Cannot open position in {symbol}")
            return
        
        # Execute order (in paper trading, just update risk manager)
        if self.mode == "paper":
            logger.info(
                f"[PAPER] BUY {quantity} shares of {symbol} @ ${entry_price:.2f} "
                f"| SL: ${stop_loss:.2f} | TP: ${take_profit:.2f}"
            )
            self.risk_manager.add_position(
                symbol, quantity, entry_price, stop_loss, take_profit
            )
        else:
            # In live mode, execute actual order via broker API
            logger.info("Live trading not implemented yet")
    
    def close_position(self, symbol: str, exit_price: float, reason: str):
        """
        Close an existing position
        
        Args:
            symbol: Stock symbol
            exit_price: Exit price
            reason: Reason for closing
        """
        if self.mode == "paper":
            position = self.risk_manager.remove_position(symbol, exit_price)
            if position:
                logger.info(
                    f"[PAPER] SELL {position.quantity} shares of {symbol} @ ${exit_price:.2f} "
                    f"| Reason: {reason} "
                    f"| P&L: ${position.unrealized_pnl:.2f}"
                )
        else:
            # In live mode, execute actual order via broker API
            logger.info("Live trading not implemented yet")
    
    def start(self, interval_minutes: int = 5):
        """
        Start the trading bot
        
        Args:
            interval_minutes: How often to run trading cycle (in minutes)
        """
        logger.info(f"Starting trading bot (running every {interval_minutes} minutes)")
        
        # Run immediately
        self.run_trading_cycle()
        
        # Schedule recurring runs
        schedule.every(interval_minutes).minutes.do(self.run_trading_cycle)
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the trading bot"""
        logger.info("Shutting down trading bot...")
        
        # Print final portfolio summary
        portfolio = self.risk_manager.get_portfolio_summary()
        logger.info("=" * 50)
        logger.info("FINAL PORTFOLIO SUMMARY")
        logger.info(f"Total Value: ${portfolio['total_value']:,.2f}")
        logger.info(f"Cash: ${portfolio['cash']:,.2f}")
        logger.info(f"Positions Value: ${portfolio['positions_value']:,.2f}")
        logger.info(f"Total Return: {portfolio['total_return_percent']:.2f}%")
        logger.info(f"Open Positions: {portfolio['num_positions']}")
        logger.info("=" * 50)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Intraday Trading Bot")
    parser.add_argument(
        '--mode',
        type=str,
        default='paper',
        choices=['paper', 'live'],
        help='Trading mode (paper or live)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Trading cycle interval in minutes'
    )
    
    args = parser.parse_args()
    
    # Create and start bot
    bot = TradingBot(mode=args.mode)
    bot.start(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
