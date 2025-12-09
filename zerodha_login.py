"""
Zerodha Kite Connect - One-Time Login Script
Run this script to generate your access token
"""

import os
from dotenv import load_dotenv, set_key
import webbrowser

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("❌ kiteconnect not installed!")
    print("Run: pip install kiteconnect")
    exit(1)

# Load environment variables
load_dotenv()

def main():
    print("=" * 60)
    print("🇮🇳 ZERODHA KITE CONNECT - ONE-TIME LOGIN")
    print("=" * 60)
    print()
    
    # Get API credentials
    api_key = os.getenv('ZERODHA_API_KEY')
    api_secret = os.getenv('ZERODHA_API_SECRET')
    
    if not api_key or not api_secret:
        print("⚠️  API credentials not found in .env file!")
        print()
        print("Please create a .env file with:")
        print("ZERODHA_API_KEY=your_api_key")
        print("ZERODHA_API_SECRET=your_api_secret")
        print()
        
        # Manual input
        api_key = input("Enter your API Key: ").strip()
        api_secret = input("Enter your API Secret: ").strip()
        
        if not api_key or not api_secret:
            print("❌ API key and secret are required!")
            return
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=api_key)
    
    # Step 1: Generate login URL
    login_url = kite.login_url()
    
    print("📋 STEP 1: Login to Zerodha")
    print("-" * 60)
    print(f"Login URL: {login_url}")
    print()
    print("A browser window will open. Please:")
    print("1. Login with your Zerodha credentials")
    print("2. Authorize the app")
    print("3. Copy the request_token from the redirect URL")
    print()
    
    # Open browser
    try:
        webbrowser.open(login_url)
        print("✅ Browser opened successfully")
    except:
        print("⚠️  Could not open browser automatically")
        print(f"Please open this URL manually: {login_url}")
    
    print()
    print("-" * 60)
    print("📋 STEP 2: Get Request Token")
    print("-" * 60)
    print()
    print("After logging in, you'll be redirected to:")
    print("http://127.0.0.1:5000/callback?request_token=XXXXXX&action=login")
    print()
    print("Copy the 'request_token' value from the URL")
    print()
    
    # Get request token from user
    request_token = input("Enter request_token: ").strip()
    
    if not request_token:
        print("❌ Request token is required!")
        return
    
    # Step 2: Generate access token
    try:
        print()
        print("📋 STEP 3: Generating Access Token...")
        print("-" * 60)
        
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print()
        print("✅ SUCCESS! Access token generated")
        print()
        print("=" * 60)
        print("🔑 YOUR ACCESS TOKEN:")
        print("=" * 60)
        print(access_token)
        print("=" * 60)
        print()
        
        # Save to .env file
        env_file = '.env'
        if os.path.exists(env_file):
            set_key(env_file, 'ZERODHA_ACCESS_TOKEN', access_token)
            print(f"✅ Access token saved to {env_file}")
        else:
            # Create .env file
            with open(env_file, 'w') as f:
                f.write(f"ZERODHA_API_KEY={api_key}\n")
                f.write(f"ZERODHA_API_SECRET={api_secret}\n")
                f.write(f"ZERODHA_ACCESS_TOKEN={access_token}\n")
            print(f"✅ Created {env_file} with credentials")
        
        print()
        print("=" * 60)
        print("📌 IMPORTANT NOTES:")
        print("=" * 60)
        print("1. Access token expires at end of trading day (6:00 AM IST)")
        print("2. Run this script again next day to get new token")
        print("3. Keep your .env file secure (don't commit to GitHub!)")
        print()
        
        # Test connection
        print("📋 STEP 4: Testing Connection...")
        print("-" * 60)
        
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print()
        print("✅ Connection successful!")
        print()
        print(f"User ID: {profile.get('user_id')}")
        print(f"User Name: {profile.get('user_name')}")
        print(f"Email: {profile.get('email')}")
        print()
        
        # Get margins
        margins = kite.margins()
        equity_margin = margins.get('equity', {})
        available = equity_margin.get('available', {})
        cash = available.get('cash', 0)
        
        print("💰 Available Margin:")
        print(f"   Cash: ₹{cash:,.2f}")
        print()
        
        print("=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("You can now run:")
        print("  python main.py --mode paper    (for paper trading)")
        print("  python main.py --mode live     (for live trading)")
        print()
        
    except Exception as e:
        print()
        print("❌ ERROR:")
        print(str(e))
        print()
        print("Common issues:")
        print("1. Wrong request_token (check URL carefully)")
        print("2. Wrong API secret (check .env file)")
        print("3. Token already used (get new one by logging in again)")
        print()

if __name__ == "__main__":
    main()
