"""
Fetch Instrument Tokens from Zerodha
Required for WebSocket streaming
"""

import os
import json
from dotenv import load_dotenv

try:
    from kiteconnect import KiteConnect
    KITE_AVAILABLE = True
except ImportError:
    print("❌ kiteconnect not installed!")
    print("Run: pip install kiteconnect")
    exit(1)

# Load environment variables
load_dotenv()

def get_instrument_tokens():
    """
    Fetch instrument tokens for NIFTY 50 stocks
    Saves to instrument_tokens.json
    """
    api_key = os.getenv('ZERODHA_API_KEY')
    access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ Missing Zerodha credentials in .env file")
        print("Required: ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN")
        exit(1)
    
    print("\n" + "="*80)
    print(" FETCHING INSTRUMENT TOKENS FROM ZERODHA")
    print("="*80 + "\n")
    
    # Initialize Kite
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    
    print("📡 Fetching instruments from NSE...")
    
    try:
        # Get all NSE instruments
        instruments = kite.instruments("NSE")
        print(f"✅ Fetched {len(instruments)} instruments from NSE\n")
    except Exception as e:
        print(f"❌ Error fetching instruments: {e}")
        print("Check if your access token is valid (run: python zerodha_login.py)")
        exit(1)
    
    # NIFTY 50 symbols (without .NS suffix for NSE instruments API)
    nifty50_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
        "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "HCLTECH",
        "BAJFINANCE", "TITAN", "SUNPHARMA", "ULTRACEMCO", "NESTLEIND",
        "WIPRO", "ONGC", "NTPC", "POWERGRID", "TECHM",
        "M&M", "TATAMOTORS", "TATASTEEL", "INDUSINDBK", "BAJAJFINSV",
        "ADANIENT", "COALINDIA", "DRREDDY", "GRASIM", "HINDALCO",
        "DIVISLAB", "CIPLA", "EICHERMOT", "SHREECEM", "APOLLOHOSP",
        "BPCL", "JSWSTEEL", "HEROMOTOCO", "BRITANNIA", "TATACONSUM",
        "SBILIFE", "ADANIPORTS", "UPL", "BAJAJ-AUTO", "HDFCLIFE"
    ]
    
    print("🔍 Mapping NIFTY 50 symbols to instrument tokens...")
    
    # Build token mapping
    token_map = {}
    symbol_map = {}  # For display
    
    for instrument in instruments:
        symbol = instrument['tradingsymbol']
        
        if symbol in nifty50_symbols:
            # Use .NS suffix for consistency with rest of bot
            full_symbol = symbol + ".NS"
            token = instrument['instrument_token']
            
            token_map[full_symbol] = token
            symbol_map[full_symbol] = {
                'token': token,
                'name': instrument['name'],
                'exchange': instrument['exchange']
            }
    
    print(f"✅ Found {len(token_map)} NIFTY 50 instruments\n")
    
    # Display some examples
    print("📋 Sample mappings:")
    for symbol, data in list(symbol_map.items())[:5]:
        print(f"   {symbol:20} → Token: {data['token']:10} ({data['name']})")
    print("   ...\n")
    
    # Save to JSON
    output_file = 'instrument_tokens.json'
    with open(output_file, 'w') as f:
        json.dump(token_map, f, indent=2)
    
    print(f"💾 Saved to: {output_file}")
    
    # Save detailed mapping too
    detail_file = 'instrument_details.json'
    with open(detail_file, 'w') as f:
        json.dump(symbol_map, f, indent=2)
    
    print(f"💾 Saved details to: {detail_file}")
    
    print("\n" + "="*80)
    print(" SUCCESS!")
    print("="*80 + "\n")
    
    print("✅ Instrument tokens ready for WebSocket streaming")
    print(f"✅ {len(token_map)} NIFTY 50 stocks mapped")
    print("\n📝 Next steps:")
    print("   1. Use these tokens with RealtimeDataStream")
    print("   2. Start WebSocket connection")
    print("   3. Subscribe to real-time ticks")
    print("   4. Enjoy instant signal detection! 🚀\n")
    
    return token_map


if __name__ == "__main__":
    try:
        tokens = get_instrument_tokens()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
