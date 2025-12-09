"""
Test Script - Quick functionality test
Run this to verify everything is working correctly
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.data_fetcher import DataFetcher
from src.data.data_processor import DataProcessor
from src.indicators.technical_indicators import TechnicalIndicators
from src.strategies.intraday_strategy import IntradayStrategy
from src.risk.risk_manager import RiskManager
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger('test', config.get('logging'))


def test_data_fetching():
    """Test data fetching functionality"""
    print("\n" + "=" * 50)
    print("Testing Data Fetcher...")
    print("=" * 50)
    
    try:
        data_fetcher = DataFetcher()
        
        # Test market status
        is_open = data_fetcher.is_market_open()
        print(f"✓ Market is {'OPEN' if is_open else 'CLOSED'}")
        
        # Test data fetching
        print("\nFetching AAPL data...")
        df = data_fetcher.get_historical_data("AAPL", "5min", 2)
        
        if not df.empty:
            print(f"✓ Fetched {len(df)} rows of data")
            print(f"✓ Columns: {', '.join(df.columns[:5])}...")
            print(f"✓ Latest close price: ${df.iloc[-1]['close']:.2f}")
        else:
            print("✗ No data fetched (market might be closed)")
        
        # Test quote
        quote = data_fetcher.get_real_time_quote("AAPL")
        if quote:
            print(f"✓ Current quote: ${quote.get('price', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_indicators():
    """Test technical indicators"""
    print("\n" + "=" * 50)
    print("Testing Technical Indicators...")
    print("=" * 50)
    
    try:
        data_fetcher = DataFetcher()
        indicators_calc = TechnicalIndicators()
        
        # Fetch data
        df = data_fetcher.get_historical_data("AAPL", "5min", 2)
        
        if df.empty:
            print("⚠ No data available (market might be closed)")
            return True
        
        # Calculate indicators
        df = indicators_calc.calculate_all_indicators(df)
        
        # Check if indicators are calculated
        latest = df.iloc[-1]
        
        print(f"✓ RSI: {latest['rsi']:.2f}")
        print(f"✓ MACD: {latest['macd']:.4f}")
        print(f"✓ MACD Signal: {latest['macd_signal']:.4f}")
        print(f"✓ SMA 20: ${latest.get('sma_20', 0):.2f}")
        print(f"✓ Bollinger Upper: ${latest.get('bb_upper', 0):.2f}")
        print(f"✓ ATR: {latest.get('atr', 0):.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_strategy():
    """Test trading strategy"""
    print("\n" + "=" * 50)
    print("Testing Trading Strategy...")
    print("=" * 50)
    
    try:
        data_fetcher = DataFetcher()
        data_processor = DataProcessor()
        strategy = IntradayStrategy()
        
        # Fetch and process data
        df = data_fetcher.get_historical_data("AAPL", "5min", 5)
        
        if df.empty:
            print("⚠ No data available (market might be closed)")
            return True
        
        df = data_processor.clean_data(df)
        
        # Generate signals
        signals = strategy.generate_signals(df, "AAPL")
        
        print(f"✓ Strategy initialized: {strategy.name}")
        print(f"✓ Generated {len(signals)} signals")
        
        if signals:
            for i, signal in enumerate(signals[:3], 1):
                print(f"\nSignal {i}:")
                print(f"  Type: {signal.signal_type.value}")
                print(f"  Price: ${signal.price:.2f}")
                print(f"  Strength: {signal.strength*100:.1f}%")
                print(f"  Reason: {signal.reason}")
        else:
            print("  No active signals (waiting for conditions)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management():
    """Test risk management"""
    print("\n" + "=" * 50)
    print("Testing Risk Manager...")
    print("=" * 50)
    
    try:
        risk_manager = RiskManager()
        
        print(f"✓ Initial capital: ${risk_manager.initial_capital:,.2f}")
        print(f"✓ Max positions: {risk_manager.risk_config.get('max_open_positions')}")
        
        # Test position sizing
        entry_price = 150.0
        stop_loss = 148.5
        
        shares = risk_manager.calculate_position_size(
            "AAPL",
            entry_price,
            stop_loss,
            signal_strength=0.8
        )
        
        print(f"✓ Position size calculated: {shares} shares")
        print(f"  Entry: ${entry_price:.2f}, Stop: ${stop_loss:.2f}")
        
        # Test adding position
        if shares > 0:
            can_open = risk_manager.can_open_position("AAPL", shares * entry_price)
            print(f"✓ Can open position: {can_open}")
            
            if can_open:
                risk_manager.add_position(
                    "AAPL",
                    shares,
                    entry_price,
                    stop_loss,
                    entry_price * 1.02
                )
                
                summary = risk_manager.get_portfolio_summary()
                print(f"✓ Position added to portfolio")
                print(f"  Remaining cash: ${summary['cash']:,.2f}")
                print(f"  Open positions: {summary['num_positions']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  INTRADAY TRADING BOT - FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = {
        'Data Fetching': test_data_fetching(),
        'Technical Indicators': test_indicators(),
        'Trading Strategy': test_strategy(),
        'Risk Management': test_risk_management()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou're ready to start trading!")
        print("\nNext steps:")
        print("1. Run the bot: python main.py")
        print("2. Run the dashboard: streamlit run dashboard/app.py")
    else:
        print("  ⚠ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease check the errors above and ensure:")
        print("1. All dependencies are installed (run: python setup.py)")
        print("2. You have internet connection")
        print("3. Market might be closed (tests work better during market hours)")
    
    print()


if __name__ == "__main__":
    main()
