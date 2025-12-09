"""
Backtesting Script - Test strategy on historical data
Tests the 8-layer filtering system on past market data to evaluate performance
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

from src.brokers.zerodha_broker import ZerodhaBroker
from src.strategies.intraday_strategy import IntradayStrategy
from src.data.data_processor import DataProcessor
from src.utils.logger import get_logger
from src.utils.config import config

# Load environment variables
load_dotenv()

logger = get_logger('backtest', config.get('logging'))


class StrategyBacktester:
    """Backtest the trading strategy on historical data"""
    
    def __init__(self, symbols=None, days_back=30):
        """
        Initialize backtester
        
        Args:
            symbols: List of symbols to test (default: NIFTY 50)
            days_back: Number of days to backtest
        """
        self.days_back = days_back
        
        # Initialize components
        api_key = os.getenv('ZERODHA_API_KEY')
        api_secret = os.getenv('ZERODHA_API_SECRET')
        access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
        
        if not all([api_key, api_secret, access_token]):
            raise ValueError("Missing Zerodha credentials in .env file")
        
        self.broker = ZerodhaBroker(api_key, api_secret, access_token)
        self.strategy = IntradayStrategy()
        self.processor = DataProcessor()
        
        # Get symbols to test
        if symbols:
            self.symbols = symbols
        else:
            # Use NIFTY 50 stocks
            self.symbols = config.get_symbols()[:10]  # Start with first 10 for faster testing
        
        logger.info(f"Initialized backtester for {len(self.symbols)} symbols")
        logger.info(f"Testing period: Last {days_back} days")
    
    def fetch_historical_data(self, symbol, interval='5minute'):
        """
        Fetch historical data for backtesting
        
        Args:
            symbol: Stock symbol (e.g., RELIANCE.NS)
            interval: Data interval (5minute, 15minute, day)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=self.days_back)
            
            logger.info(f"Fetching {symbol} data from {from_date.date()} to {to_date.date()}")
            
            # Fetch historical data from Zerodha
            # ZerodhaBroker expects instrument_token parameter
            df = self.broker.get_historical_data(
                instrument_token=symbol,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            if df is None or df.empty:
                logger.warning(f"No data received for {symbol}")
                return None
            
            # Clean and process the data
            df = self.processor.clean_data(df)
            
            logger.info(f"Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def backtest_symbol(self, symbol):
        """
        Backtest strategy on a single symbol
        
        Args:
            symbol: Stock symbol to test
        
        Returns:
            dict: Backtest results for this symbol
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Backtesting {symbol}")
        logger.info(f"{'='*60}")
        
        # Fetch historical data
        df = self.fetch_historical_data(symbol)
        
        if df is None or df.empty:
            return {
                'symbol': symbol,
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'data_points': 0,
                'date_range': 'No data',
                'signals_detail': [],
                'error': 'No data available'
            }
        
        # Generate signals using the strategy
        signals = self.strategy.generate_signals(df, symbol)
        
        # Analyze the signals
        buy_signals = [s for s in signals if s.signal_type.value == 'BUY']
        sell_signals = [s for s in signals if s.signal_type.value == 'SELL']
        
        result = {
            'symbol': symbol,
            'total_signals': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'data_points': len(df),
            'date_range': f"{df.index[0].date()} to {df.index[-1].date()}",
            'signals_detail': []
        }
        
        # Log detailed signal information
        logger.info(f"\n📊 Results for {symbol}:")
        logger.info(f"  Data points: {len(df)}")
        logger.info(f"  Total signals: {len(signals)}")
        logger.info(f"  BUY signals: {len(buy_signals)}")
        logger.info(f"  SELL signals: {len(sell_signals)}")
        
        if signals:
            logger.info(f"\n  Signal Details:")
            for idx, signal in enumerate(signals, 1):
                signal_info = {
                    'timestamp': str(signal.timestamp),
                    'type': signal.signal_type.value,
                    'price': signal.price,
                    'strength': signal.strength,
                    'reason': signal.reason
                }
                result['signals_detail'].append(signal_info)
                
                logger.info(f"\n  [{idx}] {signal.signal_type.value} Signal")
                logger.info(f"      Time: {signal.timestamp}")
                logger.info(f"      Price: Rs {signal.price:.2f}")
                logger.info(f"      Strength: {signal.strength:.1%}")
                logger.info(f"      Stop Loss: Rs {signal.stop_loss:.2f}")
                logger.info(f"      Target: Rs {signal.take_profit:.2f}")
                logger.info(f"      Reason: {signal.reason}")
        
        return result
    
    def run_backtest(self):
        """
        Run backtest on all symbols
        
        Returns:
            dict: Complete backtest results
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING STRATEGY BACKTEST")
        logger.info("="*80)
        logger.info(f"Symbols: {len(self.symbols)}")
        logger.info(f"Period: Last {self.days_back} days")
        logger.info(f"Strategy: 8-Layer Filtering System")
        logger.info("="*80 + "\n")
        
        results = []
        
        for idx, symbol in enumerate(self.symbols, 1):
            logger.info(f"\n[{idx}/{len(self.symbols)}] Testing {symbol}...")
            
            result = self.backtest_symbol(symbol)
            results.append(result)
        
        # Generate summary
        summary = self.generate_summary(results)
        
        # Save results to file
        self.save_results(results, summary)
        
        return {
            'results': results,
            'summary': summary
        }
    
    def generate_summary(self, results):
        """Generate summary statistics from backtest results"""
        
        total_signals = sum(r['total_signals'] for r in results)
        total_buy = sum(r['buy_signals'] for r in results)
        total_sell = sum(r['sell_signals'] for r in results)
        symbols_with_signals = len([r for r in results if r['total_signals'] > 0])
        
        summary = {
            'total_symbols_tested': len(results),
            'symbols_with_signals': symbols_with_signals,
            'total_signals': total_signals,
            'total_buy_signals': total_buy,
            'total_sell_signals': total_sell,
            'avg_signals_per_symbol': total_signals / len(results) if results else 0,
            'test_period_days': self.days_back
        }
        
        logger.info("\n" + "="*80)
        logger.info("BACKTEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Symbols Tested: {summary['total_symbols_tested']}")
        logger.info(f"Symbols with Signals: {summary['symbols_with_signals']}")
        logger.info(f"Total Signals Generated: {summary['total_signals']}")
        logger.info(f"  - BUY Signals: {summary['total_buy_signals']}")
        logger.info(f"  - SELL Signals: {summary['total_sell_signals']}")
        logger.info(f"Average Signals per Symbol: {summary['avg_signals_per_symbol']:.2f}")
        logger.info(f"Test Period: {self.days_back} days")
        logger.info("="*80 + "\n")
        
        return summary
    
    def save_results(self, results, summary):
        """Save backtest results to JSON file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_results_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'summary': summary,
            'results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"✅ Results saved to: {filename}")
        logger.info(f"📊 You can review detailed results in this file\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest Trading Strategy')
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to backtest (default: 30)'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        nargs='+',
        help='Specific symbols to test (default: first 10 NIFTY 50)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Test all 49 NIFTY 50 stocks (takes longer)'
    )
    
    args = parser.parse_args()
    
    # Determine which symbols to test
    symbols = None
    if args.all:
        symbols = config.get_symbols()  # All NIFTY 50
        print(f"\n📈 Testing ALL {len(symbols)} NIFTY 50 stocks")
    elif args.symbols:
        symbols = args.symbols
        print(f"\n📈 Testing {len(symbols)} specific symbols")
    else:
        symbols = config.get_symbols()[:10]  # First 10
        print(f"\n📈 Testing first 10 NIFTY 50 stocks (use --all for all 49)")
    
    print(f"📅 Period: Last {args.days} days")
    print(f"⚙️  Strategy: 8-Layer Filtering System")
    print("\n" + "="*60)
    
    # Create backtester
    backtester = StrategyBacktester(symbols=symbols, days_back=args.days)
    
    # Run backtest
    results = backtester.run_backtest()
    
    print("\n" + "="*60)
    print("✅ BACKTEST COMPLETE!")
    print("="*60)
    print(f"\nResults saved to backtest_results_*.json")
    print("\nKey Findings:")
    print(f"  • Total Signals: {results['summary']['total_signals']}")
    print(f"  • BUY Signals: {results['summary']['total_buy_signals']}")
    print(f"  • SELL Signals: {results['summary']['total_sell_signals']}")
    print(f"  • Symbols with Signals: {results['summary']['symbols_with_signals']}/{results['summary']['total_symbols_tested']}")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
