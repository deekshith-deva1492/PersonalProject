"""
Automated Trading Bot - 24x7 Scanner with Auto-Execution
Continuously scans NIFTY 50, generates signals, and executes trades automatically
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

from src.scanner.multi_symbol_scanner import MultiSymbolScanner
from src.execution.auto_executor import AutoTradeExecutor
from src.brokers.zerodha_broker import ZerodhaBroker
from src.risk.risk_manager import RiskManager
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('auto_trading_bot', config.get('logging'))

# Load environment variables
load_dotenv()


class AutomatedTradingBot:
    """Fully automated trading bot with scanner and executor"""
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize automated trading bot
        
        Args:
            dry_run: If True, simulate trades without actual execution
        """
        self.dry_run = dry_run
        
        # Initialize components
        logger.info("=" * 80)
        logger.info("🤖 Initializing Automated Trading Bot")
        logger.info("=" * 80)
        
        # Get Zerodha credentials
        api_key = os.getenv('ZERODHA_API_KEY')
        api_secret = os.getenv('ZERODHA_API_SECRET')
        access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
        
        if not all([api_key, api_secret, access_token]):
            raise ValueError("Missing Zerodha credentials in .env file")
        
        # Initialize broker
        self.broker = ZerodhaBroker(api_key, api_secret, access_token)
        logger.info("✅ Broker initialized")
        
        # Initialize risk manager
        self.risk_manager = RiskManager()
        logger.info("✅ Risk manager initialized")
        
        # Initialize executor
        self.executor = AutoTradeExecutor(
            broker=self.broker,
            risk_manager=self.risk_manager,
            dry_run=dry_run
        )
        logger.info(f"✅ Executor initialized ({'DRY RUN' if dry_run else 'LIVE'})")
        
        # Initialize scanner
        symbols = config.get_symbols()
        self.scanner = MultiSymbolScanner(symbols=symbols)
        logger.info(f"✅ Scanner initialized with {len(symbols)} symbols")
        
        # State
        self.is_running = False
        self.start_time = None
        
        logger.info("=" * 80)
        logger.info("🎉 Bot initialization complete!")
        logger.info("=" * 80)
    
    def signal_callback(self, signals):
        """
        Callback function called when scanner finds new signals
        
        Args:
            signals: List of Signal objects
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📢 NEW SIGNALS DETECTED: {len(signals)} signal(s)")
        logger.info(f"{'='*80}\n")
        
        for signal in signals:
            # Log signal details
            logger.info(signal.get_detailed_explanation())
            logger.info("-" * 80)
            
            # Execute signal if executor is active
            if self.executor.is_active:
                order_result = self.executor.execute_signal(signal)
                
                if order_result:
                    logger.info(f"✅ Trade executed for {signal.symbol}")
                else:
                    logger.warning(f"⚠️ Trade not executed for {signal.symbol}")
            else:
                logger.info("⏸️ Executor is inactive. Signal logged but not executed.")
            
            logger.info("=" * 80 + "\n")
    
    def start(self, auto_trade: bool = False):
        """
        Start the automated trading bot
        
        Args:
            auto_trade: If True, automatically execute trades
        """
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("\n" + "=" * 80)
        logger.info("🚀 STARTING AUTOMATED TRADING BOT")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else '🔴 LIVE TRADING'}")
        logger.info(f"Auto-trade: {'ENABLED' if auto_trade else 'DISABLED'}")
        logger.info(f"Symbols: {len(self.scanner.symbols)}")
        logger.info(f"Capital: ₹{self.risk_manager.portfolio_value:,.2f}")
        logger.info(f"Max positions: {self.risk_manager.risk_config.get('max_open_positions', 5)}")
        logger.info(f"Risk per trade: {self.risk_manager.risk_config.get('max_portfolio_risk', 0.01):.1%}")
        logger.info("=" * 80 + "\n")
        
        # Activate executor if auto_trade is enabled
        if auto_trade:
            self.executor.activate()
        
        # Start scanner with callback
        try:
            self.scanner.start_continuous_scan(callback=self.signal_callback)
        except KeyboardInterrupt:
            logger.info("\n⛔ Bot stopped by user")
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        self.scanner.stop()
        self.executor.deactivate()
        
        # Print statistics
        self.print_statistics()
        
        logger.info("👋 Bot stopped successfully")
    
    def print_statistics(self):
        """Print bot statistics"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 BOT STATISTICS")
        logger.info("=" * 80)
        
        # Runtime
        if self.start_time:
            runtime = datetime.now() - self.start_time
            logger.info(f"Runtime: {runtime}")
        
        # Scanner stats
        scanner_stats = self.scanner.get_statistics()
        logger.info(f"\n🔍 Scanner:")
        logger.info(f"  Symbols scanned: {scanner_stats['symbols_scanned']}")
        logger.info(f"  Signals generated: {scanner_stats['signals_generated']}")
        logger.info(f"  Signals in memory: {scanner_stats['signals_in_memory']}")
        
        # Executor stats
        executor_stats = self.executor.get_statistics()
        logger.info(f"\n⚡ Executor:")
        logger.info(f"  Active: {executor_stats['is_active']}")
        logger.info(f"  Trades today: {executor_stats['trades_today']}/{executor_stats['max_trades_per_day']}")
        logger.info(f"  Orders placed: {executor_stats['orders_placed']}")
        logger.info(f"  Orders rejected: {executor_stats['orders_rejected']}")
        
        # Portfolio stats
        logger.info(f"\n💰 Portfolio:")
        logger.info(f"  Current value: ₹{self.risk_manager.portfolio_value:,.2f}")
        logger.info(f"  Daily P&L: ₹{self.risk_manager.daily_pnl:,.2f}")
        logger.info(f"  Open positions: {len(self.risk_manager.positions)}")
        
        logger.info("=" * 80 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Trading Bot')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in LIVE mode (default is DRY RUN)'
    )
    parser.add_argument(
        '--auto-trade',
        action='store_true',
        help='Enable automatic trade execution'
    )
    
    args = parser.parse_args()
    
    # Create bot
    bot = AutomatedTradingBot(dry_run=not args.live)
    
    # Warning for live mode
    if args.live:
        print("\n" + "⚠️  " * 20)
        print("WARNING: LIVE TRADING MODE ENABLED!")
        print("Real money will be used for trades!")
        print("⚠️  " * 20 + "\n")
        
        response = input("Type 'YES' to confirm: ")
        if response != 'YES':
            print("Cancelled.")
            return
    
    # Start bot
    try:
        bot.start(auto_trade=args.auto_trade)
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.stop()


if __name__ == '__main__':
    main()
