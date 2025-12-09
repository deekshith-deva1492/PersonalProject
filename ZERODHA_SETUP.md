# 🇮🇳 Zerodha Integration Setup Guide

## ✅ Configuration Updated

Your bot is now configured for:
- **Risk per trade:** 1% of capital
- **Market:** NIFTY 50 stocks (all 50 stocks)
- **Broker:** Zerodha (via Kite Connect API)
- **Trading hours:** 9:15 AM - 3:30 PM IST
- **Timezone:** Asia/Kolkata

---

## 📋 Step-by-Step Zerodha Setup

### Step 1: Create Zerodha Kite Connect App

1. **Go to:** https://developers.kite.trade/
2. **Login** with your Zerodha credentials
3. **Create a new app:**
   - Click "Create new app"
   - App name: "TradingBot" (or any name)
   - Redirect URL: `http://127.0.0.1:5000/callback`
   - Description: "Intraday trading bot"
   - Click "Create"

4. **Save your credentials:**
   - **API Key:** (copy this)
   - **API Secret:** (copy this)

### Step 2: Install Kite Connect Library

```powershell
pip install kiteconnect
```

### Step 3: Set Up Environment Variables

Create a `.env` file in your TradingBot folder:

```env
# Zerodha API Credentials
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here
```

**Note:** You'll get the access token in Step 4.

### Step 4: Complete First-Time Login

Run this script to get your access token (one-time setup):

```powershell
python zerodha_login.py
```

This will:
1. Open your browser
2. Ask you to login to Zerodha
3. Redirect to a URL with `request_token`
4. Generate your `access_token`
5. Save it to `.env` file

**The access token is valid until the next trading day!**

### Step 5: Update Main Bot to Use Zerodha

I'll create an updated version that uses Zerodha API instead of yfinance.

---

## 🔧 Files Created/Modified

### New Files:

1. **`src/brokers/zerodha_broker.py`** - Zerodha API integration
2. **`zerodha_login.py`** - One-time login script
3. **`ZERODHA_SETUP.md`** - This guide

### Modified Files:

1. **`config.yaml`:**
   - Risk: 1% per trade (was 0.5%)
   - Symbols: All NIFTY 50 stocks (50 stocks)
   - Trading hours: 9:15 AM - 3:30 PM IST
   - Timezone: Asia/Kolkata

---

## 📊 NIFTY 50 Stocks Now Tracked

Your bot will scan all 50 stocks:

```
RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, HINDUNILVR, ITC, SBIN, 
BHARTIARTL, KOTAKBANK, LT, AXISBANK, ASIANPAINT, MARUTI, HCLTECH, 
BAJFINANCE, TITAN, SUNPHARMA, ULTRACEMCO, NESTLEIND, WIPRO, ONGC, 
NTPC, POWERGRID, TECHM, M&M, TATAMOTORS, TATASTEEL, INDUSINDBK, 
BAJAJFINSV, ADANIENT, COALINDIA, DRREDDY, GRASIM, HINDALCO, DIVISLAB, 
CIPLA, EICHERMOT, SHREECEM, APOLLOHOSP, BPCL, JSWSTEEL, HEROMOTOCO, 
BRITANNIA, TATACONSUM, SBILIFE, ADANIPORTS, UPL, BAJAJ-AUTO, HDFCLIFE
```

---

## 🎯 Risk Management (Updated)

### New Risk Parameters:

- **Per trade risk:** 1% of capital
- **Max open positions:** 5 (increased from 3)
- **Max daily loss:** 3% (increased from 2%)
- **Stop loss:** 0.3% per trade
- **Take profit:** 0.7% per trade

### Position Sizing Example:

**Capital:** ₹1,00,000

**Risk per trade:** 1% = ₹1,000

**Stock price:** ₹2,000 (e.g., RELIANCE)

**Stop loss:** 0.3% = ₹6 per share

**Position size:** ₹1,000 / ₹6 = **166 shares**

**Total investment:** 166 × ₹2,000 = ₹3,32,000

**Margin required (MIS):** ~₹66,400 (20% of total)

---

## 🚀 How to Use

### Mode 1: Paper Trading (Test First!)

```powershell
python main.py --mode paper
```

This uses **mock Zerodha broker** - no real trades!

### Mode 2: Live Trading (Real Money!)

```powershell
python main.py --mode live
```

This places **real orders** on Zerodha!

⚠️ **WARNING:** Only use live mode after thorough paper trading!

---

## 📱 Features of Zerodha Integration

### ✅ What It Can Do:

1. **Fetch real-time data** for NIFTY 50 stocks
2. **Place market orders** (BUY/SELL)
3. **Place limit orders** with specific prices
4. **Place stop-loss orders** (SL, SL-M)
5. **Modify existing orders**
6. **Cancel orders**
7. **Get positions** (current holdings)
8. **Get margins** (available capital)
9. **Get order history**
10. **Check market hours** (9:15 AM - 3:30 PM IST)

### 📊 Data Available:

- **5-minute candles** for intraday
- **Real-time quotes** (LTP, bid, ask)
- **Historical data** (up to 60 days)
- **OHLCV data** with volume

---

## 🔐 Security Best Practices

### DO:

✅ Keep API keys in `.env` file (not in code!)
✅ Add `.env` to `.gitignore`
✅ Use paper trading mode first
✅ Test thoroughly before live trading
✅ Monitor your account regularly

### DON'T:

❌ Share your API keys with anyone
❌ Commit `.env` to GitHub
❌ Use live mode without testing
❌ Leave bot running unattended initially
❌ Disable risk management features

---

## 🎓 Understanding Zerodha Product Types

### MIS (Margin Intraday Square-off)

- **Use:** Intraday trading (recommended)
- **Margin:** 5x-20x leverage
- **Auto square-off:** 3:20 PM IST
- **Benefit:** Lower capital required

### CNC (Cash and Carry)

- **Use:** Delivery trading
- **Margin:** No leverage (100% capital)
- **No auto square-off**
- **Benefit:** Hold overnight

### NRML (Normal)

- **Use:** F&O trading
- **Margin:** As per exchange
- **Can hold overnight**

**For intraday bot:** Use **MIS** (configured by default)

---

## 📈 Strategy Recap (Ultra-Simple)

Your bot uses the ultra-simple strategy:

### Entry:

1. ✅ **Trend check:** Price > 50 EMA (uptrend) OR Price < 50 EMA (downtrend)
2. ✅ **RSI extreme:** RSI < 30 (dip) OR RSI > 70 (spike)
3. ✅ **VWAP touch:** Price at VWAP band
4. ✅ **Reversal candle:** Bullish (uptrend) OR Bearish (downtrend)

### Exit:

- **Take profit:** 0.7% gain OR VWAP return
- **Stop loss:** 0.3% loss

### Risk:

- **1% per trade** (₹1,000 on ₹1,00,000 capital)
- **Max 5 positions** simultaneously
- **3% max daily loss**

---

## 🧪 Testing Checklist

Before going live, test these:

### Paper Trading Tests:

- [ ] Bot connects to Zerodha API
- [ ] Fetches NIFTY 50 data correctly
- [ ] Calculates indicators (RSI, EMA, VWAP)
- [ ] Generates buy/sell signals
- [ ] Calculates position sizes correctly
- [ ] Places paper orders successfully
- [ ] Tracks positions correctly
- [ ] Exits at profit/stop loss
- [ ] Respects max positions (5)
- [ ] Stops at daily loss limit (3%)

### Live Trading Tests (Small Capital):

- [ ] Start with ₹10,000-₹20,000
- [ ] Monitor for 1-2 weeks
- [ ] Verify order execution
- [ ] Check margins usage
- [ ] Validate P&L tracking
- [ ] Test stop-loss triggers
- [ ] Test take-profit exits

---

## 🆘 Troubleshooting

### Issue: "kiteconnect not installed"

```powershell
pip install kiteconnect
```

### Issue: "Access token expired"

Run the login script again:

```powershell
python zerodha_login.py
```

Access tokens expire daily - you need to regenerate!

### Issue: "Insufficient funds"

Check your available margin:

```python
broker.get_margins()
```

MIS requires 20-30% of position value.

### Issue: "Market closed"

NSE timings: 9:15 AM - 3:30 PM IST, Monday-Friday

Pre-market: 9:00 AM - 9:15 AM
Post-market: 3:40 PM - 4:00 PM

### Issue: "Order rejected"

Common reasons:
- Insufficient margin
- Invalid quantity (lot size)
- Stock in ban period
- Circuit limit hit
- After market hours

---

## 💰 Cost & Fees

### Zerodha Charges:

- **Equity Intraday:** ₹20 or 0.03% per trade (whichever is lower)
- **STT:** 0.025% on sell side
- **Transaction charges:** ~0.00325%
- **GST:** 18% on brokerage
- **SEBI charges:** ₹10 per crore

### Example Trade Cost:

**Trade:** Buy 100 RELIANCE @ ₹2,000, Sell @ ₹2,014 (0.7% profit)

- **Investment:** ₹2,00,000 (or ₹40,000 with 5x margin)
- **Profit:** ₹1,400
- **Brokerage:** ₹20 + ₹20 = ₹40
- **Other charges:** ~₹100
- **Net profit:** ~₹1,260

---

## 📞 Support

### Zerodha Support:

- **Website:** https://support.zerodha.com/
- **Email:** support@zerodha.com
- **Phone:** 080-4719-2020

### Kite Connect Documentation:

- **Docs:** https://kite.trade/docs/connect/v3/
- **GitHub:** https://github.com/zerodhatech/pykiteconnect
- **Forum:** https://kite.trade/forum/

---

## 🎯 Next Steps

1. **Install kiteconnect:**
   ```powershell
   pip install kiteconnect
   ```

2. **Create Kite app** at https://developers.kite.trade/

3. **Run login script:**
   ```powershell
   python zerodha_login.py
   ```

4. **Test in paper mode:**
   ```powershell
   python main.py --mode paper
   ```

5. **Monitor dashboard:**
   ```powershell
   streamlit run dashboard/app.py
   ```

6. **Go live** (after thorough testing):
   ```powershell
   python main.py --mode live
   ```

---

**Your bot is now configured for NIFTY 50 trading with Zerodha!** 🇮🇳📈

**Risk:** 1% per trade | **Broker:** Zerodha | **Market:** NSE | **Stocks:** NIFTY 50

Happy Trading! 🚀
